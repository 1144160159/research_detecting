from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.neighbors import NearestNeighbors

from .metrics import fpr_at_95_tpr, open_set_classification_rate


ORIENTED_METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


@dataclass(frozen=True)
class PseudoUnknownTask:
    name: str
    features: np.ndarray
    target: np.ndarray
    reference_risk: np.ndarray
    labels: np.ndarray
    prediction: np.ndarray

    def __post_init__(self) -> None:
        features = np.asarray(self.features, dtype=np.float64)
        target = np.asarray(self.target, dtype=bool)
        reference = np.asarray(self.reference_risk, dtype=np.float64)
        labels = np.asarray(self.labels, dtype=np.int64)
        prediction = np.asarray(self.prediction, dtype=np.int64)
        if features.ndim != 2 or features.shape[0] != len(target):
            raise ValueError("pseudo-unknown features and targets are incompatible")
        if not (len(reference) == len(labels) == len(prediction) == len(target)):
            raise ValueError("pseudo-unknown task arrays must have equal length")
        if target.all() or not target.any():
            raise ValueError("each pseudo-unknown task requires known and held-out rows")
        if not np.isfinite(features).all() or not np.isfinite(reference).all():
            raise ValueError("pseudo-unknown task contains non-finite scores")


def fit_nonnegative_weights(
    tasks: Sequence[PseudoUnknownTask],
    *,
    regularization: float = 0.1,
    seed: int = 0,
    boundary_training: bool = False,
    boundary_hard_pseudo_fraction: float = 0.5,
    boundary_interpolation: float = 0.5,
    boundary_max_per_task: int = 512,
    training_objective: str = "pointwise",
) -> np.ndarray:
    if not tasks:
        raise ValueError("at least one pseudo-unknown task is required")
    feature_count = np.asarray(tasks[0].features).shape[1]
    if any(np.asarray(task.features).shape[1] != feature_count for task in tasks):
        raise ValueError("pseudo-unknown tasks use different feature dimensions")
    if training_objective not in {"pointwise", "pairwise"}:
        raise ValueError("training objective must be pointwise or pairwise")
    if training_objective == "pairwise":
        if not boundary_training:
            raise ValueError("pairwise training requires boundary samples")
        values, targets, _ = boundary_pairwise_arrays(
            tasks,
            hard_pseudo_fraction=boundary_hard_pseudo_fraction,
            interpolation=boundary_interpolation,
            max_per_task=boundary_max_per_task,
        )
    elif boundary_training:
        values, targets, _ = boundary_training_arrays(
            tasks,
            hard_pseudo_fraction=boundary_hard_pseudo_fraction,
            interpolation=boundary_interpolation,
            max_per_task=boundary_max_per_task,
        )
    else:
        values = np.concatenate([np.asarray(task.features) for task in tasks], axis=0)
        targets = np.concatenate(
            [np.asarray(task.target, dtype=np.int64) for task in tasks]
        )
    model = LogisticRegression(
        C=float(regularization),
        class_weight="balanced",
        max_iter=1000,
        random_state=int(seed),
        solver="liblinear",
        fit_intercept=training_objective != "pairwise",
    )
    model.fit(values, targets)
    weights = np.maximum(np.asarray(model.coef_[0], dtype=np.float64), 0.0)
    if weights.sum() < 1e-12:
        weights = np.ones(feature_count, dtype=np.float64)
    return weights / weights.sum()


def boundary_training_arrays(
    tasks: Sequence[PseudoUnknownTask],
    *,
    hard_pseudo_fraction: float = 0.5,
    interpolation: float = 0.5,
    max_per_task: int = 512,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    if not 0.0 < float(hard_pseudo_fraction) <= 1.0:
        raise ValueError("hard pseudo fraction must lie in (0, 1]")
    if not 0.0 < float(interpolation) < 1.0:
        raise ValueError("boundary interpolation must lie in (0, 1)")
    if int(max_per_task) < 1:
        raise ValueError("boundary max per task must be positive")
    values = []
    targets = []
    audit_rows = []
    for task in tasks:
        features = np.asarray(task.features, dtype=np.float64)
        target = np.asarray(task.target, dtype=bool)
        reference = np.asarray(task.reference_risk, dtype=np.float64)
        known_index = np.flatnonzero(~target)
        pseudo_index = np.flatnonzero(target)
        pseudo_count = min(
            len(pseudo_index),
            int(max_per_task),
            max(1, int(np.ceil(len(pseudo_index) * float(hard_pseudo_fraction)))),
        )
        hard_pseudo_index = pseudo_index[
            np.argsort(reference[pseudo_index], kind="stable")[:pseudo_count]
        ]
        known_count = min(len(known_index), int(max_per_task), 2 * pseudo_count)
        hard_known_index = known_index[
            np.argsort(reference[known_index], kind="stable")[-known_count:]
        ]

        known_features = features[known_index]
        pseudo_features = features[hard_pseudo_index]
        median = np.median(known_features, axis=0)
        scale = np.quantile(known_features, 0.75, axis=0) - np.quantile(
            known_features, 0.25, axis=0
        )
        scale = np.where(scale > 1e-6, scale, 1.0)
        neighbors = NearestNeighbors(n_neighbors=1, algorithm="auto")
        neighbors.fit((known_features - median) / scale)
        nearest = neighbors.kneighbors(
            (pseudo_features - median) / scale, return_distance=False
        )[:, 0]
        nearest_known = known_features[nearest]
        synthetic = (
            (1.0 - float(interpolation)) * nearest_known
            + float(interpolation) * pseudo_features
        )
        task_values = np.concatenate(
            [features[hard_known_index], pseudo_features, synthetic], axis=0
        )
        task_targets = np.concatenate(
            [
                np.zeros(known_count, dtype=np.int64),
                np.ones(pseudo_count, dtype=np.int64),
                np.ones(pseudo_count, dtype=np.int64),
            ]
        )
        values.append(task_values)
        targets.append(task_targets)
        audit_rows.append(
            {
                "task": task.name,
                "source_known_samples": int(len(known_index)),
                "source_pseudo_unknown_samples": int(len(pseudo_index)),
                "hard_known_samples": int(known_count),
                "hard_pseudo_unknown_samples": int(pseudo_count),
                "synthetic_boundary_samples": int(pseudo_count),
                "hard_pseudo_reference_risk_mean": float(
                    reference[hard_pseudo_index].mean()
                ),
                "all_pseudo_reference_risk_mean": float(
                    reference[pseudo_index].mean()
                ),
            }
        )
    combined_values = np.concatenate(values, axis=0)
    combined_targets = np.concatenate(targets)
    return combined_values, combined_targets, {
        "enabled": True,
        "hard_pseudo_fraction": float(hard_pseudo_fraction),
        "interpolation": float(interpolation),
        "max_per_task": int(max_per_task),
        "training_samples": int(len(combined_targets)),
        "known_training_samples": int((combined_targets == 0).sum()),
        "pseudo_unknown_training_samples": int((combined_targets == 1).sum()),
        "tasks": audit_rows,
        "unknown_or_test_labels_used": False,
    }


def boundary_pairwise_arrays(
    tasks: Sequence[PseudoUnknownTask],
    *,
    hard_pseudo_fraction: float = 0.5,
    interpolation: float = 0.5,
    max_per_task: int = 512,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    pair_values = []
    pair_targets = []
    task_audits = []
    for task in tasks:
        values, targets, audit = boundary_training_arrays(
            [task],
            hard_pseudo_fraction=hard_pseudo_fraction,
            interpolation=interpolation,
            max_per_task=max_per_task,
        )
        known = values[targets == 0]
        pseudo = values[targets == 1]
        median = np.median(known, axis=0)
        scale = np.quantile(known, 0.75, axis=0) - np.quantile(
            known, 0.25, axis=0
        )
        scale = np.where(scale > 1e-6, scale, 1.0)
        neighbors = NearestNeighbors(n_neighbors=1, algorithm="auto")
        neighbors.fit((known - median) / scale)
        nearest = neighbors.kneighbors(
            (pseudo - median) / scale, return_distance=False
        )[:, 0]
        difference = pseudo - known[nearest]
        pair_values.extend((difference, -difference))
        pair_targets.extend(
            (
                np.ones(len(difference), dtype=np.int64),
                np.zeros(len(difference), dtype=np.int64),
            )
        )
        task_audit = dict(audit["tasks"][0])
        task_audit["ranking_pairs"] = int(len(difference))
        task_audits.append(task_audit)
    combined_values = np.concatenate(pair_values, axis=0)
    combined_targets = np.concatenate(pair_targets)
    return combined_values, combined_targets, {
        "enabled": True,
        "objective": "pairwise_logistic_ranking",
        "hard_pseudo_fraction": float(hard_pseudo_fraction),
        "interpolation": float(interpolation),
        "max_per_task": int(max_per_task),
        "ranking_pairs": int(len(combined_targets) // 2),
        "training_samples": int(len(combined_targets)),
        "known_training_samples": int((combined_targets == 0).sum()),
        "pseudo_unknown_training_samples": int((combined_targets == 1).sum()),
        "tasks": task_audits,
        "unknown_or_test_labels_used": False,
    }


def empirical_tail_scores(reference: np.ndarray, query: np.ndarray) -> np.ndarray:
    known = np.sort(np.asarray(reference, dtype=np.float64))
    values = np.asarray(query, dtype=np.float64)
    if known.ndim != 1 or known.size == 0:
        raise ValueError("known reference scores must be a non-empty vector")
    if not np.isfinite(known).all() or not np.isfinite(values).all():
        raise ValueError("tail calibration requires finite scores")
    insertion = np.searchsorted(known, values, side="left")
    upper_count = len(known) - insertion
    return 1.0 - (upper_count + 1.0) / (len(known) + 1.0)


def quantile_local_rank_blend(
    reference_validation: np.ndarray,
    reference_query: np.ndarray,
    learned_validation: np.ndarray,
    learned_query: np.ndarray,
    *,
    bins: int,
    beta: float,
) -> tuple[np.ndarray, np.ndarray]:
    if int(bins) < 2:
        raise ValueError("local-rank bins must be at least two")
    if not 0.0 <= float(beta) <= 1.0:
        raise ValueError("local-rank beta must lie in [0, 1]")
    validation_reference = np.asarray(reference_validation, dtype=np.float64)
    query_reference = np.asarray(reference_query, dtype=np.float64)
    validation_learned = np.asarray(learned_validation, dtype=np.float64)
    query_learned = np.asarray(learned_query, dtype=np.float64)
    if validation_reference.shape != validation_learned.shape:
        raise ValueError("validation reference and learned risks are incompatible")
    if query_reference.shape != query_learned.shape:
        raise ValueError("query reference and learned risks are incompatible")
    arrays = (
        validation_reference,
        query_reference,
        validation_learned,
        query_learned,
    )
    if any(array.ndim != 1 or not np.isfinite(array).all() for array in arrays):
        raise ValueError("local-rank blending requires finite vectors")
    edges = np.quantile(
        validation_reference, np.linspace(0.0, 1.0, int(bins) + 1)
    )
    edges[0] -= 1e-12
    edges[-1] += 1e-12

    def transform(reference: np.ndarray, learned: np.ndarray) -> np.ndarray:
        index = np.clip(
            np.searchsorted(edges[1:-1], reference, side="right"),
            0,
            int(bins) - 1,
        )
        lower = edges[index]
        upper = edges[index + 1]
        local_reference = np.divide(
            reference - lower,
            upper - lower,
            out=np.zeros_like(reference),
            where=(upper - lower) > 1e-12,
        )
        within_bin = (
            (1.0 - float(beta)) * np.clip(local_reference, 0.0, 1.0)
            + float(beta) * np.clip(learned, 0.0, 1.0) * (1.0 - 1e-9)
        )
        return (index + within_bin) / float(bins)

    return (
        transform(validation_reference, validation_learned),
        transform(query_reference, query_learned),
    )


def task_metrics(task: PseudoUnknownTask, risk: np.ndarray) -> dict[str, float]:
    target = np.asarray(task.target, dtype=bool)
    score = np.asarray(risk, dtype=np.float64)
    return {
        "unknown_auroc": float(roc_auc_score(target.astype(np.int64), score)),
        "unknown_aupr": float(average_precision_score(target.astype(np.int64), score)),
        "unknown_fpr95": float(fpr_at_95_tpr(target.astype(np.int64), score)),
        "oscr": float(
            open_set_classification_rate(
                np.asarray(task.labels, dtype=np.int64),
                np.asarray(task.prediction, dtype=np.int64),
                target,
                score,
            )
        ),
    }


def oriented_gain(
    candidate: dict[str, float], reference: dict[str, float]
) -> dict[str, float]:
    return {
        metric: (
            reference[metric] - candidate[metric]
            if metric == "unknown_fpr95"
            else candidate[metric] - reference[metric]
        )
        for metric in ORIENTED_METRICS
    }


def _summarize_gains(rows: Sequence[dict[str, float]]) -> dict[str, object]:
    by_metric = {
        metric: np.asarray([row[metric] for row in rows], dtype=np.float64)
        for metric in ORIENTED_METRICS
    }
    metric_means = {
        metric: float(values.mean()) for metric, values in by_metric.items()
    }
    metric_minima = {
        metric: float(values.min()) for metric, values in by_metric.items()
    }
    return {
        "metric_mean_oriented_gains": metric_means,
        "metric_minimum_oriented_gains": metric_minima,
        "minimum_metric_mean_gain": float(min(metric_means.values())),
        "mean_metric_mean_gain": float(np.mean(list(metric_means.values()))),
        "minimum_fold_metric_gain": float(min(metric_minima.values())),
    }


def robust_fold_gate(
    learned: dict[str, object], *, minimum_fold_gain: float
) -> dict[str, object]:
    summary = learned.get("selected_summary", {})
    if not isinstance(summary, dict):
        summary = {}
    observed = float(summary.get("minimum_fold_metric_gain", float("-inf")))
    mean_gate = bool(learned.get("passes", False))
    fold_gate = observed >= float(minimum_fold_gain)
    return {
        "passes": bool(mean_gate and fold_gate),
        "mean_gain_gate_passes": mean_gate,
        "fold_stability_gate_passes": fold_gate,
        "minimum_fold_metric_gain": observed,
        "required_minimum_fold_gain": float(minimum_fold_gain),
    }


def cross_fitted_shrinkage(
    tasks: Sequence[PseudoUnknownTask],
    *,
    alphas: Sequence[float] = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0),
    minimum_mean_gain: float = 0.0,
    regularization: float = 0.1,
    seed: int = 0,
    boundary_training: bool = False,
    boundary_hard_pseudo_fraction: float = 0.5,
    boundary_interpolation: float = 0.5,
    boundary_max_per_task: int = 512,
    training_objective: str = "pointwise",
) -> dict[str, object]:
    tasks = tuple(tasks)
    if len(tasks) < 3:
        return {
            "passes": False,
            "fallback_reason": "at least three held-out attack classes are required",
            "selected_alpha": 0.0,
            "folds": [],
            "alpha_summaries": {},
            "final_weights": [],
        }
    alpha_values = sorted({float(value) for value in alphas})
    if not alpha_values or alpha_values[0] < 0.0 or alpha_values[-1] > 1.0:
        raise ValueError("shrinkage alphas must lie in [0, 1]")

    folds = []
    gains_by_alpha: dict[float, list[dict[str, float]]] = {
        alpha: [] for alpha in alpha_values
    }
    for index, task in enumerate(tasks):
        training = tuple(value for offset, value in enumerate(tasks) if offset != index)
        weights = fit_nonnegative_weights(
            training,
            regularization=regularization,
            seed=seed + index,
            boundary_training=boundary_training,
            boundary_hard_pseudo_fraction=boundary_hard_pseudo_fraction,
            boundary_interpolation=boundary_interpolation,
            boundary_max_per_task=boundary_max_per_task,
            training_objective=training_objective,
        )
        raw_learned = np.asarray(task.features, dtype=np.float64) @ weights
        learned_tail = empirical_tail_scores(raw_learned[~task.target], raw_learned)
        reference_metrics = task_metrics(task, task.reference_risk)
        candidates = {}
        for alpha in alpha_values:
            candidate_risk = (
                (1.0 - alpha) * np.asarray(task.reference_risk) + alpha * learned_tail
            )
            candidate_metrics = task_metrics(task, candidate_risk)
            gains = oriented_gain(candidate_metrics, reference_metrics)
            gains_by_alpha[alpha].append(gains)
            candidates[str(alpha)] = {
                "metrics": candidate_metrics,
                "oriented_gains": gains,
            }
        folds.append(
            {
                "task": task.name,
                "training_tasks": [value.name for value in training],
                "weights": weights.tolist(),
                "reference_metrics": reference_metrics,
                "candidates": candidates,
            }
        )

    summaries = {
        alpha: _summarize_gains(gains_by_alpha[alpha]) for alpha in alpha_values
    }
    positive_alphas = [value for value in alpha_values if value > 0.0]
    selected_alpha = max(
        positive_alphas,
        key=lambda alpha: (
            summaries[alpha]["minimum_metric_mean_gain"],
            summaries[alpha]["mean_metric_mean_gain"],
            -alpha,
        ),
    )
    selected_summary = summaries[selected_alpha]
    passes = bool(
        selected_summary["minimum_metric_mean_gain"] > float(minimum_mean_gain)
    )
    final_weights = fit_nonnegative_weights(
        tasks,
        regularization=regularization,
        seed=seed + len(tasks),
        boundary_training=boundary_training,
        boundary_hard_pseudo_fraction=boundary_hard_pseudo_fraction,
        boundary_interpolation=boundary_interpolation,
        boundary_max_per_task=boundary_max_per_task,
        training_objective=training_objective,
    )
    if boundary_training:
        builder = (
            boundary_pairwise_arrays
            if training_objective == "pairwise"
            else boundary_training_arrays
        )
        _, _, training_distribution = builder(
            tasks,
            hard_pseudo_fraction=boundary_hard_pseudo_fraction,
            interpolation=boundary_interpolation,
            max_per_task=boundary_max_per_task,
        )
    else:
        training_distribution = {
            "enabled": False,
            "unknown_or_test_labels_used": False,
        }
    return {
        "passes": passes,
        "fallback_reason": None if passes else "joint four-metric mean-gain gate failed",
        "selection_rule": (
            "leave-one-attack cross-fitted nonnegative logistic weights; choose the "
            "reference shrinkage alpha maximizing the worst oriented mean gain over "
            "AUROC, AUPR, FPR95 and OSCR"
        ),
        "minimum_mean_gain": float(minimum_mean_gain),
        "selected_alpha": float(selected_alpha if passes else 0.0),
        "development_selected_alpha": float(selected_alpha),
        "selected_summary": selected_summary,
        "folds": folds,
        "alpha_summaries": {str(key): value for key, value in summaries.items()},
        "final_weights": final_weights.tolist(),
        "unknown_or_test_labels_used": False,
        "pseudo_unknown_source": (
            "known validation attack labels plus known-only boundary interpolation"
            if boundary_training
            else "known validation attack labels only"
        ),
        "training_distribution": training_distribution,
        "training_objective": training_objective,
    }

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

from .pseudo_unknown_risk import (
    ORIENTED_METRICS,
    PseudoUnknownTask,
    empirical_tail_scores,
    oriented_gain,
    task_metrics,
)


DEFAULT_POWERS = (1, 2, 4)


def monotone_tail_basis(
    features: np.ndarray,
    feature_names: Sequence[str],
    *,
    powers: Sequence[int] = DEFAULT_POWERS,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Build a bounded monotone basis that can emphasize component tails."""
    values = np.asarray(features, dtype=np.float64)
    names = tuple(str(name) for name in feature_names)
    exponent_values = tuple(sorted({int(value) for value in powers}))
    if values.ndim != 2 or values.shape[1] != len(names):
        raise ValueError("tail basis feature names do not match the matrix")
    if not names or len(names) != len(set(names)):
        raise ValueError("tail basis requires unique non-empty feature names")
    if not exponent_values or exponent_values[0] < 1:
        raise ValueError("tail basis powers must be positive integers")
    if not np.isfinite(values).all():
        raise ValueError("tail basis requires finite features")

    bounded = np.clip(values, 0.0, 1.0)
    columns = []
    basis_names = []
    for power in exponent_values:
        columns.append(np.power(bounded, power))
        suffix = "" if power == 1 else f"^{power}"
        basis_names.extend(f"{name}{suffix}" for name in names)

    ordered = np.sort(bounded, axis=1)
    top_count = min(2, bounded.shape[1])
    summaries = np.stack(
        [
            bounded.mean(axis=1),
            bounded.max(axis=1),
            ordered[:, -top_count:].mean(axis=1),
        ],
        axis=1,
    )
    columns.append(summaries)
    basis_names.extend(("summary_mean", "summary_max", "summary_top2_mean"))
    return np.concatenate(columns, axis=1), tuple(basis_names)


def tail_aware_pairwise_arrays(
    tasks: Sequence[PseudoUnknownTask],
    feature_names: Sequence[str],
    *,
    hard_pseudo_fraction: float = 0.5,
    interpolation: float = 0.5,
    max_per_task: int = 512,
    tail_gamma: float = 2.0,
    powers: Sequence[int] = DEFAULT_POWERS,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, object]]:
    if not tasks:
        raise ValueError("at least one pseudo-unknown task is required")
    if not 0.0 < float(hard_pseudo_fraction) <= 1.0:
        raise ValueError("hard pseudo fraction must lie in (0, 1]")
    if not 0.0 < float(interpolation) < 1.0:
        raise ValueError("boundary interpolation must lie in (0, 1)")
    if int(max_per_task) < 1:
        raise ValueError("boundary max per task must be positive")
    if float(tail_gamma) < 0.0:
        raise ValueError("tail gamma must be non-negative")

    pair_values = []
    pair_targets = []
    pair_weights = []
    task_audits = []
    expected_basis_names: tuple[str, ...] | None = None
    for task in tasks:
        features = np.asarray(task.features, dtype=np.float64)
        target = np.asarray(task.target, dtype=bool)
        reference = np.clip(
            np.asarray(task.reference_risk, dtype=np.float64), 0.0, 1.0
        )
        known_index = np.flatnonzero(~target)
        pseudo_index = np.flatnonzero(target)
        pseudo_count = min(
            len(pseudo_index),
            int(max_per_task),
            max(1, int(np.ceil(len(pseudo_index) * float(hard_pseudo_fraction)))),
        )
        hard_pseudo = pseudo_index[
            np.argsort(reference[pseudo_index], kind="stable")[:pseudo_count]
        ]
        known_count = min(len(known_index), int(max_per_task), 2 * pseudo_count)
        hard_known = known_index[
            np.argsort(reference[known_index], kind="stable")[-known_count:]
        ]

        known_features = features[hard_known]
        pseudo_features = features[hard_pseudo]
        known_basis, basis_names = monotone_tail_basis(
            known_features, feature_names, powers=powers
        )
        pseudo_basis, observed_names = monotone_tail_basis(
            pseudo_features, feature_names, powers=powers
        )
        if basis_names != observed_names:
            raise AssertionError("tail basis construction is inconsistent")
        if expected_basis_names is None:
            expected_basis_names = basis_names
        elif expected_basis_names != basis_names:
            raise ValueError("pseudo-unknown tasks use different tail bases")

        median = np.median(known_basis, axis=0)
        scale = np.quantile(known_basis, 0.75, axis=0) - np.quantile(
            known_basis, 0.25, axis=0
        )
        scale = np.where(scale > 1e-6, scale, 1.0)
        neighbors = NearestNeighbors(n_neighbors=1, algorithm="auto")
        neighbors.fit((known_basis - median) / scale)
        nearest = neighbors.kneighbors(
            (pseudo_basis - median) / scale, return_distance=False
        )[:, 0]
        paired_known_basis = known_basis[nearest]

        synthetic_features = (
            (1.0 - float(interpolation)) * known_features[nearest]
            + float(interpolation) * pseudo_features
        )
        synthetic_basis, _ = monotone_tail_basis(
            synthetic_features, feature_names, powers=powers
        )
        differences = np.concatenate(
            [
                pseudo_basis - paired_known_basis,
                synthetic_basis - paired_known_basis,
            ],
            axis=0,
        )
        pseudo_reference = reference[hard_pseudo]
        known_reference = reference[hard_known[nearest]]
        hardness = np.power(
            1.0 + (1.0 - pseudo_reference) + known_reference,
            float(tail_gamma),
        )
        positive_weights = np.concatenate([hardness, 0.5 * hardness])
        pair_values.extend((differences, -differences))
        pair_targets.extend(
            (
                np.ones(len(differences), dtype=np.int64),
                np.zeros(len(differences), dtype=np.int64),
            )
        )
        pair_weights.extend((positive_weights, positive_weights))
        task_audits.append(
            {
                "task": task.name,
                "source_known_samples": int(len(known_index)),
                "source_pseudo_unknown_samples": int(len(pseudo_index)),
                "hard_known_samples": int(known_count),
                "hard_pseudo_unknown_samples": int(pseudo_count),
                "direct_ranking_pairs": int(pseudo_count),
                "synthetic_boundary_pairs": int(pseudo_count),
                "mean_pair_weight": float(positive_weights.mean()),
                "maximum_pair_weight": float(positive_weights.max()),
            }
        )

    values = np.concatenate(pair_values, axis=0)
    targets = np.concatenate(pair_targets)
    weights = np.concatenate(pair_weights)
    return values, targets, weights, {
        "enabled": True,
        "objective": "tail_weighted_monotone_pairwise_logistic_ranking",
        "hard_pseudo_fraction": float(hard_pseudo_fraction),
        "interpolation": float(interpolation),
        "max_per_task": int(max_per_task),
        "tail_gamma": float(tail_gamma),
        "powers": [int(value) for value in sorted({int(v) for v in powers})],
        "basis_names": list(expected_basis_names or ()),
        "ranking_pairs": int(len(targets) // 2),
        "training_samples": int(len(targets)),
        "tasks": task_audits,
        "unknown_or_test_labels_used": False,
    }


def fit_tail_aware_weights(
    tasks: Sequence[PseudoUnknownTask],
    feature_names: Sequence[str],
    *,
    regularization: float = 0.1,
    seed: int = 0,
    hard_pseudo_fraction: float = 0.5,
    interpolation: float = 0.5,
    max_per_task: int = 512,
    tail_gamma: float = 2.0,
    powers: Sequence[int] = DEFAULT_POWERS,
) -> tuple[np.ndarray, dict[str, object]]:
    values, targets, sample_weights, audit = tail_aware_pairwise_arrays(
        tasks,
        feature_names,
        hard_pseudo_fraction=hard_pseudo_fraction,
        interpolation=interpolation,
        max_per_task=max_per_task,
        tail_gamma=tail_gamma,
        powers=powers,
    )
    model = LogisticRegression(
        C=float(regularization),
        class_weight="balanced",
        max_iter=1000,
        random_state=int(seed),
        solver="liblinear",
        fit_intercept=False,
    )
    model.fit(values, targets, sample_weight=sample_weights)
    weights = np.maximum(np.asarray(model.coef_[0], dtype=np.float64), 0.0)
    if weights.sum() < 1e-12:
        weights = np.ones(values.shape[1], dtype=np.float64)
    return weights / weights.sum(), audit


def _gain_summary(rows: Sequence[dict[str, float]]) -> dict[str, object]:
    by_metric = {
        metric: np.asarray([row[metric] for row in rows], dtype=np.float64)
        for metric in ORIENTED_METRICS
    }
    means = {metric: float(values.mean()) for metric, values in by_metric.items()}
    minima = {metric: float(values.min()) for metric, values in by_metric.items()}
    return {
        "metric_mean_oriented_gains": means,
        "metric_minimum_oriented_gains": minima,
        "minimum_metric_mean_gain": float(min(means.values())),
        "mean_metric_mean_gain": float(np.mean(list(means.values()))),
        "minimum_fold_metric_gain": float(min(minima.values())),
    }


def cross_fitted_tail_aware_shrinkage(
    tasks: Sequence[PseudoUnknownTask],
    feature_names: Sequence[str],
    *,
    alphas: Sequence[float] = (0.1, 0.25, 0.5, 0.75, 1.0),
    tail_gammas: Sequence[float] = (0.0, 1.0, 2.0, 4.0),
    minimum_mean_gain: float = 0.0,
    regularization: float = 0.1,
    seed: int = 0,
    hard_pseudo_fraction: float = 0.5,
    interpolation: float = 0.5,
    max_per_task: int = 512,
    powers: Sequence[int] = DEFAULT_POWERS,
) -> dict[str, object]:
    task_values = tuple(tasks)
    if len(task_values) < 3:
        return {
            "passes": False,
            "fallback_reason": "at least three held-out attack classes are required",
            "selected_alpha": 0.0,
            "development_selected_alpha": 0.0,
            "selected_tail_gamma": 0.0,
            "folds": [],
            "candidate_summaries": {},
            "final_weights": [],
            "basis_names": [],
            "unknown_or_test_labels_used": False,
        }
    alpha_values = sorted({float(value) for value in alphas if float(value) > 0.0})
    gamma_values = sorted({float(value) for value in tail_gammas})
    if not alpha_values or alpha_values[-1] > 1.0:
        raise ValueError("tail-aware shrinkage alphas must lie in (0, 1]")
    if not gamma_values or gamma_values[0] < 0.0:
        raise ValueError("tail-aware gamma values must be non-negative")

    gains: dict[tuple[float, float], list[dict[str, float]]] = {
        (gamma, alpha): [] for gamma in gamma_values for alpha in alpha_values
    }
    folds = []
    for index, held_out in enumerate(task_values):
        training = tuple(task for offset, task in enumerate(task_values) if offset != index)
        fold_candidates = {}
        for gamma in gamma_values:
            learned_weights, training_audit = fit_tail_aware_weights(
                training,
                feature_names,
                regularization=regularization,
                seed=seed + index,
                hard_pseudo_fraction=hard_pseudo_fraction,
                interpolation=interpolation,
                max_per_task=max_per_task,
                tail_gamma=gamma,
                powers=powers,
            )
            held_basis, basis_names = monotone_tail_basis(
                held_out.features, feature_names, powers=powers
            )
            raw = held_basis @ learned_weights
            learned_tail = empirical_tail_scores(raw[~held_out.target], raw)
            reference_metrics = task_metrics(held_out, held_out.reference_risk)
            gamma_candidates = {}
            for alpha in alpha_values:
                risk = (
                    (1.0 - alpha) * np.asarray(held_out.reference_risk)
                    + alpha * learned_tail
                )
                metrics = task_metrics(held_out, risk)
                oriented = oriented_gain(metrics, reference_metrics)
                gains[(gamma, alpha)].append(oriented)
                gamma_candidates[str(alpha)] = {
                    "metrics": metrics,
                    "oriented_gains": oriented,
                }
            fold_candidates[str(gamma)] = {
                "weights": learned_weights.tolist(),
                "basis_names": list(basis_names),
                "training_audit": training_audit,
                "candidates": gamma_candidates,
            }
        folds.append(
            {
                "task": held_out.name,
                "training_tasks": [task.name for task in training],
                "candidates": fold_candidates,
            }
        )

    summaries = {
        key: _gain_summary(rows) for key, rows in gains.items()
    }
    selected_gamma, selected_alpha = max(
        summaries,
        key=lambda key: (
            summaries[key]["minimum_metric_mean_gain"],
            summaries[key]["mean_metric_mean_gain"],
            -key[0],
            -key[1],
        ),
    )
    selected_summary = summaries[(selected_gamma, selected_alpha)]
    passes = bool(
        selected_summary["minimum_metric_mean_gain"] > float(minimum_mean_gain)
    )
    final_weights, final_training_audit = fit_tail_aware_weights(
        task_values,
        feature_names,
        regularization=regularization,
        seed=seed + len(task_values),
        hard_pseudo_fraction=hard_pseudo_fraction,
        interpolation=interpolation,
        max_per_task=max_per_task,
        tail_gamma=selected_gamma,
        powers=powers,
    )
    basis_names = final_training_audit["basis_names"]
    return {
        "schema_version": "tail_aware_pairwise_ranking_head_v1",
        "passes": passes,
        "fallback_reason": None if passes else "joint four-metric mean-gain gate failed",
        "selection_rule": (
            "leave-one-known-attack cross-fitted tail-weighted monotone pairwise "
            "head; jointly select tail gamma and reference shrinkage by worst "
            "oriented mean gain over AUROC, AUPR, FPR95 and OSCR"
        ),
        "minimum_mean_gain": float(minimum_mean_gain),
        "selected_alpha": float(selected_alpha if passes else 0.0),
        "development_selected_alpha": float(selected_alpha),
        "selected_tail_gamma": float(selected_gamma),
        "selected_summary": selected_summary,
        "folds": folds,
        "candidate_summaries": {
            f"gamma={gamma},alpha={alpha}": summary
            for (gamma, alpha), summary in summaries.items()
        },
        "final_weights": final_weights.tolist(),
        "basis_names": list(basis_names),
        "base_feature_names": [str(name) for name in feature_names],
        "powers": [int(value) for value in sorted({int(v) for v in powers})],
        "training_distribution": final_training_audit,
        "unknown_or_test_labels_used": False,
        "pseudo_unknown_source": (
            "known validation attack labels plus known-only boundary interpolation"
        ),
        "training_objective": "tail_weighted_monotone_pairwise",
    }


def apply_tail_aware_head(
    features: np.ndarray,
    feature_names: Sequence[str],
    weights: Sequence[float],
    *,
    powers: Sequence[int] = DEFAULT_POWERS,
) -> np.ndarray:
    basis, _ = monotone_tail_basis(features, feature_names, powers=powers)
    weight_values = np.asarray(weights, dtype=np.float64)
    if weight_values.ndim != 1 or weight_values.shape[0] != basis.shape[1]:
        raise ValueError("tail-aware head weights do not match the basis")
    if not np.isfinite(weight_values).all() or np.any(weight_values < 0.0):
        raise ValueError("tail-aware head weights must be finite and non-negative")
    return basis @ weight_values


def selected_tail_aware_fold_metrics(
    result: dict[str, object], fold: dict[str, object]
) -> dict[str, float]:
    if result.get("schema_version") != "tail_aware_pairwise_ranking_head_v1":
        raise ValueError("unexpected tail-aware ranking result schema")
    gamma = str(float(result["selected_tail_gamma"]))
    alpha = str(float(result["development_selected_alpha"]))
    try:
        metrics = fold["candidates"][gamma]["candidates"][alpha]["metrics"]
    except (KeyError, TypeError) as error:
        raise ValueError("tail-aware selected fold metrics are absent") from error
    return {metric: float(metrics[metric]) for metric in ORIENTED_METRICS}

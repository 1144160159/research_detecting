from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from caeos.data import prepare_tabular_open_set
from caeos.foss import FOSSForest
from caeos.hybrid import ConflictAwareHybridClassifier
from caeos.hybrid_open_set import (
    ClassConditionalDiagonalDistance,
    ClassConditionalEmpiricalTailCalibrator,
    EmpiricalTailCalibrator,
    EmpiricalTwoSidedCalibrator,
    ForestLeafRarity,
    KnownKnnDistance,
    KnownLocalOutlierFactor,
    PredictedClassKnnDistance,
    KnownQuantileNormalizer,
    RISK_WEIGHTS,
    evaluate_hybrid_open_set,
    cauchy_combined_risk,
    bonferroni_union_risk,
    hybrid_open_set_components,
    weighted_risk,
)
from caeos.pseudo_unknown_risk import (
    PseudoUnknownTask,
    cross_fitted_shrinkage,
    empirical_tail_scores,
    quantile_local_rank_blend,
    robust_fold_gate,
)
from caeos.continuous_outer_min_p import continuous_outer_min_p
from caeos.pseudo_unknown_gated_continuous import (
    PUG_GATE_V1,
    PUG_RISK_NAME,
    PUG_SELECTION_NAME,
    evaluate_pseudo_unknown_gate,
    select_pug_route,
)
from caeos.tail_aware_ranking import (
    apply_tail_aware_head,
    cross_fitted_tail_aware_shrinkage,
    selected_tail_aware_fold_metrics,
)
from train_hybrid import parse_max_features


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MC7 leave-family-out open-set experiment")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--global-max-features", default="0.5")
    parser.add_argument("--minimum-view-gain", type=float, default=0.002)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument(
        "--split-strategy",
        choices=(
            "random",
            "fingerprint_grouped",
            "capture_grouped",
            "temporal_capture_grouped",
        ),
        default="random",
    )
    parser.add_argument(
        "--risk-selection",
        choices=(
            "fixed_evidence",
            "fixed_entropy",
            "fixed_named",
            "fixed_cauchy_modality_support_union",
            "nested_leave_one_attack",
            "nested_pseudo_unknown_blend",
            "nested_robust_pseudo_unknown_blend",
            "nested_local_rank_pseudo_unknown_blend",
            "nested_boundary_pseudo_unknown_blend",
            "nested_boundary_pairwise_pseudo_unknown_blend",
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
            "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
            PUG_SELECTION_NAME,
            "nested_conflict_gate",
            "nested_modality_gate",
            "nested_modality_support_gate",
            "nested_anchor_conflict_gate",
            "nested_hierarchical_anchor_gate",
            "nested_hierarchical_fallback_gate",
            "nested_hierarchical_joint_gate",
            "nested_density_reliability_gate",
            "nested_structural_partition_gate",
            "nested_structural_support_gate",
        ),
        default="fixed_evidence",
    )
    parser.add_argument(
        "--fixed-risk-name",
        default="",
        help="Predeclared report risk used only with --risk-selection fixed_named.",
    )
    parser.add_argument("--modality-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--conflict-fallback-minimum-gain", type=float, default=0.055)
    parser.add_argument("--joint-fallback-minimum-gain", type=float, default=0.055)
    parser.add_argument("--density-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--density-gate-minimum-known-classes", type=int, default=8)
    parser.add_argument("--density-gate-blend-weight", type=float, default=0.05)
    parser.add_argument("--pseudo-unknown-max-alpha", type=float, default=1.0)
    parser.add_argument("--pseudo-unknown-min-fold-gain", type=float, default=-0.125)
    parser.add_argument("--pseudo-unknown-local-rank-bins", type=int, default=5)
    parser.add_argument("--pseudo-unknown-local-rank-beta", type=float, default=1.0)
    parser.add_argument("--boundary-hard-pseudo-fraction", type=float, default=0.5)
    parser.add_argument("--boundary-interpolation", type=float, default=0.5)
    parser.add_argument("--boundary-max-per-task", type=int, default=512)
    parser.add_argument("--tail-aware-confidence-z", type=float, default=1.645)
    parser.add_argument("--tail-aware-min-metric-lcb-gain", type=float, default=0.0)
    parser.add_argument("--tail-aware-min-aupr-lcb-gain", type=float, default=0.0)
    parser.add_argument("--tail-aware-min-aupr-fold-gain", type=float, default=-0.05)
    parser.add_argument(
        "--boundary-training-objective",
        choices=("pointwise", "pairwise"),
        default="pointwise",
    )
    parser.add_argument("--risk-policy-name", default="")
    parser.add_argument("--structural-gate-minimum-gain", type=float, default=0.02)
    parser.add_argument("--foss-trees", type=int, default=30)
    parser.add_argument("--foss-subsample-size", type=int, default=100)
    parser.add_argument("--foss-candidate-dimensions", type=int, default=5)
    parser.add_argument("--foss-min-samples", type=int, default=1)
    parser.add_argument("--foss-structural-view", action="store_true")
    parser.add_argument(
        "--foss-structural-view-mode",
        choices=("tree", "aggregate"),
        default="tree",
    )
    parser.add_argument(
        "--foss-structural-view-scope",
        choices=("full", "evidence", "support"),
        default="full",
    )
    parser.add_argument("--structural-support-weights", default="0,0.1,0.25,0.5,1.0")
    parser.add_argument("--structural-support-minimum-gain", type=float, default=0.005)
    parser.add_argument(
        "--test-corruption-kind",
        choices=(
            "none",
            "modality_missing",
            "field_missing",
            "row_missing",
            "feature_shuffle",
            "gaussian_drift",
        ),
        default="none",
    )
    parser.add_argument("--test-corruption-modality", type=int, default=0)
    parser.add_argument("--test-corruption-severity", type=float, default=0.0)
    parser.add_argument("--test-corruption-seed", type=int, default=20260717)
    parser.add_argument("--train-label-noise", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def views(dataset) -> list[np.ndarray]:
    return [view.numpy() for view in dataset.views]


def concatenate(dataset) -> np.ndarray:
    return np.concatenate(views(dataset), axis=1)


def apply_training_label_noise(
    labels: np.ndarray, fraction: float, seed: int
) -> tuple[np.ndarray, int]:
    values = np.asarray(labels, dtype=np.int64).copy()
    if not 0.0 <= fraction < 1.0:
        raise ValueError("--train-label-noise must be in [0, 1)")
    classes = np.unique(values)
    if fraction == 0.0:
        return values, 0
    if len(classes) < 2:
        raise ValueError("label noise requires at least two known classes")
    count = min(len(values), max(1, int(round(fraction * len(values)))))
    rng = np.random.default_rng(seed)
    selected = rng.choice(len(values), size=count, replace=False)
    for index in selected:
        alternatives = classes[classes != values[index]]
        values[index] = int(rng.choice(alternatives))
    return values, count


def apply_test_corruption(
    test_views: list[np.ndarray],
    train_views: list[np.ndarray],
    kind: str,
    modality: int,
    severity: float,
    seed: int,
) -> tuple[list[np.ndarray], dict[str, object]]:
    corrupted = [np.asarray(view).copy() for view in test_views]
    if kind == "none":
        if severity != 0.0:
            raise ValueError("none corruption requires severity 0")
        return corrupted, {
            "kind": kind,
            "modality": None,
            "severity": 0.0,
            "seed": seed,
            "affected_entries": 0,
        }
    if not 0 <= modality < len(corrupted):
        raise ValueError("test corruption modality index is out of range")
    if kind == "gaussian_drift":
        if severity <= 0.0:
            raise ValueError("gaussian drift severity must be positive")
    elif kind == "modality_missing":
        if severity not in (0.0, 1.0):
            raise ValueError("modality missing severity must be 0 or 1")
        severity = 1.0
    elif not 0.0 < severity <= 1.0:
        raise ValueError(f"{kind} severity must be in (0, 1]")

    rng = np.random.default_rng(seed)
    target = corrupted[modality]
    affected = 0
    if kind == "modality_missing":
        target.fill(0.0)
        affected = int(target.size)
    elif kind == "field_missing":
        mask = rng.random(target.shape) < severity
        target[mask] = 0.0
        affected = int(mask.sum())
    elif kind == "row_missing":
        mask = rng.random(len(target)) < severity
        target[mask] = 0.0
        affected = int(mask.sum() * target.shape[1])
    elif kind == "feature_shuffle":
        mask = rng.random(len(target)) < severity
        selected = np.flatnonzero(mask)
        if len(selected) > 1:
            target[selected] = target[rng.permutation(selected)]
        affected = int(len(selected) * target.shape[1])
    elif kind == "gaussian_drift":
        scale = np.std(np.asarray(train_views[modality]), axis=0)
        scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
        target += rng.normal(0.0, severity, size=target.shape) * scale
        affected = int(target.size)
    else:
        raise ValueError(f"unsupported test corruption kind: {kind}")
    if not np.isfinite(target).all():
        raise ValueError("test corruption produced non-finite values")
    return corrupted, {
        "kind": kind,
        "modality": modality,
        "severity": float(severity),
        "seed": seed,
        "affected_entries": affected,
    }


def missing_view_mask(
    validation_views: list[np.ndarray],
    query_views: list[np.ndarray],
    quantile: float = 0.99,
    minimum_excess: float = 0.10,
) -> tuple[np.ndarray, list[float]]:
    if len(validation_views) != len(query_views) or not query_views:
        raise ValueError("missing-view detection requires aligned non-empty views")
    masks = []
    thresholds = []
    for validation, query in zip(validation_views, query_views):
        validation_zero = np.mean(np.isclose(validation, 0.0), axis=1)
        query_zero = np.mean(np.isclose(query, 0.0), axis=1)
        threshold = min(
            1.0,
            max(
                float(np.quantile(validation_zero, quantile)),
                float(np.median(validation_zero) + minimum_excess),
            ),
        )
        masks.append((query_zero > threshold + 1e-12) | np.all(np.isclose(query, 0.0), axis=1))
        thresholds.append(threshold)
    return np.stack(masks, axis=1), thresholds


def missing_aware_view_probability(
    view_probability: np.ndarray,
    view_reliability: np.ndarray,
    missing: np.ndarray,
    fallback: np.ndarray,
) -> np.ndarray:
    probability = np.asarray(view_probability, dtype=np.float64)
    reliability = np.asarray(view_reliability, dtype=np.float64)
    missing = np.asarray(missing, dtype=bool)
    if probability.ndim != 3 or reliability.shape != probability.shape[:2]:
        raise ValueError("view probability and reliability shapes are incompatible")
    if missing.shape != probability.shape[:2]:
        raise ValueError("missing-view mask shape is incompatible")
    weights = np.where(missing, 0.0, np.maximum(reliability, 0.0))
    totals = weights.sum(axis=1, keepdims=True)
    fused = np.einsum("nv,nvc->nc", weights, probability)
    available = totals[:, 0] > 1e-12
    fused[available] /= totals[available]
    fused[~available] = np.asarray(fallback, dtype=np.float64)[~available]
    normalizer = np.maximum(fused.sum(axis=1, keepdims=True), 1e-12)
    return fused / normalizer


def missing_aware_cauchy_risk(
    view_risks: np.ndarray, missing: np.ndarray, fallback: np.ndarray
) -> np.ndarray:
    risks = np.asarray(view_risks, dtype=np.float64)
    missing = np.asarray(missing, dtype=bool)
    if risks.ndim != 2 or risks.shape != missing.shape:
        raise ValueError("view risks and missing-view mask shapes are incompatible")
    p_values = np.clip(1.0 - risks, 1e-6, 1.0 - 1e-6)
    terms = np.tan((0.5 - p_values) * np.pi)
    available = ~missing
    counts = available.sum(axis=1)
    statistic = np.zeros(len(risks), dtype=np.float64)
    valid = counts > 0
    statistic[valid] = (terms * available).sum(axis=1)[valid] / counts[valid]
    combined_p = 0.5 - np.arctan(statistic) / np.pi
    result = np.clip(1.0 - combined_p, 0.0, 1.0)
    result[~valid] = np.asarray(fallback, dtype=np.float64)[~valid]
    return result


def missing_aware_max_risk(
    view_risks: np.ndarray, missing: np.ndarray, fallback: np.ndarray
) -> np.ndarray:
    risks = np.asarray(view_risks, dtype=np.float64)
    missing = np.asarray(missing, dtype=bool)
    if risks.ndim != 2 or risks.shape != missing.shape:
        raise ValueError("view risks and missing-view mask shapes are incompatible")
    available = ~missing
    masked = np.where(available, risks, -np.inf)
    result = masked.max(axis=1)
    none_available = ~available.any(axis=1)
    result[none_available] = np.asarray(fallback, dtype=np.float64)[none_available]
    return result


def foss_representation(
    model: FOSSForest, values: np.ndarray, mode: str
) -> np.ndarray:
    if mode == "aggregate":
        return model.transform_aggregated(values)
    return model.transform(values)


def compose_structural_inputs(
    raw_views: list[np.ndarray],
    structural_view: np.ndarray | None,
    scope: str,
) -> tuple[list[np.ndarray], np.ndarray, int | None]:
    model_views = list(raw_views)
    support_views = list(raw_views)
    global_view_count = None
    if structural_view is not None:
        if scope in {"full", "evidence"}:
            model_views.append(structural_view)
        if scope in {"full", "support"}:
            support_views.append(structural_view)
        if scope == "evidence":
            global_view_count = len(raw_views)
    return model_views, np.concatenate(support_views, axis=1), global_view_count


def parse_structural_support_weights(value: str) -> tuple[float, ...]:
    weights = tuple(sorted({float(item) for item in value.split(",") if item.strip()}))
    if not weights or weights[0] < 0.0 or 0.0 not in weights:
        raise ValueError("structural support weights must be non-negative and include 0")
    return weights


def structural_support_risk_name(weight: float) -> str:
    token = ("%.6g" % float(weight)).replace(".", "p")
    return f"structural_support_w{token}"


def structural_support_risk_pairs(
    train_views: list[np.ndarray],
    train_labels: np.ndarray,
    validation_views: list[np.ndarray],
    test_views: list[np.ndarray],
    train_structural: np.ndarray,
    validation_structural: np.ndarray,
    test_structural: np.ndarray,
    weights: tuple[float, ...],
    anchor_index: int | None,
    anchor_weight: float,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    anchor_validation = anchor_test = None
    if anchor_index is not None:
        anchor_model = KnownKnnDistance(neighbors=10)
        anchor_model.fit(train_views[anchor_index])
        anchor_validation = anchor_model.score(validation_views[anchor_index])
        anchor_test = anchor_model.score(test_views[anchor_index])

    result = {}
    for weight in weights:
        train_parts = list(train_views)
        validation_parts = list(validation_views)
        test_parts = list(test_views)
        if weight > 0.0:
            train_parts.append(weight * train_structural)
            validation_parts.append(weight * validation_structural)
            test_parts.append(weight * test_structural)
        train_values = np.concatenate(train_parts, axis=1)
        validation_values = np.concatenate(validation_parts, axis=1)
        test_values = np.concatenate(test_parts, axis=1)
        distance = ClassConditionalDiagonalDistance()
        distance.fit(train_values, train_labels)
        knn = KnownKnnDistance(neighbors=10)
        knn.fit(train_values)
        validation_components = {
            "distance": distance.score(validation_values),
            "knn_distance": knn.score(validation_values),
        }
        test_components = {
            "distance": distance.score(test_values),
            "knn_distance": knn.score(test_values),
        }
        component_names = ["distance", "knn_distance"]
        if anchor_validation is not None and anchor_test is not None:
            validation_components["anchor"] = anchor_validation
            test_components["anchor"] = anchor_test
            component_names.append("anchor")
        calibrator = EmpiricalTailCalibrator()
        calibrator.fit(validation_components)
        validation_tail = calibrator.transform(validation_components)
        test_tail = calibrator.transform(test_components)
        validation_support = bonferroni_union_risk(
            validation_tail, ("distance", "knn_distance")
        )
        test_support = bonferroni_union_risk(
            test_tail, ("distance", "knn_distance")
        )
        if "anchor" in component_names:
            validation_support = (
                (1.0 - anchor_weight) * validation_support
                + anchor_weight * validation_tail["anchor"]
            )
            test_support = (
                (1.0 - anchor_weight) * test_support
                + anchor_weight * test_tail["anchor"]
            )
        result[structural_support_risk_name(weight)] = (
            validation_support,
            test_support,
        )
    return result


def dump_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.std() < 1e-12 or right.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


CONFORMAL_VARIANTS = {
    "cauchy_baseline": ("uncertainty", "distance"),
    "cauchy_conflict": ("uncertainty", "distance", "conflict"),
    "cauchy_all": (
        "uncertainty",
        "distance",
        "conflict",
        "tree_disagreement",
    ),
    "cauchy_evidence": ("conflict", "tree_disagreement"),
    "cauchy_distance_knn": ("distance", "knn_distance"),
    "cauchy_distance_class_knn": ("distance", "class_knn_distance"),
    "cauchy_distance_lof": ("distance", "lof_density"),
    "cauchy_local_support": ("distance", "knn_distance", "leaf_rarity"),
}


BIDIRECTIONAL_VARIANTS = {
    "cauchy_bidirectional": (
        "uncertainty",
        "distance",
        "conflict",
        "tree_disagreement",
    ),
    "cauchy_bidirectional_evidence": (
        "conflict",
        "tree_disagreement",
    ),
    "cauchy_bidirectional_support": (
        "uncertainty",
        "distance",
        "knn_distance",
        "conflict",
        "tree_disagreement",
    ),
}


def mixed_bidirectional_tail(
    upper_tail: dict[str, np.ndarray],
    two_sided_tail: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    result = dict(upper_tail)
    for name in ("uncertainty", "inverse_belief", "inverse_margin", "conflict", "tree_disagreement"):
        result[name] = two_sided_tail[name]
    return result


def candidate_risk(
    name: str,
    normalized: dict[str, np.ndarray],
    tail: dict[str, np.ndarray],
) -> np.ndarray:
    if name in RISK_WEIGHTS:
        return weighted_risk(normalized, RISK_WEIGHTS[name])
    return cauchy_combined_risk(tail, CONFORMAL_VARIANTS[name])


def select_hierarchical_fallback(
    aggregates: dict[str, dict[str, float]], minimum_gain: float,
    challenger: str = "cauchy_baseline",
) -> tuple[str, dict[str, object]]:
    def rank(name: str) -> tuple[float, float, float]:
        values = aggregates[name]
        return (
            values["robust_objective"],
            values["minimum_auroc"],
            values["mean_auroc"],
        )

    first_stage = max(("support_union", "cauchy_evidence"), key=rank)
    if first_stage == "support_union":
        return "anchor_support", {
            "first_stage_selected_risk": first_stage,
            "conflict_fallback_candidate": None,
            "conflict_fallback_gain": 0.0,
        }
    gain = rank(challenger)[0] - rank("cauchy_evidence")[0]
    selected = (
        challenger
        if gain > minimum_gain + 1e-12
        else "cauchy_evidence"
    )
    return selected, {
        "first_stage_selected_risk": first_stage,
        "conflict_fallback_candidate": challenger,
        "conflict_fallback_gain": float(gain),
    }


def select_density_reliability_fallback(
    aggregates: dict[str, dict[str, float]],
    joint_minimum_gain: float,
    density_minimum_gain: float,
    known_class_count: int,
    minimum_known_classes: int,
) -> tuple[str, dict[str, object]]:
    parent, details = select_hierarchical_fallback(
        aggregates,
        joint_minimum_gain,
        challenger="cauchy_all",
    )
    reliable = known_class_count >= minimum_known_classes
    challenger = None
    gain = 0.0
    selected = parent
    if parent == "anchor_support" and reliable:
        challenger = max(
            ("density_support_union", "triple_support_union"),
            key=lambda name: (
                aggregates[name]["robust_objective"],
                aggregates[name]["minimum_auroc"],
                aggregates[name]["mean_auroc"],
            ),
        )
        gain = (
            aggregates[challenger]["robust_objective"]
            - aggregates[parent]["robust_objective"]
        )
        if gain > density_minimum_gain + 1e-12:
            selected = challenger
    return selected, {
        **details,
        "parent_selected_risk": parent,
        "density_reliability_satisfied": reliable,
        "known_class_count": int(known_class_count),
        "minimum_known_classes": int(minimum_known_classes),
        "density_support_candidate": challenger,
        "density_support_candidate_gain": float(gain),
    }


def select_modality_support_fallback(
    aggregates: dict[str, dict[str, float]],
    joint_minimum_gain: float,
    modality_minimum_gain: float,
) -> tuple[str, dict[str, object]]:
    parent, details = select_hierarchical_fallback(
        aggregates,
        joint_minimum_gain,
        challenger="cauchy_all",
    )
    challenger = "modality_support_union"
    gain = (
        aggregates[challenger]["robust_objective"]
        - aggregates[parent]["robust_objective"]
    )
    selected = (
        challenger
        if gain > modality_minimum_gain + 1e-12
        else parent
    )
    return selected, {
        **details,
        "parent_selected_risk": parent,
        "modality_support_candidate": challenger,
        "modality_support_candidate_gain": float(gain),
    }


def select_structural_partition(
    aggregates: dict[str, dict[str, float]],
    joint_minimum_gain: float,
    structural_minimum_gain: float,
) -> tuple[str, dict[str, object]]:
    parent, details = select_hierarchical_fallback(
        aggregates,
        joint_minimum_gain,
        challenger="cauchy_all",
    )
    parent_objective = aggregates[parent]["robust_objective"]
    structural_objective = aggregates["foss_partition"]["robust_objective"]
    structural_gain = structural_objective - parent_objective
    selected = (
        "foss_partition"
        if structural_gain > structural_minimum_gain + 1e-12
        else parent
    )
    return selected, {
        **details,
        "parent_selected_risk": parent,
        "structural_candidate": "foss_partition",
        "structural_candidate_gain": float(structural_gain),
    }


def select_structural_support_weight(
    aggregates: dict[str, dict[str, float]], minimum_gain: float
) -> tuple[str, dict[str, object]]:
    baseline = structural_support_risk_name(0.0)
    if baseline not in aggregates:
        raise ValueError("structural support selection requires the zero-weight baseline")
    best = max(
        aggregates,
        key=lambda name: (
            aggregates[name]["joint_robust_objective"],
            aggregates[name]["oscr_robust_objective"],
            aggregates[name]["auroc_robust_objective"],
            -aggregates[name]["weight"],
        ),
    )
    gain = (
        aggregates[best]["joint_robust_objective"]
        - aggregates[baseline]["joint_robust_objective"]
    )
    selected = best if best != baseline and gain > minimum_gain + 1e-12 else baseline
    return selected, {
        "best_structural_support_candidate": best,
        "structural_support_baseline": baseline,
        "structural_support_gain": float(gain),
        "selected_structural_support_candidate": selected,
    }


def select_nested_risk(
    bundle,
    args: argparse.Namespace,
) -> tuple[str, dict[str, object]]:
    train_views = views(bundle.train)
    validation_views = views(bundle.validation)
    train_labels = bundle.train.labels.numpy()
    validation_labels = bundle.validation.labels.numpy()
    nested_weighted = tuple(
        name
        for name, weights in RISK_WEIGHTS.items()
        if "knn_distance" not in weights
        and "class_knn_distance" not in weights
        and "lof_density" not in weights
        and "leaf_rarity" not in weights
    )
    nested_conformal = tuple(
        name
        for name, components in CONFORMAL_VARIANTS.items()
        if "knn_distance" not in components
        and "class_knn_distance" not in components
        and "lof_density" not in components
        and "leaf_rarity" not in components
    )
    standard_candidates = nested_weighted + nested_conformal
    adaptive_candidates = (
        "support_union",
        "modality_support_union",
        "cauchy_modality_support_union",
        "density_support_union",
        "triple_support_union",
        "conflict_support_union",
    )
    number_of_views = len(train_views) + int(
        args.foss_structural_view
        and args.foss_structural_view_scope in {"full", "evidence"}
    )
    view_candidate_names = tuple(
        f"knn_view_{index}" for index in range(number_of_views)
    )
    anchor_modality = getattr(args, "anchor_support_modality", "")
    anchor_index = (
        bundle.modality_names.index(anchor_modality)
        if anchor_modality in bundle.modality_names
        else None
    )
    anchor_candidates = ("anchor_support",) if anchor_index is not None else ()
    candidate_scores = {
        name: []
        for name in standard_candidates
        + adaptive_candidates
        + view_candidate_names
        + anchor_candidates
        + ("foss_partition",)
    }
    structural_support_weights = (
        parse_structural_support_weights(args.structural_support_weights)
        if args.foss_structural_view
        and args.foss_structural_view_scope == "support"
        else ()
    )
    structural_support_scores = {
        structural_support_risk_name(weight): {"auroc": [], "oscr": []}
        for weight in structural_support_weights
    }
    held_out_reports = []
    feature_names = (
        "uncertainty",
        "inverse_belief",
        "inverse_margin",
        "conflict",
        "tree_disagreement",
        "distance",
        "knn_distance",
        *view_candidate_names,
        "class_knn_distance",
        "lof_density",
    )
    calibration_tasks = []
    pug_fold_comparisons = []

    for held_out in range(1, len(bundle.class_names)):
        train_known = train_labels != held_out
        validation_known = validation_labels != held_out
        validation_pseudo = validation_labels == held_out
        if validation_pseudo.sum() == 0:
            continue
        structural_scores_for_class = {}
        remaining = sorted(set(train_labels[train_known]))
        label_map = {old: new for new, old in enumerate(remaining)}
        auxiliary_train_labels = np.asarray(
            [label_map[value] for value in train_labels[train_known]], dtype=np.int64
        )
        auxiliary_validation_labels = np.asarray(
            [label_map[value] for value in validation_labels[validation_known]],
            dtype=np.int64,
        )
        auxiliary_train_views = [view[train_known] for view in train_views]
        auxiliary_validation_views = [
            view[validation_known] for view in validation_views
        ]
        pseudo_unknown_views = [
            view[validation_pseudo] for view in validation_views
        ]
        auxiliary_raw_train_values = np.concatenate(auxiliary_train_views, axis=1)
        known_raw_values = np.concatenate(auxiliary_validation_views, axis=1)
        pseudo_raw_values = np.concatenate(pseudo_unknown_views, axis=1)
        auxiliary_foss = FOSSForest(
            num_trees=args.foss_trees,
            subsample_size=args.foss_subsample_size,
            candidate_dimensions=args.foss_candidate_dimensions,
            min_samples=args.foss_min_samples,
            seed=args.seed + 4000 + held_out,
        )
        auxiliary_foss.fit(auxiliary_raw_train_values, auxiliary_train_labels)
        _, known_foss_risk, _ = auxiliary_foss.predict(known_raw_values)
        _, pseudo_foss_risk, _ = auxiliary_foss.predict(pseudo_raw_values)
        train_structural = validation_structural = pseudo_structural = None
        if args.foss_structural_view:
            train_structural = foss_representation(
                auxiliary_foss,
                auxiliary_raw_train_values,
                args.foss_structural_view_mode,
            )
            validation_structural = foss_representation(
                auxiliary_foss,
                known_raw_values,
                args.foss_structural_view_mode,
            )
            pseudo_structural = foss_representation(
                auxiliary_foss,
                pseudo_raw_values,
                args.foss_structural_view_mode,
            )
        auxiliary_train_views, auxiliary_train_values, global_view_count = (
            compose_structural_inputs(
                auxiliary_train_views,
                train_structural,
                args.foss_structural_view_scope,
            )
        )
        auxiliary_validation_views, known_support_values, _ = (
            compose_structural_inputs(
                auxiliary_validation_views,
                validation_structural,
                args.foss_structural_view_scope,
            )
        )
        pseudo_unknown_views, pseudo_support_values, _ = compose_structural_inputs(
            pseudo_unknown_views,
            pseudo_structural,
            args.foss_structural_view_scope,
        )

        auxiliary_model = ConflictAwareHybridClassifier(
            estimators=args.estimators,
            seed=args.seed + 1000 + held_out,
            jobs=args.jobs,
            minimum_view_gain=args.minimum_view_gain,
            global_max_features=parse_max_features(args.global_max_features),
            global_seed_offsets=(202, 606),
            global_view_count=global_view_count,
        )
        auxiliary_model.fit(
            auxiliary_train_views,
            auxiliary_train_labels,
            auxiliary_validation_views,
            auxiliary_validation_labels,
        )
        distance_model = ClassConditionalDiagonalDistance()
        distance_model.fit(auxiliary_train_values, auxiliary_train_labels)
        auxiliary_knn = KnownKnnDistance(neighbors=10)
        auxiliary_knn.fit(auxiliary_train_values)
        auxiliary_view_knn = []
        for auxiliary_train_view in auxiliary_train_views:
            view_model = KnownKnnDistance(neighbors=10)
            view_model.fit(auxiliary_train_view)
            auxiliary_view_knn.append(view_model)
        auxiliary_class_knn = PredictedClassKnnDistance(neighbors=10)
        auxiliary_class_knn.fit(auxiliary_train_values, auxiliary_train_labels)
        auxiliary_lof = KnownLocalOutlierFactor(neighbors=20, jobs=args.jobs)
        auxiliary_lof.fit(auxiliary_train_values)
        known_components, known_probability = hybrid_open_set_components(
            auxiliary_model,
            auxiliary_validation_views,
            distance_model,
            known_support_values,
        )
        pseudo_components, pseudo_probability = hybrid_open_set_components(
            auxiliary_model,
            pseudo_unknown_views,
            distance_model,
            pseudo_support_values,
        )
        known_components["knn_distance"] = auxiliary_knn.score(known_support_values)
        pseudo_components["knn_distance"] = auxiliary_knn.score(
            pseudo_support_values
        )
        for index, (view_model, known_view, pseudo_view) in enumerate(
            zip(
                auxiliary_view_knn,
                auxiliary_validation_views,
                pseudo_unknown_views,
            )
        ):
            component_name = f"knn_view_{index}"
            known_components[component_name] = view_model.score(known_view)
            pseudo_components[component_name] = view_model.score(pseudo_view)
        known_components["class_knn_distance"] = auxiliary_class_knn.score(
            known_support_values,
            known_probability.argmax(axis=1),
        )
        pseudo_components["class_knn_distance"] = auxiliary_class_knn.score(
            pseudo_support_values,
            pseudo_probability.argmax(axis=1),
        )
        known_components["lof_density"] = auxiliary_lof.score(known_support_values)
        pseudo_components["lof_density"] = auxiliary_lof.score(
            pseudo_support_values
        )
        if structural_support_weights:
            if (
                train_structural is None
                or validation_structural is None
                or pseudo_structural is None
            ):
                raise RuntimeError("structural support selection requires embeddings")
            support_pairs = structural_support_risk_pairs(
                auxiliary_train_views,
                auxiliary_train_labels,
                auxiliary_validation_views,
                pseudo_unknown_views,
                train_structural,
                validation_structural,
                pseudo_structural,
                structural_support_weights,
                anchor_index,
                float(getattr(args, "anchor_support_weight", 0.15)),
            )
            nested_labels = np.concatenate(
                [
                    auxiliary_validation_labels,
                    np.full(validation_pseudo.sum(), -1, dtype=np.int64),
                ]
            )
            nested_unknown = np.concatenate(
                [
                    np.zeros(validation_known.sum(), dtype=bool),
                    np.ones(validation_pseudo.sum(), dtype=bool),
                ]
            )
            nested_prediction = np.concatenate(
                [
                    known_probability.argmax(axis=1),
                    pseudo_probability.argmax(axis=1),
                ]
            )
            for name, (known_risk, pseudo_risk) in support_pairs.items():
                combined_risk = np.concatenate([known_risk, pseudo_risk])
                threshold = float(np.quantile(known_risk, args.known_acceptance))
                nested_report = evaluate_hybrid_open_set(
                    nested_labels,
                    nested_unknown,
                    nested_prediction,
                    combined_risk,
                    threshold,
                )
                structural_support_scores[name]["auroc"].append(
                    float(nested_report["unknown_auroc"])
                )
                structural_support_scores[name]["oscr"].append(
                    float(nested_report["oscr"])
                )
                structural_scores_for_class[name] = {
                    "unknown_auroc": float(nested_report["unknown_auroc"]),
                    "oscr": float(nested_report["oscr"]),
                }
        normalizer = KnownQuantileNormalizer()
        normalizer.fit(known_components)
        tail_calibrator = EmpiricalTailCalibrator()
        tail_calibrator.fit(known_components)
        known_normalized = normalizer.transform(known_components)
        pseudo_normalized = normalizer.transform(pseudo_components)
        known_tail = tail_calibrator.transform(known_components)
        pseudo_tail = tail_calibrator.transform(pseudo_components)
        two_sided_calibrator = EmpiricalTwoSidedCalibrator()
        two_sided_calibrator.fit(known_components)
        known_two_sided = two_sided_calibrator.transform(known_components)
        pseudo_two_sided = two_sided_calibrator.transform(pseudo_components)
        known_bidirectional = mixed_bidirectional_tail(
            known_tail, known_two_sided
        )
        pseudo_bidirectional = mixed_bidirectional_tail(
            pseudo_tail, pseudo_two_sided
        )
        target = np.concatenate(
            [np.zeros(validation_known.sum()), np.ones(validation_pseudo.sum())]
        )
        feature_matrix = np.concatenate(
            [
                np.stack([known_normalized[name] for name in feature_names], axis=1),
                np.stack([pseudo_normalized[name] for name in feature_names], axis=1),
            ],
            axis=0,
        )
        scores_for_class = {}
        foss_risk = np.concatenate([known_foss_risk, pseudo_foss_risk])
        foss_score = float(roc_auc_score(target, foss_risk))
        candidate_scores["foss_partition"].append(foss_score)
        scores_for_class["foss_partition"] = foss_score
        for name in standard_candidates:
            risk = np.concatenate(
                [
                    candidate_risk(name, known_normalized, known_tail),
                    candidate_risk(name, pseudo_normalized, pseudo_tail),
                ]
            )
            score = float(roc_auc_score(target, risk))
            candidate_scores[name].append(score)
            scores_for_class[name] = score
        for name in view_candidate_names:
            risk = np.concatenate([known_tail[name], pseudo_tail[name]])
            score = float(roc_auc_score(target, risk))
            candidate_scores[name].append(score)
            scores_for_class[name] = score
        if anchor_index is not None:
            inner_support = bonferroni_union_risk(
                known_tail, ("distance", "knn_distance")
            )
            pseudo_support = bonferroni_union_risk(
                pseudo_tail, ("distance", "knn_distance")
            )
            anchor_name = f"knn_view_{anchor_index}"
            anchor_weight = float(getattr(args, "anchor_support_weight", 0.15))
            risk = np.concatenate(
                [
                    (1.0 - anchor_weight) * inner_support
                    + anchor_weight * known_tail[anchor_name],
                    (1.0 - anchor_weight) * pseudo_support
                    + anchor_weight * pseudo_tail[anchor_name],
                ]
            )
            score = float(roc_auc_score(target, risk))
            candidate_scores["anchor_support"].append(score)
            scores_for_class["anchor_support"] = score
        union_definitions = {
            "support_union": (
                known_tail,
                pseudo_tail,
                ("distance", "knn_distance"),
            ),
            "modality_support_union": (
                known_tail,
                pseudo_tail,
                ("distance", *view_candidate_names),
            ),
            "density_support_union": (
                known_tail,
                pseudo_tail,
                ("distance", "lof_density"),
            ),
            "triple_support_union": (
                known_tail,
                pseudo_tail,
                ("distance", "knn_distance", "lof_density"),
            ),
            "conflict_support_union": (
                known_bidirectional,
                pseudo_bidirectional,
                ("distance", "knn_distance", "conflict", "tree_disagreement"),
            ),
        }
        for name, (known_source, pseudo_source, components) in union_definitions.items():
            risk = np.concatenate(
                [
                    bonferroni_union_risk(known_source, components),
                    bonferroni_union_risk(pseudo_source, components),
                ]
            )
            score = float(roc_auc_score(target, risk))
            candidate_scores[name].append(score)
            scores_for_class[name] = score
        known_modality_support = bonferroni_union_risk(
            known_tail, ("distance", *view_candidate_names)
        )
        pseudo_modality_support = bonferroni_union_risk(
            pseudo_tail, ("distance", *view_candidate_names)
        )
        known_cauchy_evidence = cauchy_combined_risk(
            known_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
        )
        pseudo_cauchy_evidence = cauchy_combined_risk(
            pseudo_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
        )
        known_combined_union = bonferroni_union_risk(
            {
                "cauchy_evidence": known_cauchy_evidence,
                "modality_support": known_modality_support,
            },
            ("cauchy_evidence", "modality_support"),
        )
        pseudo_combined_union = bonferroni_union_risk(
            {
                "cauchy_evidence": pseudo_cauchy_evidence,
                "modality_support": pseudo_modality_support,
            },
            ("cauchy_evidence", "modality_support"),
        )
        combined_union_risk = np.concatenate(
            [known_combined_union, pseudo_combined_union]
        )
        combined_union_score = float(roc_auc_score(target, combined_union_risk))
        candidate_scores["cauchy_modality_support_union"].append(
            combined_union_score
        )
        scores_for_class["cauchy_modality_support_union"] = combined_union_score
        if args.risk_selection == PUG_SELECTION_NAME:
            known_pug_continuous = continuous_outer_min_p(
                known_cauchy_evidence, known_modality_support
            )
            pseudo_pug_continuous = continuous_outer_min_p(
                pseudo_cauchy_evidence, pseudo_modality_support
            )
            nested_labels = np.concatenate(
                [
                    auxiliary_validation_labels,
                    np.full(validation_pseudo.sum(), -1, dtype=np.int64),
                ]
            )
            nested_unknown = np.concatenate(
                [
                    np.zeros(validation_known.sum(), dtype=bool),
                    np.ones(validation_pseudo.sum(), dtype=bool),
                ]
            )
            nested_prediction = np.concatenate(
                [
                    known_probability.argmax(axis=1),
                    pseudo_probability.argmax(axis=1),
                ]
            )
            candidate_continuous_risk = np.concatenate(
                [known_pug_continuous, pseudo_pug_continuous]
            )
            reference_threshold = float(
                np.quantile(known_combined_union, args.known_acceptance)
            )
            candidate_threshold = float(
                np.quantile(known_pug_continuous, args.known_acceptance)
            )
            reference_report = evaluate_hybrid_open_set(
                nested_labels,
                nested_unknown,
                nested_prediction,
                combined_union_risk,
                reference_threshold,
            )
            candidate_report = evaluate_hybrid_open_set(
                nested_labels,
                nested_unknown,
                nested_prediction,
                candidate_continuous_risk,
                candidate_threshold,
            )
            fold_metrics = (
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            )
            pug_fold_comparisons.append(
                {
                    "fold": bundle.class_names[held_out],
                    "reference": {
                        name: float(reference_report[name])
                        for name in fold_metrics
                    },
                    "candidate": {
                        name: float(candidate_report[name])
                        for name in fold_metrics
                    },
                }
            )
        calibration_tasks.append(
            PseudoUnknownTask(
                name=bundle.class_names[held_out],
                features=feature_matrix,
                target=target.astype(bool),
                reference_risk=combined_union_risk,
                labels=np.concatenate(
                    [
                        auxiliary_validation_labels,
                        np.full(validation_pseudo.sum(), -1, dtype=np.int64),
                    ]
                ),
                prediction=np.concatenate(
                    [
                        known_probability.argmax(axis=1),
                        pseudo_probability.argmax(axis=1),
                    ]
                ),
            )
        )
        held_out_reports.append(
            {
                "class_index": held_out,
                "class_name": bundle.class_names[held_out],
                "known_validation_samples": int(validation_known.sum()),
                "pseudo_unknown_samples": int(validation_pseudo.sum()),
                "candidate_auroc": scores_for_class,
                "structural_support_candidates": structural_scores_for_class,
            }
        )

    learned_weights = {}
    pseudo_unknown_blend = {}
    if calibration_tasks:
        maximum_alpha = float(getattr(args, "pseudo_unknown_max_alpha", 1.0))
        if not 0.0 < maximum_alpha <= 1.0:
            raise ValueError("--pseudo-unknown-max-alpha must be in (0, 1]")
        alpha_grid = tuple(
            sorted(
                {
                    0.0,
                    maximum_alpha,
                    *(
                        value
                        for value in (0.1, 0.25, 0.5, 0.75, 1.0)
                        if value <= maximum_alpha
                    ),
                }
            )
        )
        if args.risk_selection in {
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
            "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
        }:
            conservative_lcb = (
                args.risk_selection
                == "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend"
            )
            pseudo_unknown_blend = cross_fitted_tail_aware_shrinkage(
                calibration_tasks,
                feature_names,
                alphas=tuple(value for value in alpha_grid if value > 0.0),
                tail_gammas=(0.0, 1.0, 2.0, 4.0),
                minimum_mean_gain=0.0,
                regularization=0.1,
                seed=args.seed + 9000,
                hard_pseudo_fraction=args.boundary_hard_pseudo_fraction,
                interpolation=args.boundary_interpolation,
                max_per_task=args.boundary_max_per_task,
                confidence_z=(args.tail_aware_confidence_z if conservative_lcb else 0.0),
                minimum_metric_lcb_gain=(
                    args.tail_aware_min_metric_lcb_gain if conservative_lcb else None
                ),
                minimum_aupr_lcb_gain=(
                    args.tail_aware_min_aupr_lcb_gain if conservative_lcb else None
                ),
                minimum_aupr_fold_gain=(
                    args.tail_aware_min_aupr_fold_gain if conservative_lcb else None
                ),
            )
        else:
            pseudo_unknown_blend = cross_fitted_shrinkage(
                calibration_tasks,
                alphas=alpha_grid,
                minimum_mean_gain=0.0,
                regularization=0.1,
                seed=args.seed + 9000,
                boundary_training=(
                    args.risk_selection
                    in {
                        "nested_boundary_pseudo_unknown_blend",
                        "nested_boundary_pairwise_pseudo_unknown_blend",
                        PUG_SELECTION_NAME,
                    }
                ),
                boundary_hard_pseudo_fraction=args.boundary_hard_pseudo_fraction,
                boundary_interpolation=args.boundary_interpolation,
                boundary_max_per_task=args.boundary_max_per_task,
                training_objective=(
                    "pairwise"
                    if args.risk_selection
                    in {
                        "nested_boundary_pairwise_pseudo_unknown_blend",
                        PUG_SELECTION_NAME,
                    }
                    else args.boundary_training_objective
                ),
            )
        final_weights = pseudo_unknown_blend.get("final_weights", [])
        if final_weights:
            learned_names = pseudo_unknown_blend.get("basis_names", feature_names)
            learned_weights = {
                name: float(weight)
                for name, weight in zip(learned_names, final_weights)
            }
        selected_alpha = float(
            pseudo_unknown_blend.get("development_selected_alpha", 0.0)
        )
        fold_by_name = {
            value["task"]: value for value in pseudo_unknown_blend.get("folds", [])
        }
        for report in held_out_reports:
            fold = fold_by_name.get(report["class_name"])
            if fold is None:
                continue
            if pseudo_unknown_blend.get("schema_version") in {
                "tail_aware_pairwise_ranking_head_v1",
                "tail_aware_lcb_pairwise_ranking_head_v1",
            }:
                metrics = selected_tail_aware_fold_metrics(
                    pseudo_unknown_blend, fold
                )
            else:
                metrics = fold["candidates"][str(selected_alpha)]["metrics"]
            score = float(metrics["unknown_auroc"])
            report["candidate_auroc"]["pseudo_unknown_learned_blend"] = score

    aggregates = {}
    for name, scores in candidate_scores.items():
        if not scores:
            continue
        mean_score = float(np.mean(scores))
        minimum_score = float(np.min(scores))
        aggregates[name] = {
            "mean_auroc": mean_score,
            "minimum_auroc": minimum_score,
            "robust_objective": 0.5 * mean_score + 0.5 * minimum_score,
        }
    structural_support_aggregates = {}
    for weight in structural_support_weights:
        name = structural_support_risk_name(weight)
        auroc_scores = structural_support_scores[name]["auroc"]
        oscr_scores = structural_support_scores[name]["oscr"]
        if not auroc_scores or not oscr_scores:
            continue
        mean_auroc = float(np.mean(auroc_scores))
        minimum_auroc = float(np.min(auroc_scores))
        mean_oscr = float(np.mean(oscr_scores))
        minimum_oscr = float(np.min(oscr_scores))
        auroc_robust = 0.5 * mean_auroc + 0.5 * minimum_auroc
        oscr_robust = 0.5 * mean_oscr + 0.5 * minimum_oscr
        structural_support_aggregates[name] = {
            "weight": float(weight),
            "mean_auroc": mean_auroc,
            "minimum_auroc": minimum_auroc,
            "auroc_robust_objective": auroc_robust,
            "mean_oscr": mean_oscr,
            "minimum_oscr": minimum_oscr,
            "oscr_robust_objective": oscr_robust,
            "joint_robust_objective": 0.5 * auroc_robust + 0.5 * oscr_robust,
        }
    pug_gate = None
    if args.risk_selection == PUG_SELECTION_NAME:
        if len(pug_fold_comparisons) >= int(PUG_GATE_V1["minimum_fold_count"]):
            pug_gate = evaluate_pseudo_unknown_gate(
                pug_fold_comparisons, PUG_GATE_V1
            )
        else:
            pug_gate = {
                "schema_version": "caeos_pug_pseudo_unknown_gate_v1",
                "fold_count": len(pug_fold_comparisons),
                "passes": False,
                "selected_route": "exact_pairwise_passthrough",
                "reason": "insufficient_pseudo_unknown_folds",
                "selection_uses_unknown_or_test_labels": False,
            }
    if not aggregates:
        return "cauchy_evidence", {
            "fallback_reason": "no eligible known attack class",
            "held_out_reports": held_out_reports,
            "candidate_aggregates": aggregates,
            "structural_support_weight_aggregates": structural_support_aggregates,
            "pug_continuous_outer_gate": pug_gate,
        }
    selected = max(
        aggregates,
        key=lambda name: (
            aggregates[name]["robust_objective"],
            aggregates[name]["minimum_auroc"],
            aggregates[name]["mean_auroc"],
        ),
    )
    return selected, {
        "selection_rule": "0.5 * mean_auroc + 0.5 * minimum_auroc",
        "learned_nonnegative_weights": learned_weights,
        "pseudo_unknown_learned_blend": pseudo_unknown_blend,
        "pseudo_unknown_max_alpha": float(
            getattr(args, "pseudo_unknown_max_alpha", 1.0)
        ),
        "learned_feature_names": list(feature_names),
        "held_out_reports": held_out_reports,
        "candidate_aggregates": aggregates,
        "structural_support_weight_aggregates": structural_support_aggregates,
        "pug_continuous_outer_gate": pug_gate,
    }


def main() -> None:
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    unknown_classes = [
        value.strip() for value in args.unknown_classes.split(",") if value.strip()
    ]
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    args.anchor_support_modality = str(config.get("anchor_support_modality", ""))
    args.anchor_support_weight = float(config.get("anchor_support_weight", 0.15))
    bundle = prepare_tabular_open_set(
        args.csv,
        config,
        unknown_classes,
        args.benign_class,
        args.max_per_class,
        args.chunksize,
        args.seed,
        split_strategy=args.split_strategy,
    )
    raw_train_views = views(bundle.train)
    raw_validation_views = views(bundle.validation)
    raw_test_views = views(bundle.test)
    train_labels, noisy_label_count = apply_training_label_noise(
        bundle.train.labels.numpy(), args.train_label_noise, args.test_corruption_seed
    )
    raw_test_views, test_corruption = apply_test_corruption(
        raw_test_views,
        raw_train_views,
        args.test_corruption_kind,
        args.test_corruption_modality,
        args.test_corruption_severity,
        args.test_corruption_seed,
    )
    raw_training_values = np.concatenate(raw_train_views, axis=1)
    raw_validation_values = np.concatenate(raw_validation_views, axis=1)
    raw_test_values = np.concatenate(raw_test_views, axis=1)
    foss_model = FOSSForest(
        num_trees=args.foss_trees,
        subsample_size=args.foss_subsample_size,
        candidate_dimensions=args.foss_candidate_dimensions,
        min_samples=args.foss_min_samples,
        seed=args.seed,
    )
    foss_model.fit(raw_training_values, train_labels)
    train_structural = validation_structural = test_structural = None
    if args.foss_structural_view:
        train_structural = foss_representation(
            foss_model, raw_training_values, args.foss_structural_view_mode
        )
        validation_structural = foss_representation(
            foss_model, raw_validation_values, args.foss_structural_view_mode
        )
        test_structural = foss_representation(
            foss_model, raw_test_values, args.foss_structural_view_mode
        )
    model_train_views, training_values, global_view_count = compose_structural_inputs(
        raw_train_views, train_structural, args.foss_structural_view_scope
    )
    model_validation_views, validation_values, _ = compose_structural_inputs(
        raw_validation_views,
        validation_structural,
        args.foss_structural_view_scope,
    )
    model_test_views, test_values, _ = compose_structural_inputs(
        raw_test_views, test_structural, args.foss_structural_view_scope
    )
    model_modality_names = bundle.modality_names + (
        ["foss_structural_embedding"]
        if args.foss_structural_view
        and args.foss_structural_view_scope in {"full", "evidence"}
        else []
    )

    model = ConflictAwareHybridClassifier(
        estimators=args.estimators,
        seed=args.seed,
        jobs=args.jobs,
        minimum_view_gain=args.minimum_view_gain,
        global_max_features=parse_max_features(args.global_max_features),
        global_seed_offsets=(202, 606),
        global_view_count=global_view_count,
    )
    start = time.perf_counter()
    model.fit(
        model_train_views,
        train_labels,
        model_validation_views,
        bundle.validation.labels.numpy(),
    )
    distance_model = ClassConditionalDiagonalDistance()
    distance_model.fit(training_values, train_labels)
    knn_model = KnownKnnDistance(neighbors=10)
    knn_model.fit(training_values)
    view_knn_models = []
    for training_view in model_train_views:
        view_model = KnownKnnDistance(neighbors=10)
        view_model.fit(training_view)
        view_knn_models.append(view_model)
    class_knn_model = PredictedClassKnnDistance(neighbors=10)
    class_knn_model.fit(training_values, train_labels)
    lof_model = KnownLocalOutlierFactor(neighbors=20, jobs=args.jobs)
    lof_model.fit(training_values)
    leaf_rarity_model = ForestLeafRarity()
    global_training_values = model._global_values(model_train_views)
    global_validation_values = model._global_values(model_validation_views)
    global_test_values = model._global_values(model_test_views)
    leaf_rarity_model.fit(
        [model.random_forest, model.extra_trees], global_training_values
    )
    validation_components, validation_probability = hybrid_open_set_components(
        model, model_validation_views, distance_model, validation_values
    )
    test_components, test_probability = hybrid_open_set_components(
        model, model_test_views, distance_model, test_values
    )
    validation_components["knn_distance"] = knn_model.score(validation_values)
    test_components["knn_distance"] = knn_model.score(test_values)
    view_knn_components = []
    for index, (view_model, validation_view, test_view) in enumerate(
        zip(view_knn_models, model_validation_views, model_test_views)
    ):
        component_name = f"knn_view_{index}"
        view_knn_components.append(component_name)
        validation_components[component_name] = view_model.score(validation_view)
        test_components[component_name] = view_model.score(test_view)
    validation_components["class_knn_distance"] = class_knn_model.score(
        validation_values, validation_probability.argmax(axis=1)
    )
    test_components["class_knn_distance"] = class_knn_model.score(
        test_values, test_probability.argmax(axis=1)
    )
    validation_components["lof_density"] = lof_model.score(validation_values)
    test_components["lof_density"] = lof_model.score(test_values)
    validation_components["leaf_rarity"] = leaf_rarity_model.score(
        global_validation_values
    )
    test_components["leaf_rarity"] = leaf_rarity_model.score(global_test_values)
    _, validation_foss_risk, _ = foss_model.predict(raw_validation_values)
    _, test_foss_risk, _ = foss_model.predict(raw_test_values)
    validation_components["foss_partition"] = validation_foss_risk
    test_components["foss_partition"] = test_foss_risk
    normalizer = KnownQuantileNormalizer()
    normalizer.fit(validation_components)
    validation_normalized = normalizer.transform(validation_components)
    test_normalized = normalizer.transform(test_components)
    tail_calibrator = EmpiricalTailCalibrator()
    tail_calibrator.fit(validation_components)
    validation_tail = tail_calibrator.transform(validation_components)
    test_tail = tail_calibrator.transform(test_components)
    class_tail_calibrator = ClassConditionalEmpiricalTailCalibrator()
    validation_prediction = validation_probability.argmax(axis=1)
    test_prediction = test_probability.argmax(axis=1)
    class_tail_calibrator.fit(validation_components, validation_prediction)
    validation_class_tail = class_tail_calibrator.transform(
        validation_components, validation_prediction
    )
    test_class_tail = class_tail_calibrator.transform(
        test_components, test_prediction
    )
    two_sided_calibrator = EmpiricalTwoSidedCalibrator()
    two_sided_calibrator.fit(validation_components)
    validation_two_sided = two_sided_calibrator.transform(validation_components)
    test_two_sided = two_sided_calibrator.transform(test_components)
    validation_bidirectional = mixed_bidirectional_tail(
        validation_tail, validation_two_sided
    )
    test_bidirectional = mixed_bidirectional_tail(test_tail, test_two_sided)
    reports = {}
    thresholds = {}
    test_unknown = bundle.test.is_unknown.numpy()
    test_labels = bundle.test.labels.numpy()
    prediction = test_probability.argmax(axis=1)
    for name, weights in RISK_WEIGHTS.items():
        validation_risk = weighted_risk(validation_normalized, weights)
        test_risk = weighted_risk(test_normalized, weights)
        threshold = float(np.quantile(validation_risk, args.known_acceptance))
        thresholds[name] = threshold
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            threshold,
        )
    for name, component_names in CONFORMAL_VARIANTS.items():
        validation_risk = cauchy_combined_risk(
            validation_tail, component_names
        )
        test_risk = cauchy_combined_risk(test_tail, component_names)
        threshold = float(np.quantile(validation_risk, args.known_acceptance))
        thresholds[name] = threshold
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            threshold,
        )
    for name, component_names in BIDIRECTIONAL_VARIANTS.items():
        validation_risk = cauchy_combined_risk(
            validation_bidirectional, component_names
        )
        test_risk = cauchy_combined_risk(test_bidirectional, component_names)
        threshold = float(np.quantile(validation_risk, args.known_acceptance))
        thresholds[name] = threshold
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            threshold,
        )
    validation_support_union = bonferroni_union_risk(
        validation_tail, ("distance", "knn_distance")
    )
    test_support_union = bonferroni_union_risk(
        test_tail, ("distance", "knn_distance")
    )
    thresholds["support_union"] = float(
        np.quantile(validation_support_union, args.known_acceptance)
    )
    reports["support_union"] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        prediction,
        test_support_union,
        thresholds["support_union"],
    )
    anchor_support_risks = None
    if args.anchor_support_modality in bundle.modality_names:
        anchor_index = bundle.modality_names.index(args.anchor_support_modality)
        anchor_component = f"knn_view_{anchor_index}"
        anchor_support_risks = (
            (1.0 - args.anchor_support_weight) * validation_support_union
            + args.anchor_support_weight * validation_tail[anchor_component],
            (1.0 - args.anchor_support_weight) * test_support_union
            + args.anchor_support_weight * test_tail[anchor_component],
        )
        thresholds["anchor_support"] = float(
            np.quantile(anchor_support_risks[0], args.known_acceptance)
        )
        reports["anchor_support"] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            anchor_support_risks[1],
            thresholds["anchor_support"],
        )
    for name, components in {
        "class_support_union": ("distance", "class_knn_distance"),
        "dual_knn_support_union": (
            "distance",
            "knn_distance",
            "class_knn_distance",
        ),
    }.items():
        validation_risk = bonferroni_union_risk(validation_tail, components)
        test_risk = bonferroni_union_risk(test_tail, components)
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    density_support_risks = {}
    for name, components in {
        "density_support_union": ("distance", "lof_density"),
        "triple_support_union": ("distance", "knn_distance", "lof_density"),
    }.items():
        validation_risk = bonferroni_union_risk(validation_tail, components)
        test_risk = bonferroni_union_risk(test_tail, components)
        density_support_risks[name] = (validation_risk, test_risk)
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    modality_risk_definitions = {
        "modality_knn_union": tuple(view_knn_components),
        "modality_support_union": ("distance", *view_knn_components),
    }
    for component_name in view_knn_components:
        validation_risk = validation_tail[component_name]
        test_risk = test_tail[component_name]
        thresholds[component_name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[component_name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[component_name],
        )
    validation_view_risk = np.stack(
        [validation_tail[name] for name in view_knn_components], axis=1
    )
    test_view_risk = np.stack(
        [test_tail[name] for name in view_knn_components], axis=1
    )
    ordered_validation_view_risk = np.sort(validation_view_risk, axis=1)
    ordered_test_view_risk = np.sort(test_view_risk, axis=1)
    continuous_modality_risks = {
        "max_modality_knn": (
            ordered_validation_view_risk[:, -1],
            ordered_test_view_risk[:, -1],
        ),
        "top2_modality_knn": (
            ordered_validation_view_risk[:, -2:].mean(axis=1),
            ordered_test_view_risk[:, -2:].mean(axis=1),
        ),
        "mean_modality_knn": (
            validation_view_risk.mean(axis=1),
            test_view_risk.mean(axis=1),
        ),
    }
    for name, (validation_risk, test_risk) in continuous_modality_risks.items():
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    for name, components in modality_risk_definitions.items():
        validation_risk = bonferroni_union_risk(validation_tail, components)
        test_risk = bonferroni_union_risk(test_tail, components)
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    validation_cauchy_evidence_for_union = cauchy_combined_risk(
        validation_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
    )
    test_cauchy_evidence_for_union = cauchy_combined_risk(
        test_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
    )
    validation_modality_support = bonferroni_union_risk(
        validation_tail, modality_risk_definitions["modality_support_union"]
    )
    test_modality_support = bonferroni_union_risk(
        test_tail, modality_risk_definitions["modality_support_union"]
    )
    validation_cauchy_modality_union = bonferroni_union_risk(
        {
            "cauchy_evidence": validation_cauchy_evidence_for_union,
            "modality_support": validation_modality_support,
        },
        ("cauchy_evidence", "modality_support"),
    )
    test_cauchy_modality_union = bonferroni_union_risk(
        {
            "cauchy_evidence": test_cauchy_evidence_for_union,
            "modality_support": test_modality_support,
        },
        ("cauchy_evidence", "modality_support"),
    )
    union_name = "cauchy_modality_support_union"
    thresholds[union_name] = float(
        np.quantile(validation_cauchy_modality_union, args.known_acceptance)
    )
    reports[union_name] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        prediction,
        test_cauchy_modality_union,
        thresholds[union_name],
    )
    pug_continuous_risks = None
    if args.risk_selection == PUG_SELECTION_NAME:
        validation_pug_continuous = continuous_outer_min_p(
            validation_cauchy_evidence_for_union,
            validation_modality_support,
        )
        test_pug_continuous = continuous_outer_min_p(
            test_cauchy_evidence_for_union,
            test_modality_support,
        )
        pug_continuous_risks = (
            validation_pug_continuous,
            test_pug_continuous,
        )
        thresholds[PUG_RISK_NAME] = float(
            np.quantile(validation_pug_continuous, args.known_acceptance)
        )
        reports[PUG_RISK_NAME] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_pug_continuous,
            thresholds[PUG_RISK_NAME],
        )
    validation_evidence = model.predict_with_evidence(model_validation_views)
    test_evidence = model.predict_with_evidence(model_test_views)
    validation_missing, missing_thresholds = missing_view_mask(
        raw_validation_views, raw_validation_views
    )
    test_missing, _ = missing_view_mask(raw_validation_views, raw_test_views)
    raw_view_count = len(raw_validation_views)
    validation_missing_probability = missing_aware_view_probability(
        validation_evidence["view_probability"][:, :raw_view_count],
        validation_evidence["view_reliability"][:, :raw_view_count],
        validation_missing,
        validation_probability,
    )
    test_missing_probability = missing_aware_view_probability(
        test_evidence["view_probability"][:, :raw_view_count],
        test_evidence["view_reliability"][:, :raw_view_count],
        test_missing,
        test_probability,
    )
    validation_missing_risk = missing_aware_cauchy_risk(
        validation_view_risk, validation_missing, validation_cauchy_modality_union
    )
    test_missing_risk = missing_aware_cauchy_risk(
        test_view_risk, test_missing, test_cauchy_modality_union
    )
    validation_any_missing = validation_missing.any(axis=1)
    test_any_missing = test_missing.any(axis=1)
    validation_missing_risk = np.where(
        validation_any_missing,
        validation_missing_risk,
        validation_cauchy_modality_union,
    )
    test_missing_risk = np.where(
        test_any_missing, test_missing_risk, test_cauchy_modality_union
    )
    validation_missing_prediction = np.where(
        validation_any_missing,
        validation_missing_probability.argmax(axis=1),
        validation_prediction,
    )
    test_missing_prediction = np.where(
        test_any_missing,
        test_missing_probability.argmax(axis=1),
        test_prediction,
    )
    missing_aware_name = "missing_aware_cauchy_modality_support_union"
    thresholds[missing_aware_name] = float(
        np.quantile(validation_missing_risk, args.known_acceptance)
    )
    reports[missing_aware_name] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        test_missing_prediction,
        test_missing_risk,
        thresholds[missing_aware_name],
    )
    validation_missing_max_risk = missing_aware_max_risk(
        validation_view_risk,
        validation_missing,
        validation_cauchy_modality_union,
    )
    test_missing_max_risk = missing_aware_max_risk(
        test_view_risk, test_missing, test_cauchy_modality_union
    )
    missing_max_name = "missing_aware_max_modality_knn"
    thresholds[missing_max_name] = float(
        np.quantile(validation_missing_max_risk, args.known_acceptance)
    )
    reports[missing_max_name] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        prediction,
        test_missing_max_risk,
        thresholds[missing_max_name],
    )
    missing_aware_diagnostics = {
        "zero_fraction_thresholds": missing_thresholds,
        "validation_any_missing_rate": float(validation_any_missing.mean()),
        "test_any_missing_rate": float(test_any_missing.mean()),
        "validation_view_missing_rates": validation_missing.mean(axis=0).tolist(),
        "test_view_missing_rates": test_missing.mean(axis=0).tolist(),
        "uses_unknown_or_test_labels": False,
    }
    for name, components in {
        "cauchy_modality_knn": tuple(view_knn_components),
        "cauchy_modality_support": ("distance", *view_knn_components),
    }.items():
        validation_risk = cauchy_combined_risk(validation_tail, components)
        test_risk = cauchy_combined_risk(test_tail, components)
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    for name, components in {
        "mondrian_support_union": ("distance", "knn_distance"),
        "mondrian_class_support_union": (
            "distance",
            "class_knn_distance",
        ),
    }.items():
        validation_risk = bonferroni_union_risk(
            validation_class_tail, components
        )
        test_risk = bonferroni_union_risk(test_class_tail, components)
        thresholds[name] = float(
            np.quantile(validation_risk, args.known_acceptance)
        )
        reports[name] = evaluate_hybrid_open_set(
            test_labels,
            test_unknown,
            prediction,
            test_risk,
            thresholds[name],
        )
    validation_conflict_support_union = bonferroni_union_risk(
        validation_bidirectional,
        ("distance", "knn_distance", "conflict", "tree_disagreement"),
    )
    test_conflict_support_union = bonferroni_union_risk(
        test_bidirectional,
        ("distance", "knn_distance", "conflict", "tree_disagreement"),
    )
    thresholds["conflict_support_union"] = float(
        np.quantile(
            validation_conflict_support_union, args.known_acceptance
        )
    )
    reports["conflict_support_union"] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        prediction,
        test_conflict_support_union,
        thresholds["conflict_support_union"],
    )
    thresholds["foss_partition"] = float(
        np.quantile(validation_foss_risk, args.known_acceptance)
    )
    reports["foss_partition"] = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        prediction,
        test_foss_risk,
        thresholds["foss_partition"],
    )
    structural_support_pairs = {}
    if args.foss_structural_view and args.foss_structural_view_scope == "support":
        if (
            train_structural is None
            or validation_structural is None
            or test_structural is None
        ):
            raise RuntimeError("structural support reports require embeddings")
        structural_anchor_index = (
            bundle.modality_names.index(args.anchor_support_modality)
            if args.anchor_support_modality in bundle.modality_names
            else None
        )
        structural_support_pairs = structural_support_risk_pairs(
            raw_train_views,
            train_labels,
            raw_validation_views,
            raw_test_views,
            train_structural,
            validation_structural,
            test_structural,
            parse_structural_support_weights(args.structural_support_weights),
            structural_anchor_index,
            args.anchor_support_weight,
        )
        for name, (validation_risk, test_risk) in structural_support_pairs.items():
            thresholds[name] = float(
                np.quantile(validation_risk, args.known_acceptance)
            )
            reports[name] = evaluate_hybrid_open_set(
                test_labels,
                test_unknown,
                prediction,
                test_risk,
                thresholds[name],
            )
    component_auroc = {
        name: reports[name]["unknown_auroc"]
        for name in ("msp", "entropy", "distance", "conflict", "tree_disagreement")
    }
    component_auroc["knn_distance"] = float(
        roc_auc_score(test_unknown.astype(np.int64), test_components["knn_distance"])
    )
    for component_name in view_knn_components:
        component_auroc[component_name] = float(
            roc_auc_score(
                test_unknown.astype(np.int64), test_components[component_name]
            )
        )
    component_auroc["class_knn_distance"] = float(
        roc_auc_score(
            test_unknown.astype(np.int64),
            test_components["class_knn_distance"],
        )
    )
    component_auroc["lof_density"] = float(
        roc_auc_score(test_unknown.astype(np.int64), test_components["lof_density"])
    )
    component_auroc["leaf_rarity"] = float(
        roc_auc_score(test_unknown.astype(np.int64), test_components["leaf_rarity"])
    )
    component_auroc["foss_partition"] = float(
        roc_auc_score(test_unknown.astype(np.int64), test_foss_risk)
    )
    known_test = ~test_unknown
    component_diagnostics = {
        "validation_conflict_uncertainty_correlation": safe_correlation(
            validation_components["conflict"],
            validation_components["uncertainty"],
        ),
        "known_test_conflict_uncertainty_correlation": safe_correlation(
            test_components["conflict"][known_test],
            test_components["uncertainty"][known_test],
        ),
        "unknown_test_conflict_uncertainty_correlation": safe_correlation(
            test_components["conflict"][test_unknown],
            test_components["uncertainty"][test_unknown],
        ),
        "mean_known_conflict": float(test_components["conflict"][known_test].mean()),
        "mean_unknown_conflict": float(test_components["conflict"][test_unknown].mean()),
        "mean_known_uncertainty": float(test_components["uncertainty"][known_test].mean()),
        "mean_unknown_uncertainty": float(test_components["uncertainty"][test_unknown].mean()),
    }
    selected_risk = "cauchy_evidence"
    density_reliability_blend_risks = None
    pseudo_unknown_blend_risks = None
    pseudo_unknown_blend_name = None
    pseudo_unknown_local_rank_risks = None
    risk_selection_details = {"selection_rule": "fixed_evidence"}
    if args.risk_selection == "fixed_entropy":
        selected_risk = "entropy"
        risk_selection_details = {
            "selection_rule": "fixed predictive entropy risk",
            "unknown_or_test_labels_used_for_selection": False,
        }
    elif args.risk_selection == "fixed_named":
        fixed_risk_name = str(args.fixed_risk_name).strip()
        if not fixed_risk_name:
            raise ValueError("--fixed-risk-name is required for fixed_named")
        if fixed_risk_name not in reports:
            raise ValueError(
                f"fixed risk {fixed_risk_name!r} is not available in reports"
            )
        selected_risk = fixed_risk_name
        risk_selection_details = {
            "selection_rule": f"predeclared fixed risk: {fixed_risk_name}",
            "fixed_risk_name": fixed_risk_name,
            "unknown_or_test_labels_used_for_selection": False,
        }
    elif args.risk_selection == "fixed_cauchy_modality_support_union":
        selected_risk = "cauchy_modality_support_union"
        risk_selection_details = {
            "selection_rule": (
                "fixed Bonferroni union of known-calibrated Cauchy evidence "
                "and all-modality support risks"
            ),
            "unknown_or_test_labels_used_for_selection": False,
        }
    elif args.risk_selection in {
        "nested_leave_one_attack",
        "nested_pseudo_unknown_blend",
        "nested_robust_pseudo_unknown_blend",
        "nested_local_rank_pseudo_unknown_blend",
        "nested_boundary_pseudo_unknown_blend",
        "nested_boundary_pairwise_pseudo_unknown_blend",
        "nested_tail_aware_pairwise_pseudo_unknown_blend",
        "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
        PUG_SELECTION_NAME,
        "nested_conflict_gate",
        "nested_modality_gate",
        "nested_modality_support_gate",
        "nested_anchor_conflict_gate",
        "nested_hierarchical_anchor_gate",
        "nested_hierarchical_fallback_gate",
        "nested_hierarchical_joint_gate",
        "nested_density_reliability_gate",
        "nested_structural_partition_gate",
        "nested_structural_support_gate",
    }:
        selected_risk, risk_selection_details = select_nested_risk(bundle, args)
        if args.risk_selection in {
            "nested_pseudo_unknown_blend",
            "nested_robust_pseudo_unknown_blend",
            "nested_local_rank_pseudo_unknown_blend",
            "nested_boundary_pseudo_unknown_blend",
            "nested_boundary_pairwise_pseudo_unknown_blend",
            "nested_tail_aware_pairwise_pseudo_unknown_blend",
            "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
            PUG_SELECTION_NAME,
        }:
            learned = risk_selection_details["pseudo_unknown_learned_blend"]
            robust_gate = None
            gate_passes = bool(learned.get("passes"))
            if args.risk_selection in {
                "nested_robust_pseudo_unknown_blend",
                "nested_local_rank_pseudo_unknown_blend",
                "nested_boundary_pseudo_unknown_blend",
                "nested_boundary_pairwise_pseudo_unknown_blend",
                "nested_tail_aware_pairwise_pseudo_unknown_blend",
                "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
                PUG_SELECTION_NAME,
            }:
                robust_gate = robust_fold_gate(
                    learned,
                    minimum_fold_gain=args.pseudo_unknown_min_fold_gain,
                )
                gate_passes = bool(robust_gate["passes"])
            learned_endpoint = (
                "pseudo_unknown_local_rank_blend"
                if args.risk_selection == "nested_local_rank_pseudo_unknown_blend"
                else (
                    "pseudo_unknown_tail_aware_blend"
                    if args.risk_selection
                    in {
                        "nested_tail_aware_pairwise_pseudo_unknown_blend",
                        "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
                    }
                    else "pseudo_unknown_learned_blend"
                )
            )
            selected_risk = learned_endpoint if gate_passes else "cauchy_modality_support_union"
            if robust_gate is None:
                if args.risk_selection == "nested_boundary_pseudo_unknown_blend":
                    risk_selection_details["selection_rule"] = (
                        "training-time leave-one-known-attack cross-fitted boundary "
                        "hard-negative risk learning; fall back unless AUROC, AUPR, "
                        "FPR95 and OSCR oriented mean gains are all positive"
                    )
                else:
                    risk_selection_details["selection_rule"] = (
                        "training-time leave-one-known-attack cross-fitted risk learning; "
                        "fall back to cauchy_modality_support_union unless AUROC, AUPR, "
                        "FPR95 and OSCR oriented mean gains are all positive"
                    )
            else:
                if args.risk_selection in {
                    "nested_boundary_pseudo_unknown_blend",
                    "nested_boundary_pairwise_pseudo_unknown_blend",
                    "nested_tail_aware_pairwise_pseudo_unknown_blend",
                    "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
                    PUG_SELECTION_NAME,
                }:
                    evidence_rule = (
                        "known-only one-sided confidence-bound and AUPR-tail gates"
                        if args.risk_selection
                        == "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend"
                        else "positive four-metric mean gains"
                    )
                    risk_selection_details["selection_rule"] = (
                        "training-time leave-one-known-attack boundary hard-negative "
                        "%s risk learning; require %s and "
                        "worst fold-metric gain >= %.6f, otherwise fall back to the "
                        "frozen reference"
                        % (
                            "pairwise-ranking"
                            if args.risk_selection
                            in {
                                "nested_boundary_pairwise_pseudo_unknown_blend",
                                "nested_tail_aware_pairwise_pseudo_unknown_blend",
                                "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
                                PUG_SELECTION_NAME,
                            }
                            else "pointwise",
                            evidence_rule,
                            args.pseudo_unknown_min_fold_gain,
                        )
                    )
                else:
                    risk_selection_details["selection_rule"] = (
                        "training-time leave-one-known-attack cross-fitted risk learning; "
                        "require positive four-metric mean gains and worst fold-metric "
                        "gain >= %.6f, otherwise fall back to the frozen reference"
                        % args.pseudo_unknown_min_fold_gain
                    )
                risk_selection_details["pseudo_unknown_robust_fold_gate"] = robust_gate
                if args.risk_selection == "nested_local_rank_pseudo_unknown_blend":
                    risk_selection_details["pseudo_unknown_local_rank"] = {
                        "bins": int(args.pseudo_unknown_local_rank_bins),
                        "beta": float(args.pseudo_unknown_local_rank_beta),
                        "global_reference_bin_order_preserved": True,
                    }
            risk_selection_details["pseudo_unknown_gate_passes"] = gate_passes
            if args.risk_selection == PUG_SELECTION_NAME:
                pug_gate = risk_selection_details["pug_continuous_outer_gate"]
                pug_route = select_pug_route(selected_risk, pug_gate)
                selected_risk = pug_route["selected_risk"]
                risk_selection_details.update(
                    {
                        **pug_route,
                        "selection_rule": (
                            "first preserve the frozen boundary-pairwise "
                            "pseudo-unknown route; only when it falls back to "
                            "cauchy_modality_support_union may the fixed "
                            "multi-metric leave-one-known-attack PUG gate select "
                            "continuous outer min-p, otherwise pass Pairwise "
                            "through exactly"
                        ),
                    }
                )
        elif args.risk_selection == "nested_conflict_gate":
            eligible = ("support_union", "cauchy_evidence")
            aggregates = risk_selection_details["candidate_aggregates"]
            selected_risk = max(
                eligible,
                key=lambda name: (
                    aggregates[name]["robust_objective"],
                    aggregates[name]["minimum_auroc"],
                    aggregates[name]["mean_auroc"],
                ),
            )
            risk_selection_details["selection_rule"] = (
                "nested conflict gate over support_union and cauchy_evidence"
            )
        elif args.risk_selection == "nested_modality_gate":
            aggregates = risk_selection_details["candidate_aggregates"]
            rank = lambda name: (
                aggregates[name]["robust_objective"],
                aggregates[name]["minimum_auroc"],
                aggregates[name]["mean_auroc"],
            )
            hybrid = max(("support_union", "cauchy_evidence"), key=rank)
            view_names = tuple(
                f"knn_view_{index}" for index in range(len(model_modality_names))
            )
            best_view = max(view_names, key=rank)
            gain = (
                aggregates[best_view]["robust_objective"]
                - aggregates[hybrid]["robust_objective"]
            )
            selected_risk = (
                best_view
                if gain > args.modality_gate_minimum_gain
                else hybrid
            )
            risk_selection_details["selection_rule"] = (
                "nested modality gate; view requires robust-objective gain > %.6f"
                % args.modality_gate_minimum_gain
            )
            risk_selection_details["best_hybrid_candidate"] = hybrid
            risk_selection_details["best_view_candidate"] = best_view
            risk_selection_details["view_candidate_gain"] = float(gain)
        elif args.risk_selection == "nested_modality_support_gate":
            aggregates = risk_selection_details["candidate_aggregates"]
            selected_risk, modality_details = select_modality_support_fallback(
                aggregates,
                args.joint_fallback_minimum_gain,
                args.modality_gate_minimum_gain,
            )
            risk_selection_details.update(modality_details)
            risk_selection_details["selection_rule"] = (
                "v1.4.4 hierarchical joint parent; select the distance plus "
                "all-modality KNN Bonferroni union only when its leave-one-known-"
                "class robust-objective gain exceeds %.6f"
                % args.modality_gate_minimum_gain
            )
        elif args.risk_selection == "nested_anchor_conflict_gate":
            if "anchor_support" not in reports:
                raise ValueError(
                    "nested_anchor_conflict_gate requires anchor_support_modality"
                )
            aggregates = risk_selection_details["candidate_aggregates"]
            eligible = ("anchor_support", "cauchy_evidence")
            selected_risk = max(
                eligible,
                key=lambda name: (
                    aggregates[name]["robust_objective"],
                    aggregates[name]["minimum_auroc"],
                    aggregates[name]["mean_auroc"],
                ),
            )
            risk_selection_details["selection_rule"] = (
                "nested conflict gate over anchor_support and cauchy_evidence"
            )
        elif args.risk_selection == "nested_structural_support_gate":
            aggregates = risk_selection_details["candidate_aggregates"]
            parent_risk, fallback_details = select_hierarchical_fallback(
                aggregates,
                args.joint_fallback_minimum_gain,
                challenger="cauchy_all",
            )
            selected_risk = parent_risk
            risk_selection_details.update(fallback_details)
            if parent_risk == "anchor_support":
                weight_aggregates = risk_selection_details[
                    "structural_support_weight_aggregates"
                ]
                weight_risk, weight_details = select_structural_support_weight(
                    weight_aggregates,
                    args.structural_support_minimum_gain,
                )
                risk_selection_details.update(weight_details)
                selected_risk = weight_risk
            risk_selection_details["parent_selected_risk"] = parent_risk
            risk_selection_details["selection_rule"] = (
                "v1.4.4 hierarchical joint parent; on anchor support only, "
                "select structural weight by equal AUROC/OSCR robust objective "
                "with gain > %.6f over zero weight"
                % args.structural_support_minimum_gain
            )
        elif args.risk_selection == "nested_density_reliability_gate":
            aggregates = risk_selection_details["candidate_aggregates"]
            density_endpoint, density_details = select_density_reliability_fallback(
                aggregates,
                args.joint_fallback_minimum_gain,
                args.density_gate_minimum_gain,
                len(bundle.class_names),
                args.density_gate_minimum_known_classes,
            )
            risk_selection_details.update(density_details)
            parent = density_details["parent_selected_risk"]
            if density_endpoint != parent:
                if not 0.0 <= args.density_gate_blend_weight <= 1.0:
                    raise ValueError("density gate blend weight must be in [0, 1]")
                if parent != "anchor_support" or anchor_support_risks is None:
                    raise RuntimeError("density blend requires anchor support parent")
                candidate_risks = density_support_risks[density_endpoint]
                weight = args.density_gate_blend_weight
                density_reliability_blend_risks = (
                    (1.0 - weight) * anchor_support_risks[0]
                    + weight * candidate_risks[0],
                    (1.0 - weight) * anchor_support_risks[1]
                    + weight * candidate_risks[1],
                )
                selected_risk = "density_reliability_blend"
                thresholds[selected_risk] = float(
                    np.quantile(
                        density_reliability_blend_risks[0],
                        args.known_acceptance,
                    )
                )
                reports[selected_risk] = evaluate_hybrid_open_set(
                    test_labels,
                    test_unknown,
                    prediction,
                    density_reliability_blend_risks[1],
                    thresholds[selected_risk],
                )
            else:
                selected_risk = parent
            risk_selection_details["density_support_endpoint"] = density_endpoint
            risk_selection_details["density_gate_blend_weight"] = float(
                args.density_gate_blend_weight
            )
            risk_selection_details["selection_rule"] = (
                "v1.4.4 hierarchical joint parent; on reliable anchor-support "
                "problems with at least %d known classes, blend weight %.6f of "
                "the best LOF density support candidate only when robust-objective "
                "gain > %.6f"
                % (
                    args.density_gate_minimum_known_classes,
                    args.density_gate_blend_weight,
                    args.density_gate_minimum_gain,
                )
            )
        elif args.risk_selection in {
            "nested_hierarchical_anchor_gate",
            "nested_hierarchical_fallback_gate",
            "nested_hierarchical_joint_gate",
            "nested_structural_partition_gate",
        }:
            if "anchor_support" not in reports:
                raise ValueError(
                    "nested_hierarchical_anchor_gate requires anchor_support_modality"
                )
            aggregates = risk_selection_details["candidate_aggregates"]
            if args.risk_selection == "nested_hierarchical_anchor_gate":
                first_stage = max(
                    ("support_union", "cauchy_evidence"),
                    key=lambda name: (
                        aggregates[name]["robust_objective"],
                        aggregates[name]["minimum_auroc"],
                        aggregates[name]["mean_auroc"],
                    ),
                )
                selected_risk = (
                    "anchor_support"
                    if first_stage == "support_union"
                    else "cauchy_evidence"
                )
                risk_selection_details["first_stage_selected_risk"] = first_stage
                risk_selection_details["selection_rule"] = (
                    "original nested conflict gate followed by deterministic anchor "
                    "augmentation only on the support path"
                )
            elif args.risk_selection == "nested_hierarchical_fallback_gate":
                selected_risk, fallback_details = select_hierarchical_fallback(
                    aggregates, args.conflict_fallback_minimum_gain
                )
                risk_selection_details.update(fallback_details)
                risk_selection_details["selection_rule"] = (
                    "hierarchical anchor gate with cauchy_baseline fallback on the "
                    "conflict branch when robust-objective gain > %.6f"
                    % args.conflict_fallback_minimum_gain
                )
            elif args.risk_selection == "nested_hierarchical_joint_gate":
                selected_risk, fallback_details = select_hierarchical_fallback(
                    aggregates,
                    args.joint_fallback_minimum_gain,
                    challenger="cauchy_all",
                )
                risk_selection_details.update(fallback_details)
                risk_selection_details["selection_rule"] = (
                    "hierarchical anchor gate with joint uncertainty-distance-"
                    "conflict-disagreement fallback on the conflict branch when "
                    "robust-objective gain > %.6f"
                    % args.joint_fallback_minimum_gain
                )
            else:
                selected_risk, structural_details = select_structural_partition(
                    aggregates,
                    args.joint_fallback_minimum_gain,
                    args.structural_gate_minimum_gain,
                )
                risk_selection_details.update(structural_details)
                risk_selection_details.update(
                    {
                        "selection_rule": (
                            "v1.4.4 hierarchical joint parent with FOSS random-"
                            "partition representation only when nested robust-"
                            "objective gain > %.6f"
                            % args.structural_gate_minimum_gain
                        ),
                    }
                )
        learned_weights = risk_selection_details.get(
            "learned_nonnegative_weights", {}
        )
        if learned_weights:
            learned_details = risk_selection_details.get(
                "pseudo_unknown_learned_blend", {}
            )
            tail_aware = (
                learned_details.get("schema_version")
                in {
                    "tail_aware_pairwise_ranking_head_v1",
                    "tail_aware_lcb_pairwise_ranking_head_v1",
                }
            )
            if tail_aware:
                base_feature_names = tuple(learned_details["base_feature_names"])
                validation_feature_matrix = np.stack(
                    [validation_normalized[name] for name in base_feature_names],
                    axis=1,
                )
                test_feature_matrix = np.stack(
                    [test_normalized[name] for name in base_feature_names], axis=1
                )
                final_weights = learned_details["final_weights"]
                powers = learned_details["powers"]
                validation_raw_learned = apply_tail_aware_head(
                    validation_feature_matrix,
                    base_feature_names,
                    final_weights,
                    powers=powers,
                )
                test_raw_learned = apply_tail_aware_head(
                    test_feature_matrix,
                    base_feature_names,
                    final_weights,
                    powers=powers,
                )
                pseudo_unknown_blend_name = "pseudo_unknown_tail_aware_blend"
            else:
                validation_raw_learned = weighted_risk(
                    validation_normalized, learned_weights
                )
                test_raw_learned = weighted_risk(test_normalized, learned_weights)
                pseudo_unknown_blend_name = "pseudo_unknown_learned_blend"
            validation_learned_tail = empirical_tail_scores(
                validation_raw_learned, validation_raw_learned
            )
            test_learned_tail = empirical_tail_scores(
                validation_raw_learned, test_raw_learned
            )
            alpha = float(learned_details.get("selected_alpha", 0.0))
            validation_risk = (
                (1.0 - alpha) * validation_cauchy_modality_union
                + alpha * validation_learned_tail
            )
            test_risk = (
                (1.0 - alpha) * test_cauchy_modality_union
                + alpha * test_learned_tail
            )
            pseudo_unknown_blend_risks = (validation_risk, test_risk)
            threshold = float(np.quantile(validation_risk, args.known_acceptance))
            thresholds[pseudo_unknown_blend_name] = threshold
            reports[pseudo_unknown_blend_name] = evaluate_hybrid_open_set(
                test_labels,
                test_unknown,
                prediction,
                test_risk,
                threshold,
            )
            if not tail_aware:
                local_validation_risk, local_test_risk = quantile_local_rank_blend(
                    validation_cauchy_modality_union,
                    test_cauchy_modality_union,
                    validation_learned_tail,
                    test_learned_tail,
                    bins=args.pseudo_unknown_local_rank_bins,
                    beta=args.pseudo_unknown_local_rank_beta,
                )
                pseudo_unknown_local_rank_risks = (
                    local_validation_risk,
                    local_test_risk,
                )
                local_threshold = float(
                    np.quantile(local_validation_risk, args.known_acceptance)
                )
                thresholds["pseudo_unknown_local_rank_blend"] = local_threshold
                reports["pseudo_unknown_local_rank_blend"] = evaluate_hybrid_open_set(
                    test_labels,
                    test_unknown,
                    prediction,
                    local_test_risk,
                    local_threshold,
                )

    risk_selection_details.setdefault(
        "unknown_or_test_labels_used_for_selection", False
    )

    result = {
        "model": "mc7_stable_open_set",
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {
            "train": len(bundle.train),
            "validation": len(bundle.validation),
            "test": len(bundle.test),
            "test_unknown": int(bundle.test.is_unknown.sum()),
        },
        "corruption_protocol": {
            "train_label_noise_fraction": args.train_label_noise,
            "train_label_noise_count": noisy_label_count,
            "test_corruption": test_corruption,
            "train_only_label_corruption": True,
            "validation_is_clean": True,
            "test_only_feature_corruption": True,
            "unknown_or_test_labels_used_to_generate_corruption": False,
        },
        "model_selection": {
            "global_rf_weight": model.global_rf_weight,
            "view_weight": model.view_weight,
            "conflict_scale": model.conflict_scale,
            "temperature": model.temperature,
            "validation_scores": model.validation_scores,
        },
        "risk_weights": RISK_WEIGHTS,
        "cauchy_components": CONFORMAL_VARIANTS,
        "bidirectional_cauchy_components": BIDIRECTIONAL_VARIANTS,
        "support_union_components": ["distance", "knn_distance"],
        "modality_names": model_modality_names,
        "anchor_support_modality": args.anchor_support_modality,
        "anchor_support_weight": args.anchor_support_weight,
        "modality_knn_components": view_knn_components,
        "modality_support_union_components": ["distance", *view_knn_components],
        "missing_aware_diagnostics": missing_aware_diagnostics,
        "class_support_union_components": ["distance", "class_knn_distance"],
        "dual_knn_support_union_components": [
            "distance",
            "knn_distance",
            "class_knn_distance",
        ],
        "mondrian_support_union_components": ["distance", "knn_distance"],
        "mondrian_class_support_union_components": [
            "distance",
            "class_knn_distance",
        ],
        "density_support_union_components": ["distance", "lof_density"],
        "triple_support_union_components": [
            "distance",
            "knn_distance",
            "lof_density",
        ],
        "conflict_support_union_components": [
            "distance",
            "knn_distance",
            "two_sided_conflict",
            "two_sided_tree_disagreement",
        ],
        "foss_partition_parameters": {
            "trees": args.foss_trees,
            "subsample_size": args.foss_subsample_size,
            "candidate_dimensions": args.foss_candidate_dimensions,
            "min_samples": args.foss_min_samples,
            "structural_view": args.foss_structural_view,
            "structural_view_mode": args.foss_structural_view_mode,
            "structural_view_scope": args.foss_structural_view_scope,
            "support_weights": list(
                parse_structural_support_weights(args.structural_support_weights)
            ),
            "support_minimum_gain": args.structural_support_minimum_gain,
        },
        "risk_policy": args.risk_policy_name or args.risk_selection,
        "risk_selection": args.risk_selection,
        "risk_selection_details": risk_selection_details,
        "selected_risk": selected_risk,
        "selected_report": reports[selected_risk],
        "validation_thresholds": thresholds,
        "component_auroc": component_auroc,
        "component_diagnostics": component_diagnostics,
        "reports": reports,
        "conflict_delta_auroc": (
            reports["conflict_augmented"]["unknown_auroc"]
            - reports["baseline"]["unknown_auroc"]
        ),
        "disagreement_delta_auroc": (
            reports["disagreement_augmented"]["unknown_auroc"]
            - reports["baseline"]["unknown_auroc"]
        ),
        "cauchy_conflict_delta_auroc": (
            reports["cauchy_conflict"]["unknown_auroc"]
            - reports["cauchy_baseline"]["unknown_auroc"]
        ),
        "cauchy_all_delta_auroc": (
            reports["cauchy_all"]["unknown_auroc"]
            - reports["cauchy_baseline"]["unknown_auroc"]
        ),
        "evidence_package": {
            "file": "evidence_package.npz",
            "contains_test_ground_truth": False,
            "decision_rule": "reject when selected risk exceeds the known-validation threshold",
            "modality_fields": [
                "view_evidence",
                "view_probability",
                "view_uncertainty",
                "view_reliability",
                "local_conflict",
                "pairwise_conflict",
            ],
        },
        "elapsed_seconds": time.perf_counter() - start,
    }
    validation_cauchy_evidence = cauchy_combined_risk(
        validation_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
    )
    test_cauchy_evidence = cauchy_combined_risk(
        test_tail, CONFORMAL_VARIANTS["cauchy_evidence"]
    )
    score_archive = {
        "validation_labels": bundle.validation.labels.numpy(),
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "test_prediction": prediction,
        "validation_any_missing": validation_any_missing,
        "test_any_missing": test_any_missing,
        "validation_view_missing": validation_missing,
        "test_view_missing": test_missing,
        "validation_support_union": validation_support_union,
        "test_support_union": test_support_union,
        "validation_cauchy_evidence": validation_cauchy_evidence,
        "test_cauchy_evidence": test_cauchy_evidence,
        "validation_cauchy_modality_support_union": (
            validation_cauchy_modality_union
        ),
        "test_cauchy_modality_support_union": test_cauchy_modality_union,
        "validation_missing_aware_cauchy_modality_support_union": (
            validation_missing_risk
        ),
        "test_missing_aware_cauchy_modality_support_union": test_missing_risk,
        "test_missing_aware_prediction": test_missing_prediction,
        "validation_missing_aware_max_modality_knn": validation_missing_max_risk,
        "test_missing_aware_max_modality_knn": test_missing_max_risk,
    }
    for component_name in view_knn_components:
        score_archive[f"validation_{component_name}"] = validation_tail[
            component_name
        ]
        score_archive[f"test_{component_name}"] = test_tail[component_name]
    for name, (validation_risk, test_risk) in continuous_modality_risks.items():
        score_archive[f"validation_{name}"] = validation_risk
        score_archive[f"test_{name}"] = test_risk
    if anchor_support_risks is not None:
        score_archive["validation_anchor_support"] = anchor_support_risks[0]
        score_archive["test_anchor_support"] = anchor_support_risks[1]
    if density_reliability_blend_risks is not None:
        score_archive["validation_density_reliability_blend"] = (
            density_reliability_blend_risks[0]
        )
        score_archive["test_density_reliability_blend"] = (
            density_reliability_blend_risks[1]
        )
    if pseudo_unknown_blend_risks is not None:
        score_archive[f"validation_{pseudo_unknown_blend_name}"] = (
            pseudo_unknown_blend_risks[0]
        )
        score_archive[f"test_{pseudo_unknown_blend_name}"] = (
            pseudo_unknown_blend_risks[1]
        )
    if pseudo_unknown_local_rank_risks is not None:
        score_archive["validation_pseudo_unknown_local_rank_blend"] = (
            pseudo_unknown_local_rank_risks[0]
        )
        score_archive["test_pseudo_unknown_local_rank_blend"] = (
            pseudo_unknown_local_rank_risks[1]
        )
    if pug_continuous_risks is not None:
        score_archive[f"validation_{PUG_RISK_NAME}"] = (
            pug_continuous_risks[0]
        )
        score_archive[f"test_{PUG_RISK_NAME}"] = pug_continuous_risks[1]
    for name, (validation_risk, test_risk) in structural_support_pairs.items():
        score_archive[f"validation_{name}"] = validation_risk
        score_archive[f"test_{name}"] = test_risk
    np.savez_compressed(output_dir / "scores.npz", **score_archive)

    stable_risk_pairs = {
        "support_union": (validation_support_union, test_support_union),
        "cauchy_evidence": (
            validation_cauchy_evidence,
            test_cauchy_evidence,
        ),
        "cauchy_all": (
            cauchy_combined_risk(
                validation_tail, CONFORMAL_VARIANTS["cauchy_all"]
            ),
            cauchy_combined_risk(test_tail, CONFORMAL_VARIANTS["cauchy_all"]),
        ),
        "cauchy_modality_support_union": (
            validation_cauchy_modality_union,
            test_cauchy_modality_union,
        ),
    }
    if anchor_support_risks is not None:
        stable_risk_pairs["anchor_support"] = anchor_support_risks
    for name, weights in RISK_WEIGHTS.items():
        stable_risk_pairs[name] = (
            weighted_risk(validation_normalized, weights),
            weighted_risk(test_normalized, weights),
        )
    for name, components in CONFORMAL_VARIANTS.items():
        stable_risk_pairs[name] = (
            cauchy_combined_risk(validation_tail, components),
            cauchy_combined_risk(test_tail, components),
        )
    for name, components in BIDIRECTIONAL_VARIANTS.items():
        stable_risk_pairs[name] = (
            cauchy_combined_risk(validation_bidirectional, components),
            cauchy_combined_risk(test_bidirectional, components),
        )
    for name, components in {
        "class_support_union": ("distance", "class_knn_distance"),
        "dual_knn_support_union": (
            "distance",
            "knn_distance",
            "class_knn_distance",
        ),
        "density_support_union": ("distance", "lof_density"),
        "triple_support_union": ("distance", "knn_distance", "lof_density"),
        **modality_risk_definitions,
    }.items():
        stable_risk_pairs[name] = (
            bonferroni_union_risk(validation_tail, components),
            bonferroni_union_risk(test_tail, components),
        )
    for component_name in view_knn_components:
        stable_risk_pairs[component_name] = (
            validation_tail[component_name],
            test_tail[component_name],
        )
    stable_risk_pairs.update(continuous_modality_risks)
    if density_reliability_blend_risks is not None:
        stable_risk_pairs["density_reliability_blend"] = (
            density_reliability_blend_risks
        )
    if pseudo_unknown_blend_risks is not None:
        stable_risk_pairs[pseudo_unknown_blend_name] = pseudo_unknown_blend_risks
    if pseudo_unknown_local_rank_risks is not None:
        stable_risk_pairs["pseudo_unknown_local_rank_blend"] = (
            pseudo_unknown_local_rank_risks
        )
    if pug_continuous_risks is not None:
        stable_risk_pairs[PUG_RISK_NAME] = pug_continuous_risks
    for name, components in {
        "cauchy_modality_knn": tuple(view_knn_components),
        "cauchy_modality_support": ("distance", *view_knn_components),
    }.items():
        stable_risk_pairs[name] = (
            cauchy_combined_risk(validation_tail, components),
            cauchy_combined_risk(test_tail, components),
        )
    for name, components in {
        "mondrian_support_union": ("distance", "knn_distance"),
        "mondrian_class_support_union": ("distance", "class_knn_distance"),
    }.items():
        stable_risk_pairs[name] = (
            bonferroni_union_risk(validation_class_tail, components),
            bonferroni_union_risk(test_class_tail, components),
        )
    stable_risk_pairs["conflict_support_union"] = (
        validation_conflict_support_union,
        test_conflict_support_union,
    )
    stable_risk_pairs["foss_partition"] = (
        validation_foss_risk,
        test_foss_risk,
    )
    stable_risk_pairs.update(structural_support_pairs)
    if selected_risk not in stable_risk_pairs:
        raise RuntimeError(
            "selected risk %s is not supported by the deployable evidence package"
            % selected_risk
        )
    validation_selected_risk, test_selected_risk = stable_risk_pairs[selected_risk]
    selected_threshold = float(thresholds[selected_risk])
    open_set_prediction = prediction.copy()
    open_set_prediction[test_selected_risk > selected_threshold] = -1
    evidence_package = {
        "schema_version": np.asarray("1.0"),
        "modality_names": np.asarray(model_modality_names),
        "known_class_names": np.asarray(bundle.class_names),
        "selected_risk_name": np.asarray(selected_risk),
        "selected_threshold": np.asarray(selected_threshold),
        "validation_selected_risk": validation_selected_risk,
        "test_sample_index": np.arange(len(test_selected_risk), dtype=np.int64),
        "test_known_prediction": prediction,
        "test_open_set_prediction": open_set_prediction,
        "test_rejected": test_selected_risk > selected_threshold,
        "test_selected_risk": test_selected_risk,
        "validation_any_missing": validation_any_missing,
        "test_any_missing": test_any_missing,
        "validation_view_missing": validation_missing,
        "test_view_missing": test_missing,
    }
    for name in (
        "view_evidence",
        "view_probability",
        "view_uncertainty",
        "view_reliability",
        "local_conflict",
        "pairwise_conflict",
        "global_conflict",
        "global_probability",
        "view_fused_probability",
        "gate",
        "final_probability",
    ):
        evidence_package[f"validation_{name}"] = validation_evidence[name]
        evidence_package[f"test_{name}"] = test_evidence[name]
    for name in (
        "uncertainty",
        "distance",
        "conflict",
        "tree_disagreement",
    ):
        evidence_package[f"validation_component_{name}"] = validation_components[
            name
        ]
        evidence_package[f"test_component_{name}"] = test_components[name]
        evidence_package[f"validation_tail_{name}"] = validation_tail[name]
        evidence_package[f"test_tail_{name}"] = test_tail[name]
    np.savez_compressed(output_dir / "evidence_package.npz", **evidence_package)
    dump_json(output_dir / "metrics.json", result)
    print("metrics=" + json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

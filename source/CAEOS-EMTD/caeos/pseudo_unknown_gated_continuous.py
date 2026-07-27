from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


HIGHER_IS_BETTER = ("unknown_auroc", "unknown_aupr", "oscr")
LOWER_IS_BETTER = ("unknown_fpr95",)
REQUIRED_METRICS = ("known_macro_f1", *HIGHER_IS_BETTER, *LOWER_IS_BETTER)
PUG_RISK_NAME = "caeos_pug_continuous_outer_min_p"
PUG_SELECTION_NAME = "nested_pug_continuous_outer_min_p"
PAIRWISE_REFERENCE_RISK = "cauchy_modality_support_union"
PUG_GATE_V1 = {
    "minimum_fold_count": 5,
    "mean_unknown_fpr95_oriented_improvement_minimum": 0.02,
    "mean_unknown_auroc_oriented_nonregression": 0.0,
    "mean_unknown_aupr_oriented_nonregression": 0.0,
    "mean_oscr_oriented_nonregression": 0.0,
    "known_macro_f1_absolute_tolerance": 1e-12,
    "per_fold_unknown_fpr95_regression_tolerance": 0.02,
    "per_fold_unknown_auroc_regression_tolerance": 0.01,
    "per_fold_unknown_aupr_regression_tolerance": 0.01,
    "per_fold_oscr_regression_tolerance": 0.01,
}


def _finite_metric(source: Mapping[str, Any], name: str) -> float:
    if name not in source:
        raise ValueError(f"fold metrics are missing {name!r}")
    value = float(source[name])
    if not np.isfinite(value):
        raise ValueError(f"fold metric must be finite: {name}")
    return value


def _oriented_delta(
    candidate: Mapping[str, Any],
    reference: Mapping[str, Any],
    metric: str,
) -> float:
    candidate_value = _finite_metric(candidate, metric)
    reference_value = _finite_metric(reference, metric)
    if metric in HIGHER_IS_BETTER:
        return candidate_value - reference_value
    if metric in LOWER_IS_BETTER:
        return reference_value - candidate_value
    raise ValueError(f"unsupported oriented metric: {metric}")


def evaluate_pseudo_unknown_gate(
    folds: Sequence[Mapping[str, Any]],
    gate: Mapping[str, Any],
) -> dict[str, Any]:
    minimum_fold_count = int(gate["minimum_fold_count"])
    if len(folds) < minimum_fold_count:
        raise ValueError(
            f"at least {minimum_fold_count} pseudo-unknown folds are required"
        )

    names: set[str] = set()
    deltas = {
        metric: []
        for metric in (*HIGHER_IS_BETTER, *LOWER_IS_BETTER)
    }
    known_f1_absolute_deltas = []
    fold_rows = []
    for fold in folds:
        name = str(fold.get("fold", "")).strip()
        if not name or name in names:
            raise ValueError("pseudo-unknown fold identities must be unique")
        names.add(name)
        reference = fold.get("reference")
        candidate = fold.get("candidate")
        if not isinstance(reference, Mapping) or not isinstance(candidate, Mapping):
            raise ValueError("each fold requires reference and candidate metrics")
        for metric in REQUIRED_METRICS:
            _finite_metric(reference, metric)
            _finite_metric(candidate, metric)
        known_delta = abs(
            _finite_metric(candidate, "known_macro_f1")
            - _finite_metric(reference, "known_macro_f1")
        )
        known_f1_absolute_deltas.append(known_delta)
        row_deltas = {}
        for metric in deltas:
            delta = _oriented_delta(candidate, reference, metric)
            deltas[metric].append(delta)
            row_deltas[metric] = delta
        fold_rows.append(
            {
                "fold": name,
                "known_macro_f1_absolute_delta": known_delta,
                "oriented_delta": row_deltas,
            }
        )

    aggregates = {}
    for metric, values in deltas.items():
        array = np.asarray(values, dtype=np.float64)
        aggregates[metric] = {
            "mean_oriented_delta": float(array.mean()),
            "minimum_oriented_delta": float(array.min()),
            "win_count": int((array > 1e-12).sum()),
            "tie_count": int((np.abs(array) <= 1e-12).sum()),
            "loss_count": int((array < -1e-12).sum()),
        }

    checks = {
        "minimum_fold_count": len(folds) >= minimum_fold_count,
        "known_macro_f1_invariant": max(known_f1_absolute_deltas)
        <= float(gate["known_macro_f1_absolute_tolerance"]),
        "mean_fpr95_improvement": aggregates["unknown_fpr95"][
            "mean_oriented_delta"
        ]
        >= float(gate["mean_unknown_fpr95_oriented_improvement_minimum"]),
        "mean_auroc_nonregression": aggregates["unknown_auroc"][
            "mean_oriented_delta"
        ]
        >= float(gate["mean_unknown_auroc_oriented_nonregression"]),
        "mean_aupr_nonregression": aggregates["unknown_aupr"][
            "mean_oriented_delta"
        ]
        >= float(gate["mean_unknown_aupr_oriented_nonregression"]),
        "mean_oscr_nonregression": aggregates["oscr"]["mean_oriented_delta"]
        >= float(gate["mean_oscr_oriented_nonregression"]),
        "worst_fold_fpr95_protection": aggregates["unknown_fpr95"][
            "minimum_oriented_delta"
        ]
        >= -float(gate["per_fold_unknown_fpr95_regression_tolerance"]),
        "worst_fold_auroc_protection": aggregates["unknown_auroc"][
            "minimum_oriented_delta"
        ]
        >= -float(gate["per_fold_unknown_auroc_regression_tolerance"]),
        "worst_fold_aupr_protection": aggregates["unknown_aupr"][
            "minimum_oriented_delta"
        ]
        >= -float(gate["per_fold_unknown_aupr_regression_tolerance"]),
        "worst_fold_oscr_protection": aggregates["oscr"][
            "minimum_oriented_delta"
        ]
        >= -float(gate["per_fold_oscr_regression_tolerance"]),
    }
    return {
        "schema_version": "caeos_pug_pseudo_unknown_gate_v1",
        "fold_count": len(folds),
        "folds": fold_rows,
        "aggregates": aggregates,
        "checks": checks,
        "passes": all(checks.values()),
        "selected_route": (
            "continuous_outer_min_p"
            if all(checks.values())
            else "exact_pairwise_passthrough"
        ),
        "selection_uses_unknown_or_test_labels": False,
    }


def select_pug_route(
    pairwise_base_risk: str,
    gate_result: Mapping[str, Any],
) -> dict[str, Any]:
    base_risk = str(pairwise_base_risk).strip()
    if not base_risk:
        raise ValueError("Pairwise base risk is required")
    if gate_result.get("selection_uses_unknown_or_test_labels") is not False:
        raise ValueError("PUG gate must not use unknown or test labels")
    gate_passes = gate_result.get("passes")
    if not isinstance(gate_passes, bool):
        raise ValueError("PUG gate must contain a boolean passes decision")
    eligible = base_risk == PAIRWISE_REFERENCE_RISK
    selected = PUG_RISK_NAME if eligible and gate_passes else base_risk
    return {
        "pairwise_base_selected_risk": base_risk,
        "pug_base_route_eligible": eligible,
        "pug_gate_passes": gate_passes,
        "pug_selected": selected == PUG_RISK_NAME,
        "selected_risk": selected,
    }

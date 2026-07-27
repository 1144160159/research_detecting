from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .hybrid_open_set import bonferroni_union_risk


BASE_RISK = "cauchy_modality_support_union"
CANDIDATE_NAME = "caeos_comp"


def _array(source: Mapping[str, Any], key: str) -> np.ndarray:
    if key not in source:
        raise ValueError(f"required risk array is absent: {key}")
    value = np.asarray(source[key], dtype=np.float64).reshape(-1)
    if not len(value) or not np.isfinite(value).all():
        raise ValueError(f"finite non-empty risk array required: {key}")
    return value


def _selected_name(evidence: Mapping[str, Any]) -> str:
    if "selected_risk_name" not in evidence:
        raise ValueError("selected_risk_name is absent")
    value = np.asarray(evidence["selected_risk_name"])
    if value.size != 1:
        raise ValueError("selected_risk_name must be scalar")
    return str(value.item())


def _view_names(scores: Mapping[str, Any], prefix: str) -> list[str]:
    names = sorted(
        key[len(prefix) :]
        for key in scores.keys()
        if key.startswith(prefix + "knn_view_")
    )
    if not names:
        raise ValueError(f"no modality KNN risks found for {prefix!r}")
    return names


def modality_support_union(
    scores: Mapping[str, Any],
    evidence: Mapping[str, Any],
    prefix: str,
) -> np.ndarray:
    view_names = _view_names(scores, prefix)
    components = {"distance": _array(evidence, prefix + "tail_distance")}
    for name in view_names:
        components[name] = _array(scores, prefix + name)
    shapes = {value.shape for value in components.values()}
    if len(shapes) != 1:
        raise ValueError(f"modality support component shapes differ: {shapes}")
    return bonferroni_union_risk(
        components, ("distance", *view_names)
    )


def continuous_outer_min_p(
    cauchy_evidence: np.ndarray, modality_support: np.ndarray
) -> np.ndarray:
    cauchy = np.asarray(cauchy_evidence, dtype=np.float64).reshape(-1)
    modality = np.asarray(modality_support, dtype=np.float64).reshape(-1)
    if cauchy.shape != modality.shape or not len(cauchy):
        raise ValueError("continuous outer min-p risks must have matching shapes")
    if not np.isfinite(cauchy).all() or not np.isfinite(modality).all():
        raise ValueError("continuous outer min-p risks must be finite")
    if (
        (cauchy < 0.0).any()
        or (cauchy > 1.0).any()
        or (modality < 0.0).any()
        or (modality > 1.0).any()
    ):
        raise ValueError("continuous outer min-p inputs must lie in [0, 1]")
    return np.maximum(cauchy, modality)


def reconstruct_candidate_risks(
    scores: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    selected = _selected_name(evidence)
    validation_selected = _array(evidence, "validation_selected_risk")
    test_selected = _array(evidence, "test_selected_risk")
    score_validation_key = f"validation_{selected}"
    score_test_key = f"test_{selected}"
    if score_validation_key in scores and not np.array_equal(
        validation_selected, _array(scores, score_validation_key)
    ):
        raise ValueError("validation selected risk differs from score archive")
    if score_test_key in scores and not np.array_equal(
        test_selected, _array(scores, score_test_key)
    ):
        raise ValueError("test selected risk differs from score archive")

    if selected != BASE_RISK:
        return {
            "candidate_name": CANDIDATE_NAME,
            "selected_risk_name": selected,
            "route": "frozen_pairwise_passthrough",
            "changed": False,
            "validation_reference": validation_selected,
            "test_reference": test_selected,
            "validation_candidate": validation_selected.copy(),
            "test_candidate": test_selected.copy(),
        }

    validation_modality = modality_support_union(
        scores, evidence, "validation_"
    )
    test_modality = modality_support_union(scores, evidence, "test_")
    validation_candidate = continuous_outer_min_p(
        _array(scores, "validation_cauchy_evidence"), validation_modality
    )
    test_candidate = continuous_outer_min_p(
        _array(scores, "test_cauchy_evidence"), test_modality
    )
    if (
        validation_candidate.shape != validation_selected.shape
        or test_candidate.shape != test_selected.shape
    ):
        raise ValueError("candidate and selected risk shapes differ")
    return {
        "candidate_name": CANDIDATE_NAME,
        "selected_risk_name": selected,
        "route": "continuous_outer_min_p_refinement",
        "changed": True,
        "validation_reference": validation_selected,
        "test_reference": test_selected,
        "validation_candidate": validation_candidate,
        "test_candidate": test_candidate,
    }

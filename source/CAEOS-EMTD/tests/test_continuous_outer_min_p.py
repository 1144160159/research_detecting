from __future__ import annotations

import numpy as np

from caeos.continuous_outer_min_p import (
    BASE_RISK,
    continuous_outer_min_p,
    reconstruct_candidate_risks,
)


def archive(selected: str = BASE_RISK) -> tuple[dict, dict]:
    validation_cauchy = np.asarray([0.2, 0.4, 0.7, 0.9])
    test_cauchy = np.asarray([0.1, 0.3, 0.8, 0.95])
    validation_view = np.asarray([0.1, 0.2, 0.7, 0.8])
    test_view = np.asarray([0.2, 0.4, 0.6, 0.9])
    validation_distance = np.asarray([0.1, 0.2, 0.6, 0.9])
    test_distance = np.asarray([0.1, 0.3, 0.7, 0.8])
    validation_modality = np.maximum(
        0.0, 2.0 * np.maximum(validation_distance, validation_view) - 1.0
    )
    test_modality = np.maximum(
        0.0, 2.0 * np.maximum(test_distance, test_view) - 1.0
    )
    validation_base = np.maximum(
        0.0, 2.0 * np.maximum(validation_cauchy, validation_modality) - 1.0
    )
    test_base = np.maximum(
        0.0, 2.0 * np.maximum(test_cauchy, test_modality) - 1.0
    )
    scores = {
        "validation_cauchy_evidence": validation_cauchy,
        "test_cauchy_evidence": test_cauchy,
        "validation_knn_view_0": validation_view,
        "test_knn_view_0": test_view,
        f"validation_{selected}": validation_base,
        f"test_{selected}": test_base,
    }
    evidence = {
        "selected_risk_name": np.asarray(selected),
        "validation_selected_risk": validation_base,
        "test_selected_risk": test_base,
        "validation_tail_distance": validation_distance,
        "test_tail_distance": test_distance,
    }
    return scores, evidence


def test_continuous_outer_min_p_refines_bonferroni_floor() -> None:
    scores, evidence = archive()

    result = reconstruct_candidate_risks(scores, evidence)

    assert result["changed"] is True
    assert result["route"] == "continuous_outer_min_p_refinement"
    assert result["validation_reference"][0] == 0.0
    assert result["validation_candidate"][0] == 0.2
    assert np.all(result["validation_candidate"] >= result["validation_reference"])


def test_nonbase_selected_risk_is_exact_passthrough() -> None:
    scores, evidence = archive("pseudo_unknown_learned_blend")

    result = reconstruct_candidate_risks(scores, evidence)

    assert result["changed"] is False
    assert result["route"] == "frozen_pairwise_passthrough"
    assert np.array_equal(
        result["validation_candidate"], result["validation_reference"]
    )
    assert np.array_equal(result["test_candidate"], result["test_reference"])


def test_continuous_outer_min_p_validates_shape_and_range() -> None:
    with np.testing.assert_raises(ValueError):
        continuous_outer_min_p(np.asarray([0.1]), np.asarray([0.1, 0.2]))
    with np.testing.assert_raises(ValueError):
        continuous_outer_min_p(np.asarray([-0.1]), np.asarray([0.2]))

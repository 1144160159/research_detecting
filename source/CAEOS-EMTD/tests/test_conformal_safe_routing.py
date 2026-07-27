from __future__ import annotations

import numpy as np

from caeos.conformal_safe_routing import (
    KnownValidationMaxRoutingCalibration,
)


def evidence(probability, conflict):
    return {
        "final_probability": np.asarray(probability, dtype=np.float64),
        "local_conflict": np.asarray(conflict, dtype=np.float64),
    }


def test_calibration_is_inactive_on_its_nonmissing_reference() -> None:
    clean = evidence(
        [[0.9, 0.1], [0.8, 0.2], [0.4, 0.6]],
        [[0.1], [0.2], [0.3]],
    )
    robust = evidence(
        [[0.85, 0.15], [0.7, 0.3], [0.3, 0.7]],
        [[0.1], [0.2], [0.3]],
    )
    clean_risk = np.asarray([0.1, 0.2, 0.3])
    robust_risk = np.asarray([0.2, 0.4, 0.5])
    missing_risk = np.asarray([0.3, 0.5, 0.6])
    calibration = KnownValidationMaxRoutingCalibration.fit(
        clean, robust, clean_risk, robust_risk, missing_risk
    )
    result = calibration.apply(
        clean,
        robust,
        clean_risk,
        robust_risk,
        missing_risk,
        np.zeros(3, dtype=bool),
    )
    assert not result["active"].any()
    np.testing.assert_array_equal(result["prediction"], [0, 0, 1])
    np.testing.assert_array_equal(
        result["probability"], clean["final_probability"]
    )
    np.testing.assert_array_equal(result["risk"], clean_risk)


def test_active_route_only_monotonically_uplifts_risk() -> None:
    reference_clean = evidence(
        [[0.9, 0.1], [0.8, 0.2]], [[0.1], [0.2]]
    )
    reference_robust = evidence(
        [[0.85, 0.15], [0.7, 0.3]], [[0.1], [0.2]]
    )
    calibration = KnownValidationMaxRoutingCalibration.fit(
        reference_clean,
        reference_robust,
        np.asarray([0.1, 0.9]),
        np.asarray([0.1, 0.9]),
        np.asarray([0.1, 0.9]),
    )
    query_clean = evidence(
        [[0.9, 0.1], [0.8, 0.2]], [[0.5], [0.1]]
    )
    query_robust = evidence(
        [[0.1, 0.9], [0.2, 0.8]], [[0.5], [0.1]]
    )
    clean_risk = np.asarray([0.2, 0.4])
    result = calibration.apply(
        query_clean,
        query_robust,
        clean_risk,
        np.asarray([0.8, 0.1]),
        np.asarray([0.7, 0.9]),
        np.asarray([False, True]),
    )
    assert result["active"].tolist() == [True, True]
    np.testing.assert_array_equal(result["prediction"], [0, 0])
    np.testing.assert_array_equal(
        result["probability"], query_clean["final_probability"]
    )
    assert np.all(result["risk"] >= clean_risk)
    evidence_record = calibration.evidence()
    assert evidence_record["unknown_or_test_labels_used"] is False
    assert evidence_record["prediction_source"] == "clean_pairwise_exact"

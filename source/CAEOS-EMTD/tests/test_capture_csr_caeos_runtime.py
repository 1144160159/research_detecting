from __future__ import annotations

import numpy as np

from capture_csr_caeos_runtime import (
    SplitKnownValidationMaxCalibration,
    calibration_indices,
    safety_indices,
)


def test_partition_is_disjoint_and_complete() -> None:
    calibration = calibration_indices(9)
    safety = safety_indices(9)
    assert set(calibration).isdisjoint(set(safety))
    assert sorted([*calibration, *safety]) == list(range(9))


def test_split_calibration_ignores_safety_extreme() -> None:
    clean_probability = np.asarray(
        [
            [0.9, 0.1],
            [0.9, 0.1],
            [0.8, 0.2],
            [0.8, 0.2],
        ]
    )
    robust_probability = np.asarray(
        [
            [0.85, 0.15],
            [0.1, 0.9],
            [0.75, 0.25],
            [0.1, 0.9],
        ]
    )
    calibration = SplitKnownValidationMaxCalibration.fit(
        {
            "final_probability": clean_probability,
            "local_conflict": np.asarray(
                [[0.1], [0.99], [0.2], [0.98]]
            ),
        },
        {"final_probability": robust_probability},
        np.asarray([0.1, 0.2, 0.3, 0.4]),
        np.asarray([0.2, 0.3, 0.4, 0.5]),
        np.asarray([0.3, 0.4, 0.5, 0.6]),
        quantile=0.99,
    )
    assert calibration.calibration_count == 2
    assert calibration.conflict_threshold == 0.2

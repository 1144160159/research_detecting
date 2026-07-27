from __future__ import annotations

import unittest

import numpy as np

from evaluate_strict_v4_vgrf_selected_system_corruption import (
    degradation,
    risk_ece,
)


class VGRFSelectedSystemCorruptionTests(unittest.TestCase):
    def test_degradation_orientation(self) -> None:
        clean = {"unknown_auroc": 0.9, "unknown_fpr95": 0.2, "ece": 0.1}
        corrupted = {
            "unknown_auroc": 0.7,
            "unknown_fpr95": 0.5,
            "ece": 0.3,
        }
        self.assertAlmostEqual(
            degradation(clean, corrupted, "unknown_auroc"), 0.2
        )
        self.assertAlmostEqual(
            degradation(clean, corrupted, "unknown_fpr95"), 0.3
        )
        self.assertAlmostEqual(
            degradation(clean, corrupted, "ece"), 0.2
        )

    def test_risk_ece_is_finite(self) -> None:
        value = risk_ece(
            np.asarray([0.1, 0.9, 0.2, 0.8]),
            np.asarray([False, True, False, True]),
        )
        self.assertTrue(np.isfinite(value))
        self.assertGreaterEqual(value, 0.0)

    def test_invalid_risk_ece_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            risk_ece(np.asarray([]), np.asarray([]))


if __name__ == "__main__":
    unittest.main()

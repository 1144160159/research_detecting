from __future__ import annotations

import unittest

import numpy as np

from analyze_known_acceptance_sensitivity import evaluate_acceptances, parse_float_set


class KnownAcceptanceSensitivityTest(unittest.TestCase):
    def test_higher_validation_acceptance_trades_rejection_for_known_acceptance(self) -> None:
        result = evaluate_acceptances(
            validation_risk=np.asarray([0.1, 0.2, 0.3, 0.4]),
            test_labels=np.asarray([0, 0, 0, 0, 0, 0]),
            test_unknown=np.asarray([False, False, False, True, True, True]),
            test_prediction=np.asarray([0, 0, 0, 0, 0, 0]),
            test_risk=np.asarray([0.15, 0.25, 0.35, 0.25, 0.45, 0.55]),
            acceptances=(0.5, 0.9),
        )
        lower = result[0.5]["report"]
        higher = result[0.9]["report"]
        self.assertGreaterEqual(
            higher["known_acceptance_rate"], lower["known_acceptance_rate"]
        )
        self.assertLessEqual(
            higher["unknown_rejection_rate"], lower["unknown_rejection_rate"]
        )

    def test_acceptances_are_sorted_and_validated(self) -> None:
        self.assertEqual((0.9, 0.95, 0.99), parse_float_set("0.99,0.9,0.95", "x"))
        with self.assertRaisesRegex(ValueError, "unique"):
            parse_float_set("0.9,0.9", "x")
        with self.assertRaisesRegex(ValueError, "\(0, 1\)"):
            parse_float_set("1.0", "x")


if __name__ == "__main__":
    unittest.main()

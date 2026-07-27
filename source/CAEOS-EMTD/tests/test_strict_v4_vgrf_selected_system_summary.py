from __future__ import annotations

import unittest

from summarize_strict_v4_vgrf_selected_system import (
    bootstrap_mean,
    holm_adjust,
)


class VGRFSelectedSystemSummaryTests(unittest.TestCase):
    def test_bootstrap_mean_is_deterministic(self) -> None:
        first = bootstrap_mean([0.5, 1.0, 1.5], seed=7, repetitions=1000)
        second = bootstrap_mean([0.5, 1.0, 1.5], seed=7, repetitions=1000)
        self.assertEqual(first, second)
        self.assertEqual(first["n"], 3)
        self.assertEqual(first["mean"], 1.0)

    def test_holm_adjustment_is_monotone_in_sorted_order(self) -> None:
        adjusted = holm_adjust({"a": 0.01, "b": 0.03, "c": 0.20})
        self.assertAlmostEqual(adjusted["a"], 0.03)
        self.assertAlmostEqual(adjusted["b"], 0.06)
        self.assertAlmostEqual(adjusted["c"], 0.20)

    def test_nonfinite_bootstrap_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            bootstrap_mean([1.0, float("nan")], seed=1)


if __name__ == "__main__":
    unittest.main()

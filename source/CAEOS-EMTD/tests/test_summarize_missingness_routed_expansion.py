from __future__ import annotations

import unittest

from summarize_missingness_routed_expansion import aggregate


def manifest() -> dict:
    return {
        "expected_pair_count": 3,
        "gates": {
            "per_pair_gain_minimum": -0.002,
            "overall_mean_gain_minimum": 0.02,
            "per_modality_mean_gain_minimum": 0.01,
            "routed_sample_rate_minimum": 0.9,
        },
    }


def row(modality: int, f1: float, oscr: float, routed: float = 0.99) -> dict:
    return {
        "modality": modality,
        "known_macro_f1_gain": f1,
        "oscr_gain": oscr,
        "routed_sample_rate": routed,
    }


class RoutedExpansionSummaryTests(unittest.TestCase):
    def test_all_gates_confirm_consistent_gain(self) -> None:
        result = aggregate(
            [row(0, 0.1, 0.08), row(1, 0.05, 0.04), row(2, 0.03, 0.02)],
            manifest(),
        )
        self.assertEqual(result["state"], "confirmed")
        self.assertTrue(result["gate_results"]["all_modality_means_passed"])

    def test_one_pair_regression_rejects_expansion(self) -> None:
        result = aggregate(
            [row(0, 0.1, 0.08), row(1, -0.01, 0.04), row(2, 0.03, 0.02)],
            manifest(),
        )
        self.assertEqual(result["state"], "rejected")
        self.assertFalse(result["gate_results"]["all_pairs_passed"])


if __name__ == "__main__":
    unittest.main()

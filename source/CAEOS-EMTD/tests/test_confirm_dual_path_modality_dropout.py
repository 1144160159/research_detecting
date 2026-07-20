from __future__ import annotations

import unittest

from confirm_dual_path_modality_dropout import apply_gates


def pair(scenario: str, condition: str, f1_gain: float, oscr_gain: float) -> dict:
    return {
        "scenario": scenario,
        "condition": condition,
        "detector_ranking_metrics_exactly_preserved": True,
        "decision_architecture": {
            "routed_sample_rate": 0.0 if condition == "clean" else 0.99
        },
        "detector_report": {"known_macro_f1": 0.5, "oscr": 0.4},
        "dual_path_report": {
            "known_macro_f1": 0.5 + f1_gain,
            "oscr": 0.4 + oscr_gain,
        },
    }


def manifest() -> dict:
    return {
        "confirmation_gates": {
            "per_clean_pair": {
                "known_macro_f1_delta_minimum": -0.002,
                "oscr_delta_minimum": -0.002,
                "routed_sample_rate_maximum": 0.01,
            },
            "per_corrupted_pair": {
                "known_macro_f1_delta_minimum": -0.002,
                "oscr_delta_minimum": -0.002,
                "routed_sample_rate_minimum": 0.90,
            },
            "corrupted_scenario_mean": {
                "known_macro_f1_gain_minimum": 0.02,
                "oscr_gain_minimum": 0.02,
            },
        }
    }


class DualPathConfirmationTests(unittest.TestCase):
    def test_all_pair_and_mean_gates_must_pass(self) -> None:
        pairs = [
            pair("a", "clean", 0.0, 0.0),
            pair("a", "missing", 0.04, 0.03),
            pair("b", "clean", 0.001, 0.001),
            pair("b", "missing", 0.02, 0.02),
        ]
        result = apply_gates(pairs, manifest())
        self.assertTrue(result["confirmed"])
        self.assertAlmostEqual(result["corrupted_scenario_mean_gain"]["known_macro_f1"], 0.03)

    def test_single_clean_regression_rejects_candidate(self) -> None:
        pairs = [
            pair("a", "clean", -0.01, 0.0),
            pair("a", "missing", 0.10, 0.10),
            pair("b", "clean", 0.0, 0.0),
            pair("b", "missing", 0.10, 0.10),
        ]
        self.assertFalse(apply_gates(pairs, manifest())["confirmed"])


if __name__ == "__main__":
    unittest.main()

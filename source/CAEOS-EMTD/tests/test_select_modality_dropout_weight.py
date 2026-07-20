from __future__ import annotations

import unittest

from select_modality_dropout_weight import select_weight


def metrics(tag: str, clean_delta: float, mean: float, minimum: float) -> dict:
    return {
        "split_metadata": {"split_fingerprint": {"combined": tag}},
        "corruption_protocol": {"test_corruption": {"kind": "none"}},
        "model_selection": {
            "validation_scores": {
                "selected": 0.9 + clean_delta,
                "clean_delta_from_baseline": clean_delta,
                "field_dropout_validation": {
                    "uses_known_validation_labels_only": True,
                    "unknown_or_test_labels_used": False,
                    "mean_macro_f1": mean,
                    "minimum_macro_f1": minimum,
                    "minimax_objective": 0.5 * (mean + minimum),
                },
            }
        },
    }


class ModalityDropoutWeightSelectionTests(unittest.TestCase):
    def test_best_validation_minimax_candidate_is_selected(self) -> None:
        result = select_weight(
            [
                (0.0, metrics("a", 0.0, 0.70, 0.20)),
                (0.25, metrics("a", 0.0, 0.88, 0.57)),
                (1.0, metrics("a", 0.001, 0.87, 0.56)),
            ],
            clean_tolerance=0.002,
        )
        self.assertEqual(result["selected_weight"], 0.25)
        self.assertFalse(result["unknown_or_test_labels_used_for_selection"])

    def test_clean_regression_and_fingerprint_drift_are_rejected(self) -> None:
        result = select_weight(
            [
                (0.25, metrics("a", -0.01, 0.99, 0.99)),
                (0.5, metrics("a", 0.0, 0.8, 0.7)),
            ],
            clean_tolerance=0.002,
        )
        self.assertEqual(result["selected_weight"], 0.5)
        with self.assertRaisesRegex(ValueError, "split fingerprints differ"):
            select_weight(
                [(0.0, metrics("a", 0.0, 0.7, 0.5)), (1.0, metrics("b", 0.0, 0.8, 0.6))],
                clean_tolerance=0.002,
            )


if __name__ == "__main__":
    unittest.main()

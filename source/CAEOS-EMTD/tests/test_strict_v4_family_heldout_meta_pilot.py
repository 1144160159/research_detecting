from __future__ import annotations

import unittest

import numpy as np

from evaluate_strict_v4_family_heldout_meta_pilot import fixed_evaluation


class FamilyHeldoutMetaPilotTests(unittest.TestCase):
    def test_fixed_evaluation_uses_no_candidate_selection(self) -> None:
        metrics = {
            "model": {
                "name": (
                    "FHMM-CAEOS family-held-out malicious-boundary meta learner"
                )
            },
            "training": {"meta_heldout_loss_weight": 1.0},
            "benign_index": 0,
        }
        arrays = {
            "validation_labels": np.asarray([0] * 100 + [1] * 20),
            "validation_attack_head_attack_probability": np.asarray(
                [0.01] * 100 + [0.99] * 20
            ),
            "validation_open_max": np.linspace(0.0, 1.0, 120),
            "test_attack_head_attack_probability": np.asarray(
                [0.01, 0.99, 0.99, 0.99]
            ),
            "test_open_max": np.asarray([0.01, 0.01, 0.99, 0.99]),
            "test_type_prediction": np.asarray([0, 1, 1, 1]),
            "test_labels": np.asarray([0, 1, -1, -1]),
            "test_unknown": np.asarray([False, False, True, True]),
        }
        result = fixed_evaluation(metrics, arrays)
        self.assertEqual(
            "none_fixed_before_test",
            result["configuration"]["configuration_selection"],
        )
        self.assertEqual(0.0, result["metrics"]["benign_fpr"])
        self.assertEqual(1.0, result["metrics"]["unknown_attack_alert_recall"])

    def test_rejects_non_meta_task(self) -> None:
        with self.assertRaises(ValueError):
            fixed_evaluation(
                {
                    "model": {"name": "DMC-CAEOS"},
                    "training": {"meta_heldout_loss_weight": 0.0},
                    "benign_index": 0,
                },
                {},
            )


if __name__ == "__main__":
    unittest.main()

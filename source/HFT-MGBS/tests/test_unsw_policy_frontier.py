from __future__ import annotations

import unittest

from scripts.compare_unsw_decision_policies import (
    compare,
    dominates,
    materially_dominates,
)


def candidate(mode, floor=0.8, **overrides):
    item = {
        "mode": mode,
        "batch_size": 512,
        "budget_us": 5000,
        "execution_budget_safety_ratio": 0.5,
        "decision_policy": {
            "feature_profile": "invariant_no_ports_v1",
            "classifier": "extra_trees",
            "threshold_policy": "calibration_macro_f1",
            "calibration_attack_recall_floor": floor,
            "calibration_groups": ["january"],
            "evaluation_groups": ["february"],
        },
        "repeat_gate_passed": True,
        "hard_constraints_passed": True,
        "hard_constraint_violations": [],
        "macro_f1_min": 0.5,
        "balanced_accuracy_min": 0.7,
        "attack_recall_min": 0.7,
        "benign_recall_min": 0.75,
        "auroc_min": 0.85,
        "auprc_min": 0.1,
        "ece_max": 0.6,
        "ground_truth_event_recall_min": 0.67,
        "budget_overrun_count_max": 0,
        "key_flow_coverage_min": 1.0,
        "input_hash_manifest_sha256": "abc",
    }
    item.update(overrides)
    return item


class UnswPolicyFrontierTest(unittest.TestCase):
    def test_normal_and_fallback_are_paired_by_exact_policy(self):
        output = compare(
            [
                (
                    "floor080",
                    {
                        "candidates": [
                            candidate("normal"),
                            candidate("fallback", macro_f1_min=0.48),
                        ]
                    },
                )
            ]
        )

        self.assertEqual(output["feasible_candidate_count"], 1)
        self.assertEqual(output["candidates"][0]["macro_f1_min"], 0.48)
        self.assertEqual(
            output["candidates"][0]["attack_recall_min"], 0.7
        )

    def test_mismatched_modes_cannot_form_deployable_pair(self):
        output = compare(
            [
                (
                    "mixed",
                    {
                        "candidates": [
                            candidate("normal", floor=0.8),
                            candidate("fallback", floor=0.9),
                        ]
                    },
                )
            ]
        )

        self.assertEqual(output["candidate_count"], 2)
        self.assertEqual(output["feasible_candidate_count"], 0)

    def test_attack_recall_tradeoff_remains_on_frontier(self):
        balanced = {
            "macro_f1_min": 0.50,
            "attack_recall_min": 0.65,
            "benign_recall_min": 0.75,
            "auprc_min": 0.10,
            "ece_max": 0.6,
        }
        recall = {
            "macro_f1_min": 0.40,
            "attack_recall_min": 0.85,
            "benign_recall_min": 0.55,
            "auprc_min": 0.09,
            "ece_max": 0.65,
        }

        self.assertFalse(dominates(balanced, recall))
        self.assertFalse(dominates(recall, balanced))

    def test_strictly_worse_policy_is_dominated(self):
        reference = {
            "macro_f1_min": 0.50,
            "attack_recall_min": 0.70,
            "benign_recall_min": 0.75,
            "auprc_min": 0.10,
            "ece_max": 0.6,
        }
        worse = {
            "macro_f1_min": 0.40,
            "attack_recall_min": 0.60,
            "benign_recall_min": 0.70,
            "auprc_min": 0.08,
            "ece_max": 0.7,
        }

        self.assertTrue(dominates(reference, worse))

    def test_materiality_treats_small_gains_as_ties(self):
        balanced = {
            "macro_f1_min": 0.731,
            "attack_recall_min": 0.765,
            "benign_recall_min": 0.945,
            "auprc_min": 0.523,
            "ece_max": 0.038,
        }
        macro_tilt = {
            "macro_f1_min": 0.739,
            "attack_recall_min": 0.729,
            "benign_recall_min": 0.946,
            "auprc_min": 0.478,
            "ece_max": 0.042,
        }

        self.assertTrue(
            materially_dominates(balanced, macro_tilt, epsilon=0.03)
        )
        self.assertFalse(
            materially_dominates(macro_tilt, balanced, epsilon=0.03)
        )


if __name__ == "__main__":
    unittest.main()

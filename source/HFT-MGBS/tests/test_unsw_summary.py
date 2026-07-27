from __future__ import annotations

import unittest

from scripts.evaluate_unsw_independent_holdout import (
    select_macro_f1_threshold,
    train_and_score,
)
from scripts.summarize_unsw_holdout import summarize


def payload(overrun=0, coverage=1.0, event_recall=0.8, macro_f1=0.4):
    audit = {
        "budget_overrun_count": overrun,
        "key_flow_coverage_min": coverage,
    }
    return {
        "candidate": {"batch_size": 512, "budget_us": 5000},
        "protocol": {
            "feature_profile": "invariant_no_ports_v1",
            "classifier": "extra_trees",
            "threshold_policy": "calibration_macro_f1",
            "calibration_attack_recall_floor": 0.8,
            "calibration_groups": ["unsw_january"],
            "evaluation_groups": ["unsw_february"],
        },
        "training_constraint_audit": audit,
        "holdout_constraint_audit": audit,
        "ground_truth_event_recall_audit": {
            "event_recall": event_recall
        },
        "input_hash_evidence": {"sha256": "abc"},
        "quality": {
            "train_flow_count": 100,
            "test_flow_count": 50,
            "conservative": {
                "macro_f1_min": macro_f1,
                "balanced_accuracy_min": macro_f1,
                "auroc_min": macro_f1,
                "auprc_min": macro_f1,
                "benign_recall_min": macro_f1,
                "attack_recall_min": macro_f1,
                "ece_max": 1 - macro_f1,
            },
        },
        "missing_final_evidence": ["threshold"],
    }


class UnswSummaryTest(unittest.TestCase):
    def test_calibration_threshold_is_selected_without_evaluation_data(self):
        selected = select_macro_f1_threshold(
            [0, 0, 1, 1], [0.1, 0.2, 0.7, 0.9]
        )

        self.assertEqual(selected["threshold"], 0.7)
        self.assertEqual(selected["macro_f1"], 1.0)

    def test_calibration_attack_recall_floor_is_enforced(self):
        selected = select_macro_f1_threshold(
            [0, 0, 1, 1],
            [0.1, 0.6, 0.55, 0.9],
            min_attack_recall=1.0,
        )

        self.assertEqual(selected["attack_recall"], 1.0)
        self.assertLessEqual(selected["threshold"], 0.55)

    def test_worst_repeat_and_hard_constraints_are_combined(self):
        summary = summarize(
            [
                ("normal_repeat1.json", payload(macro_f1=0.5)),
                ("normal_repeat2.json", payload(macro_f1=0.4)),
                ("normal_repeat3.json", payload(macro_f1=0.45)),
            ],
            min_event_recall=0.7,
        )

        candidate = summary["candidates"][0]
        self.assertEqual(candidate["macro_f1_min"], 0.4)
        self.assertTrue(candidate["hard_constraints_passed"])
        self.assertEqual(summary["feasible_candidate_count"], 1)

    def test_high_metric_cannot_hide_constraint_failure(self):
        failing = payload(
            overrun=1, coverage=0.0, event_recall=0.2, macro_f1=0.999
        )
        summary = summarize(
            [
                ("normal_repeat1.json", failing),
                ("normal_repeat2.json", failing),
                ("normal_repeat3.json", failing),
            ],
            min_event_recall=0.5,
        )

        candidate = summary["candidates"][0]
        self.assertFalse(candidate["hard_constraints_passed"])
        self.assertEqual(
            candidate["hard_constraint_violations"],
            [
                "budget_overrun",
                "key_flow_coverage",
                "ground_truth_event_recall",
            ],
        )
        self.assertEqual(summary["feasible_candidate_count"], 0)

    def test_mixed_decision_policies_are_rejected(self):
        first = payload()
        second = payload()
        third = payload()
        second["protocol"]["feature_profile"] = "raw"

        candidate = summarize(
            [
                ("normal_repeat1.json", first),
                ("normal_repeat2.json", second),
                ("normal_repeat3.json", third),
            ]
        )["candidates"][0]

        self.assertFalse(candidate["hard_constraints_passed"])
        self.assertIsNone(candidate["decision_policy"])
        self.assertIn(
            "inconsistent_or_missing_decision_policy",
            candidate["hard_constraint_violations"],
        )

    def test_adaptation_calibration_and_evaluation_are_disjoint(self):
        train_rows = [{"x": value} for value in range(8)]
        train_labels = [0, 0, 0, 0, 1, 1, 1, 1]
        train_groups = ["source_a"] * 4 + ["source_b"] * 4
        test_rows = [{"x": value} for value in range(8, 20)]
        test_labels = [0, 0, 1, 1] * 3
        test_groups = (
            ["adapt"] * 4 + ["calibrate"] * 4 + ["evaluate"] * 4
        )

        quality = train_and_score(
            train_rows,
            train_labels,
            train_groups,
            test_rows,
            test_labels,
            seeds=[7],
            estimators=5,
            n_jobs=1,
            test_groups=test_groups,
            calibration_groups=["calibrate"],
            adaptation_groups=["adapt"],
            adaptation_policy="calibration_weighted",
            adaptation_weight_multiplier=2.0,
            threshold_policy="calibration_macro_f1",
            calibration_attack_recall_floor=0.5,
        )

        self.assertEqual(quality["train_flow_count"], 8)
        self.assertEqual(quality["adaptation_flow_count"], 4)
        self.assertEqual(quality["fit_flow_count"], 12)
        self.assertEqual(quality["calibration_flow_count"], 4)
        self.assertEqual(quality["test_flow_count"], 4)
        self.assertEqual(quality["evaluation_groups"], ["evaluate"])


if __name__ == "__main__":
    unittest.main()

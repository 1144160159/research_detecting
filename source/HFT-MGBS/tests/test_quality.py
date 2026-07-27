import unittest

from hft_mgbs.quality import (
    expected_calibration_error,
    minimum_metric,
    summarize_quality_runs,
)


class QualityHelperTests(unittest.TestCase):
    def test_ece_is_zero_for_perfect_binary_probabilities(self):
        self.assertEqual(expected_calibration_error([0, 1], [0.0, 1.0]), 0.0)

    def test_ece_validates_lengths(self):
        with self.assertRaises(ValueError):
            expected_calibration_error([0], [0.1, 0.2])

    def test_minimum_metric_uses_conservative_value(self):
        self.assertEqual(minimum_metric([{"f1": 0.9}, {"f1": 0.8}], "f1"), 0.8)

    def test_quality_summary_uses_worst_full_repeat(self):
        def payload(value):
            return {
                "candidate": {"batch_size": 512, "budget_us": 5000},
                "candidate_constraint_audit": {
                    "budget_overrun_count": 0,
                    "key_flow_coverage_min": 1.0,
                },
                "quality": {
                    "flow_sample_count": 100,
                    "feature_count": 10,
                    "conservative": {
                        "macro_f1_min": value,
                        "balanced_accuracy_min": value,
                        "capture_balanced_accuracy_min": value,
                        "auroc_min": value,
                        "auprc_min": value,
                        "ece_max": 1 - value,
                    },
                },
                "missing_final_evidence": ["holdout"],
            }

        summary = summarize_quality_runs(
            [
                ("normal_repeat1.json", payload(0.9)),
                ("normal_repeat2.json", payload(0.8)),
                ("normal_repeat3.json", payload(0.85)),
            ]
        )
        candidate = summary["candidates"][0]
        self.assertEqual(candidate["macro_f1_min"], 0.8)
        self.assertAlmostEqual(candidate["ece_max"], 0.2)
        self.assertTrue(candidate["repeat_gate_passed"])
        self.assertTrue(candidate["hard_constraints_passed"])
        self.assertEqual(summary["feasible_candidate_count"], 1)

    def test_high_quality_is_infeasible_when_execution_constraints_fail(self):
        payload = {
            "candidate": {"batch_size": 512, "budget_us": 5000},
            "candidate_constraint_audit": {
                "budget_overrun_count": 1,
                "key_flow_coverage_min": 0.0,
            },
            "quality": {
                "flow_sample_count": 100,
                "feature_count": 10,
                "conservative": {
                    "macro_f1_min": 0.999,
                    "balanced_accuracy_min": 0.999,
                    "capture_balanced_accuracy_min": 0.999,
                    "auroc_min": 0.999,
                    "auprc_min": 0.999,
                    "ece_max": 0.001,
                },
            },
            "missing_final_evidence": [],
        }

        summary = summarize_quality_runs(
            [
                ("normal_repeat1.json", payload),
                ("normal_repeat2.json", payload),
                ("normal_repeat3.json", payload),
            ]
        )

        candidate = summary["candidates"][0]
        self.assertFalse(candidate["hard_constraints_passed"])
        self.assertEqual(
            candidate["hard_constraint_violations"],
            ["budget_overrun", "key_flow_coverage"],
        )
        self.assertEqual(summary["feasible_candidate_count"], 0)


if __name__ == "__main__":
    unittest.main()

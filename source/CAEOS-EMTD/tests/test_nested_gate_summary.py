import unittest

from summarize_nested_gate import summarize


class NestedGateSummaryTest(unittest.TestCase):
    def test_summary_reports_oracle_regret_and_path_accuracy(self):
        runs = [
            {
                "scenario": "a",
                "seed": 7,
                "selected_risk": "support_union",
                "oracle_risk": "support_union",
                "selection_correct": True,
                "selected_auroc": 0.8,
                "support_auroc": 0.8,
                "conflict_auroc": 0.7,
                "oracle_auroc": 0.8,
                "oracle_regret": 0.0,
            },
            {
                "scenario": "a",
                "seed": 11,
                "selected_risk": "support_union",
                "oracle_risk": "cauchy_evidence",
                "selection_correct": False,
                "selected_auroc": 0.6,
                "support_auroc": 0.6,
                "conflict_auroc": 0.9,
                "oracle_auroc": 0.9,
                "oracle_regret": 0.3,
            },
        ]
        summary = summarize(runs)
        self.assertEqual(summary["overall"]["selection_accuracy"], 0.5)
        self.assertAlmostEqual(
            summary["overall"]["oracle_regret"]["mean"], 0.15
        )


if __name__ == "__main__":
    unittest.main()

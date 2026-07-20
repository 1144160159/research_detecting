from __future__ import annotations

import unittest

from summarize_neural_comparison import REPORT_METRICS, aggregate, merge_runs


def report(auroc: float, fpr95: float) -> dict[str, float]:
    values = {metric: 0.5 for metric in REPORT_METRICS}
    values["unknown_auroc"] = auroc
    values["unknown_fpr95"] = fpr95
    return values


class NeuralSummaryTest(unittest.TestCase):
    def test_merge_runs_combines_methods_on_same_task(self) -> None:
        base = {
            "suite": "hikari",
            "scenario": "probing",
            "seed": 7,
            "gate": 0.9,
            "gate_report": report(0.9, 0.1),
            "gate_selected_risk": "support",
        }
        runs = merge_runs(
            [
                {
                    **base,
                    "neural": {"closr": 0.8},
                    "neural_reports": {"closr": report(0.8, 0.2)},
                    "oracle_neural": 0.8,
                },
                {
                    **base,
                    "neural": {"cade": 0.7},
                    "neural_reports": {"cade": report(0.7, 0.3)},
                    "oracle_neural": 0.7,
                },
            ]
        )

        self.assertEqual(len(runs), 1)
        self.assertEqual(set(runs[0]["neural"]), {"closr", "cade"})
        self.assertEqual(runs[0]["oracle_neural"], 0.8)

    def test_aggregate_reports_secondary_metrics_with_fpr_orientation(self) -> None:
        runs = [
            {
                "gate_method": "nested_density_reliability_gate",
                "gate": 0.8,
                "gate_report": report(0.8, 0.2),
                "neural": {"closr": 0.7},
                "neural_reports": {"closr": report(0.7, 0.3)},
                "oracle_neural": 0.7,
            },
            {
                "gate_method": "nested_density_reliability_gate",
                "gate": 0.9,
                "gate_report": report(0.9, 0.1),
                "neural": {"closr": 0.85},
                "neural_reports": {"closr": report(0.85, 0.15)},
                "oracle_neural": 0.85,
            },
        ]

        summary = aggregate(runs)
        metrics = summary["methods"]["closr"]["metric_summary"]

        self.assertAlmostEqual(
            metrics["unknown_auroc"]["oriented_gate_delta"], 0.075
        )
        self.assertAlmostEqual(
            metrics["unknown_fpr95"]["oriented_gate_delta"], 0.075
        )


if __name__ == "__main__":
    unittest.main()

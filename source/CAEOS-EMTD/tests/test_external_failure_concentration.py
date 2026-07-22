from __future__ import annotations

import unittest

from analyze_external_failure_concentration import METRICS, analyze


class ExternalFailureConcentrationTests(unittest.TestCase):
    def test_concentration_and_pilot_coverage(self) -> None:
        metric_payloads = {}
        for metric in METRICS:
            blocks = []
            for index in range(102):
                gain = 0.01
                if index == 0:
                    gain = -0.2
                elif index == 1 and metric == "unknown_fpr95":
                    gain = -0.05
                blocks.append(
                    {
                        "scenario": f"suite/scenario_{index}",
                        "oriented_improvement": gain,
                    }
                )
            metric_payloads[metric] = {
                "oriented_mean_improvement": sum(
                    block["oriented_improvement"] for block in blocks
                )
                / len(blocks),
                "scenario_blocks": blocks,
            }
        confirmation = {
            "selected_algorithm": "candidate",
            "selected_comparator": "reference",
            "scenario_blocked_inference": {
                "scenario_count": 102,
                "metrics": metric_payloads,
            },
        }
        pilot = {"pilot": {"scenarios": {"suite": ["scenario_0", "other"]}}}
        result = analyze(confirmation, pilot)
        self.assertEqual(result["severe_scenario_count"], 1)
        self.assertEqual(result["lcb_severe_coverage_count"], 1)
        self.assertEqual(
            result["metric_diagnostics"]["unknown_fpr95"]["loss_count"], 2
        )
        self.assertEqual(
            result["joint_failure_scenarios"][0]["scenario"], "suite/scenario_0"
        )

    def test_rejects_incomplete_metric_blocks(self) -> None:
        confirmation = {
            "scenario_blocked_inference": {
                "scenario_count": 102,
                "metrics": {metric: {"scenario_blocks": []} for metric in METRICS},
            }
        }
        with self.assertRaisesRegex(ValueError, "102 scenario blocks"):
            analyze(confirmation, {"pilot": {"scenarios": {}}})


if __name__ == "__main__":
    unittest.main()

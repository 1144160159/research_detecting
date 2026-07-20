from __future__ import annotations

import unittest

from summarize_strict_v4_full103 import full_report_metrics, parse_task, routed_report


class StrictV4Full103SummaryTest(unittest.TestCase):
    def test_parse_task_preserves_scenario_underscores(self) -> None:
        self.assertEqual(parse_task("ddos_ack_fragmentation_seed7"), ("ddos_ack_fragmentation", 7))

    def test_parse_task_rejects_missing_seed(self) -> None:
        with self.assertRaisesRegex(ValueError, "seed suffix"):
            parse_task("ddos_ack_fragmentation")

    def test_full_report_preserves_paired_operating_rates(self) -> None:
        report = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.6,
        }
        self.assertEqual(full_report_metrics(report, "test"), report)

    def test_full_report_rejects_missing_operating_rate(self) -> None:
        report = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
        }
        with self.assertRaisesRegex(ValueError, "unknown_rejection_rate"):
            full_report_metrics(report, "test")

    def test_router_uses_pairwise_fallback(self) -> None:
        report = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.6,
        }
        router = {"routing": {"suite": {"method": "caeos_pairwise"}}}
        self.assertEqual(
            routed_report({"gate_report": report}, "suite", router, "task"), report
        )

    def test_router_uses_frozen_fusion(self) -> None:
        report = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.6,
        }
        router = {"routing": {"suite": {"method": "rank_cauchy"}}}
        self.assertEqual(
            routed_report(
                {"reports": {"rank_cauchy": report}}, "suite", router, "task"
            ),
            report,
        )


if __name__ == "__main__":
    unittest.main()

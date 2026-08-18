from __future__ import annotations

import unittest

from evaluate_strict_v4_neural_empirical_tail_hybrid_qualification import (
    contract_metrics,
)
from project_contract import evaluate_delivery_line
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    summarize_samples,
)


class NeuralEmpiricalTailHybridQualificationTest(unittest.TestCase):
    def test_contract_metrics_renames_legacy_fields(self) -> None:
        observed = contract_metrics(
            {
                "alert_accuracy": 0.97,
                "alert_precision": 0.98,
                "alert_recall": 0.96,
                "benign_fpr": 0.04,
                "known_attack_type_accuracy": 0.95,
                "unknown_attack_alert_recall": 0.951,
                "unknown_attack_recall": 0.952,
            }
        )
        self.assertEqual(observed["attack_recall"], 0.96)
        self.assertEqual(observed["unknown_label_recall"], 0.952)
        self.assertTrue(
            evaluate_delivery_line(observed, "engineering")["passed"]
        )
        self.assertTrue(evaluate_delivery_line(observed, "paper")["passed"])

    def test_engineering_gate_fails_unknown_alert_recall(self) -> None:
        observed = {
            "alert_accuracy": 0.99,
            "alert_precision": 0.99,
            "attack_recall": 0.99,
            "benign_fpr": 0.01,
            "known_attack_type_accuracy": 0.99,
            "unknown_attack_alert_recall": 0.949,
            "unknown_label_recall": 0.99,
        }
        result = evaluate_delivery_line(observed, "engineering")
        self.assertFalse(result["passed"])
        self.assertFalse(
            result["checks"]["unknown_attack_alert_recall"]["passed"]
        )

    def test_resource_summary_reports_load_gates(self) -> None:
        samples = [
            {
                "gpu_utilization_percent": 40.0,
                "memory_used_mib": 1000.0,
                "power_draw_watts": 100.0,
            },
            {
                "gpu_utilization_percent": 80.0,
                "memory_used_mib": 2000.0,
                "power_draw_watts": 200.0,
            },
        ]
        summary = summarize_samples(samples)
        self.assertEqual(summary["mean_gpu_utilization_percent"], 60.0)
        self.assertEqual(summary["fraction_samples_at_least_50_percent"], 0.5)
        self.assertEqual(summary["peak_gpu_memory_mib"], 2000.0)


if __name__ == "__main__":
    unittest.main()

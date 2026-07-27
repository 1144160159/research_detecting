from __future__ import annotations

import unittest

import numpy as np

from create_strict_v4_optimized_efficiency_protocol import create_protocol
from run_strict_v4_optimized_efficiency_block import method_order
from summarize_strict_v4_optimized_efficiency import median_ci


class OptimizedEfficiencyProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.v5_protocol = {"manifest_sha256": "a" * 64}
        training = [
            {"suite": f"suite{i}", "scenario": "sentinel", "repetition": 0}
            for i in range(21)
        ]
        inference = [
            {"suite": f"suite{i // 17}", "scenario": f"scenario{i}"}
            for i in range(102)
        ]
        self.v5_plan = {
            "manifest_sha256": "b" * 64,
            "protocol_manifest_sha256": "a" * 64,
            "training_blocks": training,
            "inference_blocks": inference,
        }
        self.hashes = {
            name: str(index) * 64
            for index, name in enumerate(
                (
                    "pairwise_runtime",
                    "optimized_pairwise_runtime",
                    "open_detect_runtime",
                    "triad_block_runner",
                    "triad_matrix_runner",
                    "triad_summarizer",
                    "protocol_creator",
                ),
                start=1,
            )
        }

    def test_latin_square_order_balances_all_positions(self) -> None:
        orders = [method_order(index) for index in range(3)]
        self.assertEqual(len(set(orders)), 3)
        for position in range(3):
            self.assertEqual(
                {order[position] for order in orders},
                {"original", "optimized", "comparator"},
            )

    def test_protocol_freezes_102_scenarios_before_results(self) -> None:
        protocol = create_protocol(
            v5_protocol=self.v5_protocol,
            v5_plan=self.v5_plan,
            v5_protocol_file_sha256="c" * 64,
            v5_plan_file_sha256="d" * 64,
            implementation_sha256=self.hashes,
            optimized_results_observed=0,
            source_v5_metrics_observed=18,
            source_v5_complete_at_freeze=False,
        )
        self.assertEqual(protocol["scenario_count"], 102)
        self.assertEqual(protocol["optimized_results_observed_at_freeze"], 0)
        self.assertFalse(
            protocol["source_v5_state_at_freeze"]["used_for_optimized_parameter_selection"]
        )
        self.assertTrue(protocol["claim_policy"]["v5_original_results_are_not_overwritten"])
        self.assertEqual(
            protocol["deployment_target"][
                "optimized_over_original_artifact_size_ratio_maximum"
            ],
            1.0,
        )

    def test_protocol_rejects_late_freeze(self) -> None:
        with self.assertRaisesRegex(ValueError, "before triad metrics"):
            create_protocol(
                v5_protocol=self.v5_protocol,
                v5_plan=self.v5_plan,
                v5_protocol_file_sha256="c" * 64,
                v5_plan_file_sha256="d" * 64,
                implementation_sha256=self.hashes,
                optimized_results_observed=1,
                source_v5_metrics_observed=18,
                source_v5_complete_at_freeze=False,
            )

    def test_median_ci_requires_102_scenarios(self) -> None:
        result = median_ci([2.0] * 102, 7)
        self.assertEqual(result["median"], 2.0)
        with self.assertRaisesRegex(ValueError, "102"):
            median_ci([2.0] * 101, 7)

    def test_negative_repetition_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            method_order(-1)


if __name__ == "__main__":
    unittest.main()

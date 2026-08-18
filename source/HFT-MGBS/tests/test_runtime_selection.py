from __future__ import annotations

import copy
import unittest

from hft_mgbs.runtime_selection import select_runtime_candidate


def config():
    return {
        "search_budget": {
            "minimum_candidates": 2,
            "maximum_candidates": 2,
        },
        "hard_thresholds": {
            "minimum_repeats": 3,
            "minimum_campaigns": 2,
            "minimum_total_repeats": 6,
            "max_pipeline_drop_rate": 0.0,
            "max_parse_reject_rate": 0.001,
            "min_observed_mpps": 0.01,
            "max_end_to_end_p99_us": 10000,
            "max_end_to_end_p999_us": 50000,
            "max_internal_feature_p99_us": 5000,
            "max_inference_batch_p99_us": 100000,
            "min_key_flow_coverage": 1.0,
            "max_budget_overrun_count": 0,
        },
        "candidates": [
            {
                "candidate_id": "wide",
                "prediction_execution": "thread",
                "cpu_set": "all",
                "eligible_cpu_count": 80,
            },
            {
                "candidate_id": "pinned",
                "prediction_execution": "thread",
                "cpu_set": "0-3",
                "eligible_cpu_count": 4,
            },
        ],
    }


def evidence(inference_p99, internal_p99, e2e_p99, code="a"):
    return {
        "scope": "virtual_link_live_diagnostic_repeat_audit",
        "accepted": True,
        "errors": [],
        "run_count": 3,
        "final_pareto_ingestion_allowed": False,
        "identity": {
            "candidate_id": "A09",
            "config_version": "rc1",
            "code_sha256": code * 64,
            "input_sha256": "b" * 64,
            "thresholds_sha256": "c" * 64,
        },
        "observed_worst_case": {
            "pipeline_drop_rate_max": 0.0,
            "parse_reject_rate_max": 0.0002,
            "observed_mpps_min": 0.0101,
            "end_to_end_p99_us_max": e2e_p99,
            "end_to_end_p999_us_max": 9000,
            "internal_feature_p99_us_max": internal_p99,
            "inference_batch_p99_us_max": inference_p99,
            "key_flow_coverage_min": 1.0,
            "budget_overrun_count_max": 0,
        },
    }


def campaigns(inference_p99, internal_p99, e2e_p99):
    return [
        evidence(inference_p99, internal_p99, e2e_p99, "a"),
        evidence(
            inference_p99 - 1000,
            internal_p99 - 100,
            e2e_p99 - 100,
            "d",
        ),
    ]


class RuntimeSelectionTest(unittest.TestCase):
    def test_dominating_passing_candidate_is_selected(self):
        result = select_runtime_candidate(
            config(),
            {
                "wide": campaigns(92000, 4900, 8200),
                "pinned": campaigns(91000, 4700, 8100),
            },
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(result["selected_candidate"], "pinned")
        self.assertEqual(result["pareto_front"], ["pinned"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_failed_repeat_audit_cannot_be_selected(self):
        failed = campaigns(80000, 4000, 7000)
        failed[0]["accepted"] = False
        failed[0]["errors"] = ["repeat1.run_status"]

        result = select_runtime_candidate(
            config(),
            {
                "wide": campaigns(92000, 4900, 8200),
                "pinned": failed,
            },
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(result["selected_candidate"], "wide")
        pinned = next(
            item
            for item in result["candidates"]
            if item["candidate_id"] == "pinned"
        )
        self.assertFalse(pinned["hard_pass"])
        self.assertIn(
            "evidence.campaign1.repeat_audit_failed", pinned["errors"]
        )
        self.assertEqual(pinned["campaign_count"], 2)
        self.assertEqual(pinned["total_run_count"], 6)

    def test_tail_threshold_violation_is_rejected(self):
        result = select_runtime_candidate(
            config(),
            {
                "wide": campaigns(102000, 4900, 8200),
                "pinned": campaigns(101000, 4700, 8100),
            },
        )

        self.assertFalse(result["accepted"])
        self.assertIsNone(result["selected_candidate"])
        self.assertIn(
            "no_candidate_passed_hard_constraints", result["errors"]
        )

    def test_recent_fast_campaign_cannot_hide_historical_failure(self):
        pinned = campaigns(65000, 1700, 1900)
        pinned[0]["accepted"] = False
        pinned[0]["observed_worst_case"][
            "inference_batch_p99_us_max"
        ] = 130000

        result = select_runtime_candidate(
            config(),
            {
                "wide": campaigns(92000, 4900, 8200),
                "pinned": pinned,
            },
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(result["selected_candidate"], "wide")
        rejected = next(
            item
            for item in result["candidates"]
            if item["candidate_id"] == "pinned"
        )
        self.assertEqual(
            rejected["metrics"]["inference_batch_p99_us_max"], 130000
        )
        self.assertIn(
            "hard_gate.inference_batch_p99_us_max.<=100000",
            rejected["errors"],
        )


if __name__ == "__main__":
    unittest.main()

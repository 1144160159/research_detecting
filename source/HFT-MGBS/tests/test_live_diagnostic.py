from __future__ import annotations

import copy
import unittest

from hft_mgbs.live_diagnostic import (
    audit_virtual_diagnostic_repeats,
)


def diagnostic_run(run_id):
    return {
        "schema_version": 1,
        "scope": "virtual_link_live_diagnostic",
        "run_status": "diagnostic_complete",
        "identity": {
            "run_id": run_id,
            "candidate_id": "A09",
            "config_version": "hft-mgbs-rc1",
            "code_sha256": "a" * 64,
            "input_sha256": "b" * 64,
            "thresholds_sha256": "c" * 64,
        },
        "capture": {
            "physical_nic_visible": False,
            "virtual_interface_visible": True,
        },
        "frozen_thresholds": {
            "diagnostic_only": True,
            "final_pareto_ingestion_allowed": False,
        },
        "counters": {
            "offered_packets": 1000,
            "nic_received_packets": 1000,
            "nic_drop_packets": 0,
            "capture_accepted_packets": 1000,
            "capture_ring_drop_packets": 0,
            "parser_accepted_packets": 999,
            "parser_rejected_packets": 1,
            "hft_processed_packets": 999,
            "hft_drop_packets": 0,
            "feature_events_produced": 100,
            "sender_delivered_events": 100,
            "sender_dropped_events": 0,
        },
        "load": {
            "observed_mpps_min": 0.01,
            "segmented_source_packets": 2,
        },
        "end_to_end_latency": {"p99_us": 1000, "p999_us": 2000},
        "internal_latency_not_end_to_end": {"p99_us": 500},
        "inference_batch_round_trip_latency": {"p99_us": 50000},
        "hft": {"key_flow_coverage": 1.0, "budget_overrun_count": 0},
        "composition": {
            "accepted": False,
            "diagnostic_accepted": True,
            "diagnostic_errors": [],
            "final_pareto_ingestion_allowed": False,
        },
    }


class VirtualLiveDiagnosticTest(unittest.TestCase):
    def test_three_consistent_diagnostics_are_aggregated(self):
        runs = [diagnostic_run("run-{}".format(index)) for index in range(3)]

        result = audit_virtual_diagnostic_repeats(runs)

        self.assertTrue(result["accepted"])
        self.assertEqual(result["run_count"], 3)
        self.assertFalse(result["final_pareto_ingestion_allowed"])
        self.assertEqual(
            result["observed_worst_case"]["pipeline_drop_rate_max"], 0
        )

    def test_physical_admission_marker_is_rejected(self):
        runs = [diagnostic_run("run-{}".format(index)) for index in range(3)]
        runs[1] = copy.deepcopy(runs[1])
        runs[1]["composition"]["final_pareto_ingestion_allowed"] = True

        result = audit_virtual_diagnostic_repeats(runs)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "repeat2.composition.final_pareto_marker", result["errors"]
        )


if __name__ == "__main__":
    unittest.main()

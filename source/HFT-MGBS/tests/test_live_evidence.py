from __future__ import annotations

import copy
import unittest

from hft_mgbs.live_evidence import audit_live_repeats, audit_live_run


def valid_run(repeat=1):
    return {
        "schema_version": 1,
        "scope": "physical_nic_live_replay",
        "run_status": "complete",
        "identity": {
            "run_id": "run-{}".format(repeat),
            "candidate_id": "batch512_budget5000_safety050",
            "config_version": "hft-v1",
            "code_sha256": "a" * 64,
            "input_sha256": "b" * 64,
            "thresholds_sha256": "c" * 64,
        },
        "capture": {
            "physical_nic_visible": True,
            "driver": "xdp",
            "interface": "ens1f0",
            "driver_counter_source": "ethtool+xdp",
            "isolated_test_traffic": True,
        },
        "frozen_thresholds": {
            "frozen": True,
            "target_load_mpps": 1.0,
            "target_load_gbps": None,
            "max_pipeline_drop_rate": 0.001,
            "max_parse_reject_rate": 0.01,
            "max_end_to_end_p99_us": 1000.0,
            "max_end_to_end_p999_us": 2000.0,
            "max_budget_overrun_count": 0,
            "min_key_flow_coverage": 0.99,
            "max_fallback_recovery_s": 1.0,
            "min_independent_macro_f1": 0.30,
            "min_independent_attack_recall": 0.60,
            "min_independent_benign_recall": 0.80,
            "min_independent_auprc": 0.10,
            "max_independent_ece": 0.20,
            "min_ground_truth_event_recall": 0.60,
            "min_run_duration_s": 60.0,
            "resource_max": {
                "cpu_utilization_max": 0.85,
                "gpu_utilization_max": 0.85,
                "memory_utilization_max": 0.85,
                "gpu_memory_utilization_max": 0.85,
            },
        },
        "counters": {
            "offered_packets": 100000,
            "nic_received_packets": 100000,
            "nic_drop_packets": 0,
            "capture_accepted_packets": 100000,
            "capture_ring_drop_packets": 0,
            "parser_accepted_packets": 99500,
            "parser_rejected_packets": 500,
            "hft_processed_packets": 99500,
            "hft_drop_packets": 0,
            "feature_events_produced": 1000,
            "sender_delivered_events": 1000,
            "sender_dropped_events": 0,
        },
        "load": {
            "packet_profile": "IMIX",
            "observed_mpps_min": 1.05,
            "rate_window_s": 1.0,
            "rate_sample_count": 60,
        },
        "end_to_end_latency": {
            "start_point": "nic_hardware_timestamp",
            "end_point": "feature_event_enqueued",
            "timestamp_provenance_verified": True,
            "sample_count": 1000,
            "p99_us": 800.0,
            "p999_us": 1200.0,
            "max_us": 1500.0,
        },
        "resources": {
            "cpu_utilization_max": 0.50,
            "gpu_utilization_max": 0.20,
            "memory_utilization_max": 0.30,
            "gpu_memory_utilization_max": 0.10,
        },
        "hft": {
            "budget_overrun_count": 0,
            "key_flow_coverage": 1.0,
        },
        "fallback": {
            "activation_verified": True,
            "real_traffic_during_fallback_verified": True,
            "same_candidate_pipeline_verified": True,
            "recovery_verified": True,
            "recovery_s_max": 0.30,
        },
        "independent_quality": {
            "macro_f1_min": 0.42,
            "attack_recall_min": 0.70,
            "benign_recall_min": 0.90,
            "auprc_min": 0.20,
            "ece_max": 0.10,
            "ground_truth_event_recall_min": 0.67,
        },
        "duration_s": 3600.0,
    }


class LiveEvidenceTest(unittest.TestCase):
    def test_complete_reconciled_live_run_is_accepted(self):
        self.assertTrue(audit_live_run(valid_run()).accepted)

    def test_boolean_claim_cannot_replace_physical_nic_visibility(self):
        run = valid_run()
        run["capture"]["physical_nic_visible"] = False

        audit = audit_live_run(run)

        self.assertFalse(audit.accepted)
        self.assertIn("capture.physical_nic_visible", audit.errors)

    def test_counter_mismatch_and_p99_violation_are_rejected(self):
        run = valid_run()
        run["counters"]["capture_accepted_packets"] = 99990
        run["end_to_end_latency"]["p99_us"] = 1100.0

        audit = audit_live_run(run)

        self.assertIn("counter_reconciliation.nic_to_capture", audit.errors)
        self.assertIn("hard_constraint.end_to_end_p99", audit.errors)

    def test_repeat_identity_must_be_consistent(self):
        runs = [valid_run(1), valid_run(2), valid_run(3)]
        runs[2] = copy.deepcopy(runs[2])
        runs[2]["identity"]["config_version"] = "different"

        audit = audit_live_repeats(runs)

        self.assertFalse(audit.accepted)
        self.assertIn(
            "repeat_identity_inconsistent.config_version", audit.errors
        )

    def test_target_load_is_a_hard_constraint(self):
        run = valid_run()
        run["load"]["observed_mpps_min"] = 0.90

        audit = audit_live_run(run)

        self.assertIn("hard_constraint.target_load_mpps", audit.errors)

    def test_average_load_or_unverified_timestamp_cannot_substitute(self):
        run = valid_run()
        run["load"]["rate_sample_count"] = 0
        run["end_to_end_latency"]["timestamp_provenance_verified"] = False

        audit = audit_live_run(run)

        self.assertIn("load.rate_sample_count.zero", audit.errors)
        self.assertIn(
            "end_to_end_latency.timestamp_provenance_verified",
            audit.errors,
        )

    def test_all_independent_quality_gates_are_enforced(self):
        run = valid_run()
        run["independent_quality"]["attack_recall_min"] = 0.59
        run["independent_quality"]["benign_recall_min"] = 0.79
        run["independent_quality"]["auprc_min"] = 0.09
        run["independent_quality"]["ece_max"] = 0.21

        audit = audit_live_run(run)

        self.assertIn(
            "hard_constraint.independent_attack_recall", audit.errors
        )
        self.assertIn(
            "hard_constraint.independent_benign_recall", audit.errors
        )
        self.assertIn("hard_constraint.independent_auprc", audit.errors)
        self.assertIn("hard_constraint.independent_ece", audit.errors)

    def test_external_threshold_content_and_hash_must_match(self):
        runs = [valid_run(1), valid_run(2), valid_run(3)]
        expected = copy.deepcopy(runs[0]["frozen_thresholds"])

        accepted = audit_live_repeats(
            runs,
            expected_thresholds=expected,
            expected_thresholds_sha256="c" * 64,
        )
        self.assertTrue(accepted.accepted)

        expected["max_pipeline_drop_rate"] = 0.0
        rejected = audit_live_repeats(
            runs,
            expected_thresholds=expected,
            expected_thresholds_sha256="d" * 64,
        )
        self.assertFalse(rejected.accepted)
        self.assertIn(
            "repeat1.external_thresholds_content_mismatch",
            rejected.errors,
        )
        self.assertIn(
            "repeat1.external_thresholds_sha256_mismatch",
            rejected.errors,
        )


if __name__ == "__main__":
    unittest.main()

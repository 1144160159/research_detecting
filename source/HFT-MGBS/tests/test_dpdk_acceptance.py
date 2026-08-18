from __future__ import annotations

import copy
import unittest

from scripts.validate_dpdk_run import evaluate


THRESHOLD_HASH = "a" * 64
INPUT_HASHES = {
    "thresholds": THRESHOLD_HASH,
    "result": "b" * 64,
    "process_time": "c" * 64,
    "hugepage_snapshot": "d" * 64,
    "runner": "e" * 64,
    "binary": "f" * 64,
    "dpdk_build_manifest": "2" * 64,
    "cpu_preflight": "4" * 64,
    "validator": "1" * 64,
}
HUGEPAGE_SNAPSHOT = {
    "schema_version": 2,
    "source": "sysfs_all_numa_nodes_reserved_hugepages",
    "node_glob": (
        "/sys/devices/system/node/node*/hugepages/"
        "hugepages-2048kB/nr_hugepages"
    ),
    "target_node_path": (
        "/sys/devices/system/node/node1/hugepages/"
        "hugepages-2048kB/nr_hugepages"
    ),
    "sampled_at": "2026-07-31T00:00:00Z",
    "nodes_before": [
        {
            "path": (
                "/sys/devices/system/node/node0/hugepages/"
                "hugepages-2048kB/nr_hugepages"
            ),
            "count": 0,
        },
        {
            "path": (
                "/sys/devices/system/node/node1/hugepages/"
                "hugepages-2048kB/nr_hugepages"
            ),
            "count": 0,
        },
    ],
    "nodes_during": [
        {
            "path": (
                "/sys/devices/system/node/node0/hugepages/"
                "hugepages-2048kB/nr_hugepages"
            ),
            "count": 0,
        },
        {
            "path": (
                "/sys/devices/system/node/node1/hugepages/"
                "hugepages-2048kB/nr_hugepages"
            ),
            "count": 512,
        },
    ],
    "global_count_before": 0,
    "global_count_during": 512,
    "page_size_bytes": 2 * 1024 * 1024,
}
CPU_PREFLIGHT_EVIDENCE = {
    "schema_version": 1,
    "scope": "non_mutating_dpdk_cpu_idle_preflight",
    "requested_cpus": [28, 36, 44],
    "include_smt_siblings": True,
    "effective_cpus": [28, 36, 44, 84, 92, 100],
    "max_utilization_threshold": 0.05,
    "sample_seconds": 1.0,
    "samples": 5,
    "max_observed_utilization": {
        "28": 0.01,
        "36": 0.01,
        "44": 0.01,
        "84": 0.01,
        "92": 0.01,
        "100": 0.01,
    },
    "evidence_complete": True,
    "passed": True,
    "mutations_performed": False,
}


def thresholds():
    return {
        "schema_version": 2,
        "qualification_mode": "release_gate_v2",
        "candidate_id": "R0_DPDK_Q1_B128_RELEASE_V2",
        "frozen": True,
        "diagnostic_only": True,
        "target_load_mpps": 1.0,
        "frame_size_bytes": 64,
        "burst_size": 128,
        "queue_count": 1,
        "main_cpu": 28,
        "rx_cpus": [36],
        "tx_cpus": [44],
        "realtime_priority": 0,
        "capture_pci": "0000:cb:00.0",
        "replay_pci": "0000:cb:00.1",
        "expected_backend": "dpdk_bnx2x_single_queue",
        "binary_freeze_pending": False,
        "expected_binary_sha256": "f" * 64,
        "expected_runner_sha256": "e" * 64,
        "expected_validator_sha256": "1" * 64,
        "expected_composer_sha256": "5" * 64,
        "expected_cpu_preflight_sha256": "6" * 64,
        "expected_dpdk_preflight_sha256": "7" * 64,
        "expected_dpdk_build_manifest_sha256": "2" * 64,
        "hugepage_count": 512,
        "hugepage_size_bytes": 2097152,
        "hugepage_target_node_path": (
            "/sys/devices/system/node/node1/hugepages/"
            "hugepages-2048kB/nr_hugepages"
        ),
        "hugepage_node_glob": (
            "/sys/devices/system/node/node*/hugepages/"
            "hugepages-2048kB/nr_hugepages"
        ),
        "interface_baseline": {
            "profile": "dedicated_bnx2x_kernel_default_v1",
            "admin_up": True,
            "mtu": 1500,
            "txqlen": 1000,
            "features_sha256": "8" * 64,
            "coalesce_sha256": "9" * 64,
            "ring_sha256": "a" * 64,
            "channels_sha256": "b" * 64,
            "qdisc_sha256": "c" * 64,
        },
        "max_pipeline_drop_rate": 0.0,
        "max_end_to_end_p99_us": 100.0,
        "max_end_to_end_p999_us": 500.0,
        "rate_window_alignment": "shared_monotonic_epoch_fixed_1s_v1",
        "min_rate_full_windows": 15,
        "latency_sampling": {
            "stride_packets": 1024,
            "min_samples": 10000,
            "timestamp_source": "dpdk_tsc_embedded_tx_rx_v1",
        },
        "cpu_preflight": {
            "max_utilization": 0.05,
            "sample_seconds": 1.0,
            "samples": 5,
            "include_smt_siblings": True,
        },
        "min_run_duration_s": 15,
        "resource_max": {
            "process_cpu_cores_average": 1.5,
            "process_rss_kib": 65536,
            "process_wall_overhead_s": 5.0,
            "hugepage_reserved_bytes": 1073741824,
        },
        "resource_semantics": {
            "process_cpu_cores_average": "gnu_time_cpu_percent_div_100",
            "process_rss_kib": "gnu_time_max_rss_kib",
            "process_wall_overhead_s": "gnu_time_elapsed_minus_rust_duration",
            "hugepage_reserved_bytes":
                "sysfs_all_numa_nodes_reserved_count_during_run",
        },
        "final_pareto_ingestion_allowed": False,
    }


def result():
    return {
        "schema_version": 5,
        "scope": "r0_dpdk_bnx2x_capture_only",
        "backend": "dpdk_bnx2x_single_queue",
        "candidate_id": "R0_DPDK_Q1_B128_RELEASE_V2",
        "frozen_thresholds_sha256": THRESHOLD_HASH,
        "target_mpps": 1.0,
        "frame_size_bytes": 64,
        "burst_size": 128,
        "queue_count": 1,
        "main_cpu": 28,
        "rx_cpus": [36],
        "tx_cpus": [44],
        "realtime_priority": 0,
        "capture_pci": "0000:cb:00.0",
        "replay_pci": "0000:cb:00.1",
        "max_end_to_end_p99_us": 100.0,
        "max_end_to_end_p999_us": 500.0,
        "duration_s": 15.1,
        "offered_packets": 15_150_000,
        "received_packets": 15_150_000,
        "offered_received_gap": 0,
        "observed_tx_mpps_min_1s": 1.01,
        "observed_rx_mpps_min_1s": 1.01,
        "rate_window_alignment": "shared_monotonic_epoch_fixed_1s_v1",
        "tx_rate_full_windows": 15,
        "rx_rate_full_windows": 15,
        "capture_stats_delta": {"imissed": 0, "ierrors": 0, "rx_nombuf": 0},
        "replay_stats_delta": {"oerrors": 0},
        "latency_sample_stride": 1024,
        "latency_timestamp_source": "dpdk_tsc_embedded_tx_rx_v1",
        "end_to_end_latency_us": {
            "samples": 12000,
            "p99": 80.0,
            "p999": 420.0,
        },
        "hard_gate_errors": [],
        "data_plane_qualified": True,
        "resource_gate_evaluated": False,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


PROCESS_TIME = """
    Percent of CPU this job got: 100%
    Elapsed (wall clock) time (h:mm:ss or m:ss): 0:18.47
    Maximum resident set size (kbytes): 40460
"""


class DpdkAcceptanceTest(unittest.TestCase):
    def evaluate(self, threshold=None, raw_result=None, process_time=PROCESS_TIME):
        return evaluate(
            threshold if threshold is not None else thresholds(),
            raw_result if raw_result is not None else result(),
            process_time,
            512,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            INPUT_HASHES,
            HUGEPAGE_SNAPSHOT,
            CPU_PREFLIGHT_EVIDENCE,
        )

    def test_complete_run_passes_capture_only(self):
        acceptance = self.evaluate()
        self.assertTrue(acceptance["data_resource_qualified"])
        self.assertFalse(acceptance["runner_qualified"])
        self.assertFalse(acceptance["r0_capture_only_qualified"])
        self.assertFalse(acceptance["full_pipeline_qualified"])
        self.assertFalse(acceptance["final_pareto_ingestion_allowed"])

    def test_rx_rate_is_independent_hard_gate(self):
        raw_result = result()
        raw_result["observed_rx_mpps_min_1s"] = 0.99
        acceptance = self.evaluate(raw_result=raw_result)
        self.assertIn("rx_target_load", acceptance["errors"])
        self.assertFalse(acceptance["runner_qualified"])

    def test_missing_result_and_resource_observation_fail_closed(self):
        input_hashes = dict(INPUT_HASHES)
        input_hashes.pop("result")
        acceptance = evaluate(
            thresholds(),
            None,
            "",
            512,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            input_hashes,
            HUGEPAGE_SNAPSHOT,
            CPU_PREFLIGHT_EVIDENCE,
        )
        self.assertIn("result_missing", acceptance["errors"])
        self.assertIn("resource_evidence_incomplete", acceptance["errors"])

    def test_each_resource_limit_is_enforced(self):
        cpu = self.evaluate(
            process_time=PROCESS_TIME.replace("100%", "151%")
        )
        self.assertIn("process_cpu_resource", cpu["errors"])

        rss = self.evaluate(
            process_time=PROCESS_TIME.replace("40460", "65537")
        )
        self.assertIn("process_rss_resource", rss["errors"])

        threshold = copy.deepcopy(thresholds())
        threshold["resource_max"]["hugepage_reserved_bytes"] = 1073741823
        hugepages = self.evaluate(threshold=threshold)
        self.assertIn("hugepage_resource", hugepages["errors"])

    def test_legacy_or_unfrozen_thresholds_are_rejected(self):
        threshold = thresholds()
        threshold["schema_version"] = 1
        acceptance = self.evaluate(threshold=threshold)
        self.assertIn("threshold_schema", acceptance["errors"])

    def test_threshold_and_candidate_identity_are_bound(self):
        raw_result = result()
        raw_result["frozen_thresholds_sha256"] = "b" * 64
        raw_result["candidate_id"] = "other"
        acceptance = self.evaluate(raw_result=raw_result)
        self.assertIn("threshold_identity", acceptance["errors"])
        self.assertIn("candidate_identity", acceptance["errors"])

    def test_raw_result_cannot_claim_wrapper_or_final_qualification(self):
        raw_result = result()
        raw_result["r0_capture_only_qualified"] = True
        raw_result["resource_gate_evaluated"] = True
        raw_result["final_pareto_ingestion_allowed"] = True
        acceptance = self.evaluate(raw_result=raw_result)
        self.assertIn("result_schema", acceptance["errors"])
        self.assertFalse(acceptance["runner_qualified"])

    def test_boolean_or_missing_counters_do_not_pass_as_zero(self):
        raw_result = result()
        raw_result["offered_received_gap"] = False
        raw_result["capture_stats_delta"]["imissed"] = False
        raw_result["replay_stats_delta"]["oerrors"] = False
        acceptance = self.evaluate(raw_result=raw_result)
        self.assertIn("offered_received_mismatch", acceptance["errors"])
        self.assertIn("capture_drop", acceptance["errors"])
        self.assertIn("replay_tx_error", acceptance["errors"])

    def test_hugepage_identity_is_independent_of_resource_limit(self):
        acceptance = evaluate(
            thresholds(),
            result(),
            PROCESS_TIME,
            511,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            INPUT_HASHES,
            {**HUGEPAGE_SNAPSHOT, "global_count_during": 511},
            CPU_PREFLIGHT_EVIDENCE,
        )
        self.assertIn("hugepage_identity", acceptance["errors"])

    def test_hugepage_evidence_covers_all_numa_nodes(self):
        snapshot = copy.deepcopy(HUGEPAGE_SNAPSHOT)
        snapshot["nodes_during"][0]["count"] = 1
        snapshot["global_count_during"] = 513
        acceptance = evaluate(
            thresholds(),
            result(),
            PROCESS_TIME,
            513,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            INPUT_HASHES,
            snapshot,
            CPU_PREFLIGHT_EVIDENCE,
        )
        self.assertIn("hugepage_evidence", acceptance["errors"])
        self.assertIn("hugepage_identity", acceptance["errors"])

    def test_shared_rate_windows_latency_sampling_and_wall_time_are_hard_gates(self):
        raw_result = result()
        raw_result["rx_rate_full_windows"] = 14
        raw_result["end_to_end_latency_us"]["samples"] = 9999
        acceptance = self.evaluate(
            raw_result=raw_result,
            process_time=PROCESS_TIME.replace("0:18.47", "0:20.50"),
        )
        self.assertIn("rate_window_evidence", acceptance["errors"])
        self.assertIn("latency_evidence_incomplete", acceptance["errors"])
        self.assertIn("process_wall_time", acceptance["errors"])

    def test_all_evidence_inputs_are_hash_bound(self):
        hashes = dict(INPUT_HASHES)
        hashes.pop("binary")
        acceptance = evaluate(
            thresholds(),
            result(),
            PROCESS_TIME,
            512,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            hashes,
            HUGEPAGE_SNAPSHOT,
            CPU_PREFLIGHT_EVIDENCE,
        )
        self.assertIn("evidence_binding", acceptance["errors"])

    def test_frozen_artifact_hashes_are_enforced(self):
        hashes = dict(INPUT_HASHES)
        hashes["binary"] = "3" * 64
        acceptance = evaluate(
            thresholds(),
            result(),
            PROCESS_TIME,
            512,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            hashes,
            HUGEPAGE_SNAPSHOT,
            CPU_PREFLIGHT_EVIDENCE,
        )
        self.assertIn("artifact_identity", acceptance["errors"])

    def test_cpu_preflight_evidence_is_bound_and_fail_closed(self):
        cpu_evidence = copy.deepcopy(CPU_PREFLIGHT_EVIDENCE)
        cpu_evidence["passed"] = False
        cpu_evidence["max_observed_utilization"]["44"] = 0.06
        acceptance = evaluate(
            thresholds(),
            result(),
            PROCESS_TIME,
            512,
            2 * 1024 * 1024,
            THRESHOLD_HASH,
            INPUT_HASHES,
            HUGEPAGE_SNAPSHOT,
            cpu_evidence,
        )
        self.assertIn("cpu_preflight_evidence", acceptance["errors"])


if __name__ == "__main__":
    unittest.main()

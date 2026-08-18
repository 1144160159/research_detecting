from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.live_evidence import audit_live_run
from hft_mgbs.live_raw import compose_live_run


ROOT = Path(__file__).resolve().parents[1]


def write_json(path, values):
    Path(path).write_text(
        json.dumps(values, sort_keys=True) + "\n", encoding="utf-8"
    )


def thresholds():
    return {
        "frozen": True,
        "target_load_mpps": 1.0,
        "target_load_gbps": None,
        "max_pipeline_drop_rate": 0.0,
        "max_parse_reject_rate": 0.01,
        "max_end_to_end_p99_us": 1000.0,
        "max_end_to_end_p999_us": 2000.0,
        "max_budget_overrun_count": 0,
        "min_key_flow_coverage": 0.99,
        "max_fallback_recovery_s": 0.3,
        "min_independent_macro_f1": 0.7,
        "min_independent_attack_recall": 0.72,
        "min_independent_benign_recall": 0.93,
        "min_independent_auprc": 0.45,
        "max_independent_ece": 0.05,
        "min_ground_truth_event_recall": 0.7,
        "min_run_duration_s": 60.0,
        "resource_max": {
            "cpu_utilization_max": 0.85,
            "gpu_utilization_max": 0.85,
            "memory_utilization_max": 0.85,
            "gpu_memory_utilization_max": 0.85,
        },
    }


class LiveRawCompositionTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        self.counter_map = json.loads(
            (
                ROOT
                / "configs"
                / "live_counter_map_bnx2x_rc1.json"
            ).read_text(encoding="utf-8")
        )
        binary = self.root / "hft-capture.bin"
        binary.write_bytes(b"binary")
        input_path = self.root / "input.pcap"
        input_path.write_bytes(b"pcap")
        threshold_path = self.root / "frozen_thresholds.json"
        write_json(threshold_path, thresholds())
        manifest = "\n".join(
            [
                "run_id=live-1",
                "status=raw_evidence_complete",
                "candidate_id=A09",
                "capture_interface=ens8f0",
                "replay_interface=ens8f1",
                "binary={}".format(binary),
                "binary_sha256={}".format(
                    hashlib.sha256(binary.read_bytes()).hexdigest()
                ),
                "replay_input={}".format(input_path),
                "input_sha256={}".format(
                    hashlib.sha256(input_path.read_bytes()).hexdigest()
                ),
                "thresholds_sha256={}".format(
                    hashlib.sha256(threshold_path.read_bytes()).hexdigest()
                ),
            ]
        )
        (self.root / "manifest.txt").write_text(
            manifest + "\n", encoding="utf-8"
        )
        write_json(
            self.root / "metrics.json",
            {
                "capture_driver": "af_packet",
                "packets_received": 66_000_000,
                "capture_packets_dropped": 0,
                "packets_parsed": 65_999_000,
                "parse_rejected": 1000,
                "flows_emitted": 10,
                "gpu_flows_scored": 10,
                "fallback_flows": 0,
                "budget_overrun_count": 0,
                "key_flow_coverage": 1.0,
                "flow_materialization_to_feature_enqueue_latency": {
                    "samples": 10,
                    "p50_us": 100.0,
                    "p99_us": 200.0,
                    "p999_us": 250.0,
                    "max_us": 300.0,
                },
                "gpu_batch_round_trip_latency": {
                    "samples": 10,
                    "p50_us": 30000.0,
                    "p99_us": 50000.0,
                    "p999_us": 60000.0,
                    "max_us": 70000.0,
                },
                "timestamp_provenance": (
                    "kernel_software_receive_realtime_so_timestampns"
                ),
                "kernel_timestamp_anomalies": 0,
                "realtime_clock_step_count": 0,
                "kernel_receive_to_feature_enqueue_latency": {
                    "samples": 10,
                    "p50_us": 500.0,
                    "p99_us": 800.0,
                    "p999_us": 1200.0,
                    "max_us": 1500.0,
                },
            },
        )
        write_json(
            self.root / "injector_metrics.json",
            {
                "scope": "physical_nic_live_replay",
                "interface_mtu": 1500,
                "source_packets_read": 66_000_000,
                "segmented_source_packets": 0,
                "generated_tcp_segments": 0,
                "rate_headroom_ratio": 1.01,
                "offered_packets": 66_000_000,
                "duration_s": 60.0,
                "observed_mpps_min_1s": 1.05,
                "observed_gbps_min_1s": 1.0,
                "rate_window_s": 1.0,
                "rate_sample_count": 60,
            },
        )
        preflight = {
            "accepted": True,
            "physical_nic_visible": True,
            "virtual_interface_visible": False,
            "driver": "bnx2x",
            "scope": "physical_nic_live_host_preflight",
        }
        write_json(self.root / "capture_preflight.json", preflight)
        write_json(self.root / "replay_preflight.json", preflight)
        self._write_counter_pair(
            "capture",
            before={
                "rx_packets": 0,
                "rx_dropped": 0,
                "rx_errors": 0,
                "rx_missed_errors": 0,
            },
            after={
                "rx_packets": 66_000_000,
                "rx_dropped": 0,
                "rx_errors": 0,
                "rx_missed_errors": 0,
            },
            ethtool_before={"rx_discards": 0, "rx_brb_truncate": 0},
            ethtool_after={"rx_discards": 0, "rx_brb_truncate": 0},
        )
        self._write_counter_pair(
            "replay",
            before={"tx_packets": 0},
            after={"tx_packets": 66_000_000},
        )
        self.latency = self.root / "latency.json"
        write_json(
            self.latency,
            {
                "timestamp_provenance_verified": True,
                "start_point": "kernel_receive_monotonic",
                "end_point": "feature_event_enqueued",
                "sample_count": 10,
                "p99_us": 800.0,
                "p999_us": 1200.0,
                "max_us": 1500.0,
            },
        )
        self.resources = self.root / "resources.json"
        write_json(
            self.resources,
            {
                "cpu_utilization_max": 0.5,
                "gpu_utilization_max": 0.1,
                "memory_utilization_max": 0.2,
                "gpu_memory_utilization_max": 0.1,
            },
        )
        self.fallback = self.root / "fallback.json"
        write_json(
            self.fallback,
            {
                "activation_verified": True,
                "real_traffic_during_fallback_verified": True,
                "same_candidate_pipeline_verified": True,
                "recovery_verified": True,
                "recovery_s_max": 0.1,
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def _write_counter_pair(
        self,
        prefix,
        before,
        after,
        ethtool_before=None,
        ethtool_after=None,
    ):
        for suffix, values in (("before", before), ("after", after)):
            (self.root / "{}_{}_sysfs_counters.txt".format(
                prefix, suffix
            )).write_text(
                "".join(
                    "{}={}\n".format(key, value)
                    for key, value in values.items()
                ),
                encoding="utf-8",
            )
        if ethtool_before is not None:
            for suffix, values in (
                ("before", ethtool_before),
                ("after", ethtool_after),
            ):
                (self.root / "{}_{}_ethtool_stats.txt".format(
                    prefix, suffix
                )).write_text(
                    "NIC statistics:\n"
                    + "".join(
                        "     {}: {}\n".format(key, value)
                        for key, value in values.items()
                    ),
                    encoding="utf-8",
                )

    def compose(self, **overrides):
        arguments = {
            "latency_evidence": self.latency,
            "resource_evidence": self.resources,
            "fallback_evidence": self.fallback,
        }
        arguments.update(overrides)
        return compose_live_run(
            self.root,
            self.release,
            self.counter_map,
            **arguments,
        )

    def test_complete_reconciled_raw_evidence_is_accepted(self):
        payload = self.compose()

        self.assertTrue(payload["composition"]["accepted"])
        self.assertEqual(payload["run_status"], "complete")
        self.assertEqual(
            payload["counters"]["offered_packets"], 66_000_000
        )
        self.assertIn(
            "internal_latency_not_end_to_end", payload
        )

    def test_missing_true_latency_resources_and_fallback_fail_closed(self):
        metrics = json.loads(
            (self.root / "metrics.json").read_text(encoding="utf-8")
        )
        metrics["timestamp_provenance"] = "unverified"
        write_json(self.root / "metrics.json", metrics)
        payload = self.compose(
            latency_evidence=None,
            resource_evidence=None,
            fallback_evidence=None,
        )

        self.assertFalse(payload["composition"]["accepted"])
        errors = payload["composition"]["errors"]
        self.assertIn(
            "missing_external_evidence.kernel_to_feature_latency",
            errors,
        )
        self.assertIn(
            "missing_external_evidence.cross_host_resource_maxima",
            errors,
        )
        self.assertIn(
            "missing_external_evidence.live_fallback_under_traffic",
            errors,
        )

    def test_verified_kernel_timestamp_metric_can_supply_latency(self):
        payload = self.compose(latency_evidence=None)

        self.assertTrue(payload["composition"]["accepted"])
        self.assertEqual(
            payload["end_to_end_latency"]["start_point"],
            "kernel_receive_realtime",
        )
        self.assertTrue(
            payload["end_to_end_latency"][
                "timestamp_provenance_verified"
            ]
        )

    def test_verified_xdp_metadata_can_supply_latency(self):
        metrics = json.loads(
            (self.root / "metrics.json").read_text(encoding="utf-8")
        )
        metrics["capture_driver"] = "xdp_skb"
        metrics["timestamp_provenance"] = (
            "xdp_bpf_ktime_get_ns_converted_realtime_metadata"
        )
        write_json(self.root / "metrics.json", metrics)

        payload = self.compose(latency_evidence=None)

        self.assertTrue(payload["composition"]["accepted"])
        self.assertEqual(payload["capture"]["driver"], "xdp")
        self.assertEqual(
            payload["end_to_end_latency"]["start_point"],
            "kernel_xdp_entry_realtime",
        )
        self.assertTrue(
            payload["end_to_end_latency"][
                "timestamp_provenance_verified"
            ]
        )

    def test_unexplained_replay_tx_mismatch_is_rejected(self):
        metrics = json.loads(
            (self.root / "injector_metrics.json").read_text(
                encoding="utf-8"
            )
        )
        metrics["offered_packets"] -= 1
        write_json(self.root / "injector_metrics.json", metrics)

        payload = self.compose()

        self.assertFalse(payload["composition"]["accepted"])
        self.assertIn(
            "counter_reconciliation.injector_to_replay_tx",
            payload["composition"]["errors"],
        )

    def test_internal_and_inference_p99_remain_hard_gates(self):
        metrics = json.loads(
            (self.root / "metrics.json").read_text(encoding="utf-8")
        )
        metrics["flow_materialization_to_feature_enqueue_latency"][
            "p99_us"
        ] = 5001
        metrics["gpu_batch_round_trip_latency"]["p99_us"] = 100001
        write_json(self.root / "metrics.json", metrics)

        payload = self.compose()

        self.assertFalse(payload["composition"]["accepted"])
        self.assertIn(
            "hard_constraint.internal_feature_p99",
            payload["composition"]["errors"],
        )
        self.assertIn(
            "hard_constraint.gpu_batch_p99",
            payload["composition"]["errors"],
        )

    def test_virtual_diagnostic_passes_normal_path_but_not_final_gate(self):
        with (self.root / "manifest.txt").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write("evidence_scope=virtual_link_live_diagnostic\n")
            handle.write("diagnostic_only=true\n")
        preflight = {
            "accepted": True,
            "physical_nic_visible": False,
            "virtual_interface_visible": True,
            "driver": "virtual",
            "scope": "virtual_link_live_host_preflight",
        }
        write_json(self.root / "capture_preflight.json", preflight)
        write_json(self.root / "replay_preflight.json", preflight)
        injector = json.loads(
            (self.root / "injector_metrics.json").read_text(
                encoding="utf-8"
            )
        )
        injector["scope"] = "virtual_link_live_diagnostic"
        write_json(self.root / "injector_metrics.json", injector)
        counter_map = {
            "config_version": "veth-diagnostic-v1",
            "driver": "virtual",
            "replay_transmitted_packets": {
                "source": "sysfs",
                "counter": "tx_packets",
            },
            "capture_received_packets": {
                "source": "sysfs",
                "counter": "rx_packets",
            },
            "capture_nic_drop_packets": {
                "source": "sysfs",
                "counter": "rx_dropped",
            },
            "fail_if_nonzero_capture_counters": [
                {"source": "sysfs", "counter": "rx_errors"},
                {
                    "source": "sysfs",
                    "counter": "rx_missed_errors",
                },
            ],
        }

        payload = compose_live_run(
            self.root,
            self.release,
            counter_map,
            latency_evidence=None,
            resource_evidence=None,
            fallback_evidence=None,
        )

        self.assertFalse(payload["composition"]["accepted"])
        self.assertTrue(
            payload["composition"]["diagnostic_accepted"],
            payload["composition"],
        )
        self.assertFalse(
            payload["composition"]["final_pareto_ingestion_allowed"]
        )
        self.assertEqual(payload["run_status"], "diagnostic_complete")
        self.assertFalse(audit_live_run(payload).accepted)

    def test_physical_diagnostic_passes_mechanics_but_not_final_gate(self):
        with (self.root / "manifest.txt").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write("evidence_scope=physical_link_live_diagnostic\n")
            handle.write("diagnostic_only=true\n")
        injector = json.loads(
            (self.root / "injector_metrics.json").read_text(
                encoding="utf-8"
            )
        )
        injector["scope"] = "physical_link_live_diagnostic"
        write_json(self.root / "injector_metrics.json", injector)

        payload = self.compose(
            latency_evidence=None,
            resource_evidence=None,
            fallback_evidence=None,
        )

        self.assertFalse(payload["composition"]["accepted"])
        self.assertTrue(
            payload["composition"]["diagnostic_accepted"],
            payload["composition"],
        )
        self.assertFalse(
            payload["composition"]["final_pareto_ingestion_allowed"]
        )
        self.assertEqual(payload["run_status"], "diagnostic_complete")
        self.assertFalse(audit_live_run(payload).accepted)


if __name__ == "__main__":
    unittest.main()

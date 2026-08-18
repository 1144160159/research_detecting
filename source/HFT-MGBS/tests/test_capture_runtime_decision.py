import copy
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from hft_mgbs.capture_runtime_decision import (
    DPDK_BACKEND,
    GENERIC_XDP_BACKEND,
    NATIVE_XDP_BACKEND,
    RuntimeDecisionContractError,
    evaluate_runtime_decision,
)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 12, 12, 0, 5, tzinfo=timezone.utc)
OBSERVED = "2026-08-12T12:00:00Z"
SHA256 = "a" * 64


def policy():
    return json.loads(
        (ROOT / "configs" / "xdp_dpdk_runtime_policy_v1.json").read_text(
            encoding="utf-8"
        )
    )


def xdp_capability(*, eligible=True):
    return {
        "observed_at_utc": OBSERVED,
        "attach_mode": "native" if eligible else "generic",
        "native_attach_succeeded": eligible,
        "af_xdp_bind_mode": "zerocopy" if eligible else "copy",
        "forced_zerocopy_bind_succeeded": eligible,
        "copy_mode_active": not eligible,
        "rx_queue_count": 8,
        "probe_restoration_verified": True,
        "management_isolated": True,
    }


def dpdk_capability(*, eligible=True, topology="dedicated_standby_adapter"):
    return {
        "observed_at_utc": OBSERVED,
        "topology": topology,
        "pmd_probe_succeeded": eligible,
        "capacity_qualified": eligible,
        "observed_min_rx_mpps": 12.2 if eligible else 2.57,
        "rx_queue_count": 4 if eligible else 1,
        "rss_supported": eligible,
        "rx_queue_coverage_qualified": eligible,
        "zero_error_probe": eligible,
        "restoration_verified": True,
        "management_isolated": True,
        "standby_preflight_passed": eligible,
        "binary_sha256": SHA256,
    }


def window(backend=NATIVE_XDP_BACKEND, *, key_total=100, key_covered=100, start=0):
    item = {
        "start_utc": f"2026-08-12T11:59:{start:02d}Z",
        "end_utc": f"2026-08-12T11:59:{start + 5:02d}Z",
        "capture_backend": backend,
        "packets_received": 10_000_000,
        "packets_dropped": 0,
        "capture_drop_rate": 0.0,
        "poll_errors": 0,
        "invalid_descriptors": 0,
        "ring_full": 0,
        "fill_empty": 0,
        "host_cpu_fraction": 0.25,
        "memory_fraction": 0.20,
        "budget_overrun_count": 0,
        "fallback_recovery_ms": 0.0,
        "kernel_to_feature_p99_us": 50.0,
        "kernel_to_feature_p999_us": 100.0,
        "active_rx_queues": 4,
        "key_flow_total": key_total,
        "key_flow_covered": key_covered,
        "key_flow_coverage": None if key_total == 0 else key_covered / key_total,
        "key_flow_coverage_basis": "remote_scored_or_local_fallback_completed",
    }
    if backend in (NATIVE_XDP_BACKEND, GENERIC_XDP_BACKEND):
        item["xdp_attach_mode"] = "native" if backend == NATIVE_XDP_BACKEND else "generic"
        item["af_xdp_bind_mode"] = "zerocopy" if backend == NATIVE_XDP_BACKEND else "copy"
    elif backend == DPDK_BACKEND:
        item["dpdk_pmd_active"] = True
    return item


def observation(
    backend=NATIVE_XDP_BACKEND,
    *,
    xdp_eligible=True,
    dpdk_eligible=True,
    topology="dedicated_standby_adapter",
):
    return {
        "schema_version": 1,
        "observed_at_utc": OBSERVED,
        "current_backend": backend,
        "capabilities": {
            "xdp": xdp_capability(eligible=xdp_eligible),
            "dpdk": dpdk_capability(eligible=dpdk_eligible, topology=topology),
        },
        "online_windows": []
        if backend == "none"
        else [window(backend, start=value) for value in (40, 45, 50)],
        "automatic_switch_authorized": True,
        "handoff": {
            "traffic_quiesced": True,
            "state_snapshot_verified": True,
            "target_preflight_passed": True,
            "rollback_ready": True,
        },
    }


class CaptureRuntimeDecisionTests(unittest.TestCase):
    def test_python_current_snapshot_matches_shared_rust_golden(self):
        golden = json.loads(
            (ROOT / "tests" / "fixtures" / "capture_runtime_current_golden_v1.json").read_text(
                encoding="utf-8"
            )
        )
        snapshot = json.loads(
            (ROOT / "configs" / "current_bcm57810_runtime_snapshot_v1.json").read_text(
                encoding="utf-8"
            )
        )
        result = evaluate_runtime_decision(
            policy(),
            snapshot,
            now=datetime.fromisoformat(golden["now_utc"].replace("Z", "+00:00")),
        )
        self.assertEqual(result["action"], golden["action"])
        self.assertEqual(result["selected_backend"], golden["selected_backend"])
        self.assertEqual(
            result["transition_permitted"], golden["transition_permitted"]
        )
        self.assertEqual(
            result["production_backend_available"],
            golden["production_backend_available"],
        )
        self.assertEqual(
            result["generic_xdp_production_eligible"],
            golden["generic_xdp_production_eligible"],
        )
        self.assertEqual(
            result["empty_key_flow_denominator_qualified"],
            golden["empty_key_flow_denominator_qualified"],
        )
        self.assertEqual(result["xdp_capability"]["eligible"], golden["xdp_eligible"])
        self.assertEqual(
            result["xdp_capability"]["native_verified"],
            golden["xdp_native_verified"],
        )
        self.assertEqual(
            result["xdp_capability"]["zerocopy_verified"],
            golden["xdp_zerocopy_verified"],
        )
        self.assertEqual(result["dpdk_capability"]["eligible"], golden["dpdk_eligible"])
        self.assertEqual(result["dpdk_capability"]["topology"], golden["dpdk_topology"])

    def test_cli_runs_from_project_root_without_pythonpath_or_install(self):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "decision.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/decide_xdp_dpdk_runtime.py",
                    "--policy",
                    "configs/xdp_dpdk_runtime_policy_v1.json",
                    "--observation",
                    "configs/current_bcm57810_runtime_snapshot_v1.json",
                    "--output",
                    str(output),
                    "--now-utc",
                    "2026-08-12T12:00:05Z",
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 10, completed.stderr)
            decision = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(decision["action"], "stop_fail_closed")
            self.assertIsNone(decision["selected_backend"])
            self.assertFalse(decision["production_backend_available"])

    def test_cli_returns_ten_for_valid_maintenance_decision(self):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        item = observation(topology="same_adapter_all_pf_rebind")
        item["online_windows"][2]["poll_errors"] = 1
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            observation_path = temporary / "observation.json"
            output = temporary / "decision.json"
            observation_path.write_text(json.dumps(item), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/decide_xdp_dpdk_runtime.py",
                    "--policy",
                    "configs/xdp_dpdk_runtime_policy_v1.json",
                    "--observation",
                    str(observation_path),
                    "--output",
                    str(output),
                    "--now-utc",
                    "2026-08-12T12:00:05Z",
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 10, completed.stderr)
            decision = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(decision["action"], "request_maintenance_dpdk_fallback")
            self.assertFalse(decision["transition_permitted"])

    def test_cli_returns_zero_only_for_keep_and_two_for_contract_error(self):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            observation_path = temporary / "observation.json"
            output = temporary / "decision.json"
            observation_path.write_text(json.dumps(observation()), encoding="utf-8")
            command = [
                sys.executable,
                "scripts/decide_xdp_dpdk_runtime.py",
                "--policy",
                "configs/xdp_dpdk_runtime_policy_v1.json",
                "--observation",
                str(observation_path),
                "--output",
                str(output),
                "--now-utc",
                "2026-08-12T12:00:05Z",
            ]
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["action"], "keep_xdp"
            )

            observation_path.write_text("{", encoding="utf-8")
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["action"],
                "stop_fail_closed",
            )

    def test_keeps_native_zerocopy_xdp_when_all_windows_pass(self):
        result = evaluate_runtime_decision(policy(), observation(), now=NOW)
        self.assertEqual(result["action"], "keep_xdp")
        self.assertEqual(result["selected_backend"], NATIVE_XDP_BACKEND)
        self.assertTrue(result["xdp_capability"]["native_verified"])
        self.assertTrue(result["xdp_capability"]["zerocopy_verified"])
        self.assertTrue(result["online_gates"]["key_flow_gate_qualified"])
        self.assertFalse(result["transition_permitted"])

    def test_generic_xdp_is_never_promoted_to_native_or_production(self):
        item = observation(
            GENERIC_XDP_BACKEND, xdp_eligible=False, dpdk_eligible=False
        )
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "stop_fail_closed")
        self.assertFalse(result["xdp_capability"]["native_verified"])
        self.assertFalse(result["xdp_capability"]["zerocopy_verified"])
        self.assertFalse(result["generic_xdp_production_eligible"])
        self.assertIn("generic_xdp_skb_is_not_native_or_zerocopy", result["reasons"])

    def test_capture_failure_can_switch_to_qualified_dedicated_dpdk(self):
        item = observation()
        item["online_windows"][2]["poll_errors"] = 1
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "switch_to_dpdk")
        self.assertEqual(result["selected_backend"], DPDK_BACKEND)
        self.assertTrue(result["transition_permitted"])

    def test_same_pf_dpdk_rebind_requires_maintenance(self):
        item = observation(topology="same_adapter_all_pf_rebind")
        item["online_windows"][2]["ring_full"] = 1
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "request_maintenance_dpdk_fallback")
        self.assertEqual(result["selected_backend"], DPDK_BACKEND)
        self.assertFalse(result["transition_permitted"])

    def test_key_flow_failure_stops_instead_of_hiding_it_with_backend_switch(self):
        item = observation()
        item["online_windows"][2]["key_flow_covered"] = 98
        item["online_windows"][2]["key_flow_coverage"] = 0.98
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "stop_fail_closed")
        self.assertFalse(result["transition_permitted"])
        self.assertIn(
            "key_flow_failure_is_not_a_capture_backend_fallback_signal",
            result["reasons"],
        )

    def test_empty_key_flow_denominator_is_not_perfect_coverage(self):
        item = observation()
        item["online_windows"][2] = window(
            NATIVE_XDP_BACKEND, key_total=0, key_covered=0, start=50
        )
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertFalse(result["online_gates"]["key_flow_gate_qualified"])
        self.assertFalse(result["empty_key_flow_denominator_qualified"])
        self.assertIn("window[2].empty_denominator", result["reasons"])

    def test_reported_coverage_must_match_integer_counters(self):
        item = observation()
        item["online_windows"][2]["key_flow_covered"] = 98
        with self.assertRaisesRegex(RuntimeDecisionContractError, "does not match counters"):
            evaluate_runtime_decision(policy(), item, now=NOW)

    def test_drop_rate_must_match_packet_counters(self):
        item = observation()
        item["online_windows"][2]["packets_dropped"] = 1
        with self.assertRaisesRegex(RuntimeDecisionContractError, "does not match counters"):
            evaluate_runtime_decision(policy(), item, now=NOW)

    def test_nonfinite_values_fail_closed(self):
        item = observation()
        item["online_windows"][2]["kernel_to_feature_p99_us"] = math.nan
        with self.assertRaisesRegex(RuntimeDecisionContractError, "finite number"):
            evaluate_runtime_decision(policy(), item, now=NOW)

    def test_stale_observation_cannot_switch(self):
        item = observation()
        result = evaluate_runtime_decision(
            policy(),
            item,
            now=datetime(2026, 8, 12, 12, 2, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(result["action"], "stop_fail_closed")
        self.assertFalse(result["transition_permitted"])
        self.assertIn("observation.observed_at_utc.stale", result["reasons"])

    def test_missing_handoff_flag_only_prepares_fallback(self):
        item = observation()
        item["online_windows"][2]["poll_errors"] = 1
        item["handoff"]["rollback_ready"] = False
        result = evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "prepare_dpdk_fallback")
        self.assertFalse(result["transition_permitted"])
        self.assertIn("handoff.rollback_ready", result["reasons"])

    def test_cpu_memory_budget_and_recovery_are_fail_closed_safety_gates(self):
        fields = {
            "host_cpu_fraction": 0.86,
            "memory_fraction": 0.86,
            "budget_overrun_count": 1,
            "fallback_recovery_ms": 300.001,
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                item = observation()
                item["online_windows"][2][field] = value
                result = evaluate_runtime_decision(policy(), item, now=NOW)
                self.assertEqual(result["action"], "stop_fail_closed")
                self.assertFalse(result["transition_permitted"])
                self.assertIn(
                    "runtime_safety_failure_is_not_a_capture_backend_fallback_signal",
                    result["reasons"],
                )
                self.assertIn(
                    f"window[2].{field}", result["online_gates"]["runtime_safety_reasons"]
                )

    def test_policy_cannot_label_generic_xdp_native(self):
        candidate = copy.deepcopy(policy())
        candidate["semantic_guards"]["generic_xdp_skb_is_native"] = True
        with self.assertRaisesRegex(RuntimeDecisionContractError, "must remain false"):
            evaluate_runtime_decision(candidate, observation(), now=NOW)

    def test_current_bcm57810_snapshot_has_no_production_backend(self):
        snapshot = json.loads(
            (ROOT / "configs" / "current_bcm57810_runtime_snapshot_v1.json").read_text(
                encoding="utf-8"
            )
        )
        result = evaluate_runtime_decision(
            policy(),
            snapshot,
            now=datetime(2026, 8, 12, 13, 5, 57, tzinfo=timezone.utc),
        )
        self.assertEqual(result["action"], "stop_fail_closed")
        self.assertIsNone(result["selected_backend"])
        self.assertFalse(result["production_backend_available"])
        self.assertFalse(result["xdp_capability"]["eligible"])
        self.assertFalse(result["dpdk_capability"]["eligible"])
        self.assertEqual(
            result["dpdk_capability"]["topology"], "same_adapter_all_pf_rebind"
        )
        self.assertIn(GENERIC_XDP_BACKEND, result["diagnostic_only_backends"])
        self.assertIn(DPDK_BACKEND, result["diagnostic_only_backends"])
        self.assertIn(
            "dpdk.latest_symmetric_q2_tcp_diagnostic_failed", result["reasons"]
        )
        self.assertIn(
            "dpdk.latest_symmetric_q2_tcp_rx_queue_coverage_failed",
            result["reasons"],
        )

    def test_latest_dpdk_diagnostic_cannot_claim_pass_with_idle_queue(self):
        item = observation()
        item["capabilities"]["dpdk"]["latest_symmetric_q2_tcp_diagnostic"] = {
            "diagnostic_passed": True,
            "rx_queue_packets": [10_000, 0],
        }
        with self.assertRaisesRegex(
            RuntimeDecisionContractError, "cannot pass with an idle required RX queue"
        ):
            evaluate_runtime_decision(policy(), item, now=NOW)
        self.assertIn(
            "dpdk.latest_symmetric_q2_tcp_diagnostic_failed", result["reasons"]
        )
        self.assertIn(
            "dpdk.latest_symmetric_q2_tcp_rx_queue_coverage_failed",
            result["reasons"],
        )

    def test_latest_dpdk_diagnostic_cannot_claim_pass_with_idle_queue(self):
        item = observation()
        item["capabilities"]["dpdk"]["latest_symmetric_q2_tcp_diagnostic"] = {
            "diagnostic_passed": True,
            "rx_queue_packets": [10_000, 0],
        }
        with self.assertRaisesRegex(
            RuntimeDecisionContractError, "cannot pass with an idle required RX queue"
        ):
            evaluate_runtime_decision(policy(), item, now=NOW)


if __name__ == "__main__":
    unittest.main()

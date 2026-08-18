from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from hft_mgbs.capture_runtime_failover import (
    CURRENT_HARDWARE_BACKEND,
    DPDK_BACKEND,
    NATIVE_XDP_BACKEND,
    RuntimeFailoverContractError,
    evaluate_failover_decision,
)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 15, 0, 0, 5, tzinfo=timezone.utc)
OBSERVED = "2026-08-15T00:00:00Z"
SHA = "a" * 64


def policy():
    return json.loads(
        (ROOT / "configs" / "capture_runtime_failover_policy_v2.json").read_text(encoding="utf-8")
    )


def capability(backend, eligible=True):
    topology = {
        NATIVE_XDP_BACKEND: "new_nic_with_dedicated_bcm57810_fallback",
        DPDK_BACKEND: "dedicated_dpdk_standby_adapter",
        CURRENT_HARDWARE_BACKEND: "dedicated_legacy_bcm57810_pair",
    }[backend]
    return {
        "backend": backend,
        "observed_at_utc": OBSERVED,
        "ready": eligible,
        "health_verified": eligible,
        "topology": topology,
        "observed_min_mpps": 12.2 if backend != CURRENT_HARDWARE_BACKEND else 2.61,
        "active_rx_queues": 8,
        "zero_drop_qualified": eligible,
        "restoration_verified": True,
        "management_isolated": True,
        "binary_sha256": SHA,
        "service_continuity_qualified": eligible,
        "production_sla_qualified": eligible and backend != CURRENT_HARDWARE_BACKEND,
    }


def observation(current=NATIVE_XDP_BACKEND, *, xdp=True, dpdk=True, current_hw=True):
    none = current == "none"
    return {
        "schema_version": 2,
        "scope": "hft_mgbs_capture_runtime_failover_observation_v2",
        "observed_at_utc": OBSERVED,
        "current_backend": current,
        "capabilities": {
            NATIVE_XDP_BACKEND: capability(NATIVE_XDP_BACKEND, xdp),
            DPDK_BACKEND: capability(DPDK_BACKEND, dpdk),
            CURRENT_HARDWARE_BACKEND: capability(CURRENT_HARDWARE_BACKEND, current_hw),
        },
        "current_status": {
            "consecutive_healthy_windows": 0 if none else 3,
            "consecutive_failed_windows": 0,
            "capture_gate_qualified": not none,
            "key_flow_gate_qualified": not none,
            "runtime_safety_gate_qualified": not none,
        },
        "automatic_switch_authorized": True,
        "handoff": {
            "traffic_quiesced": True,
            "state_snapshot_verified": True,
            "target_preflight_passed": True,
            "rollback_ready": True,
        },
    }


class CaptureRuntimeFailoverTests(unittest.TestCase):
    def test_xdp_failure_prefers_dpdk_then_current_hardware(self):
        item = observation()
        item["current_status"].update(
            consecutive_healthy_windows=0,
            consecutive_failed_windows=2,
            capture_gate_qualified=False,
        )
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "switch_to_dpdk")
        self.assertEqual(result["selected_backend"], DPDK_BACKEND)
        self.assertFalse(result["degraded_mode"])

        item["capabilities"][DPDK_BACKEND] = capability(DPDK_BACKEND, False)
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "switch_to_" + CURRENT_HARDWARE_BACKEND)
        self.assertEqual(result["selected_backend"], CURRENT_HARDWARE_BACKEND)
        self.assertTrue(result["degraded_mode"])
        self.assertFalse(result["production_sla_qualified"])

    def test_current_hardware_is_kept_as_degraded_continuity_only(self):
        item = observation(CURRENT_HARDWARE_BACKEND, xdp=False, dpdk=False)
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "keep_" + CURRENT_HARDWARE_BACKEND)
        self.assertTrue(result["service_continuity_backend_available"])
        self.assertTrue(result["current_hardware_fallback_eligible"])
        self.assertTrue(result["degraded_mode"])
        self.assertFalse(result["production_sla_qualified"])
        self.assertFalse(result["release_qualification"])

    def test_current_hardware_can_recover_to_xdp_with_handoff(self):
        item = observation(CURRENT_HARDWARE_BACKEND, xdp=True, dpdk=True)
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "switch_to_" + NATIVE_XDP_BACKEND)
        self.assertEqual(result["selected_backend"], NATIVE_XDP_BACKEND)
        self.assertTrue(result["transition_permitted"])

        item["automatic_switch_authorized"] = False
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "prepare_" + NATIVE_XDP_BACKEND)
        self.assertFalse(result["transition_permitted"])

    def test_quality_or_runtime_safety_failure_never_triggers_capture_fallback(self):
        for field in ("key_flow_gate_qualified", "runtime_safety_gate_qualified"):
            item = observation()
            item["current_status"][field] = False
            result = evaluate_failover_decision(policy(), item, now=NOW)
            self.assertEqual(result["action"], "stop_fail_closed")
            self.assertIsNone(result["selected_backend"])
            self.assertFalse(result["transition_permitted"])

    def test_unqualified_current_hardware_cannot_be_selected(self):
        item = observation("none", xdp=False, dpdk=False, current_hw=False)
        result = evaluate_failover_decision(policy(), item, now=NOW)
        self.assertEqual(result["action"], "stop_fail_closed")
        self.assertFalse(result["service_continuity_backend_available"])

    def test_policy_cannot_promote_current_hardware_to_production(self):
        value = policy()
        value["backend_requirements"][CURRENT_HARDWARE_BACKEND]["production_eligible"] = True
        with self.assertRaisesRegex(RuntimeFailoverContractError, "degraded fallback"):
            evaluate_failover_decision(value, observation(), now=NOW)

    def test_cli_runs_without_pythonpath_and_current_snapshot_stays_fail_closed(self):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "decision.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/decide_capture_runtime_failover.py",
                    "--policy", "configs/capture_runtime_failover_policy_v2.json",
                    "--observation", "configs/current_bcm57810_failover_observation_v2.json",
                    "--output", str(output),
                    "--now-utc", "2026-08-15T00:00:05Z",
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 10, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["action"], "stop_fail_closed")
            self.assertFalse(result["current_hardware_fallback_eligible"])


if __name__ == "__main__":
    unittest.main()

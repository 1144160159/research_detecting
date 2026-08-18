from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.capture_runtime_executor import RuntimeExecutionError
from hft_mgbs.capture_runtime_failover import (
    CURRENT_HARDWARE_BACKEND,
    NATIVE_XDP_BACKEND,
    build_failover_decision_receipt,
)
from hft_mgbs.capture_runtime_failover_executor import execute_failover_transition


ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def fixtures():
    path = ROOT / "tests" / "test_capture_runtime_failover.py"
    spec = importlib.util.spec_from_file_location("failover_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = r'''
import argparse,json,pathlib
p=argparse.ArgumentParser(); p.add_argument('--mode',required=True); p.add_argument('--output'); p.add_argument('--state',required=True); p.add_argument('--fail-stop',action='store_true')
a=p.parse_args(); state=pathlib.Path(a.state); current=state.read_text().strip()
targets=('native_af_xdp_zerocopy','dpdk','current_tpacket_v3_bcm57810')
if a.mode=='snapshot': value={'active_backend':current,'state_domains':{'capture_backend':current}}
elif a.mode.startswith('health-'):
 target=a.mode[len('health-'):]; value={'backend':target,'healthy':target in targets}
elif a.mode.startswith('start-'):
 target=a.mode[len('start-'):]; state.write_text('both:'+current+':'+target); raise SystemExit(0)
elif a.mode.startswith('stop-'):
 if a.fail_stop: raise SystemExit(9)
 source=a.mode[len('stop-'):]; parts=current.split(':'); state.write_text(parts[-1] if parts[0]=='both' and parts[1]==source else current); raise SystemExit(0)
elif a.mode=='rollback': state.write_text('native_af_xdp_zerocopy'); raise SystemExit(0)
else: raise SystemExit(2)
pathlib.Path(a.output).write_text(json.dumps(value,sort_keys=True)+'\n',encoding='utf-8')
'''


class CaptureRuntimeFailoverExecutorTests(unittest.TestCase):
    def _fixture(self, base: Path, fail_stop=False):
        module = fixtures()
        policy = module.policy()
        observation = module.observation()
        observation["capabilities"]["dpdk"] = module.capability("dpdk", False)
        observation["current_status"].update(
            consecutive_healthy_windows=0,
            consecutive_failed_windows=2,
            capture_gate_qualified=False,
        )
        policy_path = base / "policy.json"; write(policy_path, policy)
        observation_path = base / "observation.json"; write(observation_path, observation)
        receipt = build_failover_decision_receipt(
            policy,
            observation,
            policy_sha256=sha(policy_path),
            observation_sha256=sha(observation_path),
            decision_at_utc=module.NOW.isoformat().replace("+00:00", "Z"),
        )
        receipt_path = base / "decision.json"; write(receipt_path, receipt)
        adapter = base / "adapter.py"; adapter.write_text(ADAPTER, encoding="utf-8")
        state = base / "state.txt"; state.write_text(NATIVE_XDP_BACKEND, encoding="utf-8")
        python = Path(sys.executable).resolve()
        common = {
            "executable_sha256": sha(python),
            "bound_files": [{"path": str(adapter), "sha256": sha(adapter)}],
            "timeout_seconds": 10,
        }

        def operation(mode, evidence, extra=None):
            argv = [str(python), "-I", "-S", str(adapter), "--mode", mode, "--state", str(state)]
            if evidence:
                argv += ["--output", "{output}"]
            if extra:
                argv += extra
            return dict(common, argv=argv)

        operations = {"snapshot": operation("snapshot", True), "rollback": operation("rollback", False)}
        for backend in (NATIVE_XDP_BACKEND, "dpdk", CURRENT_HARDWARE_BACKEND):
            operations["health_" + backend] = operation("health-" + backend, True)
            operations["start_" + backend] = operation("start-" + backend, False)
            extra = ["--fail-stop"] if fail_stop and backend == NATIVE_XDP_BACKEND else None
            operations["stop_" + backend] = operation("stop-" + backend, False, extra)
        plan = {
            "schema_version": 2,
            "scope": "hft_mgbs_capture_runtime_failover_execution_plan_v2",
            "policy_id": policy["policy_id"],
            "topology": "new_nic_with_dedicated_bcm57810_fallback",
            "operations": operations,
        }
        plan_path = base / "plan.json"; write(plan_path, plan)
        return policy_path, observation_path, receipt_path, plan_path, state

    def test_switches_from_xdp_to_current_hardware_and_seals_degraded_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, receipt, plan, state = self._fixture(base)
            result = execute_failover_transition(
                policy_path=policy,
                observation_path=observation,
                decision_receipt_path=receipt,
                execution_plan_path=plan,
                trusted_plan_sha256=sha(plan),
                authorization="I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2",
                work_dir=base / "work",
                output_path=base / "execution.json",
            )
            self.assertEqual(result["outcome"], "switched_to_" + CURRENT_HARDWARE_BACKEND)
            self.assertEqual(state.read_text(encoding="utf-8"), CURRENT_HARDWARE_BACKEND)
            self.assertTrue(result["degraded_mode"])
            self.assertFalse(result["production_sla_qualified"])
            self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_failure_after_start_rolls_back_to_original_backend(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, receipt, plan, state = self._fixture(base, fail_stop=True)
            with self.assertRaises(RuntimeExecutionError):
                execute_failover_transition(
                    policy_path=policy,
                    observation_path=observation,
                    decision_receipt_path=receipt,
                    execution_plan_path=plan,
                    trusted_plan_sha256=sha(plan),
                    authorization="I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2",
                    work_dir=base / "work",
                    output_path=base / "execution.json",
                )
            result = json.loads((base / "execution.json").read_text(encoding="utf-8"))
            self.assertTrue(result["rollback_attempted"])
            self.assertTrue(result["rollback_succeeded"])
            self.assertEqual(state.read_text(encoding="utf-8"), NATIVE_XDP_BACKEND)

    def test_recovery_switches_from_current_hardware_back_to_xdp(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy_path, observation_path, receipt_path, plan, state = self._fixture(base)
            module = fixtures()
            policy_value = module.policy()
            observation_value = module.observation(CURRENT_HARDWARE_BACKEND)
            write(observation_path, observation_value)
            receipt_value = build_failover_decision_receipt(
                policy_value,
                observation_value,
                policy_sha256=sha(policy_path),
                observation_sha256=sha(observation_path),
                decision_at_utc=module.NOW.isoformat().replace("+00:00", "Z"),
            )
            write(receipt_path, receipt_value)
            state.write_text(CURRENT_HARDWARE_BACKEND, encoding="utf-8")
            result = execute_failover_transition(
                policy_path=policy_path,
                observation_path=observation_path,
                decision_receipt_path=receipt_path,
                execution_plan_path=plan,
                trusted_plan_sha256=sha(plan),
                authorization="I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2",
                work_dir=base / "work",
                output_path=base / "execution.json",
            )
            self.assertEqual(result["outcome"], "switched_to_" + NATIVE_XDP_BACKEND)
            self.assertEqual(state.read_text(encoding="utf-8"), NATIVE_XDP_BACKEND)
            self.assertFalse(result["degraded_mode"])

    def test_missing_authorization_rejects_before_work_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, receipt, plan, _ = self._fixture(base)
            with self.assertRaisesRegex(RuntimeExecutionError, "authorization"):
                execute_failover_transition(
                    policy_path=policy,
                    observation_path=observation,
                    decision_receipt_path=receipt,
                    execution_plan_path=plan,
                    trusted_plan_sha256=sha(plan),
                    authorization="NO",
                    work_dir=base / "work",
                    output_path=base / "execution.json",
                )
            self.assertFalse((base / "work").exists())


if __name__ == "__main__":
    unittest.main()

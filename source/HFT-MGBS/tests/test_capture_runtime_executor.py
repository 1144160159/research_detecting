from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.capture_runtime_decision import build_runtime_decision_receipt
from hft_mgbs.capture_runtime_executor import RuntimeExecutionError, execute_runtime_decision


ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def load_decision_fixtures():
    path = ROOT / "tests" / "test_capture_runtime_decision.py"
    spec = importlib.util.spec_from_file_location("runtime_decision_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = r'''
import argparse,json,pathlib
p=argparse.ArgumentParser(); p.add_argument('--mode',required=True); p.add_argument('--output'); p.add_argument('--state',required=True)
a=p.parse_args(); state=pathlib.Path(a.state)
current=state.read_text().strip() if state.exists() else 'native_af_xdp_zerocopy'
if a.mode=='snapshot': value={'active_backend':current,'state_domains':{'capture_backend':current}}
elif a.mode=='health-dpdk': value={'backend':'dpdk','healthy':current!='broken'}
elif a.mode=='health-xdp': value={'backend':'native_af_xdp_zerocopy','healthy':current=='native_af_xdp_zerocopy'}
elif a.mode=='start-dpdk': state.write_text('both'); raise SystemExit(0)
elif a.mode=='stop-xdp': state.write_text('dpdk'); raise SystemExit(0)
elif a.mode=='rollback': state.write_text('native_af_xdp_zerocopy'); raise SystemExit(0)
else: raise SystemExit(2)
pathlib.Path(a.output).write_text(json.dumps(value,sort_keys=True)+'\n',encoding='utf-8')
'''


class CaptureRuntimeExecutorTests(unittest.TestCase):
    def _fixture(self, base: Path, *, switch: bool = True):
        fixture = load_decision_fixtures()
        policy = fixture.policy()
        observation = fixture.observation()
        if switch:
            observation["online_windows"][2]["poll_errors"] = 1
        policy_path, observation_path = base / "policy.json", base / "observation.json"
        write_json(policy_path, policy)
        write_json(observation_path, observation)
        decision = build_runtime_decision_receipt(
            policy,
            observation,
            policy_sha256=sha(policy_path),
            observation_sha256=sha(observation_path),
            raw_runtime_evidence_sha256=sha(observation_path),
            observation_artifact={"path": str(observation_path), "sha256": sha(observation_path)},
            raw_runtime_evidence={"path": str(observation_path), "sha256": sha(observation_path)},
            decision_at_utc=fixture.NOW.isoformat().replace("+00:00", "Z"),
        )
        decision_path = base / "decision.json"
        write_json(decision_path, decision)
        adapter = base / "adapter.py"
        adapter.write_text(ADAPTER, encoding="utf-8")
        state = base / "state.txt"
        state.write_text("native_af_xdp_zerocopy", encoding="utf-8")
        python = Path(sys.executable).resolve()
        common = {
            "executable_sha256": sha(python),
            "bound_files": [{"path": str(adapter), "sha256": sha(adapter)}],
            "timeout_seconds": 10,
        }
        def operation(mode: str, output: bool):
            argv = [str(python), "-I", "-S", str(adapter), "--mode", mode, "--state", str(state)]
            if output:
                argv += ["--output", "{output}"]
            return {**common, "argv": argv}
        plan = {
            "schema_version": 1,
            "scope": "hft_mgbs_capture_runtime_execution_plan_v1",
            "policy_id": policy["policy_id"],
            "topology": "dedicated_standby_adapter",
            "operations": {
                "snapshot": operation("snapshot", True),
                "health_xdp": operation("health-xdp", True),
                "health_dpdk": operation("health-dpdk", True),
                "start_dpdk": operation("start-dpdk", False),
                "stop_xdp": operation("stop-xdp", False),
                "rollback": operation("rollback", False),
            },
        }
        plan_path = base / "plan.json"
        write_json(plan_path, plan)
        return policy_path, observation_path, decision_path, plan_path, state

    def test_replayed_switch_executes_and_seals_state_transition(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, decision, plan, state = self._fixture(base)
            output = base / "receipt.json"
            result = execute_runtime_decision(
                policy_path=policy,
                observation_path=observation,
                decision_receipt_path=decision,
                execution_plan_path=plan,
                trusted_plan_sha256=sha(plan),
                authorization="I_AUTHORIZE_XDP_DPDK_RUNTIME_EXECUTION",
                work_dir=base / "work",
                output_path=output,
            )
            self.assertEqual(result["outcome"], "switched_to_dpdk")
            self.assertTrue(result["mutations_performed"])
            self.assertEqual(result["after_snapshot"]["active_backend"], "dpdk")
            self.assertEqual(state.read_text(encoding="utf-8"), "dpdk")
            self.assertFalse(result["release_qualification"])

    def test_missing_authorization_rejects_before_work_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, decision, plan, _ = self._fixture(base)
            with self.assertRaisesRegex(RuntimeExecutionError, "authorization"):
                execute_runtime_decision(
                    policy_path=policy,
                    observation_path=observation,
                    decision_receipt_path=decision,
                    execution_plan_path=plan,
                    trusted_plan_sha256=sha(plan),
                    authorization="NO",
                    work_dir=base / "work",
                    output_path=base / "receipt.json",
                )
            self.assertFalse((base / "work").exists())

    def test_keep_decision_creates_non_mutating_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            policy, observation, decision, plan, state = self._fixture(base, switch=False)
            result = execute_runtime_decision(
                policy_path=policy,
                observation_path=observation,
                decision_receipt_path=decision,
                execution_plan_path=plan,
                trusted_plan_sha256=sha(plan),
                authorization="I_AUTHORIZE_XDP_DPDK_RUNTIME_EXECUTION",
                work_dir=base / "work",
                output_path=base / "receipt.json",
            )
            self.assertEqual(result["outcome"], "decision_requires_no_automatic_mutation")
            self.assertFalse(result["mutations_performed"])
            self.assertEqual(state.read_text(encoding="utf-8"), "native_af_xdp_zerocopy")


if __name__ == "__main__":
    unittest.main()

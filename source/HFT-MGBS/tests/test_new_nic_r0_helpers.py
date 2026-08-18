from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.new_nic_r0 import evaluate_r0_campaign


ROOT = Path(__file__).resolve().parents[1]
HELPER_ROOT = ROOT / "scripts" / "new_nic_helpers"
ROLES = (
    "xdp_runner",
    "dpdk_runner",
    "generator_runner",
    "resource_sampler",
    "fallback_orchestrator",
    "restore_helper",
    "campaign_executor",
    "trust_root_recorder",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


ADAPTER = r'''
import argparse, datetime, json, pathlib
p=argparse.ArgumentParser(); p.add_argument('--mode', required=True); p.add_argument('--output')
p.add_argument('--repeat', type=int, default=1); p.add_argument('--phase'); a=p.parse_args()
if a.mode == 'restore':
    raise SystemExit(0)
out=pathlib.Path(a.output)
if a.mode == 'snapshot':
    names=('management_plane','xdp_attachment','pci_driver_and_override','mtu_txqlen',
      'offloads_channels_rings_coalesce','rss_reta','irq_affinity','all_numa_hugepages',
      'dpdk_runtime_prefixes')
    value={'state_domains': {name: {'frozen': name} for name in names}}
elif a.mode in ('xdp','dpdk'):
    base=datetime.datetime(2026,8,14,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=a.repeat*100)
    iso=lambda x:(base+datetime.timedelta(seconds=x)).isoformat().replace('+00:00','Z')
    sent=180000000; queues=[22500000]*8
    proof=({'attach_mode':'native','xsk_bind_mode':'forced_zerocopy','zero_copy_confirmed':True,
      'copy_fallback_detected':False,'xdp_attach_flags':4,'xsk_bind_flags':4,
      'xdp_program_ids':[1001],'xsk_socket_count':8,'xsk_zerocopy_rx_packets':sent,
      'xsk_copy_rx_packets':0} if a.mode=='xdp' else
      {'rss_enabled':True,'tss_enabled':True,'reta_programmed':True,'rx_queues_configured':8,
       'tx_queues_configured':8,'rss_reta':list(range(8))*16,
       'rss_hash_types':['ipv4','ipv4-tcp','ipv4-udp'],'per_queue_rx_packets':queues,
       'per_queue_tx_packets':[1000000]*8})
    value={'started_at_utc':iso(0),'completed_at_utc':iso(15),
      'generator':{'started_at_utc':iso(0),'completed_at_utc':iso(15),
        'requested_packets':sent,'sent_packets':sent,'tx_errors':0},
      'capture':{'unique_packets':sent,'sequence_gaps':0,'nic_rx_missed':0,'nic_rx_errors':0,
        'socket_drops':0,'descriptor_errors':0,'duplicate_packets':0,'out_of_order_packets':0,
        'queue_packets':queues},
      'latency_histogram':[{'le_us':50.0,'cumulative_count':sent}],
      'latency_proof':{'measurement_method':'hardware_timestamp_ptp_correlated',
        'clock_sync_error_us':1.0,'timestamped_packets':sent,'negative_latency_samples':0},
      'resource':{'samples':[{'timestamp_utc':iso(i),'host_cpu_fraction':0.5,
        'host_memory_fraction':0.4,'process_rss_bytes':1073741824,
        'hugepage_reserved_bytes':2147483648} for i in range(15)]},
      'key_flow':{'basis':'independent_generator_marker_manifest','marker_manifest_sha256':'a'*64,
        'total':100,'covered':100,'skipped_due_budget':0},'backend_proof':proof}
else:
    value={'generator_transition':{'window_started_monotonic_ns':900000000,
      'window_completed_monotonic_ns':1300000000,'requested_packets':1000000,
      'sent_packets':1000000,'tx_errors':0,'packets_before_fault':250000,
      'packets_fault_to_recovery':500000,'packets_after_recovery':250000,
      'max_inter_packet_gap_us':10.0},'fault_injected_monotonic_ns':1000000000,
      'first_dpdk_packet_monotonic_ns':1200000000,
      'transition':{'expected_packets':1000000,'received_unique_packets':1000000,
      'sequence_gaps':0,'duplicate_packets':0,'out_of_order_packets':0}}
out.write_text(json.dumps(value,sort_keys=True)+'\n',encoding='utf-8')
'''


class NewNicR0HelperTests(unittest.TestCase):
    def setUp(self):
        hashes = {sha(HELPER_ROOT / role) for role in ROLES}
        self.assertEqual(len(hashes), 1, "the eight frozen role files must be byte-identical")

    def _fixture(self, base: Path):
        run_dir = base / "campaign"
        frozen = run_dir / "frozen"
        frozen.mkdir(parents=True)
        helpers = {}
        for role in ROLES:
            target = frozen / role
            shutil.copy2(HELPER_ROOT / role, target)
            helpers[role] = target
        manifest = run_dir / "frozen_helper_manifest.txt"
        manifest.write_text(
            "\n".join("{} {} {}".format(role, helpers[role], sha(helpers[role])) for role in ROLES) + "\n",
            encoding="utf-8",
        )
        adapter = base / "adapter.py"
        adapter.write_text(ADAPTER, encoding="utf-8")
        executable = Path(sys.executable).resolve()
        common = {
            "executable_sha256": sha(executable),
            "bound_files": [{"path": str(adapter.resolve()), "sha256": sha(adapter)}],
            "timeout_seconds": 20,
        }
        operations = {
            "snapshot": {**common, "argv": [str(executable), "-I", "-S", str(adapter), "--mode", "snapshot", "--phase", "{phase}", "--output", "{raw_output}"]},
            "restore": {**common, "argv": [str(executable), "-I", "-S", str(adapter), "--mode", "restore"]},
            "xdp_run": {**common, "argv": [str(executable), "-I", "-S", str(adapter), "--mode", "xdp", "--repeat", "{repeat_index}", "--output", "{raw_output}"]},
            "dpdk_run": {**common, "argv": [str(executable), "-I", "-S", str(adapter), "--mode", "dpdk", "--repeat", "{repeat_index}", "--output", "{raw_output}"]},
            "fallback": {**common, "argv": [str(executable), "-I", "-S", str(adapter), "--mode", "fallback", "--repeat", "{repeat_index}", "--output", "{raw_output}"]},
        }
        plan = {
            "schema_version": 1,
            "scope": "hft_mgbs_new_nic_r0_execution_plan_v1",
            "campaign_id": "r0-helper-integration",
            "capture_host_id": "capture-host",
            "candidate_pci_addresses": ["0000:41:00.0"],
            "generator_identity": {"generator_host_id": "generator-host", "generator_nic_serial": "GENERATOR-SERIAL", "physical_link_id": "direct-link-a", "marker_manifest_sha256": "a" * 64},
            "topology": {"fallback_design": "prearmed_secondary_pf", "same_pf_runtime_driver_rebind": False, "independent_generator": True, "same_adapter_loopback": False},
            "operations": operations,
        }
        plan_path = run_dir / "execution-plan.json"
        write_json(plan_path, plan)
        (run_dir / "execution_plan.sha256").write_text(sha(plan_path) + "\n", encoding="ascii")
        return run_dir, helpers, plan_path

    def _call(self, helper: Path, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", "-S", str(helper), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_full_helper_campaign_produces_recomputable_r0_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            run_dir, helpers, plan = self._fixture(base)
            contract = ROOT / "configs" / "new_nic_r0_campaign_contract_v1.json"
            for phase in ("snapshot-before", "snapshot-after"):
                result = self._call(
                    helpers["restore_helper"], "--mode", phase, "--execution-plan", str(plan),
                    "--change-ticket", "HFT-R0-TEST", "--run-dir", str(run_dir),
                    "--output", str(run_dir / ("restoration_" + ("before" if phase.endswith("before") else "after") + ".json")),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            command = [
                "--contract", str(contract), "--execution-plan", str(plan),
                "--xdp-runner", str(helpers["xdp_runner"]), "--dpdk-runner", str(helpers["dpdk_runner"]),
                "--generator-runner", str(helpers["generator_runner"]), "--resource-sampler", str(helpers["resource_sampler"]),
                "--fallback-orchestrator", str(helpers["fallback_orchestrator"]),
                "--arrival-evidence-manifest-sha256", "7" * 64, "--change-ticket", "HFT-R0-TEST",
                "--run-dir", str(run_dir), "--packet-size", "64", "--offered-mpps", "12",
                "--duration-seconds", "15", "--xdp-repeats", "3", "--dpdk-repeats", "3", "--fallback-trials", "3",
            ]
            result = self._call(helpers["campaign_executor"], *command)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = lambda path: json.loads(path.read_text(encoding="utf-8"))
            bundle = {
                "contract": payload(contract),
                "campaign": payload(run_dir / "campaign.json"),
                "arrival_inventory": {"schema_version": 1, "scope": "new_high_speed_nic_inventory", "candidate_ports": [{"pci_address": "0000:41:00.0", "interface": "ens10f0", "adapter_serial": "CAPTURE-SERIAL"}]},
                "arrival_preflight": {"schema_version": 1, "scope": "new_high_speed_nic_preflight_result", "status": "self_consistent_capability_receipts_only", "hardware_present": True, "self_consistent_capability_receipts_valid": True, "production_qualified": False, "inventory_sha256": "0" * 64},
                "xdp_runs": [payload(run_dir / "xdp_run_{}.json".format(i)) for i in (1, 2, 3)],
                "dpdk_runs": [payload(run_dir / "dpdk_run_{}.json".format(i)) for i in (1, 2, 3)],
                "fallback_trials": [payload(run_dir / "fallback_trial_{}.json".format(i)) for i in (1, 2, 3)],
                "restoration_before": payload(run_dir / "restoration_before.json"),
                "restoration_after": payload(run_dir / "restoration_after.json"),
                "producer_hashes": {**{role: sha(path) for role, path in helpers.items()}, "arrival_evidence_manifest": "7" * 64},
            }
            from hft_mgbs.new_nic_r0 import canonical_sha256
            bundle["arrival_preflight"]["inventory_sha256"] = canonical_sha256(bundle["arrival_inventory"])
            audit = evaluate_r0_campaign(**bundle, trusted_manifest_verified=True, trusted_manifest_sha256="f" * 64)
            self.assertEqual(audit["status"], "r0_qualified", audit.get("errors"))

    def test_plan_or_adapter_drift_is_rejected_before_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            run_dir, helpers, plan = self._fixture(base)
            plan.write_text(plan.read_text(encoding="utf-8") + " ", encoding="utf-8")
            result = self._call(
                helpers["restore_helper"], "--mode", "snapshot-before", "--execution-plan", str(plan),
                "--change-ticket", "HFT-R0-TEST", "--run-dir", str(run_dir), "--output", str(run_dir / "out.json"),
            )
            self.assertEqual(result.returncode, 74)
            self.assertFalse((run_dir / "out.json").exists())


if __name__ == "__main__":
    unittest.main()

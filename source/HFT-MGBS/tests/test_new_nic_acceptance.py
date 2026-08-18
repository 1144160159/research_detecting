from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.new_nic_acceptance import (
    compare_restoration,
    evaluate_inventory,
    receipt_content_sha256,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "configs" / "new_nic_acceptance_contract_v1.json"
SCHEMA_PATH = ROOT / "configs" / "schemas" / "new_nic_inventory_v1.schema.json"
RESULT_SCHEMA_PATH = (
    ROOT / "configs" / "schemas" / "new_nic_preflight_result_v1.schema.json"
)
CLI = ROOT / "scripts" / "preflight_new_nic.py"
RUNNER = ROOT / "scripts" / "run_new_nic_acceptance.sh"
SHA = "a" * 64


def contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def valid_inventory():
    ports = []
    stack_ports = []
    pci_addresses = ["0000:41:00.0"]
    for index, pci in enumerate(pci_addresses):
        interface = "ens10f{}".format(index)
        serial = "NEW-NIC-SERIAL-{}".format(index)
        ports.append(
            {
                "interface": interface,
                "pci_address": pci,
                "vendor_id": "8086",
                "device_id": "159b",
                "adapter_serial": serial,
                "physical": True,
                "kernel_driver": "ice",
                "driver_version": "1.15.7",
                "firmware_version": "4.80",
                "numa_node": 1,
                "carrier": 1,
                "operstate": "up",
                "link_speed_mbps": 25000,
                "pcie_current_width": 8,
                "pcie_current_speed_gtps": 16.0,
                "pcie_max_width": 8,
                "pcie_max_speed_gtps": 16.0,
                "master": None,
                "ip_addresses": [],
                "default_route": False,
                "queue_capabilities": {
                    "max_rx": 64,
                    "max_tx": 64,
                    "max_combined": 64,
                },
                "read_only_xdp_feature_query": "xdp supported",
                "restoration_state": {
                    "xdp_attachment": None,
                    "driver_override": None,
                    "kernel_driver": "ice",
                    "mtu": 1500,
                    "tx_queue_len": 1000,
                    "features": "features-frozen",
                    "channels": "channels-frozen",
                    "rings": "rings-frozen",
                    "coalesce": "coalesce-frozen",
                    "rss_indirection": "rss-reta-frozen",
                    "irq_affinity": {"100": "48"},
                },
            }
        )
        stack_ports.append(
            {
                "pci_address": pci,
                "kernel_driver": "ice",
                "driver_version": "1.15.7",
                "firmware_version": "4.80",
                "ddp_package": "ice_comms",
                "ddp_version": "1.3.41.0",
                "ddp_profile": "default",
                "ddp_sha256": SHA,
                "compatible": True,
                "native_xdp_driver_supported": True,
                "af_xdp_zerocopy_driver_supported": True,
                "dpdk_rss_supported": True,
                "dpdk_tss_supported": True,
                "dpdk_pmd": "ice",
                "capability_source": "upstream-version-bound-capability-matrix",
                "capability_evidence_sha256": SHA,
            }
        )
    return {
        "schema_version": 1,
        "scope": "new_high_speed_nic_inventory",
        "captured_at_utc": "2026-08-13T00:00:00Z",
        "capture_host_id": "capture-host-10-0-5-8",
        "collection_mode": "read_only",
        "candidate_ports": ports,
        "management_plane": {
            "interfaces_present": ["br0", "ens9f0", "ens10f0"],
            "default_route_interfaces": ["br0"],
            "lower_to_master": {"ens9f0": "br0"},
        },
        "worker_cpu_plan": {
            "cpus": [48, 49, 50, 51, 52, 53, 54, 55],
            "numa_nodes": [1, 1, 1, 1, 1, 1, 1, 1],
        },
        "stack_attestation": {
            "kernel_release": "6.8.0",
            "dpdk_version": "25.11",
            "compatibility_verified": True,
            "compatibility_source": "vendor-and-upstream-matrix",
            "compatibility_matrix_sha256": SHA,
            "ports": stack_ports,
        },
        "independent_generator": {
            "generator_host_id": "generator-host-01",
            "generator_nic_serial": "GENERATOR-NIC-01",
            "same_adapter_loopback": False,
            "identity_verified": True,
            "identity_receipt_sha256": SHA,
            "max_sustained_64b_mpps": 20.0,
            "link_speed_mbps": 25000,
            "physical_link_id": "capture-host-ens10f0--generator-host-port0",
        },
        "xdp_probe_receipt": None,
        "dpdk_probe_receipt": None,
        "host_restoration_state": {
            "numa_hugepages": {"node1/hugepages-2048kB": "0"},
            "dpdk_runtime_prefixes": [],
        },
        "mutations_performed": False,
    }


def receipt_common(inventory, run_id):
    return {
        "capture_host_id": inventory["capture_host_id"],
        "pci_addresses": [
            item["pci_address"] for item in inventory["candidate_ports"]
        ],
        "run_id": run_id,
        "probe_binary_sha256": SHA,
        "started_at_utc": "2026-08-13T00:01:00Z",
        "completed_at_utc": "2026-08-13T00:02:00Z",
        "success": True,
        "state_restored": True,
        "persistent_mutations": False,
    }


def attach_valid_receipts(inventory):
    xdp = receipt_common(inventory, "xdp-live-001")
    xdp.update(
        {
            "native_feature_supported": True,
            "attach_mode": "native",
            "xsk_bind_mode": "forced_zerocopy",
            "zero_copy_confirmed": True,
            "copy_fallback_detected": False,
            "tested_queue_count": 8,
            "queue_results": [
                {
                    "queue_id": queue_id,
                    "xsk_bind_mode": "forced_zerocopy",
                    "zero_copy_confirmed": True,
                    "packets": 1000,
                }
                for queue_id in range(8)
            ],
        }
    )
    dpdk = receipt_common(inventory, "dpdk-live-001")
    dpdk.update(
        {
            "pmd": "ice",
            "rss_enabled": True,
            "tss_enabled": True,
            "reta_programmed": True,
            "rx_queues_configured": 8,
            "tx_queues_configured": 8,
            "rx_queues_with_packets": 8,
            "tx_queues_with_packets": 8,
            "rx_queue_packets": [1000] * 8,
            "tx_queue_packets": [1000] * 8,
        }
    )
    xdp["receipt_sha256"] = receipt_content_sha256(xdp)
    dpdk["receipt_sha256"] = receipt_content_sha256(dpdk)
    inventory["xdp_probe_receipt"] = xdp
    inventory["dpdk_probe_receipt"] = dpdk


class NewNicAcceptanceTest(unittest.TestCase):
    def test_frozen_contract_and_schema_are_strict_json(self):
        value = contract()
        self.assertEqual(validate_contract(value), [])
        self.assertTrue(value["frozen"])
        self.assertEqual(value["status"], "hardware_pending")
        self.assertFalse(value["production_qualified"])
        self.assertFalse(value["final_pareto_ingestion_allowed"])
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        result_schema = json.loads(RESULT_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["mutations_performed"]["const"], False)
        self.assertEqual(result_schema["properties"]["production_qualified"]["const"], False)

    def test_no_hardware_is_hardware_pending_and_not_qualified(self):
        value = valid_inventory()
        value["candidate_ports"] = []
        value["stack_attestation"]["ports"] = []
        result = evaluate_inventory(value, contract())
        self.assertEqual(result["status"], "hardware_pending")
        self.assertFalse(result["hardware_present"])
        self.assertFalse(result["read_only_preflight_qualified"])
        self.assertFalse(result["production_qualified"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])
        self.assertFalse(result["mutations_performed"])

    def test_inventory_can_be_ready_but_authorized_probes_are_pending(self):
        result = evaluate_inventory(valid_inventory(), contract())
        self.assertEqual(result["status"], "capability_probe_pending")
        self.assertTrue(result["inventory_ready_for_authorized_probes"])
        self.assertFalse(result["read_only_preflight_qualified"])
        self.assertTrue(result["authorized_probe_execution_required"])

    def test_valid_live_receipts_complete_preflight_but_never_production(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        result = evaluate_inventory(value, contract(), baseline_inventory=value)
        self.assertEqual(result["status"], "self_consistent_capability_receipts_only")
        self.assertFalse(result["read_only_preflight_qualified"])
        self.assertTrue(result["self_consistent_capability_receipts_valid"])
        self.assertIn("not_external_attestation", result["receipt_trust_level"])
        self.assertFalse(result["production_qualified"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_current_bnx2x_is_rejected_even_if_other_fields_are_forged(self):
        value = valid_inventory()
        value["candidate_ports"][0]["pci_address"] = "0000:cb:00.0"
        value["stack_attestation"]["ports"][0]["pci_address"] = "0000:cb:00.0"
        result = evaluate_inventory(value, contract())
        self.assertEqual(result["status"], "preflight_failed")
        self.assertIn("hardware.preexisting_pci_excluded", result["blockers"])

    def test_preexisting_bcm5719_management_functions_are_rejected(self):
        value = valid_inventory()
        value["candidate_ports"][0]["interface"] = "ens9f1"
        value["candidate_ports"][0]["pci_address"] = "0000:e3:00.1"
        value["candidate_ports"][0]["vendor_id"] = "14e4"
        value["candidate_ports"][0]["device_id"] = "1657"
        value["stack_attestation"]["ports"][0]["pci_address"] = "0000:e3:00.1"
        result = evaluate_inventory(value, contract())
        self.assertIn("hardware.preexisting_pci_excluded", result["blockers"])
        self.assertIn("management.capture_interface_isolation", result["blockers"])

    def test_preexisting_device_id_is_rejected_after_pci_renumbering(self):
        value = valid_inventory()
        value["candidate_ports"][0]["pci_address"] = "0000:81:00.0"
        value["candidate_ports"][0]["vendor_id"] = "14e4"
        value["candidate_ports"][0]["device_id"] = "168e"
        value["stack_attestation"]["ports"][0]["pci_address"] = "0000:81:00.0"
        result = evaluate_inventory(value, contract())
        self.assertIn("hardware.preexisting_device_id_excluded", result["blockers"])

    def test_dual_port_adapter_may_share_serial_but_pci_interfaces_are_unique(self):
        value = valid_inventory()
        second = copy.deepcopy(value["candidate_ports"][0])
        second["interface"] = "ens10f1"
        second["pci_address"] = "0000:41:00.1"
        value["candidate_ports"].append(second)
        stack_second = copy.deepcopy(value["stack_attestation"]["ports"][0])
        stack_second["pci_address"] = "0000:41:00.1"
        value["stack_attestation"]["ports"].append(stack_second)
        result = evaluate_inventory(value, contract())
        self.assertNotIn("hardware.identity_complete_unique", result["blockers"])

    def test_degraded_pcie_link_fails(self):
        value = valid_inventory()
        value["candidate_ports"][0]["pcie_current_width"] = 4
        result = evaluate_inventory(value, contract())
        self.assertIn("pcie.link_width_speed", result["blockers"])

    def test_numa_unknown_or_remote_workers_fail(self):
        value = valid_inventory()
        value["worker_cpu_plan"]["numa_nodes"][0] = 0
        result = evaluate_inventory(value, contract())
        self.assertIn("numa.local_worker_plan", result["blockers"])

    def test_management_capture_ip_and_default_route_fail(self):
        value = valid_inventory()
        port = value["candidate_ports"][0]
        port["ip_addresses"] = ["10.0.5.99"]
        port["default_route"] = True
        result = evaluate_inventory(value, contract())
        self.assertIn("management.capture_interface_isolation", result["blockers"])

    def test_driver_firmware_ddp_claim_requires_bound_attestation(self):
        value = valid_inventory()
        value["stack_attestation"]["ports"][0]["firmware_version"] = "stale"
        result = evaluate_inventory(value, contract())
        self.assertIn(
            "stack.driver_firmware_ddp_compatibility", result["blockers"]
        )

    def test_same_host_or_same_nic_generator_fails(self):
        value = valid_inventory()
        value["independent_generator"]["generator_host_id"] = value["capture_host_id"]
        value["independent_generator"]["generator_nic_serial"] = value[
            "candidate_ports"
        ][0]["adapter_serial"]
        result = evaluate_inventory(value, contract())
        self.assertIn("generator.independent_identity_capacity", result["blockers"])

    def test_xdp_copy_fallback_or_generic_attach_fails(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["xdp_probe_receipt"]["attach_mode"] = "generic"
        value["xdp_probe_receipt"]["xsk_bind_mode"] = "copy"
        value["xdp_probe_receipt"]["copy_fallback_detected"] = True
        value["xdp_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["xdp_probe_receipt"]
        )
        result = evaluate_inventory(value, contract())
        self.assertIn(
            "xdp.native_forced_zerocopy_live_receipt", result["blockers"]
        )

    def test_dpdk_single_active_queue_or_missing_tss_fails(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["dpdk_probe_receipt"]["tss_enabled"] = False
        value["dpdk_probe_receipt"]["rx_queue_packets"] = [8000] + [0] * 7
        value["dpdk_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["dpdk_probe_receipt"]
        )
        result = evaluate_inventory(value, contract())
        self.assertIn("dpdk.rss_tss_multiqueue_live_receipt", result["blockers"])

    def test_xdp_and_dpdk_extreme_queue_skew_fail(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        for queue_id, queue in enumerate(value["xdp_probe_receipt"]["queue_results"]):
            queue["packets"] = 1000000 if queue_id == 0 else 1
        value["dpdk_probe_receipt"]["rx_queue_packets"] = [1000000] + [1] * 7
        value["dpdk_probe_receipt"]["tx_queue_packets"] = [1000000] + [1] * 7
        value["xdp_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["xdp_probe_receipt"]
        )
        value["dpdk_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["dpdk_probe_receipt"]
        )
        result = evaluate_inventory(value, contract())
        self.assertIn("xdp.native_forced_zerocopy_live_receipt", result["blockers"])
        self.assertIn("dpdk.rss_tss_multiqueue_live_receipt", result["blockers"])

    def test_receipt_identity_and_run_ids_are_bound(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["xdp_probe_receipt"]["capture_host_id"] = "other-host"
        value["dpdk_probe_receipt"]["run_id"] = value["xdp_probe_receipt"]["run_id"]
        value["xdp_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["xdp_probe_receipt"]
        )
        value["dpdk_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["dpdk_probe_receipt"]
        )
        result = evaluate_inventory(value, contract())
        self.assertIn(
            "xdp.native_forced_zerocopy_live_receipt", result["blockers"]
        )
        self.assertIn("probes.distinct_runs", result["blockers"])

    def test_receipt_content_hash_is_recomputed(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["xdp_probe_receipt"]["tested_queue_count"] = 999
        result = evaluate_inventory(value, contract())
        self.assertIn(
            "xdp.native_forced_zerocopy_live_receipt", result["blockers"]
        )

    def test_restoration_detects_management_and_driver_drift(self):
        before = valid_inventory()
        after = copy.deepcopy(before)
        after["management_plane"]["default_route_interfaces"] = ["ens10f0"]
        after["candidate_ports"][0]["kernel_driver"] = "vfio-pci"
        comparison = compare_restoration(before, after)
        self.assertFalse(comparison["verified"])
        self.assertNotEqual(comparison["before_sha256"], comparison["after_sha256"])

    def test_invalid_inventory_envelope_fails_closed(self):
        value = valid_inventory()
        value["collection_mode"] = "mutating"
        value["mutations_performed"] = True
        result = evaluate_inventory(value, contract())
        self.assertEqual(result["status"], "invalid_inventory")
        self.assertIn("inventory.envelope", result["blockers"])

    def test_malformed_numeric_types_fail_closed_without_exception(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["dpdk_probe_receipt"]["rx_queues_configured"] = "8"
        value["dpdk_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["dpdk_probe_receipt"]
        )
        result = evaluate_inventory(value, contract())
        self.assertEqual(result["status"], "preflight_failed")
        self.assertIn("dpdk.rss_tss_multiqueue_live_receipt", result["blockers"])

        value = valid_inventory()
        value["candidate_ports"][0]["queue_capabilities"]["max_rx"] = "64"
        result = evaluate_inventory(value, contract())
        self.assertEqual(result["status"], "preflight_failed")
        self.assertIn("queues.advertised_capacity", result["blockers"])

    def test_cli_malformed_numeric_type_writes_fail_closed_output(self):
        value = valid_inventory()
        attach_valid_receipts(value)
        value["dpdk_probe_receipt"]["rx_queues_configured"] = "8"
        value["dpdk_probe_receipt"]["receipt_sha256"] = receipt_content_sha256(
            value["dpdk_probe_receipt"]
        )
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            inventory = directory / "inventory.json"
            output = directory / "result.json"
            inventory.write_text(json.dumps(value), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(CLI), "--inventory", str(inventory), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 22, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "preflight_failed")

    def test_restoration_detects_extended_data_plane_state_drift(self):
        before = valid_inventory()
        after = copy.deepcopy(before)
        after["candidate_ports"][0]["restoration_state"]["xdp_attachment"] = {
            "mode": "driver"
        }
        after["candidate_ports"][0]["restoration_state"]["mtu"] = 9000
        after["host_restoration_state"]["numa_hugepages"][
            "node1/hugepages-2048kB"
        ] = "1024"
        self.assertFalse(compare_restoration(before, after)["verified"])

    def test_cli_hardware_pending_exit_and_atomic_json(self):
        value = valid_inventory()
        value["candidate_ports"] = []
        value["stack_attestation"]["ports"] = []
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            inventory = directory / "inventory.json"
            output = directory / "result.json"
            inventory.write_text(json.dumps(value), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--contract",
                    str(CONTRACT_PATH),
                    "--inventory",
                    str(inventory),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=directory,
                env={
                    key: value
                    for key, value in os.environ.items()
                    if key != "PYTHONPATH"
                },
            )
            self.assertEqual(completed.returncode, 20, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "hardware_pending")
            self.assertEqual(list(directory.glob("*.tmp")), [])

    def test_cli_malformed_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            inventory = directory / "inventory.json"
            output = directory / "result.json"
            inventory.write_text("{broken", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--inventory",
                    str(inventory),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 23)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "invalid_inventory")
            self.assertFalse(result["production_qualified"])

    def test_cli_rejects_duplicate_keys_and_nonfinite_numbers(self):
        for payload in (
            '{"schema_version":1,"schema_version":1}',
            '{"schema_version":NaN}',
            '{"schema_version":Infinity}',
        ):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                inventory = directory / "inventory.json"
                output = directory / "result.json"
                inventory.write_text(payload, encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, str(CLI), "--inventory", str(inventory), "--output", str(output)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 23)
                self.assertEqual(json.loads(output.read_text())["status"], "invalid_inventory")

    def test_runner_default_is_read_only_and_authorization_precedes_mutation(self):
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('execute_probes="${HFT_NEW_NIC_EXECUTE_PROBES:-NO}"', runner)
        self.assertIn("APPROVED_NEW_NIC_PF_MAINTENANCE", runner)
        self.assertIn("HFT_NEW_NIC_MAINTENANCE_WINDOW", runner)
        self.assertIn("HFT_NEW_NIC_CHANGE_TICKET", runner)
        self.assertIn("HFT_NEW_NIC_HELPER_MANIFEST", runner)
        self.assertIn("HFT_NEW_NIC_TRUSTED_MANIFEST_SHA256", runner)
        self.assertIn("externally supplied trusted SHA-256 root", runner)
        self.assertIn("trap finalize EXIT", runner)
        self.assertIn("trap '' HUP INT TERM", runner)
        self.assertIn("restore_attempted=true", runner)
        self.assertIn("restoration_accepted", runner)
        self.assertNotIn("rm -rf", runner)
        self.assertIn("! -name 'evidence.sha256'", runner)
        self.assertIn("! -name 'evidence.sha256.check'", runner)
        self.assertIn('mv -- "${manifest_tmp}" evidence.sha256', runner)
        self.assertIn("receipt probe_binary_sha256 does not match", runner)
        self.assertIn("frozen_artifact_dir", runner)
        self.assertIn('timeout --signal=TERM --kill-after=10s', runner)
        for frozen_name in (
            "runner",
            "preflight_cli",
            "acceptance_module",
            "contract",
        ):
            self.assertIn(frozen_name, runner)
        authorization = runner.index('authorization}" != "APPROVED_NEW_NIC_PF_MAINTENANCE')
        helper_hash = runner.index("frozen artifact hash mismatch")
        mutation = runner.index("mutations_started=1")
        self.assertLess(authorization, mutation)
        self.assertLess(helper_hash, mutation)
        core_path_check = runner.index("path does not match the active frozen artifact")
        frozen_contract_switch = runner.index(
            'contract="${frozen_artifact_dir}/contract"'
        )
        self.assertLess(core_path_check, frozen_contract_switch)
        self.assertIn("for helper_name in xdp_probe dpdk_probe restore_helper", runner)
        self.assertNotIn('! -x "${artifact_path}"', runner)
        self.assertIn('! -f "${artifact_path}"', runner)

    @unittest.skipUnless(Path("/bin/bash").exists(), "dynamic runner test requires Linux")
    def test_runner_default_hardware_pending_and_manifest_is_complete(self):
        value = valid_inventory()
        value["candidate_ports"] = []
        value["stack_attestation"]["ports"] = []
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            inventory = directory / "inventory.json"
            inventory.write_text(json.dumps(value), encoding="utf-8")
            fake_cli_source = """#!/usr/bin/env python3
import argparse,json,pathlib,shutil
p=argparse.ArgumentParser()
p.add_argument('--contract'); p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--inventory-output',type=pathlib.Path,required=True)
p.add_argument('--worker-cpus'); p.add_argument('--interfaces',nargs='+')
p.add_argument('--stack-attestation'); p.add_argument('--generator-attestation')
p.add_argument('--xdp-receipt'); p.add_argument('--dpdk-receipt')
p.add_argument('--baseline-inventory')
a=p.parse_args()
source=pathlib.Path(__import__('os').environ['HFT_TEST_PENDING_INVENTORY'])
shutil.copyfile(source,a.inventory_output)
result={'schema_version':1,'scope':'new_high_speed_nic_acceptance_preflight',
'status':'hardware_pending','checks':[],'blockers':[],'pending':['hardware.candidate_not_present'],
'hardware_present':False,'inventory_ready_for_authorized_probes':False,
'read_only_preflight_qualified':False,'production_qualified':False,
'final_pareto_ingestion_allowed':False,'mutations_performed':False}
a.output.write_text(json.dumps(result)+'\\n',encoding='utf-8')
raise SystemExit(20)
"""
            project = directory / "project"
            (project / "scripts").mkdir(parents=True)
            (project / "configs").mkdir(parents=True)
            runner = project / "scripts" / RUNNER.name
            runner.write_text(RUNNER.read_text(encoding="utf-8"), encoding="utf-8")
            (project / "scripts" / "preflight_new_nic.py").write_text(
                fake_cli_source, encoding="utf-8"
            )
            (project / "configs" / "new_nic_acceptance_contract_v1.json").write_text(
                CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
            )
            evidence = directory / "evidence"
            env = dict(os.environ)
            env.update(
                {
                    "HFT_NEW_NIC_EVIDENCE_ROOT": str(evidence),
                    "HFT_NEW_NIC_PYTHON": sys.executable,
                    "HFT_TEST_PENDING_INVENTORY": str(inventory),
                }
            )
            completed = subprocess.run(
                ["/bin/bash", str(runner)],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 20, completed.stderr)
            run_dirs = list(evidence.glob("hft_new_nic_acceptance_*"))
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]
            result = json.loads((run_dir / "preflight.before.json").read_text())
            self.assertEqual(result["status"], "hardware_pending")
            self.assertFalse(result["mutations_performed"])
            manifest = (run_dir / "evidence.sha256").read_text(encoding="utf-8")
            self.assertNotIn("evidence.sha256  ", manifest)
            self.assertNotIn("evidence.sha256.check", manifest)
            for line in manifest.splitlines():
                digest, name = line.split("  ", 1)
                self.assertEqual(
                    hashlib.sha256((run_dir / name).read_bytes()).hexdigest(), digest
                )


if __name__ == "__main__":
    unittest.main()

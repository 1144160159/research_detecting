from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hft_mgbs.new_nic_r0 import (
    canonical_sha256,
    evaluate_r0_campaign,
    receipt_content_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "configs" / "new_nic_r0_campaign_contract_v1.json"
COMPOSER = ROOT / "scripts" / "compose_new_nic_r0_acceptance.py"
EVALUATOR = ROOT / "hft_mgbs" / "new_nic_r0.py"
RUNNER = ROOT / "scripts" / "run_new_nic_r0_campaign.sh"


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(value):
    value["receipt_sha256"] = receipt_content_sha256(value)
    return value


def iso(second: int) -> str:
    value = datetime(2026, 8, 13, tzinfo=timezone.utc) + timedelta(seconds=second)
    return value.isoformat().replace("+00:00", "Z")


def synthetic_bundle(producer_hashes=None):
    hashes = producer_hashes or {
        "xdp_runner": "1" * 64,
        "dpdk_runner": "2" * 64,
        "generator_runner": "3" * 64,
        "resource_sampler": "4" * 64,
        "fallback_orchestrator": "5" * 64,
        "restore_helper": "6" * 64,
        "arrival_evidence_manifest": "7" * 64,
    }
    campaign_id = "r0-synthetic-campaign"
    campaign = {
        "schema_version": 1,
        "scope": "new_high_speed_nic_r0_campaign",
        "campaign_id": campaign_id,
        "capture_host_id": "capture-host",
        "authorized_execution": True,
        "mutations_performed": True,
        "arrival_evidence_manifest_sha256": hashes["arrival_evidence_manifest"],
        "candidate_pci_addresses": ["0000:41:00.0"],
        "generator_identity": {
            "generator_host_id": "generator-host",
            "generator_nic_serial": "GENERATOR-SERIAL",
            "physical_link_id": "direct-link-a",
            "marker_manifest_sha256": "a" * 64,
        },
        "topology": {
            "fallback_design": "prearmed_secondary_pf",
            "same_pf_runtime_driver_rebind": False,
            "independent_generator": True,
            "same_adapter_loopback": False,
        },
    }
    inventory = {
        "schema_version": 1,
        "scope": "new_high_speed_nic_inventory",
        "candidate_ports": [
            {
                "pci_address": "0000:41:00.0",
                "interface": "ens10f0",
                "adapter_serial": "CAPTURE-SERIAL",
            }
        ],
    }
    preflight = {
        "schema_version": 1,
        "scope": "new_high_speed_nic_preflight_result",
        "status": "self_consistent_capability_receipts_only",
        "hardware_present": True,
        "self_consistent_capability_receipts_valid": True,
        "production_qualified": False,
        "inventory_sha256": canonical_sha256(inventory),
    }

    def make_run(backend: str, repeat: int):
        role = "xdp_runner" if backend.startswith("native") else "dpdk_runner"
        run_id = ("xdp" if role == "xdp_runner" else "dpdk") + "-{}".format(repeat)
        start = repeat * 100
        sent = 180_000_000
        generator = seal(
            {
                "schema_version": 1,
                "scope": "new_nic_r0_generator_window_receipt",
                "campaign_id": campaign_id,
                "producer_role": "generator_runner",
                "producer_sha256": hashes["generator_runner"],
                "run_id": run_id,
                "generator_host_id": "generator-host",
                "generator_nic_serial": "GENERATOR-SERIAL",
                "physical_link_id": "direct-link-a",
                "marker_manifest_sha256": "a" * 64,
                "started_at_utc": iso(start),
                "completed_at_utc": iso(start + 15),
                "requested_packets": sent,
                "sent_packets": sent,
                "tx_errors": 0,
            }
        )
        resource = seal(
            {
                "schema_version": 1,
                "scope": "new_nic_r0_resource_window_receipt",
                "campaign_id": campaign_id,
                "producer_role": "resource_sampler",
                "producer_sha256": hashes["resource_sampler"],
                "run_id": run_id,
                "started_at_utc": iso(start),
                "completed_at_utc": iso(start + 15),
                "samples": [
                    {
                        "timestamp_utc": iso(start + offset),
                        "host_cpu_fraction": 0.50,
                        "host_memory_fraction": 0.40,
                        "process_rss_bytes": 1_073_741_824,
                        "hugepage_reserved_bytes": 2_147_483_648,
                    }
                    for offset in range(15)
                ],
            }
        )
        backend_proof = (
            {
                "attach_mode": "native",
                "xsk_bind_mode": "forced_zerocopy",
                "zero_copy_confirmed": True,
                "copy_fallback_detected": False,
                "xdp_attach_flags": 4,
                "xsk_bind_flags": 4,
                "xdp_program_ids": [1001],
                "xsk_socket_count": 8,
                "xsk_zerocopy_rx_packets": sent,
                "xsk_copy_rx_packets": 0,
            }
            if role == "xdp_runner"
            else {
                "rss_enabled": True,
                "tss_enabled": True,
                "reta_programmed": True,
                "rx_queues_configured": 8,
                "tx_queues_configured": 8,
                "rss_reta": list(range(8)) * 16,
                "rss_hash_types": ["ipv4", "ipv4-tcp", "ipv4-udp"],
                "per_queue_rx_packets": [22_500_000] * 8,
                "per_queue_tx_packets": [1_000_000] * 8,
            }
        )
        return seal(
            {
                "schema_version": 1,
                "scope": "new_nic_r0_run_receipt",
                "campaign_id": campaign_id,
                "producer_role": role,
                "producer_sha256": hashes[role],
                "run_id": run_id,
                "repeat_index": repeat,
                "backend": backend,
                "capture_host_id": "capture-host",
                "candidate_pci_addresses": ["0000:41:00.0"],
                "generator_host_id": "generator-host",
                "generator_nic_serial": "GENERATOR-SERIAL",
                "physical_link_id": "direct-link-a",
                "started_at_utc": iso(start),
                "completed_at_utc": iso(start + 15),
                "packet_size_bytes": 64,
                "generator": generator,
                "capture": {
                    "unique_packets": sent,
                    "sequence_gaps": 0,
                    "nic_rx_missed": 0,
                    "nic_rx_errors": 0,
                    "socket_drops": 0,
                    "descriptor_errors": 0,
                    "duplicate_packets": 0,
                    "out_of_order_packets": 0,
                    "queue_packets": [22_500_000] * 8,
                },
                "latency_histogram": [
                    {"le_us": 50.0, "cumulative_count": sent}
                ],
                "latency_proof": {
                    "measurement_method": "hardware_timestamp_ptp_correlated",
                    "clock_sync_error_us": 1.0,
                    "timestamped_packets": sent,
                    "negative_latency_samples": 0,
                },
                "resource": resource,
                "key_flow": {
                    "basis": "independent_generator_marker_manifest",
                    "marker_manifest_sha256": "a" * 64,
                    "total": 100,
                    "covered": 100,
                    "skipped_due_budget": 0,
                },
                "backend_proof": backend_proof,
            }
        )

    xdp = [make_run("native_af_xdp_forced_zerocopy", index) for index in (1, 2, 3)]
    dpdk = [make_run("dpdk_rss_tss_multiqueue", index) for index in (1, 2, 3)]
    fallback = []
    for index in (1, 2, 3):
        generator_transition = seal(
            {
                "schema_version": 1,
                "scope": "new_nic_r0_generator_transition_receipt",
                "campaign_id": campaign_id,
                "producer_role": "generator_runner",
                "producer_sha256": hashes["generator_runner"],
                "trial_id": "fallback-{}".format(index),
                "generator_host_id": "generator-host",
                "generator_nic_serial": "GENERATOR-SERIAL",
                "physical_link_id": "direct-link-a",
                "marker_manifest_sha256": "a" * 64,
                "window_started_monotonic_ns": 900_000_000,
                "window_completed_monotonic_ns": 1_300_000_000,
                "requested_packets": 1_000_000,
                "sent_packets": 1_000_000,
                "tx_errors": 0,
                "packets_before_fault": 250_000,
                "packets_fault_to_recovery": 500_000,
                "packets_after_recovery": 250_000,
                "max_inter_packet_gap_us": 10.0,
            }
        )
        fallback.append(
            seal(
                {
                    "schema_version": 1,
                    "scope": "new_nic_r0_fallback_trial_receipt",
                    "campaign_id": campaign_id,
                    "producer_role": "fallback_orchestrator",
                    "producer_sha256": hashes["fallback_orchestrator"],
                    "trial_id": "fallback-{}".format(index),
                    "repeat_index": index,
                    "xdp_run_id": "xdp-{}".format(index),
                    "dpdk_run_id": "dpdk-{}".format(index),
                    "fault_kind": "forced_xdp_primary_stop",
                    "generator_continuous": True,
                    "generator_transition": generator_transition,
                    "fault_injected_monotonic_ns": 1_000_000_000,
                    "first_dpdk_packet_monotonic_ns": 1_200_000_000,
                    "reported_recovery_ms": 200.0,
                    "transition": {
                        "expected_packets": 1_000_000,
                        "received_unique_packets": 1_000_000,
                        "sequence_gaps": 0,
                        "duplicate_packets": 0,
                        "out_of_order_packets": 0,
                    },
                }
            )
        )
    domains = {name: {"frozen": name} for name in load_contract()["restoration_gate"]["required_state_domains"]}

    def snapshot(phase):
        return seal(
            {
                "schema_version": 1,
                "scope": "new_nic_r0_restoration_snapshot",
                "campaign_id": campaign_id,
                "producer_role": "restore_helper",
                "producer_sha256": hashes["restore_helper"],
                "phase": phase,
                "state_domains": copy.deepcopy(domains),
            }
        )

    return {
        "contract": load_contract(),
        "campaign": campaign,
        "arrival_inventory": inventory,
        "arrival_preflight": preflight,
        "xdp_runs": xdp,
        "dpdk_runs": dpdk,
        "fallback_trials": fallback,
        "restoration_before": snapshot("before"),
        "restoration_after": snapshot("after"),
        "producer_hashes": hashes,
    }


def evaluate(bundle):
    return evaluate_r0_campaign(
        **bundle,
        trusted_manifest_verified=True,
        trusted_manifest_sha256="f" * 64,
    )


def reseal_run(run):
    run["receipt_sha256"] = receipt_content_sha256(run)


class NewNicR0EvaluatorTests(unittest.TestCase):
    def test_valid_campaign_qualifies_only_r0(self):
        result = evaluate(synthetic_bundle())
        self.assertEqual(result["status"], "r0_qualified")
        self.assertEqual(result["xdp_primary_repeats_qualified"], 3)
        self.assertEqual(result["dpdk_fallback_repeats_qualified"], 3)
        self.assertEqual(result["fallback_trials_qualified"], 3)
        self.assertTrue(result["restoration"]["qualified"])
        self.assertTrue(result["mutations_performed"])
        self.assertFalse(result["production_qualified"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def assert_rejected(self, mutate):
        bundle = synthetic_bundle()
        mutate(bundle)
        self.assertEqual(evaluate(bundle)["status"], "r0_rejected")

    def test_exact_three_repeats_required(self):
        self.assert_rejected(lambda b: b["xdp_runs"].pop())

    def test_below_12_mpps_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["generator"]["requested_packets"] = 179_000_000
            run["generator"]["sent_packets"] = 179_000_000
            run["generator"]["receipt_sha256"] = receipt_content_sha256(run["generator"])
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_short_window_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["completed_at_utc"] = iso(114)
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_loss_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["capture"]["sequence_gaps"] = 1
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_bad_p99_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["latency_histogram"] = [{"le_us": 101.0, "cumulative_count": 180_000_000}]
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_latency_provenance_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["latency_proof"]["clock_sync_error_us"] = 6.0
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_resource_limit_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["resource"]["samples"][0]["host_cpu_fraction"] = 0.90
            run["resource"]["receipt_sha256"] = receipt_content_sha256(run["resource"])
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_resource_window_gap_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["resource"]["samples"][-1]["timestamp_utc"] = iso(112)
            run["resource"]["receipt_sha256"] = receipt_content_sha256(run["resource"])
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_key_flow_denominator_and_budget_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["key_flow"]["total"] = 0
            run["key_flow"]["covered"] = 0
            run["key_flow"]["skipped_due_budget"] = 1
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_generic_or_copy_xdp_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["backend_proof"]["attach_mode"] = "generic"
            run["backend_proof"]["copy_fallback_detected"] = True
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_xdp_self_report_cannot_override_raw_flags(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["backend_proof"]["xdp_attach_flags"] = 2
            run["backend_proof"]["xsk_bind_flags"] = 2
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_dpdk_string_queue_count_fails_closed(self):
        def mutate(bundle):
            run = bundle["dpdk_runs"][0]
            run["backend_proof"]["rx_queues_configured"] = "8"
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_queue_skew_rejected(self):
        def mutate(bundle):
            run = bundle["dpdk_runs"][0]
            run["capture"]["queue_packets"] = [179_999_993] + [1] * 7
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_dpdk_self_report_cannot_override_raw_reta(self):
        def mutate(bundle):
            run = bundle["dpdk_runs"][0]
            run["backend_proof"]["rss_reta"] = [0] * 128
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_slow_fallback_rejected(self):
        def mutate(bundle):
            trial = bundle["fallback_trials"][0]
            trial["first_dpdk_packet_monotonic_ns"] = 1_400_000_000
            trial["reported_recovery_ms"] = 400.0
            trial["receipt_sha256"] = receipt_content_sha256(trial)
        self.assert_rejected(mutate)

    def test_fallback_continuity_boolean_cannot_override_raw_gap(self):
        def mutate(bundle):
            trial = bundle["fallback_trials"][0]
            trial["generator_continuous"] = True
            generator = trial["generator_transition"]
            generator["max_inter_packet_gap_us"] = 101.0
            generator["receipt_sha256"] = receipt_content_sha256(generator)
            trial["receipt_sha256"] = receipt_content_sha256(trial)
        self.assert_rejected(mutate)

    def test_transition_loss_rejected(self):
        def mutate(bundle):
            trial = bundle["fallback_trials"][0]
            trial["transition"]["received_unique_packets"] -= 1
            trial["receipt_sha256"] = receipt_content_sha256(trial)
        self.assert_rejected(mutate)

    def test_restoration_drift_rejected(self):
        def mutate(bundle):
            after = bundle["restoration_after"]
            after["state_domains"]["irq_affinity"] = {"drift": True}
            after["receipt_sha256"] = receipt_content_sha256(after)
        self.assert_rejected(mutate)

    def test_restoration_phase_rejected(self):
        def mutate(bundle):
            after = bundle["restoration_after"]
            after["phase"] = "before"
            after["receipt_sha256"] = receipt_content_sha256(after)
        self.assert_rejected(mutate)

    def test_generator_not_independent_rejected(self):
        def mutate(bundle):
            bundle["campaign"]["generator_identity"]["generator_host_id"] = "capture-host"
        self.assert_rejected(mutate)

    def test_same_pf_runtime_rebind_rejected(self):
        self.assert_rejected(
            lambda b: b["campaign"]["topology"].__setitem__("same_pf_runtime_driver_rebind", True)
        )

    def test_nested_generator_receipt_tamper_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["generator"]["sent_packets"] -= 1
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_nested_resource_producer_hash_rejected(self):
        def mutate(bundle):
            run = bundle["xdp_runs"][0]
            run["resource"]["producer_sha256"] = "0" * 64
            run["resource"]["receipt_sha256"] = receipt_content_sha256(run["resource"])
            reseal_run(run)
        self.assert_rejected(mutate)

    def test_untrusted_manifest_rejected(self):
        bundle = synthetic_bundle()
        result = evaluate_r0_campaign(
            **bundle,
            trusted_manifest_verified=False,
            trusted_manifest_sha256=None,
        )
        self.assertEqual(result["status"], "r0_rejected")

    def test_nonfinite_contract_does_not_crash_result(self):
        bundle = synthetic_bundle()
        bundle["contract"]["latency_gate"]["p99_us_max"] = float("nan")
        result = evaluate(bundle)
        self.assertEqual(result["status"], "r0_rejected")
        self.assertIsNone(result["contract_sha256"])


class NewNicR0CliTests(unittest.TestCase):
    def test_hardware_pending_without_pythonpath(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "audit.json"
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            result = subprocess.run(
                [sys.executable, str(COMPOSER), "--hardware-pending", "--output", str(output)],
                cwd=temporary,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 20, result.stderr)
            audit = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(audit["status"], "hardware_pending")
            self.assertFalse(audit["mutations_performed"])

    def test_duplicate_json_key_fails_closed_with_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            contract = Path(temporary) / "contract.json"
            output = Path(temporary) / "audit.json"
            contract.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMPOSER),
                    "--hardware-pending",
                    "--contract",
                    str(contract),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 24)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "invalid_contract")

    def test_missing_external_manifest_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "audit.json"
            result = subprocess.run(
                [sys.executable, str(COMPOSER), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 21)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "evidence_pending")

    def test_formal_manifest_and_composer_identity_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "campaign"
            (root / "scripts").mkdir(parents=True)
            (root / "hft_mgbs").mkdir()
            (root / "configs").mkdir()
            shutil.copy2(COMPOSER, root / "scripts" / COMPOSER.name)
            shutil.copy2(EVALUATOR, root / "hft_mgbs" / EVALUATOR.name)
            (root / "hft_mgbs" / "__init__.py").write_text("", encoding="utf-8")
            shutil.copy2(CONTRACT_PATH, root / "configs" / CONTRACT_PATH.name)
            role_paths = {
                "composer": root / "scripts" / COMPOSER.name,
                "evaluator": root / "hft_mgbs" / EVALUATOR.name,
                "contract": root / "configs" / CONTRACT_PATH.name,
            }
            for role in (
                "xdp_runner",
                "dpdk_runner",
                "generator_runner",
                "resource_sampler",
                "fallback_orchestrator",
                "restore_helper",
                "campaign_executor",
                "trust_root_recorder",
                "runner",
            ):
                path = root / "helpers" / role
                path.parent.mkdir(exist_ok=True)
                path.write_text("#!/bin/sh\n# {}\nexit 0\n".format(role), encoding="utf-8")
                role_paths[role] = path
            arrival_manifest = root / "evidence" / "arrival_evidence_manifest.sha256"
            arrival_manifest.parent.mkdir(exist_ok=True)
            arrival_manifest.write_text("arrival-root-fixture\n", encoding="utf-8")
            role_paths["arrival_evidence_manifest"] = arrival_manifest
            execution_plan = root / "configs" / "new_nic_r0_execution_plan_v1.json"
            execution_plan.write_text('{"schema_version":1,"scope":"test-execution-plan"}\n', encoding="utf-8")
            execution_binding = root / "execution_plan.sha256"
            execution_binding.write_text(file_sha(execution_plan) + "\n", encoding="ascii")
            role_paths["execution_plan"] = execution_plan
            role_paths["execution_plan_binding"] = execution_binding
            helper_hashes = {role: file_sha(path) for role, path in role_paths.items()}
            bundle = synthetic_bundle(helper_hashes)
            json_roles = {
                "campaign": bundle["campaign"],
                "arrival_inventory": bundle["arrival_inventory"],
                "arrival_preflight": bundle["arrival_preflight"],
                "restoration_before": bundle["restoration_before"],
                "restoration_after": bundle["restoration_after"],
            }
            for index, value in enumerate(bundle["xdp_runs"], 1):
                json_roles["xdp_run_{}".format(index)] = value
            for index, value in enumerate(bundle["dpdk_runs"], 1):
                json_roles["dpdk_run_{}".format(index)] = value
            for index, value in enumerate(bundle["fallback_trials"], 1):
                json_roles["fallback_trial_{}".format(index)] = value
            for role, value in json_roles.items():
                path = root / "evidence" / (role + ".json")
                path.parent.mkdir(exist_ok=True)
                path.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
                role_paths[role] = path
            arrival_manifest.write_text(
                "{}  inventory.probes.json\n{}  preflight.probes.json\n".format(
                    file_sha(role_paths["arrival_inventory"]),
                    file_sha(role_paths["arrival_preflight"]),
                ),
                encoding="utf-8",
            )
            bundle["campaign"]["arrival_evidence_manifest_sha256"] = file_sha(arrival_manifest)
            role_paths["campaign"].write_text(
                json.dumps(bundle["campaign"], sort_keys=True, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            artifacts = [
                {
                    "role": role,
                    "path": path.relative_to(root).as_posix(),
                    "sha256": file_sha(path),
                }
                for role, path in sorted(role_paths.items())
            ]
            manifest = {
                "schema_version": 1,
                "scope": "new_nic_r0_artifact_manifest",
                "campaign_id": bundle["campaign"]["campaign_id"],
                "artifacts": artifacts,
            }
            manifest_path = root / "evidence.manifest.json"
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
            output = Path(temporary) / "audit.json"
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            command = [
                sys.executable,
                str(root / "scripts" / COMPOSER.name),
                "--artifact-root",
                str(root),
                "--manifest",
                str(manifest_path),
                "--trusted-manifest-sha256",
                file_sha(manifest_path),
                "--output",
                str(output),
            ]
            result = subprocess.run(command, cwd=temporary, env=env, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "r0_qualified")
            manifest["artifacts"][0]["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
            tampered = subprocess.run(
                command[:-3] + [file_sha(manifest_path), "--output", str(output)],
                cwd=temporary,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(tampered.returncode, 26)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "provenance_rejected")


class NewNicR0RunnerTests(unittest.TestCase):
    def test_runner_is_two_phase_locked_and_recoverable(self):
        source = RUNNER.read_text(encoding="utf-8")
        for token in (
            'phase="${HFT_NEW_NIC_R0_PHASE:-PENDING}"',
            "flock -n 9",
            '"${phase}" == "EXECUTE"',
            '"${phase}" == "COMPOSE"',
            '"${phase}" == "RECOVER"',
            "I_AUTHORIZE_NEW_NIC_R0_MUTATION",
            "I_AUTHORIZE_NEW_NIC_R0_RECOVERY",
            "HFT_NEW_NIC_R0_TRUSTED_HELPER_MANIFEST_SHA256",
            "HFT_NEW_NIC_R0_TRUSTED_EVIDENCE_MANIFEST_SHA256",
            "HFT_NEW_NIC_R0_TRUSTED_ARRIVAL_MANIFEST_SHA256",
            "arrival_binding.sha256",
            "timeout --signal=TERM --kill-after=15s",
            "RECOVERY_REQUIRED",
            "atomic_state",
        ):
            self.assertIn(token, source)

    def test_runner_freezes_all_executed_helpers(self):
        source = RUNNER.read_text(encoding="utf-8")
        for role in load_contract()["required_manifest_roles"]:
            if role in {
                "campaign",
                "arrival_inventory",
                "arrival_preflight",
                "arrival_evidence_manifest",
                "restoration_before",
                "restoration_after",
                "xdp_run_1",
                "xdp_run_2",
                "xdp_run_3",
                "dpdk_run_1",
                "dpdk_run_2",
                "dpdk_run_3",
                "fallback_trial_1",
                "fallback_trial_2",
                "fallback_trial_3",
            }:
                continue
            self.assertIn(role, source)
        self.assertIn("--xdp-repeats 3 --dpdk-repeats 3 --fallback-trials 3", source)
        self.assertIn("--offered-mpps 12 --duration-seconds 15", source)

    def test_runner_contains_no_vendor_pf_commands(self):
        source = RUNNER.read_text(encoding="utf-8")
        for forbidden in ("devlink dev eswitch set", "dpdk-devbind.py --bind", "ip link set dev ens"):
            self.assertNotIn(forbidden, source)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux runner integration")
    def test_runner_default_is_read_only_hardware_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            env = os.environ.copy()
            env.update(
                {
                    "HFT_NEW_NIC_R0_EVIDENCE_ROOT": temporary,
                    "HFT_NEW_NIC_R0_PYTHON": sys.executable,
                }
            )
            for name in list(env):
                if name.startswith("HFT_NEW_NIC_R0_") and name not in {
                    "HFT_NEW_NIC_R0_EVIDENCE_ROOT",
                    "HFT_NEW_NIC_R0_PYTHON",
                }:
                    env.pop(name, None)
            result = subprocess.run(
                ["bash", str(RUNNER)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 20, result.stdout + result.stderr)
            directories = [item for item in Path(temporary).iterdir() if item.is_dir()]
            self.assertEqual(len(directories), 1)
            audit = json.loads((directories[0] / "r0_audit.json").read_text(encoding="utf-8"))
            state = json.loads((directories[0] / "runner_state.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["status"], "hardware_pending")
            self.assertFalse(audit["mutations_performed"])
            self.assertFalse(state["mutations_performed"])
            check = subprocess.run(
                ["sha256sum", "-c", "evidence.sha256"],
                cwd=directories[0],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.production_pareto import FinalParetoSelector, SelectionPolicy
from hft_mgbs.capture_runtime_decision import build_runtime_decision_receipt


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "configs" / "final_pareto_policy_v1.json"
RUNTIME_POLICY = ROOT / "configs" / "xdp_dpdk_runtime_policy_v1.json"
ALGORITHM_SEARCH = ROOT / "configs" / "algorithm_search_rc1.json"
TEST_ALGORITHM_SHA256 = hashlib.sha256(ALGORITHM_SEARCH.read_bytes()).hexdigest()


def _accepted_algorithm_optimality_audit():
    search = json.loads(ALGORITHM_SEARCH.read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "scope": "bounded_offline_algorithm_optimality_audit",
        "search_id": search["search_id"],
        "accepted": True,
        "algorithm_only_practical_optimum_proven": True,
        "final_pareto_ingestion_allowed": False,
        "production_joint_optimum_proven": False,
        "errors": [],
        "actual_candidate_count": 10,
        "confirmatory_metric_comparison_complete": True,
        "confirmatory_evidence_hash_complete": True,
        "evidence_hash_complete_candidate_count": 10,
        "paired_metric_complete_candidate_count": 10,
        "confirmatory_practical_winner": "A09",
        "confirmatory_practical_front": ["A09"],
        "practical_front_recomputed_from_available_metrics": ["A09"],
    }
RECEIPTS = tempfile.TemporaryDirectory()
RECEIPT_ROOT = Path(RECEIPTS.name)


def metrics(name: str, **overrides):
    values = {
        "name": name,
        "grouped_macro_f1": 0.95,
        "independent_macro_f1": 0.74,
        "independent_attack_recall": 0.76,
        "independent_benign_recall": 0.945,
        "independent_auprc": 0.52,
        "independent_ece": 0.038,
        "ground_truth_event_recall": 0.735,
        "gain_per_cost": 1.00,
        "throughput_mpps": 10.5,
        "packet_drop_count": 0,
        "p99_latency_us": 7000.0,
        "p999_latency_us": 30000.0,
        "cpu_utilization": 0.60,
        "gpu_utilization": 0.50,
        "memory_utilization": 0.50,
        "gpu_memory_utilization": 0.40,
        "budget_overrun_count": 0,
        "key_flow_coverage": 0.995,
        "fallback_recovery_s": 0.20,
        "complexity": 0.40,
    }
    values.update(overrides)
    return values


def _write_runtime_receipt(record):
    values = record["metrics"]
    backend = record["backend"]
    windows = []
    raw_windows = []
    throughput_packets = int(round(values["throughput_mpps"] * 1_000_000))
    total_drops = int(values["packet_drop_count"])
    key_total = 1000
    key_covered = int(round(values["key_flow_coverage"] * key_total))
    recovery_ns = int(round(values["fallback_recovery_s"] * 1_000_000_000))
    latency = [values["p99_latency_us"]] * 990 + [values["p999_latency_us"]] * 10
    for index, second in enumerate((40, 45, 50)):
        dropped = total_drops if index == 0 else 0
        start = f"2026-08-12T11:59:{second:02d}Z"
        end = f"2026-08-12T11:59:{second + 1:02d}Z"
        observed = {
            "start_utc": start,
            "end_utc": end,
            "capture_backend": "native_af_xdp_zerocopy",
            "packets_received": throughput_packets,
            "packets_dropped": dropped,
            "capture_drop_rate": dropped / (throughput_packets + dropped),
            "poll_errors": 0,
            "invalid_descriptors": 0,
            "ring_full": 0,
            "fill_empty": 0,
            "host_cpu_fraction": values["cpu_utilization"],
            "memory_fraction": values["memory_utilization"],
            "budget_overrun_count": int(values["budget_overrun_count"]),
            "fallback_recovery_ms": values["fallback_recovery_s"] * 1000.0,
            "kernel_to_feature_p99_us": values["p99_latency_us"],
            "kernel_to_feature_p999_us": values["p999_latency_us"],
            "active_rx_queues": 4,
            "key_flow_total": key_total,
            "key_flow_covered": key_covered,
            "key_flow_coverage": key_covered / key_total,
            "key_flow_coverage_basis": "remote_scored_or_local_fallback_completed",
            "xdp_attach_mode": "native",
            "af_xdp_bind_mode": "zerocopy",
        }
        windows.append(observed)
        raw_windows.append(
            {
                "run_id": f"{record['candidate_id']}-runtime-{index + 1}",
                "start_utc": start,
                "end_utc": end,
                "capture_backend": "native_af_xdp_zerocopy",
                "packets_offered": throughput_packets + dropped,
                "packets_received": throughput_packets,
                "packets_dropped": dropped,
                "latency_samples_us": latency,
                "host_cpu_samples_fraction": [values["cpu_utilization"]],
                "gpu_samples_fraction": [values["gpu_utilization"]],
                "memory_samples_fraction": [values["memory_utilization"]],
                "gpu_memory_samples_fraction": [values["gpu_memory_utilization"]],
                "budget_overrun_count": int(values["budget_overrun_count"]),
                "key_flow_total": key_total,
                "key_flow_covered": key_covered,
                "fallback_started_monotonic_ns": 1_000_000_000,
                "fallback_ready_monotonic_ns": 1_000_000_000 + recovery_ns,
                "fallback_target_backend": "dpdk",
                "fallback_mode": "dedicated_standby_adapter",
                "restoration_verified": True,
            }
        )
    observation = {
        "schema_version": 1,
        "observed_at_utc": "2026-08-12T12:00:00Z",
        "current_backend": "native_af_xdp_zerocopy",
        "capabilities": {
            "xdp": {
                "observed_at_utc": "2026-08-12T12:00:00Z",
                "attach_mode": "native",
                "native_attach_succeeded": True,
                "af_xdp_bind_mode": "zerocopy",
                "forced_zerocopy_bind_succeeded": True,
                "copy_mode_active": False,
                "rx_queue_count": 8,
                "probe_restoration_verified": True,
                "management_isolated": True,
            },
            "dpdk": {
                "observed_at_utc": "2026-08-12T12:00:00Z",
                "topology": "dedicated_standby_adapter",
                "pmd_probe_succeeded": True,
                "capacity_qualified": True,
                "observed_min_rx_mpps": 12.2,
                "rx_queue_count": 4,
                "rss_supported": True,
                "rx_queue_coverage_qualified": True,
                "zero_error_probe": True,
                "restoration_verified": True,
                "management_isolated": True,
                "standby_preflight_passed": True,
                "binary_sha256": "d" * 64,
            },
        },
        "online_windows": windows,
        "automatic_switch_authorized": True,
        "handoff": {
            "traffic_quiesced": True,
            "state_snapshot_verified": True,
            "target_preflight_passed": True,
            "rollback_ready": True,
        },
    }
    observation_path = RECEIPT_ROOT / f"{record['candidate_id']}.runtime-observation.json"
    observation_path.write_text(json.dumps(observation, sort_keys=True) + "\n", encoding="utf-8")
    observation_sha256 = hashlib.sha256(observation_path.read_bytes()).hexdigest()
    raw = {
        "schema_version": 1,
        "scope": "hft_mgbs_runtime_pareto_raw_v1",
        "candidate_id": record["candidate_id"],
        "backend": backend,
        "observation_sha256": observation_sha256,
        "windows": raw_windows,
    }
    raw_path = RECEIPT_ROOT / f"{record['candidate_id']}.runtime-raw.json"
    raw_path.write_text(json.dumps(raw, sort_keys=True) + "\n", encoding="utf-8")
    raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    policy_payload = json.loads(RUNTIME_POLICY.read_text(encoding="utf-8"))
    policy_sha256 = hashlib.sha256(RUNTIME_POLICY.read_bytes()).hexdigest()
    receipt = build_runtime_decision_receipt(
        policy_payload,
        observation,
        policy_sha256=policy_sha256,
        observation_sha256=observation_sha256,
        raw_runtime_evidence_sha256=raw_sha256,
        observation_artifact={"path": str(observation_path), "sha256": observation_sha256},
        raw_runtime_evidence={"path": str(raw_path), "sha256": raw_sha256},
        decision_at_utc="2026-08-12T12:00:05Z",
    )
    receipt_path = RECEIPT_ROOT / f"{record['candidate_id']}.runtime-receipt.json"
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    record["runtime_decision_receipt"] = {
        "path": str(receipt_path),
        "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    }


def sealed_candidate(name: str, **overrides):
    record = {
        "candidate_id": name,
        "algorithm_id": "A09",
        "metrics": metrics(name),
        "manifest_status": "complete",
        "measured_repeats": 3,
        "evidence": {
            name: True
            for name in (
                "throughput_live_replay",
                "nic_packet_drop",
                "end_to_end_p99",
                "end_to_end_p999",
                "cpu_resource",
                "gpu_resource",
                "memory_resource",
                "budget_overrun",
                "key_flow_coverage",
                "fallback_recovery",
                "host_restoration",
                "quality_protocol",
            )
        },
        "code_sha256": "a" * 64,
        "input_sha256": "b" * 64,
        "evidence_manifest_sha256": "c" * 64,
        "fallback_qualified": True,
        "restoration_verified": True,
        "final_pareto_ingestion_allowed": True,
        "backend": "xdp-native",
    }
    for key, value in overrides.items():
        if key == "metrics":
            record["metrics"].update(value)
        else:
            record[key] = value
    _write_runtime_receipt(record)
    unified_audit = {
        "schema_version": 1,
        "scope": "hft_mgbs_unified_candidate_evidence_audit",
        "candidate_id": record["candidate_id"],
        "algorithm_id": record["algorithm_id"],
        "candidate_evidence_accepted": True,
        "accepted": False,
        "production_release_accepted": False,
        "selection_performed": False,
        "selected_candidate": None,
        "final_pareto_ingestion_allowed": True,
        "full_pipeline_qualified": True,
        "errors": [],
        "derived_production_pareto_metrics": record["metrics"],
    }
    unified_audit_path = RECEIPT_ROOT / f"{name}.unified-audit.json"
    unified_audit_path.write_text(
        json.dumps(unified_audit, sort_keys=True) + "\n", encoding="utf-8"
    )
    unified_audit_sha256 = hashlib.sha256(
        unified_audit_path.read_bytes()
    ).hexdigest()
    receipt = {
        "schema_version": 1,
        "scope": "sealed_unified_candidate_evidence_receipt",
        "candidate_id": record["candidate_id"],
        "algorithm_id": record["algorithm_id"],
        "backend": record["backend"],
        "candidate_evidence_accepted": True,
        "production_release_accepted": False,
        "selection_performed": False,
        "final_pareto_ingestion_allowed": True,
        "fallback_qualified": record["fallback_qualified"],
        "restoration_verified": record["restoration_verified"],
        "algorithm_search_sha256": TEST_ALGORITHM_SHA256,
        "measured_run_ids": [
            f"{name}-run-1",
            f"{name}-run-2",
            f"{name}-run-3",
        ],
        "metrics": record["metrics"],
        "manifest_status": record["manifest_status"],
        "measured_repeats": record["measured_repeats"],
        "unified_candidate_evidence_audit_sha256": unified_audit_sha256,
        "evidence": record["evidence"],
        "code_sha256": record["code_sha256"],
        "input_sha256": record["input_sha256"],
        "evidence_manifest_sha256": record["evidence_manifest_sha256"],
        "runtime_decision_receipt_sha256": record["runtime_decision_receipt"]["sha256"],
    }
    receipt_path = RECEIPT_ROOT / f"{name}.receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8"
    )
    record["candidate_evidence_receipt"] = {
        "path": str(receipt_path),
        "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    }
    record["unified_candidate_evidence_audit"] = {
        "path": str(unified_audit_path),
        "sha256": unified_audit_sha256,
    }
    return record


class FinalParetoSelectorTests(unittest.TestCase):
    def setUp(self):
        policy_payload = json.loads(POLICY.read_text(encoding="utf-8"))
        policy_payload["algorithm_search_gate"]["sha256"] = TEST_ALGORITHM_SHA256
        optimality = _accepted_algorithm_optimality_audit()
        optimality_bytes = (
            json.dumps(optimality, sort_keys=True) + "\n"
        ).encode("utf-8")
        policy_payload["algorithm_search_gate"]["optimality_audit_path"] = (
            "algorithm_optimality_audit.json"
        )
        policy_payload["algorithm_search_gate"]["optimality_audit_sha256"] = (
            hashlib.sha256(optimality_bytes).hexdigest()
        )
        policy_payload["runtime_decision_gate"]["runtime_policy_sha256"] = (
            hashlib.sha256(RUNTIME_POLICY.read_bytes()).hexdigest()
        )
        policy_payload["algorithm_campaign_gate"] = {
            "required": True,
            "contract": {"path": "algorithm-campaign-contract.json", "sha256": "a" * 64},
            "receipt": {"path": "algorithm-campaign-receipt.json", "sha256": "b" * 64},
        }
        self.policy = SelectionPolicy.from_mapping(policy_payload)
        self.policy_fixture = tempfile.TemporaryDirectory()
        policy_root = Path(self.policy_fixture.name)
        (policy_root / "algorithm_search_rc1.json").write_bytes(
            ALGORITHM_SEARCH.read_bytes()
        )
        (policy_root / "xdp_dpdk_runtime_policy_v1.json").write_bytes(
            RUNTIME_POLICY.read_bytes()
        )
        (policy_root / "algorithm_optimality_audit.json").write_bytes(
            optimality_bytes
        )
        self.campaign_patch = __import__("unittest.mock", fromlist=["patch"]).patch(
            "hft_mgbs.production_pareto.verify_algorithm_campaign_gate",
            return_value={
                "qualified": True,
                "winner": "A09",
                "contract_sha256": "a" * 64,
                "receipt_sha256": "b" * 64,
                "projection_sha256": "c" * 64,
                "errors": [],
            },
        )
        self.campaign_patch.start()
        self.selector = FinalParetoSelector(self.policy, policy_artifact_root=policy_root)

    def tearDown(self):
        self.campaign_patch.stop()
        self.policy_fixture.cleanup()

    def test_policy_freezes_multimetric_objectives_and_ten_algorithm_cap(self):
        self.assertEqual(self.policy.max_algorithm_candidates, 10)
        self.assertGreaterEqual(len(self.policy.objectives), 6)
        self.assertIn("throughput_mpps", self.policy.objectives)
        self.assertIn("grouped_macro_f1", self.policy.objectives)
        self.assertIn("independent_macro_f1", self.policy.objectives)
        self.assertIn("independent_attack_recall", self.policy.objectives)
        self.assertIn("independent_auprc", self.policy.objectives)
        self.assertIn("independent_ece", self.policy.objectives)
        self.assertIn("p99_latency_us", self.policy.objectives)
        self.assertIn("p999_latency_us", self.policy.objectives)
        self.assertIn("resource_pressure", self.policy.objectives)
        self.assertIn("key_flow_coverage", self.policy.objectives)
        self.assertIn("fallback_recovery_s", self.policy.objectives)

    def test_current_algorithm_optimality_audit_forces_fail_closed(self):
        current_policy = SelectionPolicy.from_mapping(
            json.loads(POLICY.read_text(encoding="utf-8"))
        )
        with __import__("unittest.mock", fromlist=["patch"]).patch(
            "hft_mgbs.production_pareto.verify_algorithm_campaign_gate",
            return_value={
                "qualified": False,
                "winner": None,
                "contract_sha256": "a" * 64,
                "receipt_sha256": None,
                "projection_sha256": None,
                "errors": ["algorithm_campaign.receipt.reference"],
            },
        ):
            selector = FinalParetoSelector(
                current_policy, policy_artifact_root=POLICY.parent
            )
        self.assertIn("algorithm_optimality.accepted", selector.policy_errors)
        self.assertIn(
            "algorithm_optimality.algorithm_only_practical_optimum_proven",
            selector.policy_errors,
        )
        self.assertNotIn(
            "algorithm_optimality.final_pareto_ingestion_allowed",
            selector.policy_errors,
        )

    def test_complete_algorithm_audit_reaches_joint_runtime_selection_only(self):
        self.assertFalse(self.selector.policy_errors)
        result = self.selector.select([sealed_candidate("algorithm_gate_passes")])
        self.assertIsNone(result.champion_id)
        self.assertIn("candidate_count_below_min:1<2", result.global_errors)

    def test_only_pareto_champion_grants_final_production_release(self):
        result = self.selector.select(
            [sealed_candidate("candidate_a"), sealed_candidate("candidate_b")]
        ).as_dict()

        self.assertTrue(result["selection_qualified"])
        self.assertTrue(result["production_release_accepted"])
        self.assertTrue(result["accepted"])
        self.assertEqual(result["selected_candidate"], result["champion_id"])

    def test_legacy_optimality_cache_hash_drift_still_fails_closed(self):
        audit_path = Path(self.policy_fixture.name) / "algorithm_optimality_audit.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        audit["confirmatory_practical_winner"] = "A10"
        audit["confirmatory_practical_front"] = ["A10"]
        audit["practical_front_recomputed_from_available_metrics"] = ["A10"]
        audit_path.write_text(json.dumps(audit, sort_keys=True) + "\n", encoding="utf-8")
        selector = FinalParetoSelector(
            self.policy, policy_artifact_root=Path(self.policy_fixture.name)
        )
        self.assertIn("algorithm_optimality.sha256", selector.policy_errors)
        # The formal campaign gate owns winner semantics.  The legacy cache is
        # retained only as a hash-bound historical artifact on this path.
        self.assertNotIn("algorithm_optimality.selected_winner", selector.policy_errors)

    def test_single_metric_winners_do_not_bypass_multimetric_champion(self):
        fastest = sealed_candidate(
            "fastest",
            metrics={
                "throughput_mpps": 13.0,
                "grouped_macro_f1": 0.90,
                "independent_macro_f1": 0.70,
                "independent_attack_recall": 0.72,
                "independent_benign_recall": 0.93,
                "independent_auprc": 0.45,
                "independent_ece": 0.05,
                "ground_truth_event_recall": 0.70,
                "gain_per_cost": 0.80,
                "p99_latency_us": 9500.0,
                "p999_latency_us": 48000.0,
                "cpu_utilization": 0.84,
                "gpu_utilization": 0.84,
                "memory_utilization": 0.84,
                "gpu_memory_utilization": 0.84,
                "key_flow_coverage": 0.990,
                "fallback_recovery_s": 0.29,
                "complexity": 0.80,
            },
        )
        most_accurate = sealed_candidate(
            "most_accurate",
            metrics={
                "throughput_mpps": 10.0,
                "grouped_macro_f1": 0.99,
                "independent_macro_f1": 0.90,
                "independent_attack_recall": 0.92,
                "independent_benign_recall": 0.98,
                "independent_auprc": 0.80,
                "independent_ece": 0.01,
                "ground_truth_event_recall": 0.90,
                "gain_per_cost": 0.75,
                "p99_latency_us": 9000.0,
                "p999_latency_us": 45000.0,
                "cpu_utilization": 0.80,
                "gpu_utilization": 0.82,
                "memory_utilization": 0.80,
                "gpu_memory_utilization": 0.82,
                "key_flow_coverage": 0.992,
                "fallback_recovery_s": 0.28,
                "complexity": 0.75,
            },
        )
        balanced = sealed_candidate(
            "balanced",
            metrics={
                "throughput_mpps": 11.2,
                "grouped_macro_f1": 0.96,
                "independent_macro_f1": 0.80,
                "independent_attack_recall": 0.84,
                "independent_benign_recall": 0.96,
                "independent_auprc": 0.65,
                "independent_ece": 0.025,
                "ground_truth_event_recall": 0.82,
                "gain_per_cost": 1.30,
                "p99_latency_us": 5500.0,
                "p999_latency_us": 24000.0,
                "cpu_utilization": 0.55,
                "gpu_utilization": 0.50,
                "memory_utilization": 0.48,
                "gpu_memory_utilization": 0.45,
                "key_flow_coverage": 1.0,
                "fallback_recovery_s": 0.12,
                "complexity": 0.30,
            },
        )
        result = self.selector.select([fastest, most_accurate, balanced])
        self.assertEqual(result.champion_id, "balanced")
        self.assertNotEqual(result.champion_id, "fastest")
        self.assertNotEqual(result.champion_id, "most_accurate")

    def test_all_operational_hard_gates_are_applied_before_pareto(self):
        unsafe = sealed_candidate(
            "unsafe",
            metrics={
                "throughput_mpps": 9.9,
                "packet_drop_count": 1,
                "p99_latency_us": 10001.0,
                "p999_latency_us": 50001.0,
                "cpu_utilization": 0.86,
                "gpu_utilization": 0.86,
                "memory_utilization": 0.86,
                "gpu_memory_utilization": 0.86,
                "budget_overrun_count": 1,
                "key_flow_coverage": 0.98,
                "fallback_recovery_s": 0.31,
            },
        )
        result = self.selector.select([unsafe, sealed_candidate("safe")])
        audit = result.audit_by_id("unsafe")
        # Runtime evidence is replayed before Pareto admission, so an envelope
        # that violates live operational gates is rejected at the stronger
        # evidence boundary instead of trusting its self-reported metrics.
        self.assertEqual(audit.decision_stage, "evidence")
        codes = {reason.code for reason in audit.reasons}
        self.assertTrue(
            {
                "runtime_decision.action",
                "runtime_decision.selected_backend",
                "runtime_decision.online_gates",
            }.issubset(codes)
        )
        self.assertEqual(result.champion_id, "safe")

    def test_evidence_hash_fallback_and_restoration_are_fail_closed(self):
        evidence = sealed_candidate("unsealed")
        evidence["evidence"]["fallback_recovery"] = False
        evidence["evidence"]["host_restoration"] = False
        evidence["code_sha256"] = "not-a-hash"
        evidence["input_sha256"] = "B" * 64
        evidence["evidence_manifest_sha256"] = ""
        evidence["fallback_qualified"] = False
        evidence["restoration_verified"] = False
        result = self.selector.select([evidence])
        audit = result.audit_by_id("unsealed")
        self.assertEqual(audit.decision_stage, "evidence")
        codes = {reason.code for reason in audit.reasons}
        self.assertTrue(
            {
                "evidence.fallback_recovery",
                "evidence.host_restoration",
                "code_sha256",
                "input_sha256",
                "evidence_manifest_sha256",
                "fallback_qualified",
                "restoration_verified",
            }.issubset(codes)
        )
        self.assertIsNone(result.champion_id)

    def test_candidate_evidence_receipt_is_rehashed_and_binds_independent_run_ids(self):
        candidate = sealed_candidate("receipt_tamper")
        receipt_path = Path(candidate["candidate_evidence_receipt"]["path"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["measured_run_ids"] = ["same", "same", "same"]
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        result = self.selector.select([candidate])
        codes = {reason.code for reason in result.audit_by_id("receipt_tamper").reasons}
        self.assertIn("candidate_evidence_receipt.sha256", codes)
        self.assertIsNone(result.champion_id)

    def test_candidate_evidence_receipt_binds_exact_joint_metrics(self):
        candidate = sealed_candidate("metric_tamper")
        candidate["metrics"]["throughput_mpps"] = 99.0
        result = self.selector.select([candidate, sealed_candidate("control")])
        codes = {reason.code for reason in result.audit_by_id("metric_tamper").reasons}
        self.assertIn("candidate_evidence_receipt.metrics", codes)

    def test_receipt_without_unified_candidate_evidence_audit_cannot_qualify(self):
        candidate = sealed_candidate("missing_unified")
        candidate["unified_candidate_evidence_audit"] = None
        result = self.selector.select([candidate, sealed_candidate("control")])
        codes = {
            reason.code
            for reason in result.audit_by_id("missing_unified").reasons
        }
        self.assertIn("unified_candidate_evidence_audit", codes)

    def test_generic_xdp_is_not_a_production_candidate(self):
        candidate = sealed_candidate("generic_xdp", backend="xdp-generic")
        result = self.selector.select([candidate])
        audit = result.audit_by_id("generic_xdp")
        self.assertEqual(audit.decision_stage, "evidence")
        self.assertIn("backend.production_capability", {reason.code for reason in audit.reasons})

    def test_unknown_algorithm_cannot_enter_production_selection(self):
        candidate = sealed_candidate("unknown_algorithm", algorithm_id="FAKE")
        result = self.selector.select([candidate, sealed_candidate("control")])
        codes = {
            reason.code
            for reason in result.audit_by_id("unknown_algorithm").reasons
        }
        self.assertIn("algorithm_id.production_admission", codes)

    def test_cli_runs_directly_from_project_root_without_pythonpath(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "audit.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/select_production_pareto.py",
                    "--policy",
                    "configs/final_pareto_policy_v1.json",
                    "--candidates",
                    "configs/current_environment_joint_candidates_v1.json",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=False,
                env={
                    key: value
                    for key, value in __import__("os").environ.items()
                    if key != "PYTHONPATH"
                },
            )
            self.assertEqual(completed.returncode, 10, completed.stderr)
            self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["selection_qualified"])

    def test_backend_priority_breaks_only_an_exact_objective_tie(self):
        dpdk = sealed_candidate("a_dpdk", backend="dpdk")
        xdp = sealed_candidate("z_xdp", backend="xdp-native")
        result = self.selector.select([dpdk, xdp])
        self.assertEqual(result.champion_id, "z_xdp")
        self.assertIn(
            "runtime_decision.dpdk_primary_forbidden",
            {reason.code for reason in result.audit_by_id("a_dpdk").reasons},
        )

    def test_runtime_receipt_and_raw_evidence_are_mandatory(self):
        candidate = sealed_candidate("missing_runtime")
        candidate["runtime_decision_receipt"] = None
        result = self.selector.select([candidate, sealed_candidate("control_runtime")])
        codes = {reason.code for reason in result.audit_by_id("missing_runtime").reasons}
        self.assertIn("runtime_decision_receipt", codes)
        self.assertIn(
            "candidate_evidence_receipt.runtime_decision_receipt_sha256", codes
        )

    def test_raw_latency_is_recomputed_after_all_hashes_are_resealed(self):
        candidate = sealed_candidate("raw_recompute")
        runtime_path = Path(candidate["runtime_decision_receipt"]["path"])
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        raw_path = Path(runtime["raw_runtime_evidence"]["path"])
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw["windows"][0]["latency_samples_us"] = [1.0] * 1000
        raw_path.write_text(json.dumps(raw, sort_keys=True) + "\n", encoding="utf-8")
        raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        runtime["raw_runtime_evidence"]["sha256"] = raw_sha256
        runtime["raw_runtime_evidence_sha256"] = raw_sha256
        runtime_path.write_text(json.dumps(runtime, sort_keys=True) + "\n", encoding="utf-8")
        runtime_sha256 = hashlib.sha256(runtime_path.read_bytes()).hexdigest()
        candidate["runtime_decision_receipt"]["sha256"] = runtime_sha256
        release_path = Path(candidate["candidate_evidence_receipt"]["path"])
        release = json.loads(release_path.read_text(encoding="utf-8"))
        release["runtime_decision_receipt_sha256"] = runtime_sha256
        release_path.write_text(json.dumps(release, sort_keys=True) + "\n", encoding="utf-8")
        candidate["candidate_evidence_receipt"]["sha256"] = hashlib.sha256(
            release_path.read_bytes()
        ).hexdigest()
        result = self.selector.select([candidate, sealed_candidate("raw_control")])
        codes = {reason.code for reason in result.audit_by_id("raw_recompute").reasons}
        self.assertIn("runtime_raw.windows[0].observation_p99", codes)
        self.assertIn("runtime_raw.windows[0].observation_p999", codes)

    def test_candidate_count_above_frozen_cap_invalidates_selection(self):
        result = self.selector.select(
            [sealed_candidate(f"A{index:02d}") for index in range(1, 12)]
        )
        self.assertIsNone(result.champion_id)
        self.assertEqual(result.pareto_front_ids, ())
        self.assertIn(
            "candidate_count_exceeds_max:11>10", result.global_errors
        )

    def test_dominated_candidate_has_named_explainable_eliminator(self):
        strong = sealed_candidate("strong")
        weak = sealed_candidate(
            "weak",
            metrics={
                "grouped_macro_f1": 0.90,
                "independent_macro_f1": 0.70,
                "independent_attack_recall": 0.72,
                "independent_benign_recall": 0.93,
                "independent_auprc": 0.45,
                "independent_ece": 0.05,
                "ground_truth_event_recall": 0.70,
                "gain_per_cost": 0.70,
                "throughput_mpps": 10.1,
                "p99_latency_us": 8000.0,
                "p999_latency_us": 40000.0,
                "cpu_utilization": 0.70,
                "gpu_utilization": 0.65,
                "memory_utilization": 0.65,
                "gpu_memory_utilization": 0.60,
                "key_flow_coverage": 0.991,
                "fallback_recovery_s": 0.25,
                "complexity": 0.60,
            },
        )
        result = self.selector.select([weak, strong])
        weak_audit = result.audit_by_id("weak")
        self.assertEqual(weak_audit.decision_stage, "dominated")
        self.assertEqual(weak_audit.dominated_by, ("strong",))
        self.assertEqual(result.pareto_front_ids, ("strong",))


if __name__ == "__main__":
    unittest.main()

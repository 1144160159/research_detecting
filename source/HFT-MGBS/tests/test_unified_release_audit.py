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
from unittest import mock

from scripts.audit_unified_release import (
    EXPECTED_BACKEND_PRIORITY,
    audit_algorithm,
    audit_manifest,
    audit_physical_observations,
    audit_production_evidence,
    audit_stage_campaign,
    sha256_file,
    validate_backend_selection,
    validate_r0_raw_result,
    validate_r0_repeat_independence,
    validate_tpacket_receipt,
    verify_remote_evidence_manifest,
)
from hft_mgbs.stage_evidence import canonical_json_bytes, load_contract
from tests.test_stage_evidence import (
    campaign as valid_stage_campaign,
    digest,
    dual_backend_campaign,
    identity_manifests,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "release_manifest_v2.json"


def seal_stage_campaign(root: Path, receipts):
    """Materialize a stage campaign exactly as the unified auditor consumes it."""

    references = []
    runtime_hashes = {}
    for index, original in enumerate(receipts):
        receipt = copy.deepcopy(original)
        run = root / f"run-{index}"
        run.mkdir()
        backend = receipt["backend"]
        capture_binary = f"capture-binary-frozen:{backend}\n".encode("utf-8")
        receipt["identity"]["capture_binary_sha256"] = hashlib.sha256(
            capture_binary
        ).hexdigest()
        receipt["identity_manifests"] = identity_manifests(
            receipt["stage"], backend, receipt["identity"]
        )
        runtime_hashes[receipt.get("backend_role", backend)] = receipt[
            "identity"
        ]["runtime_manifest_sha256"]
        if receipt["stage"].startswith("r4_"):
            for window in receipt["windows"]:
                window["runtime_manifest_sha256"] = receipt["identity"][
                    "runtime_manifest_sha256"
                ]
        bound_files = {
            "code_manifest.json": canonical_json_bytes(
                receipt["identity_manifests"]["code"]
            ),
            "input_manifest.json": canonical_json_bytes(
                receipt["identity_manifests"]["input"]
            ),
            "stage_config.json": canonical_json_bytes(
                receipt["identity_manifests"]["stage_config"]
            ),
            "runtime_manifest.json": canonical_json_bytes(
                receipt["identity_manifests"]["runtime"]
            ),
            "model_manifest.json": canonical_json_bytes(
                receipt["identity_manifests"]["model"]
            ),
            "capture_binary.sha256": capture_binary,
            "raw-counters.json": json.dumps(
                {"run_index": index}, sort_keys=True
            ).encode("utf-8"),
        }
        for name, content in bound_files.items():
            (run / name).write_bytes(content)
        evidence_manifest = run / "evidence_sha256_complete.txt"
        evidence_manifest.write_text(
            "".join(
                f"{sha256_file(run / name)}  {name}\n"
                for name in sorted(bound_files)
            ),
            encoding="utf-8",
        )
        receipt["identity"]["evidence_manifest_sha256"] = sha256_file(
            evidence_manifest
        )
        receipt_path = run / "stage_receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, sort_keys=True), encoding="utf-8"
        )
        references.append(
            {
                "stage": receipt["stage"],
                "receipt": {
                    "path": f"/run-{index}/stage_receipt.json",
                    "sha256": sha256_file(receipt_path),
                },
                "evidence_manifest": {
                    "path": f"/run-{index}/evidence_sha256_complete.txt",
                    "sha256": sha256_file(evidence_manifest),
                },
            }
        )
    return references, runtime_hashes


class UnifiedReleaseAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_current_state_is_complete_audit_but_not_a_release(self):
        result = audit_manifest(MANIFEST_PATH, copy.deepcopy(self.manifest))

        self.assertTrue(result["audit_complete"])
        self.assertFalse(result["offline_algorithm_candidate_accepted"])
        self.assertFalse(result["algorithm_search_qualified"])
        self.assertFalse(result["algorithm_campaign_qualified"])
        self.assertTrue(result["capture_contract_qualified"])
        self.assertTrue(result["capture_backend_feasible_set_empty"])
        self.assertFalse(result["physical_r0_qualified"])
        self.assertFalse(result["runtime_identity_current"])
        self.assertFalse(result["full_pipeline_qualified"])
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["final_pareto_eligible"])
        self.assertIsNone(result["derived_production_pareto_metrics"])
        self.assertFalse(result["derived_production_pareto_metrics_available"])
        self.assertNotIn("production_pareto_metrics", result)
        self.assertEqual(
            result["physical_r0_identity_summary"]["run_bundle_identities"], []
        )
        self.assertIn("runtime_identity.unverified", result["errors"])
        self.assertIn("stage.campaign.pending", result["errors"])
        self.assertIn(
            "algorithm.optimality.recomputed_not_accepted", result["errors"]
        )
        self.assertIn("algorithm_campaign.receipt.reference", result["errors"])

    def test_complete_sealed_candidate_reaches_pareto_ingestion_only(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["deployment_candidate_id"] = "A09__native_xdp_candidate"
        manifest["claimed_final_state"].update(
            {
                "candidate_evidence_accepted": True,
                "full_pipeline_qualified": True,
                "production_release_accepted": False,
                "final_pareto_eligible": False,
                "final_pareto_ingestion_allowed": True,
            }
        )
        identity = {
            "run_bundle_identities": ["1" * 64, "2" * 64, "3" * 64],
            "generator_run_identities": ["4" * 64, "5" * 64, "6" * 64],
            "hardware_identity_sha256": ["7" * 64] * 3,
            "backends": ["native_af_xdp_forced_zerocopy"] * 3,
            "contracts": ["r0"] * 3,
        }
        production = {
            name: True
            for name in (
                "runtime_identity",
                "resources",
                "key_flow",
                "fallback",
                "r1",
                "r2",
                "r3",
                "r4_24h",
                "r4_72h",
            )
        }
        production["derived_production_pareto_metrics"] = {
            "name": "A09",
            "throughput_mpps": 12.0,
        }
        production["stage_campaign_blockers"] = []

        with mock.patch(
            "scripts.audit_unified_release.audit_algorithm",
            return_value=(True, True),
        ), mock.patch(
            "scripts.audit_unified_release.verify_algorithm_campaign_gate",
            return_value={
                "qualified": True,
                "winner": "A09",
                "contract_sha256": "a" * 64,
                "receipt_sha256": "b" * 64,
                "projection_sha256": "c" * 64,
                "errors": [],
            },
        ), mock.patch(
            "scripts.audit_unified_release.audit_capture_configs",
            return_value=True,
        ), mock.patch(
            "scripts.audit_unified_release.audit_physical_observations",
            return_value=(True, True, {}, identity),
        ), mock.patch(
            "scripts.audit_unified_release.audit_production_evidence",
            return_value=production,
        ):
            result = audit_manifest(MANIFEST_PATH, manifest)

        self.assertEqual(result["candidate_id"], "A09__native_xdp_candidate")
        self.assertEqual(result["algorithm_id"], "A09")
        self.assertTrue(result["candidate_evidence_accepted"])
        self.assertTrue(result["full_pipeline_qualified"])
        self.assertTrue(result["final_pareto_ingestion_allowed"])
        self.assertEqual(
            result["derived_production_pareto_metrics"]["name"],
            "A09__native_xdp_candidate",
        )
        self.assertFalse(result["selection_performed"])
        self.assertIsNone(result["selected_candidate"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["final_pareto_eligible"])
        self.assertEqual(result["errors"], [])

    def test_fabricated_algorithm_acceptance_is_rejected(self):
        search = json.loads(
            (ROOT / "configs" / "algorithm_search_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        frozen = json.loads(
            (ROOT / "configs" / "current_algorithm_optimality_audit_v1.json")
            .read_text(encoding="utf-8")
        )
        frozen["accepted"] = True
        frozen["algorithm_only_practical_optimum_proven"] = True
        errors = []

        algorithm_ok, offline_ok = audit_algorithm(
            search, release, frozen, errors
        )

        self.assertFalse(algorithm_ok)
        self.assertFalse(offline_ok)
        self.assertIn("algorithm.optimality.fabricated_acceptance", errors)
        self.assertIn("algorithm.optimality.frozen_drift", errors)

    def test_algorithm_audit_drift_is_rejected(self):
        search = json.loads(
            (ROOT / "configs" / "algorithm_search_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        frozen = json.loads(
            (ROOT / "configs" / "current_algorithm_optimality_audit_v1.json")
            .read_text(encoding="utf-8")
        )
        frozen["paired_metric_complete_candidate_count"] = 10
        errors = []

        algorithm_ok, offline_ok = audit_algorithm(
            search, release, frozen, errors
        )

        self.assertFalse(algorithm_ok)
        self.assertFalse(offline_ok)
        self.assertIn("algorithm.optimality.frozen_drift", errors)

    def test_algorithm_winner_mismatch_is_rejected(self):
        search = json.loads(
            (ROOT / "configs" / "algorithm_search_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        frozen = json.loads(
            (ROOT / "configs" / "current_algorithm_optimality_audit_v1.json")
            .read_text(encoding="utf-8")
        )
        frozen["confirmatory_practical_winner"] = "A10"
        errors = []

        algorithm_ok, offline_ok = audit_algorithm(
            search, release, frozen, errors
        )

        self.assertFalse(algorithm_ok)
        self.assertFalse(offline_ok)
        self.assertIn("algorithm.optimality.winner_mismatch", errors)

    def test_algorithm_optimality_artifact_hash_drift_is_fail_closed(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["config_artifacts"]["algorithm_optimality_audit"][
            "sha256"
        ] = "0" * 64

        result = audit_manifest(MANIFEST_PATH, manifest)

        self.assertFalse(result["evidence_integrity_qualified"])
        self.assertFalse(result["accepted"])
        self.assertIn(
            "config.algorithm_optimality_audit.sha256", result["errors"]
        )

    def test_cli_runs_directly_from_project_root_without_pythonpath(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "unified-audit.json"
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/audit_unified_release.py",
                    "configs/release_manifest_v2.json",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertTrue(result["audit_complete"])
            self.assertFalse(result["production_release_accepted"])

    def test_config_hash_drift_is_fail_closed(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["config_artifacts"]["algorithm_search"]["sha256"] = "0" * 64

        result = audit_manifest(MANIFEST_PATH, manifest)

        self.assertFalse(result["evidence_integrity_qualified"])
        self.assertFalse(result["accepted"])
        self.assertIn("config.algorithm_search.sha256", result["errors"])

    def test_input_cannot_promote_itself_to_final_pareto(self):
        manifest = copy.deepcopy(self.manifest)
        for name in manifest["claimed_final_state"]:
            manifest["claimed_final_state"][name] = True

        result = audit_manifest(MANIFEST_PATH, manifest)

        self.assertFalse(result["accepted"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])
        self.assertIn(
            "manifest.claim.production_release_accepted", result["errors"]
        )

    def test_missing_remote_receipts_are_not_optional(self):
        result = audit_manifest(MANIFEST_PATH, copy.deepcopy(self.manifest))

        self.assertIn("physical.0.unverified", result["errors"])
        self.assertIn("physical.3.unverified", result["errors"])
        self.assertFalse(result["host_restoration_qualified"])

    def test_legacy_key_flow_summary_cannot_bypass_stage_campaign(self):
        payload = {
            "candidate_id": "A09",
            "diagnostic_only": False,
            "qualified": True,
            "run_bundle_identity": "bundle-1",
            "key_flow_total": 0,
            "key_flow_covered": 0,
            "key_flow_coverage": 1.0,
            "key_flow_coverage_min_per_window": 1.0,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence" / "key.json"
            path.parent.mkdir(parents=True)
            encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
            path.write_bytes(encoded)
            reference = {
                "path": "/evidence/key.json",
                "sha256": hashlib.sha256(encoded).hexdigest(),
            }
            manifest = copy.deepcopy(self.manifest)
            manifest["production_evidence"]["key_flow"] = {
                "status": "qualified",
                "artifact": reference,
            }
            errors = []
            hashes = {}

            result = audit_production_evidence(
                manifest,
                json.loads(
                    (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                        encoding="utf-8"
                    )
                ),
                root,
                errors,
                hashes,
            )

        self.assertFalse(result["key_flow"])
        self.assertIn("stage.campaign.pending", errors)

    def test_tpacket_nan_and_boolean_metrics_are_rejected(self):
        receipt = {
            "schema_version": 1,
            "scope": "tpacket_v3_breakthrough_r0_acceptance",
            "candidate_id": "B2_TEST",
            "r0_capture_only_qualified": False,
            "full_pipeline_qualified": False,
            "final_pareto_ingestion_allowed": False,
            "restoration_verified": True,
            "offered_mpps_sum": float("nan"),
            "synthetic_rx_min_full_epoch_mpps": 2.7,
            "p99_us": True,
            "p999_us": 126.0,
            "host_cpu_fraction": 0.3,
            "capture_memory_fraction": 0.01,
            "offered_packets": 100,
            "synthetic_test_packets": 100,
            "offered_received_gap": 0,
            "rx_discards_delta": 0,
            "packet_socket_drops": 0,
            "packet_socket_freeze_queue_count": 0,
            "loss_accounting_exact": True,
            "generator_12mpps_gate_qualified": False,
            "capture_rate_12mpps_gate_qualified": False,
            "loss_gate_qualified": True,
            "latency_gate_qualified": False,
            "resource_gate_qualified": True,
            "irq_assignment_verified": True,
            "irq_affinity_stable": True,
            "irq_restoration_verified": True,
            "ring_restoration_verified": True,
            "coalesce_restoration_verified": True,
            "links_restored": True,
            "pktgen_module_unloaded": True,
            "runner_exit_status": 0,
            "synthetic_rx_full_epoch_windows": 15,
        }
        errors = []

        validate_tpacket_receipt(receipt, False, errors, "physical.0")

        self.assertIn("physical.0.offered_mpps_sum", errors)
        self.assertIn("physical.0.p99_us", errors)

    @staticmethod
    def _tpacket_receipt(candidate_id="B_TEST", offered_mpps=12.1):
        return {
            "schema_version": 1,
            "scope": "tpacket_v3_breakthrough_r0_acceptance",
            "candidate_id": candidate_id,
            "offered_packets": 181_500_000,
            "offered_mpps_sum": offered_mpps,
            "synthetic_test_packets": 181_500_000,
            "offered_received_gap": 0,
            "rx_discards_delta": 0,
            "packet_socket_drops": 0,
            "packet_socket_freeze_queue_count": 0,
            "loss_accounting_exact": True,
            "synthetic_rx_min_full_epoch_mpps": offered_mpps,
            "synthetic_rx_full_epoch_windows": 15,
            "p99_us": 90.0,
            "p999_us": 120.0,
            "host_cpu_fraction": 0.3,
            "capture_memory_fraction": 0.01,
            "generator_12mpps_gate_qualified": True,
            "capture_rate_12mpps_gate_qualified": True,
            "loss_gate_qualified": True,
            "latency_gate_qualified": True,
            "resource_gate_qualified": True,
            "irq_assignment_verified": True,
            "irq_affinity_stable": True,
            "irq_restoration_verified": True,
            "ring_restoration_verified": True,
            "coalesce_restoration_verified": True,
            "links_restored": True,
            "pktgen_module_unloaded": True,
            "runner_exit_status": 0,
            "restoration_verified": True,
            "r0_capture_only_qualified": True,
            "full_pipeline_qualified": False,
            "final_pareto_ingestion_allowed": False,
        }

    @staticmethod
    def _write_observation(root, index, receipt):
        run = root / "remote" / f"run-{index}"
        run.mkdir(parents=True)
        acceptance = run / "acceptance.json"
        acceptance.write_text(
            json.dumps(receipt, sort_keys=True), encoding="utf-8"
        )
        raw = run / "raw.txt"
        raw.write_text(f"run={index}\n", encoding="utf-8")
        evidence_manifest = run / "evidence_sha256_complete.txt"
        evidence_manifest.write_text(
            f"{sha256_file(raw)}  raw.txt\n", encoding="utf-8"
        )
        return {
            "id": f"run-{index}",
            "kind": "tpacket_breakthrough_acceptance",
            "acceptance": {
                "path": f"/remote/run-{index}/acceptance.json",
                "sha256": sha256_file(acceptance),
            },
            "evidence_manifest": {
                "path": f"/remote/run-{index}/evidence_sha256_complete.txt",
                "sha256": sha256_file(evidence_manifest),
            },
            "expected_r0_qualified": True,
            "production_scope": True,
            "counts_toward_r0": True,
        }

    def test_tpacket_declared_gates_must_match_raw_metrics(self):
        receipt = self._tpacket_receipt(offered_mpps=2.794217)
        receipt["synthetic_rx_min_full_epoch_mpps"] = 2.790743
        errors = []

        validate_tpacket_receipt(receipt, True, errors, "physical.0")

        self.assertIn("physical.0.generator_12mpps_gate_qualified", errors)
        self.assertIn("physical.0.capture_rate_12mpps_gate_qualified", errors)
        self.assertIn("physical.0.derived_r0_state", errors)

    def test_duplicate_receipt_cannot_count_as_independent_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observation = self._write_observation(
                root, 0, self._tpacket_receipt()
            )
            observations = []
            for index in range(3):
                duplicate = copy.deepcopy(observation)
                duplicate["id"] = f"run-{index}"
                observations.append(duplicate)
            manifest = copy.deepcopy(self.manifest)
            manifest["physical_observations"] = observations
            errors = []

            qualified, restored, _, _ = audit_physical_observations(
                manifest, {}, root, errors
            )

        self.assertFalse(qualified)
        self.assertTrue(restored)
        self.assertIn("physical.independent_runs", errors)

    def test_tpacket_diagnostic_receipts_never_count_as_production_r0(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observations = [
                self._write_observation(
                    root, index, self._tpacket_receipt(f"B_TEST_{index}")
                )
                for index in range(3)
            ]
            manifest = copy.deepcopy(self.manifest)
            manifest["physical_observations"] = observations
            errors = []

            qualified, restored, _, _ = audit_physical_observations(
                manifest, {}, root, errors
            )

        self.assertFalse(qualified)
        self.assertTrue(restored)
        self.assertIn("physical.0.diagnostic_not_countable", errors)

    def test_three_1m_contracts_cannot_satisfy_12m_r0(self):
        manifest = copy.deepcopy(self.manifest)
        observation = copy.deepcopy(manifest["physical_observations"][0])
        observation["counts_toward_r0"] = True
        observation["production_scope"] = True
        manifest["physical_observations"] = [
            {**copy.deepcopy(observation), "id": f"one-mpps-{index}"}
            for index in range(3)
        ]
        errors = []

        qualified, _, _, _ = audit_physical_observations(
            manifest, self._loaded_configs(), None, errors
        )

        self.assertFalse(qualified)
        self.assertIn("physical.0.unverified", errors)

    def test_backend_priority_policy_is_frozen_and_xdp_first(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["audit_policy"]["backend_priority"] = list(
            reversed(EXPECTED_BACKEND_PRIORITY)
        )

        result = audit_manifest(MANIFEST_PATH, manifest)

        self.assertFalse(result["accepted"])
        self.assertIn("manifest.backend_priority", result["errors"])

    @staticmethod
    def _backend_selection_receipt(backend="dpdk_multiqueue_rss_tss"):
        digest = "a" * 64
        receipt = {
            "schema_version": 1,
            "scope": "hft_capture_backend_selection_receipt",
            "candidate_id": "R0_PRODUCTION",
            "frozen_contract_sha256": digest,
            "preferred_backend": "native_af_xdp_forced_zerocopy",
            "selected_backend": backend,
            "independent_generator_verified": True,
            "generator_shares_capture_adapter_packet_budget": False,
            "restoration_verified": True,
            "hardware_identity_sha256": "b" * 64,
            "capture_hardware_identity_sha256": "b" * 64,
            "generator_hardware_identity_sha256": "c" * 64,
            "run_bundle_identity": "d" * 64,
            "generator_run_identity": "e" * 64,
            "native_xdp_probe_attempted": True,
            "af_xdp_force_zerocopy_requested": True,
            "native_af_xdp_qualified": False,
            "dpdk_multiqueue_rss_tss_verified": True,
            "fallback_reason": "native_xdp_unavailable",
            "input_sha256": {
                "hardware_identity.json": "1" * 64,
                "generator_topology.json": "2" * 64,
                "xdp_probe_acceptance.json": "3" * 64,
                "dpdk_capability.json": "4" * 64,
                "evidence_inventory.json": "5" * 64,
                "result.json": "6" * 64,
                "restoration_ledger.json": "7" * 64,
            },
        }
        return receipt

    def test_dpdk_fallback_without_xdp_probe_is_rejected(self):
        receipt = self._backend_selection_receipt()
        receipt["native_xdp_probe_attempted"] = False
        errors = []

        validate_backend_selection(
            receipt,
            "dpdk_multiqueue_rss_tss",
            errors,
            "physical.0.backend_selection",
            contract={"candidate_id": "R0_PRODUCTION"},
            contract_sha256="a" * 64,
        )

        self.assertIn("physical.0.backend_selection.dpdk_fallback", errors)

    def test_raw_r0_below_12m_is_rejected_even_if_flags_claim_success(self):
        contract = {
            "candidate_id": "R0_PRODUCTION",
            "min_run_duration_s": 15,
            "expected_runner_sha256": "1" * 64,
            "expected_binary_sha256": "2" * 64,
            "expected_validator_sha256": "3" * 64,
            "expected_composer_sha256": "4" * 64,
            "latency_sampling": {
                "min_samples": 10000,
                "stride_packets": 1024,
                "timestamp_source": "dpdk_tsc_embedded_tx_rx_v1",
            },
        }
        raw = {
            "schema_version": 1,
            "scope": "r0_production_capture_only_raw_v1",
            "evidence_semantics": "raw_counter_snapshot_v1",
            "self_qualification_trusted": False,
            "candidate_id": "R0_PRODUCTION",
            "frozen_contract_sha256": "a" * 64,
            "backend": "dpdk_multiqueue_rss_tss",
            "target_mpps": 12.0,
            "frame_size_bytes": 64,
            "errors": [],
            "full_pipeline_qualified": False,
            "final_pareto_ingestion_allowed": False,
            "runner_sha256": "1" * 64,
            "binary_sha256": "2" * 64,
            "validator_sha256": "3" * 64,
            "composer_sha256": "4" * 64,
            "observed_tx_mpps_min_1s": 12.1,
            "observed_rx_mpps_min_1s": 11.9,
            "duration_s": 15.1,
            "offered_packets": 181_500_000,
            "received_packets": 181_500_000,
            "offered_received_gap": 0,
            "capture_stats_delta": {"imissed": 0, "ierrors": 0, "rx_nombuf": 0},
            "replay_stats_delta": {"oerrors": 0},
            "rate_window_alignment": "shared_monotonic_epoch_fixed_1s_v1",
            "tx_rate_full_windows": 15,
            "rx_rate_full_windows": 15,
            "end_to_end_latency_us": {"samples": 12000, "p99": 80.0, "p999": 420.0},
            "latency_sample_stride": 1024,
            "latency_timestamp_source": "dpdk_tsc_embedded_tx_rx_v1",
            "dpdk_rss_verified": True,
            "dpdk_tss_verified": True,
            "rx_queue_count": 8,
            "tx_queue_count": 8,
        }
        errors = []

        validate_r0_raw_result(
            raw,
            "dpdk_multiqueue_rss_tss",
            contract,
            "a" * 64,
            self.manifest["audit_policy"],
            errors,
            "physical.0.raw_result",
        )

        self.assertIn("physical.0.raw_result.rate_duration_gate", errors)

    def test_duplicate_generator_identity_is_not_an_independent_repeat(self):
        errors = []
        qualified = validate_r0_repeat_independence(
            3,
            ["p1", "p2", "p3"],
            ["1" * 64, "2" * 64, "3" * 64],
            ["4" * 64, "5" * 64, "6" * 64],
            ["7" * 64, "8" * 64, "9" * 64],
            ["a" * 64, "a" * 64, "b" * 64],
            ["c" * 64] * 3,
            ["dpdk_multiqueue_rss_tss"] * 3,
            ["contract"] * 3,
            errors,
        )

        self.assertFalse(qualified)
        self.assertIn("physical.independent_runs", errors)

    def test_generic_stage_qualified_flag_cannot_release(self):
        payload = {
            "candidate_id": "A09",
            "diagnostic_only": False,
            "qualified": True,
            "run_bundle_identity": "bundle-r4",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "stage.json"
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            manifest = copy.deepcopy(self.manifest)
            manifest["production_evidence"]["r4_24h"] = {
                "status": "qualified",
                "artifact": {
                    "path": "/stage.json",
                    "sha256": sha256_file(artifact),
                },
            }
            errors = []
            result = audit_production_evidence(
                manifest,
                self._loaded_configs()["release_candidate"],
                root,
                errors,
                {},
            )

        self.assertFalse(result["r4_24h"])
        self.assertIn("stage.campaign.pending", errors)

    def test_sealed_stage_campaign_recomputes_pareto_metrics(self):
        contract = load_contract(
            ROOT / "configs" / "production_stage_receipt_contract_v1.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            references = []
            runtime_manifest_hash = None
            for index, receipt in enumerate(valid_stage_campaign()):
                run = root / f"run-{index}"
                run.mkdir()
                receipt["backend"] = "dpdk_multiqueue_rss_tss"
                capture_binary = b"capture-binary-frozen\n"
                receipt["identity"]["capture_binary_sha256"] = hashlib.sha256(
                    capture_binary
                ).hexdigest()
                receipt["identity_manifests"] = identity_manifests(
                    receipt["stage"], receipt["backend"], receipt["identity"]
                )
                if receipt["stage"].startswith("r4_"):
                    for window in receipt["windows"]:
                        window["runtime_manifest_sha256"] = receipt["identity"][
                            "runtime_manifest_sha256"
                        ]
                bound_files = {
                    "code_manifest.json": canonical_json_bytes(
                        receipt["identity_manifests"]["code"]
                    ),
                    "input_manifest.json": canonical_json_bytes(
                        receipt["identity_manifests"]["input"]
                    ),
                    "stage_config.json": canonical_json_bytes(
                        receipt["identity_manifests"]["stage_config"]
                    ),
                    "runtime_manifest.json": canonical_json_bytes(
                        receipt["identity_manifests"]["runtime"]
                    ),
                    "model_manifest.json": canonical_json_bytes(
                        receipt["identity_manifests"]["model"]
                    ),
                    "capture_binary.sha256": capture_binary,
                    "raw-counters.json": json.dumps(
                        {"run_index": index}, sort_keys=True
                    ).encode("utf-8"),
                }
                for name, content in bound_files.items():
                    (run / name).write_bytes(content)
                identity_names = {
                    "code_sha256": "code_manifest.json",
                    "input_sha256": "input_manifest.json",
                    "stage_config_sha256": "stage_config.json",
                    "runtime_manifest_sha256": "runtime_manifest.json",
                    "model_sha256": "model_manifest.json",
                    "capture_binary_sha256": "capture_binary.sha256",
                }
                for identity_name, filename in identity_names.items():
                    self.assertEqual(
                        receipt["identity"][identity_name],
                        sha256_file(run / filename),
                    )
                runtime_manifest_hash = receipt["identity"][
                    "runtime_manifest_sha256"
                ]
                if receipt["stage"].startswith("r4_"):
                    for window in receipt["windows"]:
                        window["runtime_manifest_sha256"] = runtime_manifest_hash
                evidence_manifest = run / "evidence_sha256_complete.txt"
                evidence_manifest.write_text(
                    "".join(
                        f"{sha256_file(run / name)}  {name}\n"
                        for name in sorted(bound_files)
                    ),
                    encoding="utf-8",
                )
                receipt["identity"]["evidence_manifest_sha256"] = sha256_file(
                    evidence_manifest
                )
                receipt_path = run / "stage_receipt.json"
                receipt_path.write_text(
                    json.dumps(receipt, sort_keys=True), encoding="utf-8"
                )
                references.append(
                    {
                        "stage": receipt["stage"],
                        "receipt": {
                            "path": f"/run-{index}/stage_receipt.json",
                            "sha256": sha256_file(receipt_path),
                        },
                        "evidence_manifest": {
                            "path": f"/run-{index}/evidence_sha256_complete.txt",
                            "sha256": sha256_file(evidence_manifest),
                        },
                    }
                )
            errors = []
            result = audit_stage_campaign(
                {"stage_campaign": {"status": "qualified", "receipts": references}},
                contract,
                root,
                errors,
                {},
                physical_r0_qualified=True,
                physical_identity_summary={
                    "backends": ["dpdk_multiqueue_rss_tss"] * 3,
                    "hardware_identity_sha256": [digest(1)] * 3,
                },
                runtime_manifest_sha256=runtime_manifest_hash,
            )

        self.assertTrue(result["qualified"], errors[:10])
        self.assertTrue(all(result["stage_qualified"].values()))
        self.assertEqual(
            result["derived_production_pareto_metrics"]["name"], "A09"
        )
        self.assertGreaterEqual(
            result["derived_production_pareto_metrics"]["throughput_mpps"],
            10.0,
        )

    @staticmethod
    def _dual_backend_identity_summary():
        primary = "native_af_xdp_forced_zerocopy"
        fallback = "dpdk_multiqueue_rss_tss"
        return {
            "backends": [primary, fallback],
            "primary_backend": primary,
            "fallback_backend": fallback,
            "hardware_identity_sha256": [digest(1)],
        }

    def _audit_sealed_dual_backend_campaign(
        self, root: Path, receipts, *, physical_r0_qualified=True
    ):
        references, runtime_hashes = seal_stage_campaign(root, receipts)
        errors = []
        result = audit_stage_campaign(
            {"stage_campaign": {"status": "qualified", "receipts": references}},
            load_contract(
                ROOT / "configs" / "production_stage_receipt_contract_v1.json"
            ),
            root,
            errors,
            {},
            physical_r0_qualified=physical_r0_qualified,
            physical_identity_summary=self._dual_backend_identity_summary(),
            runtime_manifest_sha256=runtime_hashes["primary"],
        )
        return result, errors

    def test_sealed_dual_backend_stage_campaign_uses_r0_role_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            result, errors = self._audit_sealed_dual_backend_campaign(
                Path(directory), dual_backend_campaign()
            )

        self.assertTrue(result["qualified"], errors[:10])
        self.assertTrue(all(result["stage_qualified"].values()))
        self.assertEqual(
            result["derived_production_pareto_metrics"]["name"], "A09"
        )

    def test_sealed_dual_backend_stage_campaign_rejects_missing_fallback(self):
        receipts = dual_backend_campaign()
        for index, receipt in enumerate(receipts):
            if receipt["stage"] == "r1" and receipt["backend_role"] == "fallback":
                del receipts[index]
                break
        with tempfile.TemporaryDirectory() as directory:
            result, errors = self._audit_sealed_dual_backend_campaign(
                Path(directory), receipts
            )

        self.assertFalse(result["qualified"])
        self.assertIn(
            "stage.campaign.recompute.campaign.r1.fallback.repeat_count", errors
        )

    def test_sealed_dual_backend_stage_campaign_rejects_role_swap(self):
        receipts = dual_backend_campaign()
        receipts[0]["backend_role"], receipts[1]["backend_role"] = (
            receipts[1]["backend_role"],
            receipts[0]["backend_role"],
        )
        with tempfile.TemporaryDirectory() as directory:
            result, errors = self._audit_sealed_dual_backend_campaign(
                Path(directory), receipts
            )

        self.assertFalse(result["qualified"])
        self.assertIn(
            "stage.campaign.recompute.campaign.receipt.0.backend_role_binding",
            errors,
        )
        self.assertIn(
            "stage.campaign.recompute.campaign.receipt.1.backend_role_binding",
            errors,
        )

    def test_dual_backend_stage_campaign_cannot_bypass_pending_r0_trust(self):
        with tempfile.TemporaryDirectory() as directory:
            result, errors = self._audit_sealed_dual_backend_campaign(
                Path(directory),
                dual_backend_campaign(),
                physical_r0_qualified=False,
            )

        self.assertFalse(result["qualified"])
        self.assertIn("stage.campaign.physical_r0_binding", errors)

    def test_stage_receipt_must_bind_its_evidence_manifest(self):
        contract = load_contract(
            ROOT / "configs" / "production_stage_receipt_contract_v1.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            run.mkdir()
            raw = run / "raw.json"
            raw.write_text("{}\n", encoding="utf-8")
            evidence_manifest = run / "evidence_sha256_complete.txt"
            evidence_manifest.write_text(
                f"{sha256_file(raw)}  {raw.name}\n", encoding="utf-8"
            )
            receipt = valid_stage_campaign()[0]
            receipt["identity"]["evidence_manifest_sha256"] = "f" * 64
            receipt_path = run / "stage_receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            errors = []
            result = audit_stage_campaign(
                {
                    "stage_campaign": {
                        "status": "qualified",
                        "receipts": [
                            {
                                "stage": receipt["stage"],
                                "receipt": {
                                    "path": "/run/stage_receipt.json",
                                    "sha256": sha256_file(receipt_path),
                                },
                                "evidence_manifest": {
                                    "path": "/run/evidence_sha256_complete.txt",
                                    "sha256": sha256_file(evidence_manifest),
                                },
                            }
                        ],
                    }
                },
                contract,
                root,
                errors,
                {},
                physical_r0_qualified=True,
                physical_identity_summary={
                    "backends": ["dpdk"] * 3,
                    "hardware_identity_sha256": [digest(1)] * 3,
                },
                runtime_manifest_sha256=digest(4),
            )

        self.assertFalse(result["qualified"])
        self.assertIn("stage.campaign.0.evidence_manifest_binding", errors)

    def test_evidence_hash_failure_does_not_hide_valid_restoration_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            run.mkdir()
            selection = run / "backend_selection.json"
            selection.write_text("{}\n", encoding="utf-8")
            ledger = run / "restoration_ledger.json"
            ledger.write_text(
                json.dumps(
                    [
                        {"step": "child_stopped", "status": 0, "ok": True},
                        {"step": "final_state_verification", "status": 0, "ok": True},
                    ]
                ),
                encoding="utf-8",
            )
            inventory = run / "evidence_inventory.json"
            required = ["backend_selection.json", "restoration_ledger.json"]
            inventory.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "required": required,
                        "present": required,
                        "missing": [],
                        "empty_required": [],
                        "restoration_verified": True,
                        "evidence_complete_before_hash": True,
                    }
                ),
                encoding="utf-8",
            )
            evidence = run / "evidence_sha256_complete.txt"
            evidence.write_text(
                "".join(
                    f"{sha256_file(path)}  {path.name}\n"
                    for path in (selection, ledger, inventory)
                ),
                encoding="utf-8",
            )
            errors = []
            verified, restored = verify_remote_evidence_manifest(
                {"path": "/run/evidence_sha256_complete.txt", "sha256": sha256_file(evidence)},
                root,
                "physical.0.evidence_manifest",
                errors,
                {},
                require_release_inventory=True,
                required_hash_entries={"backend_selection.json": "f" * 64},
                required_restoration_steps={"child_stopped", "final_state_verification"},
            )
            ledger.write_text(
                json.dumps(
                    [{"step": "child_stopped", "status": 0, "ok": True}]
                ),
                encoding="utf-8",
            )
            evidence.write_text(
                "".join(
                    f"{sha256_file(path)}  {path.name}\n"
                    for path in (selection, ledger, inventory)
                ),
                encoding="utf-8",
            )
            restoration_errors = []
            restoration_verified, restoration_ok = verify_remote_evidence_manifest(
                {"path": "/run/evidence_sha256_complete.txt", "sha256": sha256_file(evidence)},
                root,
                "physical.1.evidence_manifest",
                restoration_errors,
                {},
                require_release_inventory=True,
                required_hash_entries={
                    "backend_selection.json": sha256_file(selection)
                },
                required_restoration_steps={
                    "child_stopped",
                    "final_state_verification",
                },
            )

        self.assertFalse(verified)
        self.assertTrue(restored)
        self.assertIn(
            "physical.0.evidence_manifest.required_hash.backend_selection.json",
            errors,
        )
        self.assertFalse(restoration_verified)
        self.assertFalse(restoration_ok)
        self.assertIn(
            "physical.1.evidence_manifest.restoration_ledger_status",
            restoration_errors,
        )

    @classmethod
    def _loaded_configs(cls):
        return {
            name: json.loads(
                (MANIFEST_PATH.parent / reference["path"]).read_text(
                    encoding="utf-8"
                )
            )
            for name, reference in cls.manifest["config_artifacts"].items()
        }


if __name__ == "__main__":
    unittest.main()

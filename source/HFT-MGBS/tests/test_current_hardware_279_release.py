from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hft_mgbs.current_hardware_279_release import (
    _load_policy,
    _raw_input_tree_snapshot,
    audit_current_hardware_stage_a,
    build_current_hardware_campaign_receipt,
    select_current_hardware_stage_b,
)
ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "configs" / "current_hardware_2_79_release_profile_v2.json"
POLICY = ROOT / "configs" / "current_hardware_2_79_two_stage_release_policy_v1.json"

_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "hft_current_279_v2_fixture", ROOT / "tests" / "test_current_hardware_279_v2.py"
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_FIXTURE_MODULE = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_FIXTURE_MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> dict[str, str]:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": path.name, "sha256": digest(path)}


class CurrentHardware279ReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixtures = []

    def tearDown(self):
        for fixture in reversed(self.fixtures):
            fixture.tearDown()
        self.temp.cleanup()

    def _fixture(self, candidate_id: str, backend: str):
        fixture = _FIXTURE_MODULE.CurrentHardware279V2Test(
            methodName="test_positive_raw_run_recomputes_and_remains_nonproduction"
        )
        fixture.setUp()
        fixture.candidate = candidate_id
        fixture.backend = backend
        self.fixtures.append(fixture)
        return fixture

    def _campaign(
        self,
        candidate_id: str,
        backend: str = "tpacket-v3-hash",
        variant_identity: str | None = None,
    ):
        variant_identity = candidate_id if variant_identity is None else variant_identity
        raw_refs = []
        raw_inputs = []
        campaign_id = None
        for mode in ("normal", "fallback"):
            for repeat in (1, 2, 3):
                fixture = self._fixture(candidate_id, backend)
                raw_input_path, raw_request = fixture.raw_fixture(mode, repeat)
                config_path = fixture.root / raw_request["artifacts"]["config"]["path"]
                raw_request["artifacts"]["config"] = write_json(
                    config_path, {"candidate_variant_identity": variant_identity}
                )
                bound_names = (
                    "runner", "config", "capture_binary", "model",
                    "runtime_manifest", "service_source", "engine_source",
                    "service_launcher",
                )
                binding = {
                    name: raw_request["artifacts"][name]["sha256"]
                    for name in bound_names
                }
                identity_path = fixture.root / raw_request["artifacts"]["identity_receipt"]["path"]
                identity = json.loads(identity_path.read_text(encoding="utf-8"))
                identity["release_artifact_sha256"] = binding
                raw_request["artifacts"]["identity_receipt"] = write_json(
                    identity_path, identity
                )
                diagnostic_path = fixture.root / raw_request["artifacts"]["diagnostic_receipt"]["path"]
                diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
                for field in (
                    "campaign_id", "candidate_id", "backend", "mode", "repeat_index",
                    "run_id", "generator_run_id", "generator_process_start_ticks",
                    "hardware_identity_sha256", "code_tree_sha256",
                ):
                    diagnostic[field] = identity[field]
                diagnostic["release_artifact_sha256"] = binding
                raw_request["artifacts"]["diagnostic_receipt"] = write_json(
                    diagnostic_path, diagnostic
                )
                evidence_manifest = fixture.root / raw_request["evidence_manifest"]["path"]
                entries = []
                for line in evidence_manifest.read_text(encoding="utf-8").splitlines():
                    _old_digest, name = line.split(None, 1)
                    observed = fixture.root / name.strip()
                    entries.append(f"{digest(observed)}  {name.strip()}")
                evidence_manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
                raw_request["evidence_manifest"]["sha256"] = digest(evidence_manifest)
                write_json(raw_input_path, raw_request)
                from hft_mgbs.current_hardware_279 import compose_current_hardware_raw_run_v2

                result = compose_current_hardware_raw_run_v2(PROFILE, raw_input_path)
                campaign_id = fixture.campaign
                raw_inputs.append(raw_input_path)
                source = self.root / f"release-{candidate_id}-{mode}-{repeat}.json"
                raw_refs.append(write_json(source, result))
        candidate_input = {
            "schema_version": 2,
            "scope": "hft_mgbs_current_hardware_2_79_candidate_input_v2",
            "profile_sha256": digest(PROFILE),
            "evidence_root": str(self.root),
            "campaign_id": campaign_id,
            "candidate_id": candidate_id,
            "backend": backend,
            "raw_runs": raw_refs,
        }
        input_path = self.root / f"{candidate_id}.candidate-input.json"
        write_json(input_path, candidate_input)
        from hft_mgbs.current_hardware_279 import compose_current_hardware_candidate_v2

        candidate_audit = compose_current_hardware_candidate_v2(PROFILE, input_path)
        audit_path = self.root / f"{candidate_id}.candidate-audit.json"
        write_json(audit_path, candidate_audit)
        receipt = build_current_hardware_campaign_receipt(
            POLICY, PROFILE, input_path, audit_path, raw_inputs
        )
        receipt_path = self.root / f"{candidate_id}.campaign-receipt.json"
        receipt_ref = write_json(receipt_path, receipt)
        stage_a_manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_stage_a_manifest_v1",
            "policy_sha256": digest(POLICY),
            "campaign_receipt": receipt_ref,
            "claimed_final_state": {
                "candidate_evidence_accepted": True,
                "full_pipeline_qualified": True,
                "selection_performed": False,
                "production_release_accepted": False,
                "final_pareto_ingestion_allowed": True,
                "accepted": False,
                "selected_candidate": None,
                "ten_mpps_or_line_rate_claim_allowed": False,
            },
        }
        stage_a_manifest_path = self.root / f"{candidate_id}.stage-a-manifest.json"
        write_json(stage_a_manifest_path, stage_a_manifest)
        unified = audit_current_hardware_stage_a(POLICY, stage_a_manifest_path)
        unified_path = self.root / f"{candidate_id}.unified-audit.json"
        write_json(unified_path, unified)
        return {
            "candidate_id": candidate_id,
            "receipt": receipt,
            "receipt_path": receipt_path,
            "raw_inputs": raw_inputs,
            "stage_a_manifest_path": stage_a_manifest_path,
            "unified": unified,
            "unified_path": unified_path,
        }

    def _stage_b_manifest(self, campaigns):
        candidates = []
        for item in campaigns:
            candidates.append(
                {
                    "candidate_id": item["candidate_id"],
                    "stage_a_manifest": {
                        "path": item["stage_a_manifest_path"].name,
                        "sha256": digest(item["stage_a_manifest_path"]),
                    },
                    "unified_candidate_evidence_audit": {
                        "path": item["unified_path"].name,
                        "sha256": digest(item["unified_path"]),
                    },
                    "campaign_receipt": {
                        "path": item["receipt_path"].name,
                        "sha256": digest(item["receipt_path"]),
                    },
                }
            )
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_stage_b_candidates_v1",
            "policy_sha256": digest(POLICY),
            "candidates": candidates,
            "claimed_final_state": {
                "selection_performed": len(candidates) >= 2,
                "production_release_accepted": len(candidates) >= 2,
                "current_hardware_operating_point_release_accepted": len(candidates) >= 2,
                "production_release_scope": (
                    "current_hardware_bcm57810_2.79_mpps_only"
                    if len(candidates) >= 2 else None
                ),
                "accepted": len(candidates) >= 2,
                "ten_mpps_or_line_rate_claim_allowed": False,
            },
        }
        path = self.root / "stage-b-candidates.json"
        write_json(path, manifest)
        return path

    def test_stage_a_recomputes_sealed_six_run_campaign_but_never_production(self):
        campaign = self._campaign("hash-candidate")
        result = campaign["unified"]
        self.assertTrue(result["candidate_evidence_accepted"], result["errors"])
        self.assertTrue(result["final_pareto_ingestion_allowed"])
        self.assertFalse(result["selection_performed"])
        self.assertIsNone(result["selected_candidate"])
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["verified_normal_run_count"], 3)
        self.assertEqual(result["verified_fallback_run_count"], 3)

    def test_stage_a_rejects_failed_run_even_if_receipt_flags_are_forged(self):
        campaign = self._campaign("forged-failed-normal")
        receipt = copy.deepcopy(campaign["receipt"])
        receipt["candidate_evidence_qualified"] = True
        receipt["full_pipeline_qualified"] = True
        receipt["normal_run_count"] = 3
        raw_input = campaign["raw_inputs"][0]
        failed = json.loads(raw_input.read_text(encoding="utf-8"))
        failed["profile_sha256"] = "0" * 64
        write_json(raw_input, failed)
        for ref in receipt["raw_run_inputs"]:
            if Path(ref["path"]) == raw_input.resolve():
                ref["sha256"] = digest(raw_input)
        write_json(campaign["receipt_path"], receipt)
        stage_manifest = json.loads(
            campaign["stage_a_manifest_path"].read_text(encoding="utf-8")
        )
        stage_manifest["campaign_receipt"] = {
            "path": campaign["receipt_path"].name,
            "sha256": digest(campaign["receipt_path"]),
        }
        write_json(campaign["stage_a_manifest_path"], stage_manifest)
        result = audit_current_hardware_stage_a(
            POLICY, campaign["stage_a_manifest_path"]
        )
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])
        self.assertTrue(any("raw_run_inputs.0.recompute" in error for error in result["errors"]))

    def test_stage_a_rejects_hash_drift_and_legacy_b1_b2_shape(self):
        campaign = self._campaign("tampered")
        unified = audit_current_hardware_stage_a(POLICY, campaign["stage_a_manifest_path"])
        self.assertTrue(unified["candidate_evidence_accepted"])
        receipt = json.loads(campaign["receipt_path"].read_text(encoding="utf-8"))
        receipt["raw_run_inputs"][0]["mode"] = "fallback"
        write_json(campaign["receipt_path"], receipt)
        stage_manifest = json.loads(
            campaign["stage_a_manifest_path"].read_text(encoding="utf-8")
        )
        stage_manifest["campaign_receipt"]["sha256"] = digest(campaign["receipt_path"])
        write_json(campaign["stage_a_manifest_path"], stage_manifest)
        identity_forged = audit_current_hardware_stage_a(
            POLICY, campaign["stage_a_manifest_path"]
        )
        self.assertFalse(identity_forged["candidate_evidence_accepted"])
        self.assertIn(
            "campaign_receipt.raw_run_inputs.0.identity", identity_forged["errors"]
        )
        campaign["receipt_path"].write_text("{}\n", encoding="utf-8")
        drifted = audit_current_hardware_stage_a(POLICY, campaign["stage_a_manifest_path"])
        self.assertFalse(drifted["candidate_evidence_accepted"])
        self.assertIn("stage_a.campaign_receipt.sha256", drifted["errors"])

        legacy_path = self.root / "legacy-b2.json"
        write_json(legacy_path, {"scope": "tpacket_breakthrough_acceptance", "accepted": True})
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_stage_a_manifest_v1",
            "policy_sha256": digest(POLICY),
            "campaign_receipt": {"path": legacy_path.name, "sha256": digest(legacy_path)},
            "claimed_final_state": {},
        }
        manifest_path = self.root / "legacy-stage-a.json"
        write_json(manifest_path, manifest)
        legacy = audit_current_hardware_stage_a(POLICY, manifest_path)
        self.assertFalse(legacy["candidate_evidence_accepted"])
        self.assertIn("campaign_receipt.scope", legacy["errors"])

    def test_stage_b_rehashes_both_layers_and_requires_two_evaluated_candidates(self):
        first = self._campaign("candidate-a", "tpacket-v3-hash")
        single_path = self._stage_b_manifest([first])
        single = select_current_hardware_stage_b(POLICY, single_path)
        self.assertFalse(single["production_release_accepted"])
        self.assertIn("stage_b.candidate_count_below_min:1<2", single["errors"])

        second = self._campaign("candidate-b", "tpacket-v3-qm")
        pair_path = self._stage_b_manifest([first, second])
        selected = select_current_hardware_stage_b(POLICY, pair_path)
        self.assertTrue(selected["production_release_accepted"], selected["errors"])
        self.assertTrue(selected["selection_performed"])
        self.assertIn(selected["champion_id"], {"candidate-a", "candidate-b"})
        self.assertEqual(selected["evaluated_candidate_count"], 2)

        first["unified_path"].write_text("{}\n", encoding="utf-8")
        drifted = select_current_hardware_stage_b(POLICY, pair_path)
        self.assertFalse(drifted["production_release_accepted"])
        self.assertTrue(any("unified.sha256" in error for error in drifted["errors"]))

    def test_stage_b_rejects_stage_a_that_forges_production_or_duplicate_receipt(self):
        first = self._campaign("candidate-a", "tpacket-v3-hash")
        second = self._campaign("candidate-b", "tpacket-v3-qm")
        unified = json.loads(first["unified_path"].read_text(encoding="utf-8"))
        unified["production_release_accepted"] = True
        write_json(first["unified_path"], unified)
        path = self._stage_b_manifest([first, second])
        result = select_current_hardware_stage_b(POLICY, path)
        self.assertFalse(result["production_release_accepted"])
        self.assertTrue(any("unified.recomputed" in error for error in result["errors"]))

        # One campaign cannot be counted twice under two candidate labels.
        first = self._campaign("candidate-c", "tpacket-v3-hash")
        manifest_path = self._stage_b_manifest([first, first])
        duplicated = select_current_hardware_stage_b(POLICY, manifest_path)
        self.assertFalse(duplicated["production_release_accepted"])
        self.assertIn("stage_b.duplicate_candidate_id", duplicated["errors"])
        self.assertIn("stage_b.duplicate_campaign_receipt", duplicated["errors"])

    def test_pending_configs_and_cli_are_fail_closed(self):
        pending_a = ROOT / "configs" / "current_hardware_2_79_stage_a_pending_v1.json"
        pending_b = ROOT / "configs" / "current_hardware_2_79_stage_b_pending_v1.json"
        stage_a = audit_current_hardware_stage_a(POLICY, pending_a)
        stage_b = select_current_hardware_stage_b(POLICY, pending_b)
        self.assertFalse(stage_a["candidate_evidence_accepted"])
        self.assertFalse(stage_b["production_release_accepted"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "audit.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/audit_current_hardware_279_release.py",
                    "--stage",
                    "b",
                    "--policy",
                    str(POLICY),
                    "--input",
                    str(pending_b),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["accepted"])

    def test_policy_direction_and_hard_gate_semantics_are_code_frozen(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        policy["stage_b"]["objectives"]["minimum_mpps"] = "min"
        reversed_path = self.root / "reversed-policy.json"
        write_json(reversed_path, policy)
        with self.assertRaises(ValueError):
            _load_policy(reversed_path)

        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        policy["stage_b"]["hard_constraints"]["minimum_mpps"]["limit"] = 0.0
        weakened_path = self.root / "weakened-policy.json"
        write_json(weakened_path, policy)
        with self.assertRaises(ValueError):
            _load_policy(weakened_path)

    def test_stage_b_rejects_distinct_labels_for_same_true_variant(self):
        first = self._campaign(
            "label-a", "tpacket-v3-hash", variant_identity="same-variant"
        )
        second = self._campaign(
            "label-b", "tpacket-v3-hash", variant_identity="same-variant"
        )
        path = self._stage_b_manifest([first, second])
        result = select_current_hardware_stage_b(POLICY, path)
        self.assertFalse(result["production_release_accepted"])
        self.assertIn("stage_b.duplicate_evaluation_identity", result["errors"])

    def test_stage_a_detects_raw_input_toctou_after_composer_read(self):
        campaign = self._campaign("stage-a-toctou")
        from hft_mgbs import current_hardware_279_release as release

        original = release.compose_current_hardware_raw_run_v2
        changed = False

        def mutate_after_read(profile_path, input_path):
            nonlocal changed
            result = original(profile_path, input_path)
            if not changed:
                input_path.write_bytes(input_path.read_bytes() + b" ")
                changed = True
            return result

        with mock.patch.object(
            release, "compose_current_hardware_raw_run_v2", side_effect=mutate_after_read
        ):
            result = audit_current_hardware_stage_a(
                POLICY, campaign["stage_a_manifest_path"]
            )
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertTrue(any("stability" in error for error in result["errors"]))

    def test_stage_a_rejects_resealed_binary_without_execution_identity_binding(self):
        campaign = self._campaign("binary-substitution")
        raw_input = campaign["raw_inputs"][0]
        request = json.loads(raw_input.read_text(encoding="utf-8"))
        root_value = Path(request["evidence_root"])
        root = root_value if root_value.is_absolute() else raw_input.parent / root_value
        root = root.resolve()
        binary = root / request["artifacts"]["capture_binary"]["path"]
        binary.write_bytes(binary.read_bytes() + b"substituted")
        request["artifacts"]["capture_binary"]["sha256"] = digest(binary)
        manifest_path = root / request["evidence_manifest"]["path"]
        rewritten = []
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            _old, relative = line.split(None, 1)
            artifact = root / relative.strip()
            rewritten.append(f"{digest(artifact)}  {relative.strip()}")
        manifest_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
        request["evidence_manifest"]["sha256"] = digest(manifest_path)
        write_json(raw_input, request)
        receipt = json.loads(campaign["receipt_path"].read_text(encoding="utf-8"))
        for reference in receipt["raw_run_inputs"]:
            if Path(reference["path"]) == raw_input.resolve():
                reference["sha256"] = digest(raw_input)
        write_json(campaign["receipt_path"], receipt)
        stage_manifest = json.loads(
            campaign["stage_a_manifest_path"].read_text(encoding="utf-8")
        )
        stage_manifest["campaign_receipt"]["sha256"] = digest(campaign["receipt_path"])
        write_json(campaign["stage_a_manifest_path"], stage_manifest)
        result = audit_current_hardware_stage_a(
            POLICY, campaign["stage_a_manifest_path"]
        )
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertTrue(
            any("release_identity.identity_binding" in error for error in result["errors"]),
            result["errors"],
        )

    def test_stage_b_detects_stage_a_manifest_toctou(self):
        first = self._campaign("toctou-a", "tpacket-v3-hash")
        second = self._campaign("toctou-b", "tpacket-v3-qm")
        path = self._stage_b_manifest([first, second])
        from hft_mgbs import current_hardware_279_release as release

        original = release.audit_current_hardware_stage_a
        changed = False

        def mutate_after_read(policy_path, manifest_path):
            nonlocal changed
            result = original(policy_path, manifest_path)
            if not changed:
                manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
                changed = True
            return result

        with mock.patch.object(
            release, "audit_current_hardware_stage_a", side_effect=mutate_after_read
        ):
            result = select_current_hardware_stage_b(POLICY, path)
        self.assertFalse(result["production_release_accepted"])
        self.assertTrue(any("stability" in error for error in result["errors"]))

    def test_duplicate_key_nan_self_reference_and_cli_write_error_fail_closed(self):
        duplicate = self.root / "duplicate.json"
        duplicate.write_text(
            '{"schema_version":1,"schema_version":1,"scope":"x"}\n',
            encoding="utf-8",
        )
        result = audit_current_hardware_stage_a(POLICY, duplicate)
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertTrue(any("duplicate JSON key" in error for error in result["errors"]))
        nan = self.root / "nan.json"
        nan.write_text('{"schema_version":NaN}\n', encoding="utf-8")
        result = select_current_hardware_stage_b(POLICY, nan)
        self.assertFalse(result["production_release_accepted"])
        self.assertTrue(any("non-finite JSON" in error for error in result["errors"]))

        self_ref = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_stage_a_manifest_v1",
            "policy_sha256": digest(POLICY),
            "campaign_receipt": None,
            "claimed_final_state": {},
        }
        self_path = self.root / "self.json"
        write_json(self_path, self_ref)
        self_ref["campaign_receipt"] = {"path": self_path.name, "sha256": digest(self_path)}
        write_json(self_path, self_ref)
        result = audit_current_hardware_stage_a(POLICY, self_path)
        self.assertFalse(result["candidate_evidence_accepted"])

        output_parent = self.root / "not-a-directory"
        output_parent.write_text("occupied", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/audit_current_hardware_279_release.py",
                "--stage", "a",
                "--policy", str(POLICY),
                "--input", str(ROOT / "configs" / "current_hardware_2_79_stage_a_pending_v1.json"),
                "--output", str(output_parent / "audit.json"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertFalse(json.loads(completed.stdout)["accepted"])

    def test_parent_symlink_and_nested_duplicate_json_are_rejected(self):
        real = self.root / "real"
        real.mkdir()
        manifest = real / "pending.json"
        manifest.write_bytes(
            (ROOT / "configs" / "current_hardware_2_79_stage_a_pending_v1.json").read_bytes()
        )
        link = self.root / "linked"
        os.symlink(real, link, target_is_directory=True)
        result = audit_current_hardware_stage_a(POLICY, link / "pending.json")
        self.assertFalse(result["candidate_evidence_accepted"])
        self.assertTrue(any("symlinked path" in error for error in result["errors"]))

        evidence = self.root / "tree"
        evidence.mkdir()
        duplicate = evidence / "runtime.json"
        duplicate.write_text(
            '{"schema_version":2,"schema_version":2,"scope":"selected_runtime_thread_all"}\n',
            encoding="utf-8",
        )
        manifest_file = evidence / "evidence.sha256"
        manifest_file.write_text("placeholder\n", encoding="utf-8")
        request = {
            "evidence_root": str(evidence),
            "evidence_manifest": {"path": manifest_file.name, "sha256": digest(manifest_file)},
            "artifacts": {
                "runtime_manifest": {"path": duplicate.name, "sha256": digest(duplicate)}
            },
            "pktgen_devices": [],
            "quality": {},
        }
        raw_input = self.root / "raw-input.json"
        write_json(raw_input, request)
        errors = []
        _raw_input_tree_snapshot(raw_input.resolve(), request, "redteam", errors)
        self.assertIn("redteam.artifacts.runtime_manifest.strict_json", errors)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.new_nic_r0_unified import audit_new_nic_r0_campaign

ROOT = Path(__file__).resolve().parents[1]
_fixture_spec = importlib.util.spec_from_file_location(
    "hft_test_new_nic_r0_fixture", ROOT / "tests" / "test_new_nic_r0.py"
)
if _fixture_spec is None or _fixture_spec.loader is None:
    raise RuntimeError("unable to load new-NIC R0 fixture")
_fixture_module = importlib.util.module_from_spec(_fixture_spec)
_fixture_spec.loader.exec_module(_fixture_module)
synthetic_bundle = _fixture_module.synthetic_bundle
file_sha = _fixture_module.file_sha
BRIDGE_SCHEMA = ROOT / "configs" / "schemas" / "new_nic_r0_unified_bridge_v1.schema.json"
PROFILE_SCHEMA = ROOT / "configs" / "schemas" / "new_nic_r0_unified_trust_profile_v1.schema.json"
CAMPAIGN_CONTRACT = ROOT / "configs" / "new_nic_r0_campaign_contract_v1.json"
UNIFIED = ROOT / "scripts" / "audit_unified_release.py"


class NewNicR0UnifiedIntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.bridge = json.loads(BRIDGE_SCHEMA.read_text(encoding="utf-8"))
        self.profile = json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))
        self.campaign = json.loads(CAMPAIGN_CONTRACT.read_text(encoding="utf-8"))

    def test_schemas_parse_and_are_closed(self):
        for schema in (self.bridge, self.profile):
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertFalse(schema["additionalProperties"])

    def test_profile_roles_exactly_match_frozen_campaign(self):
        expected = self.profile["properties"]["required_artifact_roles"]["const"]
        self.assertEqual(expected, self.campaign["required_manifest_roles"])
        self.assertEqual(len(expected), 29)
        self.assertEqual(len(expected), len(set(expected)))

    def test_fixed_code_hashes_are_not_wildcards(self):
        properties = self.profile["properties"]["approved_role_sha256"]["properties"]
        self.assertEqual(
            properties["contract"]["const"],
                "65f483c72e0bdf2e5dd4c7be68501b4ab0d8bc85f1ae999756906c37bb4e7c4b",
        )
        self.assertEqual(
            properties["runner"]["const"],
            "c8e83e8017ab30d2e67a5a49fe43327d0f373882a948b42cf7f031f63b11fc90",
        )
        self.assertEqual(
            properties["composer"]["const"],
            "209063c8031f9289a6a1c2087e3bd2f44aca9e78088199267224249bb8e0408f",
        )
        self.assertEqual(
            properties["evaluator"]["const"],
            "1665ad49a32edf9ce9d8c57a47d89120257cc7408bfc0d0d8f6296a7dfda222e",
        )

    def test_bridge_requires_three_independent_trust_roots(self):
        required = set(self.bridge["required"])
        self.assertTrue(
            {
                "trusted_evidence_manifest_sha256",
                "trusted_helper_manifest_sha256",
                "trusted_arrival_manifest_sha256",
                "external_trust_root_receipt",
                "external_change_record",
            }
            <= required
        )

    def test_backend_alias_mapping_is_explicit(self):
        mapping = self.bridge["properties"]["backend_mapping"]["properties"]
        self.assertEqual(mapping["campaign_fallback"]["const"], "dpdk_rss_tss_multiqueue")
        self.assertEqual(mapping["unified_fallback"]["const"], "dpdk_multiqueue_rss_tss")

    def test_bridge_cannot_claim_production_or_pareto(self):
        expected = self.bridge["properties"]["expected_result"]["properties"]
        self.assertFalse(expected["production_qualified"]["const"])
        self.assertFalse(expected["final_pareto_ingestion_allowed"]["const"])

    def test_current_unified_is_not_silently_integrated(self):
        source = UNIFIED.read_text(encoding="utf-8")
        self.assertIn("audit_new_nic_r0_campaign", source)
        self.assertIn('manifest.get("new_nic_r0_campaign")', source)

    def test_existing_single_backend_stage_binding_is_documented_gap(self):
        source = UNIFIED.read_text(encoding="utf-8")
        self.assertIn("len(expected_backends) != 1", source)


class NewNicR0UnifiedAdapterTests(unittest.TestCase):
    def build_fixture(self, root: Path):
        remote_root = "/evidence/campaign-r0"
        campaign_root = root / remote_root.lstrip("/")
        campaign_root.mkdir(parents=True)
        outside = root / "approved"
        outside.mkdir()
        profile_schema = json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))
        code_hashes = profile_schema["properties"]["approved_role_sha256"]["properties"]
        roles = profile_schema["properties"]["required_artifact_roles"]["const"]
        profile = {
            "schema_version": 1,
            "scope": "hft_mgbs_new_nic_r0_unified_trust_profile",
            "status": "approved_for_new_nic_r0_unified_recompute",
            "contract_id": "hft-new-nic-r0-xdp-primary-dpdk-fallback-v1",
            "required_artifact_roles": roles,
            "approved_role_sha256": {},
            "evaluator_entrypoint": "hft_mgbs.new_nic_r0:evaluate_r0_campaign",
            "expected_audit_scope": "new_high_speed_nic_r0_campaign_audit",
            "backend_mapping": {
                "campaign_primary": "native_af_xdp_forced_zerocopy",
                "unified_primary": "native_af_xdp_forced_zerocopy",
                "campaign_fallback": "dpdk_rss_tss_multiqueue",
                "unified_fallback": "dpdk_multiqueue_rss_tss",
            },
            "production_qualified": False,
            "final_pareto_ingestion_allowed": False,
        }
        role_paths = {}
        fixed_sources = {
            "contract": CAMPAIGN_CONTRACT,
            "runner": ROOT / "scripts" / "run_new_nic_r0_campaign.sh",
            "composer": ROOT / "scripts" / "compose_new_nic_r0_acceptance.py",
            "evaluator": ROOT / "hft_mgbs" / "new_nic_r0.py",
        }
        for role, source in fixed_sources.items():
            target = campaign_root / "frozen" / (role + source.suffix)
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(source.read_bytes())
            role_paths[role] = target
            self.assertEqual(file_sha(target), code_hashes[role]["const"])
        for role in (
            "xdp_runner", "dpdk_runner", "generator_runner", "resource_sampler",
            "fallback_orchestrator", "restore_helper", "campaign_executor",
            "trust_root_recorder",
        ):
            target = campaign_root / "frozen" / role
            target.write_text("#!/bin/sh\n# {}\nexit 0\n".format(role), encoding="utf-8")
            role_paths[role] = target
        approved = {
            role: file_sha(path)
            for role, path in role_paths.items()
            if role in profile_schema["properties"]["approved_role_sha256"]["required"]
        }
        profile["approved_role_sha256"] = approved
        producer_hashes = dict(approved)
        producer_hashes["arrival_evidence_manifest"] = "7" * 64
        bundle = synthetic_bundle(producer_hashes)
        json_values = {
            "campaign": bundle["campaign"],
            "arrival_inventory": bundle["arrival_inventory"],
            "arrival_preflight": bundle["arrival_preflight"],
            "restoration_before": bundle["restoration_before"],
            "restoration_after": bundle["restoration_after"],
        }
        for kind in ("xdp", "dpdk"):
            for index, value in enumerate(bundle[kind + "_runs"], 1):
                json_values["{}_run_{}".format(kind, index)] = value
        for index, value in enumerate(bundle["fallback_trials"], 1):
            json_values["fallback_trial_{}".format(index)] = value
        for role, value in json_values.items():
            target = campaign_root / (role + ".json")
            target.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
            role_paths[role] = target
        arrival = campaign_root / "arrival_evidence_manifest.sha256"
        arrival.write_text(
            "{}  inventory.probes.json\n{}  preflight.probes.json\n".format(
                file_sha(role_paths["arrival_inventory"]), file_sha(role_paths["arrival_preflight"])
            ), encoding="utf-8"
        )
        arrival_sha = file_sha(arrival)
        role_paths["arrival_evidence_manifest"] = arrival
        execution_plan = campaign_root / "new_nic_r0_execution_plan_v1.json"
        execution_plan.write_text(
            '{"schema_version":1,"scope":"test-execution-plan"}\n', encoding="utf-8"
        )
        execution_binding = campaign_root / "execution_plan.sha256"
        execution_binding.write_text(file_sha(execution_plan) + "\n", encoding="ascii")
        role_paths["execution_plan"] = execution_plan
        role_paths["execution_plan_binding"] = execution_binding
        campaign = json.loads(role_paths["campaign"].read_text(encoding="utf-8"))
        campaign["arrival_evidence_manifest_sha256"] = arrival_sha
        role_paths["campaign"].write_text(json.dumps(campaign, sort_keys=True) + "\n", encoding="utf-8")
        bundle["campaign"] = campaign
        bundle["producer_hashes"] = dict(approved)
        bundle["producer_hashes"]["arrival_evidence_manifest"] = arrival_sha
        from hft_mgbs.new_nic_r0 import evaluate_r0_campaign
        result = evaluate_r0_campaign(
            **bundle, trusted_manifest_verified=True, trusted_manifest_sha256="f" * 64
        )
        # First manifest gives the real evidence root; recompute once with that root.
        def make_manifest():
            artifacts = [
                {"role": role, "path": path.relative_to(campaign_root).as_posix(), "sha256": file_sha(path)}
                for role, path in sorted(role_paths.items())
            ]
            return {"schema_version": 1, "scope": "new_nic_r0_artifact_manifest",
                    "campaign_id": campaign["campaign_id"], "artifacts": artifacts}
        manifest_path = campaign_root / "evidence.manifest.json"
        manifest_path.write_text(json.dumps(make_manifest(), sort_keys=True) + "\n", encoding="utf-8")
        evidence_sha = file_sha(manifest_path)
        result = evaluate_r0_campaign(
            **bundle, trusted_manifest_verified=True, trusted_manifest_sha256=evidence_sha
        )
        audit_path = campaign_root / "r0_audit.json"
        audit_path.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        state_path = campaign_root / "runner_state.json"
        state_path.write_text(json.dumps({"schema_version": 1, "scope": "new_nic_r0_runner_state",
            "status": "r0_qualified", "phase": "COMPOSE", "mutations_performed": True}) + "\n", encoding="utf-8")
        helper_manifest = campaign_root / "frozen_helper_manifest.txt"
        helper_manifest.write_text("\n".join("{} {} {}".format(k, role_paths[k], approved[k]) for k in sorted(approved)) + "\n", encoding="utf-8")
        helper_sha = file_sha(helper_manifest)
        receipt = outside / "campaign.sha256"
        receipt.write_text(evidence_sha + "\n", encoding="utf-8")
        change = outside / "change.json"
        change.write_text(json.dumps({"schema_version": 1, "scope": "new_nic_r0_external_change_record",
            "campaign_id": campaign["campaign_id"], "trusted_evidence_manifest_sha256": evidence_sha,
            "trusted_helper_manifest_sha256": helper_sha, "trusted_arrival_manifest_sha256": arrival_sha,
            "approved": True}) + "\n", encoding="utf-8")
        def ref(path):
            return {"path": "/" + path.relative_to(root).as_posix(), "sha256": file_sha(path)}
        expected = {"status": "r0_qualified", "xdp_primary_repeats_qualified": 3,
            "dpdk_fallback_repeats_qualified": 3, "fallback_trials_qualified": 3,
            "restoration_qualified": True, "r0_qualified": True,
            "mutations_performed": True, "production_qualified": False,
            "final_pareto_ingestion_allowed": False}
        bridge = {"schema_version": 1, "scope": "hft_mgbs_new_nic_r0_unified_bridge",
            "integration_mode": "exclusive_new_nic_campaign_v1", "campaign_id": campaign["campaign_id"],
            "artifact_root": remote_root, "trust_profile_config_name": "new_nic_r0_trust_profile",
            "artifact_manifest": ref(manifest_path), "r0_audit": ref(audit_path), "runner_state": ref(state_path),
            "frozen_helper_manifest": ref(helper_manifest), "external_trust_root_receipt": ref(receipt),
            "external_change_record": ref(change), "trusted_evidence_manifest_sha256": evidence_sha,
            "trusted_helper_manifest_sha256": helper_sha, "trusted_arrival_manifest_sha256": arrival_sha,
            "backend_mapping": profile["backend_mapping"], "expected_result": expected}
        return bridge, profile, campaign_root

    def test_complete_campaign_recomputes_and_emits_dual_backend_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bridge, profile, _ = self.build_fixture(root)
            errors, hashes = [], {}
            qualified, restored, identity = audit_new_nic_r0_campaign(bridge, profile, root, errors, hashes)
            self.assertTrue(qualified, errors)
            self.assertTrue(restored)
            self.assertEqual(identity["backends"], ["native_af_xdp_forced_zerocopy", "dpdk_multiqueue_rss_tss"])
            self.assertEqual(len(identity["run_bundle_identities"]), 6)
            self.assertEqual(len(identity["generator_run_identities"]), 9)

    def test_saved_status_cannot_override_recomputation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bridge, profile, campaign_root = self.build_fixture(root)
            audit = campaign_root / "r0_audit.json"
            value = json.loads(audit.read_text(encoding="utf-8")); value["errors"] = ["forged"]
            audit.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
            bridge["r0_audit"]["sha256"] = file_sha(audit)
            errors, hashes = [], {}
            self.assertFalse(audit_new_nic_r0_campaign(bridge, profile, root, errors, hashes)[0])

    def test_helper_manifest_cannot_self_approve_changed_helper(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bridge, profile, campaign_root = self.build_fixture(root)
            helper = campaign_root / "frozen" / "xdp_runner"
            helper.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")
            manifest = campaign_root / "evidence.manifest.json"
            value = json.loads(manifest.read_text(encoding="utf-8"))
            for item in value["artifacts"]:
                if item["role"] == "xdp_runner": item["sha256"] = file_sha(helper)
            manifest.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
            new_root = file_sha(manifest)
            bridge["artifact_manifest"]["sha256"] = new_root
            bridge["trusted_evidence_manifest_sha256"] = new_root
            errors, hashes = [], {}
            self.assertFalse(audit_new_nic_r0_campaign(bridge, profile, root, errors, hashes)[0])

    def test_external_receipt_inside_campaign_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bridge, profile, campaign_root = self.build_fixture(root)
            inside = campaign_root / "inside.sha256"
            inside.write_text(bridge["trusted_evidence_manifest_sha256"] + "\n", encoding="utf-8")
            bridge["external_trust_root_receipt"] = {"path": "/" + inside.relative_to(root).as_posix(), "sha256": file_sha(inside)}
            errors, hashes = [], {}
            self.assertFalse(audit_new_nic_r0_campaign(bridge, profile, root, errors, hashes)[0])


if __name__ == "__main__":
    unittest.main()

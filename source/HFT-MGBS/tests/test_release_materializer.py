import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_materializer_stage_fixture", ROOT / "tests" / "test_stage_evidence.py"
)
STAGE_FIXTURE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(STAGE_FIXTURE)

from hft_mgbs.release_materializer import (
    ReleaseMaterializationError,
    materialize_candidate_receipt,
    materialize_candidate_set,
    materialize_release_configuration,
    materialize_stage_receipt,
    promote_algorithm_campaign,
)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_inputs(root, candidate_id):
    metrics = {"throughput_mpps": 12.0, "packet_drop_count": 0}
    search = {"selected_candidate": "A09"}
    search_path = root / "search.json"
    write_json(search_path, search)
    runtime = {
        "receipt_scope": "hft_mgbs_capture_runtime_decision_receipt_v1",
        "candidate_id": candidate_id,
    }
    runtime_path = root / (candidate_id + ".runtime.json")
    runtime_sha = write_json(runtime_path, runtime)
    record = {
        "candidate_id": candidate_id,
        "algorithm_id": "A09",
        "backend": "xdp-native" if candidate_id.endswith("1") else "dpdk",
        "metrics": metrics,
        "manifest_status": "complete",
        "measured_repeats": 3,
        "measured_run_ids": [candidate_id + "-1", candidate_id + "-2", candidate_id + "-3"],
        "evidence": {"quality_protocol": True},
        "code_sha256": "a" * 64,
        "input_sha256": "b" * 64,
        "evidence_manifest_sha256": "c" * 64,
        "fallback_qualified": True,
        "restoration_verified": True,
        "final_pareto_ingestion_allowed": True,
        "runtime_decision_receipt": {"path": str(runtime_path), "sha256": runtime_sha},
    }
    record_path = root / (candidate_id + ".record-input.json")
    write_json(record_path, record)
    unified = {
        "schema_version": 1,
        "scope": "hft_mgbs_unified_candidate_evidence_audit",
        "candidate_id": candidate_id,
        "algorithm_id": "A09",
        "candidate_evidence_accepted": True,
        "accepted": False,
        "production_release_accepted": False,
        "selection_performed": False,
        "selected_candidate": None,
        "final_pareto_ingestion_allowed": True,
        "full_pipeline_qualified": True,
        "errors": [],
        "derived_production_pareto_metrics": metrics,
    }
    unified_path = root / (candidate_id + ".unified.json")
    unified_sha = write_json(unified_path, unified)
    return record_path, unified_path, unified_sha, search_path, runtime_path


class ReleaseMaterializerTests(unittest.TestCase):
    def test_stage_receipt_is_recomputed_before_materialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw.json"
            write_json(raw, STAGE_FIXTURE.make_receipt("r1"))
            audit = materialize_stage_receipt(
                raw_receipt_path=raw,
                contract_path=ROOT / "configs" / "production_stage_receipt_contract_v1.json",
                output_path=root / "sealed.json",
                audit_path=root / "audit.json",
            )
            self.assertTrue(audit["qualified"])
            self.assertFalse(audit["final_pareto_ingestion_allowed"])

    def test_candidate_pair_and_candidate_set_are_transactionally_sealed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            for candidate_id in ("joint-1", "joint-2"):
                record, unified, unified_sha, search, runtime = candidate_inputs(root, candidate_id)
                receipt_output = root / (candidate_id + ".receipt.json")
                record_output = root / (candidate_id + ".record.json")
                materialize_candidate_receipt(
                    candidate_record_path=record,
                    unified_audit_path=unified,
                    trusted_unified_audit_sha256=unified_sha,
                    algorithm_search_path=search,
                    runtime_decision_receipt_path=runtime,
                    output_receipt_path=receipt_output,
                    output_record_path=record_output,
                )
                outputs.append(record_output)
            manifest = materialize_candidate_set(
                candidate_record_paths=outputs,
                output_dir=root / "sealed-set",
            )
            self.assertEqual(manifest["candidate_count"], 2)
            self.assertTrue((root / "sealed-set" / "candidates.json").is_file())
            self.assertFalse(manifest["production_release_accepted"])

    def test_candidate_failure_publishes_neither_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            record, unified, unified_sha, search, runtime = candidate_inputs(root, "joint-1")
            receipt_output = root / "receipt.json"
            record_output = root / "record.json"
            record_output.write_text("occupied", encoding="utf-8")
            with self.assertRaises(ReleaseMaterializationError):
                materialize_candidate_receipt(
                    candidate_record_path=record,
                    unified_audit_path=unified,
                    trusted_unified_audit_sha256=unified_sha,
                    algorithm_search_path=search,
                    runtime_decision_receipt_path=runtime,
                    output_receipt_path=receipt_output,
                    output_record_path=record_output,
                )
            self.assertFalse(receipt_output.exists())

    def test_algorithm_promotion_is_staged_after_authoritative_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign = root / "campaign"
            campaign.mkdir()
            projection = campaign / "projection.json"
            projection_value = {"selected_candidate": "A09"}
            projection_sha = write_json(projection, projection_value)
            formal = campaign / "formal.json"
            write_json(formal, {
                "suggested_algorithm_search_projection": {
                    "path": str(projection), "sha256": projection_sha,
                }
            })
            contract = root / "contract.json"
            write_json(contract, {"schema_version": 1})
            replay = {
                "accepted": True,
                "authoritative_raw_replay_complete": True,
                "selected_candidate": "A09",
                "raw_repeat_count": 60,
                "evaluated_candidate_count": 10,
            }
            audit = {"accepted": True, "confirmatory_practical_winner": "A09"}
            with mock.patch(
                "hft_mgbs.release_materializer.verify_algorithm_campaign_raw_replay",
                return_value=replay,
            ), mock.patch(
                "hft_mgbs.release_materializer.audit_algorithm_search", return_value=audit
            ):
                receipt = promote_algorithm_campaign(
                    repo_root=ROOT,
                    contract_path=contract,
                    campaign_root=campaign,
                    formal_receipt_path=formal,
                    output_dir=root / "promotion",
                )
            self.assertEqual(receipt["winner"], "A09")
            self.assertTrue((root / "promotion" / "manifest.json").is_file())
            self.assertFalse(receipt["final_pareto_ingestion_allowed"])

    def test_release_configuration_binds_dynamic_winner_and_real_trust_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            promotion = root / "promotion"
            promotion.mkdir()
            search = {"selected_candidate": "A09"}
            audit = {"accepted": True, "confirmatory_practical_winner": "A09"}
            search_path = promotion / "algorithm_search_promoted.json"
            audit_path = promotion / "algorithm_optimality_audit.json"
            search_sha = write_json(search_path, search)
            audit_sha = write_json(audit_path, audit)
            formal = root / "formal.json"
            formal_sha = write_json(formal, {"accepted": True})
            contract = ROOT / "configs" / "algorithm_qualification_campaign_v1.json"
            contract_sha = hashlib.sha256(contract.read_bytes()).hexdigest()
            promotion_receipt = {
                "accepted": True,
                "winner": "A09",
                "formal_receipt_sha256": formal_sha,
                "contract_sha256": contract_sha,
            }
            receipt_path = promotion / "promotion_receipt.json"
            receipt_sha = write_json(receipt_path, promotion_receipt)
            write_json(promotion / "manifest.json", {
                "scope": "hft_mgbs_algorithm_promotion_manifest_v1",
                "winner": "A09",
                "production_release_accepted": False,
                "artifacts": [
                    {"path": "algorithm_search_promoted.json", "sha256": search_sha},
                    {"path": "algorithm_optimality_audit.json", "sha256": audit_sha},
                    {"path": "promotion_receipt.json", "sha256": receipt_sha},
                ],
            })
            result = materialize_release_configuration(
                promotion_dir=promotion,
                formal_receipt_path=formal,
                contract_path=contract,
                release_candidate_path=ROOT / "configs" / "release_candidate_rc1.json",
                manifest_template_path=ROOT / "configs" / "release_manifest_v2.json",
                policy_template_path=ROOT / "configs" / "final_pareto_policy_v1.json",
                new_nic_r0_trust_profile_path=(
                    ROOT / "configs" / "new_nic_r0_unified_trust_profile_v1.json"
                ),
                runtime_failover_policy_path=(
                    ROOT / "configs" / "capture_runtime_failover_policy_v2.json"
                ),
                deployment_candidate_id="A09__new_nic_joint_r1",
                output_dir=root / "release-config",
            )
            manifest = json.loads(
                (root / "release-config" / "release_manifest.json").read_text(encoding="utf-8")
            )
            policy = json.loads(
                (root / "release-config" / "final_pareto_policy.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["candidate_id"], "A09")
            self.assertIsNotNone(manifest["algorithm_campaign_gate"]["receipt"])
            self.assertEqual(policy["algorithm_search_gate"]["allowed_algorithm_ids"], ["A09"])
            self.assertFalse(result["production_release_accepted"])
            self.assertTrue(result["hardware_and_stage_evidence_required"])
            self.assertTrue(result["runtime_failover_code_ready"])
            self.assertEqual(
                result["current_hardware_fallback_role"],
                "degraded_service_continuity_fallback_only",
            )
            self.assertTrue(
                (root / "release-config" / "capture_runtime_failover_policy.json").is_file()
            )


if __name__ == "__main__":
    unittest.main()

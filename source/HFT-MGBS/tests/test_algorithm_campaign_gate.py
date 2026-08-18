from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hft_mgbs.algorithm_campaign import validate_contract
from hft_mgbs.algorithm_campaign_gate import verify_algorithm_campaign_gate
from hft_mgbs.production_pareto import FinalParetoSelector, SelectionPolicy
from scripts.audit_unified_release import audit_manifest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "algorithm_qualification_campaign_v1.json"
SEARCH = ROOT / "configs" / "algorithm_search_rc1.json"
MANIFEST = ROOT / "configs" / "release_manifest_v2.json"
PARETO_POLICY = ROOT / "configs" / "final_pareto_policy_v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_raw_replay(receipt: Path, winner: str = "A09") -> dict:
    tree = {"entry_count": 123, "sha256": "b" * 64}
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_algorithm_qualification_campaign_raw_replay_v1",
        "campaign_id": "hft-mgbs-bounded-a01-a10-qualification-v1",
        "campaign_run_id": None,
        "contract_sha256": digest(CONTRACT),
        "algorithm_search_sha256": digest(SEARCH),
        "formal_receipt": {
            "path": str(receipt.resolve()),
            "sha256": digest(receipt),
        },
        "campaign_tree_before": tree,
        "campaign_tree_after": copy.deepcopy(tree),
        "campaign_tree_unchanged": True,
        "input_manifest_entry_count": 27,
        "candidate_count": 10,
        "evaluated_candidate_count": 10,
        "feasible_candidate_count": 1,
        "qualified_candidate_count": 1,
        "mode_count": 2,
        "repeats_per_mode": 3,
        "raw_repeat_count": 60,
        "regenerated_artifact_count": 12,
        "formal_algorithm_only_accepted": True,
        "selected_candidate": winner,
        "candidate_receipts_match_raw_replay": True,
        "projection_matches_raw_replay": True,
        "formal_receipt_matches_raw_replay": True,
        "authoritative_raw_replay_complete": True,
        "accepted": True,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
        "writes_campaign_tree": False,
        "errors": [],
    }


def accepted_projection() -> dict:
    source = json.loads(SEARCH.read_text(encoding="utf-8"))
    reference = next(
        row
        for row in source["candidates"]
        if row["id"] == "A09" and "mode_metrics" in row
    )
    for candidate in source["candidates"]:
        candidate["stage"] = "fresh_confirmatory"
        candidate["evidence"] = "/gpu/receipts/{}.json".format(candidate["id"])
        candidate["evidence_sha256"] = candidate["id"].lower().encode().hex().ljust(64, "0")[:64]
        candidate["mode_contract"] = copy.deepcopy(reference["mode_contract"])
        candidate["mode_metrics"] = copy.deepcopy(reference["mode_metrics"])
        candidate["reported_worst_case_metrics"] = copy.deepcopy(
            reference["reported_worst_case_metrics"]
        )
    # Make A09 the unique practical winner while keeping all ten auditable.
    winner = next(row for row in source["candidates"] if row["id"] == "A09")
    for candidate in source["candidates"]:
        if candidate["id"] != "A09":
            candidate["mode_metrics"] = copy.deepcopy(winner["mode_metrics"])
            for mode in ("normal", "fallback"):
                candidate["mode_metrics"][mode]["macro_f1_min"] -= 0.10
                candidate["mode_metrics"][mode]["attack_recall_min"] -= 0.10
                candidate["mode_metrics"][mode]["benign_recall_min"] -= 0.10
                candidate["mode_metrics"][mode]["auprc_min"] -= 0.10
                candidate["mode_metrics"][mode]["ece_max"] += 0.02
            values = candidate["mode_metrics"]
            candidate["reported_worst_case_metrics"] = {
                "macro_f1_min": min(values[m]["macro_f1_min"] for m in ("normal", "fallback")),
                "attack_recall_min": min(values[m]["attack_recall_min"] for m in ("normal", "fallback")),
                "benign_recall_min": min(values[m]["benign_recall_min"] for m in ("normal", "fallback")),
                "auprc_min": min(values[m]["auprc_min"] for m in ("normal", "fallback")),
                "ece_max": max(values[m]["ece_max"] for m in ("normal", "fallback")),
                "ground_truth_event_recall_min": min(values[m]["ground_truth_event_recall_min"] for m in ("normal", "fallback")),
                "key_flow_coverage_min": min(values[m]["key_flow_coverage_min"] for m in ("normal", "fallback")),
                "budget_overrun_count_max": max(values[m]["budget_overrun_count_max"] for m in ("normal", "fallback")),
                "budget_us_max": max(values[m]["budget_us_max"] for m in ("normal", "fallback")),
            }
    source["strict_pareto_front"] = ["A09"]
    source["practical_front"] = ["A09"]
    source["selected_candidate"] = "A09"
    return source


class AlgorithmCampaignGateTest(unittest.TestCase):
    def test_remote_absolute_receipt_maps_under_explicit_mirror(self):
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory)
            remote = "/gpu/campaign/campaign_receipt.json"
            local = mirror / "gpu" / "campaign" / "campaign_receipt.json"
            local.parent.mkdir(parents=True)
            local.write_text("{}", encoding="utf-8")
            gate = {
                "required": True,
                "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
                "receipt": {"path": remote, "sha256": digest(local)},
            }
            result = verify_algorithm_campaign_gate(
                ROOT, gate, remote_artifact_root=mirror
            )
            self.assertNotIn("algorithm_campaign.receipt.file", result["errors"])
            self.assertIn("algorithm_campaign.receipt.scope", result["errors"])

    def test_mirror_rejects_noncanonical_or_nonabsolute_remote_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory)
            base_gate = {
                "required": True,
                "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
            }
            for remote in (
                "gpu/campaign/receipt.json",
                "/gpu/./campaign/receipt.json",
                "/gpu/../campaign/receipt.json",
                "/gpu\\campaign\\receipt.json",
            ):
                with self.subTest(remote=remote):
                    gate = copy.deepcopy(base_gate)
                    gate["receipt"] = {"path": remote, "sha256": "0" * 64}
                    result = verify_algorithm_campaign_gate(
                        ROOT, gate, remote_artifact_root=mirror
                    )
                    self.assertIn("algorithm_campaign.receipt.path", result["errors"])
                    self.assertNotIn("algorithm_campaign.receipt.file", result["errors"])

    @unittest.skipUnless(os.name == "nt", "Windows drive reinterpretation only")
    def test_windows_requires_mirror_for_posix_absolute_receipt(self):
        gate = {
            "required": True,
            "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
            "receipt": {"path": "/opt/gpu/campaign/receipt.json", "sha256": "0" * 64},
        }
        result = verify_algorithm_campaign_gate(ROOT, gate)
        self.assertIn("algorithm_campaign.receipt.path", result["errors"])
        self.assertNotIn("algorithm_campaign.receipt.file", result["errors"])

    def test_symlink_receipt_and_parent_are_rejected_before_resolve(self):
        if not hasattr(Path, "symlink_to"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            receipt = real / "receipt.json"
            receipt.write_text("{}", encoding="utf-8")
            link = root / "linked-receipt.json"
            parent_link = root / "linked-parent"
            try:
                link.symlink_to(receipt)
                parent_link.symlink_to(real, target_is_directory=True)
            except OSError as error:
                self.skipTest("symlink creation unavailable: {}".format(error))
            base_gate = {
                "required": True,
                "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
            }
            for path in (link, parent_link / "receipt.json"):
                gate = copy.deepcopy(base_gate)
                gate["receipt"] = {"path": str(path), "sha256": digest(receipt)}
                result = verify_algorithm_campaign_gate(ROOT, gate)
                self.assertIn("algorithm_campaign.receipt.symlink", result["errors"])

    def test_current_unified_and_pareto_paths_share_null_receipt_blocker(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        unified = audit_manifest(MANIFEST, manifest)
        self.assertFalse(unified["algorithm_campaign_qualified"])
        self.assertIn("algorithm_campaign.receipt.reference", unified["errors"])

        policy = SelectionPolicy.from_mapping(
            json.loads(PARETO_POLICY.read_text(encoding="utf-8"))
        )
        selector = FinalParetoSelector(
            policy, policy_artifact_root=PARETO_POLICY.parent
        )
        self.assertIn(
            "algorithm_campaign.receipt.reference", selector.policy_errors
        )

    def test_null_receipt_is_fail_closed(self):
        gate = {
            "required": True,
            "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
            "receipt": None,
        }
        result = verify_algorithm_campaign_gate(ROOT, gate)
        self.assertFalse(result["qualified"])
        self.assertIn("algorithm_campaign.receipt.reference", result["errors"])

    def test_raw_replay_is_mandatory_and_all_authoritative_fields_are_gated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projection = root / "projection.json"
            projection.write_text(json.dumps(accepted_projection()), encoding="utf-8")
            receipt = root / "receipt.json"
            candidate_refs = []
            projection_payload = accepted_projection()
            _contract, _search, expected_artifacts, _specs = validate_contract(
                ROOT, CONTRACT
            )
            input_path = root / "input_sha256.json"
            input_path.write_text('{"frozen":true}', encoding="utf-8")
            input_manifest = {
                "path": str(input_path),
                "sha256": digest(input_path),
                "entry_count": 1,
            }
            for i in range(1, 11):
                candidate_id = "A{:02d}".format(i)
                candidate_path = root / (candidate_id + ".json")
                candidate_path.write_text(
                    json.dumps(
                        {
                            "scope": "hft_mgbs_algorithm_candidate_qualification_receipt_v1",
                            "campaign_id": "hft-mgbs-bounded-a01-a10-qualification-v1",
                            "candidate_id": candidate_id,
                            "contract_sha256": digest(CONTRACT),
                            "algorithm_search_sha256": digest(SEARCH),
                            "hard_constraints_passed": candidate_id == "A09",
                            "hard_constraint_violations": (
                                [] if candidate_id == "A09" else ["min_benign_recall_min"]
                            ),
                            "production_joint_optimum_proven": False,
                            "final_pareto_ingestion_allowed": False,
                            "input_hash_manifest": input_manifest,
                            "bound_repository_artifacts": expected_artifacts,
                            "mode_contract": {},
                        }
                    ),
                    encoding="utf-8",
                )
                candidate_refs.append(
                    {"candidate_id": candidate_id, "path": str(candidate_path), "sha256": digest(candidate_path)}
                )
                projected = next(row for row in projection_payload["candidates"] if row["id"] == candidate_id)
                candidate_payload = json.loads(candidate_path.read_text(encoding="utf-8"))
                candidate_payload["mode_contract"] = projected["mode_contract"]
                candidate_payload["mode_metrics"] = projected["mode_metrics"]
                candidate_payload["reported_worst_case_metrics"] = projected[
                    "reported_worst_case_metrics"
                ]
                candidate_path.write_text(json.dumps(candidate_payload), encoding="utf-8")
                candidate_refs[-1]["sha256"] = digest(candidate_path)
                projected["evidence"] = str(candidate_path)
                projected["evidence_sha256"] = digest(candidate_path)
            audit_function = __import__("hft_mgbs.algorithm_optimality", fromlist=["audit_algorithm_search"]).audit_algorithm_search
            initial_audit = audit_function(projection_payload)
            projection_payload["strict_pareto_front"] = initial_audit[
                "strict_pareto_front_recomputed_from_available_metrics"
            ]
            projection_payload["practical_front"] = initial_audit[
                "practical_front_recomputed_from_available_metrics"
            ]
            self.assertEqual(projection_payload["practical_front"], ["A09"])
            projection_payload["selected_candidate"] = projection_payload[
                "practical_front"
            ][0]
            with patch(
                "hft_mgbs.algorithm_optimality._path_is_clean", return_value=True
            ):
                final_projection_audit = audit_function(projection_payload)
            self.assertTrue(
                final_projection_audit["accepted"], final_projection_audit["errors"]
            )
            projection.write_text(json.dumps(projection_payload), encoding="utf-8")
            receipt.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "scope": "hft_mgbs_algorithm_qualification_campaign_receipt_v1",
                        "campaign_id": "hft-mgbs-bounded-a01-a10-qualification-v1",
                        "contract_sha256": digest(CONTRACT),
                        "algorithm_search_sha256": digest(SEARCH),
                        "input_hash_manifest": input_manifest,
                        "expected_candidate_count": 10,
                        "evaluated_candidate_count": 10,
                        "feasible_candidate_count": 1,
                        "qualified_candidate_count": 1,
                        "candidate_receipts": candidate_refs,
                        "suggested_algorithm_search_projection": {
                            "path": str(projection),
                            "sha256": digest(projection),
                        },
                        "projection_optimality_audit": final_projection_audit,
                        "campaign_evidence_complete": True,
                        "algorithm_only_practical_optimum_proven": True,
                        "accepted": True,
                        "production_joint_optimum_proven": False,
                        "final_pareto_ingestion_allowed": False,
                        "source_algorithm_search_modified": False,
                        "raw_results_remain_on_gpu": True,
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            gate = {
                "required": True,
                "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
                "receipt": {"path": str(receipt), "sha256": digest(receipt)},
            }
            with patch(
                "hft_mgbs.algorithm_optimality._path_is_clean", return_value=True
            ):
                result = verify_algorithm_campaign_gate(ROOT, gate)
            self.assertFalse(result["qualified"])
            self.assertIsNone(result["winner"])
            self.assertTrue(
                any(
                    error.startswith("algorithm_campaign.authoritative_raw_replay")
                    for error in result["errors"]
                ),
                result["errors"],
            )

            valid_replay = accepted_raw_replay(receipt)
            with patch(
                "hft_mgbs.algorithm_optimality._path_is_clean", return_value=True
            ), patch(
                "hft_mgbs.algorithm_campaign_gate.verify_algorithm_campaign_raw_replay",
                return_value=valid_replay,
            ) as replay:
                accepted = verify_algorithm_campaign_gate(ROOT, gate)
            self.assertTrue(accepted["qualified"], accepted["errors"])
            self.assertEqual(accepted["winner"], "A09")
            replay.assert_called_once_with(
                ROOT.resolve(),
                CONTRACT.resolve(),
                root.resolve(),
                receipt.resolve(),
            )

            mandatory = {
                "schema_version": 2,
                "scope": "forged",
                "campaign_id": "forged",
                "contract_sha256": "0" * 64,
                "algorithm_search_sha256": "0" * 64,
                "input_manifest_entry_count": 26,
                "accepted": False,
                "authoritative_raw_replay_complete": False,
                "campaign_tree_unchanged": False,
                "candidate_count": 9,
                "evaluated_candidate_count": 9,
                "feasible_candidate_count": 9,
                "qualified_candidate_count": 9,
                "mode_count": 1,
                "repeats_per_mode": 2,
                "raw_repeat_count": 59,
                "regenerated_artifact_count": 11,
                "formal_algorithm_only_accepted": False,
                "selected_candidate": "A08",
                "candidate_receipts_match_raw_replay": False,
                "projection_matches_raw_replay": False,
                "formal_receipt_matches_raw_replay": False,
                "production_joint_optimum_proven": True,
                "final_pareto_ingestion_allowed": True,
                "writes_campaign_tree": True,
                "errors": ["forged"],
            }
            for field, forged in mandatory.items():
                with self.subTest(raw_replay_field=field):
                    replay_result = copy.deepcopy(valid_replay)
                    replay_result[field] = forged
                    with patch(
                        "hft_mgbs.algorithm_optimality._path_is_clean",
                        return_value=True,
                    ), patch(
                        "hft_mgbs.algorithm_campaign_gate.verify_algorithm_campaign_raw_replay",
                        return_value=replay_result,
                    ):
                        rejected = verify_algorithm_campaign_gate(ROOT, gate)
                    self.assertFalse(rejected["qualified"])
                    self.assertIsNone(rejected["winner"])
                    self.assertIn(
                        "algorithm_campaign.authoritative_raw_replay." + field,
                        rejected["errors"],
                    )

            nested_forgeries = {
                "formal_receipt.path": {"path": str(SEARCH.resolve())},
                "formal_receipt.sha256": {"sha256": "0" * 64},
                "campaign_tree_unchanged": {
                    "campaign_tree_after": {
                        "entry_count": 123,
                        "sha256": "c" * 64,
                    }
                },
            }
            for error_name, mutation in nested_forgeries.items():
                with self.subTest(raw_replay_nested=error_name):
                    replay_result = copy.deepcopy(valid_replay)
                    if error_name.startswith("formal_receipt."):
                        replay_result["formal_receipt"].update(mutation)
                    else:
                        replay_result.update(mutation)
                    with patch(
                        "hft_mgbs.algorithm_optimality._path_is_clean",
                        return_value=True,
                    ), patch(
                        "hft_mgbs.algorithm_campaign_gate.verify_algorithm_campaign_raw_replay",
                        return_value=replay_result,
                    ):
                        rejected = verify_algorithm_campaign_gate(ROOT, gate)
                    self.assertFalse(rejected["qualified"])
                    self.assertIn(
                        "algorithm_campaign.authoritative_raw_replay." + error_name,
                        rejected["errors"],
                    )

    def test_receipt_hash_drift_is_fail_closed(self):
        gate = {
            "required": True,
            "contract": {"path": str(CONTRACT), "sha256": digest(CONTRACT)},
            "receipt": {"path": str(SEARCH), "sha256": "0" * 64},
        }
        result = verify_algorithm_campaign_gate(ROOT, gate)
        self.assertFalse(result["qualified"])
        self.assertIn("algorithm_campaign.receipt.sha256", result["errors"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from audit_openpn_direct_baseline import (
    DOI,
    EVIDENCE_SCHEMA,
    TITLE,
    build_audit,
    canonical_hash,
    validate_evidence,
)


def evidence_fixture() -> dict:
    value = {
        "schema_version": EVIDENCE_SCHEMA,
        "publication": {
            "doi": DOI,
            "title": TITLE,
            "venue": "Journal of Computer Security",
            "volume": "34",
            "issue": "3",
            "pages": "193-210",
            "first_published_online": "2026-02-10",
            "restricted_access": True,
        },
        "openalex": {
            "is_oa": False,
            "oa_status": "closed",
            "best_oa_location": None,
            "any_repository_has_fulltext": False,
            "has_fulltext": False,
            "pdf_url": None,
        },
        "publisher_abstract_contract": {
            "openpn_recognizes_known_and_unknown_traffic": True,
            "expert_verification_is_used_after_detection": True,
            "density_based_k_reciprocal_clustering_is_used": True,
            "continuous_learning_uses_verified_novel_attacks": True,
            "experiments_reported_on_three_public_datasets": True,
        },
        "implementation_discovery": {
            "github_repository_queries": [
                {"query": "doi", "total_count": 0},
                {"query": "title", "total_count": 0},
                {"query": "method", "total_count": 0},
            ],
            "verified_author_implementation_found": False,
            "negative_search_not_proof_of_absence": True,
            "github_code_search_authenticated": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


class OpenPNDirectBaselineAuditTests(unittest.TestCase):
    def test_repository_artifacts_recompute_exactly(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        result_root = (
            project_root
            / "results"
            / "strict_v4_openpn_direct_baseline_audit"
        )
        evidence = json.loads(
            (result_root / "evidence_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        stored = json.loads(
            (result_root / "audit.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_audit(evidence), stored)

    def test_zero_result_admission_is_fail_closed(self) -> None:
        result = build_audit(evidence_fixture())
        self.assertFalse(result["native_execution_admitted"])
        self.assertFalse(result["strict_v4_main_table_admitted"])
        self.assertFalse(
            result["published_full_framework_main_table_admitted"]
        )
        self.assertTrue(result["initial_openpn_static_stage_candidate"])
        self.assertTrue(result["related_work_admitted"])
        self.assertFalse(result["model_metrics_generated"])
        self.assertEqual(result["baseline_count_increment"], 0)
        self.assertEqual(result["manifest_sha256"], canonical_hash(result))

    def test_tampered_manifest_is_rejected(self) -> None:
        value = evidence_fixture()
        value["publication"]["doi"] = "10.invalid"
        with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
            validate_evidence(value)

    def test_wrong_identity_is_rejected_after_rehash(self) -> None:
        value = evidence_fixture()
        value["publication"]["doi"] = "10.invalid"
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "DOI identity mismatch"):
            validate_evidence(value)

    def test_missing_abstract_contract_is_rejected(self) -> None:
        value = copy.deepcopy(evidence_fixture())
        value["publisher_abstract_contract"][
            "continuous_learning_uses_verified_novel_attacks"
        ] = False
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "abstract contract"):
            validate_evidence(value)

    def test_positive_repository_result_cannot_be_silently_ignored(
        self,
    ) -> None:
        value = evidence_fixture()
        value["implementation_discovery"]["github_repository_queries"][0][
            "total_count"
        ] = 1
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "search result"):
            validate_evidence(value)


if __name__ == "__main__":
    unittest.main()

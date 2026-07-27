from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from audit_sinf_direct_baseline import (
    AUDIT_SCHEMA,
    DOI,
    EVIDENCE_SCHEMA,
    SINF_CORE_COMMIT,
    SINF_CORE_REPOSITORY,
    TITLE,
    build_audit,
    canonical_hash,
    validate_evidence,
)


def evidence_fixture() -> dict:
    result_root = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "strict_v4_sinf_direct_baseline_audit"
    )
    return json.loads(
        (result_root / "evidence_manifest.json").read_text(encoding="utf-8")
    )


class SINFDirectBaselineAuditTests(unittest.TestCase):
    def test_repository_artifacts_recompute_exactly(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        result_root = (
            project_root / "results" / "strict_v4_sinf_direct_baseline_audit"
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

    def test_publication_and_core_repository_are_frozen(self) -> None:
        evidence = evidence_fixture()
        self.assertEqual(evidence["publication"]["doi"], DOI)
        self.assertEqual(evidence["publication"]["title"], TITLE)
        core = evidence["implementation_discovery"][
            "official_sinf_core_repository"
        ]
        self.assertEqual(core["full_name"], SINF_CORE_REPOSITORY)
        self.assertEqual(core["commit"], SINF_CORE_COMMIT)
        self.assertTrue(core["official_for_2021_sinf_core_paper"])
        self.assertFalse(core["official_for_2025_ids_paper"])

    def test_zero_result_admission_is_fail_closed(self) -> None:
        result = build_audit(evidence_fixture())
        self.assertEqual(result["schema_version"], AUDIT_SCHEMA)
        self.assertFalse(result["native_execution_admitted"])
        self.assertFalse(result["strict_v4_main_table_admitted"])
        self.assertTrue(result["direct_domain_related_work_admitted"])
        self.assertTrue(result["native_external_protocol_data_ready"])
        self.assertFalse(result["model_metrics_generated"])
        self.assertEqual(result["baseline_count_increment"], 0)
        self.assertEqual(result["manifest_sha256"], canonical_hash(result))

    def test_incremental_headline_is_not_zero_shot(self) -> None:
        result = build_audit(evidence_fixture())
        metrics = result["paper_contract"]["published_metrics"]
        self.assertEqual(metrics["headline_f1_after_unknown_labeling"], 0.9999)
        self.assertFalse(metrics["headline_f1_is_zero_shot_unknown_result"])
        self.assertFalse(
            result["headline_incremental_f1_counted_as_zero_shot_unknown"]
        )

    def test_cross_dataset_header_mismatch_blocks_execution(self) -> None:
        result = build_audit(evidence_fixture())
        inventory = result["gpu_dataset_inventory"]
        self.assertEqual(inventory["cicids2017_columns_including_label"], 79)
        self.assertEqual(inventory["cicddos2019_columns_including_label"], 88)
        self.assertEqual(inventory["shared_stripped_column_names"], 78)
        self.assertFalse(inventory["exact_header_match"])
        self.assertFalse(
            result["native_reproduction_gates"][
                "cross_dataset_feature_mapping_available"
            ]
        )

    def test_documented_percentile_does_not_prove_unknown_free_trace(
        self,
    ) -> None:
        result = build_audit(evidence_fixture())
        rejection = result["paper_contract"]["unknown_rejection"]
        self.assertEqual(rejection["training_density_percentile"], 1)
        self.assertTrue(
            rejection["reported_rule_known_training_only_in_principle"]
        )
        self.assertFalse(rejection["unknown_free_selection_trace_published"])
        self.assertFalse(
            result["strict_v4_main_table_gates"][
                "zero_unknown_selection_exposure_verified"
            ]
        )

    def test_raw_data_coverage_does_not_imply_native_reproduction(self) -> None:
        result = build_audit(evidence_fixture())
        self.assertEqual(
            result["gpu_dataset_inventory"]["raw_source_candidate_coverage"],
            "2/2",
        )
        self.assertTrue(result["native_external_protocol_data_ready"])
        self.assertFalse(result["native_execution_admitted"])

    def test_tampered_manifest_is_rejected(self) -> None:
        value = evidence_fixture()
        value["publication"]["doi"] = "10.invalid"
        with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
            validate_evidence(value)

    def test_false_ids_code_claim_is_rejected_after_rehash(self) -> None:
        value = copy.deepcopy(evidence_fixture())
        value["implementation_discovery"][
            "verified_2025_ids_author_implementation_found"
        ] = True
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "author implementation"):
            validate_evidence(value)

    def test_false_header_match_is_rejected_after_rehash(self) -> None:
        value = copy.deepcopy(evidence_fixture())
        value["gpu_dataset_inventory"]["exact_header_match"] = True
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "header mismatch"):
            validate_evidence(value)


if __name__ == "__main__":
    unittest.main()

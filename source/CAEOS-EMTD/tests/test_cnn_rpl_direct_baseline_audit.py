from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from audit_cnn_rpl_direct_baseline import (
    AUDIT_SCHEMA,
    DOI,
    EVIDENCE_SCHEMA,
    NON_AUTHOR_REPOSITORY,
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
            "venue": "IEEE Access",
            "volume": "12",
            "pages": "56461-56476",
            "year": 2024,
            "ieee_document_id": "10497567",
            "open_access": True,
        },
        "source_artifacts": {
            "pdf_sha256": (
                "fb3816fc94bf39fee75507f33d5750eed6764500f9367e9d8720062"
                "af2715421"
            ),
            "pdf_size_bytes": 1820639,
            "text_sha256": (
                "742a68797b9e494279ce9005d9e74f4726f5a29a7fbdf00682efa8c"
                "ce07ebfc5"
            ),
            "text_size_bytes": 137269,
        },
        "paper_contract": {
            "architecture": {
                "conv1d_operations": 7,
                "max_pool_operations": 3,
                "prelu_after_convolution": True,
                "embedding_dimensions": 2,
                "known_output_classes": 6,
                "total_parameters": 18872,
                "all_pool_stride_and_padding_explicit": False,
            },
            "training": {
                "epochs": 100,
                "learning_rate": 0.003,
                "batch_size": 512,
                "optimizer": "Adam",
                "random_seeds": [
                    0,
                    42,
                    123,
                    222,
                    419,
                    844,
                    918,
                    1344,
                    65536,
                    815149,
                ],
                "train_test_ratio": "80:20",
                "scheduler": "MultiStepLR",
                "milestones_and_gamma_specified": False,
            },
            "rejection_rule": {
                "loss": "Lc + lambda * Lo",
                "lambda": 0.3,
                "threshold": 0.7,
                "parameters_selected_to_optimize_unknown_recognition": True,
                "independent_known_only_validation_documented": False,
            },
            "datasets": {
                "known_source": "CICIDS2017 Wednesday",
                "unknown_source_count": 2,
                "unknown_attack_sets": 10,
                "exact_preprocessed_manifest_published": False,
            },
            "published_metrics": {
                "reported": ["accuracy", "precision", "recall", "f1"],
                "strict_v4_complete": False,
            },
        },
        "implementation_discovery": {
            "github_repository_queries": [
                {"query": "3388149", "total_count": 0},
                {"query": "full title", "total_count": 1},
                {"query": "CNN-RPL DDoS", "total_count": 0},
            ],
            "same_title_candidate_repository": {
                "full_name": NON_AUTHOR_REPOSITORY,
                "commit": "a4c352624707a76bf8ad921b6e9210b67b513238",
                "paper_author_repository": False,
                "cnn_rpl_architecture_present": False,
                "pytorch_present": False,
                "reciprocal_point_loss_present": False,
                "classifiers": [
                    "PassiveAggressiveClassifier",
                    "RandomForestClassifier",
                    "DecisionTreeClassifier",
                ],
                "cnn_listed_as_future_enhancement": True,
            },
            "verified_author_implementation_found": False,
            "negative_search_not_proof_of_absence": True,
        },
        "gpu_dataset_inventory": {
            "raw_source_candidate_coverage": "2/2",
            "exact_paper_preprocessed_manifest_available": False,
            "cicids2017_machine_learning_csv_zip_bytes": 235102953,
            "cicids2017_wednesday_pcap_bytes": 13420789612,
            "cicids2017_friday_pcap_bytes": 8839309056,
            "cicddos2019_csv_01_12_zip_bytes": 2330434641,
            "cicddos2019_csv_03_11_zip_bytes": 918815761,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


class CNNRPLDirectBaselineAuditTests(unittest.TestCase):
    def test_repository_artifacts_recompute_exactly(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        result_root = (
            project_root
            / "results"
            / "strict_v4_cnn_rpl_direct_baseline_audit"
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
        self.assertEqual(result["schema_version"], AUDIT_SCHEMA)
        self.assertFalse(result["native_execution_admitted"])
        self.assertFalse(result["strict_v4_main_table_admitted"])
        self.assertTrue(result["native_external_protocol_data_ready"])
        self.assertTrue(result["direct_domain_related_work_admitted"])
        self.assertFalse(result["model_metrics_generated"])
        self.assertEqual(result["baseline_count_increment"], 0)
        self.assertEqual(result["manifest_sha256"], canonical_hash(result))

    def test_same_title_repository_is_not_silently_treated_as_author_code(
        self,
    ) -> None:
        result = build_audit(evidence_fixture())
        candidate = result["implementation_discovery"][
            "same_title_candidate_repository"
        ]
        self.assertEqual(candidate["full_name"], NON_AUTHOR_REPOSITORY)
        self.assertFalse(candidate["paper_author_repository"])
        self.assertFalse(candidate["cnn_rpl_architecture_present"])
        self.assertTrue(candidate["cnn_listed_as_future_enhancement"])
        self.assertFalse(
            result["native_reproduction_gates"][
                "verified_author_implementation_available"
            ]
        )

    def test_unknown_informed_threshold_selection_blocks_strict_admission(
        self,
    ) -> None:
        result = build_audit(evidence_fixture())
        rejection = result["paper_contract"]["rejection_rule"]
        self.assertTrue(
            rejection["parameters_selected_to_optimize_unknown_recognition"]
        )
        self.assertFalse(
            rejection["independent_known_only_validation_documented"]
        )
        self.assertFalse(
            result["strict_v4_main_table_gates"][
                "zero_unknown_validation_or_selection_exposure_verified"
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

    def test_wrong_repository_classification_is_rejected_after_rehash(
        self,
    ) -> None:
        value = copy.deepcopy(evidence_fixture())
        value["implementation_discovery"]["same_title_candidate_repository"][
            "paper_author_repository"
        ] = True
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "candidate repository mismatch"):
            validate_evidence(value)

    def test_incomplete_gpu_source_coverage_is_rejected(self) -> None:
        value = copy.deepcopy(evidence_fixture())
        value["gpu_dataset_inventory"]["raw_source_candidate_coverage"] = "1/2"
        value["manifest_sha256"] = canonical_hash(value)
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            validate_evidence(value)


if __name__ == "__main__":
    unittest.main()

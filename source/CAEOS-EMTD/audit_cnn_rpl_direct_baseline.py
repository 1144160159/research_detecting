from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EVIDENCE_SCHEMA = "strict_v4_cnn_rpl_direct_baseline_evidence_v1"
AUDIT_SCHEMA = "strict_v4_cnn_rpl_direct_baseline_audit_v1"
DOI = "10.1109/ACCESS.2024.3388149"
TITLE = (
    "Open-Set Recognition in Unknown DDoS Attacks Detection With "
    "Reciprocal Points Learning"
)
NON_AUTHOR_REPOSITORY = (
    "Paipuru-vamsi-krishna/"
    "Open-Set-Recognition-In-Unknown-DDoS-Attacks-Detection-With-"
    "Reciprocal-Points-Learning"
)


def canonical_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("manifest_sha256", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_evidence(value: dict[str, Any]) -> None:
    if value.get("schema_version") != EVIDENCE_SCHEMA:
        raise ValueError("unsupported CNN-RPL evidence schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("CNN-RPL evidence manifest SHA mismatch")

    publication = value.get("publication", {})
    expected_publication = {
        "doi": DOI,
        "title": TITLE,
        "venue": "IEEE Access",
        "volume": "12",
        "pages": "56461-56476",
        "year": 2024,
        "ieee_document_id": "10497567",
        "open_access": True,
    }
    for key, expected in expected_publication.items():
        if publication.get(key) != expected:
            raise ValueError(f"CNN-RPL publication identity mismatch: {key}")

    source = value.get("source_artifacts", {})
    expected_source = {
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
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise ValueError(f"CNN-RPL source artifact mismatch: {key}")

    contract = value.get("paper_contract", {})
    architecture = contract.get("architecture", {})
    expected_architecture = {
        "conv1d_operations": 7,
        "max_pool_operations": 3,
        "embedding_dimensions": 2,
        "known_output_classes": 6,
        "total_parameters": 18872,
    }
    for key, expected in expected_architecture.items():
        if architecture.get(key) != expected:
            raise ValueError(f"CNN-RPL architecture mismatch: {key}")
    if architecture.get("prelu_after_convolution") is not True:
        raise ValueError("CNN-RPL PReLU contract is missing")
    if architecture.get("all_pool_stride_and_padding_explicit") is not False:
        raise ValueError("CNN-RPL architecture completeness is overstated")

    training = contract.get("training", {})
    if training.get("epochs") != 100:
        raise ValueError("CNN-RPL epoch contract mismatch")
    if training.get("learning_rate") != 0.003:
        raise ValueError("CNN-RPL learning-rate contract mismatch")
    if training.get("batch_size") != 512:
        raise ValueError("CNN-RPL batch-size contract mismatch")
    if training.get("optimizer") != "Adam":
        raise ValueError("CNN-RPL optimizer contract mismatch")
    expected_seeds = [0, 42, 123, 222, 419, 844, 918, 1344, 65536, 815149]
    if training.get("random_seeds") != expected_seeds:
        raise ValueError("CNN-RPL seed contract mismatch")
    if training.get("train_test_ratio") != "80:20":
        raise ValueError("CNN-RPL split contract mismatch")
    if training.get("scheduler") != "MultiStepLR":
        raise ValueError("CNN-RPL scheduler contract mismatch")
    if training.get("milestones_and_gamma_specified") is not False:
        raise ValueError("CNN-RPL scheduler completeness is overstated")

    rejection = contract.get("rejection_rule", {})
    if rejection.get("loss") != "Lc + lambda * Lo":
        raise ValueError("CNN-RPL loss contract mismatch")
    if rejection.get("lambda") != 0.3 or rejection.get("threshold") != 0.7:
        raise ValueError("CNN-RPL rejection parameters mismatch")
    if rejection.get("parameters_selected_to_optimize_unknown_recognition") is not True:
        raise ValueError("CNN-RPL unknown-informed selection finding is missing")
    if rejection.get("independent_known_only_validation_documented") is not False:
        raise ValueError("CNN-RPL validation boundary is overstated")

    datasets = contract.get("datasets", {})
    if datasets.get("known_source") != "CICIDS2017 Wednesday":
        raise ValueError("CNN-RPL known dataset contract mismatch")
    if datasets.get("unknown_source_count") != 2:
        raise ValueError("CNN-RPL unknown dataset count mismatch")
    if datasets.get("unknown_attack_sets") != 10:
        raise ValueError("CNN-RPL unknown attack-set count mismatch")
    if datasets.get("exact_preprocessed_manifest_published") is not False:
        raise ValueError("CNN-RPL preprocessed manifest status is overstated")

    metrics = contract.get("published_metrics", {})
    if metrics.get("reported") != ["accuracy", "precision", "recall", "f1"]:
        raise ValueError("CNN-RPL published metric contract mismatch")
    if metrics.get("strict_v4_complete") is not False:
        raise ValueError("CNN-RPL strict-v4 metric coverage is overstated")

    discovery = value.get("implementation_discovery", {})
    queries = discovery.get("github_repository_queries", [])
    if [item.get("total_count") for item in queries] != [0, 1, 0]:
        raise ValueError("CNN-RPL repository search result is not frozen")
    candidate = discovery.get("same_title_candidate_repository", {})
    if candidate.get("full_name") != NON_AUTHOR_REPOSITORY:
        raise ValueError("CNN-RPL same-title repository identity mismatch")
    if candidate.get("commit") != "a4c352624707a76bf8ad921b6e9210b67b513238":
        raise ValueError("CNN-RPL same-title repository commit mismatch")
    required_negative_findings = (
        "paper_author_repository",
        "cnn_rpl_architecture_present",
        "pytorch_present",
        "reciprocal_point_loss_present",
    )
    for key in required_negative_findings:
        if candidate.get(key) is not False:
            raise ValueError(f"CNN-RPL candidate repository mismatch: {key}")
    if candidate.get("classifiers") != [
        "PassiveAggressiveClassifier",
        "RandomForestClassifier",
        "DecisionTreeClassifier",
    ]:
        raise ValueError("CNN-RPL candidate repository classifier mismatch")
    if candidate.get("cnn_listed_as_future_enhancement") is not True:
        raise ValueError("CNN-RPL candidate repository future-CNN finding missing")
    if discovery.get("verified_author_implementation_found") is not False:
        raise ValueError("CNN-RPL author implementation status is invalid")
    if discovery.get("negative_search_not_proof_of_absence") is not True:
        raise ValueError("CNN-RPL negative-search limitation is missing")

    inventory = value.get("gpu_dataset_inventory", {})
    if inventory.get("raw_source_candidate_coverage") != "2/2":
        raise ValueError("CNN-RPL GPU source dataset coverage mismatch")
    if inventory.get("exact_paper_preprocessed_manifest_available") is not False:
        raise ValueError("CNN-RPL GPU preprocessing status is overstated")
    required_sizes = {
        "cicids2017_machine_learning_csv_zip_bytes": 235102953,
        "cicids2017_wednesday_pcap_bytes": 13420789612,
        "cicids2017_friday_pcap_bytes": 8839309056,
        "cicddos2019_csv_01_12_zip_bytes": 2330434641,
        "cicddos2019_csv_03_11_zip_bytes": 918815761,
    }
    for key, expected in required_sizes.items():
        if inventory.get(key) != expected:
            raise ValueError(f"CNN-RPL GPU dataset artifact mismatch: {key}")


def load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_evidence(value)
    return value


def build_audit(evidence: dict[str, Any]) -> dict[str, Any]:
    validate_evidence(evidence)
    native_gates = {
        "official_paper_identity_verified": True,
        "official_full_text_verified": True,
        "paper_method_contract_substantially_documented": True,
        "both_raw_source_dataset_candidates_available": True,
        "verified_author_implementation_available": False,
        "exact_input_feature_order_and_preprocessing_available": False,
        "exact_pooling_and_scheduler_configuration_available": False,
        "exact_preprocessed_dataset_manifest_available": False,
        "unknown_free_threshold_selection_verified": False,
    }
    strict_gates = {
        "static_pre_incremental_stage_isolatable": True,
        "flow_level_tabular_input_compatible_in_principle": True,
        "zero_unknown_validation_or_selection_exposure_verified": False,
        "same_group_disjoint_split_contract_verified": False,
        "same_strict_v4_metrics_available": False,
        "nonduplicate_strict_adapter_implementation_available": False,
    }
    native_admitted = all(native_gates.values())
    strict_admitted = native_admitted and all(strict_gates.values())
    value: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA,
        "evidence_manifest_sha256": evidence["manifest_sha256"],
        "publication_identity": evidence["publication"],
        "source_artifacts": evidence["source_artifacts"],
        "paper_contract": evidence["paper_contract"],
        "implementation_discovery": evidence["implementation_discovery"],
        "gpu_dataset_inventory": evidence["gpu_dataset_inventory"],
        "native_reproduction_gates": native_gates,
        "strict_v4_main_table_gates": strict_gates,
        "native_execution_admitted": native_admitted,
        "strict_v4_main_table_admitted": strict_admitted,
        "direct_domain_related_work_admitted": True,
        "native_external_protocol_candidate": True,
        "native_external_protocol_data_ready": True,
        "published_result_counted_as_local_baseline": False,
        "existing_arpl_adapter_is_not_cnn_rpl_reproduction": True,
        "low_fidelity_arpl_relabel_forbidden": True,
        "model_metrics_generated": False,
        "baseline_count_increment": 0,
        "reconsideration_requirements": [
            "verified author code or an exact model and preprocessing specification",
            "immutable feature order, scaling, imputation, and row filtering rules",
            "exact MultiStepLR milestones and gamma plus all pooling parameters",
            "known-only validation for lambda and threshold with no unknown-test use",
            "preprocessed dataset manifest mapping paper quantities to source files",
            "group-disjoint strict-v4 split and all six strict-v4 metrics",
        ],
        "evidence_limitations": [
            "the same-title GitHub repository is a later non-author student project",
            "the paper does not publish an exact preprocessing pipeline",
            "the paper says lambda and threshold were selected to optimize unknown recognition",
            "no independent known-only validation split is documented",
            "paper results omit AUROC, AUPR, FPR95, OSCR, and ECE",
            "raw source availability does not prove the paper's processed rows",
        ],
        "decision": (
            "admit CNN-RPL as direct-domain related work and a data-ready native "
            "external-protocol candidate; do not execute, count, or rank it in "
            "strict-v4 until implementation, preprocessing, and unknown-free "
            "selection are reconstructable"
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("CNN-RPL audit output already exists")
    value = build_audit(load_evidence(args.evidence.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EVIDENCE_SCHEMA = "strict_v4_sinf_direct_baseline_evidence_v1"
AUDIT_SCHEMA = "strict_v4_sinf_direct_baseline_audit_v1"
DOI = "10.32604/cmc.2025.061001"
TITLE = (
    "Unknown DDoS Attack Detection with Sliced Iterative "
    "Normalizing Flows Technique"
)
SINF_CORE_REPOSITORY = "biweidai/SINF"
SINF_CORE_COMMIT = "450ee7bf3d3357c0108cf575c5bbf1a1be030a58"


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
        raise ValueError("unsupported SINFlow evidence schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("SINFlow evidence manifest SHA mismatch")

    publication = value.get("publication", {})
    expected_publication = {
        "doi": DOI,
        "title": TITLE,
        "venue": "Computers, Materials & Continua",
        "volume": "82",
        "issue": "3",
        "pages": "4881-4912",
        "year": 2025,
        "open_access": True,
    }
    for key, expected in expected_publication.items():
        if publication.get(key) != expected:
            raise ValueError(f"SINFlow publication identity mismatch: {key}")

    source = value.get("source_artifacts", {})
    expected_source = {
        "pdf_sha256": (
            "c52d670907ddf3b21a10a9ca92a1165b6050a7dc447ac6db5530bb5a"
            "8aa4ef7e"
        ),
        "pdf_size_bytes": 1511090,
        "text_sha256": (
            "e20dc94dd3a15cef9f054527fbef4cf2b49e418dff693a16f975bfbd3"
            "da26c83"
        ),
        "text_size_bytes": 108733,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise ValueError(f"SINFlow source artifact mismatch: {key}")

    contract = value.get("paper_contract", {})
    pipeline = contract.get("pipeline", {})
    if pipeline.get("stages") != [
        "autoencoder",
        "binary DNN classifier",
        "GIS density estimator",
    ]:
        raise ValueError("SINFlow pipeline contract mismatch")
    required_missing = (
        "autoencoder_layer_widths_specified",
        "latent_dimension_specified",
        "activation_functions_specified",
        "dropout_rate_specified",
        "dnn_architecture_specified",
        "training_epochs_specified",
        "gis_iteration_count_specified",
        "gis_slice_count_specified",
    )
    for key in required_missing:
        if pipeline.get(key) is not False:
            raise ValueError(f"SINFlow missing architecture detail overstated: {key}")

    training = contract.get("training", {})
    expected_training = {
        "learning_rate": 0.005,
        "weight_decay": 0.003,
        "optimizer": "Adam",
        "batch_size": 512,
        "train_test_ratio": "70:30",
    }
    for key, expected in expected_training.items():
        if training.get(key) != expected:
            raise ValueError(f"SINFlow training contract mismatch: {key}")
    expected_seeds = [
        0,
        19,
        58,
        101,
        205,
        333,
        487,
        691,
        827,
        902,
        1103,
        1229,
        1453,
        1721,
        27449,
        920987,
    ]
    if training.get("random_seeds") != expected_seeds:
        raise ValueError("SINFlow seed contract mismatch")
    if training.get("run_count_descriptions_consistent") is not False:
        raise ValueError("SINFlow run-count contradiction is missing")

    preprocessing = contract.get("preprocessing", {})
    expected_preprocessing = {
        "missing_rows": "drop",
        "nan_rows": "drop",
        "infinity_replacement": 10000000000,
        "negative_replacement": 0,
        "feature_transform": "log10(X + 1) / 10",
        "range_scaling": "[0,1]",
        "label_encoding": "one-hot binary",
        "outlier_removal": False,
        "data_augmentation": False,
        "scaler_fit_scope_documented": False,
    }
    for key, expected in expected_preprocessing.items():
        if preprocessing.get(key) != expected:
            raise ValueError(f"SINFlow preprocessing mismatch: {key}")

    rejection = contract.get("unknown_rejection", {})
    if rejection.get("score") != "GIS log density":
        raise ValueError("SINFlow rejection score mismatch")
    if rejection.get("training_density_percentile") != 1:
        raise ValueError("SINFlow threshold percentile mismatch")
    if rejection.get("reported_threshold") != -23.30:
        raise ValueError("SINFlow reported threshold mismatch")
    if rejection.get("reported_rule_known_training_only_in_principle") is not True:
        raise ValueError("SINFlow threshold principle is missing")
    if rejection.get("unknown_free_selection_trace_published") is not False:
        raise ValueError("SINFlow threshold provenance is overstated")

    datasets = contract.get("datasets", {})
    if datasets.get("known_source") != "CICIDS2017 Wednesday":
        raise ValueError("SINFlow known dataset mismatch")
    if datasets.get("unknown_sources") != [
        "CICIDS2017 Friday",
        "CICDDoS2019",
    ]:
        raise ValueError("SINFlow unknown datasets mismatch")
    if datasets.get("paper_claimed_input_features") != 80:
        raise ValueError("SINFlow feature-count claim mismatch")
    if datasets.get("cross_dataset_feature_mapping_published") is not False:
        raise ValueError("SINFlow feature mapping status is overstated")

    metrics = contract.get("published_metrics", {})
    if metrics.get("static_unknown_module_metric") != "outlier detection rate":
        raise ValueError("SINFlow static unknown metric mismatch")
    if metrics.get("strict_v4_static_metrics_complete") is not False:
        raise ValueError("SINFlow strict metric coverage is overstated")
    if metrics.get("headline_f1_after_unknown_labeling") != 0.9999:
        raise ValueError("SINFlow headline incremental metric mismatch")
    if metrics.get("headline_f1_is_zero_shot_unknown_result") is not False:
        raise ValueError("SINFlow incremental result boundary is overstated")

    discovery = value.get("implementation_discovery", {})
    if [item.get("total_count") for item in discovery.get(
        "github_repository_queries", []
    )] != [0, 0, 0, 0]:
        raise ValueError("SINFlow repository query results are not frozen")
    if discovery.get("verified_2025_ids_author_implementation_found") is not False:
        raise ValueError("SINFlow IDS author implementation status is invalid")
    core = discovery.get("official_sinf_core_repository", {})
    if core.get("full_name") != SINF_CORE_REPOSITORY:
        raise ValueError("SINFlow core repository identity mismatch")
    if core.get("commit") != SINF_CORE_COMMIT:
        raise ValueError("SINFlow core repository commit mismatch")
    if core.get("official_for_2021_sinf_core_paper") is not True:
        raise ValueError("SINFlow core repository provenance is missing")
    if core.get("official_for_2025_ids_paper") is not False:
        raise ValueError("SINFlow core repository scope is overstated")
    if core.get("cic_dataset_pipeline_present") is not False:
        raise ValueError("SINFlow core repository dataset scope is overstated")

    inventory = value.get("gpu_dataset_inventory", {})
    if inventory.get("raw_source_candidate_coverage") != "2/2":
        raise ValueError("SINFlow GPU source dataset coverage mismatch")
    if inventory.get("cicids2017_columns_including_label") != 79:
        raise ValueError("SINFlow CICIDS2017 header count mismatch")
    if inventory.get("cicddos2019_columns_including_label") != 88:
        raise ValueError("SINFlow CICDDoS2019 header count mismatch")
    if inventory.get("shared_stripped_column_names") != 78:
        raise ValueError("SINFlow shared header count mismatch")
    if inventory.get("exact_header_match") is not False:
        raise ValueError("SINFlow cross-dataset header mismatch is missing")
    if inventory.get("exact_paper_preprocessed_manifest_available") is not False:
        raise ValueError("SINFlow processed manifest status is overstated")


def load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_evidence(value)
    return value


def build_audit(evidence: dict[str, Any]) -> dict[str, Any]:
    validate_evidence(evidence)
    native_gates = {
        "official_paper_identity_verified": True,
        "official_full_text_verified": True,
        "raw_source_dataset_candidates_available": True,
        "official_sinf_core_engine_available": True,
        "verified_2025_ids_author_implementation_available": False,
        "complete_autoencoder_and_dnn_architecture_available": False,
        "complete_gis_configuration_available": False,
        "cross_dataset_feature_mapping_available": False,
        "scaler_fit_scope_available": False,
        "exact_preprocessed_dataset_manifest_available": False,
    }
    strict_gates = {
        "static_pre_incremental_stage_isolatable": True,
        "flow_level_tabular_input_compatible_in_principle": True,
        "known_training_percentile_rule_documented": True,
        "zero_unknown_selection_exposure_verified": False,
        "group_disjoint_split_contract_verified": False,
        "same_strict_v4_static_metrics_available": False,
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
        "strict_adapter_candidate_after_specification": True,
        "published_result_counted_as_local_baseline": False,
        "headline_incremental_f1_counted_as_zero_shot_unknown": False,
        "model_metrics_generated": False,
        "baseline_count_increment": 0,
        "reconsideration_requirements": [
            "verified 2025 IDS author code or exact AE and DNN architecture",
            "GIS iteration, slice, KDE, whitening, and stopping configuration",
            "immutable CICIDS2017-to-CICDDoS2019 feature mapping",
            "training-only scaler fit and row-filtering provenance",
            "known-only threshold selection trace with no unknown-test use",
            "group-disjoint strict-v4 split and all six strict-v4 metrics",
        ],
        "evidence_limitations": [
            "the public biweidai/SINF repository implements the 2021 core engine, not the 2025 IDS pipeline",
            "the paper omits AE/DNN dimensions, epochs, activations, dropout rate, and GIS configuration",
            "the paper alternately reports ten runs and sixteen seeds trained twenty times",
            "the raw CIC tables have 79 and 88 columns with no published cross-dataset mapping",
            "the static unknown module reports ODR rather than AUROC, AUPR, FPR95, OSCR, and ECE",
            "the 0.9999 headline F1 follows expert labeling and incremental learning",
        ],
        "decision": (
            "admit SINFlow as 2025 direct-domain related work and a data-ready "
            "native external-protocol candidate; do not execute, count, or rank "
            "it in strict-v4 until the architecture, GIS settings, feature "
            "mapping, and unknown-free selection provenance are reconstructable"
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
        raise FileExistsError("SINFlow audit output already exists")
    value = build_audit(load_evidence(args.evidence.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

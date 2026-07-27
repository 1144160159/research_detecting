from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


USTC_UNKNOWN_FAMILIES = (
    "cridex",
    "geodo",
    "htbot",
    "miuref",
    "neris",
    "nsis_ay",
    "shifu",
    "tinba",
    "virut",
    "zeus",
)
SEEDS = (311, 313)


def load_canonical(path: Path, schema: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"invalid canonical artifact: {path}")
    return value


def create_design(
    *,
    project_root: Path,
    structural_audit_path: Path,
    canary_protocol_path: Path,
    canary_result_path: Path,
    final_selection_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    if (output_root / "summary.json").exists():
        raise ValueError("PARROT safety design must be frozen before model metrics")
    structural = json.loads(structural_audit_path.read_text(encoding="utf-8"))
    canary_protocol = load_canonical(
        canary_protocol_path, "parrot2025_no_decryption_canary_protocol_v1"
    )
    canary_result = load_canonical(
        canary_result_path, "parrot2025_no_decryption_canary_result_v1"
    )
    if (
        structural.get("schema_version") != "parrot2025_structural_admission_v1"
        or structural.get("admission_decision", {}).get(
            "external_benign_safety_evaluation_admitted"
        )
        is not True
        or structural.get("capture_identity", {}).get("applications") != 80
        or structural.get("inventory", {}).get("pcap_files") != 320
        or canary_result.get("passed") is not True
        or canary_result.get("protocol_manifest_sha256")
        != canary_protocol["manifest_sha256"]
    ):
        raise ValueError("PARROT structural or no-decryption canary gate failed")
    source_config = project_root / "configs/ustc_tfc2016_nfstream.json"
    feature_contract = json.loads(source_config.read_text(encoding="utf-8"))
    source_features = [
        column
        for columns in feature_contract["modalities"].values()
        for column in columns
    ]
    if source_features != canary_protocol["feature_columns"]:
        raise ValueError("PARROT and USTC source feature contracts diverge")
    final_selection_available = final_selection_path.is_file()
    scenarios = [
        {"source_unknown_family": family, "seed": seed}
        for family in USTC_UNKNOWN_FAMILIES
        for seed in SEEDS
    ]
    design: dict[str, Any] = {
        "schema_version": "parrot2025_external_benign_safety_design_v1",
        "status": "frozen_design_before_model_artifact_implementation_and_metrics",
        "formal_model_metric_count_at_freeze": 0,
        "dataset": "PARROT2025",
        "dataset_role": "external_benign_mobile_application_domain_shift_safety_only",
        "source_domain": {
            "dataset": "USTC_TFC2016",
            "reason": "exact ordered 56-column NFStream feature contract",
            "benign_class": "Benign",
            "config": str(source_config.resolve()),
            "config_sha256": file_hash(source_config),
            "unknown_families": list(USTC_UNKNOWN_FAMILIES),
            "seeds": list(SEEDS),
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
        },
        "population": {
            "applications": 80,
            "captures": 320,
            "capture_group_is_indivisible": True,
            "all_captures_required": True,
            "canary_rows_are_not_formal_evaluation_rows": True,
        },
        "methods": {
            "candidate": (
                "read selected_algorithm only from the canonical final self-algorithm "
                "selection after full VGRF confirmation"
            ),
            "allowed_candidates": [
                "caeos_pairwise",
                "caeos_selective_topology_uplift",
                "caeos_validation_gated_class_conditional_reliability_fusion",
            ],
            "primary_comparator": "opendetect",
            "models_per_method": len(scenarios),
            "expected_total_model_replays": len(scenarios) * 2,
        },
        "artifact_contract": {
            "candidate_requires": [
                "ordered_feature_columns",
                "per_modality_preprocessor_state",
                "known_class_names_and_benign_index",
                "fitted_hybrid_classifier_and_all_selected_risk_components",
                "known_validation_fitted_calibrators",
                "selected_risk_name_and_threshold",
                "source_split_fingerprint",
                "implementation_and_environment_hashes",
            ],
            "comparator_requires": [
                "ordered_feature_columns",
                "per_modality_preprocessor_state",
                "model_state_and_architecture_arguments",
                "known_class_names_and_benign_index",
                "known_validation_threshold",
                "source_split_fingerprint",
                "implementation_and_environment_hashes",
            ],
            "unknown_or_external_labels_used_for_fit_selection_or_threshold": False,
            "parrot_used_for_training_validation_or_calibration": False,
        },
        "formal_metrics": {
            "false_alert_rate": "mean(prediction != benign_index)",
            "reject_rate": "mean(risk > frozen_known_validation_threshold)",
            "known_attack_assignment_rate": (
                "mean((risk <= frozen_threshold) and (prediction != benign_index))"
            ),
            "normalized_risk_p50_p95_p99": (
                "quantiles(risk / frozen_known_validation_threshold)"
            ),
            "risk_shift": (
                "PARROT minus source in-domain benign capture-block estimates"
            ),
            "uncertainty": (
                "capture-block bootstrap 95 percent intervals; application summaries "
                "remain descriptive secondary analyses"
            ),
        },
        "confirmation_gate": {
            "all_320_captures_and_80_applications_covered": True,
            "failure_count_zero": True,
            "forbidden_fit_selection_or_threshold_use_observed": False,
            "candidate_false_alert_rate_bootstrap_95ci_upper_maximum": 0.10,
            "candidate_false_alert_minus_source_benign_95ci_upper_maximum": 0.05,
            "candidate_known_attack_assignment_95ci_upper_maximum": 0.05,
            "applications_with_false_alert_rate_at_most_0_20_minimum_fraction": 0.90,
            "candidate_minus_opendetect_false_alert_95ci_upper_maximum": 0.02,
        },
        "claim_boundary": {
            "successful_gate_allows": (
                "external benign mobile-app domain-shift safety noninferiority claim"
            ),
            "does_not_allow": [
                "malicious unknown detection claim on PARROT2025",
                "PARROT2025 accuracy SOTA claim",
                "training validation calibration or threshold tuning on PARROT2025",
                "replacement of existing malicious-dataset external confirmation",
            ],
        },
        "dependencies": {
            "structural_audit": {
                "path": str(structural_audit_path.resolve()),
                "file_sha256": file_hash(structural_audit_path),
            },
            "no_decryption_canary_protocol": {
                "path": str(canary_protocol_path.resolve()),
                "manifest_sha256": canary_protocol["manifest_sha256"],
                "file_sha256": file_hash(canary_protocol_path),
            },
            "no_decryption_canary_result": {
                "path": str(canary_result_path.resolve()),
                "manifest_sha256": canary_result["manifest_sha256"],
                "file_sha256": file_hash(canary_result_path),
            },
            "final_self_algorithm_selection": {
                "path": str(final_selection_path.resolve()),
                "available_at_design_freeze": final_selection_available,
            },
        },
        "execution_admission": {
            "currently_passes": False,
            "blocking_gates": [
                "final self-algorithm selection is not yet available",
                "candidate deployable artifact serialization and exact replay are not implemented",
                "full 320-capture feature extraction implementation is not frozen",
                "source in-domain benign reference replay is not frozen",
            ],
            "rule": (
                "a later zero-metric execution protocol must bind every implementation, "
                "model artifact, source benign reference, and final selection before "
                "reading any PARROT model output"
            ),
        },
        "implementation_sha256": {
            "create_parrot2025_external_benign_safety_design.py": file_hash(
                project_root
                / "create_parrot2025_external_benign_safety_design.py"
            )
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    return design


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--structural-audit", type=Path, required=True)
    parser.add_argument("--canary-protocol", type=Path, required=True)
    parser.add_argument("--canary-result", type=Path, required=True)
    parser.add_argument("--final-selection", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_design(
        project_root=args.project_root,
        structural_audit_path=args.structural_audit,
        canary_protocol_path=args.canary_protocol,
        canary_result_path=args.canary_result,
        final_selection_path=args.final_selection,
        output_root=args.output_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def create_design(
    *,
    project_root: Path,
    postselection: Dict[str, Any],
    parrot_design: Dict[str, Any],
    feature_protocol: Dict[str, Any],
    comparative: Dict[str, Any],
    mdr_design: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    creator_sha256: str,
    observed_metrics: int,
) -> Dict[str, Any]:
    require_canonical(
        postselection,
        "strict_v4_mdr_postselection_evidence_design_v1",
        "MDR post-selection design",
    )
    require_canonical(
        parrot_design,
        "parrot2025_external_benign_safety_design_v1",
        "PARROT safety design",
    )
    require_canonical(
        feature_protocol,
        "parrot2025_full_no_decryption_feature_protocol_v1",
        "PARROT feature protocol",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative protocol",
    )
    require_canonical(
        mdr_design, "strict_v4_mdr_caeos_design_v2", "MDR design"
    )
    if int(observed_metrics) != 0:
        raise ValueError("MDR PARROT design must freeze before metrics")
    sources = [
        item
        for item in comparative["source_registry"]
        if str(item["suite"]) == "ustc_tfc2016"
    ]
    identities = {
        (str(item["scenario"]), int(item["seed"])) for item in sources
    }
    if (
        len(sources) != 30
        or len(identities) != 30
        or sorted({int(item["seed"]) for item in sources})
        != [137, 139, 149]
        or len({str(item["scenario"]) for item in sources}) != 10
    ):
        raise ValueError("MDR PARROT requires the 10x3 USTC source matrix")
    if (
        int(feature_protocol.get("capture_count", -1)) != 320
        or int(feature_protocol.get("application_count", -1)) != 80
        or int(feature_protocol.get("feature_count", -1)) != 56
        or int(
            feature_protocol.get("formal_model_metric_count_at_freeze", -1)
        )
        != 0
        or feature_protocol.get("safety_policy", {}).get(
            "payload_decryption"
        )
        is not False
    ):
        raise ValueError("PARROT no-decryption feature universe drifted")
    parent = postselection["external_benign_safety_evidence"]
    if (
        parent["confirmation_gate"] != parrot_design["confirmation_gate"]
        or int(parent["capture_count"]) != 320
        or int(parent["application_count"]) != 80
    ):
        raise ValueError("MDR PARROT inherited safety gates drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_safety_design_v1",
        "status": (
            "conditional_frozen_before_mdr_selection_and_parrot_metrics"
        ),
        "project_root": str(project_root.resolve()),
        "activation_gate": postselection["activation_gate"],
        "dataset_role": (
            "external_benign_mobile_application_domain_shift_"
            "false_alert_safety_only"
        ),
        "population": {
            "dataset": "PARROT2025",
            "capture_count": 320,
            "application_count": 80,
            "captures_per_application": 4,
            "feature_count": 56,
            "payload_decryption": False,
            "all_capture_shards_required": True,
        },
        "source_model_matrix": {
            "suite": "ustc_tfc2016",
            "scenario_count": 10,
            "seeds": [137, 139, 149],
            "model_pairs": 30,
            "candidate": "fresh_mdr_caeos_v1_after_positive_selection",
            "comparator": (
                "frozen_opendetect_runtime_from_the_same_comparative_"
                "scenario_seed_and_split"
            ),
            "candidate_and_comparator_share_exact_source_preprocessing": True,
            "candidate_models_or_outputs_may_not_be_inherited": True,
        },
        "candidate_deployment_capture": {
            "selected_weight_frozen_by_full_mdr_confirmation": True,
            "raw_feature_bundle_contains": [
                "ordered_56_feature_columns",
                "three_modality_preprocessor_states",
                "class_names_and_benign_index",
                "frozen_known_validation_threshold",
                "source_split_fingerprint",
                "serializable_mdr_runtime",
            ],
            "source_benign_reference_is_final_evaluation_only": True,
            "serialization_roundtrip_required": True,
        },
        "formal_metrics": parrot_design["formal_metrics"],
        "confirmation_gate": parent["confirmation_gate"],
        "aggregation": {
            "average_30_models_within_capture_first": True,
            "capture_block_count": 320,
            "capture_block_bootstrap_repetitions": 10000,
            "capture_block_bootstrap_seed": 20260724,
            "candidate_minus_opendetect_is_paired_by_capture": True,
            "candidate_minus_source_benign_uses_independent_capture_and_model_resampling": True,
            "application_level_summary_is_secondary": True,
        },
        "leakage_policy": {
            "parrot_features_used_for_model_fit": False,
            "parrot_features_used_for_selection_calibration_or_threshold": False,
            "parrot_labels_used_for_any_model_operation": False,
            "source_benign_labels_used_for_final_reference_only": True,
            "all_thresholds_frozen_on_source_known_validation": True,
        },
        "required_output": {
            "schema_version": "strict_v4_mdr_parrot_safety_summary_v1",
            "model_pair_count": 30,
            "capture_count": 320,
            "application_count": 80,
            "safety_gate_reported_without_malicious_accuracy_claim": True,
        },
        "required_implementation": [
            "create_strict_v4_mdr_parrot_safety_protocol.py",
            "capture_mdr_parrot_deployment_bundle.py",
            "evaluate_mdr_parrot_capture.py",
            "run_strict_v4_mdr_parrot_safety.py",
            "summarize_strict_v4_mdr_parrot_safety.py",
            "audit_strict_v4_mdr_parrot_safety.py",
            "caeos/mdr_deployment.py",
            "scripts/wait_and_run_strict_v4_mdr_parrot_safety.sh",
        ],
        "claim_boundary": {
            "successful_gate_allows": (
                "cross_domain_benign_false_alert_safety_noninferiority"
            ),
            "does_not_allow_malicious_detection_accuracy_claim": True,
            "does_not_allow_parrot_accuracy_or_sota_claim": True,
            "does_not_replace_fresh_malicious_external_confirmation": True,
            "no_pairwise_vgrf_or_previous_parrot_effect_inheritance": True,
        },
        "input_manifest_sha256": {
            "postselection_design": postselection["manifest_sha256"],
            "parrot_safety_design": parrot_design["manifest_sha256"],
            "parrot_feature_protocol": feature_protocol["manifest_sha256"],
            "comparative_protocol": comparative["manifest_sha256"],
            "mdr_design": mdr_design["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": {
            "create_strict_v4_mdr_parrot_safety_design.py": creator_sha256
        },
        "formal_metric_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument("--parrot-design", type=Path, required=True)
    parser.add_argument("--feature-protocol", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "postselection_design": args.postselection_design,
        "parrot_safety_design": args.parrot_design,
        "parrot_feature_protocol": args.feature_protocol,
        "comparative_protocol": args.comparative_protocol,
        "mdr_design": args.mdr_design,
    }
    observed = (
        len(list(args.run_root.glob("**/metrics.json")))
        if args.run_root.exists()
        else 0
    )
    implementation = Path(__file__).resolve()
    value = create_design(
        project_root=args.project_root,
        postselection=load(args.postselection_design),
        parrot_design=load(args.parrot_design),
        feature_protocol=load(args.feature_protocol),
        comparative=load(args.comparative_protocol),
        mdr_design=load(args.mdr_design),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        creator_sha256=file_hash(implementation),
        observed_metrics=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

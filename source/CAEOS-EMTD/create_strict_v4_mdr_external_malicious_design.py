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
    mdr_design: Dict[str, Any],
    external_v1: Dict[str, Any],
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
        mdr_design, "strict_v4_mdr_caeos_design_v2", "MDR design"
    )
    require_canonical(
        external_v1,
        "gpu_external_dataset_evaluation_design_protocol_v1",
        "external v1 design",
    )
    if int(observed_metrics) != 0:
        raise ValueError("MDR external design must freeze before metrics")
    contract = postselection["fresh_external_malicious_evidence"]
    if (
        contract["datasets"] != ["LSNM2024", "CICDDoS2019"]
        or contract["seeds"] != [223, 227, 229]
        or contract["primary_comparator"] != "opendetect"
    ):
        raise ValueError("MDR external parent contract drifted")
    mechanism = mdr_design["mechanism"]
    if (
        float(mechanism["training_sample_fraction"]) != 0.25
        or float(mechanism["health_gate"]["quantile"]) != 0.99
    ):
        raise ValueError("MDR frozen mechanism drifted")
    if (
        external_v1["datasets"] != contract["datasets"]
        or external_v1["seeds"] != contract["seeds"]
        or external_v1["confirmation_gate"] != contract["confirmation_gate"]
    ):
        raise ValueError("external source contract differs from parent")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_design_v1"
        ),
        "status": (
            "conditional_frozen_before_mdr_selection_preparation_"
            "and_external_metrics"
        ),
        "project_root": str(project_root.resolve()),
        "activation_gate": postselection["activation_gate"],
        "datasets": contract["datasets"],
        "seeds": contract["seeds"],
        "scenario_rule": contract["scenario_rule"],
        "split_rule": contract["split_rule"],
        "candidate": "mdr_caeos_v1",
        "primary_comparator": "opendetect",
        "mdr_policy": {
            "augmentation_weight": (
                "read_exactly_once_from_positive_canonical_mdr_"
                "confirmation_protocol"
            ),
            "weight_may_not_be_reselected_on_external_data": True,
            "training_sample_fraction": 0.25,
            "health_quantile": 0.99,
            "clean_threshold_source": (
                "clean_pairwise_known_validation_only"
            ),
            "augmentation_seed_rule": (
                "first_31_bits_of_sha256("
                "design_manifest:dataset:unknown_family:training_seed:"
                "augmentation)"
            ),
            "validation_profile_seed_rule": (
                "first_31_bits_of_sha256("
                "design_manifest:dataset:unknown_family:training_seed:"
                "validation_profile)"
            ),
            "seed_rules_do_not_read_effects": True,
            "fresh_clean_and_robust_fit_per_scenario": True,
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
        },
        "opendetect_policy": external_v1["opendetect_policy"],
        "formal_metrics": external_v1["formal_metrics"],
        "confirmation_gate": external_v1["confirmation_gate"],
        "statistics": {
            "average_three_seeds_within_dataset_attack_block": True,
            "bootstrap_unit": "dataset_attack_family_block",
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260724,
            "wilcoxon_unit": "dataset_attack_family_block",
            "holm_family": list(external_v1["formal_metrics"]),
            "both_datasets_must_be_nonnegative_for_all_formal_metrics": True,
        },
        "execution_contract": {
            "preparation_summary_must_be_canonical_and_complete": True,
            "execution_protocol_freezes_after_preparation_before_metrics": True,
            "all_prepared_csv_and_sidecar_hashes_are_bound": True,
            "candidate_and_comparator_split_fingerprints_must_match": True,
            "partial_capture_or_metrics_directory_is_a_failure": True,
            "all_outputs_are_resumable_and_hash_validated": True,
            "failure_count_must_equal_zero": True,
        },
        "required_implementation": [
            "create_strict_v4_mdr_external_malicious_protocol.py",
            "run_strict_v4_mdr_external_malicious.py",
            "evaluate_mdr_external_runtime.py",
            "summarize_strict_v4_mdr_external_malicious.py",
            "audit_strict_v4_mdr_external_malicious.py",
            "scripts/wait_and_run_strict_v4_mdr_external_malicious.sh",
        ],
        "claim_boundary": {
            "success_supports_fresh_two_dataset_mdr_external_accuracy": True,
            "failure_blocks_mdr_external_and_comprehensive_claims": True,
            "does_not_replace_efficiency_deployment_or_parrot_gates": True,
            "cicddos2019_is_narrow_ddos_family_evidence_only": True,
            "no_pairwise_vgrf_or_parrot_effect_inheritance": True,
        },
        "input_manifest_sha256": {
            "postselection_design": postselection["manifest_sha256"],
            "mdr_design": mdr_design["manifest_sha256"],
            "external_v1_design": external_v1["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": {
            "create_strict_v4_mdr_external_malicious_design.py": (
                creator_sha256
            )
        },
        "formal_metric_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--external-v1-design", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "postselection_design": args.postselection_design,
        "mdr_design": args.mdr_design,
        "external_v1_design": args.external_v1_design,
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
        mdr_design=load(args.mdr_design),
        external_v1=load(args.external_v1_design),
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

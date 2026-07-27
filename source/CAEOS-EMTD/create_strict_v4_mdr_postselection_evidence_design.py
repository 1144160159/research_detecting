from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


MDR = "mdr_caeos_v1"


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
    mdr_design: Dict[str, Any],
    external_design: Dict[str, Any],
    efficiency: Dict[str, Any],
    parrot_design: Dict[str, Any],
    parrot_features: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_output_counts: Dict[str, int],
) -> Dict[str, Any]:
    require_canonical(
        mdr_design, "strict_v4_mdr_caeos_design_v2", "MDR design"
    )
    require_canonical(
        external_design,
        "gpu_external_dataset_evaluation_design_protocol_v1",
        "external evaluation design",
    )
    require_canonical(
        efficiency,
        "strict_v4_final_efficiency_protocol_v2",
        "efficiency protocol",
    )
    require_canonical(
        parrot_design,
        "parrot2025_external_benign_safety_design_v1",
        "PARROT safety design",
    )
    require_canonical(
        parrot_features,
        "parrot2025_full_no_decryption_feature_protocol_v1",
        "PARROT feature protocol",
    )
    if any(int(count) != 0 for count in observed_output_counts.values()):
        raise ValueError(
            "MDR post-selection design must freeze before its outputs"
        )
    if int(external_design.get("formal_metric_count_at_freeze", -1)) != 0:
        raise ValueError("external source design was not frozen pre-result")
    if int(efficiency.get("efficiency_metrics_observed_at_freeze", -1)) != 0:
        raise ValueError("efficiency source protocol was not frozen pre-result")
    if int(parrot_design.get("formal_model_metric_count_at_freeze", -1)) != 0:
        raise ValueError("PARROT source design was not frozen pre-result")
    reserved = mdr_design.get("reserved_confirmation", {})
    seeds = reserved.get("training_seeds", [])
    conditions = reserved.get("conditions", [])
    if (
        int(reserved.get("scenario_count", -1)) != 102
        or seeds != [347, 349, 353]
        or reserved.get("corruption_seeds") != [359, 367, 373]
        or int(reserved.get("expected_evaluations", -1)) != 1836
        or len(conditions) != 6
        or conditions[0] != "clean"
    ):
        raise ValueError(
            "MDR reserved confirmation universe is not frozen full102x3"
        )
    if (
        int(parrot_features.get("capture_count", -1)) != 320
        or int(parrot_features.get("application_count", -1)) != 80
    ):
        raise ValueError("PARROT feature universe must contain 320/80")
    if external_design.get("datasets") != ["LSNM2024", "CICDDoS2019"]:
        raise ValueError("external malicious dataset universe drifted")

    external_gate = external_design["confirmation_gate"]
    parrot_gate = parrot_design["confirmation_gate"]
    system_metrics = [
        "latency_p50_ms",
        "latency_p95_ms",
        "latency_p99_ms",
        "samples_per_second",
        "peak_gpu_memory_mb",
        "peak_host_rss_mb",
        "serialized_deployment_artifact_bytes",
        "total_fit_seconds",
    ]
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_postselection_evidence_design_v1"
        ),
        "status": (
            "conditionally_frozen_before_mdr_selection_and_"
            "postselection_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "activation_gate": {
            "selection_schema": (
                "strict_v4_final_self_algorithm_selection_v2"
            ),
            "selected_algorithm_must_equal": MDR,
            "mdr_full102_confirmation_passes": True,
            "pairwise_selection_writes_canonical_not_required_records": True,
        },
        "accuracy_and_robustness_evidence": {
            "source_schema": (
                "strict_v4_mdr_caeos_confirmation_summary_v1"
            ),
            "scenario_count": 102,
            "training_seeds": seeds,
            "corruption_seeds": reserved["corruption_seeds"],
            "capture_count": 306,
            "evaluation_count": 1836,
            "conditions": conditions,
            "all_frozen_confirmation_checks_required": True,
            "pairwise_or_vgrf_effects_cannot_be_relabelled_as_mdr": True,
        },
        "fresh_external_malicious_evidence": {
            "datasets": external_design["datasets"],
            "seeds": external_design["seeds"],
            "split_rule": external_design["split_rule"],
            "scenario_rule": external_design["scenario_rule"],
            "candidate": MDR,
            "primary_comparator": "opendetect",
            "must_train_fresh_clean_and_robust_mdr_runtimes": True,
            "pairwise_external_results_cannot_be_inherited": True,
            "vgrf_external_results_cannot_be_inherited": True,
            "confirmation_gate": external_gate,
        },
        "selected_system_evidence": {
            "deployment_equivalence": {
                "all_306_confirmation_runtime_roundtrips_required": True,
                "prediction_array_identity_required": True,
                "risk_and_probability_max_absolute_tolerance": 1e-12,
                "unknown_or_test_labels_used": False,
            },
            "same_hardware_benchmark": {
                "candidate": MDR,
                "embedded_reference": "mdr_runtime.clean_runtime",
                "batch_sizes": efficiency["inference_benchmark"][
                    "batch_sizes"
                ],
                "warmup_repetitions": 5,
                "timed_repetitions": 30,
                "alternate_method_order_by_repetition": True,
                "exclusive_machine_required": True,
                "reported_metrics": system_metrics,
            },
            "strict_efficiency_superiority_gate": {
                "all_latency_ratio_bootstrap_upper_bounds_le_1": True,
                "all_throughput_ratio_bootstrap_lower_bounds_ge_1": True,
                "artifact_ratio_bootstrap_upper_bound_le_1": True,
                "fit_time_ratio_bootstrap_upper_bound_le_1": True,
                "failure_blocks_only_multidimensional_efficiency_sota": True,
            },
            "deployability_gate": {
                "all_outputs_finite": True,
                "failure_count_zero": True,
                "serialization_roundtrip_passes": True,
                "same_hardware_metrics_completely_reported": True,
                "no_resource_metric_splicing": True,
            },
        },
        "external_benign_safety_evidence": {
            "dataset": "PARROT2025",
            "role": (
                "external_benign_mobile_application_domain_shift_safety_only"
            ),
            "capture_count": 320,
            "application_count": 80,
            "no_decryption": True,
            "candidate": MDR,
            "primary_comparator": "opendetect",
            "confirmation_gate": parrot_gate,
            "may_not_support_malicious_accuracy_or_sota_claims": True,
            "may_not_be_used_for_fit_selection_calibration_or_threshold": True,
        },
        "integrated_claim_policy": {
            "accuracy_robustness_external_sota_with_deployability_requires": [
                "mdr_full102_confirmation",
                "fresh_two_dataset_external_malicious_confirmation",
                "selected_system_deployability",
                "parrot_external_benign_safety",
            ],
            "multidimensional_comprehensive_sota_additionally_requires": [
                "strict_efficiency_superiority_over_embedded_pairwise",
                "strict_efficiency_superiority_over_opendetect",
            ],
            "all_gates_must_pass_without_dataset_metric_or_component_splicing": True,
            "parrot_cannot_substitute_for_malicious_external_evidence": True,
            "confirmation_success_alone_cannot_authorize_either_claim": True,
        },
        "required_future_outputs": {
            "mdr_external_malicious_summary": (
                "strict_v4_mdr_external_malicious_summary_v1"
            ),
            "mdr_selected_system_summary": (
                "strict_v4_mdr_selected_system_summary_v1"
            ),
            "mdr_parrot_safety_summary": (
                "strict_v4_mdr_parrot_safety_summary_v1"
            ),
            "integrated_audit": (
                "strict_v4_mdr_integrated_comprehensive_sota_audit_v1"
            ),
        },
        "source_reuse_boundary": {
            "external_v1_reuse": (
                "datasets_splits_opendetect_policy_and_frozen_gates_only"
            ),
            "efficiency_v2_reuse": (
                "hardware_controls_batch_sizes_metrics_and_equivalence_"
                "principles_only"
            ),
            "parrot_v1_reuse": (
                "dataset_feature_population_and_frozen_safety_gates_only"
            ),
            "all_mdr_model_outputs_must_be_fresh": True,
        },
        "input_manifest_sha256": {
            "mdr_design": mdr_design["manifest_sha256"],
            "external_design_v1": external_design["manifest_sha256"],
            "efficiency_protocol_v2": efficiency["manifest_sha256"],
            "parrot_safety_design_v1": parrot_design["manifest_sha256"],
            "parrot_feature_protocol_v1": parrot_features[
                "manifest_sha256"
            ],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "postselection_output_counts_at_freeze": {
            name: int(count)
            for name, count in sorted(observed_output_counts.items())
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--mdr-confirmation-creator", type=Path, required=True)
    parser.add_argument("--external-design", type=Path, required=True)
    parser.add_argument("--efficiency-protocol", type=Path, required=True)
    parser.add_argument("--parrot-design", type=Path, required=True)
    parser.add_argument("--parrot-feature-protocol", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = {
        "mdr_design": args.mdr_design,
        "mdr_confirmation_creator": args.mdr_confirmation_creator,
        "external_design_v1": args.external_design,
        "efficiency_protocol_v2": args.efficiency_protocol,
        "parrot_safety_design_v1": args.parrot_design,
        "parrot_feature_protocol_v1": args.parrot_feature_protocol,
    }
    observed = {
        "external_metrics": len(
            list(args.run_root.glob("external/**/metrics.json"))
        )
        if args.run_root.exists()
        else 0,
        "system_blocks": len(
            list(args.run_root.glob("system/**/benchmark.json"))
        )
        if args.run_root.exists()
        else 0,
        "parrot_metrics": len(
            list(args.run_root.glob("parrot/**/metrics.json"))
        )
        if args.run_root.exists()
        else 0,
        "integrated_audits": int(
            (args.result_root / "integrated_audit.json").exists()
        ),
    }
    implementation = Path(__file__).resolve()
    value = create_design(
        project_root=args.project_root,
        mdr_design=load(args.mdr_design),
        external_design=load(args.external_design),
        efficiency=load(args.efficiency_protocol),
        parrot_design=load(args.parrot_design),
        parrot_features=load(args.parrot_feature_protocol),
        input_file_sha256={
            name: file_hash(path) for name, path in inputs.items()
        },
        implementation_sha256={
            implementation.name: file_hash(implementation)
        },
        observed_output_counts=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

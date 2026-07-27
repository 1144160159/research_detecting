from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def output_counts(root: Path) -> Dict[str, int]:
    names = {
        "external_metrics": "external_metrics.json",
        "parrot_metrics": "parrot_metrics.json",
        "system_benchmark": "benchmark.json",
        "summary": "summary.json",
        "audit": "audit.json",
    }
    return {
        name: len(list(root.rglob(filename))) if root.exists() else 0
        for name, filename in names.items()
    }


def create(
    *,
    project_root: Path,
    krc_protocol: Dict[str, Any],
    external_design: Dict[str, Any],
    parrot_design: Dict[str, Any],
    parrot_features: Dict[str, Any],
    efficiency_protocol: Dict[str, Any],
    comparative_protocol: Dict[str, Any],
    observed_counts: Dict[str, int],
    input_file_sha256: Dict[str, str],
    creator_sha256: str,
) -> Dict[str, Any]:
    require_canonical(
        krc_protocol,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC confirmation protocol",
    )
    require_canonical(
        external_design,
        "gpu_external_dataset_evaluation_design_protocol_v1",
        "external malicious design",
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
    require_canonical(
        efficiency_protocol,
        "strict_v4_final_efficiency_protocol_v2",
        "efficiency protocol",
    )
    require_canonical(
        comparative_protocol,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative protocol",
    )
    if (
        krc_protocol.get("execution_admitted") is not True
        or int(krc_protocol.get("source_registry_count", -1)) != 102
        or int(
            krc_protocol.get("confirmation", {}).get(
                "full_task_count", -1
            )
        )
        != 306
    ):
        raise ValueError("admitted 102-scenario KRC confirmation required")
    if any(observed_counts.values()):
        raise ValueError(
            "KRC downstream design must freeze before downstream outputs"
        )
    if (
        external_design.get("datasets")
        != ["LSNM2024", "CICDDoS2019"]
        or external_design.get("seeds") != [223, 227, 229]
    ):
        raise ValueError("external malicious universe drifted")
    population = parrot_design.get("population", {})
    if (
        population.get("captures") != 320
        or population.get("applications") != 80
        or parrot_features.get("capture_count") != 320
        or parrot_features.get("application_count") != 80
        or parrot_features.get("feature_count") != 56
        or parrot_features.get("formal_model_metric_count_at_freeze")
        != 0
        or parrot_features.get("safety_policy", {}).get(
            "payload_decryption"
        )
        is not False
    ):
        raise ValueError("PARROT no-decryption universe drifted")
    benchmark = efficiency_protocol.get("inference_benchmark", {})
    if (
        benchmark.get("batch_sizes") != [1, 64, 512]
        or benchmark.get("warmup_repetitions") != 5
        or benchmark.get("timed_repetitions") != 30
    ):
        raise ValueError("efficiency benchmark universe drifted")
    seed137 = [
        record
        for record in comparative_protocol["source_registry"]
        if int(record["seed"]) == 137
    ]
    if (
        len(seed137) != 102
        or len(
            {
                (str(record["suite"]), str(record["scenario"]))
                for record in seed137
            }
        )
        != 102
    ):
        raise ValueError("OpenDetect efficiency registry must be full102")
    ustc_tasks = [
        task
        for task in krc_protocol["confirmation"]["tasks"]
        if str(task["suite"]) == "ustc_tfc2016"
    ]
    if (
        len(ustc_tasks) != 30
        or len({str(task["scenario"]) for task in ustc_tasks}) != 10
        or sorted({int(task["training_seed"]) for task in ustc_tasks})
        != [647, 653, 659]
    ):
        raise ValueError("KRC PARROT source matrix must be USTC 10x3")

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_downstream_sota_design_v1",
        "status": (
            "conditional_frozen_before_krc_confirmation_and_"
            "downstream_outputs"
        ),
        "execution_admitted": False,
        "algorithm": "krc_csr_caeos_v1",
        "project_root": str(project_root.resolve()),
        "activation_gate": {
            "confirmation_summary_path": (
                "results/strict_v4_krc_csr_confirmation_v1/summary.json"
            ),
            "confirmation_summary_schema": (
                "strict_v4_krc_csr_confirmation_summary_v1"
            ),
            "confirmation_summary_protocol_manifest_sha256": (
                krc_protocol["manifest_sha256"]
            ),
            "confirmation_summary_passes": True,
            "confirmation_selection": "krc_csr_caeos_v1",
            "confirmation_audit_path": (
                "results/strict_v4_krc_csr_confirmation_v1/audit.json"
            ),
            "confirmation_audit_schema": (
                "strict_v4_krc_csr_confirmation_audit_v1"
            ),
            "confirmation_audit_passes": True,
            "confirmation_audit_decision_matches_summary": True,
            "all_manifest_and_file_hashes_must_match": True,
            "otherwise": (
                "write_not_required_for_all_krc_downstream_branches_"
                "and_retain_caeos_pairwise"
            ),
        },
        "classic_baseline_policy": {
            "manuscript_main_table_count": 7,
            "methods": [
                "MLP-MSP",
                "MLP-Energy",
                "MLP-OpenMax",
                "MLP-kNN",
                "MLP-ViM",
                "Mahalanobis++",
                "OpenDetect",
            ],
            "primary_direct_domain_comparator": "OpenDetect",
            "additional_methods_belong_in_supplement": True,
            "candidate_and_pairwise_are_not_counted_as_external_baselines": (
                True
            ),
        },
        "fresh_external_malicious": {
            "role": "unknown_malicious_cross_dataset_generalization",
            "datasets": external_design["datasets"],
            "training_seeds": external_design["seeds"],
            "scenario_rule": external_design["scenario_rule"],
            "split_rule": external_design["split_rule"],
            "candidate": "krc_csr_caeos_v1",
            "comparators": ["caeos_pairwise", "opendetect"],
            "confirmation_gate": external_design["confirmation_gate"],
            "candidate_must_be_retrained_on_each_external_split": True,
            "known_only_training_selection_and_threshold": True,
            "source_confirmation_test_results_may_not_select_parameters": (
                True
            ),
        },
        "parrot2025_external_benign_safety": {
            "role": (
                "external_benign_mobile_application_domain_shift_safety_only"
            ),
            "captures": 320,
            "applications": 80,
            "feature_count": 56,
            "source_suite": "ustc_tfc2016",
            "source_unknown_family_count": 10,
            "candidate_training_seeds": [647, 653, 659],
            "candidate_bundle_count": 30,
            "opendetect_bundle_count": 30,
            "expected_total_model_replays": 60,
            "confirmation_gate": parrot_design["confirmation_gate"],
            "payload_decryption": False,
            "training_validation_calibration_or_threshold_use": False,
            "malicious_accuracy_or_sota_claim": False,
            "cannot_replace_external_malicious_confirmation": True,
        },
        "selected_system_and_efficiency": {
            "source_candidate_capture_count": 306,
            "source_scenario_count": 102,
            "candidate_training_seeds": [647, 653, 659],
            "embedded_pairwise_comparator_count": 306,
            "opendetect_seed137_runtime_count": 102,
            "batch_sizes": benchmark["batch_sizes"],
            "warmup_repetitions": benchmark["warmup_repetitions"],
            "timed_repetitions": benchmark["timed_repetitions"],
            "reported_metrics": benchmark["reported_metrics"],
            "method_order": "alternate_by_timed_repetition",
            "same_process_and_exact_same_processed_inputs": True,
            "exclusive_machine_preflight_required": True,
            "must_not_overlap_accuracy_confirmation": True,
            "scenario_seed_aggregation": (
                "average_three_krc_training_seeds_within_scenario_first"
            ),
            "scenario_block_count": 102,
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260726,
            "deployability_gate": {
                "prediction_arrays_exact": True,
                "probability_max_absolute_difference": 0.0,
                "risk_max_absolute_difference": 1e-12,
                "split_and_artifact_hashes_match": True,
            },
            "strict_efficiency_superiority_over_each_comparator": {
                "all_latency_ratio_bootstrap_upper_bounds_le_1": True,
                "all_throughput_ratio_bootstrap_lower_bounds_ge_1": True,
                "artifact_ratio_bootstrap_upper_bound_le_1": True,
                "fit_time_ratio_bootstrap_upper_bound_le_1": True,
            },
            "efficiency_results_may_not_change_accuracy_selection": True,
        },
        "integrated_claim_tiers": {
            "tier1_accuracy_robustness_external_and_deployability_requires": [
                "krc_primary88_confirmation",
                "fresh_two_dataset_external_malicious_confirmation",
                "selected_system_deployability",
                "parrot_external_benign_safety",
            ],
            "tier2_multidimensional_comprehensive_sota_additionally_requires": [
                "strict_efficiency_superiority_over_embedded_pairwise",
                "strict_efficiency_superiority_over_opendetect",
            ],
            "all_gates_without_dataset_metric_seed_suite_or_component_splicing": (
                True
            ),
            "universal_sota_claim_is_never_authorized": True,
        },
        "required_future_implementation": {
            "external_malicious": [
                "KRC external capture and evaluator",
                "paired OpenDetect evaluator",
                "summary and independent audit",
            ],
            "parrot_safety": [
                "KRC and OpenDetect deployment bundles",
                "320-capture no-decryption replay",
                "capture-block bootstrap summary and independent audit",
            ],
            "selected_system_efficiency": [
                "same-process paired benchmark",
                "resource and artifact measurement",
                "scenario-blocked summary and independent audit",
            ],
            "integrated": ["all-branch canonical evidence auditor"],
        },
        "output_counts_at_freeze": observed_counts,
        "input_manifest_sha256": {
            "krc_confirmation_protocol": krc_protocol["manifest_sha256"],
            "external_malicious_design": external_design["manifest_sha256"],
            "parrot_safety_design": parrot_design["manifest_sha256"],
            "parrot_feature_protocol": parrot_features["manifest_sha256"],
            "efficiency_protocol": efficiency_protocol["manifest_sha256"],
            "comparative_protocol": comparative_protocol["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": {
            "create_strict_v4_krc_downstream_sota_design.py": creator_sha256
        },
        "claim_boundary": {
            "design_freeze_does_not_authorize_execution": True,
            "krc_confirmation_success_alone_does_not_establish_sota": True,
            "parrot_is_benign_safety_not_malicious_accuracy_evidence": True,
            "efficiency_failure_preserves_accuracy_result_but_blocks_tier2": (
                True
            ),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--external-design", type=Path, required=True)
    parser.add_argument("--parrot-design", type=Path, required=True)
    parser.add_argument("--parrot-features", type=Path, required=True)
    parser.add_argument("--efficiency-protocol", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--downstream-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "krc_confirmation_protocol": args.krc_protocol.resolve(),
        "external_malicious_design": args.external_design.resolve(),
        "parrot_safety_design": args.parrot_design.resolve(),
        "parrot_feature_protocol": args.parrot_features.resolve(),
        "efficiency_protocol": args.efficiency_protocol.resolve(),
        "comparative_protocol": args.comparative_protocol.resolve(),
    }
    implementation = Path(__file__).resolve()
    value = create(
        project_root=args.project_root.resolve(),
        krc_protocol=load_json(paths["krc_confirmation_protocol"]),
        external_design=load_json(paths["external_malicious_design"]),
        parrot_design=load_json(paths["parrot_safety_design"]),
        parrot_features=load_json(paths["parrot_feature_protocol"]),
        efficiency_protocol=load_json(paths["efficiency_protocol"]),
        comparative_protocol=load_json(paths["comparative_protocol"]),
        observed_counts=output_counts(args.downstream_root.resolve()),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        creator_sha256=file_hash(implementation),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

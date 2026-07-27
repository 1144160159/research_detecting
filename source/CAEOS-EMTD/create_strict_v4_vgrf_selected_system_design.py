from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def create_design(
    *,
    project_root: Path,
    coverage: dict[str, Any],
    integrated: dict[str, Any],
    efficiency: dict[str, Any],
    corruption: dict[str, Any],
    pilot: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_system_outputs: int,
) -> dict[str, Any]:
    require_canonical(
        coverage, "strict_v4_coverage_manifest_v2", "coverage"
    )
    require_canonical(
        integrated,
        "strict_v4_integrated_comprehensive_sota_design_v2",
        "integrated SOTA v2 design",
    )
    require_canonical(
        efficiency,
        "strict_v4_final_efficiency_protocol_v2",
        "final efficiency protocol",
    )
    require_canonical(
        corruption,
        "strict_v4_postselection_corruption_protocol_v1",
        "post-selection corruption protocol",
    )
    require_canonical(
        pilot,
        "strict_v4_validation_gated_reliability_fusion_protocol_v1",
        "VGRF pilot protocol",
    )
    registry = coverage.get("scenario_registry", {})
    scenarios = [
        {"suite": suite, "scenario": scenario}
        for suite in sorted(registry)
        for scenario in registry[suite]["scenarios"]
    ]
    if len(registry) != 7 or len(scenarios) != 102:
        raise ValueError("VGRF system design requires the full 102 scenarios")
    efficiency_seeds = [311, 313]
    robustness_seeds = [311, 313, 317]
    if observed_system_outputs != 0:
        raise ValueError("VGRF system design must freeze before outputs")
    families = corruption["full102_confirmation"][
        "corruption_families"
    ]
    if len(families) != 5:
        raise ValueError("exactly five corruption families are required")
    sentinel = efficiency["training_calibration_benchmark"][
        "sentinel_scenarios"
    ]
    if set(sentinel) != set(registry):
        raise ValueError("training sentinel suite universe mismatch")
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_confirmation_design_v1"
        ),
        "status": (
            "conditional_frozen_before_final_selection_and_system_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "selected_algorithm": VGRF,
        "activation_gate": {
            "final_selection_schema": (
                "strict_v4_final_self_algorithm_selection_v1"
            ),
            "selected_algorithm_must_equal": VGRF,
            "vgrf_full102_confirmation_passes": True,
            "pairwise_selection_writes_canonical_not_required_record": True,
        },
        "scenario_registry": scenarios,
        "scenario_count": 102,
        "seed_policy": {
            "selection_and_efficiency_seeds": efficiency_seeds,
            "comparative_robustness_seeds": robustness_seeds,
            "third_seed_rule": (
                "smallest_prime_strictly_greater_than_313_fixed_"
                "before_vgrf_selection"
            ),
            "third_seed_is_not_selected_from_effects": True,
        },
        "runtime_equivalence_and_efficiency": {
            "expected_blocks": 204,
            "block_formula": "102_scenarios_x_2_selection_seeds",
            "batch_sizes": efficiency["inference_benchmark"][
                "batch_sizes"
            ],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": (
                "alternate_vgrf_and_opendetect_by_repetition"
            ),
            "same_hardware_and_exclusive_machine_required": True,
            "fit_once_then_time_full_forward_and_risk_transform": True,
            "scores_npz_only_postprocessing_is_not_model_inference": True,
            "equivalence": {
                "probability_prediction_risk_rejection_exact": True,
                "stable_runtime_risk_tolerance": 1e-12,
                "source_empirical_tail_difference_is_diagnostic_only": True,
                "unknown_or_test_labels_used": False,
            },
            "reported_metrics": [
                "latency_p50_ms",
                "latency_p95_ms",
                "latency_p99_ms",
                "samples_per_second",
                "peak_gpu_memory_mb",
                "peak_host_rss_mb",
                "serialized_deployment_artifact_bytes",
            ],
            "superiority_gate": {
                "all_latency_ratio_bootstrap_upper_bounds_le_1": True,
                "all_throughput_ratio_bootstrap_lower_bounds_ge_1": True,
                "artifact_ratio_bootstrap_upper_bound_le_1": True,
                "failure_is_reported_without_runtime_splicing": True,
            },
        },
        "training_calibration_efficiency": {
            "sentinel_scenarios": sentinel,
            "seeds": efficiency_seeds,
            "expected_pairs": 14,
            "clean_process_repetitions": 3,
            "reported_metrics": [
                "feature_preparation_seconds",
                "training_seconds",
                "calibration_seconds",
                "total_fit_seconds",
                "peak_gpu_memory_mb",
                "peak_host_rss_mb",
                "serialized_deployment_artifact_bytes",
            ],
            "all_cost_ratio_bootstrap_upper_bounds_le_1": True,
        },
        "comparative_corruption": {
            "source_pair_count": 306,
            "source_pair_formula": "102_scenarios_x_3_frozen_seeds",
            "families": families,
            "family_count": 5,
            "fixed_severity": corruption["full102_confirmation"][
                "fixed_severity"
            ],
            "modality_selection_rule": corruption[
                "full102_confirmation"
            ]["modality_selection_rule"],
            "corruption_seed": corruption["execution_gate"][
                "corruption_seed"
            ],
            "expected_paired_condition_evaluations": 1530,
            "condition_formula": "306_source_pairs_x_5_families",
            "average_three_seeds_inside_scenario": True,
            "bootstrap_repetitions": 20000,
            "holm_family": (
                "six_degradation_advantage_metrics_within_each_family"
            ),
            "metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
                "ece",
            ],
            "all_five_families_and_all_six_metrics_required": True,
            "all_mean_ci_and_holm_gates_required": True,
        },
        "required_output": {
            "schema_version": (
                "strict_v4_vgrf_selected_system_confirmation_summary_v1"
            ),
            "equivalence_block_count": 204,
            "comparative_corruption_pair_count": 1530,
            "required_system_gates": integrated[
                "selected_system_evidence_contract"
            ]["required_system_gates"],
            "metric_wise_or_suite_wise_splicing_forbidden": True,
        },
        "execution_protocol_requirements": {
            "freeze_after_positive_vgrf_selection_before_system_metrics": True,
            "bind_final_selection_protocol_summary_and_files": True,
            "bind_all_306_candidate_and_opendetect_source_artifacts": True,
            "bind_runtime_capture_benchmark_corruption_and_summary_code": True,
            "all_outputs_resumable_and_hash_validated": True,
        },
        "claim_boundary": {
            "design_has_no_effect_metrics": True,
            "vgrf_accuracy_confirmation_does_not_replace_system_gates": True,
            "pairwise_system_results_cannot_be_relabelled_as_vgrf": True,
            "any_failed_system_gate_blocks_comprehensive_sota": True,
        },
        "input_manifest_sha256": {
            "coverage": coverage["manifest_sha256"],
            "integrated_v2": integrated["manifest_sha256"],
            "efficiency": efficiency["manifest_sha256"],
            "corruption": corruption["manifest_sha256"],
            "vgrf_pilot": pilot["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "system_outputs_observed_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--integrated-v2", type=Path, required=True)
    parser.add_argument("--efficiency-protocol", type=Path, required=True)
    parser.add_argument("--corruption-protocol", type=Path, required=True)
    parser.add_argument("--vgrf-pilot-protocol", type=Path, required=True)
    parser.add_argument("--system-run-root", type=Path, required=True)
    parser.add_argument("--system-result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "coverage": args.coverage,
        "integrated_v2": args.integrated_v2,
        "efficiency": args.efficiency_protocol,
        "corruption": args.corruption_protocol,
        "vgrf_pilot": args.vgrf_pilot_protocol,
    }
    observed = 0
    for root in (args.system_run_root, args.system_result_root):
        if root.exists():
            observed += len(
                [
                    path
                    for path in root.rglob("*")
                    if path.is_file()
                    and path.name
                    in {
                        "metrics.json",
                        "paired_corruption.json",
                        "summary.json",
                    }
                ]
            )
    creator = Path(__file__).resolve()
    value = create_design(
        project_root=args.project_root,
        coverage=load(args.coverage),
        integrated=load(args.integrated_v2),
        efficiency=load(args.efficiency_protocol),
        corruption=load(args.corruption_protocol),
        pilot=load(args.vgrf_pilot_protocol),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        implementation_sha256={
            "create_strict_v4_vgrf_selected_system_design.py": file_hash(
                creator
            )
        },
        observed_system_outputs=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

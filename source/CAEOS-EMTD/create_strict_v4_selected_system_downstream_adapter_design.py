from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
FORMAL_OUTPUTS = (
    "activation.json",
    "selected_system_protocol.json",
    "external_malicious_protocol.json",
    "parrot_safety_protocol.json",
    "efficiency_protocol.json",
    "integrated_audit.json",
    "execution_complete.json",
)
IMPLEMENTATION_FILES = (
    "caeos/pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/rrc_csr_runtime.py",
    "caeos/selected_system_runtime.py",
)


def load_canonical(path: Path, schema: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {schema} required: {path}")
    return value


def output_counts(result_root: Path) -> dict[str, int]:
    return {
        name: int((result_root / name).is_file())
        for name in FORMAL_OUTPUTS
    }


def build_design(
    *,
    krc_protocol: dict[str, Any],
    rrc_implementation: dict[str, Any],
    pug_cross_suite_design: dict[str, Any],
    direct_tournament_design: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    creator_sha256: str,
    observed_output_counts: dict[str, int],
) -> dict[str, Any]:
    if any(observed_output_counts.values()):
        raise ValueError("downstream adapter design requires zero formal output")
    if set(implementation_sha256) != set(IMPLEMENTATION_FILES):
        raise ValueError("complete selected-system runtime implementation required")
    if (
        krc_protocol.get("execution_admitted") is not True
        or rrc_implementation.get("execution_admitted") is not False
        or pug_cross_suite_design.get("confirmation_universe", {}).get(
            "scenario_count"
        )
        != 102
        or direct_tournament_design.get("confirmation_universe", {}).get(
            "scenario_count"
        )
        != 102
    ):
        raise ValueError("frozen self-algorithm source contracts drifted")

    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_selected_system_downstream_adapter_design_v1"
        ),
        "state": "frozen_before_final_self_algorithm_selection",
        "activation": {
            "requires_final_self_algorithm_selection": True,
            "allowed_selected_algorithms": list(ALGORITHMS),
            "selected_algorithm_must_match_runtime_evidence": True,
            "selection_manifest_and_file_sha256_must_be_bound": True,
            "partial_or_inconsistent_selection_fails_closed": True,
            "formal_outputs_must_be_zero_before_activation": True,
        },
        "runtime_contract": {
            "schema_version": "strict_v4_selected_system_runtime_v1",
            "required_input": "aligned_56_column_three_modality_views",
            "required_output": [
                "prediction",
                "probability",
                "risk",
            ],
            "prediction_must_equal_probability_argmax": True,
            "probability_rows_must_sum_to_one": True,
            "probability_and_risk_range": [0.0, 1.0],
            "threshold_source": "known_validation_only",
            "unknown_or_test_labels_used_for_fit_selection_or_threshold": (
                False
            ),
            "supported_source_runtime": {
                "caeos_pairwise": {
                    "schema": "strict_v4_pairwise_runtime_v2",
                    "selected_risk_excludes": [
                        "caeos_pug_continuous_outer_min_p"
                    ],
                },
                "krc_csr_caeos_v1": {
                    "schema": "strict_v4_krc_csr_runtime_v1",
                },
                "rrc_csr_caeos_v1": {
                    "schema": "strict_v4_rrc_csr_runtime_v1",
                },
                "caeos_pug": {
                    "schema": "strict_v4_pairwise_runtime_v2",
                    "selected_risk_equals": (
                        "caeos_pug_continuous_outer_min_p"
                    ),
                },
            },
        },
        "external_malicious_branch": {
            "fresh_retraining_per_external_split": True,
            "selected_algorithm_policy_is_fixed_before_test_evaluation": True,
            "candidate_runtime_is_materialized_through_common_adapter": True,
            "fresh_opendetect_comparator_required": True,
            "existing_attack_family_block_bootstrap_and_holm_gates_preserved": (
                True
            ),
            "external_success_is_required_but_not_sufficient_for_sota": True,
        },
        "parrot_benign_safety_branch": {
            "candidate_refit_recalibration_or_selection_on_parrot": False,
            "full_56_column_order_must_match": True,
            "capture_groups_are_indivisible": True,
            "measures_unknown_benign_false_alarm_and_attack_misassignment": (
                True
            ),
            "does_not_treat_benign_as_attack_subclassification": True,
            "domain_benign_reference_and_opendetect_comparator_required": True,
            "existing_one_sided_safety_bounds_preserved": True,
        },
        "efficiency_branch": {
            "same_gpu_host_and_software_environment": True,
            "clean_process_training_runs_per_method": 3,
            "batch_sizes": [1, 64, 512],
            "warmup_and_measurement_schedule_must_match": True,
            "adapter_overhead_is_included": True,
            "reports_latency_p50_p95_p99_throughput_memory_and_fit_time": True,
            "efficiency_failure_does_not_cancel_accuracy_result": True,
        },
        "integrated_audit": {
            "binds_final_selection_runtime_and_three_downstream_branches": True,
            "integrity_pass_is_separate_from_effect_pass": True,
            "all_existing_comprehensive_sota_gates_are_preserved": True,
            "algorithm_directory_renaming_or_result_splicing_is_forbidden": True,
        },
        "implementation_status_at_freeze": {
            "common_runtime_adapter_complete": True,
            "runtime_implementation_sha256": dict(
                sorted(implementation_sha256.items())
            ),
            "remaining_components": [
                "final_selection_activation_writer",
                "algorithm_neutral_external_protocol_and_runner",
                "algorithm_neutral_parrot_protocol_and_runner",
                "algorithm_neutral_efficiency_protocol_and_runner",
                "algorithm_neutral_integrated_auditor",
                "resource_safe_conditional_watcher",
            ],
        },
        "formal_output_counts_at_freeze": observed_output_counts,
        "execution_admitted_at_freeze": False,
        "input_manifest_sha256": {
            "krc_protocol": krc_protocol["manifest_sha256"],
            "rrc_execution_implementation": rrc_implementation[
                "manifest_sha256"
            ],
            "pug_cross_suite_design": pug_cross_suite_design[
                "manifest_sha256"
            ],
            "direct_tournament_design": direct_tournament_design[
                "manifest_sha256"
            ],
        },
        "input_file_sha256": dict(sorted(input_file_sha256.items())),
        "implementation_sha256": {
            "create_strict_v4_selected_system_downstream_adapter_design.py": (
                creator_sha256
            )
        },
        "claim_boundary": {
            "common_runtime_support_is_not_downstream_execution": True,
            "design_is_not_external_safety_efficiency_or_sota_effect": True,
            "krc_specific_results_cannot_substitute_for_rrc_or_pug": True,
            "final_selected_algorithm_must_drive_every_downstream_branch": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--rrc-implementation", type=Path, required=True)
    parser.add_argument("--pug-cross-suite-design", type=Path, required=True)
    parser.add_argument("--direct-tournament-design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    paths = {
        "krc_protocol": resolve(args.krc_protocol),
        "rrc_execution_implementation": resolve(args.rrc_implementation),
        "pug_cross_suite_design": resolve(args.pug_cross_suite_design),
        "direct_tournament_design": resolve(args.direct_tournament_design),
    }
    sources = {
        relative: root / relative for relative in IMPLEMENTATION_FILES
    }
    creator = Path(__file__).resolve()
    output = resolve(args.output)
    design = build_design(
        krc_protocol=load_canonical(
            paths["krc_protocol"],
            "strict_v4_krc_csr_confirmation_protocol_v1",
        ),
        rrc_implementation=load_canonical(
            paths["rrc_execution_implementation"],
            "strict_v4_rrc_csr_execution_implementation_protocol_v1",
        ),
        pug_cross_suite_design=load_canonical(
            paths["pug_cross_suite_design"],
            "strict_v4_pug_cross_suite_confirmation_design_v1",
        ),
        direct_tournament_design=load_canonical(
            paths["direct_tournament_design"],
            "strict_v4_self_algorithm_direct_tournament_design_v1",
        ),
        input_file_sha256={
            path.relative_to(root).as_posix(): file_hash(path)
            for path in paths.values()
        },
        implementation_sha256={
            relative: file_hash(path) for relative, path in sources.items()
        },
        creator_sha256=file_hash(creator),
        observed_output_counts=output_counts(resolve(args.result_root)),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and json.loads(output.read_text(encoding="utf-8")) != design:
        raise ValueError("existing downstream adapter design is immutable")
    if not output.exists():
        temporary = output.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(design, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output)
    print(f"manifest_sha256={design['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()

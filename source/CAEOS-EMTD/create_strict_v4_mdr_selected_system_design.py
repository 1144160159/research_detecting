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
    efficiency_v2: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    creator_sha256: str,
    observed_outputs: int,
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
        efficiency_v2,
        "strict_v4_final_efficiency_protocol_v2",
        "efficiency v2 protocol",
    )
    if int(observed_outputs) != 0:
        raise ValueError("MDR system design must freeze before outputs")
    parent = postselection["selected_system_evidence"]
    reserved = mdr_design["reserved_confirmation"]
    if (
        reserved["scenario_count"] != 102
        or reserved["training_seeds"] != [347, 349, 353]
        or parent["same_hardware_benchmark"]["batch_sizes"]
        != [1, 64, 512]
    ):
        raise ValueError("MDR selected-system parent contract drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_selected_system_design_v1",
        "status": (
            "conditional_frozen_before_mdr_selection_confirmation_"
            "and_system_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "activation_gate": postselection["activation_gate"],
        "source_runtime_contract": {
            "confirmation_scenario_count": 102,
            "training_seeds": [347, 349, 353],
            "expected_capture_count": 306,
            "source_schema": "strict_v4_mdr_caeos_runtime_capture_v1",
            "all_capture_artifact_and_input_hashes_must_match": True,
            "source_confirmation_must_pass_independent_audit": True,
        },
        "deployment_equivalence": parent["deployment_equivalence"],
        "same_hardware_inference": {
            **parent["same_hardware_benchmark"],
            "comparison": "mdr_runtime_vs_embedded_clean_runtime",
            "same_inputs_and_process_required": True,
            "method_order": "alternate_by_timed_repetition",
            "threads_and_cpu_affinity_recorded": True,
            "gpu_is_not_used_by_either_mdr_or_embedded_pairwise": True,
            "cross_process_or_retraining_comparison_forbidden": True,
        },
        "training_and_artifact_cost": {
            "source": "the_same_306_confirmation_capture_manifests",
            "mdr_fit_wall_seconds": (
                "clean_capture_wall_seconds_plus_"
                "robust_capture_wall_seconds"
            ),
            "pairwise_fit_wall_seconds": "clean_capture_wall_seconds",
            "mdr_artifact_bytes": "runtime_artifact_bytes",
            "pairwise_artifact_bytes": (
                "serialize_embedded_clean_runtime_with_same_joblib_settings"
            ),
            "calibration_overhead_not_timed_separately": True,
            "reported_as_lower_bound_on_total_mdr_build_cost": True,
        },
        "aggregation": {
            "average_three_training_seeds_within_scenario_first": True,
            "scenario_block_count": 102,
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260724,
            "suite_equal_secondary_summary": True,
            "raw_per_capture_values_retained": True,
        },
        "deployability_gate": parent["deployability_gate"],
        "strict_efficiency_superiority_gate": parent[
            "strict_efficiency_superiority_gate"
        ],
        "required_output": {
            "schema_version": "strict_v4_mdr_selected_system_summary_v1",
            "capture_count": 306,
            "scenario_block_count": 102,
            "all_equivalence_and_deployability_checks_required": True,
            "strict_efficiency_gate_reported_separately": True,
        },
        "required_implementation": [
            "create_strict_v4_mdr_selected_system_protocol.py",
            "benchmark_mdr_selected_system_runtime.py",
            "run_strict_v4_mdr_selected_system.py",
            "summarize_strict_v4_mdr_selected_system.py",
            "audit_strict_v4_mdr_selected_system.py",
            "scripts/wait_and_run_strict_v4_mdr_selected_system.sh",
        ],
        "claim_boundary": {
            "deployability_pass_does_not_imply_efficiency_sota": True,
            "strict_efficiency_failure_is_preserved": True,
            "fit_cost_is_a_declared_lower_bound_not_full_pipeline_time": True,
            "pairwise_vgrf_or_opendetect_system_results_not_inherited": True,
            "no_metric_scenario_suite_or_component_splicing": True,
        },
        "input_manifest_sha256": {
            "postselection_design": postselection["manifest_sha256"],
            "mdr_design": mdr_design["manifest_sha256"],
            "efficiency_v2": efficiency_v2["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": {
            "create_strict_v4_mdr_selected_system_design.py": (
                creator_sha256
            )
        },
        "system_output_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--efficiency-v2", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "postselection_design": args.postselection_design,
        "mdr_design": args.mdr_design,
        "efficiency_v2": args.efficiency_v2,
    }
    observed = (
        len(list(args.run_root.glob("**/benchmark.json")))
        if args.run_root.exists()
        else 0
    )
    implementation = Path(__file__).resolve()
    value = create_design(
        project_root=args.project_root,
        postselection=load(args.postselection_design),
        mdr_design=load(args.mdr_design),
        efficiency_v2=load(args.efficiency_v2),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        creator_sha256=file_hash(implementation),
        observed_outputs=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

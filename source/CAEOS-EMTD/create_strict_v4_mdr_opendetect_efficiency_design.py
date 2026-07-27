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
    selected_system: Dict[str, Any],
    comparative: Dict[str, Any],
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
        selected_system,
        "strict_v4_mdr_selected_system_design_v1",
        "MDR selected-system design",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative protocol",
    )
    require_canonical(
        efficiency_v2,
        "strict_v4_final_efficiency_protocol_v2",
        "efficiency v2",
    )
    if int(observed_outputs) != 0:
        raise ValueError("MDR OpenDetect efficiency design requires zero outputs")
    seed137 = [
        item
        for item in comparative["source_registry"]
        if int(item["seed"]) == 137
    ]
    identities = {
        (str(item["suite"]), str(item["scenario"])) for item in seed137
    }
    if len(seed137) != 102 or len(identities) != 102:
        raise ValueError("OpenDetect registry must cover 102 seed137 scenarios")
    benchmark = selected_system["same_hardware_inference"]
    if (
        benchmark["batch_sizes"] != [1, 64, 512]
        or int(benchmark["warmup_repetitions"]) != 5
        or int(benchmark["timed_repetitions"]) != 30
    ):
        raise ValueError("MDR system benchmark policy drifted")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_opendetect_efficiency_design_v1"
        ),
        "status": (
            "conditional_frozen_before_mdr_selection_and_efficiency_outputs"
        ),
        "project_root": str(project_root.resolve()),
        "activation_gate": postselection["activation_gate"],
        "source_matrix": {
            "scenario_count": 102,
            "candidate_training_seeds": [347, 349, 353],
            "candidate_capture_count": 306,
            "comparator_seed": 137,
            "comparator_runtime_count": 102,
            "candidate_and_comparator_receive_exact_same_processed_arrays": True,
            "comparator_seed_reuse_is_allowed_for_runtime_efficiency_only": True,
        },
        "benchmark": {
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": "alternate_by_timed_repetition",
            "candidate": "mdr_caeos_v1",
            "comparator": "opendetect",
            "candidate_native_device": "cpu",
            "comparator_native_device": "frozen_runtime_device",
            "gpu_synchronization_required_for_opendetect": True,
            "same_process_and_input_required": True,
            "exclusive_machine_preflight_required": True,
        },
        "cost": {
            "mdr_fit_seconds_lower_bound": (
                "clean_capture_wall_seconds_plus_robust_capture_wall_seconds"
            ),
            "opendetect_fit_seconds": (
                "frozen_source_metrics_elapsed_seconds"
            ),
            "artifact_bytes_from_exact_benchmarked_runtimes": True,
        },
        "aggregation": {
            "average_three_mdr_training_seeds_within_scenario_first": True,
            "scenario_block_count": 102,
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260724,
            "suite_equal_secondary_summary": True,
            "raw_per_capture_ratios_retained": True,
        },
        "strict_efficiency_superiority_gate": {
            "all_latency_ratio_bootstrap_upper_bounds_le_1": True,
            "all_throughput_ratio_bootstrap_lower_bounds_ge_1": True,
            "artifact_ratio_bootstrap_upper_bound_le_1": True,
            "fit_time_ratio_bootstrap_upper_bound_le_1": True,
        },
        "required_output": {
            "schema_version": (
                "strict_v4_mdr_opendetect_efficiency_summary_v1"
            ),
            "benchmark_count": 306,
            "scenario_block_count": 102,
        },
        "required_implementation": [
            "create_strict_v4_mdr_opendetect_efficiency_protocol.py",
            "benchmark_mdr_opendetect_runtime.py",
            "run_strict_v4_mdr_opendetect_efficiency.py",
            "summarize_strict_v4_mdr_opendetect_efficiency.py",
            "audit_strict_v4_mdr_opendetect_efficiency.py",
            "scripts/wait_and_run_strict_v4_mdr_opendetect_efficiency.sh",
        ],
        "claim_boundary": {
            "strict_efficiency_failure_blocks_only_multidimensional_sota": True,
            "does_not_change_accuracy_or_robustness_selection": True,
            "opendetect_seed137_reuse_does_not_support_effectiveness_claim": True,
            "no_metric_scenario_suite_or_component_splicing": True,
        },
        "input_manifest_sha256": {
            "postselection_design": postselection["manifest_sha256"],
            "selected_system_design": selected_system["manifest_sha256"],
            "comparative_protocol": comparative["manifest_sha256"],
            "efficiency_v2": efficiency_v2["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": {
            "create_strict_v4_mdr_opendetect_efficiency_design.py": (
                creator_sha256
            )
        },
        "benchmark_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument("--selected-system-design", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--efficiency-v2", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "postselection_design": args.postselection_design,
        "selected_system_design": args.selected_system_design,
        "comparative_protocol": args.comparative_protocol,
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
        selected_system=load(args.selected_system_design),
        comparative=load(args.comparative_protocol),
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

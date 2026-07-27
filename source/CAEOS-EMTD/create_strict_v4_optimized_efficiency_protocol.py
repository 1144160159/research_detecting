from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def load_manifest(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected schema in {path}")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"canonical hash mismatch in {path}")
    return payload


def create_protocol(
    *,
    v5_protocol: dict[str, Any],
    v5_plan: dict[str, Any],
    v5_protocol_file_sha256: str,
    v5_plan_file_sha256: str,
    implementation_sha256: dict[str, str],
    optimized_results_observed: int,
    source_v5_metrics_observed: int,
    source_v5_complete_at_freeze: bool,
) -> dict[str, Any]:
    if v5_plan.get("protocol_manifest_sha256") != v5_protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("v5 plan/protocol binding mismatch")
    blocks = v5_plan.get("inference_blocks", [])
    scenarios = [
        {"suite": str(block["suite"]), "scenario": str(block["scenario"])}
        for block in blocks
    ]
    if len(scenarios) != 102 or len(
        {(row["suite"], row["scenario"]) for row in scenarios}
    ) != 102:
        raise ValueError("v5 inference scope must contain 102 unique scenarios")
    if optimized_results_observed != 0:
        raise ValueError("optimized protocol must freeze before triad metrics exist")
    required_hashes = {
        "pairwise_runtime",
        "optimized_pairwise_runtime",
        "open_detect_runtime",
        "triad_block_runner",
        "triad_matrix_runner",
        "triad_summarizer",
        "protocol_creator",
    }
    if set(implementation_sha256) != required_hashes or any(
        len(value) != 64 for value in implementation_sha256.values()
    ):
        raise ValueError("optimized protocol implementation registry is incomplete")
    protocol = {
        "schema_version": "strict_v4_optimized_efficiency_protocol_v1",
        "status": "frozen_before_optimized_metrics",
        "source_v5_protocol_manifest_sha256": v5_protocol["manifest_sha256"],
        "source_v5_plan_manifest_sha256": v5_plan["manifest_sha256"],
        "source_files_sha256": {
            "v5_protocol": v5_protocol_file_sha256,
            "v5_plan": v5_plan_file_sha256,
        },
        "source_v5_state_at_freeze": {
            "efficiency_metrics_observed": int(source_v5_metrics_observed),
            "recovery_complete": bool(source_v5_complete_at_freeze),
            "used_for_optimized_parameter_selection": False,
        },
        "optimized_results_observed_at_freeze": 0,
        "scenario_count": 102,
        "scenarios": scenarios,
        "methods": {
            "original": "caeos_pairwise_stable_runtime",
            "optimized": "caeos_pairwise_demand_driven_exact",
            "comparator": "opendetect",
        },
        "measurement_modes": ["native_primary", "cpu_normalized_secondary"],
        "benchmark": {
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": "three_method_latin_square_by_repetition_modulo_3",
            "exclusive_machine_required": True,
        },
        "equivalence_gate": {
            "scope": "all_input_rows_in_every_scenario",
            "prediction_array_equal": True,
            "probability_max_absolute_difference": 1e-12,
            "risk_max_absolute_difference": 1e-12,
            "unknown_or_test_labels_used": False,
        },
        "deployment_target": {
            "optimized_over_original_p99_latency_ratio_maximum": 0.5,
            "optimized_over_original_throughput_ratio_minimum": 2.0,
            "optimized_over_original_artifact_size_ratio_maximum": 1.0,
            "required_for_every_mode_and_batch": True,
            "failure_does_not_change_accuracy_incumbent": True,
        },
        "claim_policy": {
            "v5_original_results_are_not_overwritten": True,
            "no_speed_claim_from_nonisolated_diagnostics": True,
            "no_opendetect_superiority_claim_without_102_scenario_ci": True,
            "accuracy_selection_is_independent": True,
        },
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v5-protocol", type=Path, required=True)
    parser.add_argument("--v5-plan", type=Path, required=True)
    parser.add_argument("--v5-formal-root", type=Path, required=True)
    parser.add_argument("--v5-summary-root", type=Path, required=True)
    parser.add_argument("--optimized-result-root", type=Path, required=True)
    parser.add_argument("--pairwise-runtime", type=Path, required=True)
    parser.add_argument("--optimized-runtime", type=Path, required=True)
    parser.add_argument("--open-detect-runtime", type=Path, required=True)
    parser.add_argument("--block-runner", type=Path, required=True)
    parser.add_argument("--matrix-runner", type=Path, required=True)
    parser.add_argument("--summarizer", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    v5_protocol = load_manifest(
        args.v5_protocol, "strict_v4_final_efficiency_protocol_v2"
    )
    v5_plan = load_manifest(
        args.v5_plan, "strict_v4_final_efficiency_execution_plan_v2"
    )
    optimized_observed = sum(
        1 for _ in args.optimized_result_root.rglob("triad_metrics.json")
    )
    protocol = create_protocol(
        v5_protocol=v5_protocol,
        v5_plan=v5_plan,
        v5_protocol_file_sha256=file_hash(args.v5_protocol),
        v5_plan_file_sha256=file_hash(args.v5_plan),
        implementation_sha256={
            "pairwise_runtime": file_hash(args.pairwise_runtime),
            "optimized_pairwise_runtime": file_hash(args.optimized_runtime),
            "open_detect_runtime": file_hash(args.open_detect_runtime),
            "triad_block_runner": file_hash(args.block_runner),
            "triad_matrix_runner": file_hash(args.matrix_runner),
            "triad_summarizer": file_hash(args.summarizer),
            "protocol_creator": file_hash(Path(__file__)),
        },
        optimized_results_observed=optimized_observed,
        source_v5_metrics_observed=sum(
            1 for _ in args.v5_formal_root.rglob("efficiency_metrics.json")
        ),
        source_v5_complete_at_freeze=(
            args.v5_summary_root / "recovery_complete"
        ).is_file(),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / "protocol_manifest.json"
    path.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol, sort_keys=True))


if __name__ == "__main__":
    main()

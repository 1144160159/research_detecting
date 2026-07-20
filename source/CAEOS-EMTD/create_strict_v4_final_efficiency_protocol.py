from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def _sentinel(coverage_sha: str, suite: str, scenarios: list[str]) -> str:
    if not scenarios:
        raise ValueError(f"suite {suite} has no scenarios")
    digest = hashlib.sha256(f"{coverage_sha}:{suite}".encode("utf-8")).hexdigest()
    return scenarios[int(digest[:16], 16) % len(scenarios)]


def create_protocol(
    coverage: dict[str, Any], efficiency_audit: dict[str, Any]
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    if coverage.get("datasets") != 7 or coverage.get("scenario_inference_units") != 102:
        raise ValueError("efficiency protocol requires the frozen 7-dataset 102-scenario registry")
    coverage_sha = coverage.get("manifest_sha256")
    if not isinstance(coverage_sha, str) or len(coverage_sha) != 64:
        raise ValueError("coverage manifest SHA is missing")
    if efficiency_audit.get("schema_version") != "strict_v4_efficiency_evidence_audit_v1":
        raise ValueError("unexpected efficiency audit schema")

    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict) or len(registry) != 7:
        raise ValueError("scenario registry is incomplete")
    sentinels = {}
    for suite in sorted(registry):
        record = registry[suite]
        scenarios = record.get("scenarios") if isinstance(record, dict) else None
        if not isinstance(scenarios, list) or len(scenarios) != record.get("count"):
            raise ValueError(f"invalid scenario registry for {suite}")
        sentinels[suite] = _sentinel(coverage_sha, suite, scenarios)

    result = {
        "schema_version": "strict_v4_final_efficiency_protocol_v1",
        "status": "frozen_before_final_self_algorithm_selection",
        "purpose": "controlled post-selection efficiency comparison, separate from SOTA accuracy gates",
        "coverage_manifest_sha256": coverage_sha,
        "pre_audit_implementation_sha256": efficiency_audit.get(
            "audit_implementation_sha256"
        ),
        "pre_audit_direct_comparison_allowed": efficiency_audit.get(
            "direct_efficiency_comparison_allowed"
        )
        is True,
        "execution_gate": {
            "requires_optimal_self_algorithm_decision": True,
            "requires_external_comparator_confirmation_complete": True,
            "must_not_run_concurrently_with_confirmatory_accuracy_matrices": True,
        },
        "methods": {
            "candidate": "selected_algorithm_from_strict_v4_optimal_self_algorithm_decision_v1",
            "comparator": "opendetect",
            "router_accounting_rule": (
                "if the selected candidate is the domain-safe router, include every "
                "CAEOS and MLP/OpenMax component invoked by that route"
            ),
        },
        "hardware_control": {
            "same_gpu_and_cpu_for_both_methods": True,
            "exclusive_single_process_measurement": True,
            "outer_scenario_workers": 1,
            "record_gpu_name_driver_cuda_torch_cpu_ram": True,
            "synchronize_cuda_before_and_after_each_timed_region": True,
        },
        "inference_benchmark": {
            "scenario_scope": "all_102_frozen_scenarios",
            "saved_artifacts_only_no_refit": True,
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "batch_sizes": [1, 64, 512],
            "metrics": [
                "latency_p50_ms",
                "latency_p95_ms",
                "latency_p99_ms",
                "samples_per_second",
                "peak_gpu_memory_mb",
            ],
            "aggregation": "scenario-blocked median and bootstrap_95ci; seeds are not pooled as independent scenarios",
        },
        "training_calibration_benchmark": {
            "selection_rule": "one SHA-indexed scenario per dataset; independent of accuracy results",
            "sentinel_scenarios": sentinels,
            "fresh_timing_seed": 191,
            "clean_repetitions": 3,
            "metrics": [
                "feature_preparation_seconds",
                "training_seconds",
                "calibration_seconds",
                "total_fit_seconds",
                "peak_gpu_memory_mb",
                "peak_host_rss_mb",
                "trainable_parameters",
                "serialized_artifact_bytes",
            ],
        },
        "claim_policy": {
            "accuracy_selection_must_not_use_efficiency_results": True,
            "report_tradeoffs_even_if_candidate_is_slower": True,
            "no_direct_efficiency_claim_until_every_required_field_is_complete": True,
            "do_not_compare_existing_elapsed_seconds_with_training_seconds": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(protocol: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 final efficiency protocol",
        "",
        f"Protocol SHA: `{protocol['manifest_sha256']}`.",
        "",
        "Execution is gated on final self-algorithm selection and external confirmation.",
        "Accuracy selection cannot use efficiency results.",
        "",
        "## Training sentinels",
        "",
    ]
    for suite, scenario in protocol["training_calibration_benchmark"][
        "sentinel_scenarios"
    ].items():
        lines.append(f"- `{suite}`: `{scenario}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--efficiency-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    audit = json.loads(args.efficiency_audit.read_text(encoding="utf-8"))
    protocol = create_protocol(coverage, audit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "protocol_manifest.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "protocol.md").write_text(
        render(protocol), encoding="utf-8"
    )
    print(render(protocol), end="")


if __name__ == "__main__":
    main()

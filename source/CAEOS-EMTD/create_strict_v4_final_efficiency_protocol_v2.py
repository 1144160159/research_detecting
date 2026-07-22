from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sentinel(coverage_sha: str, suite: str, scenarios: list[str]) -> str:
    if not scenarios:
        raise ValueError(f"suite {suite} has no scenarios")
    digest = hashlib.sha256(f"{coverage_sha}:{suite}".encode("utf-8")).hexdigest()
    return scenarios[int(digest[:16], 16) % len(scenarios)]


def _require_sha(value: object, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} SHA is missing")
    return value


def create_protocol(
    coverage: dict[str, Any],
    v1_protocol: dict[str, Any],
    readiness: dict[str, Any],
    decision: dict[str, Any],
    external_confirmation: dict[str, Any],
    *,
    coverage_file_sha256: str,
    v1_protocol_file_sha256: str,
    readiness_file_sha256: str,
    decision_file_sha256: str,
    external_confirmation_file_sha256: str,
    candidate_implementation_sha256: str,
    comparator_implementation_sha256: str,
    candidate_runtime_sha256: str,
    candidate_capture_sha256: str,
    candidate_benchmark_sha256: str,
    comparator_runtime_sha256: str,
    comparator_capture_sha256: str,
    comparator_training_capture_sha256: str,
    comparator_benchmark_sha256: str,
    paired_runner_sha256: str,
    execution_plan_creator_sha256: str,
    execution_plan_executor_sha256: str,
    efficiency_summarizer_sha256: str,
    protocol_creator_sha256: str,
    efficiency_metrics_observed_at_freeze: int,
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    if coverage.get("datasets") != 7 or coverage.get("scenario_inference_units") != 102:
        raise ValueError("efficiency v2 requires the frozen 7-dataset registry")
    if v1_protocol.get("schema_version") != "strict_v4_final_efficiency_protocol_v1":
        raise ValueError("unexpected efficiency v1 protocol schema")
    if v1_protocol.get("manifest_sha256") != canonical_hash(v1_protocol):
        raise ValueError("efficiency v1 protocol SHA mismatch")
    if readiness.get("schema_version") != "strict_v4_final_efficiency_execution_readiness_v1":
        raise ValueError("unexpected efficiency readiness schema")
    if readiness.get("protocol_manifest_sha256") != v1_protocol["manifest_sha256"]:
        raise ValueError("efficiency readiness does not bind v1")
    if readiness.get("v1_protocol_executable") is not False:
        raise ValueError("v2 amendment is only valid for the recorded v1 artifact blocker")
    if readiness.get("direct_efficiency_claim_allowed") is not False:
        raise ValueError("pre-v2 readiness must not allow an efficiency claim")
    if decision.get("schema_version") != "strict_v4_optimal_self_algorithm_decision_v1":
        raise ValueError("unexpected optimal self-algorithm decision schema")
    if decision.get("manifest_sha256") != canonical_hash(decision):
        raise ValueError("optimal self-algorithm decision SHA mismatch")
    if decision.get("status") != "frozen_optimal_self_algorithm":
        raise ValueError("optimal self-algorithm decision is not frozen")
    selected = decision.get("selected_algorithm")
    if selected != "caeos_pairwise":
        raise ValueError("efficiency v2 currently supports the frozen pairwise branch")
    if external_confirmation.get("schema_version") != "strict_v4_external_comparator_confirmation_v1":
        raise ValueError("unexpected external confirmation schema")
    if external_confirmation.get("selected_algorithm") != selected:
        raise ValueError("external confirmation selected-algorithm mismatch")
    comparator = external_confirmation.get("selected_comparator")
    if comparator != "opendetect":
        raise ValueError("efficiency v2 requires the frozen OpenDetect comparator")
    validation = external_confirmation.get("comparator_validation", {})
    if validation.get("passes") is not True or validation.get("paired_runs") != 306:
        raise ValueError("external comparator confirmation is incomplete")
    if int(efficiency_metrics_observed_at_freeze) != 0:
        raise ValueError("efficiency v2 must be frozen before any efficiency metrics")

    coverage_sha = _require_sha(coverage.get("manifest_sha256"), "coverage manifest")
    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict) or len(registry) != 7:
        raise ValueError("scenario registry is incomplete")
    sentinels = {}
    for suite in sorted(registry):
        item = registry[suite]
        scenarios = item.get("scenarios") if isinstance(item, dict) else None
        if not isinstance(scenarios, list) or len(scenarios) != item.get("count"):
            raise ValueError(f"invalid scenario registry for {suite}")
        sentinels[suite] = _sentinel(coverage_sha, suite, scenarios)

    input_hashes = {
        "coverage_manifest": _require_sha(coverage_file_sha256, "coverage file"),
        "v1_protocol": _require_sha(v1_protocol_file_sha256, "v1 protocol file"),
        "v1_readiness": _require_sha(readiness_file_sha256, "v1 readiness file"),
        "optimal_self_algorithm_decision": _require_sha(decision_file_sha256, "decision file"),
        "external_confirmation": _require_sha(
            external_confirmation_file_sha256, "external confirmation file"
        ),
    }
    implementation_hashes = {
        "candidate_train_hybrid_open_set": _require_sha(
            candidate_implementation_sha256, "candidate implementation"
        ),
        "comparator_train_neural_open_set": _require_sha(
            comparator_implementation_sha256, "comparator implementation"
        ),
        "candidate_pairwise_runtime": _require_sha(
            candidate_runtime_sha256, "candidate runtime"
        ),
        "candidate_runtime_capture": _require_sha(
            candidate_capture_sha256, "candidate capture"
        ),
        "candidate_runtime_benchmark": _require_sha(
            candidate_benchmark_sha256, "candidate benchmark"
        ),
        "comparator_open_detect_runtime": _require_sha(
            comparator_runtime_sha256, "comparator runtime"
        ),
        "comparator_runtime_capture": _require_sha(
            comparator_capture_sha256, "comparator capture"
        ),
        "comparator_training_runtime_capture": _require_sha(
            comparator_training_capture_sha256, "comparator training capture"
        ),
        "comparator_runtime_benchmark": _require_sha(
            comparator_benchmark_sha256, "comparator benchmark"
        ),
        "efficiency_paired_runner": _require_sha(
            paired_runner_sha256, "paired runner"
        ),
        "efficiency_execution_plan_creator": _require_sha(
            execution_plan_creator_sha256, "execution plan creator"
        ),
        "efficiency_execution_plan_executor": _require_sha(
            execution_plan_executor_sha256, "execution plan executor"
        ),
        "efficiency_summarizer": _require_sha(
            efficiency_summarizer_sha256, "efficiency summarizer"
        ),
        "efficiency_protocol_creator": _require_sha(
            protocol_creator_sha256, "protocol creator"
        ),
    }
    protocol = {
        "schema_version": "strict_v4_final_efficiency_protocol_v2",
        "status": "frozen_post_selection_before_efficiency_results",
        "purpose": (
            "same-hardware deterministic replay amendment for the selected pairwise "
            "candidate and frozen OpenDetect comparator"
        ),
        "efficiency_metrics_observed_at_freeze": 0,
        "coverage_manifest_sha256": coverage_sha,
        "v1_protocol_manifest_sha256": v1_protocol["manifest_sha256"],
        "optimal_self_algorithm_manifest_sha256": decision["manifest_sha256"],
        "external_confirmation_protocol_manifest_sha256": external_confirmation.get(
            "external_protocol_manifest_sha256"
        ),
        "input_file_sha256": input_hashes,
        "implementation_sha256": implementation_hashes,
        "methods": {"candidate": selected, "comparator": comparator},
        "execution_gate": {
            "external_confirmation_complete": True,
            "selected_algorithm_is_frozen": True,
            "must_not_overlap_accuracy_confirmation_or_other_gpu_jobs": True,
            "exclusive_single_process_measurement": True,
            "outer_scenario_workers": 1,
        },
        "hardware_control": {
            "same_gpu_cpu_affinity_and_software_stack": True,
            "record_gpu_name_driver_cuda_torch_cpu_ram": True,
            "fixed_power_and_clock_state_or_record_uncontrolled_state": True,
            "synchronize_cuda_around_timed_regions": True,
            "alternate_method_order_by_repetition": True,
        },
        "training_calibration_benchmark": {
            "scenario_selection": "one coverage-SHA-indexed scenario per dataset",
            "sentinel_scenarios": sentinels,
            "seed": 191,
            "clean_process_repetitions": 3,
            "deployment_mode": "native_primary_only",
            "candidate_device": "cpu",
            "comparator_device": "cuda",
            "reported_metrics": [
                "feature_preparation_seconds",
                "training_seconds",
                "calibration_seconds",
                "total_fit_seconds",
                "peak_gpu_memory_mb",
                "peak_host_rss_mb",
                "trainable_parameters_or_not_applicable_for_nonparametric_model",
                "serialized_deployment_artifact_bytes",
            ],
        },
        "inference_benchmark": {
            "scenario_scope": "all_102_frozen_scenarios",
            "seed": 7,
            "fit_once_then_time_actual_test_forward_and_risk_transform": True,
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "batch_sizes": [1, 64, 512],
            "reported_metrics": [
                "latency_p50_ms",
                "latency_p95_ms",
                "latency_p99_ms",
                "samples_per_second",
                "peak_gpu_memory_mb",
                "peak_host_rss_mb",
            ],
            "aggregation": (
                "scenario-blocked median and bootstrap_95ci; repetitions and batches "
                "are not pooled as independent scenarios"
            ),
        },
        "deployment_device_modes": {
            "native_primary": {
                "candidate_device": "cpu",
                "comparator_device": "cuda",
                "interpretation": "measured native deployment paths on the same host",
            },
            "cpu_normalized_secondary": {
                "candidate_device": "cpu",
                "comparator_device": "cpu",
                "interpretation": "device-normalized diagnostic reported separately",
            },
            "required_modes": ["native_primary", "cpu_normalized_secondary"],
            "must_not_pool_or_conflate_modes": True,
        },
        "instrumentation_equivalence_gate": {
            "source_prediction_array_identity_required": True,
            "source_component_max_absolute_tolerance": 1e-12,
            "stable_runtime_same_device_shadow_required_per_capture": True,
            "stable_runtime_risk_max_absolute_tolerance": 1e-12,
            "source_empirical_tail_risk_difference_is_diagnostic_only": True,
            "tie_handling": (
                "collapse adjacent frozen validation references within 1e-12 into "
                "one first-rank cluster; audit source components before the "
                "discontinuous empirical-rank map"
            ),
            "runtime_stability_revision": "reference_near_tie_cluster_v1",
            "separate_stochastic_retraining_shadow_required": False,
            "separate_retraining_shadow_exclusion_reason": (
                "a second stochastic fit would confound instrumentation equivalence "
                "with optimizer and sampling variance"
            ),
            "same_device_shadow_required": True,
            "cross_device_equivalence_is_diagnostic_only": True,
            "split_fingerprint_must_match": True,
            "prediction_arrays_must_match": True,
            "metric_absolute_tolerance": 1e-12,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "claim_policy": {
            "accuracy_selection_must_not_use_efficiency_results": True,
            "report_tradeoffs_even_if_candidate_is_slower": True,
            "no_claim_until_all_scenarios_fields_and_equivalence_checks_pass": True,
            "scores_npz_postprocessing_is_not_model_inference": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def render(protocol: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 final efficiency protocol v2",
        "",
        f"Protocol SHA: `{protocol['manifest_sha256']}`.",
        "",
        "This amendment remains result-free and is executable only after external confirmation.",
        "",
        "## Frozen methods",
        "",
        f"- Candidate: `{protocol['methods']['candidate']}`",
        f"- Comparator: `{protocol['methods']['comparator']}`",
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
    parser.add_argument("--v1-protocol", type=Path, required=True)
    parser.add_argument("--readiness", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--external-confirmation", type=Path, required=True)
    parser.add_argument("--candidate-implementation", type=Path, required=True)
    parser.add_argument("--comparator-implementation", type=Path, required=True)
    parser.add_argument("--candidate-runtime", type=Path, required=True)
    parser.add_argument("--candidate-capture", type=Path, required=True)
    parser.add_argument("--candidate-benchmark", type=Path, required=True)
    parser.add_argument("--comparator-runtime", type=Path, required=True)
    parser.add_argument("--comparator-capture", type=Path, required=True)
    parser.add_argument("--comparator-training-capture", type=Path, required=True)
    parser.add_argument("--comparator-benchmark", type=Path, required=True)
    parser.add_argument("--paired-runner", type=Path, required=True)
    parser.add_argument("--execution-plan-creator", type=Path, required=True)
    parser.add_argument("--execution-plan-executor", type=Path, required=True)
    parser.add_argument("--efficiency-summarizer", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    inputs = [
        args.coverage,
        args.v1_protocol,
        args.readiness,
        args.decision,
        args.external_confirmation,
    ]
    observed = len(list(args.output_dir.glob("**/efficiency_metrics.json")))
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    protocol = create_protocol(
        *payloads,
        coverage_file_sha256=file_hash(inputs[0]),
        v1_protocol_file_sha256=file_hash(inputs[1]),
        readiness_file_sha256=file_hash(inputs[2]),
        decision_file_sha256=file_hash(inputs[3]),
        external_confirmation_file_sha256=file_hash(inputs[4]),
        candidate_implementation_sha256=file_hash(args.candidate_implementation),
        comparator_implementation_sha256=file_hash(args.comparator_implementation),
        candidate_runtime_sha256=file_hash(args.candidate_runtime),
        candidate_capture_sha256=file_hash(args.candidate_capture),
        candidate_benchmark_sha256=file_hash(args.candidate_benchmark),
        comparator_runtime_sha256=file_hash(args.comparator_runtime),
        comparator_capture_sha256=file_hash(args.comparator_capture),
        comparator_training_capture_sha256=file_hash(
            args.comparator_training_capture
        ),
        comparator_benchmark_sha256=file_hash(args.comparator_benchmark),
        paired_runner_sha256=file_hash(args.paired_runner),
        execution_plan_creator_sha256=file_hash(args.execution_plan_creator),
        execution_plan_executor_sha256=file_hash(args.execution_plan_executor),
        efficiency_summarizer_sha256=file_hash(args.efficiency_summarizer),
        protocol_creator_sha256=file_hash(Path(__file__)),
        efficiency_metrics_observed_at_freeze=observed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "protocol_manifest.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "protocol.md").write_text(render(protocol), encoding="utf-8")
    print(render(protocol), end="")


if __name__ == "__main__":
    main()

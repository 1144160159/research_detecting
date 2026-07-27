from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_vgrf_selected_system_seed317 import load


VGRF = "caeos_validation_gated_class_conditional_reliability_fusion"
EFFICIENCY_METRICS = (
    "feature_preparation_seconds",
    "training_seconds",
    "calibration_seconds",
    "total_fit_seconds",
    "peak_gpu_memory_mb",
    "peak_host_rss_mb",
    "serialized_deployment_artifact_bytes",
)
CORRUPTION_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "ece",
)
LATENCY_METRICS = (
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
)


def bootstrap_mean(
    values: Iterable[float],
    *,
    seed: int,
    repetitions: int = 20000,
) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.ndim != 1 or not len(array) or not np.isfinite(array).all():
        raise ValueError("bootstrap requires finite nonempty values")
    rng = np.random.default_rng(seed)
    samples = array[
        rng.integers(0, len(array), size=(repetitions, len(array)))
    ].mean(axis=1)
    return {
        "n": int(len(array)),
        "mean": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(samples, 0.025)),
            float(np.quantile(samples, 0.975)),
        ],
        "values": array.tolist(),
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=lambda name: (p_values[name], name))
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for index, name in enumerate(ordered):
        running = max(
            running, (total - index) * float(p_values[name])
        )
        adjusted[name] = min(1.0, running)
    return adjusted


def validate_state(
    path: Path,
    *,
    schema: str,
    protocol_sha256: str,
    completed_key: str,
    expected: int,
) -> dict[str, Any]:
    state = load(path)
    if (
        state.get("schema_version") != schema
        or state.get("state") != "complete"
        or state.get("protocol_manifest_sha256") != protocol_sha256
        or int(state.get(completed_key, -1)) != expected
    ):
        raise ValueError(f"incomplete or invalid execution state: {path}")
    return state


def verified_outputs(
    records: list[dict[str, Any]], expected: int
) -> list[dict[str, Any]]:
    if len(records) != expected:
        raise ValueError("execution state record count mismatch")
    output = []
    seen = set()
    for record in records:
        path = Path(record["output"])
        if not path.is_file() or file_hash(path) != record["output_sha256"]:
            raise ValueError(f"execution output SHA mismatch: {path}")
        value = load(path)
        if value.get("manifest_sha256") != canonical_hash(value):
            raise ValueError(f"execution output canonical SHA mismatch: {path}")
        identity = (
            value["suite"],
            value["scenario"],
            int(value["seed"]),
            value.get("repetition"),
        )
        if identity in seen:
            raise ValueError(f"duplicate execution output: {identity}")
        seen.add(identity)
        output.append(value)
    return output


def training_summary(
    state: dict[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    blocks = verified_outputs(state["blocks"], 42)
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(
        list
    )
    hardware_values = []
    for block in blocks:
        if (
            block.get("schema_version")
            != "strict_v4_vgrf_selected_system_training_efficiency_block_v1"
            or block.get("clean_process_directory_is_unique") is not True
            or block.get(
                "unknown_or_test_labels_used_for_efficiency_selection"
            )
            is not False
        ):
            raise ValueError("invalid training efficiency block")
        grouped[
            (block["suite"], block["scenario"], int(block["seed"]))
        ].append(block)
        hardware_values.append(block["hardware"])
    if len(grouped) != 14 or any(len(values) != 3 for values in grouped.values()):
        raise ValueError("training efficiency repetition coverage mismatch")
    ratios: dict[str, list[float]] = {
        metric: [] for metric in EFFICIENCY_METRICS
    }
    by_pair: dict[str, Any] = {}
    for identity, values in sorted(grouped.items()):
        key = f"{identity[0]}/{identity[1]}/seed{identity[2]}"
        by_pair[key] = {}
        for metric in EFFICIENCY_METRICS:
            candidate = float(
                np.median(
                    [value["methods"]["vgrf"][metric] for value in values]
                )
            )
            comparator = float(
                np.median(
                    [
                        value["methods"]["opendetect"][metric]
                        for value in values
                    ]
                )
            )
            if not np.isfinite(candidate) or not np.isfinite(comparator):
                raise ValueError("non-finite training efficiency metric")
            if comparator <= 0.0:
                if candidate == 0.0:
                    ratio = 1.0
                else:
                    raise ValueError("undefined training efficiency ratio")
            else:
                ratio = candidate / comparator
            ratios[metric].append(ratio)
            by_pair[key][metric] = {
                "vgrf_median": candidate,
                "opendetect_median": comparator,
                "vgrf_over_opendetect": ratio,
            }
    summaries = {
        metric: bootstrap_mean(
            values,
            seed=12000 + index,
        )
        for index, (metric, values) in enumerate(ratios.items())
    }
    checks = {
        metric: summary["bootstrap_95ci"][1] <= 1.0
        for metric, summary in summaries.items()
    }
    hardware_equal = all(
        value == hardware_values[0] for value in hardware_values
    )
    return (
        {
            "pair_count": 14,
            "clean_process_blocks": 42,
            "by_pair": by_pair,
            "ratio_inference": summaries,
            "upper_bound_le_1_checks": checks,
            "all_cost_upper_bounds_le_1": all(checks.values()),
        },
        hardware_equal,
        hardware_values[0],
    )


def runtime_summary(
    state: dict[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    blocks = verified_outputs(state["blocks"], 204)
    ratios: dict[int, dict[str, list[float]]] = {
        batch: {
            **{metric: [] for metric in LATENCY_METRICS},
            "samples_per_second": [],
        }
        for batch in (1, 64, 512)
    }
    artifact_ratios = []
    hardware_values = []
    for block in blocks:
        if (
            block.get("schema_version")
            != "strict_v4_vgrf_selected_system_runtime_block_v1"
            or block.get("same_processed_inputs_array_equal") is not True
            or block.get("scores_npz_only_postprocessing_used") is not False
            or block.get("unknown_or_test_labels_used") is not False
            or block.get("exclusive_machine_gate_passed_before_matrix")
            is not True
        ):
            raise ValueError("invalid runtime benchmark block")
        records = block["benchmark"]["records"]
        if len(records) != 3:
            raise ValueError("runtime benchmark batch coverage mismatch")
        for record in records:
            batch = int(record["batch_size"])
            if batch not in ratios:
                raise ValueError("unexpected runtime batch size")
            methods = record["methods"]
            for metric in LATENCY_METRICS:
                ratios[batch][metric].append(
                    float(methods["vgrf"][metric])
                    / float(methods["opendetect"][metric])
                )
            ratios[batch]["samples_per_second"].append(
                float(methods["vgrf"]["samples_per_second"])
                / float(methods["opendetect"]["samples_per_second"])
            )
        artifact_ratios.append(
            float(block["artifact_bytes"]["vgrf"])
            / float(block["artifact_bytes"]["opendetect"])
        )
        hardware_values.append(block["hardware"])
    summaries: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for batch, metrics in ratios.items():
        summaries[str(batch)] = {}
        for index, (metric, values) in enumerate(metrics.items()):
            summary = bootstrap_mean(
                values, seed=13000 + batch + index
            )
            summaries[str(batch)][metric] = summary
            checks[f"batch{batch}_{metric}"] = (
                summary["bootstrap_95ci"][0] >= 1.0
                if metric == "samples_per_second"
                else summary["bootstrap_95ci"][1] <= 1.0
            )
    artifact = bootstrap_mean(artifact_ratios, seed=14000)
    checks["serialized_deployment_artifact_bytes"] = (
        artifact["bootstrap_95ci"][1] <= 1.0
    )
    hardware_equal = all(
        value == hardware_values[0] for value in hardware_values
    )
    return (
        {
            "block_count": 204,
            "by_batch_size": summaries,
            "artifact_ratio": artifact,
            "superiority_checks": checks,
            "all_runtime_and_artifact_checks_pass": all(checks.values()),
        },
        hardware_equal,
        hardware_values[0],
    )


def capture_summary(state: dict[str, Any]) -> dict[str, Any]:
    results = state["results"]
    if len(results) != 306:
        raise ValueError("deployment capture state is incomplete")
    identities = {
        (item["suite"], item["scenario"], int(item["seed"]))
        for item in results
    }
    checks = (
        "pairwise_source_equivalence",
        "vgrf_source_equivalence",
        "pairwise_audit_passes",
        "vgrf_audit_passes",
        "opendetect_audit_passes",
    )
    if len(identities) != 306 or any(
        item.get(name) is not True
        for item in results
        for name in checks
    ):
        raise ValueError("deployment capture audit gate failed")
    return {
        "source_pair_count": 306,
        "all_pairwise_vgrf_opendetect_audits_pass": True,
        "all_frozen_source_equivalence_checks_pass": True,
    }


def corruption_summary(
    state: dict[str, Any],
    *,
    protocol: dict[str, Any],
) -> tuple[dict[str, Any], bool, bool]:
    from scipy.stats import wilcoxon

    blocks = verified_outputs(state["blocks"], 306)
    families = protocol["comparative_corruption"]["families"]
    values: dict[
        str, dict[str, dict[str, dict[int, float]]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    degradations: dict[
        str, dict[str, dict[str, dict[int, float]]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    condition_count = 0
    for block in blocks:
        if (
            block.get("schema_version")
            != "strict_v4_vgrf_selected_system_corruption_block_v1"
            or block.get("vgrf_opendetect_input_arrays_equal") is not True
            or block.get(
                "degradation_uses_same_deployment_runtime_clean_anchors"
            )
            is not True
            or block.get("test_labels_used_for_final_metrics_only")
            is not True
            or block.get(
                "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation"
            )
            is not False
        ):
            raise ValueError("invalid comparative corruption block")
        scenario_key = f"{block['suite']}/{block['scenario']}"
        seed = int(block["seed"])
        conditions = block["conditions"]
        if len(conditions) != 5 or {
            item["family"] for item in conditions
        } != set(families):
            raise ValueError("corruption family coverage mismatch")
        for condition in conditions:
            family = condition["family"]
            for metric in CORRUPTION_METRICS:
                values[family][metric][scenario_key][seed] = float(
                    condition["vgrf_robustness_advantage"][metric]
                )
                degradations[family][metric][scenario_key][seed] = float(
                    condition["vgrf_degradation"][metric]
                )
            condition_count += 1
    if condition_count != 1530:
        raise ValueError("comparative corruption condition count mismatch")
    thresholds = protocol["candidate_graceful_degradation_thresholds"]
    by_family: dict[str, Any] = {}
    graceful_checks: dict[str, bool] = {}
    comparative_family_checks = []
    for family_index, family in enumerate(families):
        metric_summaries = {}
        scenario_advantages: dict[str, dict[str, float]] = {}
        degradation_summaries = {}
        for metric_index, metric in enumerate(CORRUPTION_METRICS):
            scenario_values = {}
            scenario_degradation = {}
            for scenario_key, seed_values in values[family][metric].items():
                if sorted(seed_values) != [311, 313, 317]:
                    raise ValueError("corruption seed coverage mismatch")
                scenario_values[scenario_key] = float(
                    np.mean(list(seed_values.values()))
                )
                scenario_degradation[scenario_key] = float(
                    np.mean(
                        list(
                            degradations[family][metric][
                                scenario_key
                            ].values()
                        )
                    )
                )
            if len(scenario_values) != 102:
                raise ValueError("corruption scenario coverage mismatch")
            scenario_advantages[metric] = scenario_values
            summary = bootstrap_mean(
                [scenario_values[key] for key in sorted(scenario_values)],
                seed=15000 + family_index * 100 + metric_index,
            )
            array = np.asarray(
                [scenario_values[key] for key in sorted(scenario_values)]
            )
            p_value = (
                1.0
                if np.all(np.abs(array) <= 1e-15)
                else float(
                    wilcoxon(
                        array,
                        alternative="greater",
                        zero_method="wilcox",
                    ).pvalue
                )
            )
            summary["wilcoxon_one_sided_p"] = p_value
            metric_summaries[metric] = summary
            degradation_summaries[metric] = bootstrap_mean(
                [
                    scenario_degradation[key]
                    for key in sorted(scenario_degradation)
                ],
                seed=16000 + family_index * 100 + metric_index,
            )
        adjusted = holm_adjust(
            {
                metric: metric_summaries[metric][
                    "wilcoxon_one_sided_p"
                ]
                for metric in CORRUPTION_METRICS
            }
        )
        for metric in CORRUPTION_METRICS:
            metric_summaries[metric]["holm_adjusted_p"] = adjusted[
                metric
            ]
        suites = sorted(
            {
                key.split("/", 1)[0]
                for key in scenario_advantages[CORRUPTION_METRICS[0]]
            }
        )
        suite_means = {
            suite: {
                metric: float(
                    np.mean(
                        [
                            value
                            for key, value in scenario_advantages[
                                metric
                            ].items()
                            if key.startswith(f"{suite}/")
                        ]
                    )
                )
                for metric in CORRUPTION_METRICS
            }
            for suite in suites
        }
        comparative_checks = {
            "all_six_means_strictly_positive": all(
                metric_summaries[metric]["mean"] > 0.0
                for metric in CORRUPTION_METRICS
            ),
            "all_six_bootstrap_lower_bounds_strictly_positive": all(
                metric_summaries[metric]["bootstrap_95ci"][0] > 0.0
                for metric in CORRUPTION_METRICS
            ),
            "all_six_holm_adjusted_p_below_0_05": all(
                metric_summaries[metric]["holm_adjusted_p"] < 0.05
                for metric in CORRUPTION_METRICS
            ),
            "all_suite_metric_means_nonnegative": all(
                value >= -1e-12
                for metrics in suite_means.values()
                for value in metrics.values()
            ),
        }
        family_comparative = all(comparative_checks.values())
        comparative_family_checks.append(family_comparative)
        family_graceful = {
            metric: degradation_summaries[metric]["mean"]
            <= float(limit)
            for metric, limit in thresholds.items()
        }
        graceful_checks[family] = all(family_graceful.values())
        by_family[family] = {
            "relative_advantage": metric_summaries,
            "vgrf_degradation": degradation_summaries,
            "suite_mean_advantage": suite_means,
            "comparative_checks": comparative_checks,
            "comparative_passes": family_comparative,
            "graceful_threshold_checks": family_graceful,
            "graceful_passes": graceful_checks[family],
        }
    graceful = all(graceful_checks.values())
    comparative = all(comparative_family_checks)
    return (
        {
            "source_pair_count": 306,
            "paired_condition_evaluations": 1530,
            "by_family": by_family,
            "candidate_graceful_degradation_passes": graceful,
            "comparative_robustness_passes": comparative,
        },
        graceful,
        comparative,
    )


def create_summary(
    *,
    protocol: dict[str, Any],
    capture_state: dict[str, Any],
    training_state: dict[str, Any],
    benchmark_state: dict[str, Any],
    corruption_state: dict[str, Any],
) -> dict[str, Any]:
    capture = capture_summary(capture_state)
    training, training_hardware_equal, training_hardware = (
        training_summary(training_state)
    )
    runtime, runtime_hardware_equal, runtime_hardware = runtime_summary(
        benchmark_state
    )
    corruption, graceful, comparative = corruption_summary(
        corruption_state, protocol=protocol
    )
    same_hardware = (
        training_hardware_equal
        and runtime_hardware_equal
        and training_hardware == runtime_hardware
    )
    efficiency = (
        training["all_cost_upper_bounds_le_1"]
        and runtime["all_runtime_and_artifact_checks_pass"]
    )
    gates = {
        "formal_same_hardware_efficiency_characterized": same_hardware,
        "selected_runtime_equivalence_all_204_blocks": (
            runtime["block_count"] == 204
        ),
        "selected_runtime_internal_deployment_gate": (
            capture[
                "all_pairwise_vgrf_opendetect_audits_pass"
            ]
            and capture["all_frozen_source_equivalence_checks_pass"]
        ),
        "efficiency_superiority_all_required_native_metrics": efficiency,
        "candidate_graceful_degradation_gate": graceful,
        "comparative_corruption_robustness_against_opendetect": comparative,
    }
    expected = set(protocol["required_output"]["required_system_gates"])
    if set(gates) != expected:
        raise ValueError("system gate universe differs from design")
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_confirmation_summary_v1"
        ),
        "status": "complete",
        "selected_algorithm": VGRF,
        "design_manifest_sha256": protocol["design_manifest_sha256"],
        "preparation_protocol_manifest_sha256": protocol[
            "preparation_protocol_manifest_sha256"
        ],
        "final_selection_manifest_sha256": protocol[
            "final_selection_manifest_sha256"
        ],
        "vgrf_confirmation_summary_manifest_sha256": protocol[
            "vgrf_confirmation_summary_manifest_sha256"
        ],
        "execution_protocol_manifest_sha256": protocol["manifest_sha256"],
        "equivalence_block_count": 204,
        "comparative_corruption_pair_count": 1530,
        "validation": {
            "passes": True,
            "deployment_source_pairs": 306,
            "training_efficiency_blocks": 42,
            "runtime_blocks": 204,
            "paired_corruption_conditions": 1530,
        },
        "deployment": capture,
        "training_efficiency": training,
        "runtime_efficiency": runtime,
        "corruption": corruption,
        "hardware": runtime_hardware,
        "gates": gates,
        "all_system_gates_pass": all(gates.values()),
        "metric_wise_or_suite_wise_splicing_used": False,
        "leakage_validation": {
            "unknown_or_test_labels_used_for_fitting_selection_threshold_or_corruption_generation": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "claim_boundary": {
            "negative_effect_gates_are_preserved": True,
            "pairwise_system_results_are_not_inherited": True,
            "comprehensive_sota_requires_all_system_gates": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# VGRF selected-system confirmation",
        "",
        f"All system gates: **{'PASS' if value['all_system_gates_pass'] else 'FAIL'}**.",
        "",
        "| Gate | Result |",
        "|---|---|",
    ]
    for name, passed in value["gates"].items():
        lines.append(f"| {name} | {'PASS' if passed else 'FAIL'} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--capture-state", type=Path, required=True)
    parser.add_argument("--training-state", type=Path, required=True)
    parser.add_argument("--benchmark-state", type=Path, required=True)
    parser.add_argument("--corruption-state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid selected-system execution protocol")
    active = Path(__file__).resolve()
    if protocol.get("implementation_sha256", {}).get(
        active.name
    ) != file_hash(active):
        raise ValueError("active system summarizer SHA mismatch")
    capture_state = validate_state(
        args.capture_state,
        schema="strict_v4_vgrf_selected_system_capture_state_v1",
        protocol_sha256=protocol["manifest_sha256"],
        completed_key="reported_source_pairs",
        expected=306,
    )
    training_state = validate_state(
        args.training_state,
        schema=(
            "strict_v4_vgrf_selected_system_training_efficiency_state_v1"
        ),
        protocol_sha256=protocol["manifest_sha256"],
        completed_key="completed_blocks",
        expected=42,
    )
    benchmark_state = validate_state(
        args.benchmark_state,
        schema="strict_v4_vgrf_selected_system_benchmark_state_v1",
        protocol_sha256=protocol["manifest_sha256"],
        completed_key="completed_blocks",
        expected=204,
    )
    corruption_state = validate_state(
        args.corruption_state,
        schema="strict_v4_vgrf_selected_system_corruption_state_v1",
        protocol_sha256=protocol["manifest_sha256"],
        completed_key="completed_conditions",
        expected=1530,
    )
    value = create_summary(
        protocol=protocol,
        capture_state=capture_state,
        training_state=training_state,
        benchmark_state=benchmark_state,
        corruption_state=corruption_state,
    )
    value["input_file_sha256"] = {
        "protocol": file_hash(args.protocol),
        "capture_state": file_hash(args.capture_state),
        "training_state": file_hash(args.training_state),
        "benchmark_state": file_hash(args.benchmark_state),
        "corruption_state": file_hash(args.corruption_state),
    }
    value["analysis_implementation_sha256"] = file_hash(active)
    value["manifest_sha256"] = canonical_hash(value)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(
        render(value), encoding="utf-8"
    )
    (args.output_dir / "summary_complete").touch()
    print(render(value), end="")


if __name__ == "__main__":
    main()

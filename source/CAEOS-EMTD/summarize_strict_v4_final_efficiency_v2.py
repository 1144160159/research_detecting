from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


TRAINING_METRICS = (
    "feature_preparation_seconds",
    "training_seconds",
    "calibration_seconds",
    "total_fit_seconds",
    "peak_gpu_memory_mb",
    "peak_host_rss_mb",
    "deployment_artifact_bytes",
)
INFERENCE_METRICS = (
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "samples_per_second",
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def finite(value: object, name: str) -> float:
    result = float(value)
    if not np.isfinite(result) or result < 0.0:
        raise ValueError(f"invalid nonnegative metric {name}: {value}")
    return result


def median_ci(values: Iterable[float], seed: int) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("bootstrap input must be a finite nonempty vector")
    rng = np.random.default_rng(seed)
    samples = np.median(
        array[rng.integers(0, array.size, size=(5000, array.size))], axis=1
    )
    return {
        "n_blocks": int(array.size),
        "median": float(np.median(array)),
        "bootstrap_95ci": [
            float(np.quantile(samples, 0.025)),
            float(np.quantile(samples, 0.975)),
        ],
        "values": array.tolist(),
    }


def require_equivalence(path: Path, expected_mode: str) -> None:
    payload = load_json(path)
    if (
        payload.get("passes") is not True
        or payload.get("prediction_array_equal") is not True
        or float(payload.get("risk_max_absolute_difference", float("inf"))) > 1e-12
        or float(payload.get("absolute_tolerance", float("inf"))) > 1e-12
        or payload.get("equivalence_mode") != expected_mode
        or payload.get("unknown_or_test_labels_used_for_runtime_fitting_or_selection")
        is not False
    ):
        raise ValueError(f"equivalence gate failed: {path}")


def training_summary(plan: dict[str, Any], root: Path) -> dict[str, Any]:
    by_method: dict[str, dict[str, list[float]]] = {
        role: {metric: [] for metric in TRAINING_METRICS}
        for role in ("candidate", "comparator")
    }
    parameters: dict[str, list[int | None]] = {"candidate": [], "comparator": []}
    suites: dict[str, dict[str, dict[str, list[float]]]] = {}
    for block in plan["training_blocks"]:
        suite = str(block["suite"])
        scenario = str(block["scenario"])
        repetition = int(block["repetition"])
        block_root = root / "training" / suite / scenario / f"rep{repetition}"
        suites.setdefault(
            suite,
            {
                role: {metric: [] for metric in TRAINING_METRICS}
                for role in ("candidate", "comparator")
            },
        )
        for role, dirname, schema, mode in (
            (
                "candidate",
                "candidate_capture",
                "strict_v4_pairwise_runtime_capture_v1",
                "source_components_plus_stable_runtime_shadow",
            ),
            (
                "comparator",
                "comparator_capture",
                "strict_v4_opendetect_training_runtime_capture_v2",
                "runtime_vs_uninstrumented_same_device_shadow",
            ),
        ):
            capture = block_root / dirname
            manifest = load_json(capture / "capture_manifest.json")
            if manifest.get("schema_version") != schema:
                raise ValueError(f"training capture schema mismatch: {capture}")
            require_equivalence(capture / "equivalence.json", mode)
            phase = manifest.get("phase_timings", {})
            values = {
                "feature_preparation_seconds": phase.get("feature_preparation_seconds"),
                "training_seconds": phase.get("training_seconds"),
                "calibration_seconds": phase.get("calibration_seconds"),
                "total_fit_seconds": phase.get("total_fit_seconds"),
                "peak_gpu_memory_mb": manifest.get("peak_gpu_memory_mb"),
                "peak_host_rss_mb": manifest.get("peak_host_rss_mb"),
                "deployment_artifact_bytes": manifest.get("deployment_artifact_bytes"),
            }
            for metric, raw in values.items():
                value = finite(raw, f"{role}.{metric}")
                by_method[role][metric].append(value)
                suites[suite][role][metric].append(value)
            parameter = manifest.get("trainable_parameters")
            if role == "candidate":
                if parameter is not None or manifest.get("trainable_parameters_status") != (
                    "not_applicable_nonparametric_ensemble"
                ):
                    raise ValueError("candidate parameter applicability marker is invalid")
                parameters[role].append(None)
            else:
                if not isinstance(parameter, int) or parameter <= 0:
                    raise ValueError("OpenDetect trainable parameter count is invalid")
                parameters[role].append(parameter)
    if len(plan["training_blocks"]) != 21 or len(suites) != 7:
        raise ValueError("training coverage is incomplete")
    aggregate: dict[str, Any] = {}
    for role in ("candidate", "comparator"):
        aggregate[role] = {}
        for index, metric in enumerate(TRAINING_METRICS):
            suite_medians = [
                float(np.median(suites[suite][role][metric])) for suite in sorted(suites)
            ]
            aggregate[role][metric] = median_ci(suite_medians, 7100 + index)
        aggregate[role]["raw_capture_count"] = len(by_method[role]["training_seconds"])
        aggregate[role]["trainable_parameters"] = (
            {
                "status": "not_applicable_nonparametric_ensemble",
                "value": None,
            }
            if role == "candidate"
            else {
                "status": "reported",
                "values": sorted(set(int(v) for v in parameters[role] if v is not None)),
            }
        )
    paired = {}
    for metric in TRAINING_METRICS:
        ratios = []
        for suite in sorted(suites):
            candidate = float(np.median(suites[suite]["candidate"][metric]))
            comparator = float(np.median(suites[suite]["comparator"][metric]))
            ratios.append(candidate / comparator if comparator > 0.0 else float("inf"))
        if not np.all(np.isfinite(ratios)):
            raise ValueError(f"training ratio is undefined: {metric}")
        paired[metric] = median_ci(ratios, 7200 + TRAINING_METRICS.index(metric))
        paired[metric]["ratio"] = "candidate_over_comparator"
    return {
        "scope": "7_sha_selected_sentinels_x_3_clean_process_repetitions",
        "device_mode": "native_primary_only_candidate_cpu_comparator_cuda",
        "by_method": aggregate,
        "paired_candidate_over_comparator": paired,
    }


def _standalone_memory(path: Path, schema: str) -> dict[str, float]:
    payload = load_json(path)
    if payload.get("schema_version") != schema or payload.get("unknown_or_test_labels_used") is not False:
        raise ValueError(f"standalone benchmark gate failed: {path}")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError(f"standalone benchmark records incomplete: {path}")
    gpu_values = [finite(record.get("peak_gpu_memory_mb", 0.0), "peak_gpu_memory_mb") for record in records]
    return {
        "peak_host_rss_mb": finite(payload.get("peak_host_rss_mb"), "peak_host_rss_mb"),
        "peak_gpu_memory_mb": max(gpu_values),
    }


def inference_summary(plan: dict[str, Any], root: Path) -> dict[str, Any]:
    modes = ("native_primary", "cpu_normalized_secondary")
    values: dict[str, dict[int, dict[str, dict[str, list[float]]]]] = {
        mode: {
            batch: {
                role: {metric: [] for metric in INFERENCE_METRICS}
                for role in ("candidate", "comparator")
            }
            for batch in (1, 64, 512)
        }
        for mode in modes
    }
    memory = {
        mode: {
            role: {"peak_host_rss_mb": [], "peak_gpu_memory_mb": []}
            for role in ("candidate", "comparator")
        }
        for mode in modes
    }
    for block in plan["inference_blocks"]:
        suite, scenario = str(block["suite"]), str(block["scenario"])
        block_root = root / "inference" / suite / scenario
        require_equivalence(
            block_root / "candidate_capture" / "equivalence.json",
            "source_components_plus_stable_runtime_shadow",
        )
        require_equivalence(
            block_root / "comparator_native_capture" / "equivalence.json",
            "runtime_vs_uninstrumented_same_device_shadow",
        )
        require_equivalence(
            block_root / "comparator_cpu_capture" / "equivalence.json",
            "runtime_vs_uninstrumented_same_device_shadow",
        )
        candidate_memory = _standalone_memory(
            block_root / "candidate_standalone_benchmark.json",
            "strict_v4_pairwise_inference_benchmark_v1",
        )
        native_memory = _standalone_memory(
            block_root / "comparator_native_standalone_benchmark.json",
            "strict_v4_opendetect_inference_benchmark_v1",
        )
        cpu_memory = _standalone_memory(
            block_root / "comparator_cpu_standalone_benchmark.json",
            "strict_v4_opendetect_inference_benchmark_v1",
        )
        for mode, comparator_memory in (
            ("native_primary", native_memory),
            ("cpu_normalized_secondary", cpu_memory),
        ):
            for role, observed in (("candidate", candidate_memory), ("comparator", comparator_memory)):
                for metric, value in observed.items():
                    memory[mode][role][metric].append(value)
            payload = load_json(block_root / mode / "efficiency_metrics.json")
            if (
                payload.get("schema_version") != "strict_v4_final_efficiency_paired_block_v2"
                or payload.get("measurement_mode") != mode
                or payload.get("candidate_comparator_input_arrays_equal") is not True
                or payload.get("unknown_or_test_labels_used") is not False
            ):
                raise ValueError(f"paired inference gate failed: {suite}/{scenario}/{mode}")
            records = payload.get("records")
            if not isinstance(records, list) or len(records) != 6:
                raise ValueError(f"paired inference records incomplete: {suite}/{scenario}/{mode}")
            seen = set()
            for record in records:
                role = str(record["method_role"])
                batch = int(record["batch_size"])
                key = (role, batch)
                if role not in ("candidate", "comparator") or batch not in (1, 64, 512) or key in seen:
                    raise ValueError("paired inference record identity is invalid")
                seen.add(key)
                for metric in INFERENCE_METRICS:
                    values[mode][batch][role][metric].append(
                        finite(record.get(metric), f"{mode}.{batch}.{role}.{metric}")
                    )
    if len(plan["inference_blocks"]) != 102:
        raise ValueError("inference coverage is incomplete")
    result: dict[str, Any] = {}
    for mode_index, mode in enumerate(modes):
        result[mode] = {"by_batch_size": {}, "standalone_memory": {}}
        for batch in (1, 64, 512):
            batch_result: dict[str, Any] = {"by_method": {}, "paired": {}}
            for role in ("candidate", "comparator"):
                batch_result["by_method"][role] = {
                    metric: median_ci(
                        values[mode][batch][role][metric],
                        8000 + mode_index * 100 + batch + INFERENCE_METRICS.index(metric),
                    )
                    for metric in INFERENCE_METRICS
                }
            for metric in INFERENCE_METRICS:
                candidate = np.asarray(values[mode][batch]["candidate"][metric])
                comparator = np.asarray(values[mode][batch]["comparator"][metric])
                if candidate.size != 102 or comparator.size != 102 or np.any(comparator <= 0.0):
                    raise ValueError("paired scenario vector is incomplete or nonpositive")
                summary = median_ci(
                    candidate / comparator,
                    9000 + mode_index * 100 + batch + INFERENCE_METRICS.index(metric),
                )
                summary["ratio"] = "candidate_over_comparator"
                batch_result["paired"][metric] = summary
            result[mode]["by_batch_size"][str(batch)] = batch_result
        for role in ("candidate", "comparator"):
            result[mode]["standalone_memory"][role] = {
                metric: median_ci(observed, 10000 + mode_index * 100 + (0 if role == "candidate" else 10) + index)
                for index, (metric, observed) in enumerate(memory[mode][role].items())
            }
    return result


def render(summary: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 final efficiency v2",
        "",
        f"Validation: **{'PASS' if summary['gates']['formal_efficiency_claim_allowed'] else 'FAIL'}**.",
        "Training scope: 7 sentinels x 3 clean-process repetitions; inference scope: 102 scenarios.",
        "All ratios are candidate/OpenDetect; latency, time, and memory favor values below 1, throughput favors values above 1.",
        "",
        "## Inference paired medians",
        "",
        "| Mode | Batch | P50 ratio | P95 ratio | P99 ratio | Throughput ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in ("native_primary", "cpu_normalized_secondary"):
        for batch in ("1", "64", "512"):
            paired = summary["inference"][mode]["by_batch_size"][batch]["paired"]
            lines.append(
                f"| {mode} | {batch} | {paired['latency_p50_ms']['median']:.4f} | "
                f"{paired['latency_p95_ms']['median']:.4f} | {paired['latency_p99_ms']['median']:.4f} | "
                f"{paired['samples_per_second']['median']:.4f} |"
            )
    lines.extend(["", "This report is descriptive and reports tradeoffs regardless of direction.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol, plan = load_json(args.protocol), load_json(args.plan)
    if protocol.get("schema_version") != "strict_v4_final_efficiency_protocol_v2" or protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("efficiency protocol validation failed")
    if plan.get("schema_version") != "strict_v4_final_efficiency_execution_plan_v2" or plan.get("manifest_sha256") != canonical_hash(plan):
        raise ValueError("efficiency plan validation failed")
    if plan.get("protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("plan/protocol binding mismatch")
    expected_sha = protocol.get("implementation_sha256", {}).get("efficiency_summarizer")
    if expected_sha != file_hash(Path(__file__)) or plan.get("implementation_sha256", {}).get("efficiency_summarizer") != expected_sha:
        raise ValueError("active efficiency summarizer SHA mismatch")
    if not (args.formal_root / "execution_complete").is_file():
        raise ValueError("formal efficiency execution is incomplete")
    summary = {
        "schema_version": "strict_v4_final_efficiency_summary_v2",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_plan_manifest_sha256": plan["manifest_sha256"],
        "analysis_implementation_sha256": expected_sha,
        "training": training_summary(plan, args.formal_root),
        "inference": inference_summary(plan, args.formal_root),
        "gates": {
            "training_blocks_complete": True,
            "inference_scenarios_complete": True,
            "equivalence_tolerance_1e_12_passes": True,
            "paired_inputs_identical": True,
            "native_and_cpu_normalized_modes_separate": True,
            "formal_efficiency_claim_allowed": True,
        },
        "claim_policy": {
            "efficiency_not_used_for_accuracy_selection": True,
            "tradeoffs_reported_regardless_of_direction": True,
            "no_efficiency_superlative_without_metric_specific_ci": True,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(render(summary), encoding="utf-8")
    (args.output_dir / "summary_complete").touch()
    print(render(summary), end="")


if __name__ == "__main__":
    main()

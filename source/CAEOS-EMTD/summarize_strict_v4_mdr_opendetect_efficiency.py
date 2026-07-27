from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


LATENCY_METRICS = (
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def bootstrap_mean(
    values: Iterable[float], *, seed: int, repetitions: int
) -> Dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if (
        array.ndim != 1
        or not len(array)
        or not np.isfinite(array).all()
        or int(repetitions) < 1
    ):
        raise ValueError("finite nonempty bootstrap values required")
    rng = np.random.default_rng(int(seed))
    sampled = array[
        rng.integers(0, len(array), size=(int(repetitions), len(array)))
    ].mean(axis=1)
    return {
        "n": int(len(array)),
        "mean": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(sampled, 0.025)),
            float(np.quantile(sampled, 0.975)),
        ],
    }


def positive_ratio(numerator: float, denominator: float) -> float:
    numerator = float(numerator)
    denominator = float(denominator)
    if (
        not np.isfinite(numerator)
        or not np.isfinite(denominator)
        or numerator <= 0.0
        or denominator <= 0.0
    ):
        raise ValueError("positive finite ratio operands required")
    return numerator / denominator


def source_identity(record: Dict[str, Any]) -> tuple[str, str, int]:
    source = record["source"]
    return (
        str(source["suite"]),
        str(source["scenario"]),
        int(source["training_seed"]),
    )


def aggregate_benchmarks(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_opendetect_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(records) != 306
    ):
        raise ValueError("canonical protocol and 306 benchmarks required")
    expected = {
        (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        ): source
        for source in protocol["sources"]
    }
    if len(expected) != 306:
        raise ValueError("protocol source identity coverage mismatch")
    by_scenario: Dict[tuple[str, str], list[Dict[str, Any]]] = defaultdict(
        list
    )
    raw_capture_ratios = []
    contexts = []
    host_peaks = []
    gpu_peaks = []
    seen = set()
    for record in records:
        if (
            record.get("schema_version")
            != "strict_v4_mdr_opendetect_efficiency_benchmark_v1"
            or record.get("state") != "complete"
            or record.get("manifest_sha256") != canonical_hash(record)
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or record.get("same_input_evidence", {}).get(
                "candidate_and_comparator_received_same_arrays"
            )
            is not True
            or record.get("same_input_evidence", {}).get("labels_loaded")
            is not False
            or record.get("exclusive_machine_preflight_marker") != "passed"
            or record.get(
                "unknown_or_test_labels_used_for_benchmark_selection"
            )
            is not False
            or record.get(
                "comparator_seed_reuse_supports_effectiveness_claim"
            )
            is not False
        ):
            raise ValueError("invalid MDR-OpenDetect benchmark record")
        identity = source_identity(record)
        if identity in seen or identity not in expected:
            raise ValueError("duplicate or unexpected benchmark identity")
        expected_source = expected[identity]
        expected_hashes = {
            "candidate_capture_manifest_file_sha256": expected_source[
                "candidate"
            ]["capture_manifest_file_sha256"],
            "candidate_capture_execution_file_sha256": expected_source[
                "candidate"
            ]["capture_execution_file_sha256"],
            "candidate_runtime_artifact_sha256": expected_source[
                "candidate"
            ]["runtime_artifact_sha256"],
            "evaluation_inputs_sha256": expected_source["candidate"][
                "evaluation_inputs_sha256"
            ],
            "comparator_seed": int(
                expected_source["comparator"]["comparator_seed"]
            ),
            "comparator_capture_manifest_file_sha256": expected_source[
                "comparator"
            ]["capture_manifest_file_sha256"],
            "comparator_runtime_artifact_sha256": expected_source[
                "comparator"
            ]["runtime_artifact_sha256"],
            "comparator_source_metrics_file_sha256": expected_source[
                "comparator"
            ]["source_metrics_file_sha256"],
        }
        for key, expected_value in expected_hashes.items():
            if record["source"].get(key) != expected_value:
                raise ValueError("benchmark source hash binding mismatch")
        seen.add(identity)
        batches = {}
        for batch in protocol["benchmark"]["batch_sizes"]:
            block = record.get("benchmark", {}).get(str(batch))
            if set(block or {}) != {"mdr_caeos_v1", "opendetect"}:
                raise ValueError("benchmark batch or method coverage mismatch")
            ratios = {}
            for metric in LATENCY_METRICS:
                ratios[metric] = positive_ratio(
                    block["mdr_caeos_v1"][metric],
                    block["opendetect"][metric],
                )
            ratios["samples_per_second"] = positive_ratio(
                block["mdr_caeos_v1"]["samples_per_second"],
                block["opendetect"]["samples_per_second"],
            )
            batches[str(batch)] = ratios
        cost = record["cost"]
        capture_ratio = {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "batches": batches,
            "artifact_ratio": positive_ratio(
                cost["mdr_artifact_bytes"],
                cost["opendetect_artifact_bytes"],
            ),
            "fit_time_ratio": positive_ratio(
                cost["mdr_total_capture_wall_seconds"],
                cost["opendetect_training_seconds"],
            ),
            "fit_time_lower_bound_diagnostic_ratio": positive_ratio(
                cost["mdr_fit_wall_seconds_lower_bound_diagnostic"],
                cost["opendetect_training_seconds"],
            ),
        }
        peak = record.get("process_peak_rss", {}).get("peak_host_rss_mb")
        if peak is None or not np.isfinite(float(peak)) or float(peak) <= 0.0:
            raise ValueError("finite positive host peak RSS required")
        gpu_peak = float(record.get("peak_gpu_memory_mb", -1.0))
        if not np.isfinite(gpu_peak) or gpu_peak < 0.0:
            raise ValueError("finite nonnegative GPU peak memory required")
        host_peaks.append(float(peak))
        gpu_peaks.append(gpu_peak)
        contexts.append(record["execution_context"])
        raw_capture_ratios.append(capture_ratio)
        by_scenario[(identity[0], identity[1])].append(capture_ratio)
    if seen != set(expected):
        raise ValueError("benchmark source coverage mismatch")
    expected_seeds = set(map(int, protocol["training_seeds"]))
    if (
        len(by_scenario) != 102
        or any(len(values) != 3 for values in by_scenario.values())
        or any(
            {int(value["training_seed"]) for value in values}
            != expected_seeds
            for values in by_scenario.values()
        )
    ):
        raise ValueError("three-seed scenario block coverage mismatch")

    scenario_blocks = []
    ratio_series: Dict[str, list[float]] = defaultdict(list)
    diagnostic_series: Dict[str, list[float]] = defaultdict(list)
    suite_series: Dict[str, Dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for (suite, scenario), values in sorted(by_scenario.items()):
        block: Dict[str, Any] = {
            "suite": suite,
            "scenario": scenario,
            "seed_count": 3,
            "batches": {},
        }
        for batch in protocol["benchmark"]["batch_sizes"]:
            batch_key = str(batch)
            block["batches"][batch_key] = {}
            for metric in (*LATENCY_METRICS, "samples_per_second"):
                value = float(
                    np.mean(
                        [
                            item["batches"][batch_key][metric]
                            for item in values
                        ]
                    )
                )
                key = f"batch{batch}_{metric}"
                block["batches"][batch_key][metric] = value
                ratio_series[key].append(value)
                suite_series[suite][key].append(value)
        for key in ("artifact_ratio", "fit_time_ratio"):
            value = float(np.mean([item[key] for item in values]))
            block[key] = value
            ratio_series[key].append(value)
            suite_series[suite][key].append(value)
        diagnostic_key = "fit_time_lower_bound_diagnostic_ratio"
        diagnostic_value = float(
            np.mean([item[diagnostic_key] for item in values])
        )
        block[diagnostic_key] = diagnostic_value
        diagnostic_series[diagnostic_key].append(diagnostic_value)
        scenario_blocks.append(block)

    repetitions = int(protocol["aggregation"]["bootstrap_repetitions"])
    base_seed = int(protocol["aggregation"]["bootstrap_seed"])
    inference = {}
    checks = {}
    for index, key in enumerate(sorted(ratio_series)):
        summary = bootstrap_mean(
            ratio_series[key],
            seed=base_seed + index,
            repetitions=repetitions,
        )
        inference[key] = summary
        if key.endswith("samples_per_second"):
            checks[key] = summary["bootstrap_95ci"][0] >= 1.0
        else:
            checks[key] = summary["bootstrap_95ci"][1] <= 1.0
    diagnostics = {
        key: bootstrap_mean(
            values,
            seed=base_seed + 1000 + index,
            repetitions=repetitions,
        )
        for index, (key, values) in enumerate(
            sorted(diagnostic_series.items())
        )
    }
    suite_equal = {
        suite: {
            key: float(np.mean(values))
            for key, values in sorted(metrics.items())
        }
        for suite, metrics in sorted(suite_series.items())
    }
    suite_equal_mean = {
        key: float(
            np.mean([suite_equal[suite][key] for suite in suite_equal])
        )
        for key in sorted(ratio_series)
    }
    context_tokens = {json.dumps(value, sort_keys=True) for value in contexts}
    integrity_checks = {
        "benchmark_count_is_306": len(records) == 306,
        "scenario_block_count_is_102": len(scenario_blocks) == 102,
        "same_inputs_used_within_every_benchmark": True,
        "all_outputs_finite": all(
            np.isfinite(value)
            for values in ratio_series.values()
            for value in values
        ),
        "failure_count_zero": True,
        "same_hardware_context_is_constant": len(context_tokens) == 1,
        "no_resource_metric_splicing": True,
        "full_capture_wall_used_for_fit_gate": True,
    }
    return {
        "benchmark_count": len(records),
        "scenario_block_count": len(scenario_blocks),
        "failure_count": 0,
        "scenario_blocks": scenario_blocks,
        "raw_per_capture_ratios": raw_capture_ratios,
        "ratio_inference": inference,
        "diagnostic_inference": diagnostics,
        "suite_equal_secondary_summary": {
            "suite_count": len(suite_equal),
            "by_suite": suite_equal,
            "equal_weight_mean": suite_equal_mean,
        },
        "resource_reporting": {
            "peak_gpu_memory_mb_min": float(np.min(gpu_peaks)),
            "peak_gpu_memory_mb_median": float(np.median(gpu_peaks)),
            "peak_gpu_memory_mb_max": float(np.max(gpu_peaks)),
            "peak_host_rss_mb_min": float(np.min(host_peaks)),
            "peak_host_rss_mb_median": float(np.median(host_peaks)),
            "peak_host_rss_mb_max": float(np.max(host_peaks)),
            "execution_context": contexts[0],
        },
        "integrity_decision": {
            "checks": integrity_checks,
            "passes": all(integrity_checks.values()),
        },
        "strict_efficiency_decision": {
            "checks": checks,
            "passes": all(checks.values()),
            "failure_blocks_only_multidimensional_efficiency_sota": True,
        },
    }


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    file_registry = []
    for source in protocol["sources"]:
        path = (
            run_root
            / "benchmarks"
            / str(source["suite"])
            / str(source["scenario"])
            / f"seed{int(source['training_seed'])}"
            / "benchmark.json"
        )
        if not path.is_file():
            raise FileNotFoundError(f"missing efficiency benchmark: {path}")
        records.append(load(path))
        file_registry.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "benchmark_file_sha256": file_hash(path),
            }
        )
    aggregate = aggregate_benchmarks(records, protocol)
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_opendetect_efficiency_summary_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate,
        "benchmark_file_registry": file_registry,
        "claim_boundary": {
            "efficiency_only_not_effectiveness": True,
            "opendetect_seed137_reuse_not_an_accuracy_claim": True,
            "full_capture_wall_is_conservative_for_mdr_fit_cost": True,
            "lower_bound_fit_ratio_is_diagnostic_only": True,
            "no_metric_scenario_suite_or_component_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol), args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

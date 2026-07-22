from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import time
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover
    resource = None

import joblib
import numpy as np
import torch

from benchmark_pairwise_runtime import batch_indices, load_views, percentile
from benchmark_pairwise_runtime_optimized import equivalence
import caeos.open_detect_runtime as open_detect_runtime_module
from caeos.open_detect_runtime import OpenDetectRuntime
import caeos.pairwise_runtime as pairwise_runtime_module
from caeos.pairwise_runtime import PairwiseRuntime
import caeos.pairwise_runtime_optimized as optimized_runtime_module
from caeos.pairwise_runtime_optimized import OptimizedPairwiseRuntime
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


METHODS = ("original", "optimized", "comparator")


def method_order(repetition: int) -> tuple[str, str, str]:
    if repetition < 0:
        raise ValueError("repetition must be nonnegative")
    offset = repetition % 3
    return METHODS[offset:] + METHODS[:offset]


def require_capture_equivalence(path: Path, schema: str, mode: str) -> None:
    payload = json.loads((path / "equivalence.json").read_text(encoding="utf-8"))
    if (
        payload.get("schema_version") != schema
        or payload.get("passes") is not True
        or payload.get("prediction_array_equal") is not True
        or float(payload.get("risk_max_absolute_difference", float("inf"))) > 1e-12
        or float(payload.get("absolute_tolerance", float("inf"))) > 1e-12
        or payload.get("equivalence_mode") != mode
        or payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"capture equivalence failed: {path}")


def identical_views(left: list[np.ndarray], right: list[np.ndarray]) -> bool:
    return len(left) == len(right) and all(
        np.array_equal(a, b) for a, b in zip(left, right)
    )


def peak_host_rss_mb() -> float | None:
    if resource is None:
        return None
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)


def validate_implementations(protocol: dict[str, Any]) -> dict[str, str]:
    paths = {
        "pairwise_runtime": Path(pairwise_runtime_module.__file__),
        "optimized_pairwise_runtime": Path(optimized_runtime_module.__file__),
        "open_detect_runtime": Path(open_detect_runtime_module.__file__),
        "triad_block_runner": Path(__file__),
    }
    expected = protocol.get("implementation_sha256", {})
    observed = {name: file_hash(path.resolve()) for name, path in paths.items()}
    for name, value in observed.items():
        if expected.get(name) != value:
            raise ValueError(f"active implementation SHA mismatch: {name}")
    return observed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--candidate-capture", type=Path, required=True)
    parser.add_argument("--comparator-capture", type=Path, required=True)
    parser.add_argument(
        "--measurement-mode",
        choices=("native_primary", "cpu_normalized_secondary"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if (
        protocol.get("schema_version")
        != "strict_v4_optimized_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("optimized efficiency protocol validation failed")
    observed_hashes = validate_implementations(protocol)
    require_capture_equivalence(
        args.candidate_capture,
        "strict_v4_pairwise_runtime_equivalence_v2",
        "source_components_plus_stable_runtime_shadow",
    )
    require_capture_equivalence(
        args.comparator_capture,
        "strict_v4_opendetect_runtime_equivalence_v1",
        "runtime_vs_uninstrumented_same_device_shadow",
    )
    original = joblib.load(args.candidate_capture / "pairwise_runtime.joblib")
    comparator = joblib.load(args.comparator_capture / "opendetect_runtime.joblib")
    if not isinstance(original, PairwiseRuntime) or not isinstance(
        comparator, OpenDetectRuntime
    ):
        raise TypeError("triad runtime types are invalid")
    expected_device = "cuda" if args.measurement_mode == "native_primary" else "cpu"
    if torch.device(comparator.device_name).type != expected_device:
        raise ValueError("OpenDetect device does not match measurement mode")
    original_views = load_views(args.candidate_capture / "benchmark_inputs.npz")
    comparator_views = load_views(args.comparator_capture / "benchmark_inputs.npz")
    if not identical_views(original_views, comparator_views):
        raise ValueError("triad benchmark inputs differ")
    optimized = OptimizedPairwiseRuntime(original)
    gate = equivalence(original, optimized, original_views)
    if not gate["passes"]:
        raise ValueError(f"optimized full-input equivalence failed: {gate}")
    settings = protocol["benchmark"]
    sample_count = len(original_views[0])
    runtimes = {
        "original": original,
        "optimized": optimized,
        "comparator": comparator,
    }
    records = []
    for raw_batch_size in settings["batch_sizes"]:
        batch_size = int(raw_batch_size)
        for runtime in runtimes.values():
            for repetition in range(int(settings["warmup_repetitions"])):
                indices = batch_indices(sample_count, batch_size, repetition)
                runtime.predict([view[indices] for view in original_views])
            if isinstance(runtime, OpenDetectRuntime):
                runtime.synchronize()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        latencies = {name: [] for name in METHODS}
        checksums = {name: 0.0 for name in METHODS}
        timed_samples = {name: 0 for name in METHODS}
        for repetition in range(int(settings["timed_repetitions"])):
            indices = batch_indices(
                sample_count,
                batch_size,
                int(settings["warmup_repetitions"]) + repetition,
            )
            batch = [view[indices] for view in original_views]
            for name in method_order(repetition):
                runtime = runtimes[name]
                if isinstance(runtime, OpenDetectRuntime):
                    runtime.synchronize()
                started = time.perf_counter_ns()
                output = runtime.predict(batch)
                if isinstance(runtime, OpenDetectRuntime):
                    runtime.synchronize()
                latencies[name].append(
                    (time.perf_counter_ns() - started) / 1_000_000.0
                )
                checksums[name] += float(output["risk"].sum())
                timed_samples[name] += len(indices)
        for name in METHODS:
            values = latencies[name]
            total_seconds = sum(values) / 1000.0
            records.append(
                {
                    "method_role": name,
                    "method": protocol["methods"][name],
                    "batch_size": batch_size,
                    "warmup_repetitions": int(settings["warmup_repetitions"]),
                    "timed_repetitions": int(settings["timed_repetitions"]),
                    "latency_p50_ms": percentile(values, 50),
                    "latency_p95_ms": percentile(values, 95),
                    "latency_p99_ms": percentile(values, 99),
                    "samples_per_second": float(
                        timed_samples[name] / total_seconds
                    ),
                    "latency_samples_ms": values,
                    "output_checksum": checksums[name],
                }
            )
    payload = {
        "schema_version": "strict_v4_optimized_efficiency_triad_block_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "measurement_mode": args.measurement_mode,
        "sample_count": sample_count,
        "view_count": len(original_views),
        "records": records,
        "method_order_rule": settings["method_order"],
        "optimized_equivalence": gate,
        "input_arrays_equal": True,
        "deployment_artifact_bytes": {
            "original": (
                args.candidate_capture / "pairwise_runtime.joblib"
            ).stat().st_size,
            "optimized": (
                args.candidate_capture / "pairwise_runtime.joblib"
            ).stat().st_size,
            "optimized_wrapper_persistent_bytes": 0,
            "comparator": (
                args.comparator_capture / "opendetect_runtime.joblib"
            ).stat().st_size,
        },
        "peak_host_rss_mb": peak_host_rss_mb(),
        "peak_gpu_memory_mb": (
            float(torch.cuda.max_memory_allocated() / (1024**2))
            if torch.cuda.is_available()
            else 0.0
        ),
        "hardware": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_logical_count": os.cpu_count(),
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": (
                torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
            ),
        },
        "active_implementation_sha256": observed_hashes,
        "unknown_or_test_labels_used": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()

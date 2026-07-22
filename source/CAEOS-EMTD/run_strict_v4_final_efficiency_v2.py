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
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

import joblib
import numpy as np
import torch

from benchmark_pairwise_runtime import batch_indices, load_views, percentile
import caeos.open_detect_runtime as open_detect_runtime_module
import caeos.pairwise_runtime as pairwise_runtime_module
from caeos.open_detect_runtime import OpenDetectRuntime
from caeos.pairwise_runtime import PairwiseRuntime
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def method_order(repetition: int) -> tuple[str, str]:
    if repetition < 0:
        raise ValueError("repetition must be nonnegative")
    return (
        ("candidate", "comparator")
        if repetition % 2 == 0
        else ("comparator", "candidate")
    )


def require_equivalence(
    capture_dir: Path,
    expected_schema: str,
    maximum_absolute_tolerance: float = 1e-12,
    required_mode: str | None = None,
) -> dict[str, Any]:
    path = capture_dir / "equivalence.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    difference = float(payload.get("risk_max_absolute_difference", float("inf")))
    recorded_tolerance = float(payload.get("absolute_tolerance", float("inf")))
    if (
        payload.get("schema_version") != expected_schema
        or payload.get("passes") is not True
        or payload.get("prediction_array_equal") is not True
        or difference > maximum_absolute_tolerance
        or recorded_tolerance > maximum_absolute_tolerance
        or (required_mode is not None and payload.get("equivalence_mode") != required_mode)
        or payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"runtime equivalence gate failed under {capture_dir}")
    return payload


def identical_views(left: list[np.ndarray], right: list[np.ndarray]) -> bool:
    return len(left) == len(right) and all(
        np.array_equal(a, b) for a, b in zip(left, right)
    )


def hardware() -> dict[str, object]:
    cuda = torch.cuda.is_available()
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_logical_count": os.cpu_count(),
        "torch": torch.__version__,
        "cuda_available": cuda,
        "cuda_version": torch.version.cuda,
        "gpu_name": torch.cuda.get_device_name(0) if cuda else None,
    }


def validate_active_implementation_hashes(
    protocol: dict[str, Any], overrides: dict[str, Path] | None = None
) -> dict[str, str]:
    paths = {
        "candidate_pairwise_runtime": Path(pairwise_runtime_module.__file__),
        "comparator_open_detect_runtime": Path(open_detect_runtime_module.__file__),
        "efficiency_paired_runner": Path(__file__),
    }
    paths.update(overrides or {})
    expected = protocol.get("implementation_sha256")
    if not isinstance(expected, dict):
        raise ValueError("protocol implementation SHA registry is missing")
    observed = {}
    for name, path in paths.items():
        value = file_hash(path.resolve())
        observed[name] = value
        if expected.get(name) != value:
            raise ValueError(f"active implementation SHA mismatch: {name}")
    return observed


def peak_host_rss_mb() -> float | None:
    if resource is None:
        return None
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)


def require_device_mode(mode: str, comparator: OpenDetectRuntime) -> None:
    comparator_device = torch.device(comparator.device_name).type
    expected = "cuda" if mode == "native_primary" else "cpu"
    if comparator_device != expected:
        raise ValueError(
            f"{mode} requires comparator device {expected}, got {comparator_device}"
        )
    if mode == "native_primary" and not torch.cuda.is_available():
        raise ValueError("native_primary requires an available CUDA device")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one paired strict-v4 efficiency block")
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
    if protocol.get("schema_version") != "strict_v4_final_efficiency_protocol_v2":
        raise ValueError("unexpected final efficiency protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("final efficiency protocol SHA mismatch")
    active_implementation_sha256 = validate_active_implementation_hashes(protocol)
    require_equivalence(
        args.candidate_capture,
        "strict_v4_pairwise_runtime_equivalence_v2",
        required_mode="source_components_plus_stable_runtime_shadow",
    )
    require_equivalence(
        args.comparator_capture,
        "strict_v4_opendetect_runtime_equivalence_v1",
        required_mode="runtime_vs_uninstrumented_same_device_shadow",
    )
    candidate = joblib.load(args.candidate_capture / "pairwise_runtime.joblib")
    comparator = joblib.load(args.comparator_capture / "opendetect_runtime.joblib")
    if not isinstance(candidate, PairwiseRuntime) or not isinstance(comparator, OpenDetectRuntime):
        raise TypeError("paired efficiency runtime types are invalid")
    require_device_mode(args.measurement_mode, comparator)
    candidate_views = load_views(args.candidate_capture / "benchmark_inputs.npz")
    comparator_views = load_views(args.comparator_capture / "benchmark_inputs.npz")
    if not identical_views(candidate_views, comparator_views):
        raise ValueError("candidate and comparator benchmark inputs differ")
    views = candidate_views
    sample_count = len(views[0])
    settings = protocol["inference_benchmark"]
    warmups = int(settings["warmup_repetitions"])
    repetitions = int(settings["timed_repetitions"])
    runtimes = {"candidate": candidate, "comparator": comparator}
    records = []
    for batch_size in settings["batch_sizes"]:
        for name, runtime in runtimes.items():
            for repetition in range(warmups):
                indices = batch_indices(sample_count, int(batch_size), repetition)
                runtime.predict([view[indices] for view in views])
            if isinstance(runtime, OpenDetectRuntime):
                runtime.synchronize()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        latencies = {"candidate": [], "comparator": []}
        checksums = {"candidate": 0.0, "comparator": 0.0}
        timed_samples = {"candidate": 0, "comparator": 0}
        for repetition in range(repetitions):
            indices = batch_indices(sample_count, int(batch_size), warmups + repetition)
            batch = [view[indices] for view in views]
            for name in method_order(repetition):
                runtime = runtimes[name]
                if isinstance(runtime, OpenDetectRuntime):
                    runtime.synchronize()
                started = time.perf_counter_ns()
                output = runtime.predict(batch)
                if isinstance(runtime, OpenDetectRuntime):
                    runtime.synchronize()
                latencies[name].append((time.perf_counter_ns() - started) / 1_000_000.0)
                checksums[name] += float(output["risk"].sum())
                timed_samples[name] += len(indices)
        for name in ("candidate", "comparator"):
            values = latencies[name]
            total_seconds = sum(values) / 1000.0
            records.append({
                "method_role": name,
                "method": protocol["methods"][name],
                "batch_size": int(batch_size),
                "warmup_repetitions": warmups,
                "timed_repetitions": repetitions,
                "latency_p50_ms": percentile(values, 50),
                "latency_p95_ms": percentile(values, 95),
                "latency_p99_ms": percentile(values, 99),
                "samples_per_second": float(timed_samples[name] / total_seconds),
                "latency_samples_ms": values,
                "output_checksum": checksums[name],
            })
    payload = {
        "schema_version": "strict_v4_final_efficiency_paired_block_v2",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "sample_count": sample_count,
        "view_count": len(views),
        "method_order_rule": "candidate_first_on_even_repetitions_comparator_first_on_odd",
        "measurement_mode": args.measurement_mode,
        "records": records,
        "peak_host_rss_mb": peak_host_rss_mb(),
        "peak_gpu_memory_mb": (
            float(torch.cuda.max_memory_allocated() / (1024**2))
            if torch.cuda.is_available()
            else 0.0
        ),
        "hardware": hardware(),
        "active_implementation_sha256": active_implementation_sha256,
        "candidate_comparator_input_arrays_equal": True,
        "unknown_or_test_labels_used": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

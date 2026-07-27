from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, Sequence

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash

try:
    import resource
except ImportError:  # pragma: no cover - Windows development hosts
    resource = None


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def exact_batch(
    views: Sequence[np.ndarray], batch_size: int
) -> list[np.ndarray]:
    if int(batch_size) <= 0 or not views:
        raise ValueError("positive batch size and non-empty views required")
    lengths = {len(np.asarray(view)) for view in views}
    if len(lengths) != 1 or next(iter(lengths)) <= 0:
        raise ValueError("benchmark views must be aligned and non-empty")
    length = next(iter(lengths))
    indices = np.arange(int(batch_size), dtype=np.int64) % length
    return [np.asarray(view)[indices].copy() for view in views]


def timing_summary(
    timings_seconds: Sequence[float], batch_size: int
) -> Dict[str, float]:
    values = np.asarray(timings_seconds, dtype=np.float64)
    if (
        values.ndim != 1
        or not len(values)
        or not np.isfinite(values).all()
        or np.any(values <= 0.0)
    ):
        raise ValueError("finite positive timing values required")
    return {
        "latency_p50_ms": float(np.quantile(values, 0.50) * 1000.0),
        "latency_p95_ms": float(np.quantile(values, 0.95) * 1000.0),
        "latency_p99_ms": float(np.quantile(values, 0.99) * 1000.0),
        "samples_per_second": float(int(batch_size) / np.median(values)),
    }


def benchmark_method(runtime, views, repetitions: int) -> list[float]:
    timings = []
    for _ in range(int(repetitions)):
        started = time.perf_counter()
        output = runtime.predict(views)
        elapsed = time.perf_counter() - started
        if (
            not isinstance(output, dict)
            or "prediction" not in output
            or len(output["prediction"]) != len(views[0])
        ):
            raise ValueError("runtime benchmark output is incomplete")
        timings.append(float(elapsed))
    return timings


def peak_rss() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def peak_rss_mb(raw_value: int | None) -> float | None:
    if raw_value is None:
        return None
    divisor = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return float(raw_value / divisor)


def execution_context() -> Dict[str, Any]:
    affinity = (
        sorted(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None
    )
    thread_variables = {
        name: os.environ.get(name)
        for name in (
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        )
    }
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "logical_cpu_count": os.cpu_count(),
        "cpu_affinity": affinity,
        "thread_environment": thread_variables,
        "gpu_used": False,
    }


def benchmark(
    *,
    capture_dir: Path,
    protocol: Dict[str, Any],
    source: Dict[str, Any],
    output: Path,
) -> Dict[str, Any]:
    if os.environ.get("MDR_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_selected_system_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR selected-system protocol required")
    identity = (
        str(source["suite"]),
        str(source["scenario"]),
        int(source["training_seed"]),
    )
    matches = [
        item
        for item in protocol["sources"]
        if (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        )
        == identity
    ]
    if len(matches) != 1:
        raise ValueError("MDR system source identity is not in protocol")
    expected_source = matches[0]
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = load(manifest_path)
    artifact = capture_dir / manifest["runtime_artifact"]
    inputs_path = capture_dir / manifest["evaluation_inputs"]
    if (
        manifest.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or manifest.get("task", {}).get("suite") != identity[0]
        or manifest.get("task", {}).get("scenario") != identity[1]
        or int(manifest.get("training_seed", -1)) != identity[2]
        or capture_dir.resolve()
        != Path(expected_source["capture_dir"]).resolve()
        or file_hash(manifest_path)
        != expected_source["capture_manifest_file_sha256"]
        or file_hash(artifact) != manifest["runtime_artifact_sha256"]
        or manifest["runtime_artifact_sha256"]
        != expected_source["mdr_runtime_sha256"]
        or file_hash(inputs_path) != manifest["evaluation_inputs_sha256"]
        or manifest["evaluation_inputs_sha256"]
        != expected_source["evaluation_inputs_sha256"]
        or manifest.get("roundtrip", {}).get("passes") is not True
    ):
        raise ValueError("invalid MDR selected-system source capture")
    runtime = joblib.load(artifact)
    inputs = np.load(inputs_path, allow_pickle=False)
    modality_count = int(runtime.evidence()["modality_count"])
    views = [
        np.asarray(inputs[f"view_{index}"])
        for index in range(modality_count)
    ]
    pairwise_artifact = output.parent / "embedded_pairwise_runtime.joblib"
    pairwise_artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(runtime.clean_runtime, pairwise_artifact, compress=3)
    loaded_pairwise = joblib.load(pairwise_artifact)
    original = runtime.clean_runtime.predict(views)
    reloaded = loaded_pairwise.predict(views)
    pairwise_roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(
                original["prediction"], reloaded["prediction"]
            )
        ),
        "risk_max_absolute_difference": float(
            np.max(np.abs(original["risk"] - reloaded["risk"]))
        ),
        "probability_max_absolute_difference": float(
            np.max(
                np.abs(
                    original["probability"] - reloaded["probability"]
                )
            )
        ),
    }
    pairwise_roundtrip["passes"] = bool(
        pairwise_roundtrip["prediction_array_equal"]
        and pairwise_roundtrip["risk_max_absolute_difference"] <= 1e-12
        and pairwise_roundtrip["probability_max_absolute_difference"]
        <= 1e-12
    )
    if not pairwise_roundtrip["passes"]:
        raise ValueError("embedded Pairwise serialization roundtrip failed")
    benchmark_policy = protocol["benchmark"]
    warmups = int(benchmark_policy["warmup_repetitions"])
    repetitions = int(benchmark_policy["timed_repetitions"])
    blocks = {}
    peak_before = peak_rss()
    for batch_size in benchmark_policy["batch_sizes"]:
        batch = exact_batch(views, int(batch_size))
        for _ in range(warmups):
            runtime.predict(batch)
            loaded_pairwise.predict(batch)
        timings = {"mdr_caeos_v1": [], "caeos_pairwise": []}
        for repetition in range(repetitions):
            order = (
                ("mdr_caeos_v1", runtime),
                ("caeos_pairwise", loaded_pairwise),
            )
            if repetition % 2:
                order = tuple(reversed(order))
            for name, method in order:
                timings[name].extend(benchmark_method(method, batch, 1))
        blocks[str(batch_size)] = {
            name: {
                **timing_summary(values, int(batch_size)),
                "raw_seconds": values,
            }
            for name, values in timings.items()
        }
    peak_after = peak_rss()
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_selected_system_benchmark_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source": {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "capture_manifest_file_sha256": file_hash(manifest_path),
            "mdr_runtime_sha256": manifest["runtime_artifact_sha256"],
            "evaluation_inputs_sha256": manifest[
                "evaluation_inputs_sha256"
            ],
        },
        "roundtrip": {
            "mdr_capture": manifest["roundtrip"],
            "embedded_pairwise": pairwise_roundtrip,
        },
        "benchmark": blocks,
        "cost": {
            "mdr_fit_wall_seconds_lower_bound": float(
                manifest["clean_capture_wall_seconds"]
                + manifest["robust_capture_wall_seconds"]
            ),
            "pairwise_fit_wall_seconds": float(
                manifest["clean_capture_wall_seconds"]
            ),
            "mdr_artifact_bytes": int(manifest["runtime_artifact_bytes"]),
            "pairwise_artifact_bytes": int(pairwise_artifact.stat().st_size),
            "pairwise_artifact_sha256": file_hash(pairwise_artifact),
        },
        "process_peak_rss": {
            "ru_maxrss_before": peak_before,
            "ru_maxrss_after": peak_after,
            "peak_host_rss_mb": peak_rss_mb(peak_after),
            "raw_unit": (
                "bytes" if sys.platform == "darwin" else "kibibytes"
            )
            if peak_after is not None
            else "unavailable",
        },
        "peak_gpu_memory_mb": 0.0,
        "execution_context": execution_context(),
        "exclusive_machine_preflight_marker": "passed",
        "unknown_or_test_labels_used_for_benchmark_selection": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = benchmark(
        capture_dir=args.capture_dir,
        protocol=load(args.protocol),
        source={
            "suite": args.suite,
            "scenario": args.scenario,
            "training_seed": args.training_seed,
        },
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()

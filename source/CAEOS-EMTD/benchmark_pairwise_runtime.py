from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Sequence

try:
    import resource
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

import joblib
import numpy as np

from caeos.pairwise_runtime import PairwiseRuntime


def batch_indices(sample_count: int, batch_size: int, repetition: int) -> np.ndarray:
    if sample_count <= 0 or batch_size <= 0 or repetition < 0:
        raise ValueError("sample_count and batch_size must be positive")
    start = (int(repetition) * int(batch_size)) % int(sample_count)
    return np.arange(start, start + int(batch_size), dtype=np.int64) % sample_count


def percentile(values: Sequence[float], quantile: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), quantile))


def peak_host_rss_mb() -> float | None:
    if resource is None:
        return None
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)


def load_views(path: Path) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        names = sorted(
            archive.files,
            key=lambda name: int(name.split("_", 1)[1]),
        )
        if names != [f"view_{index}" for index in range(len(names))]:
            raise ValueError("benchmark input views are not contiguous")
        views = [np.asarray(archive[name]) for name in names]
    if not views or len({len(view) for view in views}) != 1:
        raise ValueError("benchmark input views are empty or misaligned")
    return views


def benchmark(
    runtime: PairwiseRuntime,
    views: Sequence[np.ndarray],
    batch_sizes: Sequence[int],
    warmups: int,
    repetitions: int,
) -> list[dict[str, object]]:
    if warmups < 0 or repetitions <= 0:
        raise ValueError("warmups must be nonnegative and repetitions positive")
    sample_count = len(views[0])
    results = []
    for batch_size in batch_sizes:
        for repetition in range(warmups):
            indices = batch_indices(sample_count, batch_size, repetition)
            runtime.predict([view[indices] for view in views])
        latencies_ms = []
        checksum = 0.0
        for repetition in range(repetitions):
            indices = batch_indices(sample_count, batch_size, warmups + repetition)
            batch = [view[indices] for view in views]
            started = time.perf_counter_ns()
            output = runtime.predict(batch)
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
            latencies_ms.append(elapsed_ms)
            checksum += float(output["risk"].sum())
            if len(output["risk"]) != batch_size:
                raise RuntimeError("runtime returned an invalid batch size")
        total_seconds = sum(latencies_ms) / 1000.0
        results.append(
            {
                "batch_size": int(batch_size),
                "warmup_repetitions": int(warmups),
                "timed_repetitions": int(repetitions),
                "latency_p50_ms": percentile(latencies_ms, 50),
                "latency_p95_ms": percentile(latencies_ms, 95),
                "latency_p99_ms": percentile(latencies_ms, 99),
                "samples_per_second": float(batch_size * repetitions / total_seconds),
                "latency_samples_ms": latencies_ms,
                "output_checksum": checksum,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark captured pairwise inference")
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-sizes", default="1,64,512")
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    runtime = joblib.load(args.runtime)
    if not isinstance(runtime, PairwiseRuntime):
        raise TypeError("runtime artifact is not a PairwiseRuntime")
    views = load_views(args.inputs)
    batch_sizes = [int(value) for value in args.batch_sizes.split(",") if value]
    records = benchmark(runtime, views, batch_sizes, args.warmups, args.repetitions)
    payload = {
        "schema_version": "strict_v4_pairwise_inference_benchmark_v1",
        "method": "caeos_pairwise",
        "input_sample_count": len(views[0]),
        "view_count": len(views),
        "records": records,
        "peak_host_rss_mb": peak_host_rss_mb(),
        "peak_gpu_memory_mb": 0.0,
        "runtime_evidence": runtime.evidence(),
        "unknown_or_test_labels_used": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

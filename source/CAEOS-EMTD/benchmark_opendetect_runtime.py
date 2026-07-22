from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import joblib
import numpy as np
import torch

from benchmark_pairwise_runtime import (
    batch_indices,
    load_views,
    peak_host_rss_mb,
    percentile,
)
from caeos.open_detect_runtime import OpenDetectRuntime


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark captured OpenDetect inference")
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-sizes", default="1,64,512")
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    runtime = joblib.load(args.runtime)
    if not isinstance(runtime, OpenDetectRuntime):
        raise TypeError("runtime artifact is not an OpenDetectRuntime")
    views = load_views(args.inputs)
    sample_count = len(views[0])
    records = []
    for batch_size in [int(value) for value in args.batch_sizes.split(",") if value]:
        for repetition in range(args.warmups):
            indices = batch_indices(sample_count, batch_size, repetition)
            runtime.predict([view[indices] for view in views])
        runtime.synchronize()
        if torch.device(runtime.device_name).type == "cuda":
            torch.cuda.reset_peak_memory_stats(torch.device(runtime.device_name))
        latencies_ms = []
        checksum = 0.0
        for repetition in range(args.repetitions):
            indices = batch_indices(sample_count, batch_size, args.warmups + repetition)
            batch = [view[indices] for view in views]
            runtime.synchronize()
            started = time.perf_counter_ns()
            output = runtime.predict(batch)
            runtime.synchronize()
            latencies_ms.append((time.perf_counter_ns() - started) / 1_000_000.0)
            checksum += float(output["risk"].sum())
        total_seconds = sum(latencies_ms) / 1000.0
        peak_gpu = (
            float(torch.cuda.max_memory_allocated(torch.device(runtime.device_name)) / (1024**2))
            if torch.device(runtime.device_name).type == "cuda"
            else 0.0
        )
        records.append({
            "batch_size": batch_size,
            "warmup_repetitions": args.warmups,
            "timed_repetitions": args.repetitions,
            "latency_p50_ms": percentile(latencies_ms, 50),
            "latency_p95_ms": percentile(latencies_ms, 95),
            "latency_p99_ms": percentile(latencies_ms, 99),
            "samples_per_second": float(batch_size * args.repetitions / total_seconds),
            "latency_samples_ms": latencies_ms,
            "peak_gpu_memory_mb": peak_gpu,
            "output_checksum": checksum,
        })
    payload = {
        "schema_version": "strict_v4_opendetect_inference_benchmark_v1",
        "method": "opendetect",
        "input_sample_count": sample_count,
        "view_count": len(views),
        "device": runtime.device_name,
        "records": records,
        "peak_host_rss_mb": peak_host_rss_mb(),
        "runtime_evidence": runtime.evidence(),
        "unknown_or_test_labels_used": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded A09 runtime search without changing the frozen model or thresholds."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from hft_mgbs.gpu_service import A09BundleBackend, MAX_BATCH_SIZE


def percentile(values, quantile):
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * quantile)))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-jobs", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[64, 512])
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    if args.repeats < 3:
        raise ValueError("--repeats must be at least 3")
    if any(size < 1 or size > MAX_BATCH_SIZE for size in args.batch_sizes):
        raise ValueError("batch sizes must be within 1..512")

    results = []
    for n_jobs in args.n_jobs:
        backend = A09BundleBackend(args.model, model_n_jobs=n_jobs)
        warmup_us = backend.warmup(MAX_BATCH_SIZE)
        for batch_size in args.batch_sizes:
            flows = [
                {
                    "flow_id": "{}-{}-{}".format(n_jobs, batch_size, index),
                    "features": {"flow_packets": float(index + 1)},
                }
                for index in range(batch_size)
            ]
            samples_us = []
            for _ in range(args.repeats):
                started = time.perf_counter()
                predictions = backend.predict(flows)
                samples_us.append((time.perf_counter() - started) * 1_000_000.0)
                if len(predictions) != batch_size:
                    raise RuntimeError("incomplete A09 prediction batch")
            median_us = statistics.median(samples_us)
            results.append(
                {
                    "candidate_id": "A09",
                    "runtime_candidate": "jobs{}_batch{}".format(
                        n_jobs, batch_size
                    ),
                    "model_n_jobs": n_jobs,
                    "batch_size": batch_size,
                    "repeats": args.repeats,
                    "warmup_us": warmup_us,
                    "latency_p50_us": median_us,
                    "latency_p99_us": percentile(samples_us, 0.99),
                    "latency_max_us": max(samples_us),
                    "throughput_flows_s": batch_size
                    / (median_us / 1_000_000.0),
                    "samples_us": samples_us,
                }
            )

    payload = {
        "schema_version": 1,
        "search_scope": "runtime_only; frozen A09 features/models/thresholds",
        "candidate_count": len(results),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

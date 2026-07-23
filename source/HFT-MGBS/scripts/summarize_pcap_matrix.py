"""Summarize a repeated PCAP matrix without promoting it to final Pareto evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.experiment import summarize_offline_runs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    parser.add_argument("--max-budget-overrun-count", type=int, default=0)
    parser.add_argument("--min-key-flow-coverage", type=float, default=0.99)
    parser.add_argument("--max-cpu-utilization", type=float, default=0.85)
    parser.add_argument("--max-memory-utilization", type=float, default=0.85)
    parser.add_argument("--max-gpu-utilization", type=float, default=0.85)
    parser.add_argument("--max-gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--max-p99-latency-us", type=float)
    parser.add_argument("--max-p999-latency-us", type=float)
    args = parser.parse_args()
    named_runs = []
    for path in sorted(args.result_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            named_runs.append((path.name, json.load(handle)))
    summary = summarize_offline_runs(
        named_runs,
        minimum_repeats=args.minimum_repeats,
        max_budget_overrun_count=args.max_budget_overrun_count,
        min_key_flow_coverage=args.min_key_flow_coverage,
        max_cpu_utilization=args.max_cpu_utilization,
        max_memory_utilization=args.max_memory_utilization,
        max_gpu_utilization=args.max_gpu_utilization,
        max_gpu_memory_utilization=args.max_gpu_memory_utilization,
        max_p99_latency_us=args.max_p99_latency_us,
        max_p999_latency_us=args.max_p999_latency_us,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["candidate_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Evaluate deployment candidates after hard constraints and emit Pareto evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.optimization import CandidateMetrics, ConstraintProfile, ParetoOptimizer


def smoke_inputs():
    profile = ConstraintProfile(
        target_load_mpps=1.0,
        max_packet_drop_count=0,
        max_p99_latency_us=200.0,
        max_p999_latency_us=400.0,
        max_cpu_utilization=0.85,
        max_gpu_utilization=0.85,
        max_memory_utilization=0.85,
        max_gpu_memory_utilization=0.85,
        max_budget_overrun_count=0,
        min_key_flow_coverage=0.99,
        max_fallback_recovery_s=2.0,
    )
    common = dict(
        throughput_mpps=1.2,
        packet_drop_count=0,
        p999_latency_us=320.0,
        memory_utilization=0.55,
        gpu_memory_utilization=0.45,
        budget_overrun_count=0,
        complexity=0.40,
    )
    candidates = [
        CandidateMetrics(
            name="accuracy_only",
            quality=0.99,
            gain_per_cost=0.70,
            p99_latency_us=230.0,
            cpu_utilization=0.90,
            gpu_utilization=0.90,
            key_flow_coverage=0.96,
            fallback_recovery_s=3.0,
            packet_drop_count=4,
            **{key: value for key, value in common.items() if key != "packet_drop_count"}
        ),
        CandidateMetrics(
            name="balanced_cascade",
            quality=0.95,
            gain_per_cost=1.00,
            p99_latency_us=160.0,
            cpu_utilization=0.68,
            gpu_utilization=0.62,
            key_flow_coverage=0.997,
            fallback_recovery_s=1.2,
            **common
        ),
        CandidateMetrics(
            name="efficient_cascade",
            quality=0.91,
            gain_per_cost=1.35,
            p99_latency_us=105.0,
            cpu_utilization=0.48,
            gpu_utilization=0.25,
            key_flow_coverage=0.995,
            fallback_recovery_s=0.8,
            **common
        ),
    ]
    return profile, candidates


def load_inputs(profile_path, candidates_path):
    with profile_path.open("r", encoding="utf-8") as handle:
        profile = ConstraintProfile.from_mapping(json.load(handle))
    with candidates_path.open("r", encoding="utf-8") as handle:
        candidates = [CandidateMetrics.from_mapping(item) for item in json.load(handle)]
    return profile, candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        profile, candidates = smoke_inputs()
    elif args.profile and args.candidates:
        profile, candidates = load_inputs(args.profile, args.candidates)
    else:
        parser.error("use --smoke or provide both --profile and --candidates")
    selection = ParetoOptimizer(profile).select(candidates)
    print(json.dumps(selection.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if selection.champion is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())

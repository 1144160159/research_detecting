"""Join hard-gated performance and grouped quality before offline Pareto ranking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.experiment import summarize_offline_runs
from hft_mgbs.quality import summarize_quality_runs


def load_named(directory):
    loaded = []
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            loaded.append((path.name, json.load(handle)))
    return loaded


def dominates(left, right):
    objectives = (
        ("throughput_mpps_min", "max"),
        ("p99_latency_us_max", "min"),
        ("resource_pressure_max", "min"),
        ("macro_f1_min", "max"),
        ("ece_max", "min"),
    )
    no_worse = True
    strictly_better = False
    for metric, direction in objectives:
        lv, rv = left[metric], right[metric]
        if direction == "max":
            no_worse = no_worse and lv >= rv
            strictly_better = strictly_better or lv > rv
        else:
            no_worse = no_worse and lv <= rv
            strictly_better = strictly_better or lv < rv
    return no_worse and strictly_better


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("performance_dir", type=Path)
    parser.add_argument("quality_dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    parser.add_argument("--min-macro-f1", type=float)
    parser.add_argument("--max-p99-latency-us", type=float)
    parser.add_argument("--max-p999-latency-us", type=float)
    args = parser.parse_args()
    performance = summarize_offline_runs(
        load_named(args.performance_dir),
        minimum_repeats=args.minimum_repeats,
        max_p99_latency_us=args.max_p99_latency_us,
        max_p999_latency_us=args.max_p999_latency_us,
    )
    quality = summarize_quality_runs(
        load_named(args.quality_dir), minimum_repeats=args.minimum_repeats
    )
    quality_by_key = {
        (item["mode"], item["batch_size"], int(item["budget_us"])): item
        for item in quality["candidates"]
    }
    candidates = []
    for perf in performance["candidates"]:
        key = (perf["mode"], perf["batch_size"], int(perf["budget_us"]))
        candidate = dict(perf)
        candidate["joint_gate_violations"] = list(perf["offline_gate_violations"])
        quality_item = quality_by_key.get(key)
        if quality_item is None:
            candidate["joint_gate_violations"].append("quality_evidence.missing")
        else:
            for metric in (
                "macro_f1_min",
                "balanced_accuracy_min",
                "capture_balanced_accuracy_min",
                "auroc_min",
                "auprc_min",
                "ece_max",
                "flow_sample_count_min",
                "feature_count_min",
            ):
                candidate[metric] = quality_item[metric]
            if not quality_item["repeat_gate_passed"]:
                candidate["joint_gate_violations"].append("quality_repeat_count")
            if (
                args.min_macro_f1 is not None
                and quality_item["macro_f1_min"] < args.min_macro_f1
            ):
                candidate["joint_gate_violations"].append("macro_f1_min")
        candidate["offline_joint_gate_passed"] = not candidate[
            "joint_gate_violations"
        ]
        candidates.append(candidate)
    eligible = [item for item in candidates if item["offline_joint_gate_passed"]]
    front = [
        item["name"]
        for item in eligible
        if not any(dominates(other, item) for other in eligible if other is not item)
    ]
    output = {
        "schema_version": 1,
        "scope": "offline_joint_preselection_only",
        "hard_constraints_applied_before_pareto": True,
        "quality_threshold_frozen": args.min_macro_f1 is not None,
        "eligible_candidate_count": len(eligible),
        "offline_joint_front": sorted(front),
        "final_pareto_eligible": False,
        "missing_final_evidence": [
            "throughput_live_replay",
            "nic_packet_drop",
            "end_to_end_p99",
            "end_to_end_p999",
            "fallback_recovery_in_same_candidate_run",
            "frozen_quality_threshold_and_independent_holdout",
        ],
        "candidates": candidates,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if candidates else 2


if __name__ == "__main__":
    raise SystemExit(main())

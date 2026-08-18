"""Conservatively summarize repeated USTC-to-UNSW holdout runs."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


RESULT_NAME = re.compile(r"^(normal|fallback)_repeat(\d+)\.json$")

DEFAULT_HARD_CONSTRAINTS = {
    "min_macro_f1_min": 0.7,
    "min_attack_recall_min": 0.72,
    "min_benign_recall_min": 0.93,
    "min_auprc_min": 0.45,
    "min_ground_truth_event_recall_min": 0.7,
    "min_key_flow_coverage_min": 0.99,
    "max_ece_max": 0.05,
    "max_budget_overrun_count_max": 0,
    "max_budget_us": 5000,
}


def _hard_constraint_violations(metrics, constraints):
    rules = {
        "min_macro_f1_min": ("macro_f1_min", "min"),
        "min_attack_recall_min": ("attack_recall_min", "min"),
        "min_benign_recall_min": ("benign_recall_min", "min"),
        "min_auprc_min": ("auprc_min", "min"),
        "min_ground_truth_event_recall_min": ("ground_truth_event_recall_min", "min"),
        "min_key_flow_coverage_min": ("key_flow_coverage_min", "min"),
        "max_ece_max": ("ece_max", "max"),
        "max_budget_overrun_count_max": ("budget_overrun_count_max", "max"),
        "max_budget_us": ("budget_us_max", "max"),
    }
    if set(constraints) != set(rules):
        raise ValueError("hard constraint set is not exact")
    return [
        name
        for name, (metric, direction) in rules.items()
        if (direction == "min" and metrics[metric] < constraints[name])
        or (direction == "max" and metrics[metric] > constraints[name])
    ]


def _decision_policy(payload):
    protocol = payload.get("protocol") or {}
    required = (
        "feature_profile",
        "classifier",
        "threshold_policy",
        "calibration_attack_recall_floor",
        "calibration_groups",
        "evaluation_groups",
    )
    missing = [name for name in required if name not in protocol]
    if missing:
        return None, missing
    return {
        "feature_profile": protocol["feature_profile"],
        "classifier": protocol["classifier"],
        "threshold_policy": protocol["threshold_policy"],
        "calibration_attack_recall_floor": float(
            protocol["calibration_attack_recall_floor"]
        ),
        "calibration_groups": list(protocol["calibration_groups"]),
        "evaluation_groups": list(protocol["evaluation_groups"]),
        "adaptation_policy": protocol.get("adaptation_policy", "none"),
        "adaptation_groups": list(protocol.get("adaptation_groups", [])),
        "adaptation_weight_multiplier": float(
            protocol.get("adaptation_weight_multiplier", 1.0)
        ),
    }, []


def summarize(
    named_runs,
    minimum_repeats=3,
    max_budget_overrun_count=0,
    min_key_flow_coverage=0.99,
    min_event_recall=0.0,
    hard_constraints=None,
):
    if hard_constraints is None:
        hard_constraints = dict(DEFAULT_HARD_CONSTRAINTS)
        hard_constraints["max_budget_overrun_count_max"] = max_budget_overrun_count
        hard_constraints["min_key_flow_coverage_min"] = min_key_flow_coverage
        hard_constraints["min_ground_truth_event_recall_min"] = min_event_recall
    else:
        hard_constraints = dict(hard_constraints)
    grouped = defaultdict(list)
    rejected = []
    for name, payload in named_runs:
        match = RESULT_NAME.match(name)
        if match is None:
            rejected.append(name)
            continue
        mode, repeat = match.groups()
        grouped[mode].append((int(repeat), payload))
    candidates = []
    for mode, runs in sorted(grouped.items()):
        runs.sort(key=lambda item: item[0])
        payloads = [item[1] for item in runs]
        safety_ratios = {
            float(
                payload["candidate"].get(
                    "execution_budget_safety_ratio", 0.75
                )
            )
            for payload in payloads
        }
        audits = [
            payload["{}_constraint_audit".format(role)]
            for payload in payloads
            for role, count in payload["capture_counts"].items()
            if count > 0
        ]
        overrun_max = max(
            int(audit["budget_overrun_count"]) for audit in audits
        )
        coverage_min = min(
            float(audit["key_flow_coverage_min"]) for audit in audits
        )
        event_recall_min = min(
            float(payload["ground_truth_event_recall_audit"]["event_recall"])
            for payload in payloads
        )
        metrics = [payload["quality"]["conservative"] for payload in payloads]
        gate_metrics = {
            "macro_f1_min": min(item["macro_f1_min"] for item in metrics),
            "attack_recall_min": min(item["attack_recall_min"] for item in metrics),
            "benign_recall_min": min(item["benign_recall_min"] for item in metrics),
            "auprc_min": min(item["auprc_min"] for item in metrics),
            "ece_max": max(item["ece_max"] for item in metrics),
            "ground_truth_event_recall_min": event_recall_min,
            "key_flow_coverage_min": coverage_min,
            "budget_overrun_count_max": overrun_max,
            "budget_us_max": payloads[0]["candidate"]["budget_us"],
        }
        violations = _hard_constraint_violations(gate_metrics, hard_constraints)
        hash_ids = {
            payload.get("input_hash_evidence", {}).get("sha256")
            for payload in payloads
            if payload.get("input_hash_evidence")
        }
        if len(hash_ids) != 1:
            violations.append("inconsistent_or_missing_input_hash_manifest")
        if len(safety_ratios) != 1:
            violations.append("inconsistent_execution_budget_safety_ratio")
        policies = []
        missing_policy_fields = set()
        for payload in payloads:
            policy, missing = _decision_policy(payload)
            missing_policy_fields.update(missing)
            if policy is not None:
                policies.append(policy)
        policy_ids = {
            json.dumps(policy, sort_keys=True, separators=(",", ":"))
            for policy in policies
        }
        if missing_policy_fields:
            violations.extend(
                "missing_decision_policy.{}".format(name)
                for name in sorted(missing_policy_fields)
            )
        if len(policies) != len(payloads) or len(policy_ids) != 1:
            violations.append("inconsistent_or_missing_decision_policy")
        decision_policy = (
            policies[0]
            if len(policies) == len(payloads) and len(policy_ids) == 1
            else None
        )
        candidate = {
            "mode": mode,
            "repeat_ids": [item[0] for item in runs],
            "repeat_count": len(runs),
            "repeat_gate_passed": len(runs) >= minimum_repeats,
            "batch_size": payloads[0]["candidate"]["batch_size"],
            "budget_us": payloads[0]["candidate"]["budget_us"],
            "execution_budget_safety_ratio": (
                next(iter(safety_ratios))
                if len(safety_ratios) == 1
                else None
            ),
            "budget_overrun_count_max": overrun_max,
            "key_flow_coverage_min": coverage_min,
            "ground_truth_event_recall_min": event_recall_min,
            "input_hash_manifest_sha256": (
                next(iter(hash_ids)) if len(hash_ids) == 1 else None
            ),
            "decision_policy": decision_policy,
            "hard_constraint_violations": violations,
            "hard_constraints_passed": not violations,
            "train_flow_count_min": min(
                payload["quality"]["train_flow_count"]
                for payload in payloads
            ),
            "test_flow_count_min": min(
                payload["quality"]["test_flow_count"]
                for payload in payloads
            ),
            "macro_f1_min": min(item["macro_f1_min"] for item in metrics),
            "balanced_accuracy_min": min(
                item["balanced_accuracy_min"] for item in metrics
            ),
            "auroc_min": min(item["auroc_min"] for item in metrics),
            "auprc_min": min(item["auprc_min"] for item in metrics),
            "benign_recall_min": min(
                item["benign_recall_min"] for item in metrics
            ),
            "attack_recall_min": min(
                item["attack_recall_min"] for item in metrics
            ),
            "ece_max": max(item["ece_max"] for item in metrics),
            "final_quality_eligible": False,
            "missing_final_evidence": sorted(
                {
                    evidence
                    for payload in payloads
                    for evidence in payload.get("missing_final_evidence", [])
                }
            ),
        }
        candidates.append(candidate)
    return {
        "schema_version": 2,
        "scope": "independent_cross_dataset_holdout_summary",
        "aggregation_policy": "worst_case_across_full_extraction_repeats",
        "minimum_repeats": minimum_repeats,
        "candidate_count": len(candidates),
        "feasible_candidate_count": sum(
            candidate["repeat_gate_passed"]
            and candidate["hard_constraints_passed"]
            for candidate in candidates
        ),
        "rejected_files": sorted(rejected),
        "candidates": candidates,
        "final_quality_eligible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    parser.add_argument("--max-budget-overrun-count", type=int, default=0)
    parser.add_argument("--min-key-flow-coverage", type=float, default=0.99)
    parser.add_argument("--min-event-recall", type=float, default=0.0)
    parser.add_argument("--algorithm-search", type=Path, required=True)
    args = parser.parse_args()
    named_runs = []
    for path in sorted(args.result_dir.glob("*.json")):
        if path.name == "summary.json":
            continue
        with path.open("r", encoding="utf-8") as handle:
            named_runs.append((path.name, json.load(handle)))
    summary = summarize(
        named_runs,
        minimum_repeats=args.minimum_repeats,
        max_budget_overrun_count=args.max_budget_overrun_count,
        min_key_flow_coverage=args.min_key_flow_coverage,
        min_event_recall=args.min_event_recall,
        hard_constraints=json.loads(
            args.algorithm_search.read_text("utf-8")
        )["hard_constraints"],
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["candidate_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

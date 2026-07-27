"""Build a deployment-level Pareto front across UNSW decision policies."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


OBJECTIVES = (
    ("macro_f1_min", "max"),
    ("attack_recall_min", "max"),
    ("benign_recall_min", "max"),
    ("auprc_min", "max"),
    ("ece_max", "min"),
)


def _minimum(items, field):
    return min(float(item[field]) for item in items)


def _maximum(items, field):
    return max(float(item[field]) for item in items)


def _policy_id(policy):
    return json.dumps(policy, sort_keys=True, separators=(",", ":"))


def _policy_name(policy):
    name = "{}__{}__{}__recall{:03d}".format(
        policy["feature_profile"],
        policy["classifier"],
        policy["threshold_policy"],
        round(float(policy["calibration_attack_recall_floor"]) * 100),
    )
    if policy.get("adaptation_policy", "none") != "none":
        name += "__{}__weight{:03d}".format(
            policy["adaptation_policy"],
            round(float(policy["adaptation_weight_multiplier"]) * 100),
        )
    return name


def dominates(left, right):
    no_worse = True
    strictly_better = False
    for metric, direction in OBJECTIVES:
        left_value = left[metric]
        right_value = right[metric]
        if direction == "max":
            no_worse = no_worse and left_value >= right_value
            strictly_better = strictly_better or left_value > right_value
        else:
            no_worse = no_worse and left_value <= right_value
            strictly_better = strictly_better or left_value < right_value
    return no_worse and strictly_better


def materially_dominates(left, right, epsilon):
    no_material_regression = True
    materially_better = False
    for metric, direction in OBJECTIVES:
        left_value = left[metric]
        right_value = right[metric]
        if direction == "max":
            no_material_regression = (
                no_material_regression
                and left_value >= right_value - epsilon
            )
            materially_better = (
                materially_better
                or left_value > right_value + epsilon
            )
        else:
            no_material_regression = (
                no_material_regression
                and left_value <= right_value + epsilon
            )
            materially_better = (
                materially_better
                or left_value < right_value - epsilon
            )
    return no_material_regression and materially_better


def compare(named_summaries, minimum_material_improvement=0.0):
    if minimum_material_improvement < 0:
        raise ValueError("minimum material improvement must be non-negative")
    grouped = defaultdict(dict)
    rejected = []
    for source_name, summary in named_summaries:
        for candidate in summary.get("candidates", []):
            policy = candidate.get("decision_policy")
            mode = candidate.get("mode")
            if policy is None or mode not in {"normal", "fallback"}:
                rejected.append(
                    {
                        "source": source_name,
                        "mode": mode,
                        "reason": "missing_policy_or_invalid_mode",
                    }
                )
                continue
            key = (
                int(candidate["batch_size"]),
                float(candidate["budget_us"]),
                float(candidate["execution_budget_safety_ratio"]),
                _policy_id(policy),
            )
            if mode in grouped[key]:
                rejected.append(
                    {
                        "source": source_name,
                        "mode": mode,
                        "reason": "duplicate_policy_mode",
                    }
                )
                continue
            grouped[key][mode] = (source_name, candidate)

    configurations = []
    for (batch_size, budget_us, safety_ratio, _), modes in sorted(
        grouped.items()
    ):
        missing_modes = sorted({"normal", "fallback"} - set(modes))
        present = [modes[mode][1] for mode in sorted(modes)]
        policy = present[0]["decision_policy"]
        violations = [
            "mode_evidence.{}.missing".format(mode) for mode in missing_modes
        ]
        for candidate in present:
            if not candidate.get("repeat_gate_passed", False):
                violations.append(
                    "{}.repeat_count".format(candidate["mode"])
                )
            if not candidate.get("hard_constraints_passed", False):
                violations.extend(
                    "{}.{}".format(candidate["mode"], violation)
                    for violation in candidate.get(
                        "hard_constraint_violations", []
                    )
                )
        hash_ids = {
            candidate.get("input_hash_manifest_sha256")
            for candidate in present
        }
        if None in hash_ids or len(hash_ids) != 1:
            violations.append("inconsistent_or_missing_input_hash_manifest")
        item = {
            "name": _policy_name(policy),
            "batch_size": batch_size,
            "budget_us": budget_us,
            "execution_budget_safety_ratio": safety_ratio,
            "decision_policy": policy,
            "source_summaries": sorted(
                {modes[mode][0] for mode in modes}
            ),
            "required_modes": ["normal", "fallback"],
            "macro_f1_min": _minimum(present, "macro_f1_min"),
            "balanced_accuracy_min": _minimum(
                present, "balanced_accuracy_min"
            ),
            "attack_recall_min": _minimum(present, "attack_recall_min"),
            "benign_recall_min": _minimum(present, "benign_recall_min"),
            "auroc_min": _minimum(present, "auroc_min"),
            "auprc_min": _minimum(present, "auprc_min"),
            "ece_max": _maximum(present, "ece_max"),
            "ground_truth_event_recall_min": _minimum(
                present, "ground_truth_event_recall_min"
            ),
            "budget_overrun_count_max": max(
                int(candidate["budget_overrun_count_max"])
                for candidate in present
            ),
            "key_flow_coverage_min": _minimum(
                present, "key_flow_coverage_min"
            ),
            "input_hash_manifest_sha256": (
                next(iter(hash_ids)) if len(hash_ids) == 1 else None
            ),
            "gate_violations": sorted(set(violations)),
        }
        item["deployable_pair_gate_passed"] = not item["gate_violations"]
        item["final_pareto_eligible"] = False
        configurations.append(item)

    feasible = [
        item
        for item in configurations
        if item["deployable_pair_gate_passed"]
    ]
    front = [
        item["name"]
        for item in feasible
        if not any(
            dominates(other, item)
            for other in feasible
            if other is not item
        )
    ]
    practical_front = [
        item["name"]
        for item in feasible
        if not any(
            materially_dominates(
                other, item, minimum_material_improvement
            )
            for other in feasible
            if other is not item
        )
    ]
    return {
        "schema_version": 1,
        "scope": "cross_policy_offline_quality_preselection",
        "candidate_semantics": (
            "Each candidate pairs normal and fallback evidence for one "
            "immutable decision policy."
        ),
        "hard_constraints_applied_before_pareto": True,
        "pareto_objectives": [
            {"metric": metric, "direction": direction}
            for metric, direction in OBJECTIVES
        ],
        "candidate_count": len(configurations),
        "feasible_candidate_count": len(feasible),
        "offline_quality_front": sorted(front),
        "minimum_material_improvement": minimum_material_improvement,
        "offline_practical_front": sorted(practical_front),
        "final_pareto_eligible": False,
        "missing_final_evidence": [
            "frozen_business_quality_thresholds",
            "throughput_live_replay",
            "nic_packet_drop",
            "end_to_end_p99",
            "end_to_end_p999",
        ],
        "rejected_inputs": rejected,
        "candidates": configurations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summaries", type=Path, nargs="+")
    parser.add_argument(
        "--min-material-improvement", type=float, default=0.0
    )
    args = parser.parse_args()
    named = []
    for path in args.summaries:
        with path.open("r", encoding="utf-8") as handle:
            named.append((str(path), json.load(handle)))
    output = compare(
        named,
        minimum_material_improvement=args.min_material_improvement,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["candidate_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

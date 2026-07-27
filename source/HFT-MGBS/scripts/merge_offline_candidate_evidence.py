"""Join hard-gated performance and grouped quality before offline Pareto ranking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.experiment import summarize_offline_runs
from hft_mgbs.quality import summarize_quality_runs
from scripts.summarize_unsw_holdout import summarize as summarize_unsw_holdout


def _minimum(values):
    present = [value for value in values if value is not None]
    return None if not present else min(present)


def _maximum(values):
    present = [value for value in values if value is not None]
    return None if not present else max(present)


def load_named(directory):
    loaded = []
    for path in sorted(directory.glob("*.json")):
        if "summary" in path.stem:
            continue
        with path.open("r", encoding="utf-8") as handle:
            loaded.append((path.name, json.load(handle)))
    return loaded


def summarize_recovery_runs(
    named_runs,
    minimum_repeats=3,
    max_budget_overrun_count=0,
    min_key_flow_coverage=0.99,
    max_fallback_recovery_s=None,
):
    """Aggregate same-pipeline fault-injection evidence by configuration."""

    grouped = {}
    rejected_files = []
    for name, payload in named_runs:
        if not name.startswith("repeat") or not name.endswith(".json"):
            rejected_files.append(name)
            continue
        candidate = payload.get("candidate") or {}
        key = (
            int(candidate.get("batch_size", -1)),
            int(candidate.get("budget_us", -1)),
            float(candidate.get("execution_budget_safety_ratio", -1)),
        )
        grouped.setdefault(key, []).append(payload)

    candidates = []
    for (batch_size, budget_us, safety_ratio), runs in sorted(
        grouped.items()
    ):
        scopes = [run.get("evidence_scope") or {} for run in runs]
        observations = [
            run.get("hard_constraint_observations") or {} for run in runs
        ]
        item = {
            "batch_size": batch_size,
            "budget_us": budget_us,
            "execution_budget_safety_ratio": safety_ratio,
            "repeat_count": len(runs),
            "repeat_gate_passed": len(runs) >= minimum_repeats,
            "fallback_recovery_s_max": _maximum(
                run.get("fallback_recovery_s") for run in runs
            ),
            "budget_overrun_count_max": _maximum(
                observation.get("budget_overrun_count")
                for observation in observations
            ),
            "key_flow_coverage_min": _minimum(
                observation.get("minimum_key_flow_coverage")
                for observation in observations
            ),
            "status_complete": all(
                run.get("status") == "complete" for run in runs
            ),
            "evidence_verified": {
                name: all(bool(scope.get(name, False)) for scope in scopes)
                for name in (
                    "fallback_activation_verified",
                    "fallback_recovery_verified",
                    "fallback_real_pcap_processing_verified",
                    "same_candidate_pipeline_instance_verified",
                    "application_budget_verified",
                    "key_flow_coverage_verified",
                )
            },
        }
        violations = []
        if batch_size <= 0 or budget_us <= 0 or not 0 < safety_ratio <= 1:
            violations.append("candidate_configuration")
        if not item["repeat_gate_passed"]:
            violations.append("repeat_count")
        if not item["status_complete"]:
            violations.append("status")
        for evidence_name, verified in item["evidence_verified"].items():
            if not verified:
                violations.append("evidence.{}".format(evidence_name))
        if (
            item["budget_overrun_count_max"] is None
            or item["budget_overrun_count_max"] > max_budget_overrun_count
        ):
            violations.append("budget_overrun_count_max")
        if (
            item["key_flow_coverage_min"] is None
            or item["key_flow_coverage_min"] < min_key_flow_coverage
        ):
            violations.append("key_flow_coverage_min")
        if (
            max_fallback_recovery_s is not None
            and (
                item["fallback_recovery_s_max"] is None
                or item["fallback_recovery_s_max"]
                > max_fallback_recovery_s
            )
        ):
            violations.append("fallback_recovery_s_max")
        item["hard_constraint_violations"] = violations
        item["hard_constraints_passed"] = not violations
        candidates.append(item)
    return {
        "candidate_count": len(candidates),
        "rejected_files": sorted(rejected_files),
        "candidates": candidates,
    }


def dominates(left, right):
    objectives = [
        ("throughput_mpps_min", "max"),
        ("p99_latency_us_max", "min"),
        ("resource_pressure_max", "min"),
        ("macro_f1_min", "max"),
        ("ece_max", "min"),
    ]
    if (
        "independent_macro_f1_min" in left
        and "independent_macro_f1_min" in right
    ):
        objectives.extend(
            [
                ("independent_macro_f1_min", "max"),
                ("independent_attack_recall_min", "max"),
            ]
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


def combine_operating_modes(candidates):
    """Pair normal/fallback mode evidence into deployable configurations."""

    grouped = {}
    for candidate in candidates:
        policy_id = json.dumps(
            candidate.get("independent_decision_policy"),
            sort_keys=True,
            separators=(",", ":"),
        )
        key = (
            candidate["batch_size"],
            int(candidate["budget_us"]),
            float(candidate["execution_budget_safety_ratio"]),
            policy_id,
        )
        grouped.setdefault(key, {})[candidate["mode"]] = candidate

    configurations = []
    for (batch_size, budget_us, safety_ratio, _policy_id), modes in sorted(
        grouped.items()
    ):
        violations = []
        missing_modes = sorted({"normal", "fallback"} - set(modes))
        if missing_modes:
            violations.extend(
                "mode_evidence.{}.missing".format(mode)
                for mode in missing_modes
            )
        profiles = [modes[mode] for mode in sorted(modes)]
        decision_policy_ids = {
            json.dumps(
                profile.get("independent_decision_policy"),
                sort_keys=True,
                separators=(",", ":"),
            )
            for profile in profiles
            if profile.get("independent_decision_policy") is not None
        }
        if (
            len(decision_policy_ids) != 1
            or len(decision_policy_ids) != len(
                {
                    json.dumps(
                        profile.get("independent_decision_policy"),
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    for profile in profiles
                }
            )
        ):
            violations.append(
                "mode_evidence.inconsistent_or_missing_decision_policy"
            )
        decision_policy = (
            profiles[0].get("independent_decision_policy")
            if len(decision_policy_ids) == 1
            else None
        )
        policy_suffix = ""
        if decision_policy is not None:
            policy_suffix = "__{}__{}__{}__recall{:03d}".format(
                decision_policy["feature_profile"],
                decision_policy["classifier"],
                decision_policy["threshold_policy"],
                round(
                    float(
                        decision_policy[
                            "calibration_attack_recall_floor"
                        ]
                    )
                    * 100
                ),
            )
            if decision_policy.get("adaptation_policy", "none") != "none":
                policy_suffix += "__{}__weight{:03d}".format(
                    decision_policy["adaptation_policy"],
                    round(
                        float(
                            decision_policy[
                                "adaptation_weight_multiplier"
                            ]
                        )
                        * 100
                    ),
                )
        for profile in profiles:
            violations.extend(
                "{}.{}".format(profile["mode"], violation)
                for violation in profile["joint_gate_violations"]
            )
        item = {
            "name": "batch{}_budget{}_safety{:03d}{}".format(
                batch_size,
                budget_us,
                round(safety_ratio * 100),
                policy_suffix,
            ),
            "batch_size": batch_size,
            "budget_us": budget_us,
            "execution_budget_safety_ratio": safety_ratio,
            "required_modes": ["normal", "fallback"],
            "independent_decision_policy": decision_policy,
            "mode_profiles": sorted(
                profile["name"] for profile in profiles
            ),
            "throughput_mpps_min": _minimum(
                profile["throughput_mpps_min"] for profile in profiles
            ),
            "p99_latency_us_max": _maximum(
                profile["p99_latency_us_max"] for profile in profiles
            ),
            "p999_latency_us_max": _maximum(
                profile["p999_latency_us_max"] for profile in profiles
            ),
            "resource_pressure_max": _maximum(
                profile["resource_pressure_max"] for profile in profiles
            ),
            "macro_f1_min": _minimum(
                profile.get("macro_f1_min") for profile in profiles
            ),
            "ece_max": _maximum(
                profile.get("ece_max") for profile in profiles
            ),
            "independent_macro_f1_min": _minimum(
                profile.get("independent_macro_f1_min")
                for profile in profiles
            ),
            "independent_balanced_accuracy_min": _minimum(
                profile.get("independent_balanced_accuracy_min")
                for profile in profiles
            ),
            "independent_auroc_min": _minimum(
                profile.get("independent_auroc_min")
                for profile in profiles
            ),
            "independent_auprc_min": _minimum(
                profile.get("independent_auprc_min")
                for profile in profiles
            ),
            "independent_ece_max": _maximum(
                profile.get("independent_ece_max")
                for profile in profiles
            ),
            "independent_benign_recall_min": _minimum(
                profile.get("independent_benign_recall_min")
                for profile in profiles
            ),
            "independent_attack_recall_min": _minimum(
                profile.get("independent_attack_recall_min")
                for profile in profiles
            ),
            "ground_truth_event_recall_min": _minimum(
                profile.get("ground_truth_event_recall_min")
                for profile in profiles
            ),
            "budget_overrun_count_max": _maximum(
                profile["budget_overrun_count_max"]
                for profile in profiles
            ),
            "key_flow_coverage_min": _minimum(
                profile["key_flow_coverage_min"] for profile in profiles
            ),
            "fallback_recovery_s_max": _maximum(
                profile.get("recovery_fallback_recovery_s_max")
                for profile in profiles
            ),
            "joint_gate_violations": sorted(set(violations)),
        }
        item["offline_joint_gate_passed"] = not item[
            "joint_gate_violations"
        ]
        configurations.append(item)
    return configurations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("performance_dir", type=Path)
    parser.add_argument("quality_dir", type=Path)
    parser.add_argument("--independent-dir", type=Path)
    parser.add_argument("--recovery-dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    parser.add_argument("--min-macro-f1", type=float)
    parser.add_argument("--min-independent-macro-f1", type=float)
    parser.add_argument("--min-event-recall", type=float)
    parser.add_argument("--max-fallback-recovery-s", type=float)
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
    independent = None
    if args.independent_dir is not None:
        independent = summarize_unsw_holdout(
            load_named(args.independent_dir),
            minimum_repeats=args.minimum_repeats,
        )
    recovery = None
    if args.recovery_dir is not None:
        recovery = summarize_recovery_runs(
            load_named(args.recovery_dir),
            minimum_repeats=args.minimum_repeats,
            max_fallback_recovery_s=args.max_fallback_recovery_s,
        )
    quality_by_key = {
        (
            item["mode"],
            item["batch_size"],
            int(item["budget_us"]),
            float(item.get("execution_budget_safety_ratio", 0.75)),
        ): item
        for item in quality["candidates"]
    }
    independent_by_key = (
        {}
        if independent is None
        else {
            (
                item["mode"],
                item["batch_size"],
                int(item["budget_us"]),
                float(
                    item.get("execution_budget_safety_ratio", 0.75)
                ),
            ): item
            for item in independent["candidates"]
        }
    )
    recovery_by_key = (
        {}
        if recovery is None
        else {
            (
                item["batch_size"],
                int(item["budget_us"]),
                float(item["execution_budget_safety_ratio"]),
            ): item
            for item in recovery["candidates"]
        }
    )
    candidates = []
    for perf in performance["candidates"]:
        key = (
            perf["mode"],
            perf["batch_size"],
            int(perf["budget_us"]),
            float(perf.get("execution_budget_safety_ratio", 0.75)),
        )
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
            if not quality_item["hard_constraints_passed"]:
                candidate["joint_gate_violations"].extend(
                    "quality.{}".format(violation)
                    for violation in quality_item[
                        "hard_constraint_violations"
                    ]
                )
            if (
                args.min_macro_f1 is not None
                and quality_item["macro_f1_min"] < args.min_macro_f1
            ):
                candidate["joint_gate_violations"].append("macro_f1_min")
        if independent is not None:
            independent_item = independent_by_key.get(key)
            if independent_item is None:
                candidate["joint_gate_violations"].append(
                    "independent_evidence.missing"
                )
            else:
                for source, target in (
                    ("macro_f1_min", "independent_macro_f1_min"),
                    (
                        "balanced_accuracy_min",
                        "independent_balanced_accuracy_min",
                    ),
                    ("auroc_min", "independent_auroc_min"),
                    ("auprc_min", "independent_auprc_min"),
                    ("ece_max", "independent_ece_max"),
                    ("benign_recall_min", "independent_benign_recall_min"),
                    ("attack_recall_min", "independent_attack_recall_min"),
                    (
                        "ground_truth_event_recall_min",
                        "ground_truth_event_recall_min",
                    ),
                    (
                        "input_hash_manifest_sha256",
                        "input_hash_manifest_sha256",
                    ),
                    (
                        "decision_policy",
                        "independent_decision_policy",
                    ),
                ):
                    candidate[target] = independent_item[source]
                if not independent_item["repeat_gate_passed"]:
                    candidate["joint_gate_violations"].append(
                        "independent_repeat_count"
                    )
                if not independent_item["hard_constraints_passed"]:
                    candidate["joint_gate_violations"].extend(
                        "independent.{}".format(violation)
                        for violation in independent_item[
                            "hard_constraint_violations"
                        ]
                    )
                if (
                    args.min_independent_macro_f1 is not None
                    and independent_item["macro_f1_min"]
                    < args.min_independent_macro_f1
                ):
                    candidate["joint_gate_violations"].append(
                        "independent_macro_f1_min"
                    )
                if (
                    args.min_event_recall is not None
                    and independent_item["ground_truth_event_recall_min"]
                    < args.min_event_recall
                ):
                    candidate["joint_gate_violations"].append(
                        "ground_truth_event_recall_min"
                    )
        if recovery is not None:
            recovery_key = (key[1], key[2], key[3])
            recovery_item = recovery_by_key.get(recovery_key)
            if recovery_item is None:
                candidate["joint_gate_violations"].append(
                    "fallback_recovery_evidence.missing"
                )
            else:
                for metric in (
                    "fallback_recovery_s_max",
                    "budget_overrun_count_max",
                    "key_flow_coverage_min",
                ):
                    candidate["recovery_{}".format(metric)] = (
                        recovery_item[metric]
                    )
                candidate["recovery_repeat_count"] = recovery_item[
                    "repeat_count"
                ]
                candidate["recovery_evidence_verified"] = recovery_item[
                    "evidence_verified"
                ]
                if not recovery_item["hard_constraints_passed"]:
                    candidate["joint_gate_violations"].extend(
                        "recovery.{}".format(violation)
                        for violation in recovery_item[
                            "hard_constraint_violations"
                        ]
                    )
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
    configurations = combine_operating_modes(candidates)
    eligible_configurations = [
        item
        for item in configurations
        if item["offline_joint_gate_passed"]
    ]
    configuration_front = [
        item["name"]
        for item in eligible_configurations
        if not any(
            dominates(other, item)
            for other in eligible_configurations
            if other is not item
        )
    ]
    missing_final_evidence = [
        "throughput_live_replay",
        "nic_packet_drop",
        "end_to_end_p99",
        "end_to_end_p999",
        "frozen_quality_and_event_recall_thresholds",
    ]
    if recovery is None:
        missing_final_evidence.append(
            "fallback_recovery_in_same_candidate_run"
        )
    if args.max_fallback_recovery_s is None:
        missing_final_evidence.append(
            "frozen_fallback_recovery_threshold"
        )
    for candidate in candidates:
        candidate["missing_final_evidence"] = list(
            missing_final_evidence
        )
    for configuration in configurations:
        configuration["missing_final_evidence"] = list(
            missing_final_evidence
        )
        configuration["final_pareto_eligible"] = False
    output = {
        "schema_version": 2,
        "scope": "offline_joint_preselection_only",
        "candidate_semantics": (
            "Pareto candidates are deployable configurations pairing "
            "normal and fallback operating-mode evidence"
        ),
        "hard_constraints_applied_before_pareto": True,
        "quality_threshold_frozen": args.min_macro_f1 is not None,
        "independent_quality_threshold_frozen": (
            args.min_independent_macro_f1 is not None
        ),
        "event_recall_threshold_frozen": args.min_event_recall is not None,
        "independent_holdout_included": independent is not None,
        "fallback_recovery_included": recovery is not None,
        "fallback_recovery_threshold_frozen": (
            args.max_fallback_recovery_s is not None
        ),
        "eligible_mode_profile_count": len(eligible),
        "eligible_candidate_count": len(eligible_configurations),
        "mode_profile_front": sorted(front),
        "offline_joint_front": sorted(configuration_front),
        "final_pareto_eligible": False,
        "missing_final_evidence": missing_final_evidence,
        "candidates": configurations,
        "mode_profiles": candidates,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if candidates else 2


if __name__ == "__main__":
    raise SystemExit(main())

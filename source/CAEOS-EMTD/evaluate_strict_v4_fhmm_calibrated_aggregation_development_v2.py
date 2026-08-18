from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import evaluate_strict_v4_fhmm_calibrated_aggregation_development as v1
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


def threshold_unknown_f1(repeat: dict[str, Any]) -> float:
    recall = float(repeat["operational"]["unknown_attack_recall"])
    precision = float(repeat["operational"]["unknown_label_precision"])
    return (
        2.0 * recall * precision / (recall + precision)
        if recall + precision
        else 0.0
    )


def augmented_worst_case(result: dict[str, Any]) -> dict[str, float]:
    values = dict(result["worst_case"])
    repeats = list(result["per_repeat"].values())
    values.update(
        {
            "unknown_attack_recall": min(
                float(value["operational"]["unknown_attack_recall"])
                for value in repeats
            ),
            "unknown_label_precision": min(
                float(value["operational"]["unknown_label_precision"])
                for value in repeats
            ),
            "unknown_f1_at_frozen_threshold": min(
                threshold_unknown_f1(value) for value in repeats
            ),
        }
    )
    return values


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    gates = result["gates"]
    worst = augmented_worst_case(result)
    typed_margin = min(
        worst["alert_accuracy"] - v1.TARGET,
        0.05 - worst["benign_fpr"],
        worst["known_attack_type_accuracy"] - v1.TARGET,
        worst["unknown_attack_alert_recall"] - v1.TARGET,
    )
    user_margin = min(
        worst["alert_accuracy"] - v1.TARGET,
        0.05 - worst["benign_fpr"],
    )
    known_type_floor_pass = (
        worst["known_attack_type_accuracy"] >= v1.TARGET
    )
    return (
        gates["all_repeats_typed_known_unknown_95_5"],
        gates["all_repeats_user_warning_95_5"],
        gates["all_repeats_legacy_botnet_expansion"],
        known_type_floor_pass,
        gates["repeat_pass_count_typed_known_unknown_95_5"],
        gates["repeat_pass_count_user_warning_95_5"],
        gates["repeat_pass_count_legacy_botnet_expansion"],
        typed_margin,
        user_margin,
        worst["unknown_attack_alert_recall"],
        worst["unknown_attack_recall"],
        worst["unknown_f1_at_frozen_threshold"],
        worst["oscr_exact_v2"],
        worst["unknown_auroc"],
        worst["known_attack_type_accuracy"],
        -worst["benign_fpr"],
    )


def summarize_candidate(result: dict[str, Any]) -> dict[str, Any]:
    value = v1.summarize_candidate(result)
    value["worst_case"] = augmented_worst_case(result)
    return value


def evaluate(
    repeats: list[tuple[int, list[Path]]],
) -> dict[str, Any]:
    if len(repeats) < 2:
        raise ValueError("at least two split repeats are required")
    prepared = {
        str(split_seed): v1.prepare_repeat(split_seed, member_dirs)
        for split_seed, member_dirs in repeats
    }
    if len(prepared) != len(repeats):
        raise ValueError("split repeat identifiers must be unique")
    dataset_sha256 = str(
        v1._same(
            "dataset_sha256",
            [value["dataset_sha256"] for value in prepared.values()],
        )
    )
    unknown_family = str(
        v1._same(
            "unknown_family",
            [value["unknown_family"] for value in prepared.values()],
        )
    )
    results = [
        v1.evaluate_configuration(prepared, configuration)
        for configuration in v1.configurations()
    ]
    ranked = sorted(results, key=selection_key, reverse=True)
    selected = ranked[0]
    selected["worst_case"] = augmented_worst_case(selected)
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fhmm_calibrated_aggregation_development_v2"
        ),
        "state": (
            "development_candidate_found"
            if selected["gates"]["all_repeats_user_warning_95_5"]
            else "development_no_dual_repeat_95_5_candidate"
        ),
        "unknown_family": unknown_family,
        "dataset_sha256": dataset_sha256,
        "repeat_count": len(prepared),
        "candidate_count": len(results),
        "selected": selected,
        "top_candidates": [
            summarize_candidate(candidate) for candidate in ranked[:20]
        ],
        "gate_pass_counts": {
            gate: sum(result["gates"][gate] for result in results)
            for gate in (
                "all_repeats_user_warning_95_5",
                "all_repeats_typed_known_unknown_95_5",
                "all_repeats_legacy_botnet_expansion",
            )
        },
        "repeat_sources": {
            identity: {
                "split_seed": value["split_seed"],
                "model_seeds": value["model_seeds"],
                "type_selection": value["type_selection"],
                "members": value["source"],
            }
            for identity, value in prepared.items()
        },
        "search_space": {
            "attack_sources": list(v1.ATTACK_SOURCES),
            "aggregations": list(v1.AGGREGATIONS),
            "alert_budgets": list(v1.ALERT_BUDGETS),
            "open_budgets": list(v1.OPEN_BUDGETS),
            "type_rules": list(v1.TYPE_RULES),
            "candidate_count": len(v1.configurations()),
        },
        "selection_rule": {
            "hard_order": [
                "all_repeats_typed_known_unknown_95_5",
                "all_repeats_user_warning_95_5",
                "all_repeats_legacy_botnet_expansion",
                "worst_known_type_at_least_95",
            ],
            "soft_order_after_hard_gates": [
                "typed_minimum_margin",
                "user_95_5_minimum_margin",
                "worst_unknown_alert_recall",
                "worst_unknown_rejection_recall",
                "worst_unknown_f1",
                "worst_oscr",
                "worst_unknown_auroc",
                "worst_known_type_accuracy",
                "lower_worst_benign_fpr",
            ],
        },
        "implementation": {
            "v1_evaluator_sha256": file_hash(Path(v1.__file__).resolve()),
            "v2_selector_sha256": file_hash(Path(__file__).resolve()),
        },
        "claim_boundary": {
            "development_only": True,
            "true_unknown_test_used_for_candidate_ranking": True,
            "v1_development_result_read_before_v2_selection_rule": True,
            "selection_rule_revision_is_posthoc_and_disclosed": True,
            "selected_configuration_is_not_confirmation": True,
            "fresh_split_confirmation_required": True,
            "member_models_and_scores_are_read_only": True,
            "no_member_retraining_performed": True,
            "all_score_scale_alignment_uses_known_validation_only": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repeat",
        action="append",
        nargs=4,
        metavar=("SPLIT_SEED", "MEMBER1", "MEMBER2", "MEMBER3"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    repeats = [
        (int(values[0]), [Path(value) for value in values[1:]])
        for values in args.repeat
    ]
    report = evaluate(repeats)
    atomic_json(args.output.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()


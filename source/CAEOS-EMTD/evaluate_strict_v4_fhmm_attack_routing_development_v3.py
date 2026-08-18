from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import evaluate_strict_v4_fhmm_calibrated_aggregation_development as base
from strict_v4_cicids2017_attack_family import (
    ATTACK_FAMILIES,
    atomic_json,
    canonical_hash,
    file_hash,
)


DEVELOPMENT_UNKNOWN_FAMILY = "Botnet"
ATTACK_SOURCES = ("attack_head", "family", "maximum", "noisy_or")
ATTACK_AGGREGATIONS = ("mean", "median", "maximum")
ALERT_BUDGETS = (0.04, 0.045, 0.049)
FIXED_OPEN_AGGREGATION = "maximum"
FIXED_OPEN_BUDGET = 0.04
FIXED_TYPE_RULE = "validation_best_macro_f1_member"


def configurations() -> list[dict[str, Any]]:
    return [
        {
            "attack_source": source,
            "attack_aggregation": aggregation,
            "alert_budget": budget,
            "open_aggregation": FIXED_OPEN_AGGREGATION,
            "open_budget": FIXED_OPEN_BUDGET,
            "type_rule": FIXED_TYPE_RULE,
        }
        for source, aggregation, budget in product(
            ATTACK_SOURCES,
            ATTACK_AGGREGATIONS,
            ALERT_BUDGETS,
        )
    ]


def development_gates(result: dict[str, Any]) -> dict[str, bool]:
    repeats = list(result["per_repeat"].values())
    return {
        "all_repeats_user_warning_95_5": all(
            value["gates"]["user_warning_95_5"] for value in repeats
        ),
        "all_repeats_known_unknown_alert_95_5": all(
            value["gates"]["typed_known_unknown_95_5"]
            for value in repeats
        ),
        "all_repeats_research_floor": all(
            value["research_main"]["unknown_auroc"] >= 0.88
            and value["research_main"]["oscr_exact_v2"] >= 0.87
            for value in repeats
        ),
    }


def worst_case(result: dict[str, Any]) -> dict[str, float]:
    repeats = list(result["per_repeat"].values())
    return {
        "alert_accuracy": min(
            value["operational"]["alert_accuracy"] for value in repeats
        ),
        "benign_fpr": max(
            value["operational"]["benign_fpr"] for value in repeats
        ),
        "known_attack_type_accuracy": min(
            value["operational"]["known_attack_type_accuracy"]
            for value in repeats
        ),
        "unknown_attack_alert_recall": min(
            value["operational"]["unknown_attack_alert_recall"]
            for value in repeats
        ),
        "unknown_attack_recall": min(
            value["operational"]["unknown_attack_recall"]
            for value in repeats
        ),
        "unknown_auroc": min(
            value["research_main"]["unknown_auroc"]
            for value in repeats
        ),
        "oscr_exact_v2": min(
            value["research_main"]["oscr_exact_v2"]
            for value in repeats
        ),
    }


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    gates = development_gates(result)
    worst = worst_case(result)
    full_margin = min(
        worst["alert_accuracy"] - 0.95,
        0.05 - worst["benign_fpr"],
        worst["known_attack_type_accuracy"] - 0.95,
        worst["unknown_attack_alert_recall"] - 0.95,
    )
    return (
        gates["all_repeats_known_unknown_alert_95_5"],
        gates["all_repeats_user_warning_95_5"],
        gates["all_repeats_research_floor"],
        full_margin,
        worst["unknown_attack_alert_recall"],
        worst["alert_accuracy"],
        worst["known_attack_type_accuracy"],
        worst["unknown_attack_recall"],
        worst["oscr_exact_v2"],
        worst["unknown_auroc"],
        -worst["benign_fpr"],
    )


def compact(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "configuration": result["configuration"],
        "gates": development_gates(result),
        "worst_case": worst_case(result),
        "macro_mean": result["macro_mean"],
    }


def evaluate(
    repeats: list[tuple[int, list[Path]]],
) -> dict[str, Any]:
    if len(repeats) != 2:
        raise ValueError("attack-routing development requires two splits")
    prepared = {
        str(split_seed): base.prepare_repeat(split_seed, member_dirs)
        for split_seed, member_dirs in repeats
    }
    if len(prepared) != len(repeats):
        raise ValueError("split identifiers must be unique")
    unknown_families = {
        str(value["unknown_family"]) for value in prepared.values()
    }
    if unknown_families != {DEVELOPMENT_UNKNOWN_FAMILY}:
        raise ValueError("Botnet must be the only development unknown family")
    dataset_hashes = {
        str(value["dataset_sha256"]) for value in prepared.values()
    }
    if len(dataset_hashes) != 1:
        raise ValueError("development dataset identity drifted")
    candidates = [
        base.evaluate_configuration(prepared, configuration)
        for configuration in configurations()
    ]
    ranked = sorted(candidates, key=selection_key, reverse=True)
    selected = ranked[0]
    selected_gates = development_gates(selected)
    qualifies = (
        selected_gates["all_repeats_known_unknown_alert_95_5"]
        and selected_gates["all_repeats_research_floor"]
    )
    report: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_attack_routing_development_v3",
        "state": (
            "development_candidate_qualifies_for_disjoint_families"
            if qualifies
            else "development_candidate_does_not_qualify"
        ),
        "development_unknown_family": DEVELOPMENT_UNKNOWN_FAMILY,
        "eligible_confirmation_unknown_families": [
            family
            for family in ATTACK_FAMILIES
            if family != DEVELOPMENT_UNKNOWN_FAMILY
        ],
        "dataset_sha256": next(iter(dataset_hashes)),
        "candidate_count": len(candidates),
        "selection_policy": {
            "primary": "dual_split_known_unknown_alert_95_5",
            "secondary": "worst_case_margin_and_unknown_alert_recall",
            "open_aggregation_fixed": FIXED_OPEN_AGGREGATION,
            "open_budget_fixed": FIXED_OPEN_BUDGET,
            "type_rule_fixed": FIXED_TYPE_RULE,
        },
        "selected": compact(selected),
        "top_candidates": [compact(candidate) for candidate in ranked[:20]],
        "gate_pass_counts": {
            gate: sum(development_gates(candidate)[gate] for candidate in candidates)
            for gate in (
                "all_repeats_user_warning_95_5",
                "all_repeats_known_unknown_alert_95_5",
                "all_repeats_research_floor",
            )
        },
        "repeat_sources": {
            identity: {
                "split_seed": value["split_seed"],
                "model_seeds": value["model_seeds"],
                "members": value["source"],
            }
            for identity, value in prepared.items()
        },
        "claim_boundary": {
            "development_only": True,
            "botnet_unknown_labels_used_for_routing_selection": True,
            "botnet_excluded_from_future_confirmation_claim": True,
            "split43_and_split47_must_not_be_reused_for_confirmation": True,
            "final_thresholds_remain_known_only_validation": True,
            "eligible_confirmation_unknown_families_are_disjoint": True,
            "no_member_training_or_score_mutation": True,
        },
    }
    report["source_sha256"] = {
        Path(__file__).name: file_hash(Path(__file__).resolve()),
        Path(base.__file__).name: file_hash(Path(base.__file__).resolve()),
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

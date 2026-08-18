from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

import evaluate_strict_v4_fhmm_calibrated_aggregation_development as base
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    operational_metrics,
    upper_tail_threshold,
)
from strict_v4_cicids2017_attack_family import (
    ATTACK_FAMILIES,
    atomic_json,
    canonical_hash,
    file_hash,
)
from strict_v4_open_set_metric_contract_v2 import (
    evaluate_open_set_metric_contract,
)


DEVELOPMENT_UNKNOWN_FAMILY = "Botnet"
FIXED_ATTACK_SOURCE = "family"
FIXED_ATTACK_AGGREGATION = "mean"
FIXED_OPEN_BUDGET = 0.04
FIXED_TYPE_RULE = "validation_best_macro_f1_member"
JOINT_RULES = ("attack_only", "maximum", "noisy_or")
OPEN_AGGREGATIONS = ("mean", "median", "maximum")
ALERT_BUDGETS = (0.04, 0.045, 0.049)


def combine_alert(
    attack_score: np.ndarray,
    open_score: np.ndarray,
    rule: str,
) -> np.ndarray:
    attack_score = np.asarray(attack_score, dtype=np.float64)
    open_score = np.asarray(open_score, dtype=np.float64)
    if attack_score.shape != open_score.shape:
        raise ValueError("attack and open scores must align")
    if rule == "attack_only":
        return attack_score
    if rule == "maximum":
        return np.maximum(attack_score, open_score)
    if rule == "noisy_or":
        return 1.0 - (1.0 - attack_score) * (1.0 - open_score)
    raise ValueError(f"unsupported joint alert rule: {rule}")


def configurations() -> list[dict[str, Any]]:
    return [
        {
            "attack_source": FIXED_ATTACK_SOURCE,
            "attack_aggregation": FIXED_ATTACK_AGGREGATION,
            "joint_alert_rule": rule,
            "alert_budget": budget,
            "open_aggregation": open_aggregation,
            "open_budget": FIXED_OPEN_BUDGET,
            "type_rule": FIXED_TYPE_RULE,
        }
        for rule, open_aggregation, budget in product(
            JOINT_RULES,
            OPEN_AGGREGATIONS,
            ALERT_BUDGETS,
        )
    ]


def evaluate_repeat(
    prepared: dict[str, Any],
    configuration: dict[str, Any],
) -> dict[str, Any]:
    validation_attack, test_attack = prepared["attack_scores"][
        configuration["attack_source"]
    ][configuration["attack_aggregation"]]
    validation_open, test_open = prepared["open_scores"][
        configuration["open_aggregation"]
    ]
    validation_alert = combine_alert(
        validation_attack,
        validation_open,
        configuration["joint_alert_rule"],
    )
    test_alert = combine_alert(
        test_attack,
        test_open,
        configuration["joint_alert_rule"],
    )
    validation_labels = prepared["validation_labels"]
    benign_index = int(prepared["benign_index"])
    calibration = calibrate_threshold(
        validation_alert,
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        float(configuration["alert_budget"]),
    )
    if not calibration["feasible"]:
        raise ValueError("joint alert calibration is infeasible")
    open_threshold = upper_tail_threshold(
        validation_open[validation_labels != benign_index],
        float(configuration["open_budget"]),
    )
    predicted_alert = test_alert >= float(calibration["threshold"])
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    type_prediction = prepared["type_predictions"][
        configuration["type_rule"]
    ]
    operational = operational_metrics(
        predicted_alert=predicted_alert,
        predicted_unknown=predicted_unknown,
        type_prediction=type_prediction,
        test_labels=prepared["test_labels"],
        test_unknown=prepared["test_unknown"],
        benign_index=benign_index,
    )
    research = evaluate_open_set_metric_contract(
        labels=prepared["test_labels"],
        known_prediction=type_prediction,
        is_unknown=prepared["test_unknown"],
        unknown_risk=test_open,
        rejected_as_unknown=predicted_unknown,
        class_names=[
            str(value) for value in prepared["known_class_names"].tolist()
        ],
    )
    gates = {
        "user_warning_95_5": (
            operational["alert_accuracy"] >= 0.95
            and operational["benign_fpr"] < 0.05
        ),
        "known_unknown_alert_95_5": (
            operational["alert_accuracy"] >= 0.95
            and operational["benign_fpr"] < 0.05
            and operational["known_attack_type_accuracy"] >= 0.95
            and operational["unknown_attack_alert_recall"] >= 0.95
        ),
        "research_floor": (
            base.compact_research(research)["unknown_auroc"] >= 0.88
            and base.compact_research(research)["oscr_exact_v2"] >= 0.87
        ),
    }
    return {
        "operational": operational,
        "research_main": base.compact_research(research),
        "gates": gates,
        "thresholds": {
            "alert": float(calibration["threshold"]),
            "open": float(open_threshold),
        },
        "validation_alert_calibration": calibration,
    }


def evaluate_configuration(
    prepared: dict[str, dict[str, Any]],
    configuration: dict[str, Any],
) -> dict[str, Any]:
    per_repeat = {
        identity: evaluate_repeat(values, configuration)
        for identity, values in prepared.items()
    }
    operational_names = tuple(
        next(iter(per_repeat.values()))["operational"]
    )
    research_names = tuple(
        next(iter(per_repeat.values()))["research_main"]
    )
    return {
        "configuration": configuration,
        "per_repeat": per_repeat,
        "macro_mean": {
            "operational": {
                name: float(
                    np.mean(
                        [
                            value["operational"][name]
                            for value in per_repeat.values()
                        ]
                    )
                )
                for name in operational_names
            },
            "research_main": {
                name: float(
                    np.mean(
                        [
                            value["research_main"][name]
                            for value in per_repeat.values()
                        ]
                    )
                )
                for name in research_names
            },
        },
    }


def gates(result: dict[str, Any]) -> dict[str, bool]:
    names = tuple(next(iter(result["per_repeat"].values()))["gates"])
    return {
        f"all_repeats_{name}": all(
            value["gates"][name] for value in result["per_repeat"].values()
        )
        for name in names
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
            value["research_main"]["unknown_auroc"] for value in repeats
        ),
        "oscr_exact_v2": min(
            value["research_main"]["oscr_exact_v2"] for value in repeats
        ),
    }


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    result_gates = gates(result)
    worst = worst_case(result)
    full_margin = min(
        worst["alert_accuracy"] - 0.95,
        0.05 - worst["benign_fpr"],
        worst["known_attack_type_accuracy"] - 0.95,
        worst["unknown_attack_alert_recall"] - 0.95,
    )
    return (
        result_gates["all_repeats_known_unknown_alert_95_5"],
        result_gates["all_repeats_user_warning_95_5"],
        result_gates["all_repeats_research_floor"],
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
        "gates": gates(result),
        "worst_case": worst_case(result),
        "macro_mean": result["macro_mean"],
        "per_repeat": result["per_repeat"],
    }


def evaluate(
    repeats: list[tuple[int, list[Path]]],
) -> dict[str, Any]:
    if len(repeats) != 2:
        raise ValueError("joint-alert development requires two splits")
    prepared = {
        str(split_seed): base.prepare_repeat(split_seed, member_dirs)
        for split_seed, member_dirs in repeats
    }
    if len(prepared) != len(repeats):
        raise ValueError("split identifiers must be unique")
    if {
        str(value["unknown_family"]) for value in prepared.values()
    } != {DEVELOPMENT_UNKNOWN_FAMILY}:
        raise ValueError("Botnet must be the only development unknown family")
    dataset_hashes = {
        str(value["dataset_sha256"]) for value in prepared.values()
    }
    if len(dataset_hashes) != 1:
        raise ValueError("development dataset identity drifted")
    candidates = [
        evaluate_configuration(prepared, configuration)
        for configuration in configurations()
    ]
    ranked = sorted(candidates, key=selection_key, reverse=True)
    selected = ranked[0]
    selected_gates = gates(selected)
    qualifies = (
        selected_gates["all_repeats_known_unknown_alert_95_5"]
        and selected_gates["all_repeats_research_floor"]
    )
    report: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_joint_alert_development_v4",
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
        "selected": compact(selected),
        "top_candidates": [compact(candidate) for candidate in ranked[:10]],
        "gate_pass_counts": {
            gate: sum(gates(candidate)[gate] for candidate in candidates)
            for gate in (
                "all_repeats_user_warning_95_5",
                "all_repeats_known_unknown_alert_95_5",
                "all_repeats_research_floor",
            )
        },
        "claim_boundary": {
            "development_only": True,
            "botnet_unknown_labels_used_for_joint_rule_selection": True,
            "botnet_excluded_from_future_confirmation_claim": True,
            "split43_and_split47_must_not_be_reused_for_confirmation": True,
            "alert_thresholds_fit_on_known_only_validation": True,
            "eligible_confirmation_unknown_families_are_disjoint": True,
            "no_member_training_or_score_mutation": True,
        },
        "source_sha256": {
            Path(__file__).name: file_hash(Path(__file__).resolve()),
            Path(base.__file__).name: file_hash(Path(base.__file__).resolve()),
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

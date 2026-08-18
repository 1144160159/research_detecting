from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_fhmm_same_split_ensemble import (
    _same,
    _same_array,
    majority_vote,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    operational_metrics,
    upper_tail_threshold,
)
from evaluate_strict_v4_packet_sequence_fusion_development import verify_task
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)
from strict_v4_open_set_metric_contract_v2 import (
    evaluate_open_set_metric_contract,
)


ATTACK_SOURCES = ("attack_head", "family", "maximum", "noisy_or")
AGGREGATIONS = ("mean", "median", "maximum")
ALERT_BUDGETS = (0.01, 0.02, 0.03, 0.04)
OPEN_BUDGETS = (0.01, 0.02, 0.04)
TYPE_RULES = ("majority", "validation_best_macro_f1_member")
TARGET = 0.95
LEGACY_UNKNOWN_ALERT_FLOOR = 0.6036585365853659


def empirical_upper_tail(
    reference: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    reference = np.sort(np.asarray(reference, dtype=np.float64).reshape(-1))
    values = np.asarray(values, dtype=np.float64)
    if reference.size == 0:
        raise ValueError("tail reference is empty")
    if not np.isfinite(reference).all() or not np.isfinite(values).all():
        raise ValueError("tail inputs must be finite")
    ranks = np.searchsorted(reference, values, side="right")
    return np.asarray(
        (ranks + 0.5) / (reference.size + 1.0),
        dtype=np.float64,
    )


def aggregate(values: list[np.ndarray], method: str) -> np.ndarray:
    if len(values) != 3:
        raise ValueError("fixed diagnostic requires exactly three members")
    stacked = np.stack(
        [np.asarray(value, dtype=np.float64) for value in values],
        axis=0,
    )
    if method == "mean":
        return stacked.mean(axis=0)
    if method == "median":
        return np.median(stacked, axis=0)
    if method == "maximum":
        return stacked.max(axis=0)
    raise ValueError(f"unsupported aggregation: {method}")


def macro_f1(labels: np.ndarray, prediction: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=np.int64)
    prediction = np.asarray(prediction, dtype=np.int64)
    classes = sorted(int(value) for value in np.unique(labels))
    scores = []
    for class_index in classes:
        true_positive = int(
            ((labels == class_index) & (prediction == class_index)).sum()
        )
        false_positive = int(
            ((labels != class_index) & (prediction == class_index)).sum()
        )
        false_negative = int(
            ((labels == class_index) & (prediction != class_index)).sum()
        )
        denominator = 2 * true_positive + false_positive + false_negative
        scores.append(
            2.0 * true_positive / denominator if denominator else 0.0
        )
    return float(np.mean(scores))


def prepare_repeat(
    split_seed: int,
    member_dirs: list[Path],
) -> dict[str, Any]:
    if len(member_dirs) != 3:
        raise ValueError("each repeat requires exactly three members")
    loaded = [verify_task(path.resolve()) for path in member_dirs]
    reports = [item[0] for item in loaded]
    arrays = [item[1] for item in loaded]
    observed_split = int(
        _same(
            "split_seed",
            [int(report["task"]["split_seed"]) for report in reports],
        )
    )
    if observed_split != split_seed:
        raise ValueError(
            f"declared split {split_seed} differs from {observed_split}"
        )
    model_seeds = [int(report["task"]["model_seed"]) for report in reports]
    if len(set(model_seeds)) != 3:
        raise ValueError("model seeds must be distinct")
    unknown_family = str(
        _same(
            "unknown_family",
            [str(report["task"]["unknown_family"]) for report in reports],
        )
    )
    benign_index = int(
        _same(
            "benign_index",
            [int(report["benign_index"]) for report in reports],
        )
    )
    dataset_sha256 = str(
        _same(
            "dataset_sha256",
            [
                str(report["source"]["sequence_dataset_sha256"])
                for report in reports
            ],
        )
    )
    known_class_names = _same_array(
        "known_class_names",
        [value["known_class_names"] for value in arrays],
    )
    validation_labels = _same_array(
        "validation_labels",
        [value["validation_labels"] for value in arrays],
    ).astype(np.int64)
    test_labels = _same_array(
        "test_labels",
        [value["test_labels"] for value in arrays],
    ).astype(np.int64)
    test_unknown = _same_array(
        "test_unknown",
        [value["test_unknown"] for value in arrays],
    ).astype(bool)
    validation_benign = validation_labels == benign_index
    validation_known_attack = validation_labels != benign_index

    attack_scores: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {}
    for source in ATTACK_SOURCES:
        member_validation = [
            np.asarray(
                value[f"validation_{source}_attack_probability"],
                dtype=np.float64,
            )
            for value in arrays
        ]
        member_test = [
            np.asarray(
                value[f"test_{source}_attack_probability"],
                dtype=np.float64,
            )
            for value in arrays
        ]
        validation_tail = [
            empirical_upper_tail(
                candidate[validation_benign],
                candidate,
            )
            for candidate in member_validation
        ]
        test_tail = [
            empirical_upper_tail(
                validation_candidate[validation_benign],
                test_candidate,
            )
            for validation_candidate, test_candidate in zip(
                member_validation,
                member_test,
            )
        ]
        attack_scores[source] = {
            method: (
                aggregate(validation_tail, method),
                aggregate(test_tail, method),
            )
            for method in AGGREGATIONS
        }

    member_validation_open = [
        np.asarray(value["validation_open_max"], dtype=np.float64)
        for value in arrays
    ]
    member_test_open = [
        np.asarray(value["test_open_max"], dtype=np.float64)
        for value in arrays
    ]
    validation_open_tail = [
        empirical_upper_tail(
            candidate[validation_known_attack],
            candidate,
        )
        for candidate in member_validation_open
    ]
    test_open_tail = [
        empirical_upper_tail(
            validation_candidate[validation_known_attack],
            test_candidate,
        )
        for validation_candidate, test_candidate in zip(
            member_validation_open,
            member_test_open,
        )
    ]
    open_scores = {
        method: (
            aggregate(validation_open_tail, method),
            aggregate(test_open_tail, method),
        )
        for method in AGGREGATIONS
    }

    validation_predictions = [
        np.asarray(value["validation_type_prediction"], dtype=np.int64)
        for value in arrays
    ]
    test_predictions = [
        np.asarray(value["test_type_prediction"], dtype=np.int64)
        for value in arrays
    ]
    validation_type_scores = [
        macro_f1(validation_labels, prediction)
        for prediction in validation_predictions
    ]
    best_index = max(
        range(3),
        key=lambda index: (
            validation_type_scores[index],
            -model_seeds[index],
        ),
    )
    type_predictions = {
        "majority": majority_vote(
            test_predictions,
            class_count=int(known_class_names.size),
        ),
        "validation_best_macro_f1_member": test_predictions[best_index],
    }
    return {
        "split_seed": split_seed,
        "unknown_family": unknown_family,
        "model_seeds": model_seeds,
        "dataset_sha256": dataset_sha256,
        "known_class_names": known_class_names,
        "benign_index": benign_index,
        "validation_labels": validation_labels,
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "attack_scores": attack_scores,
        "open_scores": open_scores,
        "type_predictions": type_predictions,
        "type_selection": {
            "validation_member_macro_f1": {
                str(seed): float(score)
                for seed, score in zip(model_seeds, validation_type_scores)
            },
            "selected_model_seed": model_seeds[best_index],
        },
        "source": [
            {
                "path": str(path.resolve()),
                "metrics_sha256": file_hash(path.resolve() / "metrics.json"),
                "scores_sha256": file_hash(path.resolve() / "scores.npz"),
                "gpu_execution_sha256": file_hash(
                    path.resolve() / "gpu_execution.json"
                ),
            }
            for path in member_dirs
        ],
    }


def configurations() -> list[dict[str, Any]]:
    return [
        {
            "attack_source": attack_source,
            "attack_aggregation": attack_aggregation,
            "alert_budget": alert_budget,
            "open_aggregation": open_aggregation,
            "open_budget": open_budget,
            "type_rule": type_rule,
        }
        for (
            attack_source,
            attack_aggregation,
            alert_budget,
            open_aggregation,
            open_budget,
            type_rule,
        ) in product(
            ATTACK_SOURCES,
            AGGREGATIONS,
            ALERT_BUDGETS,
            AGGREGATIONS,
            OPEN_BUDGETS,
            TYPE_RULES,
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
    validation_labels = prepared["validation_labels"]
    benign_index = int(prepared["benign_index"])
    alert_calibration = calibrate_threshold(
        validation_attack,
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        float(configuration["alert_budget"]),
    )
    if not alert_calibration["feasible"]:
        raise ValueError("alert calibration is infeasible")
    open_threshold = upper_tail_threshold(
        validation_open[validation_labels != benign_index],
        float(configuration["open_budget"]),
    )
    predicted_alert = test_attack >= float(alert_calibration["threshold"])
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
            operational["alert_accuracy"] >= TARGET
            and operational["benign_fpr"] < 0.05
        ),
        "typed_known_unknown_95_5": (
            operational["alert_accuracy"] >= TARGET
            and operational["benign_fpr"] < 0.05
            and operational["known_attack_type_accuracy"] >= TARGET
            and operational["unknown_attack_alert_recall"] >= TARGET
        ),
        "legacy_botnet_expansion": (
            operational["alert_accuracy"] >= TARGET
            and operational["benign_fpr"] < 0.05
            and operational["known_attack_type_accuracy"] >= TARGET
            and operational["unknown_attack_alert_recall"]
            >= LEGACY_UNKNOWN_ALERT_FLOOR
        ),
    }
    return {
        "operational": operational,
        "research": research,
        "gates": gates,
        "thresholds": {
            "alert": float(alert_calibration["threshold"]),
            "open": float(open_threshold),
        },
        "validation_alert_calibration": alert_calibration,
    }


def compact_research(contract: dict[str, Any]) -> dict[str, float]:
    return {
        "known_macro_f1": float(
            contract["closed_set_known"]["known_macro_f1"]
        ),
        "known_balanced_accuracy": float(
            contract["closed_set_known"]["known_balanced_accuracy"]
        ),
        "unknown_auroc": float(
            contract["unknown_detection"]["unknown_auroc"]
        ),
        "unknown_aupr_out": float(
            contract["unknown_detection"]["unknown_aupr_out"]
        ),
        "fpr_known_at_95_unknown_tpr": float(
            contract["unknown_detection"][
                "fpr_known_at_95_unknown_tpr"
            ]
        ),
        "oscr_exact_v2": float(
            contract["joint_open_set"]["oscr_exact_v2"]
        ),
    }


def evaluate_configuration(
    prepared_repeats: dict[str, dict[str, Any]],
    configuration: dict[str, Any],
) -> dict[str, Any]:
    per_repeat = {
        identity: evaluate_repeat(prepared, configuration)
        for identity, prepared in prepared_repeats.items()
    }
    operational_names = tuple(
        next(iter(per_repeat.values()))["operational"]
    )
    research_names = tuple(
        compact_research(
            next(iter(per_repeat.values()))["research"]
        )
    )
    compact = {
        identity: {
            "operational": value["operational"],
            "research_main": compact_research(value["research"]),
            "gates": value["gates"],
            "thresholds": value["thresholds"],
            "validation_alert_calibration": value[
                "validation_alert_calibration"
            ],
        }
        for identity, value in per_repeat.items()
    }
    macro_operational = {
        name: float(
            np.mean(
                [value["operational"][name] for value in per_repeat.values()]
            )
        )
        for name in operational_names
    }
    macro_research = {
        name: float(
            np.mean(
                [
                    compact_research(value["research"])[name]
                    for value in per_repeat.values()
                ]
            )
        )
        for name in research_names
    }
    worst_case = {
        "alert_accuracy": min(
            value["operational"]["alert_accuracy"]
            for value in per_repeat.values()
        ),
        "benign_fpr": max(
            value["operational"]["benign_fpr"]
            for value in per_repeat.values()
        ),
        "known_attack_type_accuracy": min(
            value["operational"]["known_attack_type_accuracy"]
            for value in per_repeat.values()
        ),
        "unknown_attack_alert_recall": min(
            value["operational"]["unknown_attack_alert_recall"]
            for value in per_repeat.values()
        ),
        "unknown_auroc": min(
            compact_research(value["research"])["unknown_auroc"]
            for value in per_repeat.values()
        ),
        "oscr_exact_v2": min(
            compact_research(value["research"])["oscr_exact_v2"]
            for value in per_repeat.values()
        ),
    }
    gate_names = tuple(next(iter(per_repeat.values()))["gates"])
    gates = {
        f"all_repeats_{name}": all(
            value["gates"][name] for value in per_repeat.values()
        )
        for name in gate_names
    }
    gates.update(
        {
            f"repeat_pass_count_{name}": sum(
                value["gates"][name] for value in per_repeat.values()
            )
            for name in gate_names
        }
    )
    return {
        "configuration": configuration,
        "gates": gates,
        "worst_case": worst_case,
        "macro_mean": {
            "operational": macro_operational,
            "research_main": macro_research,
        },
        "per_repeat": compact,
    }


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    gates = result["gates"]
    worst = result["worst_case"]
    typed_margin = min(
        worst["alert_accuracy"] - TARGET,
        0.05 - worst["benign_fpr"],
        worst["known_attack_type_accuracy"] - TARGET,
        worst["unknown_attack_alert_recall"] - TARGET,
    )
    user_margin = min(
        worst["alert_accuracy"] - TARGET,
        0.05 - worst["benign_fpr"],
    )
    return (
        gates["all_repeats_typed_known_unknown_95_5"],
        gates["all_repeats_user_warning_95_5"],
        gates["all_repeats_legacy_botnet_expansion"],
        gates["repeat_pass_count_typed_known_unknown_95_5"],
        gates["repeat_pass_count_user_warning_95_5"],
        gates["repeat_pass_count_legacy_botnet_expansion"],
        typed_margin,
        user_margin,
        worst["unknown_attack_alert_recall"],
        worst["known_attack_type_accuracy"],
        worst["oscr_exact_v2"],
        worst["unknown_auroc"],
        -worst["benign_fpr"],
    )


def summarize_candidate(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "configuration": result["configuration"],
        "gates": result["gates"],
        "worst_case": result["worst_case"],
        "macro_mean": result["macro_mean"],
    }


def evaluate(
    repeats: list[tuple[int, list[Path]]],
) -> dict[str, Any]:
    if len(repeats) < 2:
        raise ValueError("at least two split repeats are required")
    prepared = {
        str(split_seed): prepare_repeat(split_seed, member_dirs)
        for split_seed, member_dirs in repeats
    }
    if len(prepared) != len(repeats):
        raise ValueError("split repeat identifiers must be unique")
    dataset_sha256 = str(
        _same(
            "dataset_sha256",
            [value["dataset_sha256"] for value in prepared.values()],
        )
    )
    unknown_family = str(
        _same(
            "unknown_family",
            [value["unknown_family"] for value in prepared.values()],
        )
    )
    results = [
        evaluate_configuration(prepared, configuration)
        for configuration in configurations()
    ]
    ranked = sorted(results, key=selection_key, reverse=True)
    selected = ranked[0]
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fhmm_calibrated_aggregation_development_v1"
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
            "attack_sources": list(ATTACK_SOURCES),
            "aggregations": list(AGGREGATIONS),
            "alert_budgets": list(ALERT_BUDGETS),
            "open_budgets": list(OPEN_BUDGETS),
            "type_rules": list(TYPE_RULES),
            "candidate_count": len(configurations()),
        },
        "claim_boundary": {
            "development_only": True,
            "true_unknown_test_used_for_candidate_ranking": True,
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


from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    gates,
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


ALERT_BUDGET = 0.049
OPEN_BUDGET = 0.04
TARGET = 0.95
BOTNET_EXPANSION_UNKNOWN_ALERT_RECALL = 0.6036585365853659


def _same(name: str, values: list[Any]) -> Any:
    first = values[0]
    if any(value != first for value in values[1:]):
        raise ValueError(f"ensemble members disagree on {name}")
    return first


def _same_array(name: str, arrays: list[np.ndarray]) -> np.ndarray:
    first = np.asarray(arrays[0])
    if any(
        candidate.shape != first.shape
        or not np.array_equal(candidate, first)
        for candidate in arrays[1:]
    ):
        raise ValueError(f"ensemble member arrays differ: {name}")
    return first


def majority_vote(
    predictions: list[np.ndarray],
    *,
    class_count: int,
) -> np.ndarray:
    if len(predictions) != 3:
        raise ValueError("fixed ensemble requires exactly three members")
    stacked = np.stack(
        [np.asarray(value, dtype=np.int64) for value in predictions],
        axis=0,
    )
    counts = np.stack(
        [(stacked == index).sum(axis=0) for index in range(class_count)],
        axis=0,
    )
    return counts.argmax(axis=0).astype(np.int64)


def _pairwise_diagnostics(
    member_arrays: list[dict[str, np.ndarray]],
    *,
    split: str,
) -> list[dict[str, Any]]:
    diagnostics = []
    for left, right in combinations(range(len(member_arrays)), 2):
        left_attack = np.asarray(
            member_arrays[left][
                f"{split}_attack_head_attack_probability"
            ],
            dtype=np.float64,
        )
        right_attack = np.asarray(
            member_arrays[right][
                f"{split}_attack_head_attack_probability"
            ],
            dtype=np.float64,
        )
        left_open = np.asarray(
            member_arrays[left][f"{split}_open_max"],
            dtype=np.float64,
        )
        right_open = np.asarray(
            member_arrays[right][f"{split}_open_max"],
            dtype=np.float64,
        )
        left_type = np.asarray(
            member_arrays[left][f"{split}_type_prediction"],
            dtype=np.int64,
        )
        right_type = np.asarray(
            member_arrays[right][f"{split}_type_prediction"],
            dtype=np.int64,
        )

        def correlation(first: np.ndarray, second: np.ndarray) -> float | None:
            if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
                return None
            return float(np.corrcoef(first, second)[0, 1])

        diagnostics.append(
            {
                "left_member_index": left,
                "right_member_index": right,
                "attack_probability_pearson": correlation(
                    left_attack,
                    right_attack,
                ),
                "open_score_pearson": correlation(left_open, right_open),
                "type_prediction_agreement": float(
                    (left_type == right_type).mean()
                ),
            }
        )
    return diagnostics


def evaluate_members(
    member_dirs: list[Path],
) -> dict[str, Any]:
    if len(member_dirs) != 3:
        raise ValueError("fixed ensemble requires exactly three member dirs")
    loaded = [verify_task(path.resolve()) for path in member_dirs]
    metrics = [item[0] for item in loaded]
    arrays = [item[1] for item in loaded]
    if any(
        not str(report["model"]["name"]).startswith("FHMM-CAEOS")
        or report["training"]["meta_heldout_loss_weight"] <= 0.0
        for report in metrics
    ):
        raise ValueError("all ensemble members must be FHMM tasks")

    split_seed = int(
        _same(
            "split_seed",
            [int(report["task"]["split_seed"]) for report in metrics],
        )
    )
    model_seeds = [int(report["task"]["model_seed"]) for report in metrics]
    if len(set(model_seeds)) != 3:
        raise ValueError("ensemble model seeds must be distinct")
    unknown_family = str(
        _same(
            "unknown_family",
            [str(report["task"]["unknown_family"]) for report in metrics],
        )
    )
    benign_index = int(
        _same(
            "benign_index",
            [int(report["benign_index"]) for report in metrics],
        )
    )
    dataset_sha256 = str(
        _same(
            "sequence_dataset_sha256",
            [
                str(report["source"]["sequence_dataset_sha256"])
                for report in metrics
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

    validation_attack = np.mean(
        np.stack(
            [
                value["validation_attack_head_attack_probability"]
                for value in arrays
            ],
            axis=0,
        ),
        axis=0,
    )
    test_attack = np.mean(
        np.stack(
            [
                value["test_attack_head_attack_probability"]
                for value in arrays
            ],
            axis=0,
        ),
        axis=0,
    )
    validation_open = np.mean(
        np.stack(
            [value["validation_open_max"] for value in arrays],
            axis=0,
        ),
        axis=0,
    )
    test_open = np.mean(
        np.stack(
            [value["test_open_max"] for value in arrays],
            axis=0,
        ),
        axis=0,
    )
    type_prediction = majority_vote(
        [value["test_type_prediction"] for value in arrays],
        class_count=int(known_class_names.size),
    )

    alert_calibration = calibrate_threshold(
        validation_attack,
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        ALERT_BUDGET,
    )
    if not alert_calibration["feasible"]:
        raise ValueError("ensemble alert calibration is infeasible")
    known_attack_validation = validation_labels != benign_index
    open_threshold = upper_tail_threshold(
        validation_open[known_attack_validation],
        OPEN_BUDGET,
    )
    predicted_alert = test_attack >= float(alert_calibration["threshold"])
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    operational = operational_metrics(
        predicted_alert=predicted_alert,
        predicted_unknown=predicted_unknown,
        type_prediction=type_prediction,
        test_labels=test_labels,
        test_unknown=test_unknown,
        benign_index=benign_index,
    )
    research = evaluate_open_set_metric_contract(
        labels=test_labels,
        known_prediction=type_prediction,
        is_unknown=test_unknown,
        unknown_risk=test_open,
        rejected_as_unknown=predicted_unknown,
        class_names=[str(value) for value in known_class_names.tolist()],
    )
    expansion_gate = {
        "alert_accuracy_at_least_95_percent": (
            operational["alert_accuracy"] >= TARGET
        ),
        "benign_fpr_below_5_percent": operational["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            operational["known_attack_type_accuracy"] >= TARGET
        ),
        "unknown_attack_alert_recall_at_least_60p37_percent": (
            operational["unknown_attack_alert_recall"]
            >= BOTNET_EXPANSION_UNKNOWN_ALERT_RECALL
        ),
    }
    expansion_gate["expand_to_seven_scenarios"] = all(
        expansion_gate.values()
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_same_split_ensemble_evaluation_v1",
        "state": (
            "pilot_expansion_gate_passed"
            if expansion_gate["expand_to_seven_scenarios"]
            else "pilot_expansion_gate_not_met"
        ),
        "task": {
            "unknown_family": unknown_family,
            "split_seed": split_seed,
            "model_seeds": model_seeds,
        },
        "source": {
            "sequence_dataset_sha256": dataset_sha256,
            "members": [
                {
                    "path": str(path.resolve()),
                    "metrics_sha256": file_hash(
                        path.resolve() / "metrics.json"
                    ),
                    "scores_sha256": file_hash(
                        path.resolve() / "scores.npz"
                    ),
                    "gpu_execution_sha256": file_hash(
                        path.resolve() / "gpu_execution.json"
                    ),
                }
                for path in member_dirs
            ],
        },
        "fixed_configuration": {
            "member_count": 3,
            "attack_aggregation": "arithmetic_mean_probability",
            "open_aggregation": "arithmetic_mean_member_open_max",
            "type_aggregation": (
                "three_member_hard_majority_vote_lowest_class_tie_break"
            ),
            "alert_budget": ALERT_BUDGET,
            "open_budget": OPEN_BUDGET,
            "configuration_selection": "none_fixed_before_test",
        },
        "validation": {
            "alert_calibration": alert_calibration,
            "open_threshold": float(open_threshold),
        },
        "operational_metrics": operational,
        "operational_gates": gates(operational),
        "research_metric_contract": research,
        "expansion_gate": expansion_gate,
        "member_diagnostics": {
            "validation": _pairwise_diagnostics(
                arrays,
                split="validation",
            ),
            "test": _pairwise_diagnostics(arrays, split="test"),
        },
        "claim_boundary": {
            "development_pilot_only": True,
            "true_unknown_used_for_training_or_early_stopping": False,
            "true_unknown_used_for_configuration_or_threshold_selection": False,
            "test_labels_used_only_for_final_metric_computation": True,
            "fresh_confirmation_effect_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--member-dir",
        type=Path,
        action="append",
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = evaluate_members(args.member_dir)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

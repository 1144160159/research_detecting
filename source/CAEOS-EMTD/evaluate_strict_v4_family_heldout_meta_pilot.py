from __future__ import annotations

import argparse
import json
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


ALERT_BUDGET = 0.049
OPEN_BUDGET = 0.04
TARGET = 0.95
BOTNET_EXPANSION_UNKNOWN_ALERT_RECALL = 0.6036585365853659


def fixed_evaluation(
    metrics_report: dict[str, Any],
    arrays: dict[str, np.ndarray],
) -> dict[str, Any]:
    if not str(metrics_report["model"]["name"]).startswith("FHMM-CAEOS"):
        raise ValueError("FHMM-CAEOS task metrics are required")
    if metrics_report["training"]["meta_heldout_loss_weight"] <= 0.0:
        raise ValueError("family-held-out meta objective was not enabled")
    benign_index = int(metrics_report["benign_index"])
    validation_labels = np.asarray(
        arrays["validation_labels"], dtype=np.int64
    )
    validation_alert = np.asarray(
        arrays["validation_attack_head_attack_probability"],
        dtype=np.float64,
    )
    calibration = calibrate_threshold(
        validation_alert,
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        ALERT_BUDGET,
    )
    if not calibration["feasible"]:
        raise ValueError("fixed alert calibration is infeasible")
    validation_open = np.asarray(
        arrays["validation_open_max"], dtype=np.float64
    )
    known_attack_validation = validation_labels != benign_index
    open_threshold = upper_tail_threshold(
        validation_open[known_attack_validation],
        OPEN_BUDGET,
    )
    test_alert = np.asarray(
        arrays["test_attack_head_attack_probability"], dtype=np.float64
    )
    test_open = np.asarray(arrays["test_open_max"], dtype=np.float64)
    predicted_alert = test_alert >= float(calibration["threshold"])
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    metric_values = operational_metrics(
        predicted_alert=predicted_alert,
        predicted_unknown=predicted_unknown,
        type_prediction=np.asarray(
            arrays["test_type_prediction"], dtype=np.int64
        ),
        test_labels=np.asarray(arrays["test_labels"], dtype=np.int64),
        test_unknown=np.asarray(arrays["test_unknown"], dtype=bool),
        benign_index=benign_index,
    )
    expansion_gate = {
        "alert_accuracy_at_least_95_percent": (
            metric_values["alert_accuracy"] >= TARGET
        ),
        "benign_fpr_below_5_percent": metric_values["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            metric_values["known_attack_type_accuracy"] >= TARGET
        ),
        "unknown_attack_alert_recall_at_least_60p37_percent": (
            metric_values["unknown_attack_alert_recall"]
            >= BOTNET_EXPANSION_UNKNOWN_ALERT_RECALL
        ),
    }
    expansion_gate["expand_to_seven_scenarios"] = all(
        expansion_gate.values()
    )
    return {
        "configuration": {
            "attack_probability": "attack_head",
            "alert_budget": ALERT_BUDGET,
            "open_score": "open_max",
            "open_budget": OPEN_BUDGET,
            "configuration_selection": "none_fixed_before_test",
        },
        "validation_alert_calibration": calibration,
        "open_threshold": float(open_threshold),
        "metrics": metric_values,
        "gates": gates(metric_values),
        "expansion_gate": expansion_gate,
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    task_dir = args.task_dir.resolve()
    metrics_report, arrays = verify_task(task_dir)
    fixed = fixed_evaluation(metrics_report, arrays)
    result: dict[str, Any] = {
        "schema_version": "strict_v4_family_heldout_meta_pilot_v1",
        "state": (
            "pilot_expansion_gate_passed"
            if fixed["expansion_gate"]["expand_to_seven_scenarios"]
            else "pilot_expansion_gate_not_met"
        ),
        "scenario": metrics_report["task"]["unknown_family"],
        "fixed_evaluation": fixed,
        "task_source": {
            "task_dir": str(task_dir),
            "metrics_sha256": file_hash(task_dir / "metrics.json"),
            "scores_sha256": file_hash(task_dir / "scores.npz"),
            "gpu_execution_sha256": file_hash(task_dir / "gpu_execution.json"),
        },
        "claim_boundary": {
            "development_pilot_only": True,
            "true_unknown_used_for_training_or_early_stopping": False,
            "true_unknown_used_for_configuration_selection": False,
            "single_fixed_configuration_opened_once": True,
            "fresh_confirmation_effect_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    result = evaluate(parse_arguments())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

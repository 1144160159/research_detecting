from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_family_heldout_meta_pilot import (
    fixed_evaluation as fixed_evaluation_v1,
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


def fixed_evaluation(
    metrics_report: dict[str, Any],
    arrays: dict[str, np.ndarray],
) -> dict[str, Any]:
    fixed = fixed_evaluation_v1(metrics_report, arrays)
    test_labels = np.asarray(arrays["test_labels"], dtype=np.int64)
    test_unknown = np.asarray(arrays["test_unknown"], dtype=bool)
    test_open = np.asarray(arrays["test_open_max"], dtype=np.float64)
    test_alert = np.asarray(
        arrays["test_attack_head_attack_probability"],
        dtype=np.float64,
    )
    alert_threshold = float(
        fixed["validation_alert_calibration"]["threshold"]
    )
    predicted_unknown = (test_alert >= alert_threshold) & (
        test_open >= float(fixed["open_threshold"])
    )
    fixed["research_metric_contract"] = evaluate_open_set_metric_contract(
        labels=test_labels,
        known_prediction=np.asarray(
            arrays["test_type_prediction"], dtype=np.int64
        ),
        is_unknown=test_unknown,
        unknown_risk=test_open,
        rejected_as_unknown=predicted_unknown,
        class_names=[
            str(value) for value in arrays.get("known_class_names", [])
        ]
        or None,
        known_class_probabilities=(
            np.asarray(arrays["test_family_probability"], dtype=np.float64)
            if "test_family_probability" in arrays
            else None
        ),
    )
    return fixed


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    task_dir = args.task_dir.resolve()
    metrics_report, arrays = verify_task(task_dir)
    fixed = fixed_evaluation(metrics_report, arrays)
    result: dict[str, Any] = {
        "schema_version": "strict_v4_family_heldout_meta_pilot_v2",
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
            "gpu_execution_sha256": file_hash(
                task_dir / "gpu_execution.json"
            ),
        },
        "claim_boundary": {
            "development_pilot_only": True,
            "true_unknown_used_for_training_or_early_stopping": False,
            "true_unknown_used_for_configuration_selection": False,
            "single_fixed_configuration_opened_once": True,
            "metric_contract_added_posthoc_without_selection": True,
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

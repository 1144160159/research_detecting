from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_packet_sequence_fusion_development import verify_task
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


QUANTILES = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0)


def distribution(values: np.ndarray) -> dict[str, Any]:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError("finite non-empty score distribution required")
    return {
        "count": int(values.size),
        "mean": float(values.mean()),
        "standard_deviation": float(values.std()),
        "quantiles": {
            f"{value:.2f}": float(np.quantile(values, value))
            for value in QUANTILES
        },
    }


def task_summary(
    task_dir: Path,
    evaluation_path: Path,
) -> tuple[dict[str, Any], np.ndarray]:
    metrics, arrays = verify_task(task_dir.resolve())
    evaluation = load_canonical(
        evaluation_path.resolve(), "fixed FHMM evaluation"
    )
    threshold = float(
        evaluation["fixed_evaluation"]["validation_alert_calibration"][
            "threshold"
        ]
    )
    benign_index = int(metrics["benign_index"])
    validation_labels = np.asarray(arrays["validation_labels"], dtype=np.int64)
    test_labels = np.asarray(arrays["test_labels"], dtype=np.int64)
    test_unknown = np.asarray(arrays["test_unknown"], dtype=bool)
    validation_score = np.asarray(
        arrays["validation_attack_head_attack_probability"],
        dtype=np.float64,
    )
    test_score = np.asarray(
        arrays["test_attack_head_attack_probability"], dtype=np.float64
    )
    unknown_score = test_score[test_unknown]
    summary = {
        "seed": int(metrics["task"]["seed"]),
        "best_epoch": int(metrics["model"]["best_epoch"]),
        "best_validation_loss": float(
            metrics["model"]["best_validation_loss"]
        ),
        "epochs_completed": int(metrics["model"]["epochs_completed"]),
        "alert_threshold": threshold,
        "validation_benign": distribution(
            validation_score[validation_labels == benign_index]
        ),
        "validation_known_attack": distribution(
            validation_score[validation_labels != benign_index]
        ),
        "test_benign": distribution(
            test_score[(test_labels == benign_index) & ~test_unknown]
        ),
        "test_known_attack": distribution(
            test_score[(test_labels != benign_index) & ~test_unknown]
        ),
        "test_unknown_attack": distribution(unknown_score),
        "observed_test_benign_fpr": float(
            (
                test_score[(test_labels == benign_index) & ~test_unknown]
                >= threshold
            ).mean()
        ),
        "observed_unknown_alert_recall": float(
            (unknown_score >= threshold).mean()
        ),
        "source": {
            "task_dir": str(task_dir.resolve()),
            "metrics_sha256": file_hash(task_dir.resolve() / "metrics.json"),
            "scores_sha256": file_hash(task_dir.resolve() / "scores.npz"),
            "evaluation_path": str(evaluation_path.resolve()),
            "evaluation_sha256": file_hash(evaluation_path.resolve()),
        },
    }
    return summary, unknown_score


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    left, left_unknown = task_summary(
        args.left_task_dir, args.left_evaluation
    )
    right, right_unknown = task_summary(
        args.right_task_dir, args.right_evaluation
    )
    if left_unknown.shape != right_unknown.shape:
        raise ValueError("unknown score arrays differ in shape")
    left_alert = left_unknown >= left["alert_threshold"]
    right_alert = right_unknown >= right["alert_threshold"]
    result: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_seed_instability_v1",
        "state": "diagnostic_complete",
        "tasks": {
            str(left["seed"]): left,
            str(right["seed"]): right,
        },
        "same_unknown_rows_comparison": {
            "ordering_basis": (
                "all unknown-family rows are retained and test indices are "
                "sorted by original dataset row"
            ),
            "row_count": int(left_unknown.size),
            "pearson_probability_correlation": float(
                np.corrcoef(left_unknown, right_unknown)[0, 1]
            ),
            "mean_absolute_probability_difference": float(
                np.abs(left_unknown - right_unknown).mean()
            ),
            "alert_decision_agreement": float(
                (left_alert == right_alert).mean()
            ),
            "both_alert": float((left_alert & right_alert).mean()),
            "left_only_alert": float((left_alert & ~right_alert).mean()),
            "right_only_alert": float((~left_alert & right_alert).mean()),
            "neither_alert": float((~left_alert & ~right_alert).mean()),
        },
        "claim_boundary": {
            "post_pilot_diagnostic_only": True,
            "not_used_to_rewrite_frozen_pilot_metrics": True,
            "no_new_effect_configuration_selected": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-task-dir", type=Path, required=True)
    parser.add_argument("--left-evaluation", type=Path, required=True)
    parser.add_argument("--right-task-dir", type=Path, required=True)
    parser.add_argument("--right-evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = analyze(args)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

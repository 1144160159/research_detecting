from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


SCENARIOS = ("bot", "infiltration", "portscan")
SEEDS = (907, 911, 919)
TOTAL_BUDGETS = (0.04, 0.044)
RESCUE_BUDGETS = (0.002, 0.005, 0.01, 0.015, 0.02)


def probability_scores(probability: np.ndarray) -> dict[str, np.ndarray]:
    values = np.asarray(probability, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] < 2:
        raise ValueError("probability must be a two-dimensional class matrix")
    values = np.clip(values, 1e-12, 1.0)
    values /= values.sum(axis=1, keepdims=True)
    ordered = np.sort(values, axis=1)
    entropy = -(values * np.log(values)).sum(axis=1)
    return {
        "uncertainty": 1.0 - values.max(axis=1),
        "normalized_entropy": entropy / np.log(values.shape[1]),
        "top2_closeness": 1.0 - (ordered[:, -1] - ordered[:, -2]),
    }


def benign_threshold(score: np.ndarray, budget: float) -> float:
    values = np.asarray(score, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("benign calibration score must be non-empty")
    if budget <= 0.0:
        return float("inf")
    if not 0.0 < budget < 1.0:
        raise ValueError("false-positive budget must be in (0, 1)")
    return float(np.quantile(values, 1.0 - budget, method="higher"))


def evaluate_task(
    *,
    validation_probability: np.ndarray,
    validation_labels: np.ndarray,
    test_probability: np.ndarray,
    test_labels: np.ndarray,
    test_unknown: np.ndarray,
    primary_budget: float,
    rescue_name: str | None,
    rescue_budget: float,
) -> dict[str, Any]:
    validation_labels = np.asarray(validation_labels, dtype=np.int64)
    test_labels = np.asarray(test_labels, dtype=np.int64)
    test_unknown = np.asarray(test_unknown, dtype=bool)
    validation_benign = validation_labels == 0
    if not validation_benign.any() or np.any(validation_labels < 0):
        raise ValueError("validation must be known-only and contain benign")

    validation_attack = 1.0 - validation_probability[:, 0]
    test_attack = 1.0 - test_probability[:, 0]
    primary_threshold = benign_threshold(
        validation_attack[validation_benign], primary_budget
    )
    alert = test_attack >= primary_threshold
    validation_alert = validation_attack >= primary_threshold
    rescue_threshold: float | None = None
    if rescue_name is not None:
        validation_rescue = probability_scores(validation_probability)[
            rescue_name
        ]
        test_rescue = probability_scores(test_probability)[rescue_name]
        rescue_threshold = benign_threshold(
            validation_rescue[validation_benign], rescue_budget
        )
        alert |= test_rescue >= rescue_threshold
        validation_alert |= validation_rescue >= rescue_threshold

    attack = (test_labels != 0) | test_unknown
    benign = ~attack
    true_positive = int(np.sum(alert & attack))
    false_positive = int(np.sum(alert & benign))
    predicted_positive = true_positive + false_positive
    known_attack = (~test_unknown) & (test_labels != 0)
    type_prediction = np.asarray(test_probability).argmax(axis=1)
    return {
        "counts": {
            "samples": int(len(alert)),
            "attacks": int(attack.sum()),
            "benign": int(benign.sum()),
            "true_positive": true_positive,
            "false_positive": false_positive,
            "unknown_attacks": int(test_unknown.sum()),
            "unknown_alerts": int(np.sum(alert & test_unknown)),
            "known_attacks": int(known_attack.sum()),
            "known_type_correct": int(
                np.sum(type_prediction[known_attack] == test_labels[known_attack])
            ),
        },
        "thresholds": {
            "primary": primary_threshold,
            "rescue": rescue_threshold,
        },
        "validation_combined_benign_fpr": float(
            validation_alert[validation_benign].mean()
        ),
        "metrics": {
            "alert_accuracy": float(np.mean(alert == attack)),
            "alert_precision": float(
                true_positive / predicted_positive
                if predicted_positive
                else 0.0
            ),
            "attack_recall": float(alert[attack].mean()),
            "benign_fpr": float(alert[benign].mean()),
            "known_attack_type_accuracy": float(
                np.mean(
                    type_prediction[known_attack] == test_labels[known_attack]
                )
                if known_attack.any()
                else 0.0
            ),
            "unknown_attack_alert_recall": float(
                alert[test_unknown].mean()
            ),
        },
    }


def merge_task_metrics(tasks: list[dict[str, Any]]) -> dict[str, float]:
    counts = {
        name: sum(task["counts"][name] for task in tasks)
        for name in tasks[0]["counts"]
    }
    predicted_positive = counts["true_positive"] + counts["false_positive"]
    return {
        "alert_accuracy": float(
            (
                counts["true_positive"]
                + counts["benign"]
                - counts["false_positive"]
            )
            / counts["samples"]
        ),
        "alert_precision": float(
            counts["true_positive"] / predicted_positive
            if predicted_positive
            else 0.0
        ),
        "attack_recall": float(
            counts["true_positive"] / counts["attacks"]
        ),
        "benign_fpr": float(
            counts["false_positive"] / counts["benign"]
        ),
        "known_attack_type_accuracy": float(
            counts["known_type_correct"] / counts["known_attacks"]
        ),
        "unknown_attack_alert_recall": float(
            counts["unknown_alerts"] / counts["unknown_attacks"]
        ),
    }


def selection_key(record: dict[str, Any]) -> tuple[Any, ...]:
    metrics = record["overall"]
    return (
        metrics["benign_fpr"] < 0.05,
        metrics["unknown_attack_alert_recall"],
        metrics["attack_recall"],
        metrics["alert_accuracy"],
        -metrics["benign_fpr"],
    )


def load_task(input_root: Path, scenario: str, seed: int) -> dict[str, Any]:
    scores_path = (
        input_root / f"{scenario}_seed{seed}_xgboost_scores.npz"
    )
    metrics_path = (
        input_root / f"{scenario}_seed{seed}_xgboost_metrics.json"
    )
    with np.load(scores_path, allow_pickle=False) as payload:
        arrays = {name: np.asarray(payload[name]) for name in payload.files}
    return {
        "arrays": arrays,
        "source": {
            "scores_path": str(scores_path.resolve()),
            "scores_sha256": file_hash(scores_path),
            "metrics_path": str(metrics_path.resolve()),
            "metrics_sha256": file_hash(metrics_path),
        },
    }


def build_analysis(input_root: Path) -> dict[str, Any]:
    tasks = {
        (scenario, seed): load_task(input_root, scenario, seed)
        for scenario in SCENARIOS
        for seed in SEEDS
    }
    candidates: list[dict[str, Any]] = []
    for total_budget in TOTAL_BUDGETS:
        candidates.append(
            {
                "name": f"primary_only_{total_budget:.3f}",
                "total_budget": total_budget,
                "primary_budget": total_budget,
                "rescue_name": None,
                "rescue_budget": 0.0,
            }
        )
        for rescue_name in (
            "uncertainty",
            "normalized_entropy",
            "top2_closeness",
        ):
            for rescue_budget in RESCUE_BUDGETS:
                if rescue_budget >= total_budget:
                    continue
                candidates.append(
                    {
                        "name": (
                            f"{rescue_name}_"
                            f"{total_budget - rescue_budget:.3f}_"
                            f"{rescue_budget:.3f}"
                        ),
                        "total_budget": total_budget,
                        "primary_budget": total_budget - rescue_budget,
                        "rescue_name": rescue_name,
                        "rescue_budget": rescue_budget,
                    }
                )

    records: list[dict[str, Any]] = []
    for candidate in candidates:
        per_task: dict[str, Any] = {}
        task_values: list[dict[str, Any]] = []
        for (scenario, seed), task in tasks.items():
            result = evaluate_task(
                **task["arrays"],
                primary_budget=candidate["primary_budget"],
                rescue_name=candidate["rescue_name"],
                rescue_budget=candidate["rescue_budget"],
            )
            identity = f"{scenario}_seed{seed}"
            per_task[identity] = result
            task_values.append(result)
        records.append(
            {
                "candidate": candidate,
                "overall": merge_task_metrics(task_values),
                "per_task": per_task,
            }
        )
    selected = max(records, key=selection_key)
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fine_probability_rescue_analysis_v1"
        ),
        "state": "complete_adaptive_development_analysis",
        "selected": selected,
        "records": records,
        "sources": {
            f"{scenario}_seed{seed}": task["source"]
            for (scenario, seed), task in tasks.items()
        },
        "claim_boundary": {
            "scores_were_generated_by_formal_gpu_xgboost_runs": True,
            "analysis_runs_locally_without_model_training": True,
            "thresholds_use_known_only_validation": True,
            "current_unknown_test_used_for_candidate_selection": True,
            "adaptive_development_only": True,
            "fresh_unseen_seeds_required_before_effect_claim": True,
        },
    }
    report["trigger_confirmation"] = bool(
        selected["overall"]["alert_accuracy"] >= 0.95
        and selected["overall"]["alert_precision"] >= 0.95
        and selected["overall"]["attack_recall"] >= 0.95
        and selected["overall"]["benign_fpr"] < 0.05
        and selected["overall"]["known_attack_type_accuracy"] >= 0.95
        and selected["overall"]["unknown_attack_alert_recall"] >= 0.95
    )
    report["manifest_sha256"] = canonical_hash(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_analysis(args.input_root.resolve())
    atomic_json(args.output.resolve(), report)
    print(
        json.dumps(
            {
                "manifest_sha256": report["manifest_sha256"],
                "selected_candidate": report["selected"]["candidate"],
                "selected_metrics": report["selected"]["overall"],
                "trigger_confirmation": report["trigger_confirmation"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

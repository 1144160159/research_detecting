from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    gates,
    mean_metrics,
    operational_metrics,
    upper_tail_threshold,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


ALERT_AUXILIARIES = (
    "open_max",
    "open_noisy_or",
    "family_uncertainty_tail",
    "knownness_uncertainty_tail",
    "prototype_distance_tail",
    "benign_distance_tail",
    "benign_reference_distance_tail",
)
OPEN_VARIANTS = ALERT_AUXILIARIES
BUDGETS = (0.04, 0.045, 0.049)


def verify_task(task_dir: Path) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    metrics = load_canonical(task_dir / "metrics.json", f"metrics {task_dir.name}")
    gpu = load_canonical(
        task_dir / "gpu_execution.json", f"GPU evidence {task_dir.name}"
    )
    if (
        metrics.get("state") != "complete"
        or not metrics.get("gpu_execution", {}).get("passes")
        or not gpu.get("passes")
    ):
        raise ValueError(f"incomplete CUDA task: {task_dir}")
    for artifact in metrics["artifacts"].values():
        path = task_dir / artifact["file"]
        if file_hash(path) != artifact["sha256"]:
            raise ValueError(f"task artifact drifted: {path}")
    with np.load(task_dir / "scores.npz", allow_pickle=False) as source:
        arrays = {name: np.asarray(source[name]) for name in source.files}
    required = {
        "validation_attack_probability",
        "validation_open_max",
        "validation_open_noisy_or",
        "validation_family_uncertainty_tail",
        "validation_knownness_uncertainty_tail",
        "validation_prototype_distance_tail",
        "validation_benign_distance_tail",
        "validation_type_prediction",
        "validation_labels",
        "test_attack_probability",
        "test_open_max",
        "test_open_noisy_or",
        "test_family_uncertainty_tail",
        "test_knownness_uncertainty_tail",
        "test_prototype_distance_tail",
        "test_benign_distance_tail",
        "test_type_prediction",
        "test_labels",
        "test_unknown",
        "known_class_names",
    }
    missing = sorted(required - set(arrays))
    if missing:
        raise ValueError(f"task scores miss arrays: {missing}")
    return metrics, arrays


def auxiliary(
    arrays: dict[str, np.ndarray], split: str, variant: str
) -> np.ndarray:
    return np.asarray(arrays[f"{split}_{variant}"], dtype=np.float64)


def percentile_tail(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    reference = np.sort(np.asarray(reference, dtype=np.float64))
    if reference.size == 0:
        raise ValueError("tail percentile reference is empty")
    ranks = np.searchsorted(reference, values, side="right")
    return np.asarray((ranks + 0.5) / (reference.size + 1.0), dtype=np.float64)


def add_benign_reference_distance_tail(
    metrics: dict[str, Any],
    arrays: dict[str, np.ndarray],
) -> None:
    benign_index = int(metrics["benign_index"])
    validation_labels = np.asarray(arrays["validation_labels"], dtype=np.int64)
    validation_distance_rank = np.asarray(
        arrays["validation_benign_distance_tail"], dtype=np.float64
    )
    test_distance_rank = np.asarray(
        arrays["test_benign_distance_tail"], dtype=np.float64
    )
    reference = validation_distance_rank[validation_labels == benign_index]
    arrays["validation_benign_reference_distance_tail"] = percentile_tail(
        reference, validation_distance_rank
    )
    arrays["test_benign_reference_distance_tail"] = percentile_tail(
        reference, test_distance_rank
    )


def alert_score(
    arrays: dict[str, np.ndarray],
    *,
    split: str,
    combination: str,
    auxiliary_variant: str,
) -> np.ndarray:
    binary = np.asarray(
        arrays[f"{split}_attack_probability"], dtype=np.float64
    )
    if combination == "binary":
        return binary
    open_score = auxiliary(arrays, split, auxiliary_variant)
    if combination == "binary_open_max":
        return np.maximum(binary, open_score)
    if combination == "binary_open_noisy_or":
        return 1.0 - (1.0 - binary) * (1.0 - open_score)
    raise ValueError(f"unsupported alert combination: {combination}")


def configurations() -> list[dict[str, Any]]:
    values = []
    for combination in ("binary", "binary_open_max", "binary_open_noisy_or"):
        auxiliaries = ("open_max",) if combination == "binary" else ALERT_AUXILIARIES
        for auxiliary_variant, open_variant, alert_budget, open_budget in product(
            auxiliaries, OPEN_VARIANTS, BUDGETS, BUDGETS
        ):
            values.append(
                {
                    "alert_combination": combination,
                    "alert_auxiliary": auxiliary_variant,
                    "open_variant": open_variant,
                    "alert_budget": alert_budget,
                    "open_budget": open_budget,
                }
            )
    return values


def evaluate_configuration(
    prepared: dict[str, dict[str, Any]],
    configuration: dict[str, Any],
) -> dict[str, Any]:
    per_scenario = {}
    for scenario, task in prepared.items():
        arrays = task["arrays"]
        metrics_report = task["metrics"]
        benign_index = int(metrics_report["benign_index"])
        validation_labels = np.asarray(arrays["validation_labels"], dtype=np.int64)
        validation_alert = alert_score(
            arrays,
            split="validation",
            combination=configuration["alert_combination"],
            auxiliary_variant=configuration["alert_auxiliary"],
        )
        test_alert = alert_score(
            arrays,
            split="test",
            combination=configuration["alert_combination"],
            auxiliary_variant=configuration["alert_auxiliary"],
        )
        calibration = calibrate_threshold(
            validation_alert,
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(configuration["alert_budget"]),
        )
        if not calibration["feasible"]:
            raise ValueError(f"infeasible alert calibration for {scenario}")
        validation_open = auxiliary(
            arrays, "validation", configuration["open_variant"]
        )
        test_open = auxiliary(arrays, "test", configuration["open_variant"])
        known_attack_validation = validation_labels != benign_index
        open_threshold = upper_tail_threshold(
            validation_open[known_attack_validation],
            float(configuration["open_budget"]),
        )
        predicted_alert = test_alert >= float(calibration["threshold"])
        predicted_unknown = predicted_alert & (test_open >= open_threshold)
        metrics = operational_metrics(
            predicted_alert=predicted_alert,
            predicted_unknown=predicted_unknown,
            type_prediction=np.asarray(
                arrays["test_type_prediction"], dtype=np.int64
            ),
            test_labels=np.asarray(arrays["test_labels"], dtype=np.int64),
            test_unknown=np.asarray(arrays["test_unknown"], dtype=bool),
            benign_index=benign_index,
        )
        per_scenario[scenario] = {
            "metrics": metrics,
            "gates": gates(metrics),
            "alert_threshold": float(calibration["threshold"]),
            "open_threshold": float(open_threshold),
            "validation_alert_calibration": calibration,
        }
    macro = mean_metrics(
        value["metrics"] for value in per_scenario.values()
    )
    return {
        "configuration": configuration,
        "macro_mean": macro,
        "gates": gates(macro),
        "scenario_basic_gate_pass_count": sum(
            value["gates"]["basic_warning_95_5_gate"]
            for value in per_scenario.values()
        ),
        "scenario_full_gate_pass_count": sum(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in per_scenario.values()
        ),
        "per_scenario": per_scenario,
    }


def selection_key(result: dict[str, Any]) -> tuple[Any, ...]:
    metrics = result["macro_mean"]
    value_gates = result["gates"]
    minimum_unknown = min(
        value["metrics"]["unknown_attack_recall"]
        for value in result["per_scenario"].values()
    )
    return (
        bool(value_gates["full_known_unknown_95_5_gate"]),
        result["scenario_full_gate_pass_count"],
        bool(value_gates["basic_warning_95_5_gate"]),
        result["scenario_basic_gate_pass_count"],
        min(metrics["alert_accuracy"], metrics["alert_recall"]),
        metrics["known_attack_type_accuracy"],
        metrics["unknown_attack_recall"],
        minimum_unknown,
        -metrics["benign_fpr"],
    )


def compact(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "configuration": result["configuration"],
        "macro_mean": result["macro_mean"],
        "gates": result["gates"],
        "scenario_basic_gate_pass_count": result[
            "scenario_basic_gate_pass_count"
        ],
        "scenario_full_gate_pass_count": result[
            "scenario_full_gate_pass_count"
        ],
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    completion = load_canonical(
        args.completion.resolve(), "packet-sequence CUDA completion"
    )
    if (
        completion.get("state") != "complete"
        or completion.get("failure_count") != 0
        or not completion.get("gpu_execution", {}).get("all_tasks_passed")
    ):
        raise ValueError("packet-sequence CUDA completion did not pass")
    prepared = {}
    task_sources = {}
    for identity, task in sorted(completion["task_artifacts"].items()):
        task_dir = Path(task["output_dir"])
        metrics, arrays = verify_task(task_dir)
        add_benign_reference_distance_tail(metrics, arrays)
        scenario = str(metrics["task"]["unknown_family"])
        if scenario in prepared:
            raise ValueError(f"duplicate unknown-family task: {scenario}")
        prepared[scenario] = {"metrics": metrics, "arrays": arrays}
        task_sources[scenario] = {
            "task_dir": str(task_dir),
            "metrics_sha256": file_hash(task_dir / "metrics.json"),
            "scores_sha256": file_hash(task_dir / "scores.npz"),
            "gpu_execution_sha256": file_hash(task_dir / "gpu_execution.json"),
        }
    candidates = [
        evaluate_configuration(prepared, configuration)
        for configuration in configurations()
    ]
    selected = max(candidates, key=selection_key)
    result: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_development_v1",
        "state": (
            "development_full_gate_passed"
            if selected["gates"]["full_known_unknown_95_5_gate"]
            else "development_gate_not_met"
        ),
        "selection_seed": int(completion["seed"]),
        "candidate_count": len(candidates),
        "selected": selected,
        "candidate_summaries": [compact(candidate) for candidate in candidates],
        "task_sources": task_sources,
        "completion": {
            "path": str(args.completion.resolve()),
            "file_sha256": file_hash(args.completion.resolve()),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "claim_boundary": {
            "development_only": True,
            "true_unknown_used_for_configuration_selection": True,
            "fresh_confirmation_required_for_effect_claim": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "gpu_execution_proven_for_each_training_task": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    result = evaluate(parse_arguments())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

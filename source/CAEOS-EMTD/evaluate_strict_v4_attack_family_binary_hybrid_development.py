from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_cicids2017_attack_family_gpu_hybrid import (
    prepare_by_seed,
    verify_chain,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    OPEN_BUDGETS,
    OPEN_VARIANTS,
    combine_tail,
    empirical_cdf,
    gates,
    mean_metrics,
    open_scores,
    operational_metrics,
    selection_key,
    upper_tail_threshold,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


ALERT_VARIANTS = (
    "binary_attack",
    "binary_pairwise_tail_max",
    "binary_pairwise_tail_noisy_or",
    "xgb_binary_tail_max",
    "xgb_binary_tail_noisy_or",
    "triple_tail_max",
    "triple_tail_noisy_or",
)
ALERT_BUDGETS = (0.01, 0.02, 0.03, 0.04, 0.045, 0.049)


def verify_binary_completion(
    binary_completion_path: Path,
) -> dict[str, Any]:
    completion = load_canonical(
        binary_completion_path, "binary CUDA development completion"
    )
    if (
        completion.get("state") != "complete"
        or completion.get("failure_count") != 0
        or not completion.get("gpu_execution", {}).get("all_tasks_passed")
    ):
        raise ValueError("binary CUDA development completion did not pass")
    for identity, task in completion["task_artifacts"].items():
        for name, expected in task["artifact_sha256"].items():
            if file_hash(Path(task["output_dir"]) / name) != expected:
                raise ValueError(f"binary artifact drifted: {identity}/{name}")
    return completion


def augment_binary_scores(
    prepared: dict[str, Any],
    source_completion: dict[str, Any],
    binary_completion: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    for scenario, arrays in prepared.items():
        identity = f"{scenario}_seed{seed}"
        source_task = source_completion["task_artifacts"][identity]
        binary_task = binary_completion["task_artifacts"][identity]
        binary_dir = Path(binary_task["output_dir"])
        binary_metrics = load_canonical(
            binary_dir / "metrics.json", f"binary metrics {identity}"
        )
        if binary_metrics["task"]["scenario"] != scenario:
            raise ValueError(f"binary task identity mismatch: {identity}")
        with np.load(binary_dir / "scores.npz", allow_pickle=False) as scores:
            validation_attack_probability = np.asarray(
                scores["validation_attack_probability"], dtype=np.float64
            )
            validation_labels = np.asarray(
                scores["validation_labels"], dtype=np.int64
            )
            test_attack_probability = np.asarray(
                scores["test_attack_probability"], dtype=np.float64
            )
            test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
            test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
        if not (
            np.array_equal(validation_labels, arrays["validation_labels"])
            and np.array_equal(test_labels, arrays["test_labels"])
            and np.array_equal(test_unknown, arrays["test_unknown"])
        ):
            raise ValueError(f"binary split arrays differ: {identity}")
        benign_index = int(arrays["benign_index"])
        validation_benign = validation_labels == benign_index
        arrays["binary_validation_attack"] = validation_attack_probability
        arrays["binary_test_attack"] = test_attack_probability
        arrays["binary_validation_attack_tail"] = empirical_cdf(
            validation_attack_probability[validation_benign],
            validation_attack_probability,
        )
        arrays["binary_test_attack_tail"] = empirical_cdf(
            validation_attack_probability[validation_benign],
            test_attack_probability,
        )
        arrays["binary_source_sha256"] = {
            "metrics": binary_task["artifact_sha256"]["metrics.json"],
            "scores": binary_task["artifact_sha256"]["scores.npz"],
            "gpu_execution": binary_task["artifact_sha256"][
                "gpu_execution.json"
            ],
            "source_xgboost_metrics": source_task["xgboost_sha256"][
                "metrics.json"
            ],
        }
    return prepared


def alert_scores(
    arrays: dict[str, Any], variant: str
) -> tuple[np.ndarray, np.ndarray]:
    binary_validation = arrays["binary_validation_attack_tail"]
    binary_test = arrays["binary_test_attack_tail"]
    xgb_validation = arrays["validation_attack_tail"]
    xgb_test = arrays["test_attack_tail"]
    risk_validation = arrays["validation_risk_benign_tail"]
    risk_test = arrays["test_risk_benign_tail"]
    if variant == "binary_attack":
        return (
            arrays["binary_validation_attack"],
            arrays["binary_test_attack"],
        )
    if variant == "binary_pairwise_tail_max":
        return (
            np.maximum(binary_validation, risk_validation),
            np.maximum(binary_test, risk_test),
        )
    if variant == "binary_pairwise_tail_noisy_or":
        return (
            combine_tail(binary_validation, risk_validation, "tail_noisy_or"),
            combine_tail(binary_test, risk_test, "tail_noisy_or"),
        )
    if variant == "xgb_binary_tail_max":
        return (
            np.maximum(xgb_validation, binary_validation),
            np.maximum(xgb_test, binary_test),
        )
    if variant == "xgb_binary_tail_noisy_or":
        return (
            combine_tail(xgb_validation, binary_validation, "tail_noisy_or"),
            combine_tail(xgb_test, binary_test, "tail_noisy_or"),
        )
    if variant == "triple_tail_max":
        return (
            np.maximum.reduce(
                [xgb_validation, binary_validation, risk_validation]
            ),
            np.maximum.reduce([xgb_test, binary_test, risk_test]),
        )
    if variant == "triple_tail_noisy_or":
        return (
            combine_tail(
                combine_tail(
                    xgb_validation, binary_validation, "tail_noisy_or"
                ),
                risk_validation,
                "tail_noisy_or",
            ),
            combine_tail(
                combine_tail(xgb_test, binary_test, "tail_noisy_or"),
                risk_test,
                "tail_noisy_or",
            ),
        )
    raise ValueError(f"unsupported alert variant: {variant}")


def evaluate_configuration(
    prepared: dict[str, dict[str, Any]], configuration: dict[str, Any]
) -> dict[str, Any]:
    per_scenario = {}
    for scenario, arrays in prepared.items():
        validation_alert_score, test_alert_score = alert_scores(
            arrays, configuration["alert_variant"]
        )
        validation_open_score, test_open_score = open_scores(
            arrays, configuration["open_variant"]
        )
        benign_index = int(arrays["benign_index"])
        validation_labels = arrays["validation_labels"]
        alert_calibration = calibrate_threshold(
            validation_alert_score,
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(configuration["alert_budget"]),
        )
        open_threshold = upper_tail_threshold(
            validation_open_score[validation_labels != benign_index],
            float(configuration["open_budget"]),
        )
        predicted_alert = test_alert_score >= float(
            alert_calibration["threshold"]
        )
        predicted_unknown = predicted_alert & (
            test_open_score >= open_threshold
        )
        metrics = operational_metrics(
            predicted_alert=predicted_alert,
            predicted_unknown=predicted_unknown,
            type_prediction=arrays["type_prediction"],
            test_labels=arrays["test_labels"],
            test_unknown=arrays["test_unknown"],
            benign_index=benign_index,
        )
        per_scenario[scenario] = {
            "metrics": metrics,
            "gates": gates(metrics),
            "alert_threshold": float(alert_calibration["threshold"]),
            "open_threshold": open_threshold,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--binary-completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol, source_completion = verify_chain(
        args.project_root.resolve(),
        args.protocol.resolve(),
        args.completion.resolve(),
    )
    if protocol["stage"] != "development":
        raise ValueError("binary hybrid evaluation is development-only")
    binary_completion = verify_binary_completion(
        args.binary_completion.resolve()
    )
    if (
        binary_completion["binding"]["protocol_manifest_sha256"]
        != protocol["manifest_sha256"]
        or binary_completion["binding"]["completion_manifest_sha256"]
        != source_completion["manifest_sha256"]
    ):
        raise ValueError("binary completion does not bind source development")
    prepared_by_seed, source_hashes = prepare_by_seed(
        protocol, source_completion
    )
    seed = int(protocol["development_seed"])
    prepared = augment_binary_scores(
        prepared_by_seed[seed],
        source_completion,
        binary_completion,
        seed,
    )
    candidates = [
        evaluate_configuration(
            prepared,
            {
                "alert_variant": alert_variant,
                "alert_budget": alert_budget,
                "open_variant": open_variant,
                "open_budget": open_budget,
            },
        )
        for alert_variant, alert_budget, open_variant, open_budget in product(
            ALERT_VARIANTS, ALERT_BUDGETS, OPEN_VARIANTS, OPEN_BUDGETS
        )
    ]
    selected = max(candidates, key=selection_key)
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_binary_hybrid_development_v1",
        "state": "complete_development_only",
        "algorithm": (
            "Dual CUDA XGBoost Hybrid CAEOS: binary malicious-warning head, "
            "multiclass known-family expert, and Pairwise open-set head"
        ),
        "development_seed": seed,
        "candidate_count": len(candidates),
        "selected": selected,
        "macro_basic_gate_candidate_count": sum(
            value["gates"]["basic_warning_95_5_gate"] for value in candidates
        ),
        "macro_full_gate_candidate_count": sum(
            value["gates"]["full_known_unknown_95_5_gate"]
            for value in candidates
        ),
        "candidate_summary": {
            (
                f"{value['configuration']['alert_variant']}"
                f"__a{value['configuration']['alert_budget']:.3f}"
                f"__{value['configuration']['open_variant']}"
                f"__o{value['configuration']['open_budget']:.3f}"
            ): compact(value)
            for value in candidates
        },
        "source_sha256": {
            "source_tasks": source_hashes,
            "binary_completion_file": file_hash(
                args.binary_completion.resolve()
            ),
        },
        "binding": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "source_completion_manifest_sha256": source_completion[
                "manifest_sha256"
            ],
            "binary_completion_manifest_sha256": binary_completion[
                "manifest_sha256"
            ],
        },
        "claim_boundary": {
            "development_labels_used_for_selection": True,
            "fresh_confirmation_results_read": False,
            "not_a_confirmation_result": True,
            "all_xgboost_model_training_uses_cuda": True,
            "pairwise_open_set_head_uses_cpu": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    atomic_json(args.output.resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    combine_tail,
    empirical_cdf,
    mean_metrics,
    operational_metrics,
    upper_tail_threshold,
)
from evaluate_strict_v4_neural_empirical_tail_hybrid_qualification import (
    contract_metrics,
    verify_xgboost_source,
)
from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    prepare_scenario,
)
from project_contract import evaluate_delivery_line
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


def conditional_empirical_cdf(
    reference_values: np.ndarray,
    reference_classes: np.ndarray,
    query_values: np.ndarray,
    query_classes: np.ndarray,
    *,
    minimum_local_reference: int,
    local_shrinkage: float,
) -> np.ndarray:
    reference_values = np.asarray(reference_values, dtype=np.float64)
    reference_classes = np.asarray(reference_classes, dtype=np.int64)
    query_values = np.asarray(query_values, dtype=np.float64)
    query_classes = np.asarray(query_classes, dtype=np.int64)
    if reference_values.ndim != 1 or query_values.ndim != 1:
        raise ValueError("conditional CDF inputs must be one-dimensional")
    if reference_values.shape != reference_classes.shape:
        raise ValueError("reference values and classes differ in shape")
    if query_values.shape != query_classes.shape:
        raise ValueError("query values and classes differ in shape")
    if reference_values.size == 0:
        raise ValueError("conditional CDF reference is empty")
    if minimum_local_reference < 1 or local_shrinkage < 0.0:
        raise ValueError("invalid conditional CDF support settings")
    global_tail = empirical_cdf(reference_values, query_values)
    result = global_tail.copy()
    for class_id in np.unique(query_classes):
        query_mask = query_classes == class_id
        local_reference = reference_values[reference_classes == class_id]
        if local_reference.size < minimum_local_reference:
            continue
        local_tail = empirical_cdf(
            local_reference, query_values[query_mask]
        )
        local_weight = float(
            local_reference.size
            / (local_reference.size + local_shrinkage)
        )
        result[query_mask] = (
            local_weight * local_tail
            + (1.0 - local_weight) * global_tail[query_mask]
        )
    return result


def evaluate_scenario(
    arrays: dict[str, Any], method: dict[str, Any]
) -> dict[str, Any]:
    benign_index = int(arrays["benign_index"])
    validation_labels = arrays["validation_labels"]
    validation_attack = validation_labels != benign_index
    validation_benign = ~validation_attack
    validation_classes = arrays["validation_type_prediction"]
    test_classes = arrays["type_prediction"]
    risk_values = arrays["risk_values"][method["risk_name"]]
    support = int(method["minimum_local_reference"])
    shrinkage = float(method["local_shrinkage"])
    if method["open_score"] == "class_conditional_tail_noisy_or":
        validation_risk_tail = conditional_empirical_cdf(
            risk_values["validation"][validation_attack],
            validation_classes[validation_attack],
            risk_values["validation"],
            validation_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        test_risk_tail = conditional_empirical_cdf(
            risk_values["validation"][validation_attack],
            validation_classes[validation_attack],
            risk_values["test"],
            test_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        validation_uncertainty_tail = conditional_empirical_cdf(
            arrays["validation_uncertainty"][validation_attack],
            validation_classes[validation_attack],
            arrays["validation_uncertainty"],
            validation_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        test_uncertainty_tail = conditional_empirical_cdf(
            arrays["validation_uncertainty"][validation_attack],
            validation_classes[validation_attack],
            arrays["test_uncertainty"],
            test_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        validation_open = combine_tail(
            validation_risk_tail,
            validation_uncertainty_tail,
            "tail_noisy_or",
        )
        test_open = combine_tail(
            test_risk_tail, test_uncertainty_tail, "tail_noisy_or"
        )
    elif method["open_score"] == "global_attack_tail_noisy_or":
        global_risk_tail = arrays["risk_tails"][
            method.get("open_risk_name", method["risk_name"])
        ]
        validation_open = combine_tail(
            global_risk_tail["validation_attack"],
            arrays["validation_uncertainty_tail"],
            "tail_noisy_or",
        )
        test_open = combine_tail(
            global_risk_tail["test_attack"],
            arrays["test_uncertainty_tail"],
            "tail_noisy_or",
        )
    else:
        raise ValueError(f"unsupported open score: {method['open_score']}")
    alert_thresholds: dict[str, float]
    if method["alert_score"] == "xgboost_attack_probability":
        validation_alert = arrays["xgboost_validation_attack"]
        test_alert = arrays["xgboost_test_attack"]
    elif method["alert_score"] == "class_conditional_benign_tail_noisy_or":
        validation_benign_risk_tail = conditional_empirical_cdf(
            risk_values["validation"][validation_benign],
            validation_classes[validation_benign],
            risk_values["validation"],
            validation_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        test_benign_risk_tail = conditional_empirical_cdf(
            risk_values["validation"][validation_benign],
            validation_classes[validation_benign],
            risk_values["test"],
            test_classes,
            minimum_local_reference=support,
            local_shrinkage=shrinkage,
        )
        validation_alert = combine_tail(
            arrays["validation_attack_tail"],
            validation_benign_risk_tail,
            "tail_noisy_or",
        )
        test_alert = combine_tail(
            arrays["test_attack_tail"],
            test_benign_risk_tail,
            "tail_noisy_or",
        )
    elif method["alert_score"] == "budgeted_xgboost_or_knn_rescue":
        global_risk_tail = arrays["risk_tails"][method["risk_name"]]
        primary_calibration = calibrate_threshold(
            arrays["xgboost_validation_attack"],
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(method["primary_alert_budget"]),
        )
        if not primary_calibration["feasible"]:
            raise ValueError("infeasible primary alert calibration")
        rescue_threshold = upper_tail_threshold(
            global_risk_tail["validation_benign"][validation_benign],
            float(method["rescue_alert_budget"]),
        )
        predicted_alert = (
            arrays["xgboost_test_attack"]
            >= float(primary_calibration["threshold"])
        ) | (
            global_risk_tail["test_benign"] >= rescue_threshold
        )
        alert_thresholds = {
            "primary": float(primary_calibration["threshold"]),
            "rescue": float(rescue_threshold),
        }
    else:
        raise ValueError(f"unsupported alert score: {method['alert_score']}")
    if method["alert_score"] != "budgeted_xgboost_or_knn_rescue":
        calibration = calibrate_threshold(
            validation_alert,
            np.full(validation_labels.shape, benign_index, dtype=np.int64),
            validation_labels,
            benign_index,
            float(method["alert_budget"]),
        )
        if not calibration["feasible"]:
            raise ValueError("infeasible known-only alert calibration")
        predicted_alert = test_alert >= float(calibration["threshold"])
        alert_thresholds = {
            "combined": float(calibration["threshold"])
        }
    open_threshold = upper_tail_threshold(
        validation_open[validation_attack],
        float(method["open_budget"]),
    )
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    metrics = contract_metrics(
        operational_metrics(
            predicted_alert=predicted_alert,
            predicted_unknown=predicted_unknown,
            type_prediction=test_classes,
            test_labels=arrays["test_labels"],
            test_unknown=arrays["test_unknown"],
            benign_index=benign_index,
        )
    )
    return {
        "metrics": metrics,
        "engineering": evaluate_delivery_line(metrics, "engineering"),
        "paper": evaluate_delivery_line(metrics, "paper"),
        "alert_thresholds": alert_thresholds,
        "open_threshold": float(open_threshold),
    }


def build_development(protocol_path: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "development protocol")
    parent = load_canonical(
        Path(protocol["parent_protocol"]["path"]), "parent protocol"
    )
    completion = load_canonical(
        Path(protocol["source_completion"]["path"]), "source completion"
    )
    if file_hash(Path(protocol["parent_protocol"]["path"])) != protocol[
        "parent_protocol"
    ]["file_sha256"]:
        raise ValueError("parent protocol hash mismatch")
    if file_hash(Path(protocol["source_completion"]["path"])) != protocol[
        "source_completion"
    ]["file_sha256"]:
        raise ValueError("source completion hash mismatch")
    project_root = Path(__file__).resolve().parent
    for name, expected_hash in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected_hash:
            raise ValueError(f"implementation hash mismatch: {name}")

    per_seed = {}
    all_metrics = []
    source_sha256 = {}
    for seed in protocol["seeds"]:
        scenario_contract = {}
        seed_metrics = []
        seed_sources = {}
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            neural_artifact = completion["neural_task_artifacts"][identity]
            neural_dir = Path(neural_artifact["task_dir"])
            xgboost_dir = Path(parent["xgboost_root"]) / identity
            verify_xgboost_source(
                completion,
                identity=identity,
                task_dir=xgboost_dir,
            )
            arrays, hashes = prepare_scenario(
                neural_dir,
                xgboost_dir,
                (protocol["method"]["risk_name"],),
            )
            if (
                file_hash(neural_dir / "metrics.json")
                != neural_artifact["metrics_sha256"]
                or file_hash(neural_dir / "scores.npz")
                != neural_artifact["scores_sha256"]
            ):
                raise ValueError(f"neural source hash mismatch: {identity}")
            result = evaluate_scenario(arrays, protocol["method"])
            scenario_contract[scenario] = result
            seed_metrics.append(result["metrics"])
            all_metrics.append(result["metrics"])
            seed_sources[scenario] = hashes
        macro = mean_metrics(seed_metrics)
        per_seed[str(seed)] = {
            "metrics": macro,
            "engineering": evaluate_delivery_line(macro, "engineering"),
            "paper": evaluate_delivery_line(macro, "paper"),
            "scenario_contract": scenario_contract,
        }
        source_sha256[str(seed)] = seed_sources
    overall = mean_metrics(all_metrics)
    payload: dict[str, Any] = {
        "schema_version": (
            "strict_v4_class_conditional_tail_development_v1"
        ),
        "state": "complete_adaptive_development",
        "algorithm": protocol["method"]["algorithm"],
        "method": protocol["method"],
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
        },
        "per_seed": per_seed,
        "overall": {
            "metrics": overall,
            "engineering": evaluate_delivery_line(overall, "engineering"),
            "paper": evaluate_delivery_line(overall, "paper"),
        },
        "scenario_pass_counts": {
            "engineering": sum(
                result["engineering"]["passed"]
                for seed_result in per_seed.values()
                for result in seed_result["scenario_contract"].values()
            ),
            "paper": sum(
                result["paper"]["passed"]
                for seed_result in per_seed.values()
                for result in seed_result["scenario_contract"].values()
            ),
            "total": len(protocol["seeds"]) * len(protocol["scenarios"]),
        },
        "source_sha256": source_sha256,
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["trigger_fresh_unseen_seed_confirmation"] = bool(
        payload["overall"]["engineering"]["passed"]
        and all(
            seed_result["engineering"]["passed"]
            for seed_result in per_seed.values()
        )
    )
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_development(args.protocol)
    if args.output.resolve() != Path(
        load_canonical(args.protocol, "development protocol")["result_path"]
    ):
        raise ValueError("output does not match frozen result path")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "engineering_passed": payload["overall"]["engineering"][
                    "passed"
                ],
                "manifest_sha256": payload["manifest_sha256"],
                "paper_passed": payload["overall"]["paper"]["passed"],
                "trigger_fresh_unseen_seed_confirmation": payload[
                    "trigger_fresh_unseen_seed_confirmation"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

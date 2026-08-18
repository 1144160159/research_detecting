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


def calibrated_prediction(
    scores: np.ndarray,
    labels: np.ndarray,
    benign_index: int,
    budget: float,
) -> tuple[np.ndarray, float | None]:
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    if budget == 0.0:
        return np.zeros(labels.shape, dtype=bool), None
    calibration = calibrate_threshold(
        scores,
        np.full(labels.shape, benign_index, dtype=np.int64),
        labels,
        benign_index,
        budget,
    )
    if not calibration["feasible"]:
        raise ValueError("infeasible known-only alert calibration")
    return scores >= float(calibration["threshold"]), float(
        calibration["threshold"]
    )


def evaluate_candidate(
    *,
    arrays: dict[str, Any],
    validation_autoencoder: np.ndarray,
    test_autoencoder: np.ndarray,
    candidate: dict[str, Any],
    open_risk_name: str,
    open_budget: float,
) -> dict[str, Any]:
    benign_index = int(arrays["benign_index"])
    validation_labels = arrays["validation_labels"]
    validation_benign = validation_labels == benign_index
    validation_primary, primary_threshold = calibrated_prediction(
        arrays["xgboost_validation_attack"],
        validation_labels,
        benign_index,
        float(candidate["primary_alert_budget"]),
    )
    validation_rescue, rescue_threshold = calibrated_prediction(
        validation_autoencoder,
        validation_labels,
        benign_index,
        float(candidate["autoencoder_rescue_budget"]),
    )
    if primary_threshold is None:
        test_primary = np.zeros(arrays["test_labels"].shape, dtype=bool)
    else:
        test_primary = (
            arrays["xgboost_test_attack"] >= primary_threshold
        )
    if rescue_threshold is None:
        test_rescue = np.zeros(arrays["test_labels"].shape, dtype=bool)
    else:
        test_rescue = test_autoencoder >= rescue_threshold
    predicted_alert = test_primary | test_rescue
    validation_alert = validation_primary | validation_rescue

    risk_tail = arrays["risk_tails"][open_risk_name]
    validation_open = combine_tail(
        risk_tail["validation_attack"],
        arrays["validation_uncertainty_tail"],
        "tail_noisy_or",
    )
    test_open = combine_tail(
        risk_tail["test_attack"],
        arrays["test_uncertainty_tail"],
        "tail_noisy_or",
    )
    validation_attack = ~validation_benign
    open_threshold = upper_tail_threshold(
        validation_open[validation_attack], open_budget
    )
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    metrics = contract_metrics(
        operational_metrics(
            predicted_alert=predicted_alert,
            predicted_unknown=predicted_unknown,
            type_prediction=arrays["type_prediction"],
            test_labels=arrays["test_labels"],
            test_unknown=arrays["test_unknown"],
            benign_index=benign_index,
        )
    )
    return {
        "metrics": metrics,
        "engineering": evaluate_delivery_line(metrics, "engineering"),
        "paper": evaluate_delivery_line(metrics, "paper"),
        "thresholds": {
            "primary": primary_threshold,
            "autoencoder_rescue": rescue_threshold,
            "open": float(open_threshold),
        },
        "validation_combined_benign_fpr": float(
            validation_alert[validation_benign].mean()
        ),
    }


def selection_key(record: dict[str, Any]) -> tuple[Any, ...]:
    metrics = record["overall"]["metrics"]
    per_seed = record["per_seed"]
    test_fpr_feasible = metrics["benign_fpr"] < 0.05
    return (
        record["overall"]["engineering"]["passed"],
        all(value["engineering"]["passed"] for value in per_seed.values()),
        test_fpr_feasible,
        metrics["unknown_attack_alert_recall"],
        min(
            value["metrics"]["unknown_attack_alert_recall"]
            for value in per_seed.values()
        ),
        metrics["alert_accuracy"],
        metrics["attack_recall"],
        -metrics["benign_fpr"],
    )


def build_evaluation(protocol_path: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "autoencoder protocol")
    parent_path = Path(protocol["parent_protocol"]["path"])
    source_completion_path = Path(protocol["source_completion"]["path"])
    baseline_path = Path(protocol["baseline_qualification"]["path"])
    completion_path = Path(protocol["completion_path"])
    parent = load_canonical(parent_path, "parent protocol")
    source_completion = load_canonical(
        source_completion_path, "source completion"
    )
    baseline = load_canonical(baseline_path, "baseline qualification")
    completion = load_canonical(
        completion_path, "autoencoder completion"
    )
    for path, binding in (
        (parent_path, protocol["parent_protocol"]),
        (source_completion_path, protocol["source_completion"]),
        (baseline_path, protocol["baseline_qualification"]),
    ):
        if file_hash(path) != binding["file_sha256"]:
            raise ValueError(f"bound file hash mismatch: {path}")
    if (
        completion.get("effect_execution_passed") is not True
        or completion.get("task_coverage", {}).get("passed") is not True
        or completion.get("protocol", {}).get("manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("autoencoder CUDA effect execution is incomplete")
    project_root = Path(__file__).resolve().parent
    for name, expected_hash in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected_hash:
            raise ValueError(f"implementation hash mismatch: {name}")

    prepared = {}
    source_sha256 = {}
    risk_name = protocol["open_set_evaluation"]["risk_name"]
    for seed in protocol["seeds"]:
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            source_artifact = source_completion[
                "xgboost_task_artifacts"
            ][identity]
            neural_artifact = source_completion["neural_task_artifacts"][
                identity
            ]
            xgboost_dir = Path(parent["xgboost_root"]) / identity
            neural_dir = Path(neural_artifact["task_dir"])
            verify_xgboost_source(
                source_completion,
                identity=identity,
                task_dir=xgboost_dir,
            )
            arrays, hashes = prepare_scenario(
                neural_dir, xgboost_dir, (risk_name,)
            )
            autoencoder_artifact = completion["task_artifacts"][identity]
            autoencoder_dir = Path(autoencoder_artifact["output_dir"])
            for name, expected_hash in autoencoder_artifact[
                "artifact_sha256"
            ].items():
                if file_hash(autoencoder_dir / name) != expected_hash:
                    raise ValueError(
                        f"autoencoder artifact mismatch: {identity}/{name}"
                    )
            with np.load(
                autoencoder_dir / "scores.npz", allow_pickle=False
            ) as scores:
                validation_autoencoder = np.asarray(
                    scores["validation_reconstruction_error"],
                    dtype=np.float64,
                )
                validation_labels = np.asarray(
                    scores["validation_labels"], dtype=np.int64
                )
                test_autoencoder = np.asarray(
                    scores["test_reconstruction_error"],
                    dtype=np.float64,
                )
                test_labels = np.asarray(
                    scores["test_labels"], dtype=np.int64
                )
                test_unknown = np.asarray(
                    scores["test_unknown"], dtype=bool
                )
            if not (
                np.array_equal(validation_labels, arrays["validation_labels"])
                and np.array_equal(test_labels, arrays["test_labels"])
                and np.array_equal(test_unknown, arrays["test_unknown"])
            ):
                raise ValueError(
                    f"autoencoder split arrays differ: {identity}"
                )
            prepared[identity] = {
                "arrays": arrays,
                "validation_autoencoder": validation_autoencoder,
                "test_autoencoder": test_autoencoder,
            }
            source_sha256[identity] = {
                **hashes,
                "autoencoder_metrics": autoencoder_artifact[
                    "artifact_sha256"
                ]["metrics.json"],
                "autoencoder_scores": autoencoder_artifact[
                    "artifact_sha256"
                ]["scores.npz"],
            }

    records = []
    for candidate in protocol["alert_evaluation"]["candidates"]:
        per_seed = {}
        all_metrics = []
        for seed in protocol["seeds"]:
            scenario_contract = {}
            seed_metrics = []
            for scenario in protocol["scenarios"]:
                identity = f"{scenario}_seed{seed}"
                block = prepared[identity]
                result = evaluate_candidate(
                    arrays=block["arrays"],
                    validation_autoencoder=block["validation_autoencoder"],
                    test_autoencoder=block["test_autoencoder"],
                    candidate=candidate,
                    open_risk_name=risk_name,
                    open_budget=float(
                        protocol["open_set_evaluation"]["open_budget"]
                    ),
                )
                scenario_contract[scenario] = result
                seed_metrics.append(result["metrics"])
                all_metrics.append(result["metrics"])
            seed_macro = mean_metrics(seed_metrics)
            per_seed[str(seed)] = {
                "metrics": seed_macro,
                "engineering": evaluate_delivery_line(
                    seed_macro, "engineering"
                ),
                "paper": evaluate_delivery_line(seed_macro, "paper"),
                "scenario_contract": scenario_contract,
            }
        overall = mean_metrics(all_metrics)
        records.append(
            {
                "candidate": candidate,
                "overall": {
                    "metrics": overall,
                    "engineering": evaluate_delivery_line(
                        overall, "engineering"
                    ),
                    "paper": evaluate_delivery_line(overall, "paper"),
                },
                "per_seed": per_seed,
            }
        )
    selected = max(records, key=selection_key)
    baseline_metrics = baseline["overall"]["metrics"]
    payload: dict[str, Any] = {
        "schema_version": (
            "strict_v4_benign_autoencoder_warning_development_evaluation_v1"
        ),
        "state": "complete_adaptive_autoencoder_development",
        "algorithm": "caeos_xgboost_plus_benign_autoencoder_rescue",
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_path": str(completion_path),
            "completion_file_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
        "selected": selected,
        "records": records,
        "baseline": {
            "metrics": baseline_metrics,
            "selected_delta": {
                key: selected["overall"]["metrics"][key]
                - baseline_metrics[key]
                for key in baseline_metrics
            },
        },
        "resource_observed": completion["resource_observed"],
        "source_sha256": source_sha256,
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["trigger_fresh_unseen_seed_confirmation"] = bool(
        selected["overall"]["engineering"]["passed"]
        and all(
            value["engineering"]["passed"]
            for value in selected["per_seed"].values()
        )
    )
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_canonical(args.protocol, "autoencoder protocol")
    if args.output.resolve() != Path(protocol["result_path"]):
        raise ValueError("output does not match frozen result path")
    payload = build_evaluation(args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "engineering_passed": payload["selected"]["overall"][
                    "engineering"
                ]["passed"],
                "manifest_sha256": payload["manifest_sha256"],
                "metrics": payload["selected"]["overall"]["metrics"],
                "selected_candidate": payload["selected"]["candidate"],
                "trigger_fresh_unseen_seed_confirmation": payload[
                    "trigger_fresh_unseen_seed_confirmation"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

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


def build_evaluation(protocol_path: Path) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "binary protocol")
    parent_path = Path(protocol["parent_protocol"]["path"])
    source_completion_path = Path(protocol["source_completion"]["path"])
    completion_path = Path(protocol["completion_path"])
    baseline_path = Path(protocol["baseline_qualification"]["path"])
    parent = load_canonical(parent_path, "parent protocol")
    source_completion = load_canonical(
        source_completion_path, "source completion"
    )
    completion = load_canonical(completion_path, "binary completion")
    baseline = load_canonical(baseline_path, "baseline qualification")
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
        raise ValueError("binary CUDA effect execution is incomplete")
    project_root = Path(__file__).resolve().parent
    for name, expected_hash in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected_hash:
            raise ValueError(f"implementation hash mismatch: {name}")

    risk_name = protocol["open_set_evaluation"]["risk_name"]
    per_seed = {}
    all_metrics = []
    source_sha256 = {}
    engineering_count = 0
    paper_count = 0
    for seed in protocol["seeds"]:
        scenario_contract = {}
        seed_metrics = []
        seed_sources = {}
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
            binary_artifact = completion["task_artifacts"][identity]
            binary_dir = Path(binary_artifact["output_dir"])
            for name, expected_hash in binary_artifact[
                "artifact_sha256"
            ].items():
                if file_hash(binary_dir / name) != expected_hash:
                    raise ValueError(
                        f"binary artifact hash mismatch: {identity}/{name}"
                    )
            with np.load(
                binary_dir / "scores.npz", allow_pickle=False
            ) as scores:
                validation_attack_probability = np.asarray(
                    scores["validation_attack_probability"],
                    dtype=np.float64,
                )
                validation_labels = np.asarray(
                    scores["validation_labels"], dtype=np.int64
                )
                test_attack_probability = np.asarray(
                    scores["test_attack_probability"], dtype=np.float64
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
                raise ValueError(f"binary split arrays differ: {identity}")
            benign_index = int(arrays["benign_index"])
            calibration = calibrate_threshold(
                validation_attack_probability,
                np.full(validation_labels.shape, benign_index, dtype=np.int64),
                validation_labels,
                benign_index,
                float(
                    protocol["training"][
                        "validation_benign_fpr_budget"
                    ]
                ),
            )
            if not calibration["feasible"]:
                raise ValueError(f"infeasible binary threshold: {identity}")
            risk_tail = arrays["risk_tails"][risk_name]
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
            validation_attack = validation_labels != benign_index
            open_threshold = upper_tail_threshold(
                validation_open[validation_attack],
                float(protocol["open_set_evaluation"]["open_budget"]),
            )
            predicted_alert = (
                test_attack_probability >= float(calibration["threshold"])
            )
            predicted_unknown = predicted_alert & (
                test_open >= open_threshold
            )
            metrics = contract_metrics(
                operational_metrics(
                    predicted_alert=predicted_alert,
                    predicted_unknown=predicted_unknown,
                    type_prediction=arrays["type_prediction"],
                    test_labels=test_labels,
                    test_unknown=test_unknown,
                    benign_index=benign_index,
                )
            )
            engineering = evaluate_delivery_line(metrics, "engineering")
            paper = evaluate_delivery_line(metrics, "paper")
            engineering_count += int(engineering["passed"])
            paper_count += int(paper["passed"])
            scenario_contract[scenario] = {
                "metrics": metrics,
                "engineering": engineering,
                "paper": paper,
                "alert_threshold": float(calibration["threshold"]),
                "open_threshold": float(open_threshold),
            }
            seed_metrics.append(metrics)
            all_metrics.append(metrics)
            seed_sources[scenario] = {
                **hashes,
                "multiclass_metrics": source_artifact["metrics_sha256"],
                "binary_metrics": binary_artifact["artifact_sha256"][
                    "metrics.json"
                ],
                "binary_scores": binary_artifact["artifact_sha256"][
                    "scores.npz"
                ],
            }
        macro = mean_metrics(seed_metrics)
        per_seed[str(seed)] = {
            "metrics": macro,
            "engineering": evaluate_delivery_line(macro, "engineering"),
            "paper": evaluate_delivery_line(macro, "paper"),
            "scenario_contract": scenario_contract,
        }
        source_sha256[str(seed)] = seed_sources
    overall = mean_metrics(all_metrics)
    baseline_metrics = baseline["overall"]["metrics"]
    payload: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fine_binary_warning_development_evaluation_v1"
        ),
        "state": "complete_adaptive_binary_development",
        "algorithm": "caeos_hierarchical_binary_warning_head",
        "binding": {
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_path": str(completion_path),
            "completion_file_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
        "per_seed": per_seed,
        "overall": {
            "metrics": overall,
            "engineering": evaluate_delivery_line(overall, "engineering"),
            "paper": evaluate_delivery_line(overall, "paper"),
        },
        "baseline": {
            "metrics": baseline_metrics,
            "delta": {
                key: overall[key] - baseline_metrics[key] for key in overall
            },
        },
        "scenario_pass_counts": {
            "engineering": engineering_count,
            "paper": paper_count,
            "total": len(protocol["seeds"]) * len(protocol["scenarios"]),
        },
        "resource_observed": completion["resource_observed"],
        "source_sha256": source_sha256,
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["trigger_fresh_unseen_seed_confirmation"] = bool(
        payload["overall"]["engineering"]["passed"]
        and all(
            result["engineering"]["passed"]
            for result in per_seed.values()
        )
    )
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_canonical(args.protocol, "binary protocol")
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
                "engineering_passed": payload["overall"]["engineering"][
                    "passed"
                ],
                "manifest_sha256": payload["manifest_sha256"],
                "metrics": payload["overall"]["metrics"],
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

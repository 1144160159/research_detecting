from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    evaluate_configuration,
    prepare_scenario,
)
from evaluate_strict_v4_hybrid_self_algorithm_development import mean_metrics
from project_contract import evaluate_delivery_line


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_canonical(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    declared = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")
    return value


def contract_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {
        "alert_accuracy": float(metrics["alert_accuracy"]),
        "alert_precision": float(metrics["alert_precision"]),
        "attack_recall": float(metrics["alert_recall"]),
        "benign_fpr": float(metrics["benign_fpr"]),
        "known_attack_type_accuracy": float(
            metrics["known_attack_type_accuracy"]
        ),
        "unknown_attack_alert_recall": float(
            metrics["unknown_attack_alert_recall"]
        ),
        "unknown_label_recall": float(metrics["unknown_attack_recall"]),
    }


def verify_xgboost_source(
    completion: dict[str, Any],
    *,
    identity: str,
    task_dir: Path,
) -> None:
    expected = completion["xgboost_task_artifacts"].get(identity)
    if expected is None:
        raise ValueError(f"missing XGBoost completion artifact: {identity}")
    observed = {
        "metrics": file_hash(task_dir / "metrics.json"),
        "scores": file_hash(task_dir / "scores.npz"),
        "gpu_execution": file_hash(task_dir / "gpu_execution.json"),
    }
    if (
        observed["metrics"] != expected["metrics_sha256"]
        or observed["scores"] != expected["scores_sha256"]
        or observed["gpu_execution"] != expected["gpu_execution_sha256"]
    ):
        raise ValueError(f"XGBoost source hash mismatch: {identity}")


def build_qualification(
    protocol_path: Path, completion_path: Path
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    completion_path = completion_path.resolve()
    protocol = load_canonical(protocol_path, "protocol")
    completion = load_canonical(completion_path, "completion")
    effect_execution_passed = (
        completion.get("return_codes", {}).get("neural_matrix") == 0
        and completion.get("return_codes", {}).get("xgboost_cuda_batch") == 0
        and completion.get("task_coverage", {}).get("complete") is True
        and completion.get("all_tasks_confirmed_cuda", {}).get("neural")
        is True
        and completion.get("all_tasks_confirmed_cuda", {}).get("xgboost")
        is True
    )
    if not effect_execution_passed:
        raise ValueError("complete CUDA effect execution did not pass")
    if (
        completion.get("protocol", {}).get("manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("completion is not bound to protocol")

    configuration = protocol["selected_configuration"]
    xgboost_root = Path(protocol["xgboost_root"])
    per_seed = {}
    neural_sha256 = {}
    all_scenario_engineering_pass = True
    all_scenario_paper_pass = True
    for seed in protocol["seeds"]:
        prepared = {}
        seed_sha256 = {}
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            xgboost_dir = xgboost_root / identity
            verify_xgboost_source(
                completion,
                identity=identity,
                task_dir=xgboost_dir,
            )
            artifact = completion["neural_task_artifacts"].get(identity)
            if artifact is None:
                raise ValueError(f"missing completion artifact: {identity}")
            neural_dir = Path(artifact["task_dir"])
            if neural_dir.name != f"{identity}_mlp":
                raise ValueError(
                    f"unexpected neural task directory for {identity}"
                )
            observed_neural = {
                "metrics": file_hash(neural_dir / "metrics.json"),
                "scores": file_hash(neural_dir / "scores.npz"),
            }
            if (
                observed_neural["metrics"] != artifact["metrics_sha256"]
                or observed_neural["scores"] != artifact["scores_sha256"]
            ):
                raise ValueError(f"neural source hash mismatch: {identity}")
            arrays, hashes = prepare_scenario(
                neural_dir, xgboost_dir, (configuration["risk_name"],)
            )
            prepared[scenario] = arrays
            seed_sha256[scenario] = hashes

        result = evaluate_configuration(prepared, configuration)
        scenario_contract = {}
        for scenario, scenario_result in result["per_scenario"].items():
            observed = contract_metrics(scenario_result["metrics"])
            engineering = evaluate_delivery_line(observed, "engineering")
            paper = evaluate_delivery_line(observed, "paper")
            scenario_contract[scenario] = {
                "metrics": observed,
                "engineering": engineering,
                "paper": paper,
            }
            all_scenario_engineering_pass &= bool(engineering["passed"])
            all_scenario_paper_pass &= bool(paper["passed"])
        observed_macro = contract_metrics(result["macro_mean"])
        per_seed[str(seed)] = {
            "metrics": observed_macro,
            "engineering": evaluate_delivery_line(
                observed_macro, "engineering"
            ),
            "paper": evaluate_delivery_line(observed_macro, "paper"),
            "scenario_contract": scenario_contract,
            "legacy_metric_view": result,
        }
        neural_sha256[str(seed)] = seed_sha256

    overall_metrics = mean_metrics(
        seed_result["metrics"] for seed_result in per_seed.values()
    )
    overall_engineering = evaluate_delivery_line(
        overall_metrics, "engineering"
    )
    overall_paper = evaluate_delivery_line(overall_metrics, "paper")
    all_seed_engineering = all(
        seed_result["engineering"]["passed"]
        for seed_result in per_seed.values()
    )
    all_seed_paper = all(
        seed_result["paper"]["passed"] for seed_result in per_seed.values()
    )
    resource_gate_passed = (
        completion.get("resource_observed", {}).get(
            "minimum_mean_utilization_passed"
        )
        is True
    )
    qualification: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_qualification_v1"
        ),
        "state": (
            "complete_fresh_gpu_qualification"
            if resource_gate_passed
            else "complete_effect_evaluation_resource_gate_failed"
        ),
        "algorithm": protocol["algorithm"],
        "selected_configuration": configuration,
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
            "metrics": overall_metrics,
            "engineering": overall_engineering,
            "paper": overall_paper,
        },
        "qualification_gates": {
            "complete_cuda_effect_execution_passed": effect_execution_passed,
            "gpu_resource_minimum_passed": resource_gate_passed,
            "all_seed_engineering_point_estimates_pass": all_seed_engineering,
            "all_seed_paper_point_estimates_pass": all_seed_paper,
            "all_scenario_engineering_point_estimates_pass": (
                all_scenario_engineering_pass
            ),
            "all_scenario_paper_point_estimates_pass": all_scenario_paper_pass,
        },
        "source_sha256": {"neural_and_xgboost": neural_sha256},
        "claim_boundary": {
            "fresh_results_selected_nothing": True,
            "thresholds_use_known_only_validation": True,
            "three_seed_qualification_is_not_formal_confirmation": True,
            "confidence_acceptance_not_computed": True,
            "paper_multimodal_claim_not_authorized": True,
            "resource_gate_failure_does_not_invalidate_effect_artifacts": True,
        },
    }
    qualification["manifest_sha256"] = canonical_hash(qualification)
    return qualification


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    qualification = build_qualification(args.protocol, args.completion)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            qualification, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "engineering_point_pass": qualification[
                    "qualification_gates"
                ]["all_seed_engineering_point_estimates_pass"],
                "manifest_sha256": qualification["manifest_sha256"],
                "output": str(args.output.resolve()),
                "paper_point_pass": qualification["qualification_gates"][
                    "all_seed_paper_point_estimates_pass"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

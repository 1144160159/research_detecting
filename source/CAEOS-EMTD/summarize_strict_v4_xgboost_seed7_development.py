from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from train_strict_v4_xgboost_warning_task import operational_metrics


CORE_METRICS = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
)


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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], label: str) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")


def basic_gate(metrics: dict[str, float]) -> bool:
    return (
        metrics["alert_accuracy"] >= 0.95
        and metrics["alert_precision"] >= 0.95
        and metrics["alert_recall"] >= 0.95
        and metrics["benign_fpr"] < 0.05
        and metrics["known_attack_type_accuracy"] >= 0.95
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol = load(args.protocol.resolve())
    verify_canonical(protocol, "development protocol")
    run_root = project_root / protocol["run_root"] / "cicids2017"
    task_results: dict[str, dict[str, Any]] = {}
    task_metric_sha256: dict[str, str] = {}
    for scenario in protocol["scenarios"]:
        task_dir = run_root / f"{scenario}_seed{protocol['seed']}"
        metrics_path = task_dir / "metrics.json"
        scores_path = task_dir / "scores.npz"
        metrics_payload = load(metrics_path)
        verify_canonical(metrics_payload, str(metrics_path))
        known_class_names = metrics_payload["known_class_names"]
        benign_index = known_class_names.index("Benign")
        with np.load(scores_path, allow_pickle=False) as scores:
            validation_probability = np.asarray(
                scores["validation_probability"], dtype=np.float64
            )
            validation_labels = np.asarray(
                scores["validation_labels"], dtype=np.int64
            )
            test_probability = np.asarray(
                scores["test_probability"], dtype=np.float64
            )
            test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
            test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
        budget_results: dict[str, Any] = {}
        for budget in protocol["threshold_development"][
            "validation_benign_fpr_budgets"
        ]:
            calibration = calibrate_threshold(
                1.0 - validation_probability[:, benign_index],
                np.full(validation_labels.shape, benign_index, dtype=np.int64),
                validation_labels,
                benign_index,
                float(budget),
            )
            metrics = operational_metrics(
                test_probability=test_probability,
                test_labels=test_labels,
                test_unknown=test_unknown,
                benign_index=benign_index,
                alert_threshold=float(calibration["threshold"]),
            )
            budget_results[f"{float(budget):.4f}"] = {
                "calibration": calibration,
                "operational_metrics": metrics,
                "basic_warning_95_5_gate": basic_gate(metrics),
            }
        task_results[scenario] = budget_results
        task_metric_sha256[scenario] = file_hash(metrics_path)

    aggregate_by_budget: dict[str, Any] = {}
    for budget in protocol["threshold_development"][
        "validation_benign_fpr_budgets"
    ]:
        key = f"{float(budget):.4f}"
        scenario_metrics = [
            task_results[scenario][key]["operational_metrics"]
            for scenario in protocol["scenarios"]
        ]
        mean_metrics = {
            metric: float(np.mean([values[metric] for values in scenario_metrics]))
            for metric in CORE_METRICS
        }
        pass_count = sum(
            bool(task_results[scenario][key]["basic_warning_95_5_gate"])
            for scenario in protocol["scenarios"]
        )
        aggregate_by_budget[key] = {
            "macro_mean_operational_metrics": mean_metrics,
            "macro_mean_basic_warning_95_5_gate": basic_gate(mean_metrics),
            "scenario_basic_gate_pass_count": pass_count,
            "scenario_count": len(protocol["scenarios"]),
            "all_scenarios_pass_basic_warning_95_5_gate": (
                pass_count == len(protocol["scenarios"])
            ),
        }

    summary: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_seed7_development_summary_v1",
        "state": "complete_development_only",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "task_count": len(task_results),
        "expected_task_count": protocol["expected_task_count"],
        "aggregate_by_validation_benign_fpr_budget": aggregate_by_budget,
        "task_results": task_results,
        "task_metrics_sha256": task_metric_sha256,
        "claim_boundary": protocol["claim_boundary"],
        "selection_rule": {
            "eligible_budget_requires_all_scenarios_basic_gate": True,
            "no_eligible_budget_means_data_or_model_optimization_is_required": True,
            "fresh_three_seed_confirmation_remains_mandatory": True,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

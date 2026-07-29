#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np


METRICS = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "alert_f1",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_recall",
    "unknown_label_precision",
    "three_level_accuracy",
    "base_benign_fpr",
    "risk_incremental_benign_fpr",
    "base_attack_recall",
    "risk_incremental_attack_recall",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(payload: Dict[str, Any]) -> str:
    canonical = dict(payload)
    canonical.pop("manifest_sha256", None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _ratio(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    denominator = precision + recall
    return float(2.0 * precision * recall / denominator) if denominator else 0.0


def _mean(records: Iterable[Dict[str, Any]], key: str) -> float:
    values = [float(record["operational_metrics"][key]) for record in records]
    return float(np.mean(values))


def audit_task(task_dir: Path) -> Dict[str, Any]:
    paths = {
        "metrics": task_dir / "metrics.json",
        "scores": task_dir / "scores.npz",
        "provenance": task_dir / "provenance.json",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{task_dir}: missing {missing}")

    with paths["metrics"].open("r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    with paths["provenance"].open("r", encoding="utf-8") as handle:
        provenance = json.load(handle)
    with np.load(paths["scores"], allow_pickle=False) as scores:
        labels = np.asarray(scores["test_labels"], dtype=np.int64)
        unknown = np.asarray(scores["test_unknown"], dtype=bool)
        prediction = np.asarray(scores["test_prediction"], dtype=np.int64)
        selected_risk = str(metrics["selected_risk"])
        risk_key = f"test_{selected_risk}"
        if risk_key not in scores.files:
            raise KeyError(f"{task_dir}: missing {risk_key}")
        risk = np.asarray(scores[risk_key], dtype=np.float64)

    if not (labels.shape == unknown.shape == prediction.shape == risk.shape):
        raise ValueError(f"{task_dir}: score array shape mismatch")
    if labels.ndim != 1 or labels.size == 0:
        raise ValueError(f"{task_dir}: invalid test arrays")
    if not np.isfinite(risk).all():
        raise ValueError(f"{task_dir}: non-finite selected risk")

    known_class_names = [str(value) for value in metrics["known_class_names"]]
    benign_name = str(metrics["arguments"]["benign_class"])
    if benign_name not in known_class_names:
        raise ValueError(f"{task_dir}: benign class is absent from known classes")
    if benign_name in {str(value) for value in metrics["unknown_classes"]}:
        raise ValueError(f"{task_dir}: benign class cannot be held out as unknown")
    benign_index = known_class_names.index(benign_name)

    threshold = float(metrics["validation_thresholds"][selected_risk])
    rejected = risk >= threshold
    reported = metrics["selected_report"]
    known = ~unknown
    known_acceptance = _ratio(int((~rejected & known).sum()), int(known.sum()))
    unknown_rejection = _ratio(int((rejected & unknown).sum()), int(unknown.sum()))
    if abs(known_acceptance - float(reported["known_acceptance_rate"])) > 1e-12:
        raise ValueError(f"{task_dir}: known acceptance does not reproduce")
    if abs(unknown_rejection - float(reported["unknown_rejection_rate"])) > 1e-12:
        raise ValueError(f"{task_dir}: unknown rejection does not reproduce")

    actual_attack = unknown | (labels != benign_index)
    base_alert = prediction != benign_index
    predicted_alert = rejected | base_alert
    true_positive = int((predicted_alert & actual_attack).sum())
    false_positive = int((predicted_alert & ~actual_attack).sum())
    true_negative = int((~predicted_alert & ~actual_attack).sum())
    false_negative = int((~predicted_alert & actual_attack).sum())

    alert_precision = _ratio(true_positive, true_positive + false_positive)
    alert_recall = _ratio(true_positive, true_positive + false_negative)
    alert_accuracy = _ratio(true_positive + true_negative, labels.size)

    known_attack = known & (labels != benign_index)
    correctly_typed_known_attack = known_attack & ~rejected & (prediction == labels)
    unknown_label_precision = _ratio(int((rejected & unknown).sum()), int(rejected.sum()))
    three_level_correct = (
        (~actual_attack & ~predicted_alert)
        | correctly_typed_known_attack
        | (unknown & rejected)
    )
    benign_count = int((~actual_attack).sum())
    attack_count = int(actual_attack.sum())
    base_benign_false_alert = int((base_alert & ~actual_attack).sum())
    incremental_benign_false_alert = int(
        (rejected & ~base_alert & ~actual_attack).sum()
    )
    base_detected_attack = int((base_alert & actual_attack).sum())
    incremental_detected_attack = int((rejected & ~base_alert & actual_attack).sum())

    operational_metrics = {
        "alert_accuracy": alert_accuracy,
        "alert_precision": alert_precision,
        "alert_recall": alert_recall,
        "alert_f1": _f1(alert_precision, alert_recall),
        "benign_fpr": _ratio(false_positive, false_positive + true_negative),
        "known_attack_type_accuracy": _ratio(
            int(correctly_typed_known_attack.sum()), int(known_attack.sum())
        ),
        "unknown_attack_recall": unknown_rejection,
        "unknown_label_precision": unknown_label_precision,
        "three_level_accuracy": _ratio(int(three_level_correct.sum()), labels.size),
        "base_benign_fpr": _ratio(base_benign_false_alert, benign_count),
        "risk_incremental_benign_fpr": _ratio(
            incremental_benign_false_alert, benign_count
        ),
        "base_attack_recall": _ratio(base_detected_attack, attack_count),
        "risk_incremental_attack_recall": _ratio(
            incremental_detected_attack, attack_count
        ),
    }
    basic_gate = (
        operational_metrics["alert_accuracy"] >= 0.95
        and operational_metrics["benign_fpr"] < 0.05
    )
    full_gate = (
        basic_gate
        and operational_metrics["alert_precision"] >= 0.95
        and operational_metrics["alert_recall"] >= 0.95
        and operational_metrics["known_attack_type_accuracy"] >= 0.95
        and operational_metrics["unknown_attack_recall"] >= 0.95
    )

    task = provenance["task"]
    if task_dir.parent.name != str(task["suite"]):
        raise ValueError(f"{task_dir}: suite identity mismatch")
    return {
        "suite": str(task["suite"]),
        "scenario": str(task["scenario"]),
        "seed": int(task["seed"]),
        "task_directory": task_dir.name,
        "selected_risk": selected_risk,
        "selected_threshold": threshold,
        "sample_counts": {
            "total": int(labels.size),
            "benign": int((~actual_attack).sum()),
            "known_attack": int(known_attack.sum()),
            "unknown_attack": int(unknown.sum()),
        },
        "warning_confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
        "operational_metrics": operational_metrics,
        "gates": {
            "alert_accuracy_at_least_95_percent": alert_accuracy >= 0.95,
            "benign_fpr_below_5_percent": operational_metrics["benign_fpr"] < 0.05,
            "basic_95_5_gate": basic_gate,
            "full_known_unknown_95_5_gate": full_gate,
        },
        "source_sha256": {name: _sha256(path) for name, path in paths.items()},
        "source_open_set_metrics": {
            key: float(reported[key])
            for key in (
                "known_accuracy",
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            )
        },
    }


def build_audit(run_root: Path) -> Dict[str, Any]:
    task_dirs = sorted(
        path
        for suite_dir in run_root.iterdir()
        if suite_dir.is_dir()
        for path in suite_dir.iterdir()
        if path.is_dir() and (path / "metrics.json").is_file()
    )
    records = [audit_task(path) for path in task_dirs]
    if not records:
        raise ValueError(f"{run_root}: no complete task directories")

    by_suite: Dict[str, Any] = {}
    for suite in sorted({record["suite"] for record in records}):
        suite_records = [record for record in records if record["suite"] == suite]
        by_suite[suite] = {
            "scenario_count": len(suite_records),
            "mean": {key: _mean(suite_records, key) for key in METRICS},
            "basic_95_5_pass_count": sum(
                bool(record["gates"]["basic_95_5_gate"]) for record in suite_records
            ),
            "full_known_unknown_95_5_pass_count": sum(
                bool(record["gates"]["full_known_unknown_95_5_gate"])
                for record in suite_records
            ),
        }

    suite_names = sorted(by_suite)
    overall = {
        key: float(np.mean([by_suite[suite]["mean"][key] for suite in suite_names]))
        for key in METRICS
    }
    payload: Dict[str, Any] = {
        "schema_version": "strict_v4_operational_warning_metrics_audit_v1",
        "state": "complete_read_only_diagnostic",
        "claim_boundary": {
            "uses_existing_frozen_test_predictions_and_risk": True,
            "performs_no_training_or_threshold_selection": True,
            "test_labels_used_for_final_metrics_only": True,
            "diagnostic_does_not_define_a_post_hoc_core_benchmark": True,
            "strict_v4_unknown_fpr95_is_not_benign_alert_fpr": True,
        },
        "definitions": {
            "actual_attack": "held-out unknown malicious or known label other than benign",
            "predicted_alert": "known prediction other than benign or open-set rejection",
            "base_benign_fpr": "benign predicted as a known attack before open-set rejection",
            "risk_incremental_benign_fpr": (
                "benign predicted as benign but converted to an alert by rejection"
            ),
            "known_attack_type_correct": "known malicious accepted and predicted as its exact known class",
            "unknown_attack_detected": "held-out malicious rejected as unknown",
            "basic_95_5_gate": "alert_accuracy >= 0.95 and benign_fpr < 0.05",
            "full_known_unknown_95_5_gate": (
                "basic gate plus alert_precision, alert_recall, known_attack_type_accuracy, "
                "and unknown_attack_recall all >= 0.95"
            ),
        },
        "run_root": str(run_root.resolve()),
        "suite_count": len(suite_names),
        "scenario_count": len(records),
        "by_suite": by_suite,
        "suite_equal_mean": overall,
        "scenario_gate_counts": {
            "alert_accuracy_at_least_95_percent": sum(
                bool(record["gates"]["alert_accuracy_at_least_95_percent"])
                for record in records
            ),
            "benign_fpr_below_5_percent": sum(
                bool(record["gates"]["benign_fpr_below_5_percent"])
                for record in records
            ),
            "basic_95_5_gate": sum(
                bool(record["gates"]["basic_95_5_gate"]) for record in records
            ),
            "full_known_unknown_95_5_gate": sum(
                bool(record["gates"]["full_known_unknown_95_5_gate"])
                for record in records
            ),
        },
        "records": records,
    }
    payload["manifest_sha256"] = _canonical_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build_audit(args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "scenario_count": payload["scenario_count"],
                "suite_count": payload["suite_count"],
                "scenario_gate_counts": payload["scenario_gate_counts"],
                "output": str(args.output.resolve()),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

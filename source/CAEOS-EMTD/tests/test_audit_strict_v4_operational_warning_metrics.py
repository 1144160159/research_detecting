import json
from pathlib import Path

import numpy as np

from audit_strict_v4_operational_warning_metrics import audit_task, build_audit


def _write_task(root: Path, suite: str, task: str) -> Path:
    task_dir = root / suite / task
    task_dir.mkdir(parents=True)
    labels = np.array([0, 0, 1, 1, -1, -1], dtype=np.int64)
    unknown = np.array([False, False, False, False, True, True])
    prediction = np.array([0, 0, 1, 1, 0, 1], dtype=np.int64)
    risk = np.array([0.1, 0.2, 0.1, 0.2, 0.9, 0.8], dtype=np.float64)
    np.savez(
        task_dir / "scores.npz",
        test_labels=labels,
        test_unknown=unknown,
        test_prediction=prediction,
        test_selected=risk,
    )
    metrics = {
        "known_class_names": ["Benign", "Attack"],
        "unknown_classes": ["HeldOutAttack"],
        "arguments": {"benign_class": "Benign"},
        "selected_risk": "selected",
        "validation_thresholds": {"selected": 0.5},
        "selected_report": {
            "known_acceptance_rate": 1.0,
            "unknown_rejection_rate": 1.0,
            "known_accuracy": 1.0,
            "known_macro_f1": 1.0,
            "unknown_auroc": 1.0,
            "unknown_aupr": 1.0,
            "unknown_fpr95": 0.0,
            "oscr": 1.0,
        },
    }
    (task_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    provenance = {
        "task": {
            "suite": suite,
            "scenario": task.removesuffix("_seed7"),
            "seed": 7,
        }
    }
    (task_dir / "provenance.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )
    return task_dir


def test_audit_task_reconstructs_hierarchical_warning_metrics(tmp_path: Path) -> None:
    record = audit_task(_write_task(tmp_path, "suite_a", "attack_seed7"))
    assert record["operational_metrics"]["alert_accuracy"] == 1.0
    assert record["operational_metrics"]["alert_precision"] == 1.0
    assert record["operational_metrics"]["alert_recall"] == 1.0
    assert record["operational_metrics"]["benign_fpr"] == 0.0
    assert record["operational_metrics"]["known_attack_type_accuracy"] == 1.0
    assert record["operational_metrics"]["unknown_attack_recall"] == 1.0
    assert record["operational_metrics"]["base_benign_fpr"] == 0.0
    assert record["operational_metrics"]["risk_incremental_benign_fpr"] == 0.0
    assert record["operational_metrics"]["base_attack_recall"] == 0.75
    assert record["operational_metrics"]["risk_incremental_attack_recall"] == 0.25
    assert record["gates"]["basic_95_5_gate"] is True
    assert record["gates"]["full_known_unknown_95_5_gate"] is True


def test_build_audit_uses_suite_equal_aggregation(tmp_path: Path) -> None:
    _write_task(tmp_path, "suite_a", "attack_a_seed7")
    _write_task(tmp_path, "suite_b", "attack_b_seed7")
    audit = build_audit(tmp_path)
    assert audit["suite_count"] == 2
    assert audit["scenario_count"] == 2
    assert audit["suite_equal_mean"]["alert_accuracy"] == 1.0
    assert audit["scenario_gate_counts"]["basic_95_5_gate"] == 2
    assert len(audit["manifest_sha256"]) == 64

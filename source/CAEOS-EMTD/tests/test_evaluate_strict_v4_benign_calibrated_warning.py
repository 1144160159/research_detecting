import json
from pathlib import Path

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import (
    _aggregate_gates,
    calibrate_threshold,
    evaluate_task,
)


def test_calibrate_threshold_respects_empirical_benign_budget() -> None:
    risk = np.array([0.1, 0.2, 0.3, 0.4, 0.9, 0.8], dtype=np.float64)
    prediction = np.array([0, 0, 0, 0, 1, 1], dtype=np.int64)
    labels = np.array([0, 0, 0, 0, 1, 1], dtype=np.int64)
    result = calibrate_threshold(risk, prediction, labels, 0, 0.25)
    assert result["feasible"] is True
    assert result["achieved_validation_benign_fpr"] <= 0.25
    assert int((risk[:4] >= result["threshold"]).sum()) <= 1


def test_calibrate_threshold_fails_closed_when_base_fpr_exceeds_budget() -> None:
    risk = np.array([0.1, 0.2, 0.9, 0.8], dtype=np.float64)
    prediction = np.array([1, 0, 1, 1], dtype=np.int64)
    labels = np.array([0, 0, 1, 1], dtype=np.int64)
    result = calibrate_threshold(risk, prediction, labels, 0, 0.1)
    assert result["feasible"] is False
    assert np.isinf(result["threshold"])
    assert result["base_false_alert_count"] == 1


def test_hierarchical_probability_separates_alert_and_unknown_typing(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "scenario_seed7"
    task_dir.mkdir()
    metrics = {
        "known_class_names": ["Benign", "AttackA", "AttackB"],
        "selected_risk": "pairwise",
        "validation_thresholds": {"pairwise": 0.8},
        "arguments": {"benign_class": "Benign"},
    }
    provenance = {
        "task": {"suite": "pilot", "scenario": "attack_b", "seed": 7}
    }
    (task_dir / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    (task_dir / "provenance.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )

    validation_probability = np.array(
        [
            [0.99, 0.005, 0.005],
            [0.97, 0.02, 0.01],
            [0.10, 0.80, 0.10],
            [0.20, 0.70, 0.10],
        ],
        dtype=np.float64,
    )
    test_probability = np.array(
        [
            [0.98, 0.01, 0.01],
            [0.10, 0.85, 0.05],
            [0.20, 0.60, 0.20],
        ],
        dtype=np.float64,
    )
    test_prediction = test_probability.argmax(axis=1)
    np.savez(
        task_dir / "scores.npz",
        validation_labels=np.array([0, 0, 1, 1], dtype=np.int64),
        test_labels=np.array([0, 1, 2], dtype=np.int64),
        test_unknown=np.array([False, False, True]),
        test_prediction=test_prediction,
    )
    np.savez(
        task_dir / "evidence_package.npz",
        selected_risk_name=np.array("pairwise"),
        validation_selected_risk=np.array([0.1, 0.2, 0.2, 0.3]),
        test_selected_risk=np.array([0.1, 0.2, 0.9]),
        validation_final_probability=validation_probability,
        test_final_probability=test_probability,
        test_known_prediction=test_prediction,
        known_class_names=np.array(["Benign", "AttackA", "AttackB"]),
    )

    result = evaluate_task(
        task_dir, benign_fpr_budget=0.04, alert_mode="hierarchical_probability"
    )

    assert result["calibration"]["achieved_validation_benign_fpr"] == 0.0
    assert result["open_set_threshold"] == 0.8
    assert result["operational_metrics"]["alert_accuracy"] == 1.0
    assert result["operational_metrics"]["benign_fpr"] == 0.0
    assert result["operational_metrics"]["known_attack_type_accuracy"] == 1.0
    assert result["operational_metrics"]["unknown_attack_alert_recall"] == 1.0
    assert result["operational_metrics"]["unknown_attack_recall"] == 1.0


def test_basic_gate_includes_known_attack_type_accuracy() -> None:
    mean = {
        "alert_accuracy": 0.99,
        "alert_precision": 0.99,
        "alert_recall": 0.99,
        "alert_f1": 0.99,
        "benign_fpr": 0.01,
        "known_attack_type_accuracy": 0.94,
        "unknown_attack_alert_recall": 0.99,
        "unknown_attack_recall": 0.99,
        "unknown_label_precision": 0.99,
        "three_level_accuracy": 0.95,
    }
    gates = _aggregate_gates(mean)
    assert gates["known_attack_type_accuracy_at_least_95_percent"] is False
    assert gates["basic_warning_95_5_gate"] is False
    assert gates["full_known_unknown_95_5_gate"] is False

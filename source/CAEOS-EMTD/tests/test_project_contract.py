from __future__ import annotations

from pathlib import Path

import pytest

from project_contract import (
    evaluate_acceptance_gate,
    evaluate_delivery_line,
    load_delivery_contract,
)


def passing_metrics() -> dict[str, float]:
    return {
        "alert_accuracy": 0.97,
        "alert_precision": 0.98,
        "attack_recall": 0.96,
        "benign_fpr": 0.049,
        "known_attack_type_accuracy": 0.95,
        "unknown_attack_alert_recall": 0.95,
        "unknown_label_recall": 0.95,
    }


def test_contract_defines_two_lines_three_layers_and_two_gates() -> None:
    contract = load_delivery_contract()
    assert set(contract["delivery_lines"]) == {"engineering", "paper"}
    assert list(contract["metric_layers"]) == [
        "known_classification",
        "unknown_detection",
        "joint_open_set",
    ]
    assert set(contract["acceptance_gates"]) == {
        "engineering_safety_95_5",
        "paper_full_open_set_95_5",
    }
    source_root = Path(__file__).resolve().parents[1]
    assert all(
        (source_root / relative_path).is_file()
        for relative_path in contract["code_layout"]["canonical_entrypoints"]
    )


def test_engineering_gate_requires_unknown_attack_alert_recall() -> None:
    metrics = passing_metrics()
    metrics["unknown_attack_alert_recall"] = 0.949999
    report = evaluate_delivery_line(metrics, "engineering")
    assert report["passed"] is False
    assert report["checks"]["unknown_attack_alert_recall"]["passed"] is False


def test_paper_gate_adds_explicit_unknown_label_recall() -> None:
    metrics = passing_metrics()
    metrics.pop("unknown_label_recall")
    engineering = evaluate_delivery_line(metrics, "engineering")
    paper = evaluate_delivery_line(metrics, "paper")
    assert engineering["passed"] is True
    assert paper["passed"] is False
    assert paper["checks"]["unknown_label_recall"]["reason"] == "missing_metric"


def test_benign_fpr_boundary_is_strict() -> None:
    metrics = passing_metrics()
    metrics["benign_fpr"] = 0.05
    report = evaluate_acceptance_gate(
        metrics,
        "engineering_safety_95_5",
    )
    assert report["passed"] is False
    assert report["checks"]["benign_fpr"]["operator"] == "lt"


def test_rejects_out_of_range_metric() -> None:
    metrics = passing_metrics()
    metrics["alert_accuracy"] = 1.01
    with pytest.raises(ValueError, match=r"within \[0, 1\]"):
        evaluate_delivery_line(metrics, "engineering")

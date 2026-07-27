from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.pseudo_unknown_gated_continuous import (
    PAIRWISE_REFERENCE_RISK,
    PUG_RISK_NAME,
    PUG_SELECTION_NAME,
)
from evaluate_strict_v4_pug_confirmation import evaluate, load


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    PROJECT_ROOT
    / "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_task(
    candidate_root: Path,
    opendetect_root: Path,
    task: dict,
) -> None:
    suite = task["suite"]
    scenario = task["scenario"]
    seed = task["seed"]
    candidate = candidate_root / suite / f"{scenario}_seed{seed}"
    opendetect = (
        opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
    )
    candidate.mkdir(parents=True)
    opendetect.mkdir(parents=True)

    test_labels = np.asarray([0, 1, 0, 1, 0, 1, -1, -1, -1, -1])
    test_unknown = test_labels == -1
    test_prediction = np.asarray([0, 1, 0, 1, 1, 1, 0, 1, 0, 1])
    validation_pairwise = np.asarray([0.1, 0.2, 0.3, 0.4])
    test_pairwise = np.asarray(
        [0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 0.6, 0.7, 0.8, 0.9]
    )
    validation_pug = validation_pairwise.copy()
    test_pug = test_pairwise.copy()
    threshold = 0.5
    pairwise_report = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        test_prediction,
        test_pairwise,
        threshold,
    )
    pug_report = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        test_prediction,
        test_pug,
        threshold,
    )
    fingerprint = f"synthetic-{scenario}-{seed}"
    reports = {
        PAIRWISE_REFERENCE_RISK: pairwise_report,
        PUG_RISK_NAME: pug_report,
    }
    write_json(
        candidate / "metrics.json",
        {
            "risk_policy": "strict_v4_pug_confirmation_v1",
            "risk_selection": PUG_SELECTION_NAME,
            "selected_risk": PAIRWISE_REFERENCE_RISK,
            "selected_report": pairwise_report,
            "reports": reports,
            "validation_thresholds": {
                PAIRWISE_REFERENCE_RISK: threshold,
                PUG_RISK_NAME: threshold,
            },
            "split_metadata": {
                "split_fingerprint": {"combined": fingerprint}
            },
            "risk_selection_details": {
                "pug_continuous_outer_gate": {
                    "fold_count": 6,
                    "passes": False,
                    "checks": {"mean_fpr95_improvement": False},
                    "aggregates": {},
                    "selection_uses_unknown_or_test_labels": False,
                },
                "pairwise_base_selected_risk": PAIRWISE_REFERENCE_RISK,
                "pug_base_route_eligible": True,
                "pug_selected": False,
                "selected_risk": PAIRWISE_REFERENCE_RISK,
                "unknown_or_test_labels_used_for_selection": False,
            },
        },
    )
    np.savez_compressed(
        candidate / "scores.npz",
        test_labels=test_labels,
        test_unknown=test_unknown,
        test_prediction=test_prediction,
        **{
            f"validation_{PAIRWISE_REFERENCE_RISK}": validation_pairwise,
            f"test_{PAIRWISE_REFERENCE_RISK}": test_pairwise,
            f"validation_{PUG_RISK_NAME}": validation_pug,
            f"test_{PUG_RISK_NAME}": test_pug,
        },
    )
    np.savez_compressed(
        candidate / "evidence_package.npz",
        selected_risk_name=np.asarray(PAIRWISE_REFERENCE_RISK),
        selected_threshold=np.asarray(threshold),
        validation_selected_risk=validation_pairwise,
        test_selected_risk=test_pairwise,
        test_rejected=test_pairwise > threshold,
    )
    write_json(candidate / "provenance.json", {})

    opendetect_risk = test_pairwise.copy()
    opendetect_report = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        test_prediction,
        opendetect_risk,
        threshold,
    )
    write_json(
        opendetect / "metrics.json",
        {
            "reports": {"opendetect": opendetect_report},
            "selection_evidence": {
                "unknown_or_test_labels_used_for_fitting_or_selection": False
            },
            "split_metadata": {
                "split_fingerprint": {"combined": fingerprint}
            },
        },
    )
    np.savez_compressed(
        opendetect / "scores.npz",
        test_labels=test_labels,
        test_unknown=test_unknown,
        test_opendetect=opendetect_risk,
    )
    write_json(opendetect / "provenance.json", {})


def test_complete_evaluator_recomputes_all_18_paired_tasks(
    tmp_path: Path, monkeypatch
) -> None:
    protocol = load(PROTOCOL_PATH)
    candidate_root = tmp_path / "candidate"
    opendetect_root = tmp_path / "opendetect"
    for task in protocol["tasks"]:
        write_task(candidate_root, opendetect_root, task)
    monkeypatch.chdir(PROJECT_ROOT)

    result = evaluate(protocol, candidate_root, opendetect_root)

    assert result["task_count"] == 18
    assert len(result["artifact_sha256"]) == 126
    assert result["gate_checks"]["paired_task_count"] is True
    assert result["gate_checks"]["selection_isolation"] is True
    assert result["gate_checks"]["mean_fpr95_improvement"] is False
    assert result["decision"] == {
        "passes": False,
        "selected_method": "caeos_pairwise",
        "cross_suite_execution_admitted": False,
    }
    assert all(row["pug_selected"] is False for row in result["tasks"])

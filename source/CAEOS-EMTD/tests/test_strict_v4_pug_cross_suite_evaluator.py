from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.pseudo_unknown_gated_continuous import (
    PAIRWISE_REFERENCE_RISK,
    PUG_RISK_NAME,
    PUG_SELECTION_NAME,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_strict_v4_pug_cross_suite_confirmation import (
    create_task_record,
    evaluate_cross_task,
    select_task,
    validate_protocol,
)


def protocol():
    tasks = [
        {
            "suite": f"suite_{suite}",
            "scenario": f"scenario_{suite}_{scenario:02d}",
            "seed": seed,
        }
        for suite, count in enumerate([15, 15, 15, 15, 14, 14, 14])
        for scenario in range(count)
        for seed in [269, 271, 277]
    ]
    value = {
        "schema_version": (
            "strict_v4_pug_cross_suite_execution_protocol_v1"
        ),
        "state": "frozen_after_positive_pilot_before_cross_suite_execution",
        "execution_admitted": True,
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "expected_pairwise_pug_runs": 306,
            "expected_fresh_opendetect_runs": 306,
            "fresh_seeds": [269, 271, 277],
            "tasks": tasks,
        },
        "execution_controls": {
            "candidate_policy_name": "strict_v4_pug_confirmation_v1",
            "candidate_risk_selection": (
                "nested_pug_continuous_outer_min_p"
            ),
        },
        "output_contract": {
            "partial_metrics_must_not_be_aggregated": True,
        },
        "implementation_sha256": {},
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def row(task):
    metrics = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.8,
        "unknown_aupr": 0.7,
        "unknown_fpr95": 0.4,
        "oscr": 0.7,
    }
    return {
        **task,
        "group": "cross_suite",
        "pairwise_base_selected_risk": "cauchy_modality_support_union",
        "pug_selected_risk": "pug_continuous_outer_min_p",
        "pug_gate_passes": True,
        "pug_selected": True,
        "pairwise": metrics,
        "caeos_pug": metrics,
        "opendetect": metrics,
        "split_fingerprint": "fingerprint",
        "unknown_or_test_labels_used_for_selection": False,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_synthetic_task(
    candidate_root: Path,
    opendetect_root: Path,
    task: dict,
    *,
    opendetect_fingerprint_suffix: str = "",
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
    write_json(
        candidate / "metrics.json",
        {
            "risk_policy": "strict_v4_pug_confirmation_v1",
            "risk_selection": PUG_SELECTION_NAME,
            "selected_risk": PAIRWISE_REFERENCE_RISK,
            "selected_report": pairwise_report,
            "reports": {
                PAIRWISE_REFERENCE_RISK: pairwise_report,
                PUG_RISK_NAME: pug_report,
            },
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

    opendetect_report = evaluate_hybrid_open_set(
        test_labels,
        test_unknown,
        test_prediction,
        test_pairwise,
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
                "split_fingerprint": {
                    "combined": fingerprint + opendetect_fingerprint_suffix
                }
            },
        },
    )
    np.savez_compressed(
        opendetect / "scores.npz",
        test_labels=test_labels,
        test_unknown=test_unknown,
        test_opendetect=test_pairwise,
    )
    write_json(opendetect / "provenance.json", {})


def test_protocol_and_task_identity_are_frozen() -> None:
    value = protocol()
    validate_protocol(value, check_implementation=False)
    task = value["confirmation_universe"]["tasks"][0]

    assert (
        select_task(value, task["suite"], task["scenario"], task["seed"])
        == task
    )


def test_task_record_is_canonical_and_nonaggregated() -> None:
    value = protocol()
    task = value["confirmation_universe"]["tasks"][0]
    hashes = {
        f"artifact_{index}": f"{index + 1:064x}" for index in range(7)
    }
    record = create_task_record(
        protocol=value,
        task=task,
        row=row(task),
        artifact_sha256=hashes,
        protocol_file_sha256="8" * 64,
        evaluator_sha256="9" * 64,
    )

    assert record["task"] == task
    assert (
        record["claim_boundary"][
            "single_task_record_is_not_aggregated_effect"
        ]
        is True
    )
    assert record["manifest_sha256"] == canonical_hash(record)


def test_protocol_rejects_duplicate_task_identity() -> None:
    value = protocol()
    value = copy.deepcopy(value)
    value["confirmation_universe"]["tasks"][-1] = copy.deepcopy(
        value["confirmation_universe"]["tasks"][0]
    )
    value["manifest_sha256"] = canonical_hash(value)

    with pytest.raises(ValueError, match="universe drifted"):
        validate_protocol(value, check_implementation=False)


def test_record_rejects_wrong_artifact_count() -> None:
    value = protocol()
    task = value["confirmation_universe"]["tasks"][0]

    with pytest.raises(ValueError, match="seven"):
        create_task_record(
            protocol=value,
            task=task,
            row=row(task),
            artifact_sha256={"one": "1" * 64},
            protocol_file_sha256="8" * 64,
            evaluator_sha256="9" * 64,
        )


def test_record_rejects_selection_leakage_flag() -> None:
    value = protocol()
    task = value["confirmation_universe"]["tasks"][0]
    leaked = row(task)
    leaked["unknown_or_test_labels_used_for_selection"] = True

    with pytest.raises(ValueError, match="isolated"):
        create_task_record(
            protocol=value,
            task=task,
            row=leaked,
            artifact_sha256={
                f"artifact_{index}": f"{index + 1:064x}"
                for index in range(7)
            },
            protocol_file_sha256="8" * 64,
            evaluator_sha256="9" * 64,
        )


def test_evaluator_recomputes_single_complete_paired_task(
    tmp_path: Path,
) -> None:
    task = {
        "suite": "suite",
        "scenario": "scenario",
        "seed": 269,
    }
    candidate_root = tmp_path / "candidate"
    opendetect_root = tmp_path / "opendetect"
    write_synthetic_task(candidate_root, opendetect_root, task)

    result, hashes = evaluate_cross_task(
        task,
        candidate_root,
        opendetect_root,
        "strict_v4_pug_confirmation_v1",
    )

    assert result["pug_selected"] is False
    assert result["pairwise"] == result["caeos_pug"]
    assert result["unknown_or_test_labels_used_for_selection"] is False
    assert len(hashes) == 7


def test_evaluator_rejects_split_fingerprint_drift(
    tmp_path: Path,
) -> None:
    task = {
        "suite": "suite",
        "scenario": "scenario",
        "seed": 269,
    }
    candidate_root = tmp_path / "candidate"
    opendetect_root = tmp_path / "opendetect"
    write_synthetic_task(
        candidate_root,
        opendetect_root,
        task,
        opendetect_fingerprint_suffix="-drift",
    )

    with pytest.raises(ValueError, match="split fingerprint mismatch"):
        evaluate_cross_task(
            task,
            candidate_root,
            opendetect_root,
            "strict_v4_pug_confirmation_v1",
        )

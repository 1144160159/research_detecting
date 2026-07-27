from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_strict_v4_comp_cross_suite_confirmation import (
    create_task_record,
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
            "strict_v4_comp_cross_suite_execution_protocol_v1"
        ),
        "state": "frozen_after_positive_pilot_before_cross_suite_execution",
        "execution_admitted": True,
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "fresh_seeds": [269, 271, 277],
            "tasks": tasks,
        },
        "execution_controls": {
            "pairwise_policy_name": (
                "strict_v4_comp_cross_suite_pairwise_v1"
            )
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
        "route": "continuous_outer_min_p",
        "changed": True,
        "selected_risk_name": "cauchy_modality_support_union",
        "pairwise": metrics,
        "caeos_comp": metrics,
        "opendetect": metrics,
        "split_fingerprint": "fingerprint",
    }


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
    hashes = {f"artifact_{index}": f"{index + 1:064x}" for index in range(7)}
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
        record["claim_boundary"]["single_task_record_is_not_aggregated_effect"]
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

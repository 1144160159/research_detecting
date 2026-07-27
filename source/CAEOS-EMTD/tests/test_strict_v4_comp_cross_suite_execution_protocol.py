from __future__ import annotations

import copy

import pytest

from create_strict_v4_comp_cross_suite_design import (
    MAX_PER_CLASS,
    SEEDS,
    SUITE_SCENARIO_COUNTS,
)
from create_strict_v4_comp_cross_suite_execution_protocol import (
    REQUIRED_IMPLEMENTATION_KEYS,
    create_execution_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs(positive: bool = True):
    tasks = [
        {"suite": suite, "scenario": f"{suite}_{index:02d}", "seed": seed}
        for suite, count in SUITE_SCENARIO_COUNTS.items()
        for index in range(count)
        for seed in SEEDS
    ]
    design = {
        "schema_version": (
            "strict_v4_comp_cross_suite_confirmation_design_v1"
        ),
        "candidate": {"method": "caeos_comp"},
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "paired_task_count": 306,
            "fresh_seeds": SEEDS,
            "tasks": tasks,
        },
        "execution_controls": {"max_per_class_by_suite": MAX_PER_CLASS},
        "primary_statistics": {"aggregation": "seed_then_suite"},
        "admission_gate": {"all": True},
        "selection_policy": {"all": True},
    }
    design["manifest_sha256"] = canonical_hash(design)
    activation = canonical(
        "strict_v4_comp_cross_suite_activation_v1",
        state=(
            "positive_activation"
            if positive
            else "negative_not_required_retain_pairwise"
        ),
        pilot_decision_passes=positive,
        cross_suite_execution_admitted=positive,
        action=(
            "create_cross_suite_execution_protocol"
            if positive
            else "write_not_required_and_retain_pairwise"
        ),
        validation={"pilot_integrity_passes": True},
        input_manifest_sha256={
            "cross_suite_design": design["manifest_sha256"],
        },
    )
    return design, activation


def implementation():
    return {
        key: f"{index + 1:064x}"
        for index, key in enumerate(sorted(REQUIRED_IMPLEMENTATION_KEYS))
    }


def build(design, activation, counts=None):
    return create_execution_protocol(
        design=design,
        activation=activation,
        input_file_sha256={"design": "1" * 64, "activation": "2" * 64},
        implementation_sha256=implementation(),
        observed_output_counts=counts
        or {
            "task_metrics": 0,
            "summary": 0,
            "audit": 0,
            "completion_marker": 0,
        },
    )


def test_positive_activation_freezes_full_execution_protocol() -> None:
    design, activation = inputs(positive=True)
    protocol = build(design, activation)

    assert protocol is not None
    assert protocol["execution_admitted"] is True
    assert protocol["confirmation_universe"]["paired_task_count"] == 306
    assert protocol["output_contract"]["opendetect_task_count"] == 306
    assert set(protocol["implementation_sha256"]) == REQUIRED_IMPLEMENTATION_KEYS
    assert protocol["manifest_sha256"] == canonical_hash(protocol)


def test_negative_activation_returns_not_required() -> None:
    design, activation = inputs(positive=False)

    assert build(design, activation) is None


def test_protocol_rejects_any_existing_task_output() -> None:
    design, activation = inputs()
    with pytest.raises(ValueError, match="before task outputs"):
        build(
            design,
            activation,
            {
                "task_metrics": 1,
                "summary": 0,
                "audit": 0,
                "completion_marker": 0,
            },
        )


def test_protocol_rejects_incomplete_implementation() -> None:
    design, activation = inputs()
    values = implementation()
    values.pop(next(iter(values)))

    with pytest.raises(ValueError, match="complete frozen"):
        create_execution_protocol(
            design=design,
            activation=activation,
            input_file_sha256={"input": "1" * 64},
            implementation_sha256=values,
            observed_output_counts={"task_metrics": 0},
        )


def test_protocol_rejects_task_identity_drift() -> None:
    design, activation = inputs()
    design = copy.deepcopy(design)
    design["confirmation_universe"]["tasks"].pop()
    design["manifest_sha256"] = canonical_hash(design)
    activation["input_manifest_sha256"]["cross_suite_design"] = design[
        "manifest_sha256"
    ]
    activation["manifest_sha256"] = canonical_hash(activation)

    with pytest.raises(ValueError, match="full102x3"):
        build(design, activation)

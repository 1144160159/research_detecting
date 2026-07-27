from __future__ import annotations

import copy

import pytest

from create_strict_v4_comp_cross_suite_design import (
    SEEDS,
    SUITE_SCENARIO_COUNTS,
    create_design,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    rows = []
    for suite, count in SUITE_SCENARIO_COUNTS.items():
        rows.extend(
            {
                "suite": suite,
                "scenario": f"{suite}_scenario_{index:02d}",
                "seed": 7,
            }
            for index in range(count)
        )
    diagnosis = canonical(
        "strict_v4_pairwise_opendetect_fpr95_tail_audit_v1",
        passes=True,
        scenario_diagnostics=rows,
    )
    pilot = canonical(
        "strict_v4_comp_confirmation_protocol_v1",
        state="frozen_before_fresh_seed_execution",
        candidate={
            "method": "caeos_comp",
            "unknown_or_test_labels_used_for_routing": False,
            "unknown_or_test_labels_used_for_threshold": False,
        },
        pilot_scope={
            "paired_task_count": 18,
            "seeds": [139, 149, 163],
        },
        admission_gate={
            "passing_pilot_requires_cross_suite_expansion": True,
        },
    )
    return diagnosis, pilot


def build(diagnosis=None, pilot=None, counts=None):
    default_diagnosis, default_pilot = inputs()
    return create_design(
        diagnosis=diagnosis or default_diagnosis,
        pilot_protocol=pilot or default_pilot,
        input_file_sha256={"diagnosis": "1" * 64, "pilot": "2" * 64},
        implementation_sha256={"creator": "3" * 64},
        observed_output_counts=counts
        or {
            "activation_decision": 0,
            "execution_protocol": 0,
            "task_metrics": 0,
            "summary": 0,
            "audit": 0,
        },
    )


def test_design_freezes_full102x3_without_admitting_execution() -> None:
    design = build()
    universe = design["confirmation_universe"]

    assert SEEDS == [269, 271, 277]
    assert not set(SEEDS) & {7, 139, 149, 163}
    assert universe["suite_count"] == 7
    assert universe["scenario_count"] == 102
    assert universe["paired_task_count"] == 306
    assert len(universe["tasks"]) == 306
    assert len(
        {
            (task["suite"], task["scenario"], task["seed"])
            for task in universe["tasks"]
        }
    ) == 306
    assert design["execution_admitted_at_freeze"] is False
    assert design["claim_boundary"]["pilot_partial_metrics_are_not_read"] is True
    assert design["manifest_sha256"] == canonical_hash(design)


def test_design_rejects_any_result_before_freeze() -> None:
    with pytest.raises(ValueError, match="before result outputs"):
        build(
            counts={
                "activation_decision": 0,
                "execution_protocol": 0,
                "task_metrics": 1,
                "summary": 0,
                "audit": 0,
            }
        )


def test_design_rejects_scenario_universe_drift() -> None:
    diagnosis, pilot = inputs()
    diagnosis = copy.deepcopy(diagnosis)
    diagnosis["scenario_diagnostics"].pop()
    diagnosis["manifest_sha256"] = canonical_hash(diagnosis)

    with pytest.raises(ValueError, match="exactly 102"):
        build(diagnosis=diagnosis, pilot=pilot)


def test_design_rejects_pilot_without_cross_suite_requirement() -> None:
    diagnosis, pilot = inputs()
    pilot = copy.deepcopy(pilot)
    pilot["admission_gate"][
        "passing_pilot_requires_cross_suite_expansion"
    ] = False
    pilot["manifest_sha256"] = canonical_hash(pilot)

    with pytest.raises(ValueError, match="pilot boundary"):
        build(diagnosis=diagnosis, pilot=pilot)

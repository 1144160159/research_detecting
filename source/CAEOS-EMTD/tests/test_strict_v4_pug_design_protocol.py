from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pug_design_protocol import (
    DEVELOPMENT_SCENARIOS,
    DEVELOPMENT_SEEDS,
    FRESH_SCENARIOS,
    FRESH_SEEDS,
    RESERVED_CROSS_SUITE_SEEDS,
    create_design,
)


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    selected = set(
        FRESH_SCENARIOS["stress"] + FRESH_SCENARIOS["control"]
    )
    rows = []
    for index in range(32):
        scenario = (
            list(selected)[index]
            if index < len(selected)
            else f"other_{index:02d}"
        )
        rows.append(
            {
                "suite": "cic_iot2023",
                "scenario": scenario,
                "outcome_vs_opendetect": (
                    "loss"
                    if scenario in FRESH_SCENARIOS["stress"]
                    else "win"
                ),
                "pairwise_plateau": {
                    "minimum_plateau_explains_fpr95_one": (
                        scenario in FRESH_SCENARIOS["stress"]
                    )
                },
            }
        )
    rows.extend(
        {
            "suite": "other",
            "scenario": f"other_suite_{index:02d}",
        }
        for index in range(70)
    )
    failure = canonical(
        "strict_v4_comp_confirmation_failure_audit_v1",
        state="posthoc_development_diagnosis_complete",
        source_decision={
            "passes": False,
            "pairwise_remains_incumbent": True,
        },
        diagnostics={
            "development_feasible_gate_count": 0,
            "best_development_gate": None,
        },
    )
    confirmation = canonical(
        "strict_v4_comp_confirmation_v1",
        decision={
            "passes": False,
            "pairwise_remains_incumbent_if_false": True,
        },
    )
    diagnosis = canonical(
        "strict_v4_pairwise_opendetect_fpr95_tail_audit_v1",
        passes=True,
        scenario_diagnostics=rows,
    )
    manifest = canonical(
        "strict_v4_boundary_pairwise_candidate_v1",
        selected_method="caeos_pairwise",
    )
    return failure, confirmation, diagnosis, manifest


def build(*, failure=None, diagnosis=None, counts=None):
    default_failure, confirmation, default_diagnosis, manifest = inputs()
    return create_design(
        failure_audit=failure or default_failure,
        comp_confirmation=confirmation,
        diagnosis=diagnosis or default_diagnosis,
        pairwise_manifest=manifest,
        input_file_sha256={
            "failure_audit": "1" * 64,
            "comp_confirmation": "2" * 64,
            "pairwise_diagnosis": "3" * 64,
            "pairwise_manifest": "4" * 64,
        },
        implementation_sha256={"creator": "5" * 64},
        observed_output_counts=counts
        or {
            "execution_protocol": 0,
            "task_metrics": 0,
            "summary": 0,
            "audit": 0,
            "completion": 0,
        },
    )


def test_design_freezes_fresh_scenarios_seeds_and_multimetric_gate() -> None:
    design = build()
    pilot = design["fresh_pilot"]

    assert len(pilot["tasks"]) == 18
    assert len(
        {
            (task["scenario"], task["seed"])
            for task in pilot["tasks"]
        }
    ) == 18
    assert not set(FRESH_SEEDS) & (
        set(DEVELOPMENT_SEEDS) | set(RESERVED_CROSS_SUITE_SEEDS) | {7}
    )
    assert not set(
        FRESH_SCENARIOS["stress"] + FRESH_SCENARIOS["control"]
    ) & set(DEVELOPMENT_SCENARIOS)
    assert (
        design["training_time_selection"]["gate"][
            "per_fold_unknown_aupr_regression_tolerance"
        ]
        == 0.01
    )
    assert pilot["execution_admitted_at_design_freeze"] is False
    assert design["manifest_sha256"] == canonical_hash(design)


def test_design_rejects_any_existing_result() -> None:
    with pytest.raises(ValueError, match="before result outputs"):
        build(
            counts={
                "execution_protocol": 0,
                "task_metrics": 1,
                "summary": 0,
                "audit": 0,
                "completion": 0,
            }
        )


def test_design_rejects_a_posthoc_gate_that_claims_feasibility() -> None:
    failure, _, _, _ = inputs()
    failure = copy.deepcopy(failure)
    failure["diagnostics"]["development_feasible_gate_count"] = 1
    failure["diagnostics"]["best_development_gate"] = {"feature": "leaky"}
    failure["manifest_sha256"] = canonical_hash(failure)

    with pytest.raises(ValueError, match="negative COMP failure"):
        build(failure=failure)


def test_design_rejects_stress_boundary_drift() -> None:
    _, _, diagnosis, _ = inputs()
    diagnosis = copy.deepcopy(diagnosis)
    row = next(
        row
        for row in diagnosis["scenario_diagnostics"]
        if row.get("scenario") == FRESH_SCENARIOS["stress"][0]
    )
    row["pairwise_plateau"]["minimum_plateau_explains_fpr95_one"] = False
    diagnosis["manifest_sha256"] = canonical_hash(diagnosis)

    with pytest.raises(ValueError, match="stress boundary drifted"):
        build(diagnosis=diagnosis)

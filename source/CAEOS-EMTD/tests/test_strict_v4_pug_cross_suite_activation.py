from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from write_strict_v4_pug_cross_suite_activation import classify_activation


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs(passes: bool = True):
    pilot = canonical(
        "strict_v4_pug_execution_protocol_v1",
        state="frozen_before_fresh_seed_execution",
    )
    design = canonical(
        "strict_v4_pug_cross_suite_confirmation_design_v1",
        state=(
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        ),
        execution_admitted_at_freeze=False,
        activation_gate={
            "required_pilot_protocol_manifest_sha256": (
                pilot["manifest_sha256"]
            ),
            "required_pilot_schema": "strict_v4_pug_confirmation_v1",
            "pilot_task_count": 18,
            "pilot_decision_passes_must_equal": True,
            "pilot_selected_method_must_equal": "caeos_pug",
            "pilot_cross_suite_execution_admitted_must_equal": False,
        },
        confirmation_universe={"paired_task_count": 306},
    )
    tasks = [
        {
            "suite": "cic_iot2023",
            "scenario": f"scenario_{scenario}",
            "seed": seed,
            "split_fingerprint": f"split-{scenario}-{seed}",
            "unknown_or_test_labels_used_for_selection": False,
        }
        for scenario in range(6)
        for seed in [283, 293, 307]
    ]
    confirmation = canonical(
        "strict_v4_pug_confirmation_v1",
        protocol_manifest_sha256=pilot["manifest_sha256"],
        task_count=18,
        tasks=tasks,
        artifact_sha256={
            f"artifact-{index}": f"{index + 1:064x}"
            for index in range(126)
        },
        candidate_vs_pairwise={"complete": True},
        candidate_vs_opendetect={"complete": True},
        gate_checks={"integrity": True, "effect": passes},
        decision={
            "passes": passes,
            "selected_method": "caeos_pug" if passes else "caeos_pairwise",
            "cross_suite_execution_admitted": False,
        },
        partial_metrics_aggregated=False,
        unknown_or_test_labels_used_for_selection=False,
    )
    return design, pilot, confirmation


def classify(design, pilot, confirmation):
    return classify_activation(
        design=design,
        pilot_protocol=pilot,
        confirmation=confirmation,
        input_file_sha256={"input": "1" * 64},
        implementation_sha256={"writer": "2" * 64},
    )


def test_pending_confirmation_writes_no_decision() -> None:
    design, pilot, _ = inputs()

    assert classify(design, pilot, None) is None


def test_positive_pilot_activates_but_does_not_select_candidate() -> None:
    design, pilot, confirmation = inputs(passes=True)
    result = classify(design, pilot, confirmation)

    assert result is not None
    assert result["state"] == "positive_activation"
    assert result["cross_suite_execution_admitted"] is True
    assert (
        result["claim_boundary"][
            "positive_activation_is_not_candidate_selection"
        ]
        is True
    )
    assert result["manifest_sha256"] == canonical_hash(result)


def test_negative_pilot_retains_upstream_incumbent() -> None:
    design, pilot, confirmation = inputs(passes=False)
    result = classify(design, pilot, confirmation)

    assert result is not None
    assert (
        result["state"]
        == "negative_not_required_retain_upstream_incumbent"
    )
    assert result["cross_suite_execution_admitted"] is False
    assert (
        result["action"]
        == "write_not_required_and_retain_upstream_incumbent"
    )


def test_activation_rejects_incomplete_artifact_inventory() -> None:
    design, pilot, confirmation = inputs()
    confirmation = copy.deepcopy(confirmation)
    confirmation["artifact_sha256"].pop(next(iter(confirmation["artifact_sha256"])))
    confirmation["manifest_sha256"] = canonical_hash(confirmation)

    with pytest.raises(ValueError, match="18-task"):
        classify(design, pilot, confirmation)


def test_activation_rejects_decision_gate_inconsistency() -> None:
    design, pilot, confirmation = inputs()
    confirmation = copy.deepcopy(confirmation)
    confirmation["gate_checks"]["effect"] = False
    confirmation["manifest_sha256"] = canonical_hash(confirmation)

    with pytest.raises(ValueError, match="inconsistent"):
        classify(design, pilot, confirmation)

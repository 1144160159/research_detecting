from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from write_strict_v4_comp_cross_suite_activation import classify_activation


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs(passes: bool = True):
    pilot = canonical(
        "strict_v4_comp_confirmation_protocol_v1",
        state="frozen_before_fresh_seed_execution",
    )
    design = canonical(
        "strict_v4_comp_cross_suite_confirmation_design_v1",
        state=(
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        ),
        execution_admitted_at_freeze=False,
        activation_gate={
            "required_pilot_protocol_manifest_sha256": pilot["manifest_sha256"],
        },
        confirmation_universe={"paired_task_count": 306},
    )
    confirmation = canonical(
        "strict_v4_comp_confirmation_v1",
        state="fresh_seed_confirmation_complete",
        validation={
            "passes": True,
            "paired_task_count": 18,
            "seeds": [139, 149, 163],
            "scenario_count": 6,
            "split_fingerprint_pair_checks": 18,
            "unknown_or_test_labels_used_for_candidate_routing": False,
            "unknown_or_test_labels_used_for_candidate_thresholds": False,
        },
        input_evidence={
            "protocol_manifest_sha256": pilot["manifest_sha256"],
            "protocol_file_sha256": (
                "00411a25500270d9773d4a63750628bb5c98e23e48c9885aded49e42f8d47720"
            ),
        },
        decision={"passes": passes},
        claim_boundary={
            "cross_suite_expansion_required_after_pilot_pass": True,
        },
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
        result["claim_boundary"]["positive_activation_is_not_candidate_selection"]
        is True
    )
    assert result["manifest_sha256"] == canonical_hash(result)


def test_negative_pilot_writes_not_required_and_retains_pairwise() -> None:
    design, pilot, confirmation = inputs(passes=False)
    result = classify(design, pilot, confirmation)

    assert result is not None
    assert result["state"] == "negative_not_required_retain_pairwise"
    assert result["cross_suite_execution_admitted"] is False
    assert result["action"] == "write_not_required_and_retain_pairwise"


def test_activation_rejects_incomplete_pilot_validation() -> None:
    design, pilot, confirmation = inputs()
    confirmation = copy.deepcopy(confirmation)
    confirmation["validation"]["paired_task_count"] = 17
    confirmation["manifest_sha256"] = canonical_hash(confirmation)

    with pytest.raises(ValueError, match="18-task"):
        classify(design, pilot, confirmation)

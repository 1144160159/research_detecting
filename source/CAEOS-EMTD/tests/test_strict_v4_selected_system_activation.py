from __future__ import annotations

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from write_strict_v4_selected_system_activation import (
    ALGORITHMS,
    FORMAL_OUTPUTS,
    IMPLEMENTATION_FILES,
    build_activation,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def design() -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_selected_system_downstream_adapter_design_v1"
            ),
            "state": "frozen_before_final_self_algorithm_selection",
            "execution_admitted_at_freeze": False,
            "activation": {
                "allowed_selected_algorithms": list(ALGORITHMS),
            },
            "runtime_contract": {
                "schema_version": "strict_v4_selected_system_runtime_v1",
            },
            "implementation_status_at_freeze": {
                "common_runtime_adapter_complete": True,
            },
        }
    )


def goal(selected: str, final: bool = True) -> dict:
    return canonical(
        {
            "schema_version": "strict_v4_current_goal_status_audit_v1",
            "selected_algorithm": selected,
            "requirements": {
                "best_self_algorithm_finally_selected": {
                    "satisfied": final,
                    "status": "complete" if final else "incomplete",
                    "current_incumbent": selected,
                },
            },
            "evidence": {
                "self_algorithm_selection": {
                    "final": final,
                    "selected_algorithm": selected,
                    "krc_rrc_branch": {"terminal": final},
                    "pug_branch": {"terminal": final},
                    "direct_tournament": {"terminal": True},
                },
            },
        }
    )


def build(selected: str, final: bool = True):
    return build_activation(
        goal=goal(selected, final),
        goal_file_sha256="a" * 64,
        design=design(),
        design_file_sha256="b" * 64,
        observed_output_counts={name: 0 for name in FORMAL_OUTPUTS},
        implementation_sha256={
            name: "c" * 64 for name in IMPLEMENTATION_FILES
        },
    )


@pytest.mark.parametrize("selected", ALGORITHMS)
def test_activation_accepts_each_final_self_algorithm(selected: str) -> None:
    value = build(selected)

    assert value is not None
    assert value["selected_algorithm"] == selected
    assert value["execution_admitted"] is True
    assert value["selection_snapshot"]["final"] is True
    assert value["manifest_sha256"] == canonical_hash(value)


def test_activation_remains_pending_before_final_selection() -> None:
    assert build("caeos_pairwise", final=False) is None


def test_activation_rejects_selected_algorithm_disagreement() -> None:
    value = goal("caeos_pairwise")
    value["evidence"]["self_algorithm_selection"][
        "selected_algorithm"
    ] = "caeos_pug"
    value["manifest_sha256"] = canonical_hash(value)

    with pytest.raises(ValueError, match="fields disagree"):
        build_activation(
            goal=value,
            goal_file_sha256="a" * 64,
            design=design(),
            design_file_sha256="b" * 64,
            observed_output_counts={
                name: 0 for name in FORMAL_OUTPUTS
            },
            implementation_sha256={
                name: "c" * 64 for name in IMPLEMENTATION_FILES
            },
        )


def test_activation_rejects_preexisting_formal_output() -> None:
    counts = {name: 0 for name in FORMAL_OUTPUTS}
    counts["external_malicious_protocol.json"] = 1

    with pytest.raises(ValueError, match="zero formal output"):
        build_activation(
            goal=goal("caeos_pug"),
            goal_file_sha256="a" * 64,
            design=design(),
            design_file_sha256="b" * 64,
            observed_output_counts=counts,
            implementation_sha256={
                name: "c" * 64 for name in IMPLEMENTATION_FILES
            },
        )

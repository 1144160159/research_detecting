from __future__ import annotations

from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
import audit_strict_v4_selected_system_integrated as target


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def design() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": (
                "strict_v4_selected_system_downstream_adapter_design_v1"
            ),
            "implementation_sha256": {},
            "integrated_audit": {
                "binds_final_selection_runtime_and_three_downstream_branches": (
                    True
                ),
                "algorithm_directory_renaming_or_result_splicing_is_forbidden": (
                    True
                ),
                "all_existing_comprehensive_sota_gates_are_preserved": True,
                "integrity_pass_is_separate_from_effect_pass": True,
            },
        }
    )


def goal(
    selected: str = "caeos_pairwise",
    blockers: set[str] | None = None,
) -> dict[str, Any]:
    return canonical(
        {
            "schema_version": "strict_v4_current_goal_status_audit_v1",
            "goal_achieved": False,
            "selected_algorithm": selected,
            "blockers": sorted(
                target.EXPECTED_PRE_DOWNSTREAM_BLOCKERS
                if blockers is None
                else blockers
            ),
            "requirements": {
                "classic_baselines_few_and_persuasive": {
                    "satisfied": True
                },
                "best_self_algorithm_finally_selected": {
                    "satisfied": True
                },
                "documentation_updated": {"satisfied": True},
                "comprehensive_sota_verified": {"satisfied": False},
            },
            "evidence": {
                "self_algorithm_selection": {
                    "final": True,
                    "selected_algorithm": selected,
                }
            },
        }
    )


def activation(
    selected: str,
    design_value: dict[str, Any],
    goal_value: dict[str, Any],
    files: dict[str, str],
) -> dict[str, Any]:
    snapshot = {"final": True, "selected_algorithm": selected}
    return canonical(
        {
            "schema_version": "strict_v4_selected_system_activation_v1",
            "execution_admitted": True,
            "selected_algorithm": selected,
            "selection_snapshot": snapshot,
            "selection_snapshot_sha256": canonical_hash(snapshot),
            "input_manifest_sha256": {
                "adapter_design": design_value["manifest_sha256"],
                "current_goal_audit": goal_value["manifest_sha256"],
            },
            "input_file_sha256": {
                "adapter_design": files["adapter_design"],
                "current_goal_audit": files["current_goal_audit"],
            },
        }
    )


def branch(
    name: str,
    selected: str = "caeos_pairwise",
    *,
    effect: bool = True,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    schemas = target.BRANCH_SCHEMAS[name]
    protocol = canonical(
        {
            "schema_version": schemas[0],
            "selected_algorithm": selected,
        }
    )
    if name == "external_malicious":
        summary = canonical(
            {
                "schema_version": schemas[1],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "validation": {
                    "integrity_passes": True,
                    "effect_passes": effect,
                },
                "external_malicious_confirmation_passes": effect,
            }
        )
        audit = canonical(
            {
                "schema_version": schemas[2],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "summary_manifest_sha256": summary["manifest_sha256"],
                "integrity_passes": True,
                "effect_passes": effect,
            }
        )
    elif name == "parrot_benign_safety":
        summary = canonical(
            {
                "schema_version": schemas[1],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "safety_gate_passes": effect,
            }
        )
        audit = canonical(
            {
                "schema_version": schemas[2],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "summary_manifest_sha256": summary["manifest_sha256"],
                "passes": True,
                "benign_domain_shift_safety_gate_passes": effect,
                "claim_boundary": {
                    "parrot_accuracy_or_sota_claim_supported": False
                },
            }
        )
    else:
        summary = canonical(
            {
                "schema_version": schemas[1],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "deployability_decision": {"passes": True},
                "strict_efficiency_decision": {"passes": effect},
            }
        )
        audit = canonical(
            {
                "schema_version": schemas[2],
                "selected_algorithm": selected,
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "summary_manifest_sha256": summary["manifest_sha256"],
                "passed": True,
                "strict_efficiency_sota_supported": effect,
            }
        )
    return protocol, summary, audit


def evidence(
    *,
    efficiency_effect: bool = True,
    blockers: set[str] | None = None,
    branch_selected: str = "caeos_pairwise",
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    dict[str, str],
]:
    design_value = design()
    goal_value = goal(blockers=blockers)
    files = {
        "activation": "a" * 64,
        "adapter_design": "b" * 64,
        "current_goal_audit": "c" * 64,
    }
    branches = {
        name: branch(
            name,
            branch_selected,
            effect=(
                efficiency_effect
                if name == "same_hardware_efficiency"
                else True
            ),
        )
        for name in target.BRANCH_SCHEMAS
    }
    for name in target.BRANCH_SCHEMAS:
        for kind, suffix in zip(
            ("protocol", "summary", "audit"), ("d", "e", "f")
        ):
            files[f"{name}_{kind}"] = (
                f"{len(files):02x}{suffix}".ljust(64, suffix)
            )
    activation_value = activation(
        "caeos_pairwise", design_value, goal_value, files
    )
    return activation_value, design_value, goal_value, branches, files


def test_all_frozen_gates_support_multidimensional_sota(
    tmp_path: Path,
) -> None:
    values = evidence()
    result = target.audit_integrated(
        project_root=tmp_path,
        activation=values[0],
        design=values[1],
        goal=values[2],
        branches=values[3],
        input_file_sha256=values[4],
    )
    assert result["passes"] is True
    assert result["pre_downstream_scientific_gates_pass"] is True
    assert (
        result["effectiveness_external_and_benign_safety_supported"]
        is True
    )
    assert result["multidimensional_comprehensive_sota_supported"] is True
    assert result["comprehensive_sota_confirmed"] is True


def test_efficiency_failure_preserves_tier1_but_blocks_full_sota(
    tmp_path: Path,
) -> None:
    values = evidence(efficiency_effect=False)
    result = target.audit_integrated(
        project_root=tmp_path,
        activation=values[0],
        design=values[1],
        goal=values[2],
        branches=values[3],
        input_file_sha256=values[4],
    )
    assert result["passes"] is True
    assert (
        result["effectiveness_external_and_benign_safety_supported"]
        is True
    )
    assert result["multidimensional_comprehensive_sota_supported"] is False
    assert (
        result["claim_tier"]
        == "effectiveness_external_and_benign_safety_supported_"
        "without_strict_efficiency_sota"
    )


def test_unresolved_pre_downstream_blocker_cannot_be_bypassed(
    tmp_path: Path,
) -> None:
    blockers = {
        *target.EXPECTED_PRE_DOWNSTREAM_BLOCKERS,
        "absolute five-family corruption gate failed",
    }
    values = evidence(blockers=blockers)
    result = target.audit_integrated(
        project_root=tmp_path,
        activation=values[0],
        design=values[1],
        goal=values[2],
        branches=values[3],
        input_file_sha256=values[4],
    )
    assert result["passes"] is True
    assert result["pre_downstream_scientific_gates_pass"] is False
    assert result["comprehensive_sota_confirmed"] is False


def test_cross_algorithm_result_splicing_fails_integrity(
    tmp_path: Path,
) -> None:
    values = evidence(branch_selected="caeos_pug")
    result = target.audit_integrated(
        project_root=tmp_path,
        activation=values[0],
        design=values[1],
        goal=values[2],
        branches=values[3],
        input_file_sha256=values[4],
    )
    assert result["passes"] is False
    assert result["comprehensive_sota_confirmed"] is False
    assert (
        result["integrity_checks"][
            "all_branch_integrity_checks_pass"
        ]
        is False
    )

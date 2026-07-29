from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_selected_system_external_malicious import (
    ALGORITHMS,
    PROTOCOL_SCHEMA as EXTERNAL_PROTOCOL_SCHEMA,
)
from run_strict_v4_selected_system_parrot_safety import (
    AUDIT_SCHEMA as PARROT_AUDIT_SCHEMA,
    PROTOCOL_SCHEMA as PARROT_PROTOCOL_SCHEMA,
    SUMMARY_SCHEMA as PARROT_SUMMARY_SCHEMA,
)
from run_strict_v4_selected_system_efficiency import (
    AUDIT_SCHEMA as EFFICIENCY_AUDIT_SCHEMA,
    PROTOCOL_SCHEMA as EFFICIENCY_PROTOCOL_SCHEMA,
    SUMMARY_SCHEMA as EFFICIENCY_SUMMARY_SCHEMA,
)


SCHEMA = "strict_v4_selected_system_integrated_audit_v1"
EXTERNAL_SUMMARY_SCHEMA = (
    "strict_v4_selected_system_external_malicious_summary_v1"
)
EXTERNAL_AUDIT_SCHEMA = (
    "strict_v4_selected_system_external_malicious_audit_v1"
)
EXPECTED_PRE_DOWNSTREAM_BLOCKERS = {
    "external malicious confirmation is incomplete",
    "PARROT benign safety confirmation is incomplete",
    "selected-system efficiency comparison is incomplete",
}
BRANCH_SCHEMAS = {
    "external_malicious": (
        EXTERNAL_PROTOCOL_SCHEMA,
        EXTERNAL_SUMMARY_SCHEMA,
        EXTERNAL_AUDIT_SCHEMA,
    ),
    "parrot_benign_safety": (
        PARROT_PROTOCOL_SCHEMA,
        PARROT_SUMMARY_SCHEMA,
        PARROT_AUDIT_SCHEMA,
    ),
    "same_hardware_efficiency": (
        EFFICIENCY_PROTOCOL_SCHEMA,
        EFFICIENCY_SUMMARY_SCHEMA,
        EFFICIENCY_AUDIT_SCHEMA,
    ),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def canonical(value: dict[str, Any], schema: str) -> bool:
    return bool(
        value.get("schema_version") == schema
        and value.get("manifest_sha256") == canonical_hash(value)
    )


def branch_integrity(
    *,
    name: str,
    selected: str,
    protocol: dict[str, Any],
    summary: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, bool]:
    schemas = BRANCH_SCHEMAS[name]
    return {
        "protocol_is_canonical": canonical(protocol, schemas[0]),
        "summary_is_canonical": canonical(summary, schemas[1]),
        "audit_is_canonical": canonical(audit, schemas[2]),
        "protocol_uses_activated_algorithm": (
            protocol.get("selected_algorithm") == selected
        ),
        "summary_algorithm_does_not_conflict": (
            summary.get("selected_algorithm", selected) == selected
        ),
        "audit_algorithm_does_not_conflict": (
            audit.get("selected_algorithm", selected) == selected
        ),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "audit_binds_protocol": (
            audit.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "audit_binds_summary": (
            audit.get("summary_manifest_sha256")
            == summary.get("manifest_sha256")
        ),
    }


def audit_integrated(
    *,
    project_root: Path,
    activation: dict[str, Any],
    design: dict[str, Any],
    goal: dict[str, Any],
    branches: dict[
        str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]
    ],
    input_file_sha256: dict[str, str],
) -> dict[str, Any]:
    selected = activation.get("selected_algorithm")
    selection = goal.get("evidence", {}).get(
        "self_algorithm_selection", {}
    )
    requirements = goal.get("requirements", {})
    branch_checks = {
        name: branch_integrity(
            name=name,
            selected=str(selected),
            protocol=values[0],
            summary=values[1],
            audit=values[2],
        )
        for name, values in branches.items()
    }
    branch_integrity_passes = {
        name: all(checks.values())
        for name, checks in branch_checks.items()
    }
    implementation_ok = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in design.get(
            "implementation_sha256", {}
        ).items()
    )
    activation_snapshot = activation.get("selection_snapshot", {})
    integrity_checks = {
        "activation_is_canonical": canonical(
            activation, "strict_v4_selected_system_activation_v1"
        ),
        "adapter_design_is_canonical": canonical(
            design,
            "strict_v4_selected_system_downstream_adapter_design_v1",
        ),
        "goal_audit_is_canonical": canonical(
            goal, "strict_v4_current_goal_status_audit_v1"
        ),
        "activation_binds_adapter_design": (
            activation.get("input_manifest_sha256", {}).get(
                "adapter_design"
            )
            == design.get("manifest_sha256")
            and activation.get("input_file_sha256", {}).get(
                "adapter_design"
            )
            == input_file_sha256.get("adapter_design")
        ),
        "activation_binds_goal_audit": (
            activation.get("input_manifest_sha256", {}).get(
                "current_goal_audit"
            )
            == goal.get("manifest_sha256")
            and activation.get("input_file_sha256", {}).get(
                "current_goal_audit"
            )
            == input_file_sha256.get("current_goal_audit")
        ),
        "selection_snapshot_is_canonical": (
            activation.get("selection_snapshot_sha256")
            == canonical_hash(activation_snapshot)
        ),
        "selection_is_final_and_consistent": bool(
            selected in ALGORITHMS
            and activation.get("execution_admitted") is True
            and activation_snapshot.get("final") is True
            and activation_snapshot.get("selected_algorithm") == selected
            and selection.get("final") is True
            and selection.get("selected_algorithm") == selected
            and goal.get("selected_algorithm") == selected
        ),
        "all_branch_names_are_exact": (
            set(branches) == set(BRANCH_SCHEMAS)
        ),
        "all_branch_integrity_checks_pass": all(
            branch_integrity_passes.values()
        ),
        "design_implementation_hashes_match": implementation_ok,
        "integrated_audit_contract_is_preserved": bool(
            design.get("integrated_audit", {}).get(
                "binds_final_selection_runtime_and_three_downstream_branches"
            )
            is True
            and design.get("integrated_audit", {}).get(
                "algorithm_directory_renaming_or_result_splicing_is_forbidden"
            )
            is True
            and design.get("integrated_audit", {}).get(
                "all_existing_comprehensive_sota_gates_are_preserved"
            )
            is True
            and design.get("integrated_audit", {}).get(
                "integrity_pass_is_separate_from_effect_pass"
            )
            is True
        ),
        "input_file_registry_is_complete": (
            set(input_file_sha256)
            == {
                "activation",
                "adapter_design",
                "current_goal_audit",
                *{
                    f"{branch}_{kind}"
                    for branch in BRANCH_SCHEMAS
                    for kind in ("protocol", "summary", "audit")
                },
            }
            and all(input_file_sha256.values())
        ),
    }
    integrity_passes = all(integrity_checks.values())
    blockers = set(map(str, goal.get("blockers", [])))
    pre_downstream_checks = {
        "classic_baseline_requirement_satisfied": (
            requirements.get("classic_baselines_few_and_persuasive", {}).get(
                "satisfied"
            )
            is True
        ),
        "best_self_algorithm_finally_selected": (
            requirements.get("best_self_algorithm_finally_selected", {}).get(
                "satisfied"
            )
            is True
        ),
        "documentation_requirement_satisfied": (
            requirements.get("documentation_updated", {}).get("satisfied")
            is True
        ),
        "only_three_downstream_blockers_remained_at_activation": (
            blockers == EXPECTED_PRE_DOWNSTREAM_BLOCKERS
        ),
        "pre_downstream_goal_not_prematurely_marked_complete": (
            goal.get("goal_achieved") is False
            and requirements.get("comprehensive_sota_verified", {}).get(
                "satisfied"
            )
            is False
        ),
    }
    pre_downstream_passes = all(pre_downstream_checks.values())
    external_summary = branches["external_malicious"][1]
    external_audit = branches["external_malicious"][2]
    parrot_summary = branches["parrot_benign_safety"][1]
    parrot_audit = branches["parrot_benign_safety"][2]
    efficiency_summary = branches["same_hardware_efficiency"][1]
    efficiency_audit = branches["same_hardware_efficiency"][2]
    external_gate = bool(
        branch_integrity_passes["external_malicious"]
        and external_summary.get("validation", {}).get("integrity_passes")
        is True
        and external_summary.get(
            "external_malicious_confirmation_passes"
        )
        is True
        and external_audit.get("integrity_passes") is True
        and external_audit.get("effect_passes") is True
    )
    parrot_gate = bool(
        branch_integrity_passes["parrot_benign_safety"]
        and parrot_summary.get("safety_gate_passes") is True
        and parrot_audit.get("passes") is True
        and parrot_audit.get(
            "benign_domain_shift_safety_gate_passes"
        )
        is True
        and parrot_audit.get("claim_boundary", {}).get(
            "parrot_accuracy_or_sota_claim_supported"
        )
        is False
    )
    efficiency_integrity_gate = bool(
        branch_integrity_passes["same_hardware_efficiency"]
        and efficiency_summary.get("deployability_decision", {}).get(
            "passes"
        )
        is True
        and efficiency_audit.get("passed") is True
    )
    efficiency_effect_gate = bool(
        efficiency_integrity_gate
        and efficiency_summary.get("strict_efficiency_decision", {}).get(
            "passes"
        )
        is True
        and efficiency_audit.get(
            "strict_efficiency_sota_supported"
        )
        is True
    )
    tier1 = bool(
        integrity_passes
        and pre_downstream_passes
        and external_gate
        and parrot_gate
        and efficiency_integrity_gate
    )
    tier2 = bool(tier1 and efficiency_effect_gate)
    claim_tier = (
        "multidimensional_comprehensive_sota_within_frozen_scope"
        if tier2
        else (
            "effectiveness_external_and_benign_safety_supported_"
            "without_strict_efficiency_sota"
            if tier1
            else "integrated_sota_not_supported"
        )
    )
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "selected_algorithm": selected,
        "activation_manifest_sha256": activation.get("manifest_sha256"),
        "adapter_design_manifest_sha256": design.get("manifest_sha256"),
        "current_goal_audit_manifest_sha256": goal.get("manifest_sha256"),
        "integrity_checks": integrity_checks,
        "branch_integrity_checks": branch_checks,
        "branch_integrity_passes": branch_integrity_passes,
        "passes": integrity_passes,
        "pre_downstream_scientific_checks": pre_downstream_checks,
        "pre_downstream_scientific_gates_pass": pre_downstream_passes,
        "evidence_gates": {
            "fresh_external_malicious_effect": external_gate,
            "parrot_external_benign_safety": parrot_gate,
            "same_hardware_efficiency_integrity": (
                efficiency_integrity_gate
            ),
            "strict_efficiency_superiority_over_pairwise_and_opendetect": (
                efficiency_effect_gate
            ),
        },
        "effectiveness_external_and_benign_safety_supported": tier1,
        "multidimensional_comprehensive_sota_supported": tier2,
        "comprehensive_sota_confirmed": tier2,
        "claim_tier": claim_tier,
        "claim_scope": (
            "frozen_strict_v4_baseline_dataset_metric_and_algorithm_universe"
        ),
        "paper_writing_integrity_evidence_ready": integrity_passes,
        "claim_boundary": {
            "integrity_pass_is_separate_from_effect_pass": True,
            "efficiency_failure_does_not_cancel_tier1_effectiveness": True,
            "parrot_used_only_for_external_benign_false_alert_safety": True,
            "parrot_malicious_accuracy_or_sota_claim_supported": False,
            "algorithm_renaming_or_result_splicing_forbidden": True,
            "universal_or_out_of_scope_sota_claim_supported": False,
        },
        "input_file_sha256": dict(sorted(input_file_sha256.items())),
        "input_manifest_sha256": {
            "activation": activation.get("manifest_sha256"),
            "adapter_design": design.get("manifest_sha256"),
            "current_goal_audit": goal.get("manifest_sha256"),
            **{
                f"{name}_{kind}": value.get("manifest_sha256")
                for name, values in branches.items()
                for kind, value in zip(
                    ("protocol", "summary", "audit"), values
                )
            },
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--adapter-design", type=Path, required=True)
    parser.add_argument("--current-goal-audit", type=Path, required=True)
    for prefix in ("external", "parrot", "efficiency"):
        parser.add_argument(
            f"--{prefix}-protocol", type=Path, required=True
        )
        parser.add_argument(
            f"--{prefix}-summary", type=Path, required=True
        )
        parser.add_argument(
            f"--{prefix}-audit", type=Path, required=True
        )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mapping = {
        "external_malicious": "external",
        "parrot_benign_safety": "parrot",
        "same_hardware_efficiency": "efficiency",
    }
    paths = {
        "activation": args.activation.resolve(),
        "adapter_design": args.adapter_design.resolve(),
        "current_goal_audit": args.current_goal_audit.resolve(),
    }
    branches = {}
    for logical, prefix in mapping.items():
        values = []
        for kind in ("protocol", "summary", "audit"):
            path = getattr(args, f"{prefix}_{kind}").resolve()
            paths[f"{logical}_{kind}"] = path
            values.append(load(path))
        branches[logical] = tuple(values)
    value = audit_integrated(
        project_root=args.project_root.resolve(),
        activation=load(paths["activation"]),
        design=load(paths["adapter_design"]),
        goal=load(paths["current_goal_audit"]),
        branches=branches,
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
    )
    write_json(args.output.resolve(), value)
    print(
        json.dumps(
            {
                "passes": value["passes"],
                "claim_tier": value["claim_tier"],
                "comprehensive_sota_confirmed": value[
                    "comprehensive_sota_confirmed"
                ],
                "manifest_sha256": value["manifest_sha256"],
                "file_sha256": file_hash(args.output.resolve()),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

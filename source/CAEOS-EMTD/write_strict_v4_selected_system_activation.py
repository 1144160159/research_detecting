from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
FORMAL_OUTPUTS = (
    "activation.json",
    "selected_system_protocol.json",
    "external_malicious_protocol.json",
    "parrot_safety_protocol.json",
    "efficiency_protocol.json",
    "integrated_audit.json",
    "execution_complete.json",
)
EXPECTED_PRE_DOWNSTREAM_BLOCKERS = {
    "external malicious confirmation is incomplete",
    "PARROT benign safety confirmation is incomplete",
    "selected-system efficiency comparison is incomplete",
}
REQUIRED_PRE_DOWNSTREAM_REQUIREMENTS = (
    "classic_baselines_few_and_persuasive",
    "domain_nearest_baseline_confirmed",
    "best_self_algorithm_finally_selected",
    "documentation_updated",
)
IMPLEMENTATION_FILES = (
    "write_strict_v4_selected_system_activation.py",
    "audit_strict_v4_current_goal_status.py",
    "caeos/selected_system_runtime.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def output_counts(result_root: Path) -> dict[str, int]:
    return {
        name: int((result_root / name).is_file())
        for name in FORMAL_OUTPUTS
    }


def selection_snapshot(goal: dict[str, Any]) -> dict[str, Any]:
    requirement = goal.get("requirements", {}).get(
        "best_self_algorithm_finally_selected", {}
    )
    selection = goal.get("evidence", {}).get(
        "self_algorithm_selection", {}
    )
    selected = goal.get("selected_algorithm")
    if (
        requirement.get("satisfied") is True
    ) != (selection.get("final") is True):
        raise ValueError("goal requirement and self-selection finality disagree")
    if (
        requirement.get("current_incumbent") != selected
        or selection.get("selected_algorithm") != selected
    ):
        raise ValueError("selected algorithm fields disagree")
    return {
        "final": bool(selection.get("final")),
        "selected_algorithm": selected,
        "krc_rrc_branch": selection.get("krc_rrc_branch"),
        "pug_branch": selection.get("pug_branch"),
        "direct_tournament": selection.get("direct_tournament"),
        "requirement_status": requirement.get("status"),
    }


def pre_downstream_snapshot(goal: dict[str, Any]) -> dict[str, Any]:
    requirements = goal.get("requirements", {})
    blockers = set(map(str, goal.get("blockers", [])))
    requirement_state = {
        name: requirements.get(name, {}).get("satisfied") is True
        for name in REQUIRED_PRE_DOWNSTREAM_REQUIREMENTS
    }
    comprehensive = requirements.get("comprehensive_sota_verified", {})
    ready = bool(
        all(requirement_state.values())
        and blockers == EXPECTED_PRE_DOWNSTREAM_BLOCKERS
        and goal.get("goal_achieved") is False
        and comprehensive.get("satisfied") is False
    )
    return {
        "ready": ready,
        "requirement_state": requirement_state,
        "blockers": sorted(blockers),
        "expected_blockers": sorted(EXPECTED_PRE_DOWNSTREAM_BLOCKERS),
        "comprehensive_sota_verified_before_downstream": (
            comprehensive.get("satisfied") is True
        ),
    }


def build_activation(
    *,
    goal: dict[str, Any],
    goal_file_sha256: str,
    design: dict[str, Any],
    design_file_sha256: str,
    observed_output_counts: dict[str, int],
    implementation_sha256: dict[str, str],
) -> dict[str, Any] | None:
    require_canonical(
        goal,
        "strict_v4_current_goal_status_audit_v1",
        "current goal audit",
    )
    require_canonical(
        design,
        "strict_v4_selected_system_downstream_adapter_design_v1",
        "selected-system downstream adapter design",
    )
    allowed = design.get("activation", {}).get(
        "allowed_selected_algorithms"
    )
    runtime = design.get("runtime_contract", {})
    implementation = design.get("implementation_status_at_freeze", {})
    if (
        design.get("state")
        != "frozen_before_final_self_algorithm_selection"
        or design.get("execution_admitted_at_freeze") is not False
        or allowed != list(ALGORITHMS)
        or runtime.get("schema_version")
        != "strict_v4_selected_system_runtime_v1"
        or implementation.get("common_runtime_adapter_complete") is not True
    ):
        raise ValueError("selected-system adapter design contract drifted")
    snapshot = selection_snapshot(goal)
    if not snapshot["final"]:
        return None
    pre_downstream = pre_downstream_snapshot(goal)
    if not pre_downstream["ready"]:
        return None
    if snapshot["selected_algorithm"] not in ALGORITHMS:
        raise ValueError("unsupported final selected algorithm")
    if set(observed_output_counts) != set(FORMAL_OUTPUTS):
        raise ValueError("selected-system formal output inventory drifted")
    if any(int(count) != 0 for count in observed_output_counts.values()):
        raise ValueError(
            "selected-system activation requires zero formal output"
        )
    if set(implementation_sha256) != set(IMPLEMENTATION_FILES):
        raise ValueError("activation implementation inventory drifted")
    value: dict[str, Any] = {
        "schema_version": "strict_v4_selected_system_activation_v1",
        "state": (
            "activated_after_final_self_algorithm_selection_before_"
            "downstream_execution"
        ),
        "execution_admitted": True,
        "selected_algorithm": snapshot["selected_algorithm"],
        "runtime_contract_schema": runtime["schema_version"],
        "selection_snapshot": snapshot,
        "selection_snapshot_sha256": canonical_hash(snapshot),
        "pre_downstream_snapshot": pre_downstream,
        "pre_downstream_snapshot_sha256": canonical_hash(pre_downstream),
        "downstream_branches": [
            "external_malicious",
            "parrot_benign_safety",
            "same_hardware_efficiency",
            "integrated_comprehensive_sota_audit",
        ],
        "input_manifest_sha256": {
            "current_goal_audit": goal["manifest_sha256"],
            "adapter_design": design["manifest_sha256"],
        },
        "input_file_sha256": {
            "current_goal_audit": goal_file_sha256,
            "adapter_design": design_file_sha256,
        },
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
        "formal_output_counts_before_activation": dict(
            sorted(observed_output_counts.items())
        ),
        "claim_boundary": {
            "activation_is_not_downstream_execution_or_effect": True,
            "activation_requires_only_three_downstream_blockers": True,
            "all_branches_must_use_the_same_selected_algorithm": True,
            "krc_result_renaming_or_cross_algorithm_splicing_forbidden": True,
            "comprehensive_sota_remains_unauthorized_until_final_audit": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def validate_existing(
    value: dict[str, Any], design: dict[str, Any]
) -> None:
    require_canonical(
        value,
        "strict_v4_selected_system_activation_v1",
        "selected-system activation",
    )
    if (
        value.get("execution_admitted") is not True
        or value.get("selected_algorithm") not in ALGORITHMS
        or value.get("selection_snapshot", {}).get("final") is not True
        or value.get("selection_snapshot", {}).get("selected_algorithm")
        != value.get("selected_algorithm")
        or value.get("selection_snapshot_sha256")
        != canonical_hash(value["selection_snapshot"])
        or value.get("input_manifest_sha256", {}).get("adapter_design")
        != design.get("manifest_sha256")
    ):
        raise ValueError("existing selected-system activation is invalid")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--goal-audit",
        type=Path,
        default=Path("results/strict_v4_current_goal_status_v1/audit.json"),
    )
    parser.add_argument(
        "--adapter-design",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1/"
            "activation.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    goal_path = resolve(args.goal_audit)
    design_path = resolve(args.adapter_design)
    result_root = resolve(args.result_root)
    output = resolve(args.output)
    design = load(design_path)
    if output.is_file():
        value = load(output)
        validate_existing(value, design)
        print(
            json.dumps(
                {
                    "state": "retained_existing_activation",
                    "selected_algorithm": value["selected_algorithm"],
                    "manifest_sha256": value["manifest_sha256"],
                    "file_sha256": file_hash(output),
                },
                sort_keys=True,
            )
        )
        return
    goal = load(goal_path)
    implementation_sha256 = {
        relative: file_hash(root / relative)
        for relative in IMPLEMENTATION_FILES
    }
    value = build_activation(
        goal=goal,
        goal_file_sha256=file_hash(goal_path),
        design=design,
        design_file_sha256=file_hash(design_path),
        observed_output_counts=output_counts(result_root),
        implementation_sha256=implementation_sha256,
    )
    if value is None:
        print(
            json.dumps(
                {
                    "state": "pending_final_self_algorithm_selection",
                    "activation_written": False,
                },
                sort_keys=True,
            )
        )
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    print(
        json.dumps(
            {
                "state": value["state"],
                "selected_algorithm": value["selected_algorithm"],
                "manifest_sha256": value["manifest_sha256"],
                "file_sha256": file_hash(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

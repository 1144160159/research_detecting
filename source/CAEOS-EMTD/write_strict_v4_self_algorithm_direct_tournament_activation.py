from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


SCHEMA = "strict_v4_self_algorithm_direct_tournament_activation_v1"
DESIGN_SCHEMA = "strict_v4_self_algorithm_direct_tournament_design_v1"
GOAL_SCHEMA = "strict_v4_current_goal_status_audit_v1"
INCUMBENTS = ("krc_csr_caeos_v1", "rrc_csr_caeos_v1")


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
        "protocol": int((result_root / "protocol.json").is_file()),
        "task_records": len(
            list(result_root.glob("task_records/**/evaluation.json"))
        ),
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int(
            (result_root / "execution_complete.json").is_file()
        ),
    }


def classify_activation(
    goal_audit: dict[str, Any],
    design: dict[str, Any],
    *,
    goal_file_sha256: str,
    design_file_sha256: str,
    formal_output_counts: dict[str, int],
) -> dict[str, Any]:
    require_canonical(goal_audit, GOAL_SCHEMA, "current goal audit")
    require_canonical(design, DESIGN_SCHEMA, "direct tournament design")
    selection = goal_audit.get("evidence", {}).get(
        "self_algorithm_selection", {}
    )
    direct = selection.get("direct_tournament", {})
    requirement = goal_audit.get("requirements", {}).get(
        "best_self_algorithm_finally_selected", {}
    )
    incumbent = direct.get("incumbent")
    challenger = direct.get("challenger")
    required = bool(
        direct.get("required") is True
        and direct.get("terminal") is False
        and direct.get("status") == "fresh_direct_tournament_required"
        and incumbent in INCUMBENTS
        and challenger == "caeos_pug"
        and selection.get("selected_algorithm") == incumbent
        and selection.get("provisional_challenger") == challenger
        and selection.get("krc_rrc_branch", {}).get("terminal") is True
        and selection.get("pug_branch", {}).get("terminal") is True
        and selection.get("pug_branch", {})
        .get("cross_suite", {})
        .get("selected_algorithm")
        == challenger
        and requirement.get("satisfied") is False
        and requirement.get("status")
        == "self_algorithm_direct_tournament_incomplete"
    )
    if not required:
        return {
            "state": "pending_dual_positive_terminal_selection",
            "activation_required": False,
            "incumbent": incumbent,
            "challenger": challenger,
        }
    if any(int(value) != 0 for value in formal_output_counts.values()):
        raise ValueError(
            "direct tournament formal outputs must be zero at activation"
        )
    universe = design.get("confirmation_universe", {})
    if (
        design.get("state")
        != "conditionally_frozen_before_dual_positive_outcome"
        or design.get("execution_admitted_at_freeze") is not False
        or universe.get("suite_count") != 7
        or universe.get("scenario_count") != 102
        or universe.get("seeds") != [809, 811, 821]
        or universe.get("paired_task_count") != 306
        or universe.get("expected_paired_evaluations") != 918
        or design.get("candidate_slots", {})
        .get("incumbent", {})
        .get("allowed_algorithms")
        != list(INCUMBENTS)
    ):
        raise ValueError("frozen direct tournament design is inconsistent")
    snapshot = {
        "final": False,
        "selected_algorithm": incumbent,
        "provisional_challenger": challenger,
        "krc_rrc_branch": selection["krc_rrc_branch"],
        "pug_branch": selection["pug_branch"],
        "direct_tournament": direct,
    }
    activation: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "dual_positive_direct_tournament_admitted",
        "execution_admitted": True,
        "incumbent_algorithm": incumbent,
        "challenger_algorithm": challenger,
        "selection_snapshot": snapshot,
        "selection_snapshot_sha256": canonical_hash(snapshot),
        "input_manifest_sha256": {
            "current_goal_audit": goal_audit["manifest_sha256"],
            "direct_tournament_design": design["manifest_sha256"],
        },
        "input_file_sha256": {
            "current_goal_audit": goal_file_sha256,
            "direct_tournament_design": design_file_sha256,
        },
        "formal_output_counts_before_activation": formal_output_counts,
        "claim_boundary": {
            "activation_is_not_execution_or_effect": True,
            "incumbent_remains_selected_until_independent_audit": True,
            "test_effect_metrics_not_read": True,
            "no_threshold_seed_suite_or_metric_selected_after_results": True,
        },
    }
    activation["manifest_sha256"] = canonical_hash(activation)
    return activation


def write_activation(
    *,
    goal_audit_path: Path,
    design_path: Path,
    result_root: Path,
    output: Path,
) -> dict[str, Any]:
    value = classify_activation(
        load(goal_audit_path),
        load(design_path),
        goal_file_sha256=file_hash(goal_audit_path),
        design_file_sha256=file_hash(design_path),
        formal_output_counts=output_counts(result_root),
    )
    if value.get("activation_required") is False:
        return value
    if output.is_file():
        existing = load(output)
        if existing != value:
            raise ValueError("existing direct tournament activation is immutable")
        return existing
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--goal-audit",
        type=Path,
        default=Path("results/strict_v4_current_goal_status_v1/audit.json"),
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    result_root = resolve(args.result_root)
    value = write_activation(
        goal_audit_path=resolve(args.goal_audit),
        design_path=resolve(args.design),
        result_root=result_root,
        output=result_root / "activation.json",
    )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()

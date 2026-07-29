from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_selected_system_preconfirmation_design import (
    ALGORITHMS,
    SCHEMA as DESIGN_SCHEMA,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_activation_v1"


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


def build_activation(
    goal: dict[str, Any],
    design: dict[str, Any],
    *,
    goal_file_sha256: str,
    design_file_sha256: str,
) -> dict[str, Any] | None:
    require_canonical(
        goal, "strict_v4_current_goal_status_audit_v1", "current goal audit"
    )
    require_canonical(design, DESIGN_SCHEMA, "preconfirmation design")
    requirement = goal.get("requirements", {}).get(
        "best_self_algorithm_finally_selected", {}
    )
    selection = goal.get("evidence", {}).get(
        "self_algorithm_selection", {}
    )
    selected = goal.get("selected_algorithm")
    if (
        requirement.get("satisfied") is not True
        or selection.get("final") is not True
    ):
        return None
    if (
        selected not in ALGORITHMS
        or requirement.get("current_incumbent") != selected
        or selection.get("selected_algorithm") != selected
    ):
        raise ValueError("final selected algorithm fields disagree")
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "activated_after_final_selection_before_preconfirmation",
        "execution_admitted": True,
        "selected_algorithm": selected,
        "selection_snapshot": {
            "selected_algorithm": selected,
            "krc_rrc_branch": selection.get("krc_rrc_branch"),
            "pug_branch": selection.get("pug_branch"),
            "direct_tournament": selection.get("direct_tournament"),
        },
        "input_manifest_sha256": {
            "current_goal_audit": goal["manifest_sha256"],
            "preconfirmation_design": design["manifest_sha256"],
        },
        "input_file_sha256": {
            "current_goal_audit": goal_file_sha256,
            "preconfirmation_design": design_file_sha256,
        },
        "claim_boundary": {
            "activation_is_not_preconfirmation_execution_or_effect": True,
            "downstream_selected_system_activation_remains_separate": True,
            "comprehensive_sota_authorized": False,
        },
    }
    result["selection_snapshot_sha256"] = canonical_hash(
        result["selection_snapshot"]
    )
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal-audit", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.is_file():
        existing = load(args.output)
        require_canonical(existing, SCHEMA, "preconfirmation activation")
        print(
            json.dumps(
                {
                    "state": "existing_activation_retained",
                    "selected_algorithm": existing["selected_algorithm"],
                    "manifest_sha256": existing["manifest_sha256"],
                },
                sort_keys=True,
            )
        )
        return
    result = build_activation(
        load(args.goal_audit),
        load(args.design),
        goal_file_sha256=file_hash(args.goal_audit),
        design_file_sha256=file_hash(args.design),
    )
    if result is None:
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
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "state": result["state"],
                "selected_algorithm": result["selected_algorithm"],
                "manifest_sha256": result["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

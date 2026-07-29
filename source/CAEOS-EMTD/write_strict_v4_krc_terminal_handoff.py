from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from classify_strict_v4_rrc_terminal_decision import classify
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SCHEMA = "strict_v4_krc_terminal_handoff_v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def build_handoff(
    decision: dict[str, Any], decision_file_sha256: str
) -> dict[str, Any]:
    action = classify(decision)
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": (
            "terminal_decision_ready_for_unified_self_algorithm_selection"
        ),
        "decision_action": action,
        "krc_downstream_decision_manifest_sha256": decision[
            "manifest_sha256"
        ],
        "krc_downstream_decision_file_sha256": decision_file_sha256,
        "rrc_confirmation_required": action == "run_rrc",
        "legacy_krc_specific_downstream_started": False,
        "unified_selected_system_downstream_required": True,
        "claim_boundary": {
            "krc_terminal_decision_is_not_final_self_algorithm_selection": True,
            "pug_branch_and_direct_tournament_when_required_must_finish": True,
            "external_parrot_and_efficiency_must_wait_for_final_selection": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def validate_existing(
    value: dict[str, Any],
    *,
    decision: dict[str, Any],
    decision_file_sha256: str,
) -> None:
    expected = build_handoff(decision, decision_file_sha256)
    if value != expected:
        raise ValueError("existing KRC terminal handoff drifted")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    decision_path = args.decision.resolve()
    output = args.output.resolve()
    decision = load(decision_path)
    decision_file_sha256 = file_hash(decision_path)
    value = build_handoff(decision, decision_file_sha256)
    if output.is_file():
        validate_existing(
            load(output),
            decision=decision,
            decision_file_sha256=decision_file_sha256,
        )
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, output)
    print(
        json.dumps(
            {
                "state": value["state"],
                "decision_action": value["decision_action"],
                "manifest_sha256": value["manifest_sha256"],
                "file_sha256": file_hash(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("decision must be a JSON object")
    return value


def classify(value: Dict[str, Any]) -> str:
    if (
        value.get("schema_version")
        != "strict_v4_krc_downstream_decision_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("decision_revision")
        != "integrity_effect_separated_negative_branch_v2"
        or value.get("krc_audit_integrity_passes") is not True
    ):
        raise ValueError("canonical structurally valid KRC v2 decision required")
    if value.get("krc_effect_gate_passes") is True:
        if (
            value.get("selected_algorithm") != "krc_csr_caeos_v1"
            or value.get("downstream_execution_required") is not True
            or value.get("rrc_fallback_execution_permitted") is not False
        ):
            raise ValueError("inconsistent positive KRC decision")
        return "rrc_not_required"
    if value.get("krc_effect_gate_passes") is False:
        if (
            value.get("selected_algorithm") != "caeos_pairwise"
            or value.get("downstream_execution_required") is not False
            or value.get("rrc_fallback_execution_permitted") is not True
        ):
            raise ValueError("inconsistent terminal-negative KRC decision")
        return "run_rrc"
    raise ValueError("KRC effect gate terminal state required")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, required=True)
    args = parser.parse_args()
    print(classify(load_json(args.decision.resolve())))


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Any, Dict

import run_strict_v4_mdr_caeos_pilot as base
from create_strict_v4_external_confirmation_protocol import canonical_hash


def validate_protocol(value: Dict[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError("invalid MDR pilot v2 execution protocol")
    if value.get("execution_admitted") is not True:
        raise ValueError("MDR pilot v2 execution is not admitted")
    revision = value.get("protocol_revision", {})
    if (
        revision.get("complete_capture_count_before_revision") != 0
        or revision.get("algorithm_formula_changed") is not False
        or revision.get("fresh_run_and_result_roots_required") is not True
    ):
        raise ValueError("invalid MDR pilot v2 revision boundary")


def main() -> None:
    base.validate_protocol = validate_protocol
    base.main()


if __name__ == "__main__":
    main()

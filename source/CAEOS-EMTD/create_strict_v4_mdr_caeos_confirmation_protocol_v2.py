from __future__ import annotations

from typing import Any, Dict

import create_strict_v4_mdr_caeos_confirmation_protocol as base
from create_strict_v4_external_confirmation_protocol import canonical_hash


def validate_positive_pilot(
    design: Dict[str, Any],
    pilot_protocol: Dict[str, Any],
    selection: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
) -> None:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical MDR v2 design required")
    if (
        pilot_protocol.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        or pilot_protocol.get("manifest_sha256")
        != canonical_hash(pilot_protocol)
        or pilot_protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("invalid MDR pilot v2 protocol")
    if (
        selection.get("schema_version")
        != "strict_v4_mdr_caeos_weight_selection_v1"
        or selection.get("manifest_sha256") != canonical_hash(selection)
        or selection.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or selection.get("unknown_or_test_labels_used") is not False
    ):
        raise ValueError("invalid MDR pilot weight selection")
    if (
        summary.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or summary.get("weight_selection_manifest_sha256")
        != selection["manifest_sha256"]
        or summary.get("decision", {}).get(
            "expand_to_full102_confirmation"
        )
        is not True
    ):
        raise ValueError("positive canonical MDR pilot summary required")
    if (
        audit.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_audit_v2"
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit.get("passes") is not True
        or audit.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
        or audit.get("selection_manifest_sha256")
        != selection["manifest_sha256"]
    ):
        raise ValueError("passing canonical MDR pilot v2 audit required")


def create_protocol(*args, **kwargs):
    original = base.validate_positive_pilot
    try:
        base.validate_positive_pilot = validate_positive_pilot
        return base.create_protocol(*args, **kwargs)
    finally:
        base.validate_positive_pilot = original


def main() -> None:
    original = base.validate_positive_pilot
    try:
        base.validate_positive_pilot = validate_positive_pilot
        base.main()
    finally:
        base.validate_positive_pilot = original


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from clarify_strict_v4_krc_terminal_decision import (
    STRUCTURAL_CHECKS,
    build_clarification,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def write(path: Path, value: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")
    return value


def test_negative_krc_legacy_field_is_not_selection_mismatch(
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "summary.json"
    audit_path = tmp_path / "audit.json"
    summary = write(
        summary_path,
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_summary_v1"
            ),
            "passes": False,
            "authorize_external_safety_efficiency_confirmation": False,
            "selection": "caeos_pairwise",
        },
    )
    checks = {name: True for name in STRUCTURAL_CHECKS}
    checks["enabled_primary_suite_count_minimum"] = False
    write(
        audit_path,
        {
            "schema_version": "strict_v4_krc_csr_confirmation_audit_v1",
            "summary_manifest_sha256": summary["manifest_sha256"],
            "checks": checks,
            "passes": False,
            "decision_matches_summary": False,
        },
    )

    value = build_clarification(
        summary_path=summary_path,
        audit_path=audit_path,
    )

    assert value["all_structural_checks_pass"] is True
    assert value["effect_gate_failures"] == [
        "enabled_primary_suite_count_minimum"
    ]
    assert value["valid_negative_terminal"] is True
    assert value["no_summary_audit_selection_inconsistency"] is True
    assert value["claim_boundary"]["rrc_fallback_remains_required"] is True

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SCHEMA = "strict_v4_krc_terminal_decision_clarification_v1"
STRUCTURAL_CHECKS = (
    "protocol_task_count_306",
    "protocol_primary_task_count_264",
    "capture_universe_exact",
    "evaluation_universe_exact",
    "capture_contracts_pass",
    "evaluation_contracts_pass",
    "capture_file_hash_registry_exact",
    "evaluation_file_hash_registry_exact",
    "primary_numerical_recomputation_matches",
    "enabled_primary_identity_registry_exact",
    "reported_checks_match_independent_gate",
    "reported_passes_is_conjunction",
    "selection_obeys_frozen_rule",
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


def build_clarification(
    *,
    summary_path: Path,
    audit_path: Path,
) -> dict[str, Any]:
    summary = load(summary_path)
    audit = load(audit_path)
    require_canonical(
        summary,
        "strict_v4_krc_csr_confirmation_summary_v1",
        "KRC summary",
    )
    require_canonical(
        audit,
        "strict_v4_krc_csr_confirmation_audit_v1",
        "KRC audit",
    )
    if audit.get("summary_manifest_sha256") != summary["manifest_sha256"]:
        raise ValueError("KRC audit is not bound to summary")
    checks = audit.get("checks", {})
    structural = {
        name: checks.get(name) is True for name in STRUCTURAL_CHECKS
    }
    effect_failures = sorted(
        name
        for name, passed in checks.items()
        if name not in STRUCTURAL_CHECKS and passed is not True
    )
    expected_selection = (
        "krc_csr_caeos_v1"
        if summary.get("passes") is True
        else "caeos_pairwise"
    )
    legacy_definition = bool(
        audit.get("passes") is True and summary.get("passes") is True
    )
    negative_terminal = bool(
        summary.get("passes") is False
        and summary.get("authorize_external_safety_efficiency_confirmation")
        is False
        and summary.get("selection") == "caeos_pairwise"
        and audit.get("passes") is False
        and audit.get("decision_matches_summary") is False
    )
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "audit_manifest_sha256": audit["manifest_sha256"],
        "audit_file_sha256": file_hash(audit_path),
        "structural_checks": structural,
        "all_structural_checks_pass": all(structural.values()),
        "effect_gate_failures": effect_failures,
        "effect_gate_failure_count": len(effect_failures),
        "summary_effect_passes": summary.get("passes") is True,
        "audit_all_checks_pass": audit.get("passes") is True,
        "expected_selection_from_frozen_rule": expected_selection,
        "reported_selection": summary.get("selection"),
        "selection_is_consistent": summary.get("selection")
        == expected_selection,
        "legacy_decision_matches_summary": audit.get(
            "decision_matches_summary"
        ),
        "legacy_field_recomputed_from_its_definition": legacy_definition,
        "legacy_field_is_not_a_summary_audit_equality_check": True,
        "valid_negative_terminal": negative_terminal,
        "no_summary_audit_selection_inconsistency": bool(
            all(structural.values())
            and summary.get("selection") == expected_selection
            and audit.get("decision_matches_summary") is legacy_definition
        ),
        "claim_boundary": {
            "clarification_does_not_change_frozen_krc_effect_gate": True,
            "clarification_does_not_reclassify_krc_as_selected": True,
            "positive_average_signal_does_not_override_coverage_failure": True,
            "rrc_fallback_remains_required": negative_terminal,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build_clarification(
        summary_path=args.summary,
        audit_path=args.audit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "state": value["state"],
                "valid_negative_terminal": value[
                    "valid_negative_terminal"
                ],
                "effect_gate_failures": value["effect_gate_failures"],
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

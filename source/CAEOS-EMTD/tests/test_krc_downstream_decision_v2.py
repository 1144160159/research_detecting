from __future__ import annotations

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from finalize_strict_v4_krc_downstream_decision_v2 import (
    EFFECT_CHECKS,
    STRUCTURAL_CHECKS,
    decide,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(positive: bool):
    integrated = canonical(
        {
            "schema_version": (
                "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
            ),
            "protocol_revision": (
                "integrity_effect_separated_negative_branch_v2"
            ),
            "required_branches": {
                "krc_confirmation": {
                    "protocol_schema": (
                        "strict_v4_krc_csr_confirmation_protocol_v1"
                    ),
                    "summary_schema": (
                        "strict_v4_krc_csr_confirmation_summary_v1"
                    ),
                    "audit_schema": (
                        "strict_v4_krc_csr_confirmation_audit_v1"
                    ),
                }
            },
        }
    )
    protocol = canonical(
        {"schema_version": "strict_v4_krc_csr_confirmation_protocol_v1"}
    )
    summary = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_summary_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "passes": positive,
            "selection": (
                "krc_csr_caeos_v1" if positive else "caeos_pairwise"
            ),
            "authorize_external_safety_efficiency_confirmation": positive,
        }
    )
    checks = {
        **{name: True for name in STRUCTURAL_CHECKS},
        **{name: positive for name in EFFECT_CHECKS},
    }
    audit = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_audit_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_manifest_sha256": summary["manifest_sha256"],
            "checks": checks,
            "passes": positive,
            "decision_matches_summary": positive,
        }
    )
    return integrated, protocol, summary, audit


def test_realistic_negative_audit_writes_terminal_rrc_permission() -> None:
    integrated, protocol, summary, audit = fixtures(False)
    value = decide(
        integrated_protocol=integrated,
        confirmation_protocol=protocol,
        confirmation_summary=summary,
        confirmation_audit=audit,
        input_file_sha256={"input": "a" * 64},
    )
    assert value["krc_audit_integrity_passes"] is True
    assert value["krc_effect_gate_passes"] is False
    assert value["selected_algorithm"] == "caeos_pairwise"
    assert value["downstream_execution_required"] is False
    assert value["rrc_fallback_execution_permitted"] is True
    assert value["required_next_outputs"] == [
        "rrc_conditional_execution_protocol"
    ]


def test_positive_audit_activates_krc_downstream_only() -> None:
    integrated, protocol, summary, audit = fixtures(True)
    value = decide(
        integrated_protocol=integrated,
        confirmation_protocol=protocol,
        confirmation_summary=summary,
        confirmation_audit=audit,
        input_file_sha256={"input": "a" * 64},
    )
    assert value["krc_effect_gate_passes"] is True
    assert value["downstream_execution_required"] is True
    assert value["rrc_fallback_execution_permitted"] is False
    assert len(value["required_next_outputs"]) == 5


def test_negative_with_failed_structural_check_is_rejected() -> None:
    integrated, protocol, summary, audit = fixtures(False)
    audit["checks"][STRUCTURAL_CHECKS[0]] = False
    audit["manifest_sha256"] = canonical_hash(audit)
    with pytest.raises(ValueError):
        decide(
            integrated_protocol=integrated,
            confirmation_protocol=protocol,
            confirmation_summary=summary,
            confirmation_audit=audit,
            input_file_sha256={"input": "a" * 64},
        )

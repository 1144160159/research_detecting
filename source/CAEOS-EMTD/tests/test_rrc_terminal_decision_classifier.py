from __future__ import annotations

import pytest

from classify_strict_v4_rrc_terminal_decision import classify
from create_strict_v4_external_confirmation_protocol import canonical_hash


def decision(positive: bool):
    value = {
        "schema_version": "strict_v4_krc_downstream_decision_v1",
        "decision_revision": (
            "integrity_effect_separated_negative_branch_v2"
        ),
        "krc_audit_integrity_passes": True,
        "krc_effect_gate_passes": positive,
        "selected_algorithm": (
            "krc_csr_caeos_v1" if positive else "caeos_pairwise"
        ),
        "downstream_execution_required": positive,
        "rrc_fallback_execution_permitted": not positive,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_positive_krc_cancels_rrc():
    assert classify(decision(True)) == "rrc_not_required"


def test_valid_negative_krc_runs_rrc():
    assert classify(decision(False)) == "run_rrc"


def test_structural_or_branch_drift_is_rejected():
    value = decision(False)
    value["rrc_fallback_execution_permitted"] = False
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError):
        classify(value)

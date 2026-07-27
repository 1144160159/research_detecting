from create_strict_v4_external_confirmation_protocol import canonical_hash
from audit_strict_v4_mdr_external_malicious import audit


def fixture(effect=False):
    protocol = {
        "manifest_sha256": "p" * 64,
        "expected_formal_runs": 12,
    }
    summary = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_summary_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": "mdr_caeos_v1",
        "primary_comparator": "opendetect",
        "formal_run_count": 12,
        "failure_count": 0,
        "validation": {"passes": effect},
        "fresh_two_dataset_external_malicious_confirmation_passes": (
            effect
        ),
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    return protocol, summary


def run(protocol, summary, recomputed=None):
    return audit(
        protocol=protocol,
        recorded=summary,
        recomputed=summary if recomputed is None else recomputed,
        protocol_file_sha256="1" * 64,
        summary_file_sha256="2" * 64,
        auditor_sha256="3" * 64,
    )


def test_integrity_audit_can_pass_when_effect_gate_fails():
    protocol, summary = fixture(False)
    result = run(protocol, summary)
    assert result["passes"] is True
    assert result["external_effect_gate_passes"] is False
    assert result["manifest_sha256"] == canonical_hash(result)


def test_positive_effect_boolean_is_preserved():
    protocol, summary = fixture(True)
    result = run(protocol, summary)
    assert result["passes"] is True
    assert result["external_effect_gate_passes"] is True


def test_recomputation_mismatch_fails_audit():
    protocol, summary = fixture(False)
    recomputed = dict(summary)
    recomputed["failure_count"] = 1
    result = run(protocol, summary, recomputed)
    assert result["passes"] is False
    assert not result["checks"]["recorded_summary_exactly_recomputed"]


def test_noncanonical_summary_is_rejected():
    import pytest

    protocol, summary = fixture(False)
    summary["formal_run_count"] = 13
    with pytest.raises(ValueError, match="canonical"):
        run(protocol, summary)

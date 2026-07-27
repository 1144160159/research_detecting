import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_external_malicious_execution_protocol import (
    validate_positive_confirmation,
)


def canonical(value):
    value = copy.deepcopy(value)
    value["manifest_sha256"] = canonical_hash(value)
    return value


def positive_fixture():
    protocol = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_protocol_v1"
            )
        }
    )
    summary = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_summary_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "passes": True,
            "authorize_external_safety_efficiency_confirmation": True,
            "selection": "krc_csr_caeos_v1",
        }
    )
    audit = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_audit_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_manifest_sha256": summary["manifest_sha256"],
            "passes": True,
            "decision_matches_summary": True,
        }
    )
    return protocol, summary, audit


def test_positive_confirmation_is_admitted():
    protocol, summary, audit = positive_fixture()
    validate_positive_confirmation(protocol, summary, audit)


@pytest.mark.parametrize(
    ("document", "field", "value"),
    [
        ("summary", "passes", False),
        ("summary", "selection", "caeos_pairwise"),
        ("audit", "passes", False),
        ("audit", "decision_matches_summary", False),
    ],
)
def test_nonpositive_or_mismatched_confirmation_is_rejected(
    document, field, value
):
    protocol, summary, audit = positive_fixture()
    target = summary if document == "summary" else audit
    target[field] = value
    target["manifest_sha256"] = canonical_hash(target)
    if document == "summary":
        audit["summary_manifest_sha256"] = target["manifest_sha256"]
        audit["manifest_sha256"] = canonical_hash(audit)
    with pytest.raises(ValueError, match="positive canonical"):
        validate_positive_confirmation(protocol, summary, audit)

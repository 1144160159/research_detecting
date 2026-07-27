import numpy as np

from evaluate_krc_csr_selection import select


def canonical(value):
    from create_strict_v4_external_confirmation_protocol import canonical_hash

    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(enabled):
    protocol = canonical(
        {
            "schema_version": "strict_v4_krc_csr_development_protocol_v1",
            "source_exact_replay_protocol_manifest_sha256": "r" * 64,
            "source_evaluation_file_sha256": {
                "suite/scenario/clean": "f" * 64
            },
        }
    )
    certificate = canonical(
        {
            "schema_version": "strict_v4_krc_csr_certificate_v1",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "suite": "suite",
            "scenario": "scenario",
            "routing_enabled": enabled,
        }
    )
    source = canonical(
        {
            "schema_version": "strict_v4_csr_caeos_pilot_evaluation_v1",
            "algorithm": "csr_caeos_v1",
            "runtime_revision": "exact_clean_probability_replay_v2",
            "repair_protocol_manifest_sha256": "r" * 64,
            "suite": "suite",
            "scenario": "scenario",
            "condition": "clean",
            "routing": {
                "active_count": 3,
                "active_rate": 0.3,
                "missing_count": 1,
                "missing_rate": 0.1,
            },
            "pairwise_report": {"unknown_auroc": 0.4},
            "candidate_report": {"unknown_auroc": 0.7},
        }
    )
    return protocol, certificate, source


def test_disabled_certificate_materializes_exact_pairwise_report():
    protocol, certificate, source = fixtures(False)
    value = select(
        protocol,
        certificate,
        source,
        source_file_sha256="f" * 64,
    )
    assert value["candidate_report"] == value["pairwise_report"]
    assert value["routing"]["active_count"] == 0
    assert value["routing"]["inactive_risk_exactly_pairwise"] is True


def test_enabled_certificate_preserves_source_csr_report():
    protocol, certificate, source = fixtures(True)
    value = select(
        protocol,
        certificate,
        source,
        source_file_sha256="f" * 64,
    )
    assert value["candidate_report"] == source["candidate_report"]
    assert value["routing"] == source["routing"]

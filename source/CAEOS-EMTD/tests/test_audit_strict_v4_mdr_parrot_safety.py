from copy import deepcopy

from audit_strict_v4_mdr_parrot_safety import evaluate_audit
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def values(safety=True):
    protocol = canonical(
        {"schema_version": "strict_v4_mdr_parrot_safety_protocol_v1"}
    )
    recomputed = {
        "model_pair_count": 30,
        "capture_count": 320,
        "application_count": 80,
        "failure_count": 0,
        "capture_blocks": [],
        "application_records": [],
        "applications_with_false_alert_rate_at_most_0_20_fraction": 1.0,
        "capture_block_inference": {},
        "candidate_minus_source_benign_inference": {},
        "source_benign_model_reference_values": [],
        "confirmation_checks": {"all": safety},
        "safety_gate_passes": safety,
        "_records": [
            {
                "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": False,
                "payload_decryption_used": False,
            }
        ],
    }
    summary = canonical(
        {
            "schema_version": "strict_v4_mdr_parrot_safety_summary_v1",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            **{
                key: value
                for key, value in recomputed.items()
                if key != "_records"
            },
        }
    )
    return protocol, summary, recomputed


def test_audit_separates_integrity_and_scientific_safety_gate():
    protocol, summary, recomputed = values(safety=False)
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        metrics_hashes_match=True,
        feature_shards_match=True,
    )
    assert result["passes"] is True
    assert result["benign_domain_shift_safety_gate_passes"] is False
    assert (
        result["claim_boundary"][
            "malicious_detection_accuracy_claim_supported_by_this_audit"
        ]
        is False
    )


def test_audit_rejects_recomputed_drift():
    protocol, summary, recomputed = values()
    drifted = deepcopy(recomputed)
    drifted["capture_count"] = 319
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=drifted,
        implementation_hashes_match=True,
        metrics_hashes_match=True,
        feature_shards_match=True,
    )
    assert result["passes"] is False


def test_audit_passes_benign_safety_without_overclaim():
    protocol, summary, recomputed = values()
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        metrics_hashes_match=True,
        feature_shards_match=True,
    )
    assert result["passes"] is True
    assert result["benign_domain_shift_safety_gate_passes"] is True
    assert result["claim_boundary"]["parrot_accuracy_or_sota_claim_supported"] is False

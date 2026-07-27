from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_krc_parrot_safety import aggregate


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixture(rate=0.05):
    sources = [
        {
            "scenario": f"scenario{scenario}",
            "training_seed": seed,
        }
        for scenario in range(10)
        for seed in (647, 653, 659)
    ]
    captures = [
        {
            "capture_id": f"capture{index}",
            "application": f"app{index // 4}",
        }
        for index in range(320)
    ]
    protocol = canonical(
        {
            "schema_version": "strict_v4_krc_parrot_safety_protocol_v1",
            "source_model_pairs": sources,
            "parrot_captures": captures,
            "aggregation": {
                "capture_block_bootstrap_repetitions": 100,
                "capture_block_bootstrap_seed": 20260726,
            },
            "confirmation_gate": {
                "all_320_captures_and_80_applications_covered": True,
                "applications_with_false_alert_rate_at_most_0_20_minimum_fraction": 0.9,
                "candidate_false_alert_minus_source_benign_95ci_upper_maximum": 0.05,
                "candidate_false_alert_rate_bootstrap_95ci_upper_maximum": 0.1,
                "candidate_known_attack_assignment_95ci_upper_maximum": 0.05,
                "candidate_minus_opendetect_false_alert_95ci_upper_maximum": 0.02,
                "failure_count_zero": True,
                "forbidden_fit_selection_or_threshold_use_observed": False,
            },
        }
    )
    metrics = []
    for source in sources:
        records = []
        for capture in captures:
            method = {
                "false_alert_rate": rate,
                "known_attack_assignment_rate": rate / 2,
                "reject_rate": rate,
                "operational_intervention_rate": rate,
            }
            records.append(
                {
                    **capture,
                    "flow_row_count": 10,
                    "krc_csr_caeos_v1": method,
                    "opendetect": {**method, "false_alert_rate": 0.05},
                }
            )
        metrics.append(
            canonical(
                {
                    "schema_version": (
                        "strict_v4_krc_parrot_model_pair_metrics_v1"
                    ),
                    "state": "complete",
                    "protocol_manifest_sha256": protocol[
                        "manifest_sha256"
                    ],
                    "source": source,
                    "source_benign_reference": {
                        "false_alert_rate": 0.04
                    },
                    "capture_count": 320,
                    "records": records,
                    "failure_count": 0,
                    "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": False,
                    "payload_decryption_used": False,
                    "candidate_model_refit_for_parrot": False,
                }
            )
        )
    return protocol, metrics


def test_aggregate_passes_frozen_benign_safety_gates():
    protocol, metrics = fixture()
    result = aggregate(metrics, protocol)
    assert result["model_pair_count"] == 30
    assert result["application_count"] == 80
    assert result["safety_gate_passes"] is True
    assert "krc_csr_caeos_v1_false_alert_rate" in result[
        "capture_block_inference"
    ]


def test_aggregate_preserves_false_alert_failure():
    protocol, metrics = fixture(rate=0.25)
    result = aggregate(metrics, protocol)
    assert result["safety_gate_passes"] is False
    assert (
        result["confirmation_checks"][
            "candidate_false_alert_rate_bootstrap_95ci_upper_maximum"
        ]
        is False
    )

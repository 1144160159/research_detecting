import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_mdr_parrot_safety import (
    aggregate,
    bootstrap_independent_difference,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def protocol():
    sources = [
        {"scenario": f"scenario{scenario}", "training_seed": seed}
        for scenario in range(10)
        for seed in (137, 139, 149)
    ]
    captures = [
        {
            "capture_id": f"capture{index}",
            "application": f"app{index // 4}",
        }
        for index in range(320)
    ]
    value = {
        "schema_version": "strict_v4_mdr_parrot_safety_protocol_v1",
        "source_model_pairs": sources,
        "parrot_captures": captures,
        "aggregation": {
            "capture_block_bootstrap_repetitions": 100,
            "capture_block_bootstrap_seed": 20260724,
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
    value["manifest_sha256"] = canonical_hash(value)
    return value


def metrics(rate=0.05, comparator_rate=0.05):
    frozen = protocol()
    values = []
    for source in frozen["source_model_pairs"]:
        records = []
        for capture in frozen["parrot_captures"]:
            method = {
                "false_alert_rate": rate,
                "known_attack_assignment_rate": rate / 2,
                "reject_rate": rate,
                "operational_intervention_rate": rate,
            }
            comparator = {
                **method,
                "false_alert_rate": comparator_rate,
            }
            records.append(
                {
                    **capture,
                    "flow_row_count": 10,
                    "mdr_caeos_v1": method,
                    "opendetect": comparator,
                }
            )
        values.append(
            canonical(
                {
                    "schema_version": (
                        "strict_v4_mdr_parrot_model_pair_metrics_v1"
                    ),
                    "state": "complete",
                    "protocol_manifest_sha256": frozen["manifest_sha256"],
                    "source": {
                        "scenario": source["scenario"],
                        "training_seed": source["training_seed"],
                    },
                    "source_benign_reference": {
                        "false_alert_rate": 0.04
                    },
                    "capture_count": 320,
                    "records": records,
                    "failure_count": 0,
                    "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": False,
                    "payload_decryption_used": False,
                }
            )
        )
    return frozen, values


def test_independent_difference_is_oriented_left_minus_right():
    value = bootstrap_independent_difference(
        [0.1, 0.1],
        [0.04, 0.04],
        seed=1,
        repetitions=10,
    )
    assert value["mean_difference"] == pytest.approx(0.06)


def test_aggregate_passes_frozen_safety_gates():
    frozen, values = metrics()
    result = aggregate(values, frozen)
    assert result["model_pair_count"] == 30
    assert result["capture_count"] == 320
    assert result["application_count"] == 80
    assert result["safety_gate_passes"] is True


def test_aggregate_preserves_false_alert_failure():
    frozen, values = metrics(rate=0.25)
    result = aggregate(values, frozen)
    assert result["safety_gate_passes"] is False
    assert (
        result["confirmation_checks"][
            "candidate_false_alert_rate_bootstrap_95ci_upper_maximum"
        ]
        is False
    )

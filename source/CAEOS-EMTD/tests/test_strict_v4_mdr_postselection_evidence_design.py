from __future__ import annotations

from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_postselection_evidence_design import create_design


def canonical(schema: str, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    return {
        "mdr_design": canonical(
            "strict_v4_mdr_caeos_design_v2",
            reserved_confirmation={
                "scenario_count": 102,
                "training_seeds": [347, 349, 353],
                "corruption_seeds": [359, 367, 373],
                "expected_evaluations": 1836,
                "conditions": [
                    "clean",
                    "modality_missing",
                    "field_missing",
                    "row_missing",
                    "feature_shuffle",
                    "gaussian_drift",
                ],
            },
        ),
        "external_design": canonical(
            "gpu_external_dataset_evaluation_design_protocol_v1",
            formal_metric_count_at_freeze=0,
            datasets=["LSNM2024", "CICDDoS2019"],
            seeds=[223, 227, 229],
            split_rule="grouped",
            scenario_rule="leave_one_attack_out",
            confirmation_gate={"all_metrics": True},
        ),
        "efficiency": canonical(
            "strict_v4_final_efficiency_protocol_v2",
            efficiency_metrics_observed_at_freeze=0,
            inference_benchmark={"batch_sizes": [1, 64, 512]},
        ),
        "parrot_design": canonical(
            "parrot2025_external_benign_safety_design_v1",
            formal_model_metric_count_at_freeze=0,
            confirmation_gate={"false_alert": True},
        ),
        "parrot_features": canonical(
            "parrot2025_full_no_decryption_feature_protocol_v1",
            capture_count=320,
            application_count=80,
        ),
    }


def build(values, counts=None):
    return create_design(
        project_root=Path("/project"),
        input_file_sha256={"input": "1" * 64},
        implementation_sha256={"creator": "2" * 64},
        observed_output_counts=counts or {"external": 0, "system": 0},
        **values,
    )


def test_design_freezes_two_non_spliceable_claim_tiers():
    result = build(inputs())
    assert (
        result["activation_gate"]["selected_algorithm_must_equal"]
        == "mdr_caeos_v1"
    )
    assert result["accuracy_and_robustness_evidence"]["capture_count"] == 306
    assert result["fresh_external_malicious_evidence"]["datasets"] == [
        "LSNM2024",
        "CICDDoS2019",
    ]
    assert (
        result["external_benign_safety_evidence"][
            "may_not_support_malicious_accuracy_or_sota_claims"
        ]
        is True
    )
    policy = result["integrated_claim_policy"]
    assert "strict_efficiency_superiority_over_opendetect" in policy[
        "multidimensional_comprehensive_sota_additionally_requires"
    ]
    assert result["manifest_sha256"] == canonical_hash(result)


def test_design_rejects_any_postselection_output():
    with pytest.raises(ValueError, match="before its outputs"):
        build(inputs(), {"external": 1, "system": 0})


def test_design_rejects_wrong_confirmation_universe():
    values = inputs()
    values["mdr_design"]["reserved_confirmation"]["scenario_count"] = 101
    values["mdr_design"]["manifest_sha256"] = canonical_hash(
        values["mdr_design"]
    )
    with pytest.raises(ValueError, match="full102x3"):
        build(values)


def test_design_rejects_noncanonical_input():
    values = inputs()
    values["external_design"]["datasets"] = ["changed"]
    with pytest.raises(ValueError, match="canonical SHA"):
        build(values)

from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_external_malicious_design import create_design


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def values():
    gate = {"all_four_oriented_means_strictly_positive": True}
    contract = {
        "datasets": ["LSNM2024", "CICDDoS2019"],
        "seeds": [223, 227, 229],
        "scenario_rule": "leave_one_attack_out",
        "split_rule": "fingerprint_grouped",
        "primary_comparator": "opendetect",
        "confirmation_gate": gate,
    }
    return {
        "postselection": canonical(
            "strict_v4_mdr_postselection_evidence_design_v1",
            activation_gate={"selected_algorithm_must_equal": "mdr_caeos_v1"},
            fresh_external_malicious_evidence=contract,
        ),
        "mdr_design": canonical(
            "strict_v4_mdr_caeos_design_v2",
            mechanism={
                "training_sample_fraction": 0.25,
                "health_gate": {"quantile": 0.99},
            },
        ),
        "external_v1": canonical(
            "gpu_external_dataset_evaluation_design_protocol_v1",
            datasets=contract["datasets"],
            seeds=contract["seeds"],
            confirmation_gate=gate,
            opendetect_policy={"epochs": 100},
            formal_metrics=[
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
        ),
    }


def build(items, observed=0):
    return create_design(
        project_root=Path("/project"),
        input_file_sha256={"parent": "1" * 64},
        creator_sha256="2" * 64,
        observed_metrics=observed,
        **items,
    )


def test_external_design_freezes_fresh_mdr_contract():
    result = build(values())
    assert result["datasets"] == ["LSNM2024", "CICDDoS2019"]
    assert result["seeds"] == [223, 227, 229]
    assert result["mdr_policy"]["weight_may_not_be_reselected_on_external_data"]
    assert (
        result["mdr_policy"][
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing"
        ]
        is False
    )
    assert result["manifest_sha256"] == canonical_hash(result)


def test_external_design_rejects_observed_metrics():
    with pytest.raises(ValueError, match="before metrics"):
        build(values(), observed=1)


def test_external_design_rejects_parent_drift():
    items = values()
    items["postselection"]["fresh_external_malicious_evidence"]["seeds"] = [
        223
    ]
    items["postselection"]["manifest_sha256"] = canonical_hash(
        items["postselection"]
    )
    with pytest.raises(ValueError, match="parent contract"):
        build(items)


def test_external_design_rejects_noncanonical_source():
    items = values()
    items["external_v1"]["seeds"] = [1, 2, 3]
    with pytest.raises(ValueError, match="canonical SHA"):
        build(items)

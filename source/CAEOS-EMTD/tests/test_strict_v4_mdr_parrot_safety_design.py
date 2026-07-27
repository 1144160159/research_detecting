from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_parrot_safety_design import create_design


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    gate = {
        "all_320_captures_and_80_applications_covered": True,
        "candidate_false_alert_rate_bootstrap_95ci_upper_maximum": 0.1,
    }
    postselection = canonical(
        "strict_v4_mdr_postselection_evidence_design_v1",
        activation_gate={"selected_algorithm_must_equal": "mdr_caeos_v1"},
        external_benign_safety_evidence={
            "capture_count": 320,
            "application_count": 80,
            "confirmation_gate": gate,
        },
    )
    parrot_design = canonical(
        "parrot2025_external_benign_safety_design_v1",
        confirmation_gate=gate,
        formal_metrics={"false_alert_rate": "mean"},
    )
    captures = [
        {
            "capture_id": f"capture{index}",
            "application": f"app{index // 4}",
        }
        for index in range(320)
    ]
    features = canonical(
        "parrot2025_full_no_decryption_feature_protocol_v1",
        capture_count=320,
        application_count=80,
        feature_count=56,
        captures=captures,
        formal_model_metric_count_at_freeze=0,
        safety_policy={"payload_decryption": False},
    )
    registry = [
        {
            "suite": "ustc_tfc2016",
            "scenario": f"scenario{scenario}",
            "seed": seed,
        }
        for scenario in range(10)
        for seed in (137, 139, 149)
    ]
    comparative = canonical(
        "strict_v4_comparative_corruption_protocol_v2",
        source_registry=registry,
    )
    mdr = canonical("strict_v4_mdr_caeos_design_v2")
    return postselection, parrot_design, features, comparative, mdr


def make_design(tmp_path: Path, **overrides):
    postselection, parrot, features, comparative, mdr = inputs()
    values = {
        "project_root": tmp_path,
        "postselection": postselection,
        "parrot_design": parrot,
        "feature_protocol": features,
        "comparative": comparative,
        "mdr_design": mdr,
        "input_file_sha256": {"design": "a"},
        "creator_sha256": "b",
        "observed_metrics": 0,
    }
    values.update(overrides)
    return create_design(**values)


def test_design_freezes_30_model_pairs_and_320_captures(tmp_path):
    value = make_design(tmp_path)
    assert value["source_model_matrix"]["model_pairs"] == 30
    assert value["population"]["capture_count"] == 320
    assert value["population"]["payload_decryption"] is False
    assert value["manifest_sha256"] == canonical_hash(value)


def test_design_rejects_existing_metrics(tmp_path):
    with pytest.raises(ValueError, match="before metrics"):
        make_design(tmp_path, observed_metrics=1)


def test_design_rejects_missing_ustc_source(tmp_path):
    values = list(inputs())
    comparative = dict(values[3])
    comparative["source_registry"] = comparative["source_registry"][:-1]
    comparative["manifest_sha256"] = canonical_hash(comparative)
    with pytest.raises(ValueError, match="10x3"):
        make_design(tmp_path, comparative=comparative)


def test_design_rejects_decryption_policy(tmp_path):
    values = list(inputs())
    features = dict(values[2])
    features["safety_policy"] = {"payload_decryption": True}
    features["manifest_sha256"] = canonical_hash(features)
    with pytest.raises(ValueError, match="no-decryption"):
        make_design(tmp_path, feature_protocol=features)

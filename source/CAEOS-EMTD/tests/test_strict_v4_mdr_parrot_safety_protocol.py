from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_parrot_safety_protocol import create_protocol


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    design = canonical(
        "strict_v4_mdr_parrot_safety_design_v1",
        required_implementation=["protocol.py"],
        formal_metrics={"false_alert_rate": "mean"},
        confirmation_gate={"failure_count_zero": True},
        aggregation={"capture_block_bootstrap_repetitions": 10000},
        leakage_policy={"parrot_features_used_for_model_fit": False},
        claim_boundary={"does_not_allow_malicious_detection_accuracy_claim": True},
    )
    confirmation_protocol = canonical(
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        selected_augmentation_weight=0.25,
        confirmation={
            "training_sample_fraction": 0.25,
            "health_quantile": 0.95,
        },
    )
    confirmation_summary = canonical(
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        decision={"passes": True},
    )
    confirmation_audit = canonical(
        "strict_v4_mdr_caeos_confirmation_audit_v1", passes=True
    )
    selection = canonical(
        "strict_v4_final_self_algorithm_selection_v2",
        selected_algorithm="mdr_caeos_v1",
        mdr_confirmation_passes=True,
        protocol_manifest_sha256=confirmation_protocol["manifest_sha256"],
        summary_manifest_sha256=confirmation_summary["manifest_sha256"],
    )
    captures = [
        {
            "capture_id": f"capture{index}",
            "application": f"app{index // 4}",
        }
        for index in range(320)
    ]
    feature_protocol = canonical(
        "parrot2025_full_no_decryption_feature_protocol_v1",
        output_root="/tmp/parrot",
        captures=captures,
        feature_columns=[f"f{index}" for index in range(56)],
        metadata_columns=["CaptureGroup", "Application", "Role"],
    )
    feature_summary = canonical(
        "parrot2025_full_no_decryption_feature_summary_v1",
        protocol_manifest_sha256=feature_protocol["manifest_sha256"],
        capture_count=320,
        application_count=80,
        passed=True,
        validation={"all_present": True},
        shard_manifest_sha256={item["capture_id"]: "a" for item in captures},
    )
    comparative = canonical(
        "strict_v4_comparative_corruption_protocol_v2"
    )
    sources = [
        {
            "scenario": f"scenario{scenario}",
            "training_seed": seed,
        }
        for scenario in range(10)
        for seed in (137, 139, 149)
    ]
    return (
        design,
        selection,
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
        feature_protocol,
        feature_summary,
        comparative,
        sources,
    )


def make_protocol(tmp_path: Path, **overrides):
    values = inputs()
    arguments = {
        "project_root": tmp_path,
        "run_root": tmp_path / "run",
        "design": values[0],
        "selection": values[1],
        "confirmation_protocol": values[2],
        "confirmation_summary": values[3],
        "confirmation_audit": values[4],
        "feature_protocol": values[5],
        "feature_summary": values[6],
        "comparative": values[7],
        "sources": values[8],
        "implementation_sha256": {"protocol.py": "a"},
        "input_file_sha256": {"design": "b"},
        "observed_metrics": 0,
    }
    arguments.update(overrides)
    return create_protocol(**arguments)


def test_protocol_freezes_30_pairs_and_320_captures(tmp_path):
    value = make_protocol(tmp_path)
    assert value["source_model_pair_count"] == 30
    assert value["capture_count"] == 320
    assert value["mdr_policy"]["weight_reselected_on_parrot"] is False
    assert value["manifest_sha256"] == canonical_hash(value)


def test_protocol_rejects_existing_metrics(tmp_path):
    with pytest.raises(ValueError, match="before metrics"):
        make_protocol(tmp_path, observed_metrics=1)


def test_protocol_rejects_non_mdr_selection(tmp_path):
    values = inputs()
    selection = dict(values[1])
    selection["selected_algorithm"] = "caeos_pairwise"
    selection["manifest_sha256"] = canonical_hash(selection)
    with pytest.raises(ValueError, match="positive canonical"):
        make_protocol(tmp_path, selection=selection)


def test_protocol_rejects_incomplete_features(tmp_path):
    values = inputs()
    summary = dict(values[6])
    summary["validation"] = {"all_present": False}
    summary["manifest_sha256"] = canonical_hash(summary)
    with pytest.raises(ValueError, match="complete canonical"):
        make_protocol(tmp_path, feature_summary=summary)

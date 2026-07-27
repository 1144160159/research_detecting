from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_opendetect_efficiency_design import create_design


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    postselection = canonical(
        "strict_v4_mdr_postselection_evidence_design_v1",
        activation_gate={"selected_algorithm_must_equal": "mdr_caeos_v1"},
    )
    selected = canonical(
        "strict_v4_mdr_selected_system_design_v1",
        same_hardware_inference={
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
        },
    )
    registry = [
        {
            "suite": f"suite{scenario // 17}",
            "scenario": f"scenario{scenario}",
            "seed": 137,
        }
        for scenario in range(102)
    ]
    comparative = canonical(
        "strict_v4_comparative_corruption_protocol_v2",
        source_registry=registry,
    )
    efficiency = canonical("strict_v4_final_efficiency_protocol_v2")
    return postselection, selected, comparative, efficiency


def make_design(tmp_path: Path, **overrides):
    postselection, selected, comparative, efficiency = inputs()
    values = {
        "project_root": tmp_path,
        "postselection": postselection,
        "selected_system": selected,
        "comparative": comparative,
        "efficiency_v2": efficiency,
        "input_file_sha256": {"design": "a"},
        "creator_sha256": "b",
        "observed_outputs": 0,
    }
    values.update(overrides)
    return create_design(**values)


def test_design_freezes_306_by_102_matrix(tmp_path):
    value = make_design(tmp_path)
    assert value["source_matrix"]["candidate_capture_count"] == 306
    assert value["source_matrix"]["comparator_runtime_count"] == 102
    assert value["benchmark"]["batch_sizes"] == [1, 64, 512]
    assert value["manifest_sha256"] == canonical_hash(value)


def test_design_rejects_existing_outputs(tmp_path):
    with pytest.raises(ValueError, match="zero outputs"):
        make_design(tmp_path, observed_outputs=1)


def test_design_rejects_incomplete_opendetect_registry(tmp_path):
    values = inputs()
    comparative = dict(values[2])
    comparative["source_registry"] = comparative["source_registry"][:-1]
    comparative["manifest_sha256"] = canonical_hash(comparative)
    with pytest.raises(ValueError, match="102"):
        make_design(tmp_path, comparative=comparative)

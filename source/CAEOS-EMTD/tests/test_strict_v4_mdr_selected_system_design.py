from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_selected_system_design import create_design


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def values():
    system = {
        "deployment_equivalence": {"prediction_array_identity_required": True},
        "same_hardware_benchmark": {
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "reported_metrics": ["latency_p99_ms"],
        },
        "deployability_gate": {"all_outputs_finite": True},
        "strict_efficiency_superiority_gate": {
            "all_latency_ratio_bootstrap_upper_bounds_le_1": True
        },
    }
    return {
        "postselection": canonical(
            "strict_v4_mdr_postselection_evidence_design_v1",
            activation_gate={"selected_algorithm_must_equal": "mdr_caeos_v1"},
            selected_system_evidence=system,
        ),
        "mdr_design": canonical(
            "strict_v4_mdr_caeos_design_v2",
            reserved_confirmation={
                "scenario_count": 102,
                "training_seeds": [347, 349, 353],
            },
        ),
        "efficiency_v2": canonical(
            "strict_v4_final_efficiency_protocol_v2"
        ),
    }


def build(items, observed=0):
    return create_design(
        project_root=Path("/project"),
        input_file_sha256={"input": "1" * 64},
        creator_sha256="2" * 64,
        observed_outputs=observed,
        **items,
    )


def test_system_design_separates_deployability_and_efficiency():
    result = build(values())
    assert result["source_runtime_contract"]["expected_capture_count"] == 306
    assert result["aggregation"]["scenario_block_count"] == 102
    assert (
        result["claim_boundary"][
            "deployability_pass_does_not_imply_efficiency_sota"
        ]
        is True
    )
    assert result["manifest_sha256"] == canonical_hash(result)


def test_system_design_rejects_observed_output():
    with pytest.raises(ValueError, match="before outputs"):
        build(values(), observed=1)


def test_system_design_rejects_parent_drift():
    items = values()
    items["mdr_design"]["reserved_confirmation"]["training_seeds"] = [1, 2, 3]
    items["mdr_design"]["manifest_sha256"] = canonical_hash(
        items["mdr_design"]
    )
    with pytest.raises(ValueError, match="parent contract"):
        build(items)


def test_system_design_rejects_noncanonical_input():
    items = values()
    items["efficiency_v2"]["changed"] = True
    with pytest.raises(ValueError, match="canonical SHA"):
        build(items)

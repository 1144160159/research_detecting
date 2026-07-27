from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_selected_system_protocol import create_protocol


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    design = canonical(
        "strict_v4_mdr_selected_system_design_v1",
        required_implementation=[
            "create_strict_v4_mdr_selected_system_protocol.py"
        ],
        same_hardware_inference={
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
        },
        aggregation={"bootstrap_repetitions": 10000},
        deployability_gate={"all_outputs_finite": True},
        strict_efficiency_superiority_gate={
            "all_latency_ratio_bootstrap_upper_bounds_le_1": True
        },
        training_and_artifact_cost={"reported_as_lower_bound": True},
        claim_boundary={"no_splicing": True},
    )
    confirmation_protocol = canonical(
        "strict_v4_mdr_caeos_confirmation_protocol_v1"
    )
    confirmation_summary = canonical(
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        decision={"passes": True},
    )
    confirmation_audit = canonical(
        "strict_v4_mdr_caeos_confirmation_audit_v1",
        passes=True,
        protocol_manifest_sha256=confirmation_protocol["manifest_sha256"],
        summary_manifest_sha256=confirmation_summary["manifest_sha256"],
    )
    selection = canonical(
        "strict_v4_final_self_algorithm_selection_v2",
        selected_algorithm="mdr_caeos_v1",
        mdr_confirmation_passes=True,
        protocol_manifest_sha256=confirmation_protocol["manifest_sha256"],
        summary_manifest_sha256=confirmation_summary["manifest_sha256"],
    )
    sources = []
    for scenario in range(102):
        for seed in (347, 349, 353):
            sources.append(
                {
                    "suite": f"suite{scenario // 17}",
                    "scenario": f"scenario{scenario}",
                    "training_seed": seed,
                }
            )
    return (
        design,
        selection,
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
        sources,
    )


def make_protocol(tmp_path: Path, **overrides):
    (
        design,
        selection,
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
        sources,
    ) = inputs()
    arguments = {
        "project_root": tmp_path,
        "run_root": tmp_path / "run",
        "design": design,
        "selection": selection,
        "confirmation_protocol": confirmation_protocol,
        "confirmation_summary": confirmation_summary,
        "confirmation_audit": confirmation_audit,
        "sources": sources,
        "implementation_sha256": {
            "create_strict_v4_mdr_selected_system_protocol.py": "a"
        },
        "input_file_sha256": {"design": "b"},
        "observed_benchmarks": 0,
    }
    arguments.update(overrides)
    return create_protocol(**arguments)


def test_protocol_freezes_306_sources_and_benchmark_policy(tmp_path):
    protocol = make_protocol(tmp_path)
    assert protocol["source_count"] == 306
    assert protocol["benchmark"]["batch_sizes"] == [1, 64, 512]
    assert protocol["benchmark"]["gpu_used"] is False
    assert protocol["manifest_sha256"] == canonical_hash(protocol)


def test_protocol_rejects_existing_outputs(tmp_path):
    with pytest.raises(ValueError, match="before outputs"):
        make_protocol(tmp_path, observed_benchmarks=1)


def test_protocol_rejects_non_mdr_selection(tmp_path):
    values = list(inputs())
    selection = dict(values[1])
    selection["selected_algorithm"] = "caeos_pairwise"
    selection["manifest_sha256"] = canonical_hash(selection)
    with pytest.raises(ValueError, match="positive canonical"):
        make_protocol(tmp_path, selection=selection)


def test_protocol_rejects_duplicate_source_identity(tmp_path):
    sources = list(inputs()[-1])
    sources[-1] = dict(sources[0])
    with pytest.raises(ValueError, match="306 captures"):
        make_protocol(tmp_path, sources=sources)

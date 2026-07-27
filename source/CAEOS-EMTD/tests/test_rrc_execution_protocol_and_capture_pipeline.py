from __future__ import annotations

from pathlib import Path

import pytest

import create_strict_v4_rrc_csr_execution_protocol as creator
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_rrc_csr_capture_pipeline import (
    group_tasks,
    require_empty_or_absent,
    validate_protocol,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(tmp_path: Path):
    design = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_fallback_design_v1",
            "execution_admitted": False,
            "certificate": {"known_only": True},
            "confirmation": {
                "bootstrap_replicates": 10000,
                "bootstrap_seed": 20260727,
                "primary_enabled_scenario_count_minimum": 18,
                "primary_enabled_suite_count_minimum": 4,
                "overall_directed_means_strictly_positive": True,
                "suite_nonnegative_count_minimum_each_metric": 5,
                "each_family_metric_regression_maximum": 0.02,
                "modality_missing_composite_improves": True,
                "gaussian_drift_composite_improves": True,
            },
        }
    )
    source_registry = [
        {"suite": f"suite{index % 7}", "scenario": f"scenario{index}"}
        for index in range(83)
    ]
    tasks = [
        {
            "suite": source["suite"],
            "scenario": source["scenario"],
            "training_seed": training_seed,
            "corruption_seed": corruption_seed,
        }
        for source in source_registry
        for training_seed, corruption_seed in zip(
            [701, 709, 719], [727, 733, 739]
        )
    ]
    krc = canonical(
        {
            "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
            "coverage_manifest_sha256": "c" * 64,
            "comparative_protocol_manifest_sha256": "p" * 64,
            "confirmation": {
                "conditions": [
                    "clean",
                    "modality_missing",
                    "field_missing",
                    "row_missing",
                    "feature_shuffle",
                    "gaussian_drift",
                ],
                "fixed_severity": {
                    "modality_missing": 1.0,
                    "field_missing": 0.3,
                    "row_missing": 0.3,
                    "feature_shuffle": 0.3,
                    "gaussian_drift": 0.5,
                },
                "fixed_augmentation_weight": 0.5,
                "training_sample_fraction": 0.25,
                "health_quantile": 0.99,
            },
        }
    )
    implementation = canonical(
        {
            "schema_version": (
                "strict_v4_rrc_csr_execution_implementation_protocol_v1"
            ),
            "execution_admitted": False,
            "design_manifest_sha256": design["manifest_sha256"],
            "state": (
                "full_execution_chain_implemented_waiting_terminal_krc_decision"
            ),
            "remaining_required_components": [],
        }
    )
    input_protocol = canonical(
        {
            "schema_version": (
                "strict_v4_rrc_csr_execution_input_protocol_v1"
            ),
            "activation_gate_satisfied": True,
            "execution_admitted": False,
            "rrc_design_manifest_sha256": design["manifest_sha256"],
            "krc_protocol_manifest_sha256": krc["manifest_sha256"],
            "downstream_decision_manifest_sha256": "d" * 64,
            "source_registry": source_registry,
            "tasks": tasks,
            "training_seeds": [701, 709, 719],
            "corruption_seeds": [727, 733, 739],
            "task_counts": {
                "scenarios": 83,
                "training_seeds": 3,
                "base_csr_captures": 249,
                "scenario_certificates": 83,
                "rrc_runtime_captures": 249,
                "conditions_per_runtime": 6,
                "evaluations": 1494,
            },
        }
    )
    implementations = {}
    for index, name in enumerate(creator.IMPLEMENTATION):
        path = tmp_path / f"implementation_{index}.py"
        path.write_text(f"# {name}\n", encoding="utf-8")
        implementations[name] = path.name
    return design, input_protocol, implementation, krc, implementations


def test_execution_protocol_binds_exact_task_universe(
    tmp_path: Path, monkeypatch
):
    design, input_protocol, implementation, krc, implementations = (
        fixtures(tmp_path)
    )
    monkeypatch.setattr(creator, "IMPLEMENTATION", implementations)
    protocol = creator.create(
        project_root=tmp_path,
        design=design,
        input_protocol=input_protocol,
        implementation_protocol=implementation,
        krc_protocol=krc,
        observed_counts={
            "base_csr_captures": 0,
            "scenario_certificates": 0,
            "rrc_runtime_captures": 0,
            "evaluations": 0,
            "capture_pipeline_inventory": 0,
            "summary": 0,
            "audit": 0,
        },
        input_file_sha256={"fixture": "f" * 64},
    )
    validate_protocol(protocol)
    groups = group_tasks(protocol["tasks"])
    assert len(groups) == 83
    assert all(len(group) == 3 for group in groups)
    assert protocol["execution_admitted"] is True
    assert protocol["task_counts"]["evaluations"] == 1494


def test_execution_protocol_rejects_preexisting_result(
    tmp_path: Path, monkeypatch
):
    design, input_protocol, implementation, krc, implementations = (
        fixtures(tmp_path)
    )
    monkeypatch.setattr(creator, "IMPLEMENTATION", implementations)
    with pytest.raises(ValueError, match="before every result"):
        creator.create(
            project_root=tmp_path,
            design=design,
            input_protocol=input_protocol,
            implementation_protocol=implementation,
            krc_protocol=krc,
            observed_counts={"evaluations": 1},
            input_file_sha256={"fixture": "f" * 64},
        )


def test_partial_directory_requires_quarantine(tmp_path: Path):
    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / "capture.log").write_text("partial", encoding="utf-8")
    with pytest.raises(ValueError, match="requires quarantine"):
        require_empty_or_absent(partial, "test output")

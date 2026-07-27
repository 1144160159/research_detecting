from pathlib import Path

import numpy as np
import pytest

from audit_strict_v4_mdr_evidence_reuse import evaluate_audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_evidence_reuse_protocol import create_protocol
from evaluate_mdr_evidence_reuse import (
    DISCRETE_KEYS,
    NUMERIC_KEYS,
    compare_outputs,
)
from run_strict_v4_mdr_evidence_reuse import validate_protocol
from summarize_strict_v4_mdr_evidence_reuse import aggregate_captures


REQUIRED = [
    "create_strict_v4_mdr_evidence_reuse_protocol.py",
    "evaluate_mdr_evidence_reuse.py",
    "run_strict_v4_mdr_evidence_reuse.py",
    "summarize_strict_v4_mdr_evidence_reuse.py",
    "audit_strict_v4_mdr_evidence_reuse.py",
    "scripts/wait_and_run_strict_v4_mdr_evidence_reuse.sh",
    "caeos/mdr_evidence_reuse_runtime.py",
    "caeos/mdr_runtime.py",
    "caeos/pairwise_runtime.py",
]
CONDITIONS = [
    "clean",
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
]


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def source_matrix():
    sources = []
    tasks = []
    for scenario_index in range(102):
        suite = f"suite{scenario_index // 17}"
        scenario = f"scenario{scenario_index}"
        for seed in (347, 349, 353):
            sources.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "corruption_seed": seed + scenario_index,
                    "capture_dir": f"/capture/{suite}/{scenario}/seed{seed}",
                    "capture_manifest_file_sha256": (
                        f"manifest-{scenario_index}-{seed}"
                    ),
                    "runtime_artifact_sha256": (
                        f"runtime-{scenario_index}-{seed}"
                    ),
                    "evaluation_inputs_sha256": (
                        f"inputs-{scenario_index}-{seed}"
                    ),
                }
            )
            tasks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "corruption_seed": seed + scenario_index,
                }
            )
    return sources, tasks


def make_protocol(tmp_path: Path, observed_outputs=0):
    sources, tasks = source_matrix()
    design = canonical(
        "strict_v4_mdr_evidence_reuse_design_v1",
        formal_equivalence={
            "conditions": CONDITIONS,
            "probability_risk_and_diagnostics_max_absolute_tolerance": 1e-12,
        },
        benchmark={
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "scenario_block_bootstrap_repetitions": 20,
            "bootstrap_seed": 7,
        },
        decision={"deployment_substitution_requires_equivalence": True},
        claim_boundary={"not_a_new_effectiveness_algorithm": True},
    )
    confirmation_protocol = canonical(
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        confirmation={
            "tasks": tasks,
            "fixed_severity": {
                condition: 0.0 if condition == "clean" else 0.5
                for condition in CONDITIONS
                if condition != "clean"
            },
        },
        coverage_manifest_sha256="coverage-hash",
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
    return create_protocol(
        project_root=tmp_path,
        run_root=tmp_path / "runs",
        design=design,
        selection=selection,
        confirmation_protocol=confirmation_protocol,
        confirmation_summary=confirmation_summary,
        confirmation_audit=confirmation_audit,
        sources=sources,
        implementation_sha256={name: f"hash-{name}" for name in REQUIRED},
        input_file_sha256={"design": "file-design"},
        observed_outputs=observed_outputs,
    )


def equivalence_result():
    return {
        "discrete_array_equal": {key: True for key in DISCRETE_KEYS},
        "numeric_max_absolute_difference": {
            key: 0.0 for key in NUMERIC_KEYS
        },
        "absolute_tolerance": 1e-12,
        "passes": True,
    }


def make_records(protocol):
    records = []
    for source in protocol["sources"]:
        benchmark = {}
        for batch in (1, 64, 512):
            benchmark[str(batch)] = {
                "original_mdr_caeos_v1": {
                    "latency_p50_ms": 2.0,
                    "latency_p95_ms": 2.0,
                    "latency_p99_ms": 2.0,
                    "samples_per_second": 100.0,
                    "raw_seconds": [0.02],
                },
                "mdr_evidence_reuse_v1": {
                    "latency_p50_ms": 1.0,
                    "latency_p95_ms": 1.0,
                    "latency_p99_ms": 1.0,
                    "samples_per_second": 200.0,
                    "raw_seconds": [0.01],
                },
                "embedded_caeos_pairwise": {
                    "latency_p50_ms": 1.5,
                    "latency_p95_ms": 1.5,
                    "latency_p99_ms": 1.5,
                    "samples_per_second": 150.0,
                    "raw_seconds": [0.015],
                },
            }
        conditions = [
            {
                "condition": condition,
                "modality": None if condition == "clean" else 0,
                "severity": 0.0 if condition == "clean" else 0.5,
                "corruption_seed": source["corruption_seed"],
                "direct_equivalence": equivalence_result(),
                "serialization_equivalence": equivalence_result(),
            }
            for condition in CONDITIONS
        ]
        value = {
            "schema_version": "strict_v4_mdr_evidence_reuse_capture_v1",
            "state": "complete",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "source": {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": source["training_seed"],
                "corruption_seed": source["corruption_seed"],
                "capture_manifest_file_sha256": source[
                    "capture_manifest_file_sha256"
                ],
                "runtime_artifact_sha256": source[
                    "runtime_artifact_sha256"
                ],
                "evaluation_inputs_sha256": source[
                    "evaluation_inputs_sha256"
                ],
            },
            "equivalence": {
                "condition_count": 6,
                "conditions": conditions,
                "all_direct_pass": True,
                "all_serialization_pass": True,
                "labels_loaded": False,
            },
            "benchmark": benchmark,
            "artifact": {
                "original_mdr_bytes": 200,
                "optimized_mdr_bytes": 210,
                "optimized_mdr_sha256": "optimized",
                "embedded_pairwise_bytes": 100,
                "embedded_pairwise_sha256": "pairwise",
            },
            "fit_cost": {
                "unchanged_by_inference_optimization": True,
                "clean_plus_robust_wall_seconds_lower_bound": 10.0,
            },
            "runtime_evidence": {
                "deployment_optimization": {
                    "schema_version": "mdr_evidence_reuse_v1",
                    "effect_semantics_changed": False,
                    "clean_model_evidence_passes_per_batch": 1,
                    "robust_model_evidence_passes_per_batch": 1,
                    "original_clean_model_evidence_passes_per_batch": 2,
                    "original_robust_model_evidence_passes_per_batch": 3,
                }
            },
            "execution_context": {"platform": "test", "gpu_used": False},
            "exclusive_machine_preflight_marker": "passed",
            "unknown_or_test_labels_used": False,
        }
        value["manifest_sha256"] = canonical_hash(value)
        records.append(value)
    return records


def test_protocol_freezes_full_three_seed_matrix(tmp_path):
    protocol = make_protocol(tmp_path)
    validate_protocol(protocol)
    assert protocol["source_count"] == 306
    assert protocol["scenario_block_count"] == 102
    assert protocol["training_seeds"] == [347, 349, 353]
    assert protocol["expected_condition_count"] == 1836


def test_protocol_rejects_existing_outputs(tmp_path):
    with pytest.raises(ValueError, match="before outputs"):
        make_protocol(tmp_path, observed_outputs=1)


def test_output_comparison_requires_exact_discrete_and_tight_numeric():
    reference = {
        **{key: np.array([1, 0]) for key in DISCRETE_KEYS},
        **{key: np.array([0.1, 0.2]) for key in NUMERIC_KEYS},
    }
    equivalent = {key: value.copy() for key, value in reference.items()}
    assert compare_outputs(
        reference, equivalent, tolerance=1e-12
    )["passes"]
    equivalent["risk"][0] += 1e-6
    assert not compare_outputs(
        reference, equivalent, tolerance=1e-12
    )["passes"]


def test_summary_and_independent_audit_keep_gates_separate(tmp_path):
    protocol = make_protocol(tmp_path)
    records = make_records(protocol)
    aggregate = aggregate_captures(records, protocol)
    assert aggregate["capture_count"] == 306
    assert aggregate["condition_count"] == 1836
    assert aggregate["deployment_substitution_decision"]["passes"] is True
    assert (
        aggregate["latency_improvement_over_original_decision"]["passes"]
        is True
    )
    summary = {
        "schema_version": "strict_v4_mdr_evidence_reuse_summary_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate,
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    recomputed = dict(aggregate)
    recomputed["_records"] = records
    audit = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        capture_hashes_match=True,
        artifact_hashes_match=True,
    )
    assert audit["passes"] is True
    assert audit["deployment_substitution_gate_passes"] is True
    assert audit["latency_improvement_over_original_gate_passes"] is True


def test_watcher_waits_for_idle_machine_and_preserves_claim_boundary():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "wait_and_run_strict_v4_mdr_evidence_reuse.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "five consecutive exclusive-machine samples passed" in text
    assert "MDR_EXCLUSIVE_MACHINE_GATE=passed" in text
    assert "deployment_substitution_gate_passes" in text
    assert "latency_improvement_over_original_gate_passes" in text


def test_runner_cannot_self_issue_exclusive_machine_marker():
    path = (
        Path(__file__).parents[1]
        / "run_strict_v4_mdr_evidence_reuse.py"
    )
    text = path.read_text(encoding="utf-8")
    assert (
        'os.environ.get("MDR_EXCLUSIVE_MACHINE_GATE") != "passed"'
        in text
    )
    assert 'environment["MDR_EXCLUSIVE_MACHINE_GATE"] = "passed"' not in text

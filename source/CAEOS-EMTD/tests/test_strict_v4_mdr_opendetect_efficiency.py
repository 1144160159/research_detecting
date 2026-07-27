import json
from pathlib import Path

import pytest

from audit_strict_v4_mdr_opendetect_efficiency import evaluate_audit
from benchmark_mdr_opendetect_runtime import exact_batch, timing_summary
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_opendetect_efficiency_protocol import (
    create_protocol,
)
from run_strict_v4_mdr_caeos_confirmation import (
    validate_capture_execution,
)
from run_strict_v4_mdr_opendetect_efficiency import validate_protocol
from summarize_strict_v4_mdr_opendetect_efficiency import (
    aggregate_benchmarks,
)


REQUIRED = [
    "create_strict_v4_mdr_opendetect_efficiency_protocol.py",
    "benchmark_mdr_opendetect_runtime.py",
    "run_strict_v4_mdr_opendetect_efficiency.py",
    "summarize_strict_v4_mdr_opendetect_efficiency.py",
    "audit_strict_v4_mdr_opendetect_efficiency.py",
    "scripts/wait_and_run_strict_v4_mdr_opendetect_efficiency.sh",
]


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def source_matrix():
    sources = []
    selected = []
    for scenario_index in range(102):
        suite = f"suite{scenario_index // 17}"
        scenario = f"scenario{scenario_index}"
        comparator = {
            "suite": suite,
            "scenario": scenario,
            "comparator_seed": 137,
            "capture_dir": f"/comparator/{suite}/{scenario}",
            "capture_manifest_file_sha256": f"ocm{scenario_index}",
            "runtime_artifact_sha256": f"ora{scenario_index}",
            "runtime_artifact_bytes": 200,
            "runtime_device": "cpu",
            "source_metrics_path": f"/metrics/{suite}/{scenario}.json",
            "source_metrics_file_sha256": f"om{scenario_index}",
            "source_training_seconds": 20.0,
            "source_training_seconds_field": "training_seconds",
            "split_fingerprint": f"split{scenario_index}",
        }
        for seed in (347, 349, 353):
            candidate = {
                "capture_dir": f"/candidate/{suite}/{scenario}/seed{seed}",
                "capture_manifest_file_sha256": (
                    f"cm{scenario_index}-{seed}"
                ),
                "capture_execution_file_sha256": (
                    f"ce{scenario_index}-{seed}"
                ),
                "total_capture_wall_seconds": 10.0,
                "runtime_artifact_sha256": f"ra{scenario_index}-{seed}",
                "runtime_artifact_bytes": 100,
                "evaluation_inputs_sha256": f"ei{scenario_index}-{seed}",
                "split_fingerprint": {"combined": f"mdr-{seed}"},
            }
            sources.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "candidate": candidate,
                    "comparator": dict(comparator),
                }
            )
            selected.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "capture_manifest_file_sha256": candidate[
                        "capture_manifest_file_sha256"
                    ],
                    "mdr_runtime_sha256": candidate[
                        "runtime_artifact_sha256"
                    ],
                    "evaluation_inputs_sha256": candidate[
                        "evaluation_inputs_sha256"
                    ],
                }
            )
    return sources, selected


def make_protocol(tmp_path: Path, observed=0):
    sources, selected_sources = source_matrix()
    design = canonical(
        "strict_v4_mdr_opendetect_efficiency_design_v1",
        required_implementation=REQUIRED,
        benchmark={
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": "alternate_by_timed_repetition",
        },
        aggregation={
            "bootstrap_repetitions": 100,
            "bootstrap_seed": 7,
        },
        strict_efficiency_superiority_gate={"required": True},
        cost={
            "mdr_fit_seconds_lower_bound": "clean_plus_robust",
            "opendetect_fit_seconds": "source",
        },
        claim_boundary={"efficiency_only": True},
    )
    selection = canonical(
        "strict_v4_final_self_algorithm_selection_v2",
        selected_algorithm="mdr_caeos_v1",
        mdr_confirmation_passes=True,
    )
    confirmation_protocol = canonical(
        "strict_v4_mdr_caeos_confirmation_protocol_v1"
    )
    confirmation_summary = canonical(
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        decision={"passes": True},
    )
    confirmation_audit = canonical(
        "strict_v4_mdr_caeos_confirmation_audit_v1", passes=True
    )
    selected_protocol = canonical(
        "strict_v4_mdr_selected_system_protocol_v1",
        sources=selected_sources,
    )
    selected_summary = canonical(
        "strict_v4_mdr_selected_system_summary_v1",
        protocol_manifest_sha256=selected_protocol["manifest_sha256"],
        deployability_decision={"passes": True},
    )
    selected_audit = canonical(
        "strict_v4_mdr_selected_system_audit_v1",
        protocol_manifest_sha256=selected_protocol["manifest_sha256"],
        summary_manifest_sha256=selected_summary["manifest_sha256"],
        passes=True,
        deployability_gate_passes=True,
    )
    comparative = canonical(
        "strict_v4_comparative_corruption_protocol_v2"
    )
    return create_protocol(
        project_root=tmp_path,
        run_root=tmp_path / "runs",
        design=design,
        selection=selection,
        confirmation_protocol=confirmation_protocol,
        confirmation_summary=confirmation_summary,
        confirmation_audit=confirmation_audit,
        selected_system_protocol=selected_protocol,
        selected_system_summary=selected_summary,
        selected_system_audit=selected_audit,
        comparative_protocol=comparative,
        sources=sources,
        implementation_sha256={name: f"hash-{name}" for name in REQUIRED},
        input_file_sha256={"design": "file-hash"},
        observed_benchmarks=observed,
    )


def make_records(protocol):
    records = []
    for source in protocol["sources"]:
        candidate = source["candidate"]
        comparator = source["comparator"]
        benchmark = {}
        for batch in (1, 64, 512):
            benchmark[str(batch)] = {
                "mdr_caeos_v1": {
                    "latency_p50_ms": 1.0,
                    "latency_p95_ms": 1.0,
                    "latency_p99_ms": 1.0,
                    "samples_per_second": 200.0,
                    "raw_seconds": [0.01],
                },
                "opendetect": {
                    "latency_p50_ms": 2.0,
                    "latency_p95_ms": 2.0,
                    "latency_p99_ms": 2.0,
                    "samples_per_second": 100.0,
                    "raw_seconds": [0.02],
                },
            }
        value = {
            "schema_version": (
                "strict_v4_mdr_opendetect_efficiency_benchmark_v1"
            ),
            "state": "complete",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "source": {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": source["training_seed"],
                "candidate_capture_manifest_file_sha256": candidate[
                    "capture_manifest_file_sha256"
                ],
                "candidate_capture_execution_file_sha256": candidate[
                    "capture_execution_file_sha256"
                ],
                "candidate_runtime_artifact_sha256": candidate[
                    "runtime_artifact_sha256"
                ],
                "evaluation_inputs_sha256": candidate[
                    "evaluation_inputs_sha256"
                ],
                "comparator_seed": 137,
                "comparator_capture_manifest_file_sha256": comparator[
                    "capture_manifest_file_sha256"
                ],
                "comparator_runtime_artifact_sha256": comparator[
                    "runtime_artifact_sha256"
                ],
                "comparator_source_metrics_file_sha256": comparator[
                    "source_metrics_file_sha256"
                ],
            },
            "same_input_evidence": {
                "candidate_and_comparator_received_same_arrays": True,
                "labels_loaded": False,
            },
            "benchmark": benchmark,
            "cost": {
                "mdr_artifact_bytes": 100,
                "opendetect_artifact_bytes": 200,
                "mdr_total_capture_wall_seconds": 10.0,
                "opendetect_training_seconds": 20.0,
                "mdr_fit_wall_seconds_lower_bound_diagnostic": 8.0,
            },
            "process_peak_rss": {"peak_host_rss_mb": 100.0},
            "peak_gpu_memory_mb": 0.0,
            "execution_context": {
                "platform": "test",
                "candidate_device": "cpu",
                "comparator_device": "cpu",
            },
            "exclusive_machine_preflight_marker": "passed",
            "unknown_or_test_labels_used_for_benchmark_selection": False,
            "comparator_seed_reuse_supports_effectiveness_claim": False,
        }
        value["manifest_sha256"] = canonical_hash(value)
        records.append(value)
    return records


def test_protocol_freezes_complete_matrix_before_outputs(tmp_path):
    protocol = make_protocol(tmp_path)
    validate_protocol(protocol)
    assert protocol["source_count"] == 306
    assert protocol["scenario_block_count"] == 102
    assert (
        protocol["cost_policy"]["strict_fit_gate_candidate_measure"]
        == "full_capture_subprocess_wall_seconds"
    )


def test_protocol_rejects_existing_outputs(tmp_path):
    with pytest.raises(ValueError, match="before outputs"):
        make_protocol(tmp_path, observed=1)


def test_benchmark_helpers_are_exact_and_finite():
    import numpy as np

    views = [np.arange(6).reshape(3, 2), np.arange(9).reshape(3, 3)]
    batch = exact_batch(views, 5)
    assert [item.shape for item in batch] == [(5, 2), (5, 3)]
    assert batch[0][:, 0].tolist() == [0, 2, 4, 0, 2]
    summary = timing_summary([0.01, 0.02, 0.03], 10)
    assert summary["latency_p50_ms"] == pytest.approx(20.0)
    assert summary["samples_per_second"] == pytest.approx(500.0)


def test_summary_and_independent_audit_pass_strict_fixture(tmp_path):
    protocol = make_protocol(tmp_path)
    records = make_records(protocol)
    aggregate = aggregate_benchmarks(records, protocol)
    assert aggregate["benchmark_count"] == 306
    assert aggregate["scenario_block_count"] == 102
    assert aggregate["strict_efficiency_decision"]["passes"] is True
    summary = {
        "schema_version": (
            "strict_v4_mdr_opendetect_efficiency_summary_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate,
        "claim_boundary": {
            "lower_bound_fit_ratio_is_diagnostic_only": True
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    recomputed = dict(aggregate)
    recomputed["_records"] = records
    audit = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        benchmark_hashes_match=True,
    )
    assert audit["passes"] is True
    assert audit["strict_efficiency_superiority_gate_passes"] is True


def test_capture_execution_evidence_binds_manifest(tmp_path):
    capture_manifest = tmp_path / "capture_manifest.json"
    capture_manifest.write_text('{"state":"complete"}\n', encoding="utf-8")
    from create_strict_v4_external_confirmation_protocol import file_hash

    value = {
        "schema_version": "strict_v4_mdr_caeos_capture_execution_v1",
        "state": "complete",
        "task": {"suite": "suite0", "scenario": "scenario0"},
        "training_seed": 347,
        "capture_manifest_file_sha256": file_hash(capture_manifest),
        "total_capture_wall_seconds": 12.5,
        "timer": "time.perf_counter",
        "scope": (
            "full_capture_subprocess_including_training_calibration_"
            "validation_profile_and_serialization"
        ),
        "unknown_or_test_labels_used_for_cost_selection": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    path = tmp_path / "capture_execution.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert validate_capture_execution(
        path,
        suite="suite0",
        scenario="scenario0",
        training_seed=347,
        capture_manifest=capture_manifest,
    )


def test_watcher_preserves_claim_boundary():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "wait_and_run_strict_v4_mdr_opendetect_efficiency.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "five consecutive exclusive-machine samples passed" in text
    assert "MDR_EXCLUSIVE_MACHINE_GATE=passed" in text
    assert "strict_efficiency_superiority_gate_passes" in text

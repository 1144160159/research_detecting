from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
import run_strict_v4_selected_system_efficiency as target
import run_strict_v4_selected_system_parrot_safety as shared


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sources() -> list[dict[str, Any]]:
    values = []
    seeds = (647, 653, 659)
    for scenario_index in range(102):
        suite = f"suite_{scenario_index % 7}"
        scenario = f"scenario_{scenario_index:03d}"
        for seed in seeds:
            values.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                    "source_split_fingerprint": (
                        f"{scenario_index:02x}{seed:04x}".ljust(64, "0")
                    ),
                    "csv": "/data/source.csv",
                    "config": "/data/config.json",
                    "unknown_classes": scenario,
                    "benign_class": "Benign",
                    "split_strategy": "fingerprint_grouped",
                    "max_per_class": 4000,
                    "clean_trainer_arguments": [],
                    "corruption_seed": seed + 10,
                    "augmentation_seed": seed,
                }
            )
    assert len(values) == 306
    return values


def protocol(
    source_values: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return canonical(
        {
            "schema_version": target.PROTOCOL_SCHEMA,
            "selected_algorithm": "caeos_pairwise",
            "sources": source_values or sources(),
            "training_seeds": [647, 653, 659],
            "benchmark": {
                "batch_sizes": [1, 64, 512],
                "warmup_repetitions": 5,
                "timed_repetitions": 30,
            },
            "aggregation": {
                "bootstrap_repetitions": 200,
                "bootstrap_seed": 20260727,
            },
            "claim_boundary": {
                "efficiency_failure_does_not_cancel_accuracy_result": True
            },
        }
    )


def benchmark_record(
    source: dict[str, Any],
    protocol_value: dict[str, Any],
    *,
    opendetect_throughput: float = 60.0,
) -> dict[str, Any]:
    blocks = {}
    for batch_size in (1, 64, 512):
        blocks[str(batch_size)] = {
            "selected_candidate": {
                "latency_p50_ms": 1.0,
                "latency_p95_ms": 1.1,
                "latency_p99_ms": 1.2,
                "samples_per_second": 120.0,
            },
            "caeos_pairwise": {
                "latency_p50_ms": 1.2,
                "latency_p95_ms": 1.3,
                "latency_p99_ms": 1.4,
                "samples_per_second": 100.0,
            },
            "opendetect": {
                "latency_p50_ms": 2.0,
                "latency_p95_ms": 2.1,
                "latency_p99_ms": 2.2,
                "samples_per_second": opendetect_throughput,
            },
        }
    value: dict[str, Any] = {
        "schema_version": target.BENCHMARK_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol_value["manifest_sha256"],
        "selected_algorithm": protocol_value["selected_algorithm"],
        "source": {
            "suite": source["suite"],
            "scenario": source["scenario"],
            "training_seed": source["training_seed"],
            "source_split_fingerprint": source[
                "source_split_fingerprint"
            ],
        },
        "same_input_evidence": {
            "candidate_pairwise_opendetect_received_same_arrays": True,
            "labels_loaded": False,
        },
        "serialization_roundtrip": {
            "selected_candidate": True,
            "caeos_pairwise": True,
            "opendetect": True,
        },
        "benchmark": blocks,
        "cost": {
            "selected_candidate_artifact_bytes": 100,
            "caeos_pairwise_artifact_bytes": 120,
            "opendetect_artifact_bytes": 200,
            "selected_candidate_fit_wall_seconds": 10.0,
            "caeos_pairwise_fit_wall_seconds": 12.0,
            "opendetect_fit_wall_seconds": 20.0,
        },
        "process_peak_rss": {"peak_host_rss_mb": 512.0},
        "peak_gpu_memory_mb": 256.0,
        "execution_context": {
            "host": "same",
            "cuda_device_name": "same",
        },
        "exclusive_machine_preflight_marker": "passed",
        "unknown_or_test_labels_used_for_benchmark_selection": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def adapter_design() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": (
                "strict_v4_selected_system_downstream_adapter_design_v1"
            ),
            "activation": {
                "allowed_selected_algorithms": list(target.ALGORITHMS)
            },
            "efficiency_branch": {
                "adapter_overhead_is_included": True,
                "batch_sizes": [1, 64, 512],
                "clean_process_training_runs_per_method": 3,
                "efficiency_failure_does_not_cancel_accuracy_result": True,
                "reports_latency_p50_p95_p99_throughput_memory_and_fit_time": (
                    True
                ),
                "same_gpu_host_and_software_environment": True,
                "warmup_and_measurement_schedule_must_match": True,
            },
        }
    )


def activation(
    selected: str, design: dict[str, Any]
) -> dict[str, Any]:
    snapshot = {"final": True, "selected_algorithm": selected}
    return canonical(
        {
            "schema_version": "strict_v4_selected_system_activation_v1",
            "execution_admitted": True,
            "selected_algorithm": selected,
            "selection_snapshot": snapshot,
            "selection_snapshot_sha256": canonical_hash(snapshot),
            "input_manifest_sha256": {
                "adapter_design": design["manifest_sha256"]
            },
        }
    )


def confirmation() -> dict[str, Any]:
    tasks = [
        {
            "suite": source["suite"],
            "scenario": source["scenario"],
            "training_seed": source["training_seed"],
            "corruption_seed": int(source["training_seed"]) + 10,
        }
        for source in sources()
    ]
    return canonical(
        {
            "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
            "confirmation": {"tasks": tasks},
        }
    )


def test_cross_suite_block_paths_do_not_collide(tmp_path: Path) -> None:
    first = {
        "suite": "suite_a",
        "scenario": "same scenario",
        "training_seed": 647,
    }
    second = {**first, "suite": "suite_b"}
    assert target.block_path(tmp_path, first) != target.block_path(
        tmp_path, second
    )


def test_opendetect_refit_uses_source_seed_and_split() -> None:
    source = sources()[0]
    value = protocol()
    value["opendetect_training"] = {
        "epochs": 100,
        "patience": 100,
        "hidden_dim": 128,
        "embedding_dim": 64,
        "known_acceptance": 0.95,
    }
    arguments = target.opendetect_arguments(
        source, value, Path("/tmp/output")
    )
    assert target.option(arguments, "--seed") == "647"
    assert (
        target.option(arguments, "--split-strategy")
        == "fingerprint_grouped"
    )
    assert target.option(arguments, "--unknown-classes") == "scenario_000"


def test_rrc_materializer_accepts_efficiency_sources_alias(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_values = [
        {
            "suite": "suite_a",
            "scenario": "scenario_a",
            "training_seed": seed,
            "corruption_seed": seed + 10,
        }
        for seed in (647, 653, 659)
    ]
    backend = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
        }
    )
    protocol_value = {
        "candidate_training": {"rrc_backend_protocol": backend},
        "sources": source_values,
    }
    materialized: list[int] = []
    monkeypatch.setattr(
        shared,
        "seed_record_from_capture",
        lambda path, **kwargs: kwargs,
    )
    monkeypatch.setattr(
        shared,
        "certify_seed_records",
        lambda records, **kwargs: {"manifest_sha256": "c" * 64},
    )

    def fake_materialize(
        backend_value: dict[str, Any],
        certificate: dict[str, Any],
        source_capture: Path,
        output: Path,
        **kwargs: Any,
    ) -> None:
        assert backend_value is backend
        assert certificate["manifest_sha256"] == "c" * 64
        materialized.append(int(kwargs["training_seed"]))

    monkeypatch.setattr(shared, "materialize", fake_materialize)
    target.materialize_rrc(protocol_value, tmp_path)
    assert materialized == [647, 653, 659]


def test_benchmark_rejects_missing_exclusive_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv(
        "SELECTED_SYSTEM_EXCLUSIVE_MACHINE_GATE", raising=False
    )
    value = protocol()
    with pytest.raises(ValueError, match="exclusive-machine"):
        target.benchmark_source(
            protocol=value,
            run_root=tmp_path,
            source=value["sources"][0],
            output=tmp_path / "benchmark.json",
        )


def test_aggregate_uses_102_three_seed_scenario_blocks() -> None:
    value = protocol()
    records = [
        benchmark_record(source, value) for source in value["sources"]
    ]
    result = target.aggregate_records(records, value)
    assert result["benchmark_count"] == 306
    assert result["scenario_block_count"] == 102
    assert result["deployability_decision"]["passes"] is True
    assert result["strict_efficiency_decision"]["passes"] is True
    assert set(result["strict_efficiency_decision"]["by_comparator"]) == {
        "caeos_pairwise",
        "opendetect",
    }


def test_efficiency_failure_does_not_cancel_effectiveness() -> None:
    value = protocol()
    records = [
        benchmark_record(
            source, value, opendetect_throughput=240.0
        )
        for source in value["sources"]
    ]
    summary = {
        "schema_version": target.SUMMARY_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": value["manifest_sha256"],
        **target.aggregate_records(records, value),
        "claim_boundary": value["claim_boundary"],
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    audit_value = target.audit(value, summary)
    assert (
        audit_value["strict_efficiency_by_comparator"]["opendetect"][
            "passes"
        ]
        is False
    )
    assert audit_value["strict_efficiency_sota_supported"] is False
    assert (
        audit_value["effectiveness_sota_supported_by_this_audit"] is False
    )
    assert audit_value["passed"] is True


def test_create_protocol_is_algorithm_neutral_and_binds_full_matrix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_root = Path(target.__file__).resolve().parent
    source_values = sources()
    monkeypatch.setattr(
        target, "build_sources", lambda confirmation, capture_root: source_values
    )
    monkeypatch.setattr(
        target,
        "IMPLEMENTATION_FILES",
        ("run_strict_v4_selected_system_efficiency.py",),
    )
    design = adapter_design()
    selected = "caeos_pug"
    paths = {
        "design": tmp_path / "design.json",
        "activation": tmp_path / "activation.json",
        "confirmation": tmp_path / "confirmation.json",
    }
    write(paths["design"], design)
    write(paths["activation"], activation(selected, design))
    write(paths["confirmation"], confirmation())
    value = target.create_protocol(
        project_root=project_root,
        run_root=tmp_path / "run",
        activation_path=paths["activation"],
        adapter_design_path=paths["design"],
        confirmation_protocol_path=paths["confirmation"],
        confirmation_capture_root=tmp_path / "captures",
    )
    assert value["selected_algorithm"] == selected
    assert value["source_count"] == 306
    assert value["scenario_block_count"] == 102
    assert value["benchmark"]["methods"] == [
        "selected_candidate",
        "caeos_pairwise",
        "opendetect",
    ]
    assert (
        value["opendetect_training"][
            "training_seed_equals_source_training_seed"
        ]
        is True
    )


def test_pending_state_reports_partial_source_matrix(
    tmp_path: Path,
) -> None:
    activation_path = tmp_path / "activation.json"
    confirmation_path = tmp_path / "confirmation.json"
    capture_root = tmp_path / "captures"
    write(activation_path, {"state": "present"})
    value = confirmation()
    write(confirmation_path, value)
    for task in value["confirmation"]["tasks"][:2]:
        path = (
            capture_root
            / task["suite"]
            / task["scenario"]
            / f"seed{task['training_seed']}"
            / "capture_manifest.json"
        )
        write(path, {"state": "present"})
    state = target.pending_state(
        activation_path, confirmation_path, capture_root
    )
    assert state == {
        "state": "pending_complete_306_source_capture_matrix",
        "protocol_written": False,
        "source_capture_count": 2,
        "expected_source_capture_count": 306,
    }

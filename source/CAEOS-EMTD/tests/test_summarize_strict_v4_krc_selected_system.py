from copy import deepcopy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_krc_selected_system import aggregate_benchmarks


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def protocol():
    sources = []
    for scenario in range(102):
        for seed in (647, 653, 659):
            sources.append(
                {
                    "suite": f"suite{scenario // 17}",
                    "scenario": f"scenario{scenario}",
                    "training_seed": seed,
                    "capture_manifest_file_sha256": f"m-{scenario}-{seed}",
                    "capture_execution_file_sha256": f"e-{scenario}-{seed}",
                    "krc_runtime_sha256": f"r-{scenario}-{seed}",
                    "evaluation_inputs_sha256": f"i-{scenario}-{seed}",
                    "total_capture_wall_seconds": 80.0,
                }
            )
    return canonical(
        {
            "schema_version": "strict_v4_krc_selected_system_protocol_v1",
            "sources": sources,
            "training_seeds": [647, 653, 659],
            "benchmark": {"batch_sizes": [1, 64, 512]},
            "aggregation": {
                "bootstrap_repetitions": 100,
                "bootstrap_seed": 20260726,
            },
        }
    )


def records(protocol_value, latency_factor=0.8):
    output = []
    for source in protocol_value["sources"]:
        batches = {}
        for batch in (1, 64, 512):
            batches[str(batch)] = {
                "krc_csr_caeos_v1": {
                    "latency_p50_ms": latency_factor,
                    "latency_p95_ms": latency_factor,
                    "latency_p99_ms": latency_factor,
                    "samples_per_second": 120.0,
                },
                "caeos_pairwise": {
                    "latency_p50_ms": 1.0,
                    "latency_p95_ms": 1.0,
                    "latency_p99_ms": 1.0,
                    "samples_per_second": 100.0,
                },
            }
        output.append(
            canonical(
                {
                    "schema_version": (
                        "strict_v4_krc_selected_system_benchmark_v1"
                    ),
                    "state": "complete",
                    "protocol_manifest_sha256": protocol_value[
                        "manifest_sha256"
                    ],
                    "source": {
                        key: source[key]
                        for key in (
                            "suite",
                            "scenario",
                            "training_seed",
                            "capture_manifest_file_sha256",
                            "capture_execution_file_sha256",
                            "krc_runtime_sha256",
                            "evaluation_inputs_sha256",
                            "total_capture_wall_seconds",
                        )
                    },
                    "roundtrip": {
                        "krc_capture": {"passes": True},
                        "embedded_pairwise": {"passes": True},
                    },
                    "benchmark": batches,
                    "cost": {
                        "krc_artifact_bytes": 80,
                        "pairwise_artifact_bytes": 100,
                        "krc_full_build_wall_seconds": 80.0,
                        "pairwise_fit_wall_seconds": 100.0,
                    },
                    "process_peak_rss": {"peak_host_rss_mb": 512.0},
                    "peak_gpu_memory_mb": 0.0,
                    "execution_context": {
                        "platform": "linux",
                        "gpu_used": False,
                    },
                    "exclusive_machine_preflight_marker": "passed",
                    "unknown_or_test_labels_used_for_benchmark_selection": (
                        False
                    ),
                }
            )
        )
    return output


def test_aggregate_reports_deployable_and_strictly_efficient():
    frozen = protocol()
    result = aggregate_benchmarks(records(frozen), frozen)
    assert result["benchmark_count"] == 306
    assert result["scenario_block_count"] == 102
    assert result["deployability_decision"]["passes"] is True
    assert result["strict_efficiency_decision"]["passes"] is True
    assert result["ratio_inference"]["artifact_ratio"]["mean"] == pytest.approx(
        0.8
    )


def test_aggregate_preserves_efficiency_failure():
    frozen = protocol()
    result = aggregate_benchmarks(
        records(frozen, latency_factor=1.2), frozen
    )
    assert result["deployability_decision"]["passes"] is True
    assert result["strict_efficiency_decision"]["passes"] is False


def test_aggregate_rejects_duplicate_identity():
    frozen = protocol()
    values = records(frozen)
    values[-1] = deepcopy(values[0])
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_benchmarks(values, frozen)

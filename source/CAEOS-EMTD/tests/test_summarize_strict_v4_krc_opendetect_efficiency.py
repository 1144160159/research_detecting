from copy import deepcopy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_krc_opendetect_efficiency import (
    aggregate_benchmarks,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def protocol():
    sources = []
    for scenario in range(102):
        for seed in (647, 653, 659):
            suffix = f"{scenario}-{seed}"
            sources.append(
                {
                    "suite": f"suite{scenario // 17}",
                    "scenario": f"scenario{scenario}",
                    "training_seed": seed,
                    "candidate": {
                        "capture_manifest_file_sha256": f"cm-{suffix}",
                        "capture_execution_file_sha256": f"ce-{suffix}",
                        "runtime_artifact_sha256": f"cr-{suffix}",
                        "evaluation_inputs_sha256": f"ci-{suffix}",
                    },
                    "comparator": {
                        "comparator_seed": 137,
                        "capture_manifest_file_sha256": f"om-{scenario}",
                        "runtime_artifact_sha256": f"or-{scenario}",
                        "source_metrics_file_sha256": f"ox-{scenario}",
                    },
                }
            )
    return canonical(
        {
            "schema_version": (
                "strict_v4_krc_opendetect_efficiency_protocol_v1"
            ),
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
                "opendetect": {
                    "latency_p50_ms": 1.0,
                    "latency_p95_ms": 1.0,
                    "latency_p99_ms": 1.0,
                    "samples_per_second": 100.0,
                },
            }
        candidate = source["candidate"]
        comparator = source["comparator"]
        output.append(
            canonical(
                {
                    "schema_version": (
                        "strict_v4_krc_opendetect_efficiency_benchmark_v1"
                    ),
                    "state": "complete",
                    "protocol_manifest_sha256": protocol_value[
                        "manifest_sha256"
                    ],
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
                    "benchmark": batches,
                    "cost": {
                        "krc_fit_wall_seconds_lower_bound_diagnostic": 70.0,
                        "krc_total_capture_wall_seconds": 80.0,
                        "opendetect_training_seconds": 100.0,
                        "opendetect_source_field": "training_seconds",
                        "krc_artifact_bytes": 80,
                        "opendetect_artifact_bytes": 100,
                    },
                    "process_peak_rss": {"peak_host_rss_mb": 512.0},
                    "peak_gpu_memory_mb": 128.0,
                    "execution_context": {
                        "platform": "linux",
                        "same_process": True,
                    },
                    "exclusive_machine_preflight_marker": "passed",
                    "unknown_or_test_labels_used_for_benchmark_selection": (
                        False
                    ),
                    "comparator_seed_reuse_supports_effectiveness_claim": (
                        False
                    ),
                }
            )
        )
    return output


def test_aggregate_reports_strict_efficiency():
    frozen = protocol()
    result = aggregate_benchmarks(records(frozen), frozen)
    assert result["integrity_decision"]["passes"] is True
    assert result["strict_efficiency_decision"]["passes"] is True
    assert result["ratio_inference"]["artifact_ratio"]["mean"] == pytest.approx(
        0.8
    )


def test_aggregate_preserves_efficiency_failure():
    frozen = protocol()
    result = aggregate_benchmarks(
        records(frozen, latency_factor=1.2), frozen
    )
    assert result["integrity_decision"]["passes"] is True
    assert result["strict_efficiency_decision"]["passes"] is False


def test_aggregate_rejects_duplicate_identity():
    frozen = protocol()
    values = records(frozen)
    values[-1] = deepcopy(values[0])
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_benchmarks(values, frozen)

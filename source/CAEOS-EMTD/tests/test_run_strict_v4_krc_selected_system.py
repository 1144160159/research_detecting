import json

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_krc_selected_system import (
    validate_benchmark,
    validate_completion,
    validate_protocol,
)
from capture_pairwise_runtime import file_hash


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
                }
            )
    return canonical(
        {
            "schema_version": "strict_v4_krc_selected_system_protocol_v1",
            "execution_admitted": True,
            "selected_algorithm": "krc_csr_caeos_v1",
            "source_count": 306,
            "sources": sources,
        }
    )


def test_validate_protocol_accepts_canonical_306_sources():
    validate_protocol(protocol())


def test_validate_protocol_rejects_duplicate_sources():
    value = protocol()
    value["sources"][-1] = dict(value["sources"][0])
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)


def test_validate_benchmark_returns_false_when_absent(tmp_path):
    source = {
        "suite": "s",
        "scenario": "x",
        "training_seed": 647,
        "capture_manifest_file_sha256": "m",
        "capture_execution_file_sha256": "e",
        "krc_runtime_sha256": "r",
        "evaluation_inputs_sha256": "i",
        "total_capture_wall_seconds": 1.0,
    }
    assert (
        validate_benchmark(
            tmp_path / "benchmark.json", protocol(), source
        )
        is False
    )


def test_validate_benchmark_rejects_noncanonical_existing_file(tmp_path):
    path = tmp_path / "benchmark.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    source = {
        "suite": "s",
        "scenario": "x",
        "training_seed": 647,
        "capture_manifest_file_sha256": "m",
        "capture_execution_file_sha256": "e",
        "krc_runtime_sha256": "r",
        "evaluation_inputs_sha256": "i",
        "total_capture_wall_seconds": 1.0,
    }
    with pytest.raises(ValueError, match="invalid existing"):
        validate_benchmark(path, protocol(), source)


def test_validate_completion_accepts_bound_complete_result(tmp_path):
    frozen = protocol()
    summary = tmp_path / "summary.json"
    audit = tmp_path / "audit.json"
    completion = tmp_path / "execution_complete"
    summary.write_text("{}", encoding="utf-8")
    audit_value = canonical(
        {
            "schema_version": "strict_v4_krc_selected_system_audit_v1",
            "passes": True,
        }
    )
    audit.write_text(
        json.dumps(audit_value, sort_keys=True), encoding="utf-8"
    )
    completion.write_text(
        json.dumps(
            {
                "protocol_manifest_sha256": frozen["manifest_sha256"],
                "summary_file_sha256": file_hash(summary),
                "audit_file_sha256": file_hash(audit),
            }
        ),
        encoding="utf-8",
    )
    assert (
        validate_completion(frozen, summary, audit, completion) is True
    )

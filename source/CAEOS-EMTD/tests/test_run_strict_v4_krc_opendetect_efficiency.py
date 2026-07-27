import json

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_krc_opendetect_efficiency import (
    validate_benchmark,
    validate_protocol,
)


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
                    "candidate": {
                        "capture_manifest_file_sha256": "cm",
                        "capture_execution_file_sha256": "ce",
                        "runtime_artifact_sha256": "cr",
                        "evaluation_inputs_sha256": "ci",
                    },
                    "comparator": {
                        "comparator_seed": 137,
                        "capture_manifest_file_sha256": "om",
                        "runtime_artifact_sha256": "or",
                        "source_metrics_file_sha256": "ox",
                    },
                }
            )
    return canonical(
        {
            "schema_version": (
                "strict_v4_krc_opendetect_efficiency_protocol_v1"
            ),
            "execution_admitted": True,
            "selected_algorithm": "krc_csr_caeos_v1",
            "sources": sources,
        }
    )


def test_validate_protocol_accepts_complete_matrix():
    validate_protocol(protocol())


def test_validate_protocol_rejects_duplicate_identity():
    value = protocol()
    value["sources"][-1] = dict(value["sources"][0])
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)


def test_validate_benchmark_returns_false_when_absent(tmp_path):
    assert (
        validate_benchmark(
            tmp_path / "benchmark.json",
            protocol(),
            protocol()["sources"][0],
        )
        is False
    )


def test_validate_benchmark_rejects_noncanonical_existing_file(tmp_path):
    path = tmp_path / "benchmark.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid existing"):
        validate_benchmark(path, protocol(), protocol()["sources"][0])

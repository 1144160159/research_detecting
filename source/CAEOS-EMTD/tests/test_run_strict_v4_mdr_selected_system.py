import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_mdr_selected_system import (
    validate_benchmark,
    validate_protocol,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def protocol():
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
    return canonical(
        {
            "schema_version": "strict_v4_mdr_selected_system_protocol_v1",
            "selected_algorithm": "mdr_caeos_v1",
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
        "training_seed": 347,
        "capture_manifest_file_sha256": "m",
        "mdr_runtime_sha256": "r",
        "evaluation_inputs_sha256": "i",
    }
    assert (
        validate_benchmark(
            tmp_path / "benchmark.json", protocol(), source
        )
        is False
    )


def test_validate_benchmark_rejects_noncanonical_existing_file(tmp_path):
    path = tmp_path / "benchmark.json"
    path.write_text("{}", encoding="utf-8")
    source = {
        "suite": "s",
        "scenario": "x",
        "training_seed": 347,
        "capture_manifest_file_sha256": "m",
        "mdr_runtime_sha256": "r",
        "evaluation_inputs_sha256": "i",
    }
    with pytest.raises(ValueError, match="invalid existing"):
        validate_benchmark(path, protocol(), source)

import json

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_selected_system_protocol import (
    build_sources,
    zero_output_counts,
)
from capture_pairwise_runtime import file_hash


def write_canonical(path, value):
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def create_capture(root, suite, scenario, seed):
    capture = root / suite / scenario / f"seed{seed}"
    capture.mkdir(parents=True)
    artifact = capture / "krc.joblib"
    inputs = capture / "inputs.npz"
    artifact.write_bytes(f"runtime-{scenario}-{seed}".encode())
    inputs.write_bytes(f"inputs-{scenario}-{seed}".encode())
    manifest_path = capture / "capture_manifest.json"
    write_canonical(
        manifest_path,
        {
            "schema_version": "strict_v4_krc_csr_runtime_capture_v1",
            "state": "complete",
            "algorithm": "krc_csr_caeos_v1",
            "task": {"suite": suite, "scenario": scenario},
            "training_seed": seed,
            "runtime_artifact": artifact.name,
            "runtime_artifact_sha256": file_hash(artifact),
            "evaluation_inputs": inputs.name,
            "evaluation_inputs_sha256": file_hash(inputs),
            "roundtrip": {"passes": True},
        },
    )
    write_canonical(
        capture / "capture_execution.json",
        {
            "schema_version": "strict_v4_krc_csr_capture_execution_v1",
            "state": "complete",
            "task": {"suite": suite, "scenario": scenario},
            "training_seed": seed,
            "capture_manifest_file_sha256": file_hash(manifest_path),
            "total_capture_wall_seconds": 10.0,
            "unknown_or_test_labels_used_for_cost_selection": False,
        },
    )


def protocol_and_captures(tmp_path):
    tasks = []
    capture_root = tmp_path / "captures"
    for scenario_index in range(102):
        suite = f"suite{scenario_index // 17}"
        scenario = f"scenario{scenario_index}"
        for seed in (647, 653, 659):
            tasks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "training_seed": seed,
                }
            )
            create_capture(
                capture_root, suite, scenario, seed
            )
    return {"confirmation": {"tasks": tasks}}, capture_root


def test_build_sources_accepts_complete_306_capture_matrix(tmp_path):
    protocol, capture_root = protocol_and_captures(tmp_path)
    sources = build_sources(protocol, capture_root)
    assert len(sources) == 306
    assert {source["training_seed"] for source in sources} == {
        647,
        653,
        659,
    }


def test_build_sources_rejects_noncanonical_capture(tmp_path):
    protocol, capture_root = protocol_and_captures(tmp_path)
    path = (
        capture_root
        / "suite0"
        / "scenario0"
        / "seed647"
        / "capture_manifest.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["algorithm"] = "mutated"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid KRC"):
        build_sources(protocol, capture_root)


def test_zero_output_counts_rejects_existing_result(tmp_path):
    assert zero_output_counts(tmp_path) == {
        "benchmarks": 0,
        "summary": 0,
        "audit": 0,
        "completion": 0,
    }
    (tmp_path / "summary.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="zero-result"):
        zero_output_counts(tmp_path)

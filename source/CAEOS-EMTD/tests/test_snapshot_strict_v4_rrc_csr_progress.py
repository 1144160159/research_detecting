from __future__ import annotations

import json
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from snapshot_strict_v4_rrc_csr_progress import build_snapshot, file_hash


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")


def protocol(path: Path) -> None:
    value = {
        "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
        "task_counts": {
            "base_csr_captures": 2,
            "rrc_runtime_captures": 2,
            "scenario_certificates": 1,
            "evaluations": 6,
        },
    }
    write(path, value)


def write_base(path: Path, seed: int) -> None:
    manifest = {
        "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "task": {"suite": "suite", "scenario": "scenario"},
        "training_seed": seed,
        "test_effect_metrics_computed": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    write(
        path.parent / "capture_execution.json",
        {
            "schema_version": "strict_v4_rrc_csr_base_capture_execution_v1",
            "state": "complete",
            "task": manifest["task"],
            "training_seed": seed,
            "capture_manifest_file_sha256": file_hash(path),
            "total_capture_wall_seconds": 1.0,
        },
    )


def test_snapshot_reports_valid_partial_progress_without_effect(
    tmp_path: Path,
) -> None:
    protocol_path = tmp_path / "protocol.json"
    run_root = tmp_path / "run"
    protocol(protocol_path)
    write_base(
        run_root / "base_csr_captures/a/seed1/capture_manifest.json",
        1,
    )

    value = build_snapshot(protocol_path, run_root)

    assert value["state"] == "valid_partial_progress"
    assert value["inventory"]["base_csr_captures"]["present_count"] == 1
    assert value["invalid_artifact_count"] == 0
    assert value["effect_aggregation_performed"] is False
    assert value["manifest_sha256"] == canonical_hash(value)


def test_snapshot_requires_every_canonical_artifact_for_completion(
    tmp_path: Path,
) -> None:
    protocol_path = tmp_path / "protocol.json"
    run_root = tmp_path / "run"
    protocol(protocol_path)
    base_paths = [
        ("base_csr_captures/a/seed1/capture_manifest.json", 1),
        ("base_csr_captures/a/seed2/capture_manifest.json", 2),
    ]
    for path, seed in base_paths:
        write_base(run_root / path, seed)
    paths = [
        "rrc_runtime_captures/a/seed1/capture_manifest.json",
        "rrc_runtime_captures/a/seed2/capture_manifest.json",
        "scenario_certificates/a/certificate.json",
        *[
            f"evaluations/a/seed1/condition{index}/evaluation.json"
            for index in range(6)
        ],
    ]
    for path in paths:
        write(run_root / path, {"schema_version": "artifact"})

    value = build_snapshot(protocol_path, run_root)

    assert value["state"] == "complete_filesystem_inventory"
    assert value["all_expected_artifacts_complete"] is True

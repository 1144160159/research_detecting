from __future__ import annotations

import json
from pathlib import Path

from audit_mdr_caeos_capture_integrity import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def write(path: Path, value: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    return file_hash(path)


def fixture(tmp_path: Path):
    implementation = tmp_path / "runner.py"
    implementation_sha = write(implementation, b"runner\n")
    design = {
        "schema_version": "strict_v4_mdr_caeos_design_v2",
        "mechanism": {
            "training_augmentation_weight_grid": [0.125, 0.25]
        },
        "pilot": {"scenarios": {"suite": ["scenario"]}},
    }
    design["manifest_sha256"] = canonical_hash(design)
    protocol = {
        "schema_version": (
            "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        ),
        "design_manifest_sha256": design["manifest_sha256"],
        "implementation": {"runner": "runner.py"},
        "implementation_sha256": {"runner": implementation_sha},
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    auditor_path = tmp_path / "auditor.py"
    write(auditor_path, b"auditor\n")
    return protocol, design, auditor_path


def capture(
    root: Path,
    *,
    weight: float,
    corrupt_artifact: bool = False,
) -> Path:
    directory = root / f"weight_{weight:.3f}".replace(".", "p")
    artifact_sha = write(directory / "runtime.joblib", b"runtime\n")
    inputs_sha = write(directory / "inputs.npz", b"inputs\n")
    value = {
        "schema_version": "strict_v4_mdr_caeos_runtime_capture_v1",
        "state": "complete",
        "task": {"suite": "suite", "scenario": "scenario"},
        "weight": weight,
        "runtime_artifact": "runtime.joblib",
        "runtime_artifact_sha256": artifact_sha,
        "evaluation_inputs": "inputs.npz",
        "evaluation_inputs_sha256": inputs_sha,
        "roundtrip": {"passes": True},
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
        "known_validation_profile": {
            "schema_version": (
                "strict_v4_mdr_known_validation_profile_v1"
            ),
            "record_count": 15,
            "known_validation_labels_used": True,
            "unknown_or_test_labels_used": False,
        },
    }
    manifest = directory / "capture_manifest.json"
    manifest.write_text(json.dumps(value), encoding="utf-8")
    if corrupt_artifact:
        (directory / "runtime.joblib").write_bytes(b"changed\n")
    return manifest


def test_partial_snapshot_separates_integrity_from_completeness(
    tmp_path: Path,
) -> None:
    protocol, design, auditor_path = fixture(tmp_path)
    path = capture(tmp_path / "captures", weight=0.125)
    value = audit(
        protocol, design, [path], tmp_path, auditor_path
    )
    assert value["state"] == "partial_capture_snapshot"
    assert value["observed_capture_count"] == 1
    assert value["missing_capture_count"] == 1
    assert value["observed_integrity_passes"] is True
    assert value["passes"] is False
    assert value["checks"]["effect_metrics_read"] is False


def test_complete_matrix_requires_every_artifact_hash(
    tmp_path: Path,
) -> None:
    protocol, design, auditor_path = fixture(tmp_path)
    first = capture(tmp_path / "captures", weight=0.125)
    second = capture(
        tmp_path / "captures", weight=0.25, corrupt_artifact=True
    )
    failed = audit(
        protocol, design, [first, second], tmp_path, auditor_path
    )
    assert failed["checks"]["complete_capture_matrix"] is True
    assert failed["invalid_record_count"] == 1
    assert failed["passes"] is False

    write(second.parent / "runtime.joblib", b"runtime\n")
    passed = audit(
        protocol, design, [first, second], tmp_path, auditor_path
    )
    assert passed["observed_capture_count"] == 2
    assert passed["invalid_record_count"] == 0
    assert passed["passes"] is True

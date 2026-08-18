from __future__ import annotations

import json
from pathlib import Path

from audit_caeos_paper_readiness import build_report


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def contract() -> dict:
    return {
        "schema_version": "test_contract",
        "datasets": [
            {
                "id": "development",
                "role": "main_development",
                "required_for_development": True,
            },
            {
                "id": "external",
                "role": "external_confirmation",
                "required_for_development": False,
            },
        ],
        "gates": {
            "D0": {
                "required_presence_artifacts": ["_control/source.json"],
                "required_gate_artifacts": ["_control/data_card.json"],
                "required_dataset_manifest_fields": [
                    "complete",
                    "dataset_id",
                    "row_count",
                    "class_csvs",
                    "manifest_sha256",
                ],
            },
            "P0": {"required_gate_artifacts": ["_control/preprocess.json"]},
        },
    }


def manifest(dataset_id: str, csv_path: Path) -> dict:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_bytes(b"row\n")
    return {
        "complete": True,
        "dataset_id": dataset_id,
        "row_count": 1,
        "manifest_sha256": "a" * 64,
        "class_csvs": [
            {
                "attack_category": "Benign",
                "path": str(csv_path),
                "rows": 1,
                "sha256": "b" * 64,
                "size_bytes": 4,
                "verification": {
                    "full_row_validation": True,
                    "label_status_counts": {"aligned_unique_flow": 1},
                },
            }
        ],
    }


def test_readiness_fails_closed_until_all_manifests_and_artifacts_exist(
    tmp_path: Path,
) -> None:
    write_json(
        tmp_path / "development" / "dataset.manifest.json",
        manifest("development", tmp_path / "development" / "Benign.csv"),
    )
    report = build_report(contract(), tmp_path, check_files=True)
    assert report["summary"]["development_manifest_ready"] is True
    assert report["summary"]["paper_inventory_manifest_ready"] is False
    assert report["summary"]["D0_pass"] is False
    assert report["summary"]["F0_authorized"] is False


def test_readiness_authorizes_f0_only_after_d0_and_p0(tmp_path: Path) -> None:
    for dataset_id in ("development", "external"):
        write_json(
            tmp_path / dataset_id / "dataset.manifest.json",
            manifest(dataset_id, tmp_path / dataset_id / "Benign.csv"),
        )
    write_json(tmp_path / "_control" / "source.json", {"ready": True})
    write_json(tmp_path / "_control" / "data_card.json", {"gate_pass": True})
    write_json(tmp_path / "_control" / "preprocess.json", {"gate_pass": True})
    report = build_report(contract(), tmp_path, check_files=True)
    assert report["summary"]["paper_inventory_manifest_ready"] is True
    assert report["summary"]["D0_pass"] is True
    assert report["summary"]["P0_pass"] is True
    assert report["summary"]["F0_authorized"] is True


def test_existing_gate_artifact_without_explicit_pass_fails_closed(
    tmp_path: Path,
) -> None:
    for dataset_id in ("development", "external"):
        write_json(
            tmp_path / dataset_id / "dataset.manifest.json",
            manifest(dataset_id, tmp_path / dataset_id / "Benign.csv"),
        )
    write_json(tmp_path / "_control" / "source.json", {"ready": True})
    write_json(tmp_path / "_control" / "data_card.json", {"complete": True})
    write_json(tmp_path / "_control" / "preprocess.json", {"complete": True})
    report = build_report(contract(), tmp_path, check_files=True)
    assert report["summary"]["D0_artifacts_ready"] is False
    assert report["summary"]["P0_artifacts_ready"] is False
    assert report["summary"]["F0_authorized"] is False


def test_non_admitted_label_status_fails_manifest_gate(tmp_path: Path) -> None:
    value = manifest("development", tmp_path / "development" / "Benign.csv")
    value["class_csvs"][0]["verification"]["label_status_counts"] = {
        "unmatched_flow": 1
    }
    write_json(tmp_path / "development" / "dataset.manifest.json", value)
    report = build_report(contract(), tmp_path, check_files=True)
    assert report["datasets"][0]["passes_manifest_gate"] is False

from __future__ import annotations

import json
from pathlib import Path

from prepare_caeos_splitpcap_class_csv_legacy_cicddos import (
    archive_capture_for_label_boundary_repair,
    capture_processing_policy,
    load_label_boundary_repairs,
)


def repair_entry() -> dict[str, object]:
    return {
        "dataset_id": "cicddos2019",
        "capture_id": "a" * 64,
        "source_path": "/captures/source.zip",
        "source_member": "capture.pcap",
        "original_marker_sha256": "marker-before",
        "boundary_tolerance_ns": 2000,
        "maximum_official_gap_ns": 1952,
        "official_record_ids": ["record-2", "record-1"],
        "evidence_sha256": "e" * 64,
        "repair_rule": "test rule",
    }


def test_capture_policy_scopes_boundary_tolerance_to_repaired_capture() -> None:
    base = {"label_alignment": {"tolerance_ns": 0}, "other": "unchanged"}
    effective = capture_processing_policy(base, None, repair_entry())
    assert base["label_alignment"]["tolerance_ns"] == 0
    assert effective["label_alignment"]["tolerance_ns"] == 2000
    assert effective["capture_specific_label_boundary_repair"] == {
        "schema_version": "caeos_capture_label_boundary_repair_v1",
        "capture_id": "a" * 64,
        "source_path": "/captures/source.zip",
        "source_member": "capture.pcap",
        "boundary_tolerance_ns": 2000,
        "maximum_official_gap_ns": 1952,
        "official_record_ids": ["record-1", "record-2"],
        "evidence_sha256": "e" * 64,
        "repair_rule": "test rule",
    }


def test_load_boundary_repair_manifest_rejects_uncovered_gap(tmp_path: Path) -> None:
    entry = repair_entry()
    entry["maximum_official_gap_ns"] = 2001
    path = tmp_path / "repairs.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "caeos_label_boundary_repair_manifest_v1",
                "repairs": [entry],
            }
        ),
        encoding="utf-8",
    )
    try:
        load_label_boundary_repairs(path)
    except ValueError as error:
        assert "does not cover evidence" in str(error)
    else:
        raise AssertionError("uncovered official gap must be rejected")


def test_archive_preserves_original_marker_and_part(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    capture_id = "a" * 64
    marker_path = output_root / "_captures" / "cicddos2019" / f"{capture_id}.json"
    part_root = output_root / "_parts" / "cicddos2019" / capture_id
    marker_path.parent.mkdir(parents=True)
    part_root.mkdir(parents=True)
    marker = {"marker_sha256": "marker-before", "complete": True}
    marker_path.write_text(json.dumps(marker), encoding="utf-8")
    (part_root / "piece.part").write_bytes(b"old-part")

    archive_capture_for_label_boundary_repair(
        marker_path,
        part_root,
        output_root,
        "cicddos2019",
        capture_id,
        marker,
        repair_entry(),
    )

    backup = (
        output_root
        / "_control"
        / "label_boundary_repair_backups"
        / "cicddos2019"
        / capture_id
    )
    assert not marker_path.exists()
    assert not part_root.exists()
    assert (backup / "capture.marker.before.json").is_file()
    assert (backup / "parts.before" / "piece.part").read_bytes() == b"old-part"
    assert (backup / "repair.evidence.json").is_file()

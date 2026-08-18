from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from caeos_unified_dataset import canonical_json_hash, sha256_file


DATASET_ID = "cicids2017"
FAULTY_PREFIX = "raw/PCAPs/"


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def copy_with_fsync(source: Path, destination: Path) -> None:
    destination.unlink(missing_ok=True)
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())


def expected_capture_members(source_manifest: dict[str, Any]) -> set[str]:
    dataset = next(
        item for item in source_manifest["datasets"] if item["id"] == DATASET_ID
    )
    source_root = Path(dataset["source_root"])
    members: set[str] = set()
    for source in dataset["source_files"]:
        capture_members = source.get("capture_members")
        if capture_members:
            members.update(item["name"] for item in capture_members)
        else:
            members.add(Path(source["path"]).relative_to(source_root).as_posix())
    return members


def assert_dataset_not_running() -> None:
    result = subprocess.run(
        ["ps", "-eo", "args="], check=True, capture_output=True, text=True
    )
    active = [
        line
        for line in result.stdout.splitlines()
        if "prepare_caeos_splitpcap_class_csv" in line
        and f"--dataset {DATASET_ID}" in line
    ]
    if active:
        raise RuntimeError(f"{DATASET_ID} is still running: {active}")


def repair_working_copy(
    source: Path, working: Path, expected_members: set[str]
) -> dict[str, Any]:
    copy_with_fsync(source, working)
    connection = sqlite3.connect(working)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        if metadata.get("dataset_id") != DATASET_ID:
            raise ValueError("label index dataset mismatch")
        before = dict(
            connection.execute(
                "SELECT source_member, COUNT(*) FROM labels "
                "GROUP BY source_member ORDER BY source_member"
            )
        )
        if not before or any(
            member is None or not member.startswith(FAULTY_PREFIX)
            for member in before
        ):
            raise ValueError(f"unexpected pre-repair capture scope: {sorted(before)}")
        record_count = int(connection.execute("SELECT COUNT(*) FROM labels").fetchone()[0])
        if sum(before.values()) != record_count:
            raise ValueError("pre-repair source-member counts do not cover all records")

        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.execute(
            "UPDATE labels SET source_member = substr(source_member, ?) "
            "WHERE source_member LIKE ?",
            (len(FAULTY_PREFIX) + 1, f"{FAULTY_PREFIX}%"),
        )
        if cursor.rowcount != record_count:
            raise ValueError(
                f"capture-scope rewrite coverage mismatch: {cursor.rowcount} != {record_count}"
            )
        connection.commit()
        connection.execute("ANALYZE")
        connection.commit()

        after = dict(
            connection.execute(
                "SELECT source_member, COUNT(*) FROM labels "
                "GROUP BY source_member ORDER BY source_member"
            )
        )
        if set(after) != expected_members:
            raise ValueError(
                f"repaired capture scope does not match source manifest: "
                f"{sorted(after)} != {sorted(expected_members)}"
            )
        expected_counts = {
            member[len(FAULTY_PREFIX) :]: count for member, count in before.items()
        }
        if after != expected_counts or sum(after.values()) != record_count:
            raise ValueError("capture-scope rewrite changed label row cardinality")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity check failed: {integrity}")
    finally:
        connection.close()
    with working.open("rb") as handle:
        os.fsync(handle.fileno())
    return {
        "record_count": record_count,
        "before_source_member_counts": before,
        "after_source_member_counts": after,
        "sqlite_integrity_check": integrity,
    }


def archive_invalid_zero_row_outputs(
    output_root: Path, incident_root: Path, old_index_sha256: str
) -> dict[str, Any]:
    marker_root = output_root / "_captures" / DATASET_ID
    archived_markers = incident_root / "markers"
    archived_parts = incident_root / "parts"
    archived_markers.mkdir(parents=True, exist_ok=True)
    archived_parts.mkdir(parents=True, exist_ok=True)
    marker_reports: list[dict[str, Any]] = []
    for marker_path in sorted(marker_root.glob("*.json")):
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if int(marker.get("rows", -1)) != 0:
            raise ValueError(f"refusing to archive nonzero marker: {marker_path}")
        parts = marker.get("parts") or []
        if not parts:
            raise ValueError(f"marker has no part evidence: {marker_path}")
        label_policy = (parts[0].get("processing_policy") or {}).get(
            "label_alignment", {}
        )
        if label_policy.get("sha256") != old_index_sha256:
            raise ValueError(f"marker label-index identity mismatch: {marker_path}")
        reasons = marker.get("label_exclusion_summary", {}).get("reason_counts", {})
        if not reasons.get("five_tuple_present_only_in_other_capture_scope"):
            raise ValueError(f"marker lacks capture-scope failure evidence: {marker_path}")
        capture_id = marker_path.stem
        part_root = output_root / "_parts" / DATASET_ID / capture_id
        marker_reports.append(
            {
                "capture_id": capture_id,
                "marker_sha256": sha256_file(marker_path),
                "excluded_flows": marker["label_exclusion_summary"]["excluded_flows"],
                "reason_counts": reasons,
                "part_root_present": part_root.exists(),
            }
        )
        os.replace(marker_path, archived_markers / marker_path.name)
        if part_root.exists():
            os.replace(part_root, archived_parts / capture_id)
    return {
        "archived_marker_count": len(marker_reports),
        "archived_markers": marker_reports,
        "incident_root": str(incident_root),
    }


def update_manifest(
    manifest_path: Path,
    audit_path: Path,
    audit_sha256: str,
    index_path: Path,
    index_sha256: str,
    record_count: int,
    expected_members: set[str],
    stamp: str,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    item = next(entry for entry in manifest["datasets"] if entry["id"] == DATASET_ID)
    previous_evidence = item.get("coverage_evidence", [])
    item.update(
        {
            "path": str(index_path),
            "sha256": index_sha256,
            "record_count": record_count,
            "status": "ready",
            "formal_gate_passed": False,
            "admission_gate_passed": False,
            "ready_for_feature_revalidation": True,
            "coverage_fraction": 0.0,
            "effective_coverage_fraction": 0.0,
            "coverage_evidence": [
                {
                    "gate_type": "capture_scope_index_repair_pending_full_feature_revalidation",
                    "formal_gate_passed": False,
                    "admission_gate_passed": False,
                    "path": str(audit_path),
                    "sha256": audit_sha256,
                }
            ],
            "superseded_coverage_evidence": previous_evidence,
            "index_audit_path": str(audit_path),
            "index_audit_sha256": audit_sha256,
            "capture_scope_repair": {
                "completed_at_utc": stamp,
                "rule": f"strip_exact_prefix:{FAULTY_PREFIX}",
                "expected_source_members": sorted(expected_members),
                "full_feature_revalidation_required": True,
            },
        }
    )
    item.pop("repair_incident", None)
    manifest["ready_dataset_count"] = sum(
        entry.get("status") == "ready" for entry in manifest["datasets"]
    )
    manifest.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = canonical_json_hash(manifest)
    atomic_json(manifest_path, manifest)
    return item


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--label-index-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--work-root", type=Path, default=Path("/tmp"))
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    assert_dataset_not_running()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    source_manifest = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    expected_members = expected_capture_members(source_manifest)
    old_index_sha256 = sha256_file(args.index)
    working = args.work_root / f"cicids2017.capture-scope-repair.{stamp}.sqlite"
    details = repair_working_copy(args.index, working, expected_members)
    repaired_sha256 = sha256_file(working)

    target_partial = args.index.with_name(args.index.name + ".scope-repaired.partial")
    copy_with_fsync(working, target_partial)
    if sha256_file(target_partial) != repaired_sha256:
        target_partial.unlink(missing_ok=True)
        raise RuntimeError("published repaired index failed target reread SHA-256")

    incident_root = (
        args.output_root
        / "_control"
        / "invalid_feature_evidence"
        / "cicids2017_capture_scope_mismatch"
        / stamp
    )
    incident_root.mkdir(parents=True, exist_ok=False)
    invalid_outputs = archive_invalid_zero_row_outputs(
        args.output_root, incident_root, old_index_sha256
    )
    superseded = args.index.with_name(args.index.name + f".superseded_scope_bug.{stamp}")
    os.replace(args.index, superseded)
    os.replace(target_partial, args.index)
    working.unlink(missing_ok=True)

    audit = {
        "schema_version": "caeos_cicids2017_capture_scope_repair_v1",
        "dataset_id": DATASET_ID,
        "completed_at_utc": stamp,
        "repair_rule": f"strip_exact_prefix:{FAULTY_PREFIX}",
        "old_index_path": str(superseded),
        "old_index_sha256": old_index_sha256,
        "repaired_index_path": str(args.index),
        "repaired_index_sha256": repaired_sha256,
        "repaired_index_size_bytes": args.index.stat().st_size,
        "expected_source_members": sorted(expected_members),
        "details": details,
        "invalid_feature_outputs": invalid_outputs,
        "official_flow_fields_changed": False,
        "changed_field": "source_member capture-scope locator only",
        "full_feature_revalidation_required": True,
    }
    audit_path = incident_root / "repair.audit.json"
    atomic_json(audit_path, audit)
    audit_sha256 = sha256_file(audit_path)
    manifest_item = update_manifest(
        args.label_index_manifest,
        audit_path,
        audit_sha256,
        args.index,
        repaired_sha256,
        details["record_count"],
        expected_members,
        stamp,
    )
    print(
        json.dumps(
            {
                "dataset_id": DATASET_ID,
                "status": manifest_item["status"],
                "record_count": details["record_count"],
                "old_index_sha256": old_index_sha256,
                "repaired_index_sha256": repaired_sha256,
                "archived_marker_count": invalid_outputs["archived_marker_count"],
                "audit_path": str(audit_path),
                "audit_sha256": audit_sha256,
                "full_feature_revalidation_required": True,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

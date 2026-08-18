from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from caeos_label_alignment import SCHEMA_VERSION
from caeos_unified_dataset import atomic_json, sha256_file


STRICT_FLOW_DATASETS = {
    "cic_bot_iot",
    "cic_ton_iot",
    "cicids2017",
    "cicddos2019",
    "cicids2018",
    "edge_iiotset",
    "unsw_nb15",
}
CAPTURE_MEMBER_DATASETS = {"5gad_2022", "ciciot2022", "ciciot2023"}
SOURCE_QUALITY_DATASETS = {"dohbrw2020"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--full-hash", action="store_true")
    parser.add_argument("--source-manifest", type=Path)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sqlite_metadata(path: Path) -> dict[str, str]:
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        if connection.execute("SELECT 1 FROM labels LIMIT 1").fetchone() is None:
            raise ValueError(f"label index is empty: {path}")
        return metadata
    finally:
        connection.close()


def validate(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load(args.manifest)
    if manifest.get("schema_version") != "caeos_label_index_manifest_v1":
        raise ValueError("unsupported label index manifest")
    by_id = {item["id"]: item for item in manifest["datasets"]}
    requested = list(dict.fromkeys(args.dataset))
    source_by_id: dict[str, dict[str, Any]] = {}
    if args.source_manifest is not None:
        source_by_id = {
            item["id"]: item for item in load(args.source_manifest)["datasets"]
        }
    results: list[dict[str, Any]] = []

    for dataset_id in requested:
        item = by_id.get(dataset_id)
        if item is None or item.get("status") != "ready":
            raise ValueError(f"dataset is not ready in label manifest: {dataset_id}")
        if not item.get("admission_gate_passed"):
            raise ValueError(f"dataset has no passing admission gate: {dataset_id}")
        if float(item.get("effective_coverage_fraction", 0.0)) < 1.0 - 1e-12:
            raise ValueError(f"dataset retained coverage is incomplete: {dataset_id}")

        gate_types = set(item.get("admission_gate_types", []))
        if dataset_id in STRICT_FLOW_DATASETS:
            expected_gate = "strict_flow_label"
            if not item.get("formal_gate_passed"):
                raise ValueError(f"strict flow gate is not passing: {dataset_id}")
        elif dataset_id in CAPTURE_MEMBER_DATASETS:
            expected_gate = "full_capture_member_inventory"
            if item.get("formal_gate_passed"):
                raise ValueError(f"capture-level dataset falsely claims a strict flow gate: {dataset_id}")
        elif dataset_id in SOURCE_QUALITY_DATASETS:
            expected_gate = "source_quality_adjusted_flow_label"
            evidence = item.get("coverage_evidence", [])
            if not all(entry.get("source_quality_policy_sha256") for entry in evidence):
                raise ValueError("source-quality admission is missing its immutable policy")
            if item.get("formal_gate_passed"):
                raise ValueError("source-quality admission falsely claims a strict flow gate")
        else:
            raise ValueError(f"dataset is outside the frozen malicious delivery set: {dataset_id}")
        if gate_types != {expected_gate}:
            raise ValueError(f"unexpected admission gate for {dataset_id}: {gate_types}")

        index_path = Path(item["path"])
        audit_path = Path(item["index_audit_path"])
        if not index_path.is_file() or not audit_path.is_file():
            raise FileNotFoundError(f"missing delivery artifact for {dataset_id}")
        if sha256_file(audit_path) != item["index_audit_sha256"]:
            raise ValueError(f"index audit SHA-256 mismatch: {dataset_id}")
        audit = load(audit_path)
        audited_index = audit["label_index"]
        for key in ("path", "sha256"):
            if str(audited_index[key]) != str(item[key]):
                raise ValueError(f"manifest/audit {key} mismatch: {dataset_id}")
        if int(audited_index["record_count"]) != int(item["record_count"]):
            raise ValueError(f"manifest/audit record count mismatch: {dataset_id}")
        publication_verified = audited_index.get(
            "publication_verified_by_target_reread",
            audit.get("publication_verified_by_target_reread", False),
        )
        if not bool(publication_verified):
            raise ValueError(f"index publication was not target-reread verified: {dataset_id}")

        metadata = sqlite_metadata(index_path)
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"SQLite schema mismatch: {dataset_id}")
        if metadata.get("dataset_id") != dataset_id:
            raise ValueError(f"SQLite dataset mismatch: {dataset_id}")
        if int(metadata.get("record_count", -1)) != int(item["record_count"]):
            raise ValueError(f"SQLite record count mismatch: {dataset_id}")
        actual_sha256 = sha256_file(index_path) if args.full_hash else None
        if actual_sha256 is not None and actual_sha256 != item["sha256"]:
            raise ValueError(f"live label index SHA-256 mismatch: {dataset_id}")
        result = {
                "dataset_id": dataset_id,
                "status": "validated",
                "gate_type": expected_gate,
                "record_count": int(item["record_count"]),
                "path": str(index_path),
                "sha256": item["sha256"],
                "full_hash_verified": bool(args.full_hash),
            }
        if dataset_id in CAPTURE_MEMBER_DATASETS:
            if dataset_id not in source_by_id:
                raise ValueError(
                    f"capture adaptation validation needs --source-manifest: {dataset_id}"
                )
            from caeos_label_alignment import LabelResolver
            from prepare_caeos_unified_multimodal_csv import path_label

            resolver = LabelResolver(index_path, dataset_id, item["sha256"])
            try:
                rows = resolver.connection.execute(
                    "SELECT source_member, fine_label, family_label, binary_label "
                    "FROM labels ORDER BY source_member"
                ).fetchall()
                for source_member, fine, family, binary in rows:
                    auxiliary = path_label(source_by_id[dataset_id], str(source_member))
                    if (
                        auxiliary.fine_label,
                        auxiliary.family_label,
                        auxiliary.binary_label,
                    ) != (str(fine), str(family), int(binary)):
                        raise ValueError(
                            f"capture path/index label conflict: {dataset_id}::{source_member}"
                        )
                sample = rows[0]
                resolved = resolver.resolve(
                    str(sample[0]),
                    b"\x01\x01\x01\x01",
                    1000,
                    b"\x02\x02\x02\x02",
                    2000,
                    6,
                    1,
                    2,
                )
                if resolved.status != "aligned_unique_capture":
                    raise ValueError(f"capture resolver adaptation failed: {dataset_id}")
                result["capture_path_crosscheck_count"] = len(rows)
                result["capture_resolver_sample_status"] = resolved.status
            finally:
                resolver.close()
        results.append(result)

    report = {
        "schema_version": "caeos_label_delivery_validation_v1",
        "status": "passed",
        "manifest_path": str(args.manifest),
        "manifest_sha256": sha256_file(args.manifest),
        "requested_dataset_count": len(requested),
        "validated_dataset_count": len(results),
        "full_hash_verified": bool(args.full_hash),
        "source_manifest_path": (
            str(args.source_manifest) if args.source_manifest is not None else None
        ),
        "source_manifest_sha256": (
            sha256_file(args.source_manifest) if args.source_manifest is not None else None
        ),
        "datasets": results,
    }
    atomic_json(args.output, report)
    return report


def main() -> None:
    print(json.dumps(validate(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

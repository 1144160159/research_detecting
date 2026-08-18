from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json, canonical_json_hash, load_catalog


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--addition", action="append", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    base = load(args.base)
    catalog = load_catalog(args.catalog)
    if not base.get("full_source_hashes_computed"):
        raise ValueError("base manifest does not contain full source hashes")
    records = {item["id"]: item for item in base["datasets"]}
    added_ids: list[str] = []
    for path in args.addition:
        addition = load(path)
        if not addition.get("full_source_hashes_computed"):
            raise ValueError(f"addition lacks full source hashes: {path}")
        for item in addition["datasets"]:
            dataset_id = item["id"]
            if dataset_id in records:
                raise ValueError(f"dataset already exists in base manifest: {dataset_id}")
            records[dataset_id] = item
            added_ids.append(dataset_id)
    catalog_order = [item["id"] for item in catalog["datasets"]]
    if set(records) != set(catalog_order):
        missing = sorted(set(catalog_order) - set(records))
        extra = sorted(set(records) - set(catalog_order))
        raise ValueError(f"manifest/catalog mismatch; missing={missing}, extra={extra}")
    ordered = [records[dataset_id] for dataset_id in catalog_order]
    merged: dict[str, Any] = {
        "schema_version": "caeos_unified_source_manifest_v2",
        "catalog_schema_version": catalog["schema_version"],
        "catalog_sha256": canonical_json_hash(catalog),
        "hash_algorithm": "sha256",
        "full_source_hashes_computed": True,
        "datasets": ordered,
        "dataset_count": len(ordered),
        "capture_count": sum(int(item["capture_count"]) for item in ordered),
        "source_size_bytes": sum(int(item["source_size_bytes"]) for item in ordered),
        "manifest_extension": {
            "base_manifest_sha256": base["manifest_sha256"],
            "added_dataset_ids": sorted(added_ids),
            "existing_full_hash_records_reused": True,
            "new_full_hash_records_computed": True,
        },
    }
    merged["manifest_sha256"] = canonical_json_hash(merged)
    atomic_json(args.output, merged)
    print(json.dumps(merged, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

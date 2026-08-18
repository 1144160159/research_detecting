from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caeos_unified_dataset import (
    atomic_json,
    canonical_json_hash,
    discover_files,
    inspect_source,
    load_catalog,
    selected_datasets,
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def upgrade_manifest(
    old: dict[str, Any], catalog: dict[str, Any], refresh_archive_members: set[str]
) -> dict[str, Any]:
    if not old.get("full_source_hashes_computed"):
        raise ValueError("old manifest does not contain full source hashes")
    previous_manifest_sha256 = old.get("manifest_sha256")
    if not previous_manifest_sha256:
        raise ValueError("old manifest identity is missing")
    old_by_id = {item["id"]: item for item in old["datasets"]}
    records: list[dict[str, Any]] = []
    for dataset in selected_datasets(catalog, None):
        dataset_id = dataset["id"]
        if dataset_id not in old_by_id:
            raise ValueError(f"dataset absent from old manifest: {dataset_id}")
        previous = old_by_id[dataset_id]
        expected_paths = {str(path.resolve()) for path in discover_files(dataset)}
        previous_paths = {str(Path(item["path"]).resolve()) for item in previous["source_files"]}
        if expected_paths != previous_paths:
            raise ValueError(f"source file set drifted for {dataset_id}")
        sources: list[dict[str, Any]] = []
        for old_source in previous["source_files"]:
            path = Path(old_source["path"])
            stat = path.stat()
            if (
                int(stat.st_size) != int(old_source["size_bytes"])
                or int(stat.st_mtime_ns) != int(old_source["mtime_ns"])
                or not old_source.get("sha256")
            ):
                raise ValueError(f"source identity drifted; full rehash required: {path}")
            if dataset_id in refresh_archive_members and old_source.get("kind") == "archive":
                refreshed = inspect_source(path, compute_hash=False)
                refreshed["sha256"] = old_source["sha256"]
                sources.append(refreshed)
            else:
                sources.append(dict(old_source))
        sources.sort(key=lambda item: item["path"])
        records.append(
            {
                "id": dataset_id,
                "priority": dataset["priority"],
                "role": dataset["role"],
                "source_root": str(Path(dataset["source_root"]).resolve()),
                "source_kind": dataset["source_kind"],
                "label_policy": dataset["label_policy"],
                "label_binding": dataset["label_binding"],
                "source_file_count": len(sources),
                "capture_count": sum(int(item["capture_member_count"]) for item in sources),
                "source_size_bytes": sum(int(item["size_bytes"]) for item in sources),
                "source_files": sources,
            }
        )
    upgraded: dict[str, Any] = {
        "schema_version": "caeos_unified_source_manifest_v2",
        "catalog_schema_version": catalog["schema_version"],
        "catalog_sha256": canonical_json_hash(catalog),
        "hash_algorithm": "sha256",
        "full_source_hashes_computed": True,
        "datasets": records,
        "dataset_count": len(records),
        "capture_count": sum(item["capture_count"] for item in records),
        "source_size_bytes": sum(item["source_size_bytes"] for item in records),
        "manifest_upgrade": {
            "previous_manifest_sha256": previous_manifest_sha256,
            "source_file_set_revalidated": True,
            "size_and_mtime_revalidated": True,
            "archive_member_refresh_dataset_ids": sorted(refresh_archive_members),
            "source_content_hashes_reused_only_when_identity_unchanged": True,
        },
    }
    upgraded["manifest_sha256"] = canonical_json_hash(upgraded)
    return upgraded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-manifest", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--refresh-archive-members", action="append", default=[])
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError(f"refusing to overwrite source manifest: {args.output}")
    upgraded = upgrade_manifest(
        load_json(args.old_manifest),
        load_catalog(args.catalog),
        set(args.refresh_archive_members),
    )
    atomic_json(args.output, upgraded)
    print(json.dumps(upgraded, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

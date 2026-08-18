from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caeos_unified_dataset import (
    archive_capture_members,
    atomic_json,
    is_archive_path,
    is_pcap_name,
    load_catalog,
    selected_datasets,
)


def audit_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    root = Path(dataset["source_root"])
    if not root.is_dir():
        return {
            "id": dataset["id"],
            "source_root": str(root),
            "status": "missing_source_root",
        }

    direct_pcaps = sorted(
        path for path in root.rglob("*") if path.is_file() and is_pcap_name(path.name)
    )
    archives = sorted(
        path for path in root.rglob("*") if path.is_file() and is_archive_path(path)
    )
    archive_records = []
    archive_capture_count = 0
    archive_capture_bytes = 0
    archive_errors = []
    for path in archives:
        try:
            members = archive_capture_members(path)
        except Exception as error:  # Recorded per archive; the audit continues.
            archive_errors.append({"path": str(path), "error": repr(error)})
            continue
        archive_capture_count += len(members)
        archive_capture_bytes += sum(int(item["size_bytes"]) for item in members)
        archive_records.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "pcap_member_count": len(members),
                "pcap_member_bytes": sum(int(item["size_bytes"]) for item in members),
                "extensionless_pcap_members": sum(
                    item.get("capture_detection") == "magic" for item in members
                ),
            }
        )

    direct_bytes = sum(path.stat().st_size for path in direct_pcaps)
    eligible_count = len(direct_pcaps) + archive_capture_count
    if direct_pcaps:
        discovery_route = "direct_pcap"
    elif archives and archive_capture_count:
        discovery_route = "archive_pcap"
    elif archives:
        discovery_route = "archive_without_detectable_pcap"
    else:
        discovery_route = "no_pcap_or_archive"
    status = "ready" if eligible_count and not archive_errors else "blocked"
    return {
        "id": dataset["id"],
        "source_root": str(root.resolve()),
        "status": status,
        "discovery_route": discovery_route,
        "direct_pcap_count": len(direct_pcaps),
        "direct_pcap_bytes": direct_bytes,
        "archive_count": len(archives),
        "archive_bytes": sum(path.stat().st_size for path in archives),
        "archive_pcap_member_count": archive_capture_count,
        "archive_pcap_member_bytes": archive_capture_bytes,
        "eligible_capture_count": eligible_count,
        "eligible_capture_bytes": direct_bytes + archive_capture_bytes,
        "archive_errors": archive_errors,
        "archives": archive_records,
    }


def audit_catalog(
    catalog: dict[str, Any], dataset_ids: list[str] | None = None
) -> dict[str, Any]:
    records = [audit_dataset(item) for item in selected_datasets(catalog, dataset_ids)]
    return {
        "schema_version": "caeos_capture_asset_audit_v1",
        "dataset_count": len(records),
        "ready_dataset_count": sum(item["status"] == "ready" for item in records),
        "eligible_capture_count": sum(
            int(item.get("eligible_capture_count", 0)) for item in records
        ),
        "eligible_capture_bytes": sum(
            int(item.get("eligible_capture_bytes", 0)) for item in records
        ),
        "datasets": records,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dataset", action="append", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    catalog = load_catalog(args.catalog)
    audit = audit_catalog(catalog, args.dataset)
    atomic_json(args.output, audit)
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    if audit["ready_dataset_count"] != audit["dataset_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

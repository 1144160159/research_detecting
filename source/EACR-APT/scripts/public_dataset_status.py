"""Summarize GPU-side public dataset collection manifests."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


def disk_bytes(path: Path) -> int:
    result = subprocess.run(
        ["du", "-B1", "-s", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(result.stdout.split()[0])


def file_entries(value: Any) -> list[dict[str, Any]]:
    """Normalize legacy mapping and current list-shaped file states."""
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def entry_status(item: dict[str, Any]) -> str:
    status = str(item.get("status", "")).lower()
    if status in {"verified", "complete", "completed", "downloaded"}:
        return "verified"
    if status:
        return status
    if item.get("complete") or item.get("verified"):
        return "verified"
    if item.get("sha256") and any(
        key in item
        for key in ("bytes", "size_actual", "actual_bytes", "size_expected", "expected_bytes")
    ):
        return "verified"
    return "pending"


def dataset_status(path: Path) -> dict[str, Any]:
    state_path = path / "manifests" / "collection_state.json"
    source_path = path / "manifests" / "source_files.tsv"
    result: dict[str, Any] = {
        "name": path.name,
        "path": str(path),
        "disk_bytes": disk_bytes(path),
        "has_collection_manifest": state_path.is_file(),
    }
    if not state_path.is_file():
        return result
    if source_path.is_file():
        with source_path.open(encoding="utf-8", newline="") as handle:
            source_rows = list(csv.DictReader(handle, delimiter="\t"))
        result["expected_file_count"] = len(source_rows)
        result["expected_size_bytes"] = sum(
            int(row.get("size_bytes", 0)) for row in source_rows
        )
    with state_path.open(encoding="utf-8") as handle:
        state = json.load(handle)
    files = file_entries(state.get("files", {}))
    counts = Counter(entry_status(item) for item in files)
    verified_bytes = sum(
        int(
            item.get(
                "size_actual",
                item.get(
                    "actual_bytes",
                    item.get(
                        "size_expected",
                        item.get("expected_bytes", item.get("bytes", 0)),
                    ),
                ),
            )
        )
        for item in files
        if entry_status(item) == "verified"
    )
    result.setdefault(
        "expected_file_count",
        state.get("expected_file_count", state.get("expected_files", len(files))),
    )
    result.setdefault(
        "expected_size_bytes",
        state.get("expected_bytes", state.get("selection_size_bytes")),
    )
    result.update(
        {
            "file_count": len(files),
            "status_counts": dict(sorted(counts.items())),
            "verified_bytes": verified_bytes,
            "complete": bool(state.get("complete", False)),
            "selection_size_bytes": state.get("selection_size_bytes"),
            "manifest": str(state_path),
        }
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public"),
    )
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [
        dataset_status(path)
        for path in sorted(args.root.iterdir())
        if path.is_dir()
    ]
    if args.compact:
        print(
            "dataset\texpected_files\tverified\tdownloading\tpending\tfailed"
            "\tverified_bytes\tdisk_bytes\tcomplete"
        )
        for row in rows:
            counts = row.get("status_counts", {})
            print(
                "\t".join(
                    str(value)
                    for value in (
                        row["name"],
                        row.get("expected_file_count", ""),
                        counts.get("verified", 0),
                        counts.get("downloading", 0),
                        counts.get("pending", 0),
                        counts.get("failed", 0) + counts.get("checksum_failed", 0),
                        row.get("verified_bytes", 0),
                        row["disk_bytes"],
                        row.get("complete", False),
                    )
                )
            )
    else:
        print(json.dumps({"root": str(args.root), "datasets": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

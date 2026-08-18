#!/usr/bin/env python3
"""Freeze the complete CICIoT2023 PCAP inventory from its capture label index."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(dataset_root: Path, label_index_path: Path) -> dict:
    index = json.loads(label_index_path.read_text())
    if index.get("schema") != "caeos.ciciot2023.capture_label_index.v1":
        raise ValueError("unexpected CICIoT2023 label index schema")
    entries = []
    for capture in index["captures"]:
        source = dataset_root / capture["capture"]
        if not source.is_file() or source.stat().st_size != capture["pcap_bytes"]:
            raise ValueError(f"missing or size-changed PCAP: {capture['capture']}")
        entries.append(
            {
                "source_id": capture["capture"],
                "source_type": "file",
                "capture": capture["capture"],
                "pcap_bytes": capture["pcap_bytes"],
                "label": {
                    "is_malicious": capture["is_malicious"],
                    "attack_family": capture["attack_family"],
                    "attack_fine": capture["attack_fine"],
                },
            }
        )
    disk_set = {
        path.relative_to(dataset_root).as_posix()
        for path in (dataset_root / "PCAP").glob("*/*.pcap")
    }
    index_set = {entry["capture"] for entry in entries}
    if disk_set != index_set:
        raise ValueError(
            f"PCAP inventory/index mismatch: disk_only={sorted(disk_set-index_set)}, "
            f"index_only={sorted(index_set-disk_set)}"
        )
    return {
        "schema": "caeos.ciciot2023.all_pcap_inventory.v1",
        "dataset_id": "CICIoT2023",
        "authority_granularity": "capture_member_not_official_flow_label",
        "label_index_sha256": sha256_file(label_index_path),
        "entries": sorted(entries, key=lambda item: item["source_id"]),
        "summary": {
            "expected_source_count": len(entries),
            "expected_source_bytes": sum(item["pcap_bytes"] for item in entries),
            "filesystem_set_equals_label_index": True,
            "inventory_ready": bool(entries),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--label-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inventory = build_inventory(args.dataset_root, args.label_index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output), **inventory["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

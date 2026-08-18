#!/usr/bin/env python3
"""Expand every official CICIoT2022 experiment PCAP into a frozen inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath

from build_caeos_ciciot2022_capture_label_index import is_real_pcap_member


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def benign_archive_entries(dataset_root: Path, rule: dict) -> list[dict]:
    archive_path = dataset_root / rule["archive"]
    entries = []
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            if not is_real_pcap_member(member):
                continue
            entries.append(
                {
                    "source_id": f"{rule['archive']}::{member.name}",
                    "source_type": "archive_member",
                    "archive": rule["archive"],
                    "member": member.name,
                    "pcap_bytes": member.size,
                    "label": {
                        "is_malicious": False,
                        "attack_family": "Benign",
                        "attack_fine": "Benign",
                        "experiment": rule["experiment"],
                    },
                }
            )
    return entries


def build_inventory(dataset_root: Path, label_index_path: Path) -> dict:
    index = json.loads(label_index_path.read_text())
    if index.get("schema") != "caeos.ciciot2022.capture_label_index.v1":
        raise ValueError("unexpected CICIoT2022 label index schema")
    entries = []
    for item in index["active_captures"]:
        source = dataset_root / item["capture"]
        if not source.is_file() or source.stat().st_size != item["pcap_bytes"]:
            raise ValueError(f"missing or size-changed active PCAP: {item['capture']}")
        entries.append(
            {
                "source_id": item["capture"],
                "source_type": "file",
                "capture": item["capture"],
                "pcap_bytes": item["pcap_bytes"],
                "label": {
                    "is_malicious": False,
                    "attack_family": "Benign",
                    "attack_fine": "Benign",
                    "experiment": "Active",
                },
            }
        )
    for item in index["attack_members"]:
        entries.append(
            {
                "source_id": f"{item['archive']}::{item['member']}",
                "source_type": "archive_member",
                "archive": item["archive"],
                "member": item["member"],
                "pcap_bytes": item["pcap_bytes"],
                "label": {
                    "is_malicious": True,
                    "attack_family": item["attack_family"],
                    "attack_fine": item["attack_fine"],
                    "experiment": "Attacks",
                },
            }
        )
    benign_counts = {}
    for rule in index["benign_archive_rules"]:
        expanded = benign_archive_entries(dataset_root, rule)
        benign_counts[rule["archive"]] = len(expanded)
        entries.extend(expanded)
    source_ids = [item["source_id"] for item in entries]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("duplicate source_id in expanded CICIoT2022 inventory")
    attack_expected = {
        f"{item['archive']}::{item['member']}" for item in index["attack_members"]
    }
    attack_actual = {
        item["source_id"] for item in entries if item["label"]["experiment"] == "Attacks"
    }
    if attack_expected != attack_actual:
        raise ValueError("expanded attack inventory differs from official attack label index")
    return {
        "schema": "caeos.ciciot2022.all_pcap_inventory.v1",
        "dataset_id": "CICIoT2022",
        "authority_granularity": "capture_member_not_official_flow_label",
        "scope": "official six IP-network experiments described by Readme.txt",
        "out_of_scope_assets": ["Z-Wave expriments.tar.gz", "Zigbee expriments.tar.gz"],
        "label_index_sha256": sha256_file(label_index_path),
        "entries": sorted(entries, key=lambda item: item["source_id"]),
        "summary": {
            "expected_source_count": len(entries),
            "expected_source_bytes": sum(item["pcap_bytes"] for item in entries),
            "active_file_count": len(index["active_captures"]),
            "attack_member_count": len(index["attack_members"]),
            "benign_archive_member_count_by_archive": benign_counts,
            "all_four_benign_archives_expanded": len(benign_counts) == 4 and all(benign_counts.values()),
            "inventory_ready": bool(entries) and len(benign_counts) == 4 and all(benign_counts.values()),
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
    return 0 if inventory["summary"]["inventory_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

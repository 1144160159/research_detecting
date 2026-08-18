from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from .repair_truncated_final_pcap_record import atomic_json, sha256_file
except ImportError:
    from repair_truncated_final_pcap_record import atomic_json, sha256_file


def reusable_repair(entry: dict[str, Any]) -> bool:
    repaired = Path(entry.get("repaired_path", ""))
    return (
        entry.get("exact_captured_packet_multiset_preserved") is True
        and entry.get("full_tshark_scan_passed") is True
        and repaired.is_file()
        and sha256_file(repaired) == entry.get("repaired_sha256")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repair-script", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    if not audit.get("complete"):
        raise ValueError("truncated-record audit is incomplete")
    targets = sorted(
        Path(item["path"])
        for item in audit.get("results", [])
        if item.get("status") == "truncated_final_record"
    )
    if not targets:
        raise ValueError("audit contains no repair targets")

    completed: list[dict[str, Any]] = []
    for index, source in enumerate(targets, start=1):
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        existing = next(
            (
                item
                for item in manifest.get("repairs", [])
                if item.get("dataset_id") == args.dataset_id
                and item.get("source_path") == str(source)
                and item.get("source_member") is None
            ),
            None,
        )
        if existing is not None and reusable_repair(existing):
            status = "reused"
        else:
            subprocess.run(
                [
                    sys.executable,
                    str(args.repair_script),
                    "--dataset-id",
                    args.dataset_id,
                    "--source",
                    str(source),
                    "--output-root",
                    str(args.output_root),
                    "--manifest",
                    str(args.manifest),
                ],
                check=True,
            )
            status = "repaired"
        item = {
            "index": index,
            "total": len(targets),
            "path": str(source),
            "status": status,
        }
        completed.append(item)
        print(json.dumps(item, ensure_ascii=False, sort_keys=True), flush=True)

    summary = {
        "schema_version": "caeos_truncated_pcap_batch_repair_v1",
        "dataset_id": args.dataset_id,
        "target_count": len(targets),
        "repaired_count": sum(item["status"] == "repaired" for item in completed),
        "reused_count": sum(item["status"] == "reused" for item in completed),
        "items": completed,
        "repair_manifest_sha256": sha256_file(args.manifest),
        "complete": True,
    }
    atomic_json(args.summary, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

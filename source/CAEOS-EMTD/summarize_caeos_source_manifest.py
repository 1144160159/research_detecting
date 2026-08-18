from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare_caeos_unified_multimodal_csv import load_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = load_json(args.manifest)
    datasets = []
    for dataset in manifest["datasets"]:
        direct = [item for item in dataset["source_files"] if item["kind"] == "pcap"]
        archives = [item for item in dataset["source_files"] if item["kind"] == "archive"]
        archive_members = [
            member
            for archive in archives
            for member in archive.get("capture_members", [])
        ]
        direct_bytes = sum(int(item["size_bytes"]) for item in direct)
        archive_capture_bytes = sum(int(item["size_bytes"]) for item in archive_members)
        datasets.append(
            {
                "id": dataset["id"],
                "direct_pcap_count": len(direct),
                "direct_pcap_bytes": direct_bytes,
                "archive_count": len(archives),
                "archive_pcap_member_count": len(archive_members),
                "archive_pcap_member_bytes": archive_capture_bytes,
                "extensionless_archive_pcap_member_count": sum(
                    item.get("capture_detection") == "magic" for item in archive_members
                ),
                "eligible_capture_count": len(direct) + len(archive_members),
                "eligible_capture_bytes": direct_bytes + archive_capture_bytes,
            }
        )
    result = {
        "schema_version": "caeos_source_manifest_summary_v1",
        "source_manifest_sha256": manifest["manifest_sha256"],
        "datasets": datasets,
        "dataset_count": len(datasets),
        "eligible_capture_count": sum(item["eligible_capture_count"] for item in datasets),
        "eligible_capture_bytes": sum(item["eligible_capture_bytes"] for item in datasets),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

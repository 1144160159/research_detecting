from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--category-summary", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binary_labels(label_counts: dict[str, int]) -> list[int]:
    result: set[int] = set()
    for label in label_counts:
        marker = "::binary="
        if marker not in label:
            raise ValueError(f"candidate label lacks binary evidence: {label}")
        result.add(int(label.rsplit(marker, 1)[1]))
    return sorted(result)


def main() -> None:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    source_audit_hashes: dict[str, str] = {}
    for audit_path in sorted(args.audit_dir.glob("*.json")):
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        conflict_count = int(
            audit.get("counters", {}).get("status::conflicting_label", 0)
        )
        if not conflict_count:
            continue
        samples = audit.get("conflicting_samples", [])
        if audit.get("conflicting_samples_truncated") or len(samples) != conflict_count:
            raise ValueError(
                f"incomplete conflict evidence in {audit_path}: "
                f"samples={len(samples)} expected={conflict_count}"
            )
        source_audit_hashes[audit_path.name] = sha256(audit_path)
        source = str(audit.get("source_member", ""))
        for ordinal, sample in enumerate(samples, start=1):
            counts = {
                str(key): int(value)
                for key, value in sample.get("candidate_label_counts", {}).items()
            }
            if len(counts) < 2:
                raise ValueError(f"conflict lacks multiple labels in {audit_path}")
            labels = sorted(label.rsplit("::binary=", 1)[0] for label in counts)
            families = sorted({label.split("::", 1)[0] for label in labels})
            fine_labels = sorted({label.rsplit("::", 1)[-1] for label in labels})
            records = sample.get("candidate_records", [])
            rows.append(
                {
                    "conflict_id": "",
                    "source_member": source,
                    "source_audit": audit_path.name,
                    "source_conflict_ordinal": ordinal,
                    "flow_key_hash": sample.get("flow_key_hash", ""),
                    "protocol": sample.get("protocol", ""),
                    "port_a": sample.get("port_a", ""),
                    "port_b": sample.get("port_b", ""),
                    "flow_start_ns": sample.get("flow_start_ns", ""),
                    "flow_end_ns": sample.get("flow_end_ns", ""),
                    "duration_ns": sample.get("duration_ns", ""),
                    "packet_count": sample.get("packet_count", ""),
                    "packet_bytes": sample.get("packet_bytes", ""),
                    "finalize_reason": sample.get("finalize_reason", ""),
                    "binary_labels": ";".join(map(str, binary_labels(counts))),
                    "candidate_families": ";".join(families),
                    "candidate_fine_labels": ";".join(fine_labels),
                    "candidate_label_counts_json": json.dumps(
                        counts, ensure_ascii=False, sort_keys=True
                    ),
                    "candidate_record_count": sample.get(
                        "candidate_record_count", len(records)
                    ),
                    "candidate_record_ids": ";".join(
                        sorted(str(record.get("record_id", "")) for record in records)
                    ),
                    "candidate_label_sources": ";".join(
                        sorted(
                            {
                                str(record.get("label_source", ""))
                                for record in records
                                if record.get("label_source")
                            }
                        )
                    ),
                    "candidate_records_truncated": bool(
                        sample.get("candidate_records_truncated", False)
                    ),
                }
            )

    rows.sort(
        key=lambda row: (
            row["source_member"],
            int(row["flow_start_ns"]),
            row["flow_key_hash"],
        )
    )
    for ordinal, row in enumerate(rows, start=1):
        row["conflict_id"] = f"UNSW-CONFLICT-{ordinal:04d}"
    if len(rows) != 673:
        raise ValueError(f"expected exactly 673 conflict flows, found {len(rows)}")
    if any(row["binary_labels"] != "1" for row in rows):
        raise ValueError("not every conflict has unanimous binary malicious evidence")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    combinations = Counter(row["candidate_families"] for row in rows)
    summary_rows = [
        {
            "candidate_families": families,
            "flow_count": count,
            "fraction": count / len(rows),
        }
        for families, count in sorted(
            combinations.items(), key=lambda item: (-item[1], item[0])
        )
    ]
    with args.category_summary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    manifest = {
        "schema_version": "caeos_unsw_conflict_inventory_v1",
        "dataset_id": "unsw_nb15",
        "conflict_flow_count": len(rows),
        "all_binary_labels": [1],
        "category_combination_count": len(summary_rows),
        "output_csv": str(args.output_csv),
        "output_csv_sha256": sha256(args.output_csv),
        "category_summary": str(args.category_summary),
        "category_summary_sha256": sha256(args.category_summary),
        "source_audit_sha256": dict(sorted(source_audit_hashes.items())),
    }
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

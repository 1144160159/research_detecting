#!/usr/bin/env python3
"""Report non-formal rows from one or more CAEOS part markers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--marker", required=True, type=Path)
    parser.add_argument("--label-index", type=Path)
    parser.add_argument("--maximum-findings", type=int, default=20)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    columns = [item["name"] for item in schema["columns"]]
    indexes = {name: columns.index(name) for name in columns}
    marker = json.loads(args.marker.read_text(encoding="utf-8"))
    findings: list[dict[str, Any]] = []
    for part in marker.get("parts", []):
        part_path = Path(part["part_path"])
        with part_path.open("r", encoding="utf-8", newline="") as handle:
            for row_number, row in enumerate(csv.reader(handle), start=1):
                status = row[indexes["label_status"]]
                category = row[indexes["attack_category"]]
                binary_label = int(row[indexes["binary_label"]])
                if (
                    status.lower().startswith("aligned_unique_")
                    and category != "Pending"
                    and binary_label in {0, 1}
                ):
                    continue
                fields = (
                    "sample_id",
                    "capture_id",
                    "source_member",
                    "label_status",
                    "label_source",
                    "dataset_native_label",
                    "traffic_class",
                    "attack_category",
                    "attack_subcategory",
                    "fine_label",
                    "family_label",
                    "binary_label",
                    "flow_start_ns",
                    "flow_end_ns",
                    "transport_protocol",
                    "port_a",
                    "port_b",
                )
                findings.append(
                    {
                        "part_path": str(part_path),
                        "row_number": row_number,
                        **{name: row[indexes[name]] for name in fields},
                    }
                )
                if len(findings) >= args.maximum_findings:
                    break
        if len(findings) >= args.maximum_findings:
            break
    official_records: list[dict[str, Any]] = []
    if args.label_index and findings:
        sources = sorted(
            {
                source
                for finding in findings
                for source in str(finding["label_source"]).split(";")
                if source
            }
        )
        uri = f"file:{args.label_index.resolve().as_posix()}?mode=ro&immutable=1"
        connection = sqlite3.connect(uri, uri=True)
        try:
            placeholders = ",".join("?" for _ in sources)
            rows = connection.execute(
                "SELECT record_id, source_member, endpoint_a, port_a, endpoint_b, "
                "port_b, protocol, start_ns, end_ns, fine_label, family_label, "
                "binary_label, label_source FROM labels WHERE label_source IN ("
                + placeholders
                + ") ORDER BY record_id",
                sources,
            ).fetchall()
        finally:
            connection.close()
        for row in rows:
            endpoint_material = b"|".join(
                value if isinstance(value, bytes) else b"" for value in (row[2], row[4])
            )
            official_records.append(
                {
                    "record_id": row[0],
                    "source_member": row[1],
                    "endpoint_pair_sha256": hashlib.sha256(endpoint_material).hexdigest(),
                    "port_a": row[3],
                    "port_b": row[5],
                    "protocol": row[6],
                    "start_ns": row[7],
                    "end_ns": row[8],
                    "fine_label": row[9],
                    "family_label": row[10],
                    "binary_label": row[11],
                    "label_source": row[12],
                }
            )
    print(
        json.dumps(
            {
                "dataset_id": marker.get("dataset_id"),
                "capture_id": marker.get("capture_id"),
                "findings": findings,
                "finding_count": len(findings),
                "official_records": official_records,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

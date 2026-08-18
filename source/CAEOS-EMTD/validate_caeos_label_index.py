from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from caeos_label_alignment import SCHEMA_VERSION
from caeos_unified_dataset import atomic_json, sha256_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--group-counts", action="store_true")
    parser.add_argument("--require-protocol-distribution", action="store_true")
    return parser.parse_args()


def grouped(connection: sqlite3.Connection, column: str) -> dict[str, int]:
    allowed = {"fine_label", "family_label", "binary_label", "protocol"}
    if column not in allowed:
        raise ValueError(f"unsupported group column: {column}")
    return {
        str(key): int(count)
        for key, count in connection.execute(
            f"SELECT {column}, COUNT(*) FROM labels GROUP BY {column}"
        )
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    path = args.path.resolve()
    digest = sha256_file(path)
    connection = sqlite3.connect(
        f"file:{path.as_posix()}?mode=ro&immutable=1", uri=True
    )
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        quick_check_rows = [
            str(row[0]) for row in connection.execute("PRAGMA quick_check")
        ]
        actual_record_count = int(
            connection.execute("SELECT COUNT(*) FROM labels").fetchone()[0]
        )
        group_counts = (
            {
                column: grouped(connection, column)
                for column in (
                    "fine_label",
                    "family_label",
                    "binary_label",
                    "protocol",
                )
            }
            if args.group_counts
            else None
        )
    finally:
        connection.close()
    expected_record_count = int(metadata.get("record_count", -1))
    checks = {
        "schema_matches": metadata.get("schema_version") == SCHEMA_VERSION,
        "dataset_matches": metadata.get("dataset_id") == args.dataset_id,
        "quick_check_ok": quick_check_rows == ["ok"],
        "record_count_matches_metadata": actual_record_count
        == expected_record_count,
    }
    require_protocol_distribution = bool(
        getattr(args, "require_protocol_distribution", False)
    )
    protocol_counts = (group_counts or {}).get("protocol", {})
    protocol_values_valid = True
    for value in protocol_counts:
        try:
            protocol = int(value)
        except (TypeError, ValueError):
            protocol_values_valid = False
            break
        if not 0 <= protocol <= 255:
            protocol_values_valid = False
            break
    protocol_distribution_gate = {
        "required": require_protocol_distribution,
        "present": bool(protocol_counts),
        "record_count": sum(protocol_counts.values()),
        "sums_to_all_records": sum(protocol_counts.values()) == actual_record_count,
        "protocol_values_valid": protocol_values_valid,
    }
    if require_protocol_distribution:
        checks.update(
            {
                "protocol_distribution_present": protocol_distribution_gate[
                    "present"
                ],
                "protocol_distribution_sums_to_all_records": (
                    protocol_distribution_gate["sums_to_all_records"]
                ),
                "protocol_values_valid": protocol_distribution_gate[
                    "protocol_values_valid"
                ],
            }
        )
    report = {
        "schema_version": "caeos_label_index_validation_v1",
        "dataset_id": args.dataset_id,
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": digest,
        "metadata": metadata,
        "actual_record_count": actual_record_count,
        "quick_check_rows": quick_check_rows[:100],
        "quick_check_rows_truncated": len(quick_check_rows) > 100,
        "group_counts": group_counts,
        "protocol_distribution_gate": protocol_distribution_gate,
        "checks": checks,
        "passed": all(checks.values()),
        "read_only_validation": True,
    }
    report["audit_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(args.output, report)
    return report


def main() -> None:
    print(json.dumps(validate(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

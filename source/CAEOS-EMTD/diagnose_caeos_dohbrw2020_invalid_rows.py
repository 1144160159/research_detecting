from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_caeos_dohbrw2020_label_index import parsed_row
from caeos_unified_dataset import atomic_json


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-dir", required=True, type=Path)
    parser.add_argument("--tool-csv-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--maximum-samples", type=int, default=100)
    return parser.parse_args()


def diagnose(args: argparse.Namespace) -> dict[str, Any]:
    sources = [
        (args.total_dir / "l1-nondoh.csv", "Label", "NonDoH"),
        (args.total_dir / "l2-benign.csv", "Label", "Benign"),
        (args.tool_csv_root / "dns2tcp" / "all.csv", "DoH", "True"),
        (args.tool_csv_root / "dnscat2" / "all.csv", "DoH", "True"),
        (args.tool_csv_root / "iodine" / "all.csv", "DoH", "True"),
    ]
    counters: Counter[str] = Counter()
    samples: list[dict[str, Any]] = []
    for path, expected_column, expected_value in sources:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                counters["rows"] += 1
                try:
                    actual = str(row[expected_column]).strip()
                    if actual.lower() != expected_value.lower():
                        raise ValueError(
                            f"label_mismatch:{expected_column}={actual!r}"
                        )
                    parsed_row(row)
                except (KeyError, ValueError, TypeError, OverflowError) as error:
                    reason = f"{type(error).__name__}:{error}"
                    counters["invalid_rows"] += 1
                    counters[f"reason::{reason}"] += 1
                    counters[f"file::{path}::invalid_rows"] += 1
                    if len(samples) < args.maximum_samples:
                        samples.append(
                            {
                                "path": str(path),
                                "row_number": row_number,
                                "reason": reason,
                                "label_value": row.get(expected_column),
                                "source_ip": row.get("SourceIP"),
                                "destination_ip": row.get("DestinationIP"),
                                "source_port": row.get("SourcePort"),
                                "destination_port": row.get("DestinationPort"),
                                "timestamp": row.get("TimeStamp"),
                            }
                        )
                else:
                    counters["valid_rows"] += 1
    report = {
        "schema_version": "caeos_dohbrw2020_invalid_row_diagnostic_v1",
        "dataset_id": "dohbrw2020",
        "counters": dict(sorted(counters.items())),
        "samples": samples,
        "samples_truncated": counters["invalid_rows"] > len(samples),
        "source_files": [str(item[0]) for item in sources],
    }
    atomic_json(args.output, report)
    return report


def main() -> None:
    print(json.dumps(diagnose(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

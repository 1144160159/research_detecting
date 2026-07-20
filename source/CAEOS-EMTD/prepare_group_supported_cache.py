from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_group_supported_cache(
    input_path: Path,
    output_path: Path,
    *,
    label_column: str,
    group_column: str,
    minimum_groups: int,
) -> dict[str, Any]:
    if minimum_groups < 1:
        raise ValueError("minimum_groups must be positive")
    sidecar_path = Path(f"{input_path}.json")
    if not sidecar_path.is_file():
        raise FileNotFoundError(f"missing source sidecar: {sidecar_path}")
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    input_sha = file_sha256(input_path)
    if sidecar.get("output_sha256") != input_sha:
        raise ValueError("source cache SHA does not match its sidecar")

    groups: dict[str, set[str]] = defaultdict(set)
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("source cache has no header")
        for required in (label_column, group_column):
            if required not in reader.fieldnames:
                raise ValueError(f"missing required column: {required}")
        for row in reader:
            groups[row[label_column]].add(row[group_column])

    eligible = {
        label for label, values in groups.items() if len(values) >= minimum_groups
    }
    excluded = sorted(set(groups) - eligible)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    with input_path.open("r", encoding="utf-8", newline="") as source, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        assert reader.fieldnames is not None
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            if row[label_column] in eligible:
                writer.writerow(row)
                rows_written += 1

    report: dict[str, Any] = {
        "schema_version": "group_supported_cache_v1",
        "source_cache": str(input_path.resolve()),
        "source_cache_sha256": input_sha,
        "source_sidecar_sha256": file_sha256(sidecar_path),
        "source_schema_version": sidecar.get("schema_version"),
        "label_column": label_column,
        "group_column": group_column,
        "minimum_groups_per_class": minimum_groups,
        "groups_per_class": {
            label: len(values) for label, values in sorted(groups.items())
        },
        "eligible_labels": sorted(eligible),
        "excluded_labels": excluded,
        "output_rows": rows_written,
        "output_csv": str(output_path.resolve()),
        "output_sha256": file_sha256(output_path),
        "derivation": "filter complete classes by observed capture-group support",
    }
    Path(f"{output_path}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive a grouped cache containing only split-eligible classes"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label-column", required=True)
    parser.add_argument("--group-column", required=True)
    parser.add_argument("--minimum-groups", type=int, default=3)
    args = parser.parse_args()
    report = build_group_supported_cache(
        args.input,
        args.output,
        label_column=args.label_column,
        group_column=args.group_column,
        minimum_groups=args.minimum_groups,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

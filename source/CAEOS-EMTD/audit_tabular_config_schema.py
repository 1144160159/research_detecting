from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit an exact tabular header against a CAEOS modality config"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--expected-header-columns", type=int, required=True)
    parser.add_argument("--expected-excluded-columns", required=True)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def audit_schema(
    csv_path: str,
    config_path: str,
    expected_header_columns: int,
    expected_excluded_columns: set[str],
) -> dict[str, object]:
    source = Path(csv_path)
    config_file = Path(config_path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle))
    header = [column.strip() for column in header]
    if len(header) != len(set(header)):
        raise ValueError("source header contains duplicate columns")
    if len(header) != expected_header_columns:
        raise ValueError(
            f"header column count mismatch: expected={expected_header_columns}, "
            f"actual={len(header)}"
        )
    config = json.loads(config_file.read_text(encoding="utf-8"))
    label = str(config["label_column"])
    modalities = config.get("modalities")
    if not isinstance(modalities, dict) or not modalities:
        raise ValueError("config modalities are absent")
    features = [str(column) for columns in modalities.values() for column in columns]
    if len(features) != len(set(features)):
        raise ValueError("config contains duplicate feature columns")
    missing = sorted(set(features) - set(header))
    if missing:
        raise ValueError(f"configured features are absent from the source: {missing}")
    if label not in header:
        raise ValueError(f"label column {label!r} is absent from the source")
    excluded = set(header) - set(features) - {label}
    if excluded != expected_excluded_columns:
        raise ValueError(
            "excluded column set mismatch: "
            f"expected={sorted(expected_excluded_columns)}, actual={sorted(excluded)}"
        )
    return {
        "passes": True,
        "source_csv": str(source.resolve()),
        "source_size_bytes": source.stat().st_size,
        "header_column_count": len(header),
        "header_canonical_sha256": canonical_hash(header),
        "config": str(config_file.resolve()),
        "feature_count": len(features),
        "modality_feature_counts": {
            str(name): len(columns) for name, columns in modalities.items()
        },
        "label_column": label,
        "excluded_columns": sorted(excluded),
        "identity_and_absolute_time_columns_excluded": True,
    }


def main() -> None:
    args = parse_arguments()
    excluded = {
        unquote(value.strip())
        for value in args.expected_excluded_columns.split(",")
        if value.strip()
    }
    report = audit_schema(
        args.csv,
        args.config,
        args.expected_header_columns,
        excluded,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

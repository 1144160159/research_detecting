from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile a large labeled CSV without loading it into memory"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--label-column", required=True)
    parser.add_argument("--benign-labels", default="")
    parser.add_argument("--chunksize", type=int, default=250000)
    parser.add_argument("--schema-rows", type=int, default=5000)
    parser.add_argument("--sha256", action="store_true")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_labels(values: Iterable[object]) -> pd.Series:
    series = pd.Series(values, copy=False).astype("string").str.strip()
    return series.fillna("<MISSING>").replace("", "<EMPTY>")


def profile_dataset(
    csv_path: str,
    label_column: str,
    benign_labels: set[str],
    chunksize: int,
    schema_rows: int,
    include_sha256: bool,
) -> dict[str, object]:
    path = Path(csv_path)
    sample = pd.read_csv(path, nrows=schema_rows, low_memory=False)
    if label_column not in sample.columns:
        raise ValueError(
            f"label column {label_column!r} is absent; available columns: "
            f"{list(sample.columns)!r}"
        )

    counts: Counter[str] = Counter()
    total_rows = 0
    for chunk in pd.read_csv(
        path,
        usecols=[label_column],
        chunksize=chunksize,
        low_memory=False,
    ):
        labels = normalize_labels(chunk[label_column])
        chunk_counts = labels.value_counts(dropna=False)
        counts.update({str(label): int(count) for label, count in chunk_counts.items()})
        total_rows += int(len(chunk))

    ordered_counts = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    normalized_benign = {label.strip() for label in benign_labels}
    malicious_labels = [
        label
        for label in ordered_counts
        if label not in normalized_benign and label not in {"<MISSING>", "<EMPTY>"}
    ]
    report: dict[str, object] = {
        "source_csv": str(path.resolve()),
        "source_size_bytes": path.stat().st_size,
        "rows": total_rows,
        "columns": len(sample.columns),
        "column_names": [str(column) for column in sample.columns],
        "sample_dtypes": {str(column): str(dtype) for column, dtype in sample.dtypes.items()},
        "label_column": label_column,
        "label_counts": ordered_counts,
        "benign_labels": sorted(normalized_benign),
        "malicious_label_count": len(malicious_labels),
        "malicious_labels": malicious_labels,
        "sample_rows": int(len(sample)),
        "sample_missing_fraction": {
            str(column): float(value)
            for column, value in sample.isna().mean().sort_values(ascending=False).items()
            if float(value) > 0.0
        },
    }
    if include_sha256:
        report["source_sha256"] = file_sha256(path)
    return report


def main() -> None:
    args = parse_arguments()
    benign_labels = {
        value.strip() for value in args.benign_labels.split(",") if value.strip()
    }
    report = profile_dataset(
        args.csv,
        args.label_column,
        benign_labels,
        args.chunksize,
        args.schema_rows,
        args.sha256,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

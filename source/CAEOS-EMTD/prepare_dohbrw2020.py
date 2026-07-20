from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


IDENTIFIER_COLUMNS = {
    "SourceIP",
    "DestinationIP",
    "SourcePort",
    "DestinationPort",
    "TimeStamp",
    "DoH",
    "Label",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a capture-addressable DoHBrw2020 multiclass sample"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--captures-per-class", type=int, default=30)
    parser.add_argument("--rows-per-capture", type=int, default=200)
    parser.add_argument("--target-rows-per-class", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def class_directories(root: Path) -> dict[str, list[Path]]:
    malicious = root / "CSVs" / "CSVs"
    benign = root / "CSVs" / "BenignDoH-NonDoH-CSVs" / "CSVs"
    return {
        "dns2tcp": [malicious / "dns2tcp" / "Separate"],
        "dnscat2": [malicious / "dnscat2" / "Separate"],
        "iodine": [malicious / "iodine" / "Separate"],
        "benign": [benign / "Chrome" / "Separate", benign / "Firefox" / "Separate"],
    }


def discover_csvs(directories: list[Path]) -> list[Path]:
    return sorted(
        path
        for directory in directories
        for path in directory.glob("*.csv")
        if path.name.lower() != "all.csv" and path.stat().st_size > 256
    )


def sample_frame(path: Path, rows: int, rng: np.random.RandomState) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    if len(frame) > rows:
        selected = rng.choice(len(frame), size=rows, replace=False)
        frame = frame.iloc[np.sort(selected)]
    feature_columns = [
        column for column in frame.columns if column not in IDENTIFIER_COLUMNS
    ]
    return frame.loc[:, feature_columns].copy()


def main() -> None:
    args = parse_arguments()
    root = Path(args.root)
    rng = np.random.RandomState(args.seed)
    parts = []
    selected_files: dict[str, list[str]] = {}
    selected_capture_counts: dict[str, int] = {}
    feature_columns: list[str] | None = None
    for label, directories in class_directories(root).items():
        candidates = discover_csvs(directories)
        if not args.target_rows_per_class and len(candidates) < args.captures_per_class:
            raise ValueError(
                "%s has %d captures, requested %d"
                % (label, len(candidates), args.captures_per_class)
            )
        if args.target_rows_per_class:
            selected = [candidates[index] for index in rng.permutation(len(candidates))]
        else:
            indices = rng.choice(
                len(candidates), size=args.captures_per_class, replace=False
            )
            selected = [candidates[index] for index in sorted(indices)]
        selected_files[label] = []
        class_rows = 0
        for path in selected:
            frame = sample_frame(path, args.rows_per_capture, rng)
            if frame.empty:
                continue
            if args.target_rows_per_class:
                remaining = args.target_rows_per_class - class_rows
                if remaining <= 0:
                    break
                if len(frame) > remaining:
                    frame = frame.iloc[:remaining]
            current_features = list(frame.columns)
            if feature_columns is None:
                feature_columns = current_features
            if current_features != feature_columns:
                raise ValueError("feature columns differ in %s" % path)
            frame["Label"] = label
            frame["CaptureId"] = "%s/%s" % (label, path.name)
            parts.append(frame)
            class_rows += len(frame)
            selected_files[label].append(str(path.relative_to(root)))
        if args.target_rows_per_class and class_rows < args.target_rows_per_class:
            raise ValueError(
                "%s only provided %d of %d requested rows"
                % (label, class_rows, args.target_rows_per_class)
            )
        selected_capture_counts[label] = len(selected_files[label])
    output_frame = pd.concat(parts, ignore_index=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_frame.to_csv(output, index=False)
    report = {
        "root": str(root),
        "seed": args.seed,
        "captures_per_class": args.captures_per_class,
        "rows_per_capture": args.rows_per_capture,
        "target_rows_per_class": args.target_rows_per_class,
        "rows": int(len(output_frame)),
        "features": feature_columns,
        "class_rows": {
            str(label): int(count)
            for label, count in output_frame["Label"].value_counts().items()
        },
        "selected_files": selected_files,
        "selected_capture_counts": selected_capture_counts,
    }
    metadata = Path(args.metadata)
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

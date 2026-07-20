from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from caeos.data import load_stratified_reservoir, row_fingerprint


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit duplicate split leakage")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def duplicate_summary(
    frame: pd.DataFrame, label_column: str, feature_columns: list[str]
) -> dict[str, object]:
    if not feature_columns:
        return {
            "available": False,
            "reason": "no feature columns configured for this modality",
        }
    fingerprint = row_fingerprint(frame, feature_columns)
    work = pd.DataFrame(
        {
            "fingerprint": fingerprint,
            "label": frame[label_column].astype(str).str.strip(),
        }
    )
    group_sizes = work.groupby("fingerprint", sort=False).size()
    label_counts = work.groupby("fingerprint", sort=False)["label"].nunique()
    conflicting = label_counts[label_counts > 1].index
    per_class = {}
    for label, group in work.groupby("label", sort=True):
        unique = int(group["fingerprint"].nunique())
        per_class[label] = {
            "rows": int(len(group)),
            "unique_fingerprints": unique,
            "duplicate_rows": int(len(group) - unique),
            "duplicate_rate": float((len(group) - unique) / max(len(group), 1)),
        }
    return {
        "available": True,
        "rows": int(len(work)),
        "unique_fingerprints": int(len(group_sizes)),
        "duplicate_rows": int(len(work) - len(group_sizes)),
        "duplicate_rate": float(
            (len(work) - len(group_sizes)) / max(len(work), 1)
        ),
        "duplicate_groups": int((group_sizes > 1).sum()),
        "maximum_group_size": int(group_sizes.max()),
        "cross_label_groups": int(len(conflicting)),
        "rows_in_cross_label_groups": int(
            work["fingerprint"].isin(conflicting).sum()
        ),
        "per_class": per_class,
    }


def random_split_overlap(
    frame: pd.DataFrame,
    label_column: str,
    feature_columns: list[str],
    seed: int,
) -> dict[str, object]:
    train, holdout = train_test_split(
        frame,
        test_size=0.30,
        random_state=seed,
        stratify=frame[label_column],
    )
    validation, test = train_test_split(
        holdout,
        test_size=0.50,
        random_state=seed,
        stratify=holdout[label_column],
    )
    split_fingerprints = {
        "train": set(row_fingerprint(train, feature_columns).tolist()),
        "validation": set(row_fingerprint(validation, feature_columns).tolist()),
        "test": set(row_fingerprint(test, feature_columns).tolist()),
    }
    train_test = split_fingerprints["train"] & split_fingerprints["test"]
    train_validation = (
        split_fingerprints["train"] & split_fingerprints["validation"]
    )
    validation_test = (
        split_fingerprints["validation"] & split_fingerprints["test"]
    )
    return {
        "split_rows": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
        },
        "overlap_groups": {
            "train_test": int(len(train_test)),
            "train_validation": int(len(train_validation)),
            "validation_test": int(len(validation_test)),
        },
        "test_rows_with_train_fingerprint": int(
            row_fingerprint(test, feature_columns).isin(train_test).sum()
        ),
    }


def main() -> None:
    args = parse_arguments()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    label_column = str(config["label_column"])
    modalities = config["modalities"]
    feature_columns = [
        column for columns in modalities.values() for column in columns
    ]
    sampled = load_stratified_reservoir(
        args.csv,
        label_column,
        feature_columns,
        args.max_per_class,
        args.chunksize,
        args.seed,
    )
    report = {
        "csv": args.csv,
        "seed": args.seed,
        "max_per_class": args.max_per_class,
        "all_features": duplicate_summary(
            sampled, label_column, feature_columns
        ),
        "packet_sequence": duplicate_summary(
            sampled,
            label_column,
            list(modalities.get("packet_sequence", [])),
        ),
        "random_split_overlap": random_split_overlap(
            sampled, label_column, feature_columns, args.seed
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

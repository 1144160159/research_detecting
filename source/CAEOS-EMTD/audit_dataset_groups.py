from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit candidate dataset split groups")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--label-column", required=True)
    parser.add_argument("--group-column", required=True)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    group_rows: Counter[str] = Counter()
    group_labels: dict[str, set[str]] = defaultdict(set)
    label_rows: Counter[str] = Counter()
    label_groups: dict[str, set[str]] = defaultdict(set)

    for chunk in pd.read_csv(
        args.csv,
        usecols=[args.label_column, args.group_column],
        chunksize=args.chunksize,
        low_memory=False,
    ):
        labels = chunk[args.label_column].astype(str).str.strip()
        groups = chunk[args.group_column].astype(str).str.strip()
        for label, group in zip(labels, groups):
            label_rows[label] += 1
            group_rows[group] += 1
            group_labels[group].add(label)
            label_groups[label].add(group)

    report = {
        "rows": int(sum(label_rows.values())),
        "groups": len(group_rows),
        "cross_label_groups": sum(len(labels) > 1 for labels in group_labels.values()),
        "maximum_group_rows": max(group_rows.values(), default=0),
        "per_class": {
            label: {
                "rows": int(label_rows[label]),
                "groups": len(groups),
                "minimum_group_rows": min(group_rows[group] for group in groups),
                "maximum_group_rows": max(group_rows[group] for group in groups),
            }
            for label, groups in sorted(label_groups.items())
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

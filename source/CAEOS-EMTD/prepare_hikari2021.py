from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


IDENTIFIER_COLUMNS = ("uid", "originh", "originp", "responh", "responp")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a leakage-controlled HIKARI-2021 modeling CSV"
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-output", required=True)
    parser.add_argument("--chunksize", type=int, default=100000)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_output = Path(args.audit_output)
    audit_output.parent.mkdir(parents=True, exist_ok=True)

    label_counts: Counter[str] = Counter()
    raw_category_counts: Counter[str] = Counter()
    binary_by_category: dict[str, Counter[int]] = defaultdict(Counter)
    rows = 0
    wrote_header = False

    for chunk in pd.read_csv(args.input, chunksize=args.chunksize, low_memory=False):
        chunk = chunk.loc[:, ~chunk.columns.astype(str).str.startswith("Unnamed:")]
        raw_category = chunk["attack_category"].astype(str).str.strip()
        binary_label = pd.to_numeric(chunk["Label"], errors="raise").astype(int)
        label_name = raw_category.where(binary_label.eq(1), "Benign")

        chunk["LabelName"] = label_name
        # Group by source host within a class. The label is used only to define
        # split groups and is never exposed as a model feature.
        chunk["SourceGroup"] = label_name + "|" + chunk["originh"].astype(str)

        for category, binary in zip(raw_category, binary_label):
            raw_category_counts[category] += 1
            binary_by_category[category][int(binary)] += 1
        label_counts.update(label_name)
        rows += len(chunk)

        drop_columns = ["attack_category", "Label", *IDENTIFIER_COLUMNS]
        modeling = chunk.drop(columns=drop_columns)
        modeling.to_csv(
            output,
            mode="a" if wrote_header else "w",
            header=not wrote_header,
            index=False,
        )
        wrote_header = True

    audit = {
        "input": args.input,
        "output": str(output),
        "rows": rows,
        "model_label_counts": dict(sorted(label_counts.items())),
        "raw_attack_category_counts": dict(sorted(raw_category_counts.items())),
        "binary_label_by_category": {
            category: {str(label): count for label, count in sorted(counts.items())}
            for category, counts in sorted(binary_by_category.items())
        },
        "excluded_identifier_columns": list(IDENTIFIER_COLUMNS),
        "group_definition": "LabelName|originh",
    }
    audit_output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

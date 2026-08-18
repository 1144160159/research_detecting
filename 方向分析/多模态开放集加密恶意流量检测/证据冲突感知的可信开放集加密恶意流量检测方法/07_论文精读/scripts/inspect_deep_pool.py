from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


READING = Path(__file__).resolve().parents[1]
MANIFEST = READING / "04_120篇全文抽取" / "全文抽取清单.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--chars", type=int, default=1100)
    args = parser.parse_args()
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    root = Path(__file__).resolve().parents[5]
    for row in rows:
        rank = int(row["rank"])
        if not args.start <= rank <= args.end:
            continue
        text = (root / row["text_path"]).read_text(encoding="utf-8", errors="replace")
        match = re.search(r"\bAbstract\b|\ba\s*b\s*s\s*t\s*r\s*a\s*c\s*t\b", text, re.I)
        excerpt = text[match.start() : match.start() + args.chars] if match else text[: args.chars]
        excerpt = re.sub(r"\s+", " ", excerpt).strip()
        print(f"## {rank}. {row['title']}\nCATEGORY: {row['category']}\n{excerpt}\n")


if __name__ == "__main__":
    main()

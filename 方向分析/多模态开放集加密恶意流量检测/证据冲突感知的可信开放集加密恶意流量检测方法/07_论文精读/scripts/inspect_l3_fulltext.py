from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


READING = Path(__file__).resolve().parents[1]
WORKSPACE = Path(__file__).resolve().parents[5]
MANIFEST = READING / "04_120篇全文抽取" / "全文抽取清单.csv"


def clean(line: str) -> str:
    return re.sub(r"\s+", " ", line.replace("\u00ad", "")).strip()


def outline(pages: list[str]) -> None:
    pattern = re.compile(
        r"^(?:[IVXLC]+\.|[A-Z]\.|\d+(?:\.\d+)+\s|TABLE\s+[IVXLC0-9]+|FIG(?:URE)?\.?\s*\d+|APPENDIX|REFERENCES|ACKNOWLEDG)",
        re.I,
    )
    for page_no, page in enumerate(pages, start=1):
        for raw in page.splitlines():
            line = clean(raw)
            if line and pattern.match(line) and len(line) <= 180:
                print(f"P{page_no:02d}\t{line}")


def keyword_context(pages: list[str], terms: list[str]) -> None:
    for page_no, page in enumerate(pages, start=1):
        lines = [clean(line) for line in page.splitlines() if clean(line)]
        for index, line in enumerate(lines):
            low = line.lower()
            if any(term.lower() in low for term in terms):
                before = " ".join(lines[max(0, index - 1):index])
                after = " ".join(lines[index + 1:index + 3])
                print(f"P{page_no:02d}\t{clean(before + ' ' + line + ' ' + after)[:1600]}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", type=int)
    parser.add_argument("--pages", default="")
    parser.add_argument("--keywords", default="")
    args = parser.parse_args()
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        rows = {int(row["rank"]): row for row in csv.DictReader(handle)}
    row = rows[args.rank]
    text = (WORKSPACE / Path(row["text_path"])).read_text(encoding="utf-8", errors="replace")
    pages = text.split("\f")
    print(f"RANK={args.rank} PAGES={len(pages)} TITLE={row['title']}")
    if args.pages:
        wanted = []
        for item in args.pages.split(","):
            if "-" in item:
                start, end = (int(value) for value in item.split("-", 1))
                wanted.extend(range(start, end + 1))
            else:
                wanted.append(int(item))
        for page_no in wanted:
            print(f"\n===== PDF PAGE {page_no} =====\n")
            print(pages[page_no - 1])
    elif args.keywords:
        keyword_context(pages, [term for term in args.keywords.split("|") if term])
    else:
        outline(pages)


if __name__ == "__main__":
    main()

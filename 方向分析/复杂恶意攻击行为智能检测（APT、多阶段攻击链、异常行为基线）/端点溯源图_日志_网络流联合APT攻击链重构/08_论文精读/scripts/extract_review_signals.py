"""Extract concise, page-addressable reading signals from temporary packets."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


PAGE_RE = re.compile(r"^===== PDF PAGE (\d+) =====$", re.M)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

CATEGORY_PATTERNS: Dict[str, Sequence[Tuple[re.Pattern[str], int]]] = {
    "problem": (
        (re.compile(r"\b(problem|challenge|limitation|difficult|lack|fail)\b", re.I), 3),
        (re.compile(r"\b(attack investigation|provenance|intrusion|forensic)\b", re.I), 2),
    ),
    "method": (
        (re.compile(r"\b(we propose|we present|we develop|we design|our system|our approach)\b", re.I), 5),
        (re.compile(r"\b(algorithm|architecture|framework|model|graph|query|tracking)\b", re.I), 2),
    ),
    "data": (
        (re.compile(r"\b(we evaluate|evaluation uses|dataset|data set|DARPA|CADETS|THEIA|TRACE|OpTC|LANL)\b", re.I), 4),
        (re.compile(r"\b(real[- ]world|enterprise|attack scenarios?|benign)\b", re.I), 2),
    ),
    "metrics": (
        (re.compile(r"\b(precision|recall|F1|F-score|AUC|MCC|false positive)\b", re.I), 4),
        (re.compile(r"\b(throughput|latency|overhead|memory|storage|reduction|runtime)\b", re.I), 3),
    ),
    "result": (
        (re.compile(r"\b(achiev|outperform|improv|reduc|detect|recover|reconstruct)\w*\b", re.I), 3),
        (re.compile(r"\b(\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?\s*[xX])\b"), 3),
    ),
    "limitation": (
        (re.compile(r"\b(limitation|threats? to validity|future work|cannot|does not|unable|assume)\b", re.I), 5),
        (re.compile(r"\b(only|however|may fail|not support)\b", re.I), 2),
    ),
    "reproducibility": (
        (re.compile(r"\b(GitHub|source code|artifact|available online|open source|repository)\b", re.I), 5),
        (re.compile(r"\b(implementation|prototype|configuration|parameter)\b", re.I), 2),
    ),
}


def iter_pages(text: str) -> Iterable[Tuple[int, str]]:
    matches = list(PAGE_RE.finditer(text))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        yield int(match.group(1)), text[start:end].strip()


def sentences(page_text: str) -> Iterable[str]:
    normalized = re.sub(r"\s+", " ", page_text)
    for sentence in SENTENCE_RE.split(normalized):
        value = sentence.strip()
        if 60 <= len(value) <= 700:
            yield value


def score(sentence: str, rules: Sequence[Tuple[re.Pattern[str], int]]) -> int:
    return sum(weight for pattern, weight in rules if pattern.search(sentence))


def top_signals(page_records: Sequence[Tuple[int, str]], category: str, limit: int = 3) -> List[dict]:
    rules = CATEGORY_PATTERNS[category]
    candidates: List[Tuple[int, int, str]] = []
    seen = set()
    for page, page_text in page_records:
        for sentence in sentences(page_text):
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            value = score(sentence, rules)
            if value > 0:
                candidates.append((value, page, sentence))
    candidates.sort(key=lambda item: (-item[0], item[1], len(item[2])))
    return [
        {"page": page, "text": sentence[:500], "score": value}
        for value, page, sentence in candidates[:limit]
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    records = []
    for packet in sorted(args.packet_root.glob("L[0-9][0-9].txt")):
        raw = packet.read_text(encoding="utf-8", errors="replace")
        title = raw.splitlines()[0].removeprefix("TITLE: ").strip()
        page_records = list(iter_pages(raw))
        records.append(
            {
                "paper_id": packet.stem,
                "title": title,
                "review_pages": [page for page, _ in page_records],
                "signals": {
                    category: top_signals(page_records, category)
                    for category in CATEGORY_PATTERNS
                },
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print("SIGNAL_RECORDS={}".format(len(records)))
    print("OUTPUT={}".format(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


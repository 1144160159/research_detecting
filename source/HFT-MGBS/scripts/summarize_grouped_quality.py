"""Conservatively summarize repeated grouped quality probes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.quality import summarize_quality_runs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    args = parser.parse_args()
    named_runs = []
    for path in sorted(args.result_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            named_runs.append((path.name, json.load(handle)))
    summary = summarize_quality_runs(named_runs, args.minimum_repeats)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["candidate_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

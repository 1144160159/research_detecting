#!/usr/bin/env python3
"""Aggregate repeated inference-node resource samples conservatively."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.resource_evidence import (
    aggregate_resource_evidence,
    load_resource_runs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--minimum-runs", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs, provenance = load_resource_runs(args.inputs)
    result = aggregate_resource_evidence(runs, args.minimum_runs)
    result["provenance"] = provenance
    serialized = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

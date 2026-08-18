#!/usr/bin/env python3
"""Audit the bounded algorithm search without trusting reported frontiers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hft_mgbs.algorithm_optimality import audit_algorithm_search


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: {}".format(key))
        value[key] = item
    return value


def load_strict_json(path: Path):
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is not allowed")
    text = raw.decode("utf-8", errors="strict")
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "algorithm_search",
        type=Path,
        nargs="?",
        default=Path("configs/algorithm_search_rc1.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        search = load_strict_json(args.algorithm_search)
        result = audit_algorithm_search(search)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        result = {
            "schema_version": 1,
            "scope": "bounded_offline_algorithm_optimality_audit",
            "accepted": False,
            "algorithm_only_practical_optimum_proven": False,
            "production_joint_optimum_proven": False,
            "final_pareto_ingestion_allowed": False,
            "errors": ["strict_json: {}".format(error)],
        }
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

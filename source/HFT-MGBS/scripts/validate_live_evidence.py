"""Validate physical-NIC live evidence before final Pareto ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.live_evidence import audit_live_repeats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    args = parser.parse_args()
    if args.minimum_repeats <= 0:
        parser.error("--minimum-repeats must be positive")
    paths = sorted(args.evidence_dir.glob("repeat*.json"))
    runs = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            runs.append(json.load(handle))
    audit = audit_live_repeats(runs, minimum_repeats=args.minimum_repeats)
    output = audit.as_dict()
    output.update(
        {
            "schema_version": 1,
            "scope": "physical_nic_live_evidence_audit",
            "run_files": [path.name for path in paths],
            "repeat_count": len(runs),
            "final_pareto_ingestion_allowed": audit.accepted,
        }
    )
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if audit.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())

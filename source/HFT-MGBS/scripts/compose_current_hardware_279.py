#!/usr/bin/env python3
"""Compose current-hardware 2.79 Mpps candidate evidence from raw receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.current_hardware_279 import (
    compose_current_hardware_audit,
    compose_current_hardware_candidate_v2,
    compose_current_hardware_raw_run_v2,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kind",
        choices=("candidate-v1", "raw-run-v2", "candidate-v2"),
        default="candidate-v1",
    )
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--evidence", "--input", dest="evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    composers = {
        "candidate-v1": compose_current_hardware_audit,
        "raw-run-v2": compose_current_hardware_raw_run_v2,
        "candidate-v2": compose_current_hardware_candidate_v2,
    }
    result = composers[args.kind](args.profile, args.evidence)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    if not result.get("audit_complete"):
        return 3
    positive_field = "run_qualified" if args.kind == "raw-run-v2" else "candidate_evidence_qualified"
    return 0 if result.get(positive_field) else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Select a bounded runtime candidate using frozen hard constraints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.runtime_selection import (
    load_evidence_assignments,
    select_runtime_candidate,
    sha256_file,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--evidence",
        action="append",
        required=True,
        help="CANDIDATE_ID=/absolute/repeat_audit.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    evidence, provenance = load_evidence_assignments(args.evidence)
    result = select_runtime_candidate(config, evidence)
    result["provenance"] = {
        "config_path": str(args.config),
        "config_sha256": sha256_file(args.config),
        "evidence": provenance,
    }
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

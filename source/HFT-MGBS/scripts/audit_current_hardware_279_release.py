#!/usr/bin/env python3
"""Audit current-hardware 2.79 Mpps Stage A or select Stage B champion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.current_hardware_279_release import (  # noqa: E402
    audit_current_hardware_stage_a,
    select_current_hardware_stage_b,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("a", "b"), required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (
            audit_current_hardware_stage_a(args.policy, args.input)
            if args.stage == "a"
            else select_current_hardware_stage_b(args.policy, args.input)
        )
    except Exception as error:  # CLI boundary: never turn an audit bug into success.
        result = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_cli_failure_v1",
            "stage": args.stage,
            "audit_complete": False,
            "candidate_evidence_accepted": False,
            "full_pipeline_qualified": False,
            "selection_performed": False,
            "production_release_accepted": False,
            "accepted": False,
            "final_pareto_ingestion_allowed": False,
            "errors": [f"cli.audit:{type(error).__name__}:{error}"],
        }
    try:
        output_resolved = args.output.resolve(strict=False)
        protected = {
            args.policy.resolve(strict=True),
            args.input.resolve(strict=True),
        }
        if output_resolved in protected:
            raise ValueError("output must not overwrite policy or input manifest")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(args.output)
    except Exception as error:
        result = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_cli_failure_v1",
            "stage": args.stage,
            "audit_complete": False,
            "candidate_evidence_accepted": False,
            "full_pipeline_qualified": False,
            "selection_performed": False,
            "production_release_accepted": False,
            "accepted": False,
            "final_pareto_ingestion_allowed": False,
            "errors": [f"cli.output:{type(error).__name__}:{error}"],
        }
        print(
            f"release audit output failed closed: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
    accepted = (
        result.get("candidate_evidence_accepted")
        if args.stage == "a"
        else result.get("production_release_accepted")
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if accepted is True else 2


if __name__ == "__main__":
    raise SystemExit(main())

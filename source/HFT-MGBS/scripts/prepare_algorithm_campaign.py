#!/usr/bin/env python3
"""Compile the bounded A01--A10 campaign without executing it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.algorithm_campaign import (
    CampaignValidationError,
    canonical_json_bytes,
    compile_campaign_plan,
    discover_legacy_evidence,
    write_json_atomic,
)


def _failure(error: BaseException) -> dict:
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_algorithm_qualification_campaign_plan_v1",
        "execution_mode": "dry_run_plan",
        "execution_authorized": False,
        "algorithm_only_qualification_complete": False,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
        "errors": ["{}:{}".format(type(error).__name__, error)],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "configs" / "algorithm_qualification_campaign_v1.json",
    )
    parser.add_argument("--search", type=Path)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--campaign-run-id")
    parser.add_argument("--created-at-utc")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--legacy-evidence-manifest",
        type=Path,
        help=(
            "optional remote-only inventory of old summary files; hashes are "
            "explicitly non-qualifying and never enter the campaign plan"
        ),
    )
    args = parser.parse_args()
    try:
        plan = compile_campaign_plan(
            args.repo_root,
            args.contract,
            args.search,
            args.campaign_run_id,
            args.created_at_utc,
        )
        if args.legacy_evidence_manifest is not None:
            search_path = Path(plan["algorithm_search"]["path"])
            discovery = discover_legacy_evidence(search_path)
            write_json_atomic(args.legacy_evidence_manifest, discovery)
        if args.output is not None:
            write_json_atomic(args.output, plan)
        print(canonical_json_bytes(plan).decode("utf-8"), end="")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, CampaignValidationError) as error:
        result = _failure(error)
        if args.output is not None:
            write_json_atomic(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

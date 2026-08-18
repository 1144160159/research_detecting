#!/usr/bin/env python3
"""Seal small receipts from GPU-resident A01--A10 raw campaign evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.algorithm_campaign import (
    CampaignValidationError,
    finalize_campaign,
    write_json_atomic,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_root", type=Path)
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "configs" / "algorithm_qualification_campaign_v1.json",
    )
    parser.add_argument("--search", type=Path)
    parser.add_argument("--trusted-contract-sha256")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "formal success is restricted to "
            "CAMPAIGN_ROOT/receipts/campaign_receipt.json; when finalization "
            "fails before the campaign root can be trusted, this path is only "
            "used for a create-only fail-closed audit receipt"
        ),
    )
    parser.add_argument(
        "--projection-output",
        type=Path,
        help=(
            "must be CAMPAIGN_ROOT/suggested_algorithm_search_projection.json"
        ),
    )
    args = parser.parse_args()
    output = (
        args.output
        or args.campaign_root / "receipts" / "campaign_receipt.json"
    )
    projection = (
        args.projection_output
        or args.campaign_root / "suggested_algorithm_search_projection.json"
    )
    try:
        if args.trusted_contract_sha256 is None:
            raise CampaignValidationError("--trusted-contract-sha256 is required")
        result = finalize_campaign(
            args.repo_root,
            args.contract,
            args.campaign_root,
            output,
            projection,
            args.search,
            args.trusted_contract_sha256,
        )
    except (OSError, UnicodeError, ValueError, KeyError, CampaignValidationError) as error:
        result = {
            "schema_version": 1,
            "scope": "hft_mgbs_algorithm_qualification_campaign_receipt_v1",
            "audit_complete": False,
            "accepted": False,
            "campaign_evidence_complete": False,
            "algorithm_only_practical_optimum_proven": False,
            "production_joint_optimum_proven": False,
            "final_pareto_ingestion_allowed": False,
            "source_algorithm_search_modified": False,
            "raw_results_remain_on_gpu": True,
            "external_trust_root_sha256": args.trusted_contract_sha256,
            "errors": ["{}:{}".format(type(error).__name__, error)],
        }
        write_json_atomic(output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("accepted") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())

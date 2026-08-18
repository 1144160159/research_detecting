#!/usr/bin/env python3
"""Seal one qualified current-hardware normal3+fallback3 campaign."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.current_hardware_279_release import (  # noqa: E402
    build_current_hardware_campaign_receipt,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--candidate-input", type=Path, required=True)
    parser.add_argument("--candidate-audit", type=Path, required=True)
    parser.add_argument(
        "--raw-run-input", type=Path, action="append", required=True,
        help="Repeat exactly six times; the receipt verifies the normal/fallback matrix.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = build_current_hardware_campaign_receipt(
            args.policy,
            args.profile,
            args.candidate_input,
            args.candidate_audit,
            args.raw_run_input,
        )
    except Exception as error:  # CLI boundary: a malformed campaign never seals.
        print(f"campaign sealing failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    try:
        protected = {
            args.policy.resolve(strict=True),
            args.profile.resolve(strict=True),
            args.candidate_input.resolve(strict=True),
            args.candidate_audit.resolve(strict=True),
            *(path.resolve(strict=True) for path in args.raw_run_input),
        }
        if args.output.resolve(strict=False) in protected:
            raise ValueError("output must not overwrite sealed campaign input")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(args.output)
    except Exception as error:
        print(f"campaign receipt output failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

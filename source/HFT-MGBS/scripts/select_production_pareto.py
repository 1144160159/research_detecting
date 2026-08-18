#!/usr/bin/env python3
"""Select a production candidate from sealed joint evidence envelopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.production_pareto import FinalParetoSelector, SelectionPolicy


def load_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("input must be a regular non-symlink file: " + str(path))
    payload = path.read_bytes()
    loaded = json.loads(
        payload.decode("utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError("non-finite JSON constant: " + value)
        ),
    )
    return loaded, hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--algorithm-receipt-root",
        type=Path,
        help="mirror root for absolute GPU algorithm-campaign receipt paths",
    )
    args = parser.parse_args()

    policy_payload, policy_sha256 = load_json(args.policy)
    candidate_payload, candidates_sha256 = load_json(args.candidates)
    policy = SelectionPolicy.from_mapping(policy_payload)
    if not isinstance(candidate_payload, list):
        raise SystemExit("candidate input must be a JSON array")
    result = FinalParetoSelector(
        policy,
        artifact_root=args.candidates.resolve().parent,
        policy_artifact_root=args.policy.resolve().parent,
        algorithm_receipt_root=args.algorithm_receipt_root,
    ).select(candidate_payload)
    output = result.as_dict()
    output["input_sha256"] = {
        "policy": policy_sha256,
        "candidates": candidates_sha256,
        "algorithm_search": policy.algorithm_search_gate["sha256"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["production_release_accepted"] else 10


if __name__ == "__main__":
    raise SystemExit(main())

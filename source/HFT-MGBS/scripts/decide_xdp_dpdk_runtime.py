#!/usr/bin/env python3
"""Evaluate the non-mutating XDP-primary/DPDK-fallback contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# A checked-out repository must support the documented direct invocation
# `python scripts/decide_xdp_dpdk_runtime.py ...` without an editable install or
# caller-provided PYTHONPATH.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.capture_runtime_decision import (
    RuntimeDecisionContractError,
    build_runtime_decision_receipt,
    evaluate_runtime_decision,
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {value}")
        ))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Return a fail-closed, non-mutating capture runtime decision"
    )
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--raw-runtime-evidence",
        type=Path,
        help="optional immutable raw windows; when set, output is a bound receipt",
    )
    parser.add_argument(
        "--now-utc",
        help="optional timezone-qualified ISO-8601 decision time for replay/golden tests",
    )
    args = parser.parse_args()

    try:
        now = None
        if args.now_utc is not None:
            now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00"))
            if now.tzinfo is None:
                raise ValueError("--now-utc must include a timezone")
        policy_payload = load_json(args.policy)
        observation_payload = load_json(args.observation)
        if args.raw_runtime_evidence is None:
            result = evaluate_runtime_decision(
                policy_payload, observation_payload, now=now
            )
        else:
            if args.now_utc is None:
                raise ValueError("--raw-runtime-evidence requires --now-utc")
            for path in (args.policy, args.observation, args.raw_runtime_evidence):
                if not path.is_file() or path.is_symlink():
                    raise ValueError("receipt input must be a regular non-symlink file")
            policy_sha256 = hashlib.sha256(args.policy.read_bytes()).hexdigest()
            observation_sha256 = hashlib.sha256(
                args.observation.read_bytes()
            ).hexdigest()
            raw_sha256 = hashlib.sha256(
                args.raw_runtime_evidence.read_bytes()
            ).hexdigest()
            # Validate raw JSON syntax here; the final selector performs the
            # semantic recomputation and identity checks.
            load_json(args.raw_runtime_evidence)
            result = build_runtime_decision_receipt(
                policy_payload,
                observation_payload,
                policy_sha256=policy_sha256,
                observation_sha256=observation_sha256,
                raw_runtime_evidence_sha256=raw_sha256,
                observation_artifact={
                    "path": str(args.observation.resolve()),
                    "sha256": observation_sha256,
                },
                raw_runtime_evidence={
                    "path": str(args.raw_runtime_evidence.resolve()),
                    "sha256": raw_sha256,
                },
                decision_at_utc=args.now_utc,
            )
    except (OSError, json.JSONDecodeError, ValueError, RuntimeDecisionContractError) as error:
        result = {
            "schema_version": 1,
            "decision_is_non_mutating": True,
            "action": "stop_fail_closed",
            "selected_backend": None,
            "transition_permitted": False,
            "contract_error": str(error),
        }
        exit_code = 2
    else:
        # Exit 0 is a positive execution signal: keep an already-qualified
        # backend or perform an explicitly permitted transition.  Valid
        # stop/prepare/maintenance decisions use 10 so wrappers cannot mistake
        # a well-formed fail-closed result for GO.
        exit_code = (
            0
            if result.get("action") in {"keep_xdp", "keep_dpdk"}
            or result.get("transition_permitted") is True
            else 10
        )

    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(args.output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

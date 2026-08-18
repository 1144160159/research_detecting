#!/usr/bin/env python3
"""Create a fail-closed three-tier capture runtime decision or receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.capture_runtime_failover import (
    RuntimeFailoverContractError,
    build_failover_decision_receipt,
    evaluate_failover_decision,
)


def _pairs(items):
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _load(path: Path) -> Dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("regular non-symlink JSON input required: {}".format(path))
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda item: (_ for _ in ()).throw(ValueError("non-finite " + item)),
    )
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _create(path: Path, value: Dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError("output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    descriptor, temporary_raw = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    temporary = Path(temporary_raw)
    created = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(str(temporary), str(path))
        created = True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    if not created:
        raise ValueError("failed to create decision output")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decide XDP/DPDK/BCM57810 failover without mutating the host"
    )
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--now-utc", required=True)
    parser.add_argument("--seal-receipt", action="store_true")
    arguments = parser.parse_args()
    try:
        now = datetime.fromisoformat(arguments.now_utc.replace("Z", "+00:00"))
        if now.tzinfo is None:
            raise ValueError("--now-utc must include a timezone")
        policy = _load(arguments.policy)
        observation = _load(arguments.observation)
        if arguments.seal_receipt:
            result = build_failover_decision_receipt(
                policy,
                observation,
                policy_sha256=hashlib.sha256(arguments.policy.read_bytes()).hexdigest(),
                observation_sha256=hashlib.sha256(arguments.observation.read_bytes()).hexdigest(),
                decision_at_utc=arguments.now_utc,
            )
        else:
            result = evaluate_failover_decision(policy, observation, now=now)
        _create(arguments.output, result)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeFailoverContractError) as error:
        print("fail-closed: {}".format(error), file=sys.stderr)
        return 2
    return 0 if result.get("transition_permitted") is True or str(result.get("action", "")).startswith("keep_") else 10


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Recompute the backend-neutral feature loop from a Rust raw metrics file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.full_traffic_feature_loop import (
    BACKENDS,
    FullTrafficFeatureLoopError,
    audit_high_speed_metrics,
)


def _pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise FullTrafficFeatureLoopError("duplicate JSON key: " + key)
        value[key] = item
    return value


def _nonfinite(value):
    raise FullTrafficFeatureLoopError("non-finite JSON value: " + value)


def _read(path: Path):
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=_nonfinite,
    )
    if not isinstance(value, dict):
        raise FullTrafficFeatureLoopError("JSON object required: " + str(path))
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-closed-loop", action="store_true")
    args = parser.parse_args()

    raw = _read(args.metrics)
    metrics = raw.get("pipeline_metrics", raw)
    if not isinstance(metrics, dict):
        raise FullTrafficFeatureLoopError("pipeline_metrics must be an object")
    audit = audit_high_speed_metrics(metrics, backend=args.backend, policy=_read(args.policy))
    if args.output.exists() or args.output.is_symlink():
        raise FullTrafficFeatureLoopError("create-only output already exists")
    args.output.write_text(
        json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    if args.require_closed_loop and audit["method_contract_verified"] is not True:
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FullTrafficFeatureLoopError, OSError, ValueError) as error:
        print("full-traffic feature-loop audit failed: {}".format(error))
        raise SystemExit(2)


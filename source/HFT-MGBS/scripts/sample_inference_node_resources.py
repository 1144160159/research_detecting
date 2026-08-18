#!/usr/bin/env python3
"""Sample the running split-deployment inference service."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.resource_sampling import sample_deployment_resources


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--release-config", type=Path, required=True)
    parser.add_argument("--duration-s", type=float, default=20.0)
    parser.add_argument("--interval-s", type=float, default=0.1)
    parser.add_argument("--gpu-interval-s", type=float, default=0.5)
    parser.add_argument("--gpu-index", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = sample_deployment_resources(
        args.runtime_manifest,
        args.release_config,
        args.duration_s,
        args.interval_s,
        args.gpu_interval_s,
        args.gpu_index,
    )
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

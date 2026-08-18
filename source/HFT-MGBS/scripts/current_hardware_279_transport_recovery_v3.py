#!/usr/bin/env python3
"""Audit the independent current-hardware 2.79 transport-recovery v3 bundle."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from hft_mgbs.transport_recovery_279 import compose_transport_recovery_campaign_v3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compose_transport_recovery_campaign_v3(args.profile.resolve(), args.input.resolve())
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=output.name + ".", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return 0 if result["transport_recovery_qualified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

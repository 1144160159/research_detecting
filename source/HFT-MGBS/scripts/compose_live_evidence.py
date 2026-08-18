"""Build and audit one physical-NIC live evidence record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.live_raw import compose_live_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("release_candidate", type=Path)
    parser.add_argument("counter_map", type=Path)
    parser.add_argument("--latency-evidence", type=Path)
    parser.add_argument("--resource-evidence", type=Path)
    parser.add_argument("--fallback-evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    release = json.loads(
        args.release_candidate.read_text(encoding="utf-8")
    )
    counter_map = json.loads(
        args.counter_map.read_text(encoding="utf-8")
    )
    payload = compose_live_run(
        args.run_dir,
        release,
        counter_map,
        latency_evidence=args.latency_evidence,
        resource_evidence=args.resource_evidence,
        fallback_evidence=args.fallback_evidence,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            payload["composition"],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    composition = payload["composition"]
    return (
        0
        if composition["accepted"]
        or composition.get("diagnostic_accepted") is True
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())

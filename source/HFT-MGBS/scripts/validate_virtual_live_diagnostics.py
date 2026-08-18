"""Validate and aggregate non-production virtual-link diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from hft_mgbs.live_diagnostic import (
    audit_virtual_diagnostic_repeats,
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("run_dirs", type=Path, nargs="+")
    parser.add_argument("--minimum-repeats", type=int, default=3)
    args = parser.parse_args()
    runs = []
    evidence = []
    for run_dir in args.run_dirs:
        path = run_dir / "live_evidence.diagnostic.json"
        runs.append(json.loads(path.read_text(encoding="utf-8")))
        evidence.append(
            {
                "run_dir": str(run_dir),
                "live_evidence_sha256": sha256(path),
                "bundle_index_sha256": sha256(
                    run_dir / "evidence_sha256.txt"
                ),
            }
        )
    payload = audit_virtual_diagnostic_repeats(
        runs, minimum_repeats=args.minimum_repeats
    )
    payload["evidence"] = evidence
    serialized = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if payload["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

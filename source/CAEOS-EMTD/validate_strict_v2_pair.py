from __future__ import annotations

import argparse
import json
from pathlib import Path

from summarize_neural_comparison_strict_v2 import (
    _read_metrics,
    _validate_pair_identity,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate protocol and split identity for one strict-v2 pair"
    )
    parser.add_argument("--gate-metrics", required=True)
    parser.add_argument("--baseline-metrics", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    gate_path = Path(args.gate_metrics)
    baseline_path = Path(args.baseline_metrics)
    identity = _validate_pair_identity(
        _read_metrics(gate_path),
        gate_path,
        _read_metrics(baseline_path),
        baseline_path,
        (args.suite, args.scenario, args.seed),
    )
    print(
        json.dumps(
            {
                "state": "complete",
                "task": {
                    "suite": args.suite,
                    "scenario": args.scenario,
                    "seed": args.seed,
                },
                "split_fingerprint": identity["split_fingerprint"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

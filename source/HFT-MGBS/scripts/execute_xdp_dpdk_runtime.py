#!/usr/bin/env python3
"""Execute one independently rooted, replayed XDP-to-DPDK runtime decision."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.capture_runtime_executor import RuntimeExecutionError, execute_runtime_decision


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--observation", required=True, type=Path)
    parser.add_argument("--decision-receipt", required=True, type=Path)
    parser.add_argument("--execution-plan", required=True, type=Path)
    parser.add_argument("--trusted-execution-plan-sha256", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        result = execute_runtime_decision(
            policy_path=arguments.policy,
            observation_path=arguments.observation,
            decision_receipt_path=arguments.decision_receipt,
            execution_plan_path=arguments.execution_plan,
            trusted_plan_sha256=arguments.trusted_execution_plan_sha256,
            authorization=arguments.authorization,
            work_dir=arguments.work_dir,
            output_path=arguments.output,
        )
    except (RuntimeExecutionError, OSError, ValueError) as error:
        print("runtime execution rejected: {}".format(error), file=sys.stderr)
        return 74
    print("outcome={}".format(result["outcome"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

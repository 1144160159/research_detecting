#!/usr/bin/env python3
"""Execute one hash-bound v2 capture failover decision."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.capture_runtime_executor import RuntimeExecutionError
from hft_mgbs.capture_runtime_failover_executor import execute_failover_transition


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute an approved three-tier capture failover")
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--observation", type=Path, required=True)
    parser.add_argument("--decision-receipt", type=Path, required=True)
    parser.add_argument("--execution-plan", type=Path, required=True)
    parser.add_argument("--trusted-plan-sha256", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        result = execute_failover_transition(
            policy_path=arguments.policy,
            observation_path=arguments.observation,
            decision_receipt_path=arguments.decision_receipt,
            execution_plan_path=arguments.execution_plan,
            trusted_plan_sha256=arguments.trusted_plan_sha256,
            authorization=arguments.authorization,
            work_dir=arguments.work_dir,
            output_path=arguments.output,
        )
    except (OSError, ValueError, RuntimeExecutionError) as error:
        print("fail-closed: {}".format(error), file=sys.stderr)
        return 2
    print("outcome={}".format(result["outcome"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

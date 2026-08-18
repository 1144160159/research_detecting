#!/usr/bin/env python3
"""Aggregate repeated runtime capture fallback diagnostics conservatively."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate(paths: list[Path], minimum_runs: int = 3) -> dict[str, Any]:
    if len(paths) < minimum_runs:
        raise ValueError(f"at least {minimum_runs} fallback runs are required")
    runs: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, path in enumerate(paths, start=1):
        evidence = json.loads(path.read_text(encoding="utf-8"))
        observed = evidence.get("observed") or {}
        run_errors: list[str] = []
        if evidence.get("accepted") is not True:
            run_errors.append("accepted")
        if (
            evidence.get(
                "capture_driver_runtime_fallback_evidence_complete"
            )
            is not True
        ):
            run_errors.append("fallback_evidence_complete")
        if evidence.get("normal_path_zero_drop_evidence_reused") is not False:
            run_errors.append("normal_zero_drop_scope")
        if observed.get("fallback_count") != 1:
            run_errors.append("fallback_count")
        if observed.get("post_promiscuity") != 0:
            run_errors.append("post_promiscuity")
        if observed.get("post_xdp_program_absent") is not True:
            run_errors.append("post_xdp_program")
        if observed.get("post_gro_restored") is not True:
            run_errors.append("post_gro")
        if run_errors:
            errors.extend(f"run{index}.{item}" for item in run_errors)
        runs.append(
            {
                "path": str(path),
                "sha256": _sha256(path),
                "accepted": not run_errors,
                "fallback_recovery_ms": observed.get(
                    "fallback_recovery_ms"
                ),
                "fallback_packets": observed.get("fallback_packets"),
                "transition_packet_gap": observed.get(
                    "fallback_transition_packet_gap"
                ),
            }
        )
    recovery_values = [run["fallback_recovery_ms"] for run in runs]
    fallback_packets = [run["fallback_packets"] for run in runs]
    transition_gaps = [run["transition_packet_gap"] for run in runs]
    if not all(isinstance(value, (int, float)) for value in recovery_values):
        errors.append("aggregate.fallback_recovery_ms")
    fallback_packets_valid = all(
        isinstance(value, int) and value > 0 for value in fallback_packets
    )
    if not fallback_packets_valid:
        errors.append("aggregate.fallback_packets")
    transition_gaps_valid = all(
        isinstance(value, int) and value >= 0 for value in transition_gaps
    )
    if not transition_gaps_valid:
        errors.append("aggregate.transition_packet_gap")
    recovery_max = (
        max(float(value) for value in recovery_values)
        if not any(value is None for value in recovery_values)
        else None
    )
    if recovery_max is None or recovery_max > 300.0:
        errors.append("aggregate.recovery_gate")
    return {
        "schema_version": 1,
        "scope": "xdp_skb_to_af_packet_ts_runtime_fallback_repeat_audit",
        "diagnostic_only": True,
        "run_count": len(runs),
        "runs": runs,
        "observed_worst_case": {
            "fallback_recovery_ms_max": recovery_max,
            "fallback_packets_min": (
                min(fallback_packets) if fallback_packets_valid else None
            ),
            "transition_packet_gap_max": (
                max(transition_gaps) if transition_gaps_valid else None
            ),
        },
        "accepted": not errors,
        "errors": errors,
        "capture_driver_runtime_fallback_evidence_complete": not errors,
        "normal_path_zero_drop_evidence_reused": False,
        "production_fallback_evidence_complete": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--minimum-runs", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = aggregate(args.inputs, args.minimum_runs)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

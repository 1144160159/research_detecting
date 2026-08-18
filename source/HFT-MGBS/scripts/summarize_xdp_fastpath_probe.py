#!/usr/bin/env python3
"""Compose borrowed-UMEM capture-only evidence without full-pipeline claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(run_dir: Path) -> dict[str, Any]:
    thresholds = _json(run_dir / "frozen_thresholds.json")
    probe = _json(run_dir / "probe_metrics.json")
    injector = _json(run_dir / "injector_metrics.json")
    offered = int(injector["offered_packets"])
    received = int(probe["packets"])
    observed = injector.get("observed_mpps_min_1s")
    latency = probe["kernel_entry_to_borrowed_callback_latency"]
    errors: list[str] = []
    if not isinstance(observed, (int, float)) or observed < thresholds["target_load_mpps"]:
        errors.append("target_load")
    if received != offered:
        errors.append("offered_received_mismatch")
    if probe["capture_packets_dropped"] != 0:
        errors.append("capture_drop")
    if latency.get("p99_us") is None or latency["p99_us"] > thresholds["max_raw_capture_p99_us"]:
        errors.append("raw_capture_p99")
    if (
        latency.get("p999_us") is None
        or latency["p999_us"] > thresholds["max_raw_capture_p999_us"]
    ):
        errors.append("raw_capture_p999")
    return {
        "schema_version": 1,
        "scope": "r0_borrowed_umem_capture_only",
        "candidate_id": thresholds["candidate_id"],
        "target_mpps": thresholds["target_load_mpps"],
        "observed_mpps_min": observed,
        "offered_packets": offered,
        "received_packets": received,
        "offered_received_gap": offered - received,
        "capture_packets_dropped": probe["capture_packets_dropped"],
        "process_cpu_cores_average": probe["process_cpu_cores_average"],
        "queue_packets": probe["queue_packets"],
        "latency_sample_stride": probe["latency_sample_stride"],
        "kernel_entry_to_borrowed_callback_latency": latency,
        "hard_gate_passed": not errors,
        "hard_gate_errors": errors,
        "r0_capture_only_qualified": not errors,
        "full_pipeline_qualified": False,
        "production_sla_frozen": True,
        "repeats_complete": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.run_dir)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (args.run_dir / "summary.json").write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["hard_gate_passed"] else 10


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize a bounded XDP load sweep after hard-gate filtering."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def _rss_kib(path: Path) -> int:
    for line in path.read_text(encoding="utf-8").splitlines():
        if "Maximum resident set size" in line:
            return int(line.split(":", 1)[1].strip())
    raise ValueError(f"maximum RSS is missing from {path}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    no_worse = (
        left["observed_mpps_min"] >= right["observed_mpps_min"]
        and left["kernel_to_feature_p99_us"]
        <= right["kernel_to_feature_p99_us"]
        and left["gpu_batch_p99_us"] <= right["gpu_batch_p99_us"]
        and left["maximum_rss_kib"] <= right["maximum_rss_kib"]
    )
    strictly_better = (
        left["observed_mpps_min"] > right["observed_mpps_min"]
        or left["kernel_to_feature_p99_us"]
        < right["kernel_to_feature_p99_us"]
        or left["gpu_batch_p99_us"] < right["gpu_batch_p99_us"]
        or left["maximum_rss_kib"] < right["maximum_rss_kib"]
    )
    return no_worse and strictly_better


def summarize(run_dirs: list[Path]) -> dict[str, Any]:
    if not 2 <= len(run_dirs) <= 6:
        raise ValueError("load exploration must contain 2..6 controlled candidates")
    candidates: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        manifest = _manifest(run_dir / "manifest.txt")
        thresholds = _json(run_dir / "frozen_thresholds.json")
        injector = _json(run_dir / "injector_metrics.json")
        metrics = _json(run_dir / "metrics.json")
        live = _json(run_dir / "live_evidence.diagnostic.json")
        composition = live.get("composition") or {}
        latency = metrics.get("kernel_receive_to_feature_enqueue_latency") or {}
        gpu_latency = metrics.get("gpu_batch_round_trip_latency") or {}
        internal_latency = (
            metrics.get("flow_materialization_to_feature_enqueue_latency") or {}
        )
        target = float(thresholds["target_load_mpps"])
        observed = injector.get("observed_mpps_min_1s")
        hard_gate_errors: list[str] = []
        if composition.get("diagnostic_accepted") is not True:
            hard_gate_errors.append("diagnostic_accepted")
        if not isinstance(observed, (int, float)) or observed < target:
            hard_gate_errors.append("target_load")
        if metrics.get("capture_packets_dropped") != 0:
            hard_gate_errors.append("capture_drop")
        if metrics.get("key_flow_coverage", 0) < thresholds["min_key_flow_coverage"]:
            hard_gate_errors.append("key_flow_coverage")
        if metrics.get("parse_reject_rate", 1) > thresholds["max_parse_reject_rate"]:
            hard_gate_errors.append("parse_reject_rate")
        if latency.get("p99_us", float("inf")) > thresholds["max_end_to_end_p99_us"]:
            hard_gate_errors.append("end_to_end_p99")
        if latency.get("p999_us", float("inf")) > thresholds["max_end_to_end_p999_us"]:
            hard_gate_errors.append("end_to_end_p999")
        candidate = {
            "candidate_id": thresholds.get("candidate_id"),
            "run_dir": str(run_dir),
            "run_manifest_sha256": _sha256(run_dir / "manifest.txt"),
            "target_mpps": target,
            "observed_mpps_min": observed,
            "observed_gbps_min": injector.get("observed_gbps_min_1s"),
            "offered_packets": injector.get("offered_packets"),
            "packets_received": metrics.get("packets_received"),
            "capture_packets_dropped": metrics.get("capture_packets_dropped"),
            "parse_reject_rate": metrics.get("parse_reject_rate"),
            "key_flow_coverage": metrics.get("key_flow_coverage"),
            "kernel_to_feature_p99_us": latency.get("p99_us"),
            "kernel_to_feature_p999_us": latency.get("p999_us"),
            "internal_feature_p99_us": internal_latency.get("p99_us"),
            "gpu_batch_p99_us": gpu_latency.get("p99_us"),
            "maximum_rss_kib": _rss_kib(
                run_dir / "physical_process_time.txt"
            ),
            "hard_gate_passed": not hard_gate_errors,
            "hard_gate_errors": hard_gate_errors,
        }
        candidates.append(candidate)
    passing = [item for item in candidates if item["hard_gate_passed"]]
    pareto = [
        item
        for item in passing
        if not any(
            _dominates(other, item)
            for other in passing
            if other is not item
        )
    ]
    selected = (
        max(
            passing,
            key=lambda item: (
                item["target_mpps"],
                item["observed_mpps_min"],
                -item["kernel_to_feature_p99_us"],
            ),
        )
        if passing
        else None
    )
    return {
        "schema_version": 1,
        "scope": "bounded_xdp_skb_load_exploration",
        "diagnostic_only": True,
        "candidate_count": len(candidates),
        "candidate_budget": {"minimum": 2, "maximum": 6},
        "candidates": candidates,
        "passing_candidate_count": len(passing),
        "pareto_front": [item["candidate_id"] for item in pareto],
        "selected_for_confirmation": (
            selected["candidate_id"] if selected else None
        ),
        "selection_rule": (
            "highest controlled target Mpps after drop, latency, coverage, "
            "parse and load hard gates; Pareto is reported separately"
        ),
        "accepted": bool(passing),
        "production_sla_frozen": False,
        "repeats_complete": False,
        "final_selection_allowed": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.run)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

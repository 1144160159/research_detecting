#!/usr/bin/env python3
"""Bind XDP diagnostic runs to concurrently sampled inference resources."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def summarize(
    physical_runs: list[Path],
    resource_runs: list[Path],
    resource_summary_path: Path,
    minimum_overlap_s: float,
) -> dict[str, Any]:
    if len(physical_runs) != len(resource_runs) or len(physical_runs) < 3:
        raise ValueError("at least three one-to-one physical/resource pairs are required")

    resource_summary = _load_json(resource_summary_path)
    pairs: list[dict[str, Any]] = []
    errors: list[str] = []
    physical_rss_max = 0

    for index, (physical_run, resource_run_path) in enumerate(
        zip(physical_runs, resource_runs), start=1
    ):
        manifest = _parse_manifest(physical_run / "manifest.txt")
        metrics = _load_json(physical_run / "metrics.json")
        evidence = _load_json(physical_run / "live_evidence.diagnostic.json")
        resource = _load_json(resource_run_path)

        physical_start = _timestamp(manifest["started_at"])
        physical_end = _timestamp(manifest["ended_at"])
        resource_end = _timestamp(resource["generated_at"])
        resource_start = resource_end - timedelta(seconds=float(resource["duration_s"]))
        overlap_s = max(
            0.0,
            (
                min(physical_end, resource_end)
                - max(physical_start, resource_start)
            ).total_seconds(),
        )
        time_file = (physical_run / "physical_process_time.txt").read_text(
            encoding="utf-8"
        )
        rss_kib = next(
            int(line.split(":", 1)[1].strip())
            for line in time_file.splitlines()
            if "Maximum resident set size" in line
        )
        physical_rss_max = max(physical_rss_max, rss_kib)

        pair_errors: list[str] = []
        if manifest.get("capture_driver") != "xdp-skb":
            pair_errors.append("capture_driver")
        if manifest.get("capture_exit_status") != "0":
            pair_errors.append("capture_exit_status")
        if manifest.get("injector_exit_status") != "0":
            pair_errors.append("injector_exit_status")
        if manifest.get("live_composition_exit_status") != "0":
            pair_errors.append("composition_exit_status")
        composition = evidence.get("composition") or {}
        if composition.get("diagnostic_accepted") is not True:
            pair_errors.append("diagnostic_accepted")
        if metrics.get("capture_packets_dropped") != 0:
            pair_errors.append("capture_packets_dropped")
        if resource.get("accepted") is not True:
            pair_errors.append("resource_accepted")
        if resource.get("candidate_id") != "A09":
            pair_errors.append("candidate_id")
        if resource.get("runtime_candidate") != "thread_all":
            pair_errors.append("runtime_candidate")
        if overlap_s < minimum_overlap_s:
            pair_errors.append("sampling_overlap")
        if pair_errors:
            errors.extend(f"pair{index}.{item}" for item in pair_errors)

        pairs.append(
            {
                "physical_run": str(physical_run),
                "resource_run": str(resource_run_path),
                "physical_started_at": manifest["started_at"],
                "physical_ended_at": manifest["ended_at"],
                "resource_started_at": resource_start.isoformat(),
                "resource_ended_at": resource["generated_at"],
                "sampling_overlap_s": overlap_s,
                "physical_maximum_rss_kib": rss_kib,
                "physical_metrics_sha256": _sha256(physical_run / "metrics.json"),
                "resource_run_sha256": _sha256(resource_run_path),
                "accepted": not pair_errors,
                "errors": pair_errors,
            }
        )

    if resource_summary.get("accepted") is not True:
        errors.append("resource_summary.accepted")
    if resource_summary.get("run_count", 0) < 3:
        errors.append("resource_summary.run_count")

    return {
        "schema_version": 1,
        "scope": "xdp_skb_joint_diagnostic_resource_confirmation",
        "diagnostic_only": True,
        "run_count": len(pairs),
        "minimum_required_overlap_s": minimum_overlap_s,
        "pairs": pairs,
        "resource_summary": {
            "path": str(resource_summary_path),
            "sha256": _sha256(resource_summary_path),
            "identity": resource_summary.get("identity"),
            "observed_worst_case": resource_summary.get("observed_worst_case"),
        },
        "observed_worst_case": {
            "physical_maximum_rss_kib": physical_rss_max,
            **(resource_summary.get("observed_worst_case") or {}),
        },
        "accepted": not errors,
        "errors": errors,
        "diagnostic_resource_evidence_complete": not errors,
        "production_resource_evidence_complete": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--physical-run", type=Path, action="append", required=True)
    parser.add_argument("--resource-run", type=Path, action="append", required=True)
    parser.add_argument("--resource-summary", type=Path, required=True)
    parser.add_argument("--minimum-overlap-s", type=float, default=12.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(
        args.physical_run,
        args.resource_run,
        args.resource_summary,
        args.minimum_overlap_s,
    )
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

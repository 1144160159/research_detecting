"""Aggregate the frozen ens9f0 passive-shadow runtime matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CANDIDATES = {
    "shadow_b128_f1000": {"batch_size": 128, "feature_flush_us": 1000},
    "shadow_b64_f500": {"batch_size": 64, "feature_flush_us": 500},
    "shadow_b32_f250": {"batch_size": 32, "feature_flush_us": 250},
}
REPEATS = 3
GATES = {
    "capture_drop_rate": 0.0,
    "parse_reject_rate": 0.001,
    "key_flow_coverage": 0.99,
    "internal_feature_enqueue_p99_us": 5000.0,
    "gpu_batch_round_trip_p99_us": 100000.0,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_scope(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def _dominates(left: dict, right: dict) -> bool:
    keys = (
        "internal_feature_enqueue_p99_us_max",
        "gpu_batch_round_trip_p99_us_max",
        "packet_processing_p99_us_max",
    )
    no_worse = all(left[key] <= right[key] for key in keys)
    strictly_better = any(left[key] < right[key] for key in keys)
    return no_worse and strictly_better


def summarize(
    campaign_root: Path,
    candidate_ids: list[str] | None = None,
) -> dict:
    selected_ids = candidate_ids or list(CANDIDATES)
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("candidate ids must be unique")
    unknown = sorted(set(selected_ids) - set(CANDIDATES))
    if unknown:
        raise ValueError(f"unknown runtime candidates: {unknown}")
    candidate_rows = []
    for candidate_id in selected_ids:
        parameters = CANDIDATES[candidate_id]
        runs = []
        for repeat in range(1, REPEATS + 1):
            run_dir = campaign_root / f"{candidate_id}_r{repeat}"
            scope = _read_scope(run_dir / "scope.env")
            metrics_path = run_dir / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            if scope.get("runtime_candidate") != candidate_id:
                raise ValueError(
                    f"runtime candidate mismatch in {run_dir}"
                )
            if int(scope["batch_size"]) != parameters["batch_size"]:
                raise ValueError(f"batch size mismatch in {run_dir}")
            if (
                int(scope["feature_flush_us"])
                != parameters["feature_flush_us"]
            ):
                raise ValueError(f"feature flush mismatch in {run_dir}")
            runs.append(
                {
                    "repeat": repeat,
                    "path": str(run_dir),
                    "duration_s": int(scope["max_duration_s"]),
                    "metrics_sha256": _sha256(metrics_path),
                    "packets_received": metrics["packets_received"],
                    "capture_drop_rate": metrics["capture_drop_rate"],
                    "parse_reject_rate": metrics["parse_reject_rate"],
                    "key_flow_coverage": metrics["key_flow_coverage"],
                    "gpu_flows_scored": metrics["gpu_flows_scored"],
                    "gpu_batches_failed": metrics["gpu_batches_failed"],
                    "gpu_queue_full": metrics["gpu_queue_full"],
                    "fallback_flows": metrics["fallback_flows"],
                    "budget_overrun_count": metrics[
                        "budget_overrun_count"
                    ],
                    "internal_feature_enqueue_p99_us": metrics[
                        "flow_materialization_to_feature_enqueue_latency"
                    ]["p99_us"],
                    "gpu_batch_round_trip_p99_us": metrics[
                        "gpu_batch_round_trip_latency"
                    ]["p99_us"],
                    "packet_processing_p99_us": metrics[
                        "packet_processing_latency"
                    ]["p99_us"],
                }
            )

        aggregate = {
            "candidate_id": candidate_id,
            **parameters,
            "run_count": len(runs),
            "duration_s_min": min(run["duration_s"] for run in runs),
            "duration_s_max": max(run["duration_s"] for run in runs),
            "packets_received_min": min(
                run["packets_received"] for run in runs
            ),
            "capture_drop_rate_max": max(
                run["capture_drop_rate"] for run in runs
            ),
            "parse_reject_rate_max": max(
                run["parse_reject_rate"] for run in runs
            ),
            "key_flow_coverage_min": min(
                run["key_flow_coverage"] for run in runs
            ),
            "gpu_flows_scored_min": min(
                run["gpu_flows_scored"] for run in runs
            ),
            "gpu_batches_failed_max": max(
                run["gpu_batches_failed"] for run in runs
            ),
            "gpu_queue_full_max": max(
                run["gpu_queue_full"] for run in runs
            ),
            "fallback_flows_max": max(
                run["fallback_flows"] for run in runs
            ),
            "budget_overrun_count_max": max(
                run["budget_overrun_count"] for run in runs
            ),
            "internal_feature_enqueue_p99_us_max": max(
                run["internal_feature_enqueue_p99_us"] for run in runs
            ),
            "gpu_batch_round_trip_p99_us_max": max(
                run["gpu_batch_round_trip_p99_us"] for run in runs
            ),
            "packet_processing_p99_us_max": max(
                run["packet_processing_p99_us"] for run in runs
            ),
            "runs": runs,
        }
        aggregate["internal_latency_gate_utilization"] = (
            aggregate["internal_feature_enqueue_p99_us_max"]
            / GATES["internal_feature_enqueue_p99_us"]
        )
        aggregate["gpu_latency_gate_utilization"] = (
            aggregate["gpu_batch_round_trip_p99_us_max"]
            / GATES["gpu_batch_round_trip_p99_us"]
        )
        aggregate["max_latency_gate_utilization"] = max(
            aggregate["internal_latency_gate_utilization"],
            aggregate["gpu_latency_gate_utilization"],
        )
        aggregate["latency_gate_utilization_sum"] = (
            aggregate["internal_latency_gate_utilization"]
            + aggregate["gpu_latency_gate_utilization"]
        )
        errors = []
        if aggregate["duration_s_min"] != aggregate["duration_s_max"]:
            errors.append("duration_s_consistency")
        if aggregate["capture_drop_rate_max"] > GATES["capture_drop_rate"]:
            errors.append("capture_drop_rate")
        if aggregate["parse_reject_rate_max"] > GATES["parse_reject_rate"]:
            errors.append("parse_reject_rate")
        if aggregate["key_flow_coverage_min"] < GATES["key_flow_coverage"]:
            errors.append("key_flow_coverage")
        if (
            aggregate["internal_feature_enqueue_p99_us_max"]
            > GATES["internal_feature_enqueue_p99_us"]
        ):
            errors.append("internal_feature_enqueue_p99_us")
        if (
            aggregate["gpu_batch_round_trip_p99_us_max"]
            > GATES["gpu_batch_round_trip_p99_us"]
        ):
            errors.append("gpu_batch_round_trip_p99_us")
        for name in (
            "gpu_batches_failed_max",
            "gpu_queue_full_max",
            "fallback_flows_max",
            "budget_overrun_count_max",
        ):
            if aggregate[name] != 0:
                errors.append(name)
        aggregate["eligible"] = not errors
        aggregate["gate_errors"] = errors
        candidate_rows.append(aggregate)

    eligible = [row for row in candidate_rows if row["eligible"]]
    pareto = [
        row
        for row in eligible
        if not any(
            other is not row and _dominates(other, row)
            for other in eligible
        )
    ]
    pareto.sort(key=lambda row: row["candidate_id"])
    selected = None
    if pareto:
        selected = min(
            pareto,
            key=lambda row: (
                row["max_latency_gate_utilization"],
                row["latency_gate_utilization_sum"],
                row["packet_processing_p99_us_max"],
                row["candidate_id"],
            ),
        )["candidate_id"]

    return {
        "schema_version": 1,
        "scope": (
            "temporary_management_interface_runtime_matrix"
            if len(selected_ids) > 1
            else "temporary_management_interface_runtime_confirmation"
        ),
        "diagnostic_only": True,
        "capture_interface": "ens9f0",
        "candidate_count": len(selected_ids),
        "repeat_count": REPEATS,
        "total_run_count": len(selected_ids) * REPEATS,
        "hard_gates": GATES,
        "eligible_candidate_count": len(eligible),
        "diagnostic_pareto_front": [
            row["candidate_id"] for row in pareto
        ],
        "selection_policy": (
            "minimize_max_normalized_internal_and_gpu_latency_gate_"
            "utilization_then_sum_then_packet_p99"
        ),
        "selected_candidate": selected,
        "candidates": candidate_rows,
        "final_pareto_ingestion_allowed": False,
        "production_10gbe_claim_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--candidate",
        action="append",
        choices=tuple(CANDIDATES),
        dest="candidate_ids",
    )
    args = parser.parse_args()
    result = summarize(args.campaign_root, args.candidate_ids)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

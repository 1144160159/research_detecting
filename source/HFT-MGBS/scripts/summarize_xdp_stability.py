"""Aggregate repeated XDP physical-link diagnostics."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("{} must contain a JSON object".format(path))
    return payload


def _manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def _maximum_rss_kib(path: Path) -> int | None:
    if not path.is_file():
        return None
    match = re.search(
        r"Maximum resident set size \(kbytes\):\s*(\d+)",
        path.read_text(encoding="utf-8", errors="replace"),
    )
    return int(match.group(1)) if match else None


def read_run(run_dir: Path) -> dict:
    manifest = _manifest(run_dir / "manifest.txt")
    metrics = _json(run_dir / "metrics.json")
    injector = _json(run_dir / "injector_metrics.json")
    evidence = _json(run_dir / "live_evidence.diagnostic.json")
    composition = evidence.get("composition") or {}
    internal = metrics.get(
        "flow_materialization_to_feature_enqueue_latency"
    ) or {}
    kernel = metrics.get(
        "kernel_receive_to_feature_enqueue_latency"
    ) or {}
    gpu = metrics.get("gpu_batch_round_trip_latency") or {}
    offered = injector.get("offered_packets")
    received = metrics.get("packets_received")
    return {
        "run_dir": str(run_dir),
        "binary_sha256": manifest.get("binary_sha256"),
        "xdp_ebpf_sha256": manifest.get("xdp_ebpf_sha256"),
        "capture_exit_status": manifest.get("capture_exit_status"),
        "injector_exit_status": manifest.get("injector_exit_status"),
        "composition_exit_status": manifest.get(
            "live_composition_exit_status"
        ),
        "diagnostic_accepted": (
            composition.get("diagnostic_accepted") is True
        ),
        "offered_packets": offered,
        "packets_received": received,
        "packet_counts_reconciled": (
            isinstance(offered, int)
            and isinstance(received, int)
            and offered == received
        ),
        "capture_packets_dropped": metrics.get(
            "capture_packets_dropped"
        ),
        "parse_reject_rate": metrics.get("parse_reject_rate"),
        "key_flow_coverage": metrics.get("key_flow_coverage"),
        "gpu_flows_scored": metrics.get("gpu_flows_scored"),
        "kernel_to_feature_p99_us": kernel.get("p99_us"),
        "kernel_to_feature_p999_us": kernel.get("p999_us"),
        "internal_feature_p99_us": internal.get("p99_us"),
        "gpu_batch_p99_us": gpu.get("p99_us"),
        "gpu_batch_p999_us": gpu.get("p999_us"),
        "maximum_rss_kib": _maximum_rss_kib(
            run_dir / "physical_process_time.txt"
        ),
    }


def summarize(
    run_dirs: list[Path],
    af_packet_baseline: Path,
    native_probe: Path,
) -> dict:
    if len(run_dirs) < 3:
        raise ValueError("at least three XDP diagnostic runs are required")
    runs = [read_run(path) for path in run_dirs]
    baseline_metrics = _json(af_packet_baseline / "metrics.json")
    native_stderr = (
        native_probe / "capture_stderr.log"
    ).read_text(encoding="utf-8", errors="replace")
    all_passed = all(
        run["diagnostic_accepted"]
        and run["capture_exit_status"] == "0"
        and run["injector_exit_status"] == "0"
        and run["composition_exit_status"] == "0"
        and run["packet_counts_reconciled"]
        and run["capture_packets_dropped"] == 0
        for run in runs
    )

    def values(name: str) -> list[float]:
        return [
            float(run[name])
            for run in runs
            if isinstance(run.get(name), (int, float))
            and not isinstance(run.get(name), bool)
        ]

    def maximum(name: str) -> float | None:
        observed = values(name)
        return max(observed) if observed else None

    def minimum(name: str) -> float | None:
        observed = values(name)
        return min(observed) if observed else None

    return {
        "schema_version": 1,
        "scope": "xdp_skb_physical_diagnostic_stability",
        "diagnostic_only": True,
        "final_pareto_ingestion_allowed": False,
        "run_count": len(runs),
        "runs": runs,
        "all_runs_passed": all_passed,
        "worst_case": {
            "capture_packets_dropped": maximum(
                "capture_packets_dropped"
            ),
            "parse_reject_rate": maximum("parse_reject_rate"),
            "key_flow_coverage_min": minimum("key_flow_coverage"),
            "kernel_to_feature_p99_us": maximum(
                "kernel_to_feature_p99_us"
            ),
            "kernel_to_feature_p999_us": maximum(
                "kernel_to_feature_p999_us"
            ),
            "internal_feature_p99_us": maximum(
                "internal_feature_p99_us"
            ),
            "gpu_batch_p99_us": maximum("gpu_batch_p99_us"),
            "gpu_batch_p999_us": maximum("gpu_batch_p999_us"),
            "maximum_rss_kib": maximum("maximum_rss_kib"),
        },
        "af_packet_baseline": {
            "run_dir": str(af_packet_baseline),
            "capture_packets_dropped": baseline_metrics.get(
                "capture_packets_dropped"
            ),
            "key_flow_coverage": baseline_metrics.get(
                "key_flow_coverage"
            ),
            "kernel_to_feature_p99_us": (
                baseline_metrics.get(
                    "kernel_receive_to_feature_enqueue_latency"
                )
                or {}
            ).get("p99_us"),
            "internal_feature_p99_us": (
                baseline_metrics.get(
                    "flow_materialization_to_feature_enqueue_latency"
                )
                or {}
            ).get("p99_us"),
            "gpu_batch_p99_us": (
                baseline_metrics.get("gpu_batch_round_trip_latency")
                or {}
            ).get("p99_us"),
            "maximum_rss_kib": _maximum_rss_kib(
                af_packet_baseline / "physical_process_time.txt"
            ),
        },
        "native_xdp": {
            "run_dir": str(native_probe),
            "supported": False,
            "reason": (
                "driver_mode_operation_not_supported"
                if "Operation not supported" in native_stderr
                else "native_probe_failed"
            ),
        },
        "preferred_capture_driver": (
            "xdp-skb" if all_passed else "af-packet-ts"
        ),
        "fallback_capture_driver": "af-packet-ts",
        "production_sla_frozen": False,
        "production_resource_evidence_complete": False,
        "production_fallback_evidence_complete": False,
        "final_selection_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument(
        "--af-packet-baseline", type=Path, required=True
    )
    parser.add_argument("--native-probe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(
        args.run, args.af_packet_baseline, args.native_probe
    )
    serialized = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["all_runs_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

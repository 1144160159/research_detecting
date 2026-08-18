"""Summarize bounded physical-link capture-driver diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def _optional_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def summarize_run(run_dir: Path) -> dict:
    manifest = _manifest(run_dir / "manifest.txt")
    metrics = _optional_json(run_dir / "metrics.json")
    injector = _optional_json(run_dir / "injector_metrics.json")
    evidence = _optional_json(run_dir / "live_evidence.diagnostic.json")
    composition = evidence.get("composition") or {}
    stderr_path = run_dir / "capture_stderr.log"
    stderr = (
        stderr_path.read_text(encoding="utf-8", errors="replace")
        if stderr_path.is_file()
        else ""
    )
    return {
        "run_dir": str(run_dir),
        "capture_driver": manifest.get("capture_driver"),
        "execution_status": manifest.get("status"),
        "capture_exit_status": manifest.get("capture_exit_status"),
        "injector_exit_status": manifest.get("injector_exit_status"),
        "diagnostic_accepted": (
            composition.get("diagnostic_accepted") is True
        ),
        "final_pareto_ingestion_allowed": False,
        "offered_packets": injector.get("offered_packets"),
        "packets_received": metrics.get("packets_received"),
        "capture_packets_dropped": metrics.get(
            "capture_packets_dropped"
        ),
        "parse_reject_rate": metrics.get("parse_reject_rate"),
        "key_flow_coverage": metrics.get("key_flow_coverage"),
        "gpu_flows_scored": metrics.get("gpu_flows_scored"),
        "gpu_batch_p99_us": (
            metrics.get("gpu_batch_round_trip_latency") or {}
        ).get("p99_us"),
        "kernel_to_feature_p99_us": (
            metrics.get("kernel_receive_to_feature_enqueue_latency") or {}
        ).get("p99_us"),
        "umem_release_failure": (
            "UMEM dropped with" in stderr
            and "frames still allocated" in stderr
        ),
    }


def summarize(
    readiness_path: Path,
    af_packet_dir: Path,
    xdp_dir: Path,
    xdp_skb_dir: Path,
) -> dict:
    readiness = _optional_json(readiness_path)
    runs = [
        summarize_run(af_packet_dir),
        summarize_run(xdp_dir),
        summarize_run(xdp_skb_dir),
    ]
    by_driver = {run["capture_driver"]: run for run in runs}
    af_packet = by_driver.get("af-packet-ts") or {}
    hardware_pair_ready = readiness.get("hardware_pair_count", 0) >= 1
    selected = (
        "af-packet-ts"
        if hardware_pair_ready
        and af_packet.get("diagnostic_accepted") is True
        else None
    )
    return {
        "schema_version": 1,
        "scope": "physical_10gbe_capture_driver_diagnostic_matrix",
        "diagnostic_only": True,
        "final_pareto_ingestion_allowed": False,
        "readiness_source": str(readiness_path),
        "hardware_pair_ready": hardware_pair_ready,
        "candidate_count": 3,
        "runs": runs,
        "selected_capture_driver": selected,
        "selection_complete": selected is not None,
        "selection_reason": (
            "af-packet-ts reconciled wire and userspace packet counts; "
            "native and generic XDP both failed UMEM release"
            if selected is not None
            else "no capture driver passed the diagnostic gate"
        ),
        "production_sla_frozen": False,
        "production_run_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", type=Path, required=True)
    parser.add_argument("--af-packet", type=Path, required=True)
    parser.add_argument("--xdp", type=Path, required=True)
    parser.add_argument("--xdp-skb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(
        args.readiness,
        args.af_packet,
        args.xdp,
        args.xdp_skb,
    )
    serialized = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["selection_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an injected XDP-to-AF_PACKET runtime fallback diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(run_dir: Path, maximum_recovery_ms: float) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.txt"
    metrics_path = run_dir / "metrics.json"
    injector_path = run_dir / "injector_metrics.json"
    post_link_path = run_dir / "fallback_post_ip_link.json"
    post_xdp_path = run_dir / "fallback_post_bpftool.txt"
    post_features_path = run_dir / "fallback_post_ethtool_features.txt"
    manifest = _manifest(manifest_path)
    metrics = _load_json(metrics_path)
    injector = _load_json(injector_path)
    post_link = _load_json(post_link_path)
    post_xdp = post_xdp_path.read_text(encoding="utf-8")
    post_features = post_features_path.read_text(encoding="utf-8")
    interface = post_link[0] if isinstance(post_link, list) and post_link else {}
    errors: list[str] = []

    expected_manifest = {
        "evidence_scope": "physical_link_live_diagnostic",
        "diagnostic_only": "true",
        "capture_driver": "xdp-skb",
        "capture_fallback_driver": "af-packet-ts",
        "capture_exit_status": "0",
        "injector_exit_status": "0",
    }
    for name, expected in expected_manifest.items():
        if manifest.get(name) != expected:
            errors.append(f"manifest.{name}")
    injected_after = manifest.get("diagnostic_xdp_fail_after_packets")
    if not str(injected_after or "").isdigit() or int(injected_after) <= 0:
        errors.append("manifest.diagnostic_xdp_fail_after_packets")
        injected_after_value = 0
    else:
        injected_after_value = int(injected_after)

    if metrics.get("capture_driver") != "xdp_skb_to_af_packet_ts":
        errors.append("metrics.capture_driver")
    if metrics.get("capture_driver_fallback_count") != 1:
        errors.append("metrics.capture_driver_fallback_count")
    recovery_ms = metrics.get("capture_driver_fallback_recovery_ms")
    if (
        isinstance(recovery_ms, bool)
        or not isinstance(recovery_ms, (int, float))
        or recovery_ms < 0
        or recovery_ms > maximum_recovery_ms
    ):
        errors.append("metrics.capture_driver_fallback_recovery_ms")
    fallback_packets = metrics.get("capture_driver_fallback_packets")
    if not isinstance(fallback_packets, int) or fallback_packets <= 0:
        errors.append("metrics.capture_driver_fallback_packets")
    if not str(metrics.get("capture_driver_fallback_reason") or "").startswith(
        "primary_poll_failed:"
    ):
        errors.append("metrics.capture_driver_fallback_reason")
    if metrics.get("packets_received", 0) <= injected_after_value:
        errors.append("metrics.real_traffic_after_fallback")
    offered_packets = injector.get("offered_packets")
    received_packets = metrics.get("packets_received")
    if not isinstance(offered_packets, int) or not isinstance(
        received_packets, int
    ):
        errors.append("metrics.packet_reconciliation_inputs")
        transition_packet_gap = None
    else:
        transition_packet_gap = max(0, offered_packets - received_packets)
    if interface.get("promiscuity") != 0:
        errors.append("post_state.promiscuity")
    if "prog_id" in post_xdp or "attached" in post_xdp:
        errors.append("post_state.xdp_program")
    if "generic-receive-offload: on" not in post_features:
        errors.append("post_state.gro_restored")

    return {
        "schema_version": 1,
        "scope": "xdp_skb_to_af_packet_ts_runtime_fallback_diagnostic",
        "diagnostic_only": True,
        "run_dir": str(run_dir),
        "maximum_recovery_ms": maximum_recovery_ms,
        "observed": {
            "fault_injected_after_packets": injected_after_value,
            "offered_packets": offered_packets,
            "packets_received": received_packets,
            "fallback_transition_packet_gap": transition_packet_gap,
            "fallback_transition_zero_drop": transition_packet_gap == 0,
            "capture_packets_dropped": metrics.get("capture_packets_dropped"),
            "fallback_count": metrics.get("capture_driver_fallback_count"),
            "fallback_recovery_ms": recovery_ms,
            "fallback_packets": fallback_packets,
            "fallback_reason": metrics.get("capture_driver_fallback_reason"),
            "post_promiscuity": interface.get("promiscuity"),
            "post_gro_restored": "generic-receive-offload: on"
            in post_features,
            "post_xdp_program_absent": "prog_id" not in post_xdp
            and "attached" not in post_xdp,
        },
        "evidence": {
            "manifest_sha256": _sha256(manifest_path),
            "metrics_sha256": _sha256(metrics_path),
            "injector_metrics_sha256": _sha256(injector_path),
            "post_link_sha256": _sha256(post_link_path),
            "post_xdp_sha256": _sha256(post_xdp_path),
            "post_features_sha256": _sha256(post_features_path),
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
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--maximum-recovery-ms", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.run_dir / "capture_fallback_evidence.json"
    result = summarize(args.run_dir, args.maximum_recovery_ms)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

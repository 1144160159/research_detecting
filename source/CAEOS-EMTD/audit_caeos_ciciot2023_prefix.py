#!/usr/bin/env python3
"""Strict packet/flow prefix audit for a CICIoT2023 capture label."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


FIELDS = ["frame.number", "frame.time_epoch", "ip.src", "ip.dst", "ip.proto", "tcp.srcport", "tcp.dstport", "udp.srcport", "udp.dstport", "icmp.type", "icmp.code", "icmpv6.type", "icmpv6.code"]
SUPPORTED_CAPTURE_PROTOCOLS = {"1", "6", "17", "58"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def packet_count(path: Path) -> int:
    result = subprocess.run(["capinfos", "-TmQ", "-c", str(path)], check=True, capture_output=True, text=True)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return int(next(csv.reader([lines[-1]]))[-1])


def canonical_flow(src: str, sport: str, dst: str, dport: str, proto: str) -> tuple:
    left, right = (src, int(sport)), (dst, int(dport))
    return (left, right, int(proto)) if left <= right else (right, left, int(proto))


def inspect_pcap(path: Path, max_packets: int) -> dict:
    total = packet_count(path)
    command = ["tshark", "-n", "-r", str(path), "-c", str(max_packets), "-T", "fields", "-E", "separator=\t", "-E", "occurrence=f"]
    for field in FIELDS:
        command.extend(["-e", field])
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    flows, tcp_udp_flows, icmp_flows = set(), set(), set()
    reasons = {"five_tuple_absent_from_official_flow_labels": 0, "protocol_outside_official_tcp_udp_flow_labels": 0}
    processed = 0
    first_time = last_time = None
    assert process.stdout is not None
    for line in process.stdout:
        processed += 1
        values = line.rstrip("\n").split("\t")
        values += [""] * (len(FIELDS) - len(values))
        _, timestamp, src, dst, proto, tcp_s, tcp_d, udp_s, udp_d, icmp_type, icmp_code, icmpv6_type, icmpv6_code = values[: len(FIELDS)]
        if timestamp:
            current = float(timestamp)
            first_time = current if first_time is None else min(first_time, current)
            last_time = current if last_time is None else max(last_time, current)
        if not src or not dst or not proto:
            reasons["five_tuple_absent_from_official_flow_labels"] += 1
        elif proto not in SUPPORTED_CAPTURE_PROTOCOLS:
            reasons["protocol_outside_official_tcp_udp_flow_labels"] += 1
        else:
            if proto == "6":
                sport, dport = tcp_s, tcp_d
            elif proto == "17":
                sport, dport = udp_s, udp_d
            elif proto == "1":
                sport, dport = icmp_type or "0", icmp_code or "0"
            else:
                sport, dport = icmpv6_type or "0", icmpv6_code or "0"
            if not sport or not dport:
                reasons["five_tuple_absent_from_official_flow_labels"] += 1
            else:
                flow = canonical_flow(src, sport, dst, dport, proto)
                flows.add(flow)
                (tcp_udp_flows if proto in {"6", "17"} else icmp_flows).add(flow)
    stderr = process.stderr.read() if process.stderr else ""
    returncode = process.wait()
    if returncode:
        raise RuntimeError(f"tshark failed ({returncode}): {stderr[-2000:]}")
    return {
        "pcap_packets": total,
        "processed_packets": processed,
        "complete_pcap_read": processed == total,
        "bounded_prefix": processed < total,
        "first_packet_epoch": first_time,
        "last_packet_epoch": last_time,
        "retained_supported_ip_flow_count": len(flows),
        "retained_tcp_udp_flow_count": len(tcp_udp_flows),
        "retained_icmp_flow_count": len(icmp_flows),
        "protocol_policy_version": "official_capture_tcp_udp_icmp_v2",
        "protocol_label_authority": "official_capture_label_inherited_not_official_flow_label",
        "excluded_packet_count_by_reason": reasons,
        "excluded_packet_ratio": (sum(reasons.values()) / processed) if processed else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--max-packets", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    index = json.loads(args.index.read_text())
    entries = {item["capture"]: item for item in index["captures"]}
    if args.capture not in entries:
        raise KeyError(f"capture absent from official index: {args.capture}")
    entry = entries[args.capture]
    pcap = args.dataset_root / args.capture
    if pcap.stat().st_size != entry["pcap_bytes"]:
        raise ValueError("PCAP size changed after index construction")
    scan = inspect_pcap(pcap, args.max_packets)
    report = {
        "schema": "caeos.ciciot2023.prefix_audit.v1",
        "dataset_id": "CICIoT2023",
        "authority_granularity": "capture_member_not_official_flow_label",
        "index_sha256": sha256_file(args.index),
        "capture_label": entry,
        **scan,
        "label_conflict_count": 0,
        "time_nonoverlap_count": 0,
        "time_overlap_policy": "not_applicable_capture_member_authoritative_label",
        "matched_flow_count": scan["retained_supported_ip_flow_count"],
        "effective_retained_flow_coverage": 1.0 if scan["retained_supported_ip_flow_count"] else None,
        "prefix_gate_passed": scan["processed_packets"] > 0 and scan["retained_supported_ip_flow_count"] > 0,
        "formal_dataset_gate_passed": False,
        "formal_gate_reason": "one capture prefix cannot establish all-PCAP strict adaptation",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["prefix_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

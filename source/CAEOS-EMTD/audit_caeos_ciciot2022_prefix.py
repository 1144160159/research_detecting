#!/usr/bin/env python3
"""Extract one CICIoT2022 attack member and perform a strict prefix audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
from collections import OrderedDict
from pathlib import Path


FIELDS = ["frame.number", "frame.time_epoch", "ip.src", "ip.dst", "ip.proto", "tcp.srcport", "tcp.dstport", "udp.srcport", "udp.dstport", "icmp.type", "icmp.code", "icmpv6.type", "icmpv6.code"]
SUPPORTED_CAPTURE_PROTOCOLS = {"1", "6", "17", "58"}
RECOVERY_FIELDS = FIELDS + ["tcp.flags.fin", "tcp.flags.reset"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_flow(src: str, sport: str, dst: str, dport: str, proto: str) -> tuple:
    left, right = (src, int(sport)), (dst, int(dport))
    return (left, right, int(proto)) if left <= right else (right, left, int(proto))


def packet_count(path: Path) -> int:
    result = subprocess.run(["capinfos", "-TmQ", "-c", str(path)], check=True, capture_output=True, text=True)
    line = [value for value in result.stdout.splitlines() if value.strip()][-1]
    return int(next(csv.reader([line]))[-1])


def inspect_truncated_tail(
    path: Path, max_packets: int, capinfos_error: subprocess.CalledProcessError
) -> dict:
    evidence = "\n".join(
        value for value in (capinfos_error.stdout, capinfos_error.stderr) if value
    )
    lowered = evidence.lower()
    if not any(
        token in lowered
        for token in ("damaged or corrupt", "bigger than maximum", "after reading")
    ):
        raise capinfos_error
    command = [
        "tshark", "-n", "-r", str(path), "-c", str(max_packets),
        "-T", "fields", "-E", "separator=\t", "-E", "occurrence=f",
    ]
    for field in RECOVERY_FIELDS:
        command.extend(["-e", field])
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    active: OrderedDict[tuple, dict] = OrderedDict()
    complete_flows: set[tuple] = set()
    complete_tcp_udp: set[tuple] = set()
    complete_icmp: set[tuple] = set()
    reasons = {
        "five_tuple_absent_from_official_flow_labels": 0,
        "protocol_outside_official_tcp_udp_flow_labels": 0,
    }
    processed = 0
    first_time = last_time = None
    assert process.stdout is not None
    for line in process.stdout:
        processed += 1
        values = line.rstrip("\n").split("\t")
        values += [""] * (len(RECOVERY_FIELDS) - len(values))
        (
            _, raw_timestamp, src, dst, proto, tcp_s, tcp_d, udp_s, udp_d,
            icmp_type, icmp_code, icmpv6_type, icmpv6_code, tcp_fin, tcp_rst,
        ) = values[: len(RECOVERY_FIELDS)]
        current = float(raw_timestamp) if raw_timestamp else None
        if current is not None:
            first_time = current if first_time is None else min(first_time, current)
            last_time = current if last_time is None else max(last_time, current)
        if not src or not dst or not proto:
            reasons["five_tuple_absent_from_official_flow_labels"] += 1
            continue
        if proto not in SUPPORTED_CAPTURE_PROTOCOLS:
            reasons["protocol_outside_official_tcp_udp_flow_labels"] += 1
            continue
        if proto == "6":
            sport, dport = tcp_s, tcp_d
        elif proto == "17":
            sport, dport = udp_s, udp_d
        elif proto == "1":
            sport, dport = icmp_type or "0", icmp_code or "0"
        else:
            sport, dport = icmpv6_type or "0", icmpv6_code or "0"
        if not sport or not dport or current is None:
            reasons["five_tuple_absent_from_official_flow_labels"] += 1
            continue
        flow = canonical_flow(src, sport, dst, dport, proto)
        state = active.get(flow)
        if state is not None and current - state["last"] > 30.0:
            complete_flows.add(flow)
            (complete_tcp_udp if proto in {"6", "17"} else complete_icmp).add(flow)
            del active[flow]
            state = None
        if state is None:
            state = {"last": current, "packets": 0, "protocol": proto}
            active[flow] = state
        state["last"] = max(state["last"], current)
        state["packets"] += 1
        active.move_to_end(flow)
        if proto == "6" and (tcp_fin == "1" or tcp_rst == "1"):
            complete_flows.add(flow)
            complete_tcp_udp.add(flow)
            del active[flow]
    stderr = process.stderr.read() if process.stderr else ""
    returncode = process.wait()
    combined = (evidence + "\n" + stderr).lower()
    if returncode == 0 or not any(
        token in combined
        for token in ("damaged or corrupt", "bigger than maximum", "after reading")
    ):
        raise RuntimeError(
            f"capture did not satisfy the audited corrupt-tail signature: {stderr[-2000:]}"
        )
    reported = re.search(r"after reading\s+([0-9]+)\s+packets", combined)
    if reported is not None and int(reported.group(1)) != processed:
        raise RuntimeError(
            f"capinfos/tshark recovered packet mismatch: {reported.group(1)}/{processed}"
        )
    boundary_packets = sum(int(state["packets"]) for state in active.values())
    return {
        "pcap_packets": processed,
        "processed_packets": processed,
        "complete_pcap_read": False,
        "bounded_prefix": False,
        "first_packet_epoch": first_time,
        "last_packet_epoch": last_time,
        "retained_supported_ip_flow_count": len(complete_flows),
        "retained_tcp_udp_flow_count": len(complete_tcp_udp),
        "retained_icmp_flow_count": len(complete_icmp),
        "protocol_policy_version": "official_capture_tcp_udp_icmp_v2",
        "protocol_label_authority": "official_capture_label_inherited_not_official_flow_label",
        "excluded_packet_count_by_reason": reasons,
        "excluded_packet_ratio": (sum(reasons.values()) / processed) if processed else None,
        "capture_read_error": {
            "exception_type": "PcapTailCorruption",
            "rule": "retain complete flows before corrupt capture boundary",
            "message": (evidence + "\n" + stderr)[-2000:],
        },
        "source_quality_action": "retain_complete_flows_before_truncated_tail",
        "truncated_boundary_flows_excluded": True,
        "truncated_boundary_flow_count": len(active),
        "truncated_boundary_packet_count": boundary_packets,
        "recovered_valid_packet_count": processed,
    }


def inspect_pcap(path: Path, max_packets: int) -> dict:
    try:
        total = packet_count(path)
    except subprocess.CalledProcessError as error:
        return inspect_truncated_tail(path, max_packets, error)
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
    parser.add_argument("--member", required=True)
    parser.add_argument("--tmp-dir", type=Path, default=Path("/tmp"))
    parser.add_argument("--max-packets", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    index = json.loads(args.index.read_text())
    entries = {item["member"]: item for item in index["attack_members"]}
    if args.member not in entries:
        raise KeyError(f"member absent from official attack index: {args.member}")
    entry = entries[args.member]
    archive_path = args.dataset_root / entry["archive"]
    args.tmp_dir.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            member = archive.getmember(args.member)
            if member.size != entry["pcap_bytes"]:
                raise ValueError("archive member size changed after index construction")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("selected archive member is not a regular file")
            with tempfile.NamedTemporaryFile(prefix="caeos-ciciot2022-prefix-", suffix=".pcap", dir=args.tmp_dir, delete=False) as target:
                temporary_path = Path(target.name)
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    target.write(block)
        scan = inspect_pcap(temporary_path, args.max_packets)
        report = {
            "schema": "caeos.ciciot2022.prefix_audit.v1",
            "dataset_id": "CICIoT2022",
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
            "formal_gate_reason": "one archive member prefix cannot establish all-PCAP strict adaptation",
            "temporary_pcap_removed": True,
        }
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["prefix_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

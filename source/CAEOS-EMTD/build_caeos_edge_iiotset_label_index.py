from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import re
from collections import Counter, OrderedDict
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Iterator

import dpkt

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json
from prepare_caeos_unified_multimodal_csv import packet_reader, parse_packet


DATASET_ID = "edge_iiotset"
MISSING_IP_VALUES = {"", "0", "0.0"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", required=True, type=Path)
    parser.add_argument("--packet-csv", required=True, type=Path)
    parser.add_argument("--source-member", required=True)
    parser.add_argument("--label-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--idle-seconds", type=float, default=30.0)
    return parser.parse_args()


def integer_cell(value: str) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    return int(float(text))


def normalize_attack_type(value: str) -> str:
    text = " ".join(str(value or "").strip().replace("_", " ").split())
    return text or "Benign"


def frame_clock_ns(value: str) -> int:
    match = re.search(r"(\d{1,2}):(\d{2}):(\d{2}(?:\.\d+)?)", str(value))
    if match is None:
        raise ValueError(f"unparseable official frame.time clock: {value!r}")
    hour, minute, second = match.groups()
    return int(
        (
            Decimal(int(hour) * 3600 + int(minute) * 60)
            + Decimal(second)
        )
        * 1_000_000_000
    )


def packed_ip(value: str) -> bytes | None:
    text = str(value or "").strip()
    if text in MISSING_IP_VALUES:
        return None
    try:
        return ipaddress.ip_address(text).packed
    except ValueError:
        return None


def official_csv_layout(row: dict[str, str]) -> str:
    source = packed_ip(row["ip.src_host"])
    destination = packed_ip(row["ip.dst_host"])
    try:
        frame_clock_ns(row["frame.time"])
    except ValueError:
        if "mitm" in normalize_attack_type(row["Attack_type"]).lower():
            return "official_packet_order_only_mitm_v1"
        shifted_source = packed_ip(row["frame.time"])
        if (
            shifted_source is not None
            and source is not None
            and destination is None
        ):
            return "official_shifted_no_timestamp_ip_v1"
        raise ValueError(
            "unsupported official Edge-IIoTset CSV layout: frame.time is not a "
            "clock and the row does not match a verified shifted IP layout"
        )
    return "official_timestamped_packet_rows_v1"


def shifted_row_kind(row: dict[str, str]) -> str:
    if packed_ip(row["frame.time"]) is not None and packed_ip(
        row["ip.src_host"]
    ) is not None:
        return "ip"
    if packed_ip(row.get("ip.dst_host", "")) is not None and packed_ip(
        row.get("arp.hw.size", "")
    ) is not None:
        return "arp"
    return "unidentifiable_non_ip"


def shifted_arp_matches(frame: bytes, row: dict[str, str]) -> bool:
    try:
        payload: Any = dpkt.ethernet.Ethernet(frame).data
    except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
        return False
    while hasattr(payload, "data") and not isinstance(payload, dpkt.arp.ARP):
        payload = payload.data
    if not isinstance(payload, dpkt.arp.ARP):
        return False
    official_destination = packed_ip(row.get("ip.dst_host", ""))
    official_source = packed_ip(row.get("arp.hw.size", ""))
    if official_source is None or official_destination is None:
        return False
    return (
        {bytes(payload.spa), bytes(payload.tpa)}
        == {official_source, official_destination}
        and int(payload.op) == integer_cell(row.get("arp.dst.proto_ipv4", ""))
    )


def shifted_numeric_integers(row: dict[str, str]) -> set[int]:
    values: set[int] = set()
    for value in row.values():
        try:
            values.add(int(float(str(value or "").strip())))
        except (ValueError, OverflowError):
            continue
    return values


def shifted_ip_protocol_matches(
    row: dict[str, str], protocol: int, port_a: int, port_b: int
) -> bool:
    if protocol in {6, 17}:
        required_ports = {int(port_a), int(port_b)} - {0}
        return required_ports <= shifted_numeric_integers(row)
    if protocol in {1, 58}:
        icmp_values = (
            row.get("icmp.checksum", ""),
            row.get("icmp.seq_le", ""),
            row.get("icmp.transmit_timestamp", ""),
            row.get("icmp.unused", ""),
        )
        return packed_ip(row.get("ip.dst_host", "")) is not None or any(
            str(value or "").strip() not in {"", "0", "0.0"}
            for value in icmp_values
        )
    if protocol == 2:
        return ipaddress.ip_address(row["ip.src_host"].strip()).is_multicast
    return False


def family_label(fine_label: str, binary_label: int) -> str:
    if binary_label == 0:
        return "Benign"
    lowered = fine_label.lower()
    if "ddos" in lowered:
        return "DDoS"
    if any(token in lowered for token in ("scanning", "scanner", "fingerprint")):
        return "Reconnaissance"
    if "password" in lowered:
        return "Credential Attack"
    if any(token in lowered for token in ("sql", "xss", "upload")):
        return "Web Attack"
    if "mitm" in lowered:
        return "Man-in-the-Middle"
    if "backdoor" in lowered:
        return "Backdoor"
    if "ransomware" in lowered:
        return "Ransomware"
    return "Other Attack"


def paired_records(
    pcap: Path,
    packet_csv: Path,
    source_member: str,
    idle_seconds: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    idle_ns = int(idle_seconds * 1_000_000_000)
    counters: Counter[str] = Counter()
    active: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
    records: list[dict[str, Any]] = []

    def finalize(key: tuple[Any, ...], reason: str) -> None:
        state = active.pop(key)
        labels = state.pop("labels")
        if len(labels) != 1:
            counters["conflicting_flow_segments"] += 1
            raise ValueError(
                "official packet labels conflict within one flow segment: "
                f"{sorted(labels)}"
            )
        fine, family, binary = next(iter(labels))
        ordinal = counters["flow_segments"]
        counters["flow_segments"] += 1
        counters[f"flow_label::{family}::{fine}"] += 1
        counters[f"finalize::{reason}"] += 1
        records.append(
            {
                "record_id": hashlib.sha256(
                    (
                        f"{source_member}\0{ordinal}\0{state['start_ns']}\0"
                        f"{state['end_ns']}\0{state['protocol']}\0{fine}"
                    ).encode("utf-8")
                ).hexdigest(),
                "source_member": source_member,
                "src_ip": str(ipaddress.ip_address(state["endpoint_a"])),
                "src_port": state["port_a"],
                "dst_ip": str(ipaddress.ip_address(state["endpoint_b"])),
                "dst_port": state["port_b"],
                "protocol": state["protocol"],
                "start_ns": state["start_ns"],
                "end_ns": state["end_ns"],
                "fine_label": fine,
                "family_label": family,
                "binary_label": binary,
                "label_source": (
                    f"official Edge-IIoTset paired packet CSV::{packet_csv.name};"
                    "packet_order+endpoint+transport_port_verified;flow_consensus"
                ),
            }
        )

    def retain_paired_ip_row(
        row: dict[str, str],
        key: tuple[Any, ...],
        packet: Any,
        metadata: dict[str, Any],
        packet_number: int,
    ) -> None:
        protocol = int(metadata["protocol"])
        if protocol not in {6, 17}:
            counters["official_csv_non_tcp_udp_rows_consumed"] += 1
            counters[f"official_csv_non_tcp_udp_protocol::{protocol}"] += 1

        binary = integer_cell(row["Attack_label"])
        if binary not in {0, 1}:
            raise ValueError(
                f"packet {packet_number} has non-binary Attack_label={binary}"
            )
        fine = normalize_attack_type(row["Attack_type"])
        if binary == 0:
            fine = "Benign"
        family = family_label(fine, binary)
        label = (fine, family, binary)

        state = active.get(key)
        if state is not None and packet.timestamp_ns - state["end_ns"] > idle_ns:
            finalize(key, "idle_timeout")
            state = None
        if state is None:
            state = {
                "endpoint_a": metadata["endpoint_a"],
                "port_a": int(metadata["port_a"]),
                "endpoint_b": metadata["endpoint_b"],
                "port_b": int(metadata["port_b"]),
                "protocol": protocol,
                "start_ns": packet.timestamp_ns,
                "end_ns": packet.timestamp_ns,
                "labels": set(),
            }
            active[key] = state
        else:
            if packet.timestamp_ns < state["end_ns"]:
                counters["pcap_timestamp_regressions_within_flow"] += 1
            state["start_ns"] = min(state["start_ns"], packet.timestamp_ns)
            state["end_ns"] = max(state["end_ns"], packet.timestamp_ns)
            active.move_to_end(key)
        state["labels"].add(label)

    with packet_csv.open("r", encoding="utf-8-sig", newline="") as csv_handle:
        reader = csv.DictReader(csv_handle)
        required = {
            "frame.time",
            "ip.src_host",
            "ip.dst_host",
            "tcp.srcport",
            "tcp.dstport",
            "udp.port",
            "Attack_label",
            "Attack_type",
        }
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise ValueError(f"official packet CSV missing fields: {missing}")
        rows: Iterator[dict[str, str]] = iter(reader)
        try:
            pending_row: dict[str, str] | None = next(rows)
        except StopIteration as error:
            raise ValueError("official packet CSV contains no data rows") from error
        csv_layout = official_csv_layout(pending_row)
        clock_offset_ns: int | None = None
        day_ns = 86_400 * 1_000_000_000

        def consume_pending() -> None:
            nonlocal pending_row
            counters["official_csv_rows_consumed"] += 1
            try:
                pending_row = next(rows)
            except StopIteration:
                pending_row = None

        def consume_official_non_ip(reason: str, decoder_parsed: bool) -> None:
            assert pending_row is not None
            binary = integer_cell(pending_row["Attack_label"])
            if binary not in {0, 1}:
                raise ValueError(
                    f"official non-IP row has non-binary Attack_label={binary}"
                )
            fine = normalize_attack_type(pending_row["Attack_type"])
            if binary == 0:
                fine = "Benign"
            counters["official_csv_non_ip_rows_consumed"] += 1
            counters[f"official_csv_excluded_reason::{reason}"] += 1
            counters[f"official_csv_excluded_binary::{binary}"] += 1
            counters[f"official_csv_excluded_fine::{fine}"] += 1
            if decoder_parsed:
                counters["decoder_parsed_official_non_ip_packet_rows"] += 1
            consume_pending()

        def candidate_clock_offset(timestamp: Any) -> int:
            assert pending_row is not None
            official_clock_ns = frame_clock_ns(pending_row["frame.time"])
            pcap_clock_ns = int(Decimal(str(timestamp)) * 1_000_000_000) % day_ns
            offset_ns = (official_clock_ns - pcap_clock_ns) % day_ns
            if offset_ns > day_ns // 2:
                offset_ns -= day_ns
            return offset_ns

        with pcap.open("rb") as pcap_handle:
            for packet_number, (timestamp, frame) in enumerate(
                packet_reader(pcap_handle), start=1
            ):
                counters["pcap_packets"] += 1
                parsed = parse_packet(float(timestamp), bytes(frame))
                if csv_layout == "official_packet_order_only_mitm_v1":
                    if pending_row is None:
                        counters["pcap_unpaired_after_official_csv_end_packets"] += 1
                        continue
                    if parsed is None:
                        counters[
                            "official_csv_mitm_non_ip_rows_consumed"
                        ] += 1
                        consume_official_non_ip(
                            "official_mitm_non_ip_row_without_five_tuple", False
                        )
                        continue
                    key, packet, metadata = parsed
                    counters["pcap_parsed_ip_packets"] += 1
                    counters["paired_ip_packet_rows"] += 1
                    counters["official_csv_mitm_order_only_ip_rows_consumed"] += 1
                    row = pending_row
                    consume_pending()
                    retain_paired_ip_row(
                        row, key, packet, metadata, packet_number
                    )
                    continue
                if (
                    pending_row is not None
                    and csv_layout == "official_shifted_no_timestamp_ip_v1"
                ):
                    row_kind = shifted_row_kind(pending_row)
                    while row_kind == "unidentifiable_non_ip":
                        counters[
                            "official_csv_unidentifiable_non_ip_rows_consumed"
                        ] += 1
                        consume_official_non_ip(
                            "official_row_without_any_join_identity", False
                        )
                        if pending_row is None:
                            break
                        row_kind = shifted_row_kind(pending_row)
                    if pending_row is not None:
                        if row_kind == "arp":
                            if shifted_arp_matches(bytes(frame), pending_row):
                                counters[
                                    "official_csv_shifted_arp_rows_consumed"
                                ] += 1
                                consume_official_non_ip(
                                    "official_arp_row_without_ip_five_tuple",
                                    parsed is not None,
                                )
                                continue
                            counters[
                                "pcap_unpaired_before_pending_official_arp_row_packets"
                            ] += 1
                            continue
                        if row_kind != "ip":
                            raise ValueError(
                                "unsupported row inside shifted IP official CSV; "
                                f"official_rows_consumed={counters['official_csv_rows_consumed']}; "
                                f"row_head={dict(list(pending_row.items())[:12])}"
                            )
                if (
                    pending_row is not None
                    and csv_layout == "official_timestamped_packet_rows_v1"
                ):
                    source_text = pending_row["ip.src_host"].strip()
                    destination_text = pending_row["ip.dst_host"].strip()
                    csv_has_no_ip = (
                        source_text in MISSING_IP_VALUES
                        and destination_text in MISSING_IP_VALUES
                    )
                    if csv_has_no_ip:
                        candidate_offset_ns = candidate_clock_offset(timestamp)
                        time_matches = (
                            clock_offset_ns is None
                            or abs(candidate_offset_ns - clock_offset_ns) <= 1_000
                        )
                        if time_matches:
                            if clock_offset_ns is None:
                                clock_offset_ns = candidate_offset_ns
                            consume_official_non_ip(
                                "official_row_without_ip_five_tuple",
                                parsed is not None,
                            )
                            continue
                        counters[
                            "pcap_unpaired_before_pending_official_non_ip_row_packets"
                        ] += 1
                        continue
                if parsed is None:
                    counters["pcap_unpaired_non_ip_or_unparsed_packets"] += 1
                    continue
                key, packet, metadata = parsed
                counters["pcap_parsed_ip_packets"] += 1
                if pending_row is None:
                    counters["pcap_unpaired_after_official_csv_end_packets"] += 1
                    continue

                if csv_layout == "official_shifted_no_timestamp_ip_v1":
                    csv_source = packed_ip(pending_row["frame.time"])
                    csv_destination = packed_ip(pending_row["ip.src_host"])
                    if csv_source is None or csv_destination is None:
                        raise ValueError(
                            "shifted official row is missing a valid IP endpoint"
                        )
                else:
                    csv_source = packed_ip(pending_row["ip.src_host"])
                    csv_destination = packed_ip(pending_row["ip.dst_host"])
                    if csv_source is None or csv_destination is None:
                        raise ValueError(
                            "timestamped official row has exactly one invalid IP endpoint"
                        )
                identity_matches = {csv_source, csv_destination} == {
                    metadata["endpoint_a"],
                    metadata["endpoint_b"],
                }
                protocol = int(metadata["protocol"])
                if (
                    identity_matches
                    and csv_layout == "official_shifted_no_timestamp_ip_v1"
                ):
                    identity_matches = shifted_ip_protocol_matches(
                        pending_row,
                        protocol,
                        int(metadata["port_a"]),
                        int(metadata["port_b"]),
                    )
                elif identity_matches and protocol == 6:
                    csv_ports = {
                        integer_cell(pending_row["tcp.srcport"]),
                        integer_cell(pending_row["tcp.dstport"]),
                    }
                    identity_matches = csv_ports == {
                        metadata["port_a"],
                        metadata["port_b"],
                    }
                if csv_layout == "official_shifted_no_timestamp_ip_v1":
                    candidate_offset_ns = None
                    time_matches = True
                else:
                    candidate_offset_ns = candidate_clock_offset(timestamp)
                    time_matches = (
                        clock_offset_ns is None
                        or abs(candidate_offset_ns - clock_offset_ns) <= 1_000
                    )
                if not identity_matches or not time_matches:
                    counters["pcap_unpaired_ip_identity_or_time_packets"] += 1
                    counters[
                        f"pcap_unpaired_ip_identity_or_time_protocol::{protocol}"
                    ] += 1
                    continue
                if clock_offset_ns is None and candidate_offset_ns is not None:
                    clock_offset_ns = candidate_offset_ns
                counters["paired_ip_packet_rows"] += 1
                if csv_layout == "official_shifted_no_timestamp_ip_v1":
                    protocol_kind = {
                        1: "icmp_ip",
                        2: "igmp_ip",
                        6: "tcp_ip",
                        17: "udp_ip",
                        58: "icmpv6_ip",
                    }.get(protocol, f"protocol_{protocol}_ip")
                    counters[
                        f"official_csv_shifted_no_timestamp_{protocol_kind}_rows_consumed"
                    ] += 1
                row = pending_row
                consume_pending()
                retain_paired_ip_row(row, key, packet, metadata, packet_number)

        if pending_row is not None:
            counters["official_csv_rows_missing_from_pcap"] += 1
            for _ in rows:
                counters["official_csv_rows_missing_from_pcap"] += 1
            raise ValueError(
                "official packet CSV rows remain after the final PCAP packet: "
                f"{counters['official_csv_rows_missing_from_pcap']}"
            )

    for key in list(active):
        finalize(key, "pcap_end")
    if counters["official_csv_rows_consumed"] == 0:
        raise ValueError("paired capture consumed no official packet CSV rows")
    official_rows = counters["official_csv_rows_consumed"]
    excluded_official_rows = counters["official_csv_non_ip_rows_consumed"]
    retained_official_rows = counters["paired_ip_packet_rows"]
    exclusion_reasons = {
        key.removeprefix("official_csv_excluded_reason::"): value
        for key, value in sorted(counters.items())
        if key.startswith("official_csv_excluded_reason::")
    }
    packet_order_cardinality_passed = (
        csv_layout != "official_packet_order_only_mitm_v1"
        or counters["pcap_packets"] == official_rows
    )
    if csv_layout == "official_packet_order_only_mitm_v1":
        identity_policy = (
            "official MITM CSV and PCAP have exact equal cardinality and pair by "
            "one-to-one packet ordinal; flow identity and time come only from PCAP"
        )
    elif csv_layout == "official_shifted_no_timestamp_ip_v1":
        identity_policy = (
            "official CSV is an order-preserving filtered subsequence of the PCAP; "
            "the verified shifted layout maps frame.time to source IP and "
            "ip.src_host to destination IP; PCAP protocol is exact and every "
            "nonzero TCP/UDP port must occur in the official row; flow time bounds "
            "come from the paired PCAP"
        )
    else:
        identity_policy = (
            "official CSV is an order-preserving filtered subsequence of the PCAP; "
            "bidirectional IP endpoints, frame clock, and TCP ports are exact; flow "
            "time bounds come from the paired PCAP"
        )
    audit = {
        "schema_version": "caeos_edge_iiotset_paired_packet_label_index_audit_v2",
        "dataset_id": DATASET_ID,
        "pcap": str(pcap),
        "packet_csv": str(packet_csv),
        "source_member": source_member,
        "join_mode": "paired_capture_packet_csv_then_flow_consensus",
        "official_csv_layout": csv_layout,
        "identity_policy": identity_policy,
        "packet_order_cardinality_passed": packet_order_cardinality_passed,
        "official_frame_clock_offset_from_pcap_ns": clock_offset_ns,
        "official_row_exclusion_summary": {
            "total_official_rows": official_rows,
            "retained_ip_packet_rows": retained_official_rows,
            "excluded_rows": excluded_official_rows,
            "excluded_fraction": (
                excluded_official_rows / official_rows if official_rows else 0.0
            ),
            "reason_counts": exclusion_reasons,
            "rule": (
                "exclude only an order- and identity-verified official non-IP/ARP "
                "packet row that cannot form an IP five-tuple; never synthesize an "
                "endpoint or transport port"
            ),
        },
        "label_policy": "Attack_label and Attack_type unanimous within each 30-second-idle flow segment",
        "idle_seconds": idle_seconds,
        "counters": dict(sorted(counters.items())),
        "pairing_passed": (
            counters["official_csv_rows_consumed"] > 0
            and official_rows == retained_official_rows + excluded_official_rows
            and packet_order_cardinality_passed
            and counters["official_csv_rows_missing_from_pcap"] == 0
            and counters["conflicting_flow_segments"] == 0
        ),
        "zero_retained_supported_ip_flows": len(records) == 0,
    }
    return records, audit


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(args: argparse.Namespace) -> dict[str, Any]:
    records, report = paired_records(
        args.pcap, args.packet_csv, args.source_member, args.idle_seconds
    )
    registry = {
        "dataset_id": DATASET_ID,
        "pcap_sha256": sha256_file(args.pcap),
        "packet_csv_sha256": sha256_file(args.packet_csv),
        "source_member": args.source_member,
        "idle_seconds": args.idle_seconds,
    }
    registry_sha256 = hashlib.sha256(
        json.dumps(registry, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    index = create_label_index(args.label_index, DATASET_ID, records, registry_sha256)
    report["registry"] = registry
    report["registry_sha256"] = registry_sha256
    report["label_index"] = index
    report["ready_for_pcap_coverage_dry_run"] = bool(report["pairing_passed"])
    atomic_json(args.audit_output, report)
    return report


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

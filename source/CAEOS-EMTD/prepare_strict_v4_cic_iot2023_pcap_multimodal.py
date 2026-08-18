from __future__ import annotations

import argparse
import hashlib
import json
import math
import socket
import struct
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Iterator

import numpy as np

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


PAYLOAD_TOKENS = 512
PACKET_COUNT = 16
SEQUENCE_FEATURES = 6
GRAPH_NODE_FEATURES = 5
PAD_TOKEN = 256

FINE_TO_FAMILY = {
    "Benign_Final": "Benign",
    "DDoS-ICMP_Flood": "DDoS",
    "DDoS-SYN_Flood": "DDoS",
    "DDoS-UDP_Flood": "DDoS",
    "DoS-SYN_Flood": "DoS",
    "DoS-TCP_Flood": "DoS",
    "DoS-UDP_Flood": "DoS",
    "Mirai-greeth_flood": "Mirai",
    "Mirai-greip_flood": "Mirai",
    "Mirai-udpplain": "Mirai",
}


def source_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path.resolve()),
        "size_bytes": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
    }


def pcap_prefix_hash(path: Path, byte_limit: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read(byte_limit))
    return digest.hexdigest()


def canonical_flow_key(
    source: bytes,
    destination: bytes,
    source_port: int,
    destination_port: int,
    protocol: int,
) -> tuple[tuple[bytes, int], tuple[bytes, int], int, float]:
    first = (source, int(source_port))
    second = (destination, int(destination_port))
    if first <= second:
        return first, second, int(protocol), 1.0
    return second, first, int(protocol), -1.0


def payload_entropy(payload: bytes) -> float:
    if not payload:
        return 0.0
    counts = np.bincount(
        np.frombuffer(payload, dtype=np.uint8), minlength=256
    )
    probabilities = counts[counts > 0].astype(np.float64) / len(payload)
    return float(
        -(probabilities * np.log2(probabilities)).sum() / 8.0
    )


@dataclass
class PacketRecord:
    timestamp: float
    frame_length: int
    direction: float
    protocol: int
    flags: int
    payload: bytes


@dataclass
class FlowState:
    key: tuple[tuple[bytes, int], tuple[bytes, int], int]
    packets: list[PacketRecord] = field(default_factory=list)
    first_timestamp: float = 0.0
    last_timestamp: float = 0.0

    def append(self, packet: PacketRecord) -> None:
        if not self.packets:
            self.first_timestamp = packet.timestamp
        self.packets.append(packet)
        self.last_timestamp = packet.timestamp


def packet_features(
    records: list[PacketRecord],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    payload_tokens = np.full(
        PAYLOAD_TOKENS, PAD_TOKEN, dtype=np.uint16
    )
    payload = b"".join(record.payload for record in records)
    used_payload = payload[:PAYLOAD_TOKENS]
    if used_payload:
        payload_tokens[: len(used_payload)] = np.frombuffer(
            used_payload, dtype=np.uint8
        )

    sequence = np.zeros(
        (PACKET_COUNT, SEQUENCE_FEATURES), dtype=np.float32
    )
    graph_nodes = np.zeros(
        (PACKET_COUNT, GRAPH_NODE_FEATURES), dtype=np.float32
    )
    adjacency = np.eye(PACKET_COUNT, dtype=np.float32)
    previous_timestamp = records[0].timestamp if records else 0.0
    for index, record in enumerate(records[:PACKET_COUNT]):
        interval = max(0.0, record.timestamp - previous_timestamp)
        previous_timestamp = record.timestamp
        length_feature = min(
            1.0, math.log1p(record.frame_length) / math.log1p(65535)
        )
        interval_feature = min(
            1.0, math.log1p(interval * 1000.0) / math.log1p(60000.0)
        )
        payload_feature = min(
            1.0, math.log1p(len(record.payload)) / math.log1p(1500)
        )
        protocol_feature = {
            6: 1.0,
            17: 0.5,
            1: -0.5,
            58: -0.5,
        }.get(record.protocol, 0.0)
        flags_feature = float(record.flags & 0x3F) / 63.0
        sequence[index] = (
            length_feature * record.direction,
            interval_feature,
            record.direction,
            protocol_feature,
            flags_feature,
            payload_feature,
        )
        graph_nodes[index] = (
            length_feature,
            interval_feature,
            record.direction,
            payload_entropy(record.payload),
            1.0,
        )
        if index:
            adjacency[index - 1, index] = 1.0
            adjacency[index, index - 1] = 1.0
            if records[index - 1].direction == record.direction:
                adjacency[index - 1, index] = 2.0
                adjacency[index, index - 1] = 2.0

    graph = np.concatenate(
        [graph_nodes.reshape(-1), adjacency.reshape(-1)]
    ).astype(np.float32)
    payload_quality = min(1.0, len(used_payload) / 128.0)
    packet_quality = min(1.0, len(records) / 8.0)
    edge_quality = min(1.0, max(0, len(records) - 1) / 7.0)
    quality = np.asarray(
        [payload_quality, packet_quality, edge_quality],
        dtype=np.float32,
    )
    return payload_tokens, sequence.reshape(-1), graph, quality


def parse_ip_packet(
    timestamp: float,
    frame: bytes,
) -> tuple[
    tuple[tuple[bytes, int], tuple[bytes, int], int],
    PacketRecord,
] | None:
    try:
        import dpkt
    except ImportError as exc:  # pragma: no cover - remote dependency gate
        raise RuntimeError("dpkt is required for PCAP extraction") from exc

    try:
        ethernet = dpkt.ethernet.Ethernet(frame)
        ip = ethernet.data
        if not isinstance(ip, (dpkt.ip.IP, dpkt.ip6.IP6)):
            cooked = dpkt.sll.SLL(frame)
            ip = cooked.data
        if isinstance(ip, dpkt.ip.IP):
            protocol = int(ip.p)
        elif isinstance(ip, dpkt.ip6.IP6):
            protocol = int(ip.nxt)
        else:
            return None
        transport = ip.data
        source_port = int(getattr(transport, "sport", 0))
        destination_port = int(getattr(transport, "dport", 0))
        first, second, protocol, direction = canonical_flow_key(
            bytes(ip.src),
            bytes(ip.dst),
            source_port,
            destination_port,
            protocol,
        )
        flags = int(getattr(transport, "flags", 0))
        body = getattr(transport, "data", b"")
        if not isinstance(body, (bytes, bytearray)):
            body = bytes(body)
        record = PacketRecord(
            timestamp=float(timestamp),
            frame_length=len(frame),
            direction=direction,
            protocol=protocol,
            flags=flags,
            payload=bytes(body),
        )
        return (first, second, protocol), record
    except (
        ValueError,
        TypeError,
        IndexError,
        struct.error,
        socket.error,
        dpkt.dpkt.UnpackError,
    ):
        return None


def iter_pcap(handle: BinaryIO) -> Iterator[tuple[float, bytes]]:
    try:
        import dpkt
    except ImportError as exc:  # pragma: no cover - remote dependency gate
        raise RuntimeError("dpkt is required for PCAP extraction") from exc
    try:
        reader: Iterable[tuple[float, bytes]] = dpkt.pcap.Reader(handle)
    except (ValueError, dpkt.dpkt.NeedData):
        handle.seek(0)
        reader = dpkt.pcapng.Reader(handle)
    yield from reader


def extract_pcap(
    path: Path,
    maximum_flows: int,
    maximum_active_multiplier: int = 4,
    idle_seconds: float = 30.0,
) -> tuple[list[tuple[np.ndarray, ...]], dict[str, Any]]:
    completed: list[tuple[np.ndarray, ...]] = []
    active: OrderedDict[
        tuple[tuple[bytes, int], tuple[bytes, int], int], FlowState
    ] = OrderedDict()
    packets_read = 0
    parse_failures = 0
    maximum_active = max(maximum_flows, maximum_flows * maximum_active_multiplier)

    def finalize(key: tuple[tuple[bytes, int], tuple[bytes, int], int]) -> None:
        state = active.pop(key)
        if state.packets:
            completed.append(packet_features(state.packets))

    with path.open("rb") as handle:
        for timestamp, frame in iter_pcap(handle):
            packets_read += 1
            parsed = parse_ip_packet(float(timestamp), bytes(frame))
            if parsed is None:
                parse_failures += 1
                continue
            key, record = parsed
            state = active.get(key)
            if state is None:
                state = FlowState(key=key)
                active[key] = state
            else:
                active.move_to_end(key)
            state.append(record)
            if len(state.packets) >= PACKET_COUNT:
                finalize(key)
            while len(active) > maximum_active:
                finalize(next(iter(active)))
            if packets_read % 2048 == 0 and active:
                expired = [
                    flow_key
                    for flow_key, flow_state in active.items()
                    if timestamp - flow_state.last_timestamp >= idle_seconds
                ]
                for flow_key in expired:
                    finalize(flow_key)
                    if len(completed) >= maximum_flows:
                        break
            if len(completed) >= maximum_flows:
                break

    while len(completed) < maximum_flows and active:
        finalize(next(iter(active)))
    completed = completed[:maximum_flows]
    return completed, {
        "packets_read": packets_read,
        "parse_failures": parse_failures,
        "flows_extracted": len(completed),
    }


def selected_pcaps(
    pcap_root: Path,
    maximum_captures_per_fine_class: int,
) -> list[tuple[str, str, Path]]:
    selected: list[tuple[str, str, Path]] = []
    for fine_label, family in sorted(FINE_TO_FAMILY.items()):
        paths = sorted((pcap_root / fine_label).glob("*.pcap*"))
        if len(paths) < 4:
            raise ValueError(
                f"{fine_label} has {len(paths)} PCAPs; at least four required"
            )
        for path in paths[:maximum_captures_per_fine_class]:
            selected.append((fine_label, family, path.resolve()))
    return selected


def build_cache(args: argparse.Namespace) -> dict[str, Any]:
    pcap_root = args.pcap_root.resolve()
    output = args.output.resolve()
    records: dict[str, list[np.ndarray]] = {
        "payload": [],
        "sequence": [],
        "graph": [],
        "quality": [],
    }
    fine_labels: list[str] = []
    families: list[str] = []
    capture_groups: list[str] = []
    source_records: list[dict[str, Any]] = []
    for fine_label, family, path in selected_pcaps(
        pcap_root, args.maximum_captures_per_fine_class
    ):
        flows, extraction = extract_pcap(path, args.maximum_flows_per_capture)
        if len(flows) < args.minimum_flows_per_capture:
            raise ValueError(
                f"{path} yielded {len(flows)} flows; "
                f"minimum is {args.minimum_flows_per_capture}"
            )
        capture_group = path.relative_to(pcap_root).as_posix()
        for payload, sequence, graph, quality in flows:
            records["payload"].append(payload)
            records["sequence"].append(sequence)
            records["graph"].append(graph)
            records["quality"].append(quality)
            fine_labels.append(fine_label)
            families.append(family)
            capture_groups.append(capture_group)
        source_record = source_stat(path)
        source_record.update(
            {
                "fine_label": fine_label,
                "family": family,
                "prefix_1mib_sha256": pcap_prefix_hash(path),
                **extraction,
            }
        )
        source_records.append(source_record)

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        payload=np.stack(records["payload"]),
        sequence=np.stack(records["sequence"]),
        graph=np.stack(records["graph"]),
        quality=np.stack(records["quality"]),
        fine_label=np.asarray(fine_labels),
        family=np.asarray(families),
        capture_group=np.asarray(capture_groups),
    )
    manifest: dict[str, Any] = {
        "schema_version": (
            "strict_v4_cic_iot2023_pcap_multimodal_cache_manifest_v1"
        ),
        "source_root": str(pcap_root),
        "cache_path": str(output),
        "cache_sha256": file_hash(output),
        "samples": len(families),
        "maximum_flows_per_capture": args.maximum_flows_per_capture,
        "minimum_flows_per_capture": args.minimum_flows_per_capture,
        "maximum_captures_per_fine_class": (
            args.maximum_captures_per_fine_class
        ),
        "fine_to_family": FINE_TO_FAMILY,
        "modalities": {
            "payload_semantics": {
                "shape": [PAYLOAD_TOKENS],
                "description": "transport payload byte tokens only",
                "network_addresses_and_ports_excluded": True,
            },
            "packet_behavior": {
                "shape": [PACKET_COUNT * SEQUENCE_FEATURES],
                "description": (
                    "ordered length, interval, direction, protocol, flags, "
                    "and payload-length sequence"
                ),
            },
            "packet_interaction_graph": {
                "shape": [
                    PACKET_COUNT * GRAPH_NODE_FEATURES
                    + PACKET_COUNT * PACKET_COUNT
                ],
                "description": (
                    "packet-node attributes and temporal/direction adjacency"
                ),
            },
        },
        "capture_group_binding": "relative_source_pcap_path",
        "source_files": source_records,
        "claim_boundary": {
            "cache_is_flow_derived_not_official_csv": True,
            "source_file_full_hash_not_computed": True,
            "source_prefix_hash_and_stat_bound": True,
            "unknown_family_not_selected_or_scored_during_cache_creation": True,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    atomic_json(manifest_path, manifest)
    return manifest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-flows-per-capture", type=int, default=256)
    parser.add_argument("--minimum-flows-per-capture", type=int, default=64)
    parser.add_argument(
        "--maximum-captures-per-fine-class", type=int, default=8
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.output.exists():
        raise ValueError(f"refusing to overwrite cache: {args.output}")
    manifest = build_cache(args)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

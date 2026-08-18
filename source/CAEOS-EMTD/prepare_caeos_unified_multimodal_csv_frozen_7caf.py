from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import ipaddress
import json
import math
import os
import shutil
import struct
import subprocess
import tarfile
import tempfile
import threading
import time
import zipfile
from collections import Counter, OrderedDict
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Iterator

from caeos_unified_dataset import atomic_json, canonical_json_hash, sha256_file
from caeos_label_alignment import LabelResolver


SCHEMA_VERSION = "caeos_unified_multimodal_csv_schema_v4"
ACTIVITY_IDLE_THRESHOLD_US = 5_000_000
LABEL_MAPPING_VERSION = "caeos_attack_taxonomy_v1"
ATTACK_CATEGORIES = {
    "Benign",
    "DDoS",
    "DoS",
    "Reconnaissance",
    "Brute_Force",
    "Spoofing_MITM",
    "Botnet_Malware",
    "DNS_Tunneling",
    "Web_Attack",
    "Other_Attack",
}
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"
PCAP_MAGICS = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
}
TSHARK_FIELDS = (
    "frame.time_epoch",
    "frame.len",
    "frame.protocols",
    "ip.version",
    "ip.src",
    "ip.dst",
    "ip.len",
    "ip.dsfield",
    "ip.flags.rb",
    "ip.flags.df",
    "ip.flags.mf",
    "ip.frag_offset",
    "ip.id",
    "ip.ttl",
    "ip.proto",
    "ipv6.src",
    "ipv6.dst",
    "ipv6.plen",
    "ipv6.tclass",
    "ipv6.hlim",
    "ipv6.nxt",
    "ipv6.fraghdr.offset",
    "ipv6.fraghdr.ident",
    "ipv6.fraghdr.nxt",
    "ipv6.fraghdr.more",
    "tcp.srcport",
    "tcp.dstport",
    "tcp.hdr_len",
    "tcp.seq_raw",
    "tcp.ack_raw",
    "tcp.flags",
    "tcp.window_size_value",
    "tcp.payload",
    "udp.srcport",
    "udp.dstport",
    "udp.length",
    "udp.payload",
    "icmp.type",
    "icmp.code",
    "icmpv6.type",
    "icmpv6.code",
    "data.data",
    "tls.record.content_type",
    "tls.record.version",
    "tls.record.length",
    "tls.handshake.type",
    "quic.version",
)

TSHARK_STATE_PREFERENCES = (
    "ip.defragment:FALSE",
    "ipv6.defragment:FALSE",
    "tcp.desegment_tcp_streams:FALSE",
)

CICIOT2023_FAMILIES = {
    "BenignTraffic": "Benign",
    "Backdoor_Malware": "Web",
    "BrowserHijacking": "Web",
    "CommandInjection": "Web",
    "DDoS-ACK_Fragmentation": "DDoS",
    "DDoS-HTTP_Flood": "DDoS",
    "DDoS-ICMP_Flood": "DDoS",
    "DDoS-ICMP_Fragmentation": "DDoS",
    "DDoS-PSHACK_Flood": "DDoS",
    "DDoS-RSTFINFlood": "DDoS",
    "DDoS-SlowLoris": "DDoS",
    "DDoS-SYN_Flood": "DDoS",
    "DDoS-SynonymousIP_Flood": "DDoS",
    "DDoS-TCP_Flood": "DDoS",
    "DDoS-UDP_Flood": "DDoS",
    "DDoS-UDP_Fragmentation": "DDoS",
    "DictionaryBruteForce": "BruteForce",
    "DNS_Spoofing": "Spoofing",
    "DoS-HTTP_Flood": "DoS",
    "DoS-SYN_Flood": "DoS",
    "DoS-TCP_Flood": "DoS",
    "DoS-UDP_Flood": "DoS",
    "Mirai-greeth_flood": "Mirai",
    "Mirai-greip_flood": "Mirai",
    "Mirai-udpplain": "Mirai",
    "MITM-ArpSpoofing": "Spoofing",
    "Recon-HostDiscovery": "Recon",
    "Recon-OSScan": "Recon",
    "Recon-PingSweep": "Recon",
    "Recon-PortScan": "Recon",
    "SqlInjection": "Web",
    "Uploading_Attack": "Web",
    "VulnerabilityScan": "Recon",
    "XSS": "Web",
}

EXPLICIT_FAMILY_ATTACK_CATEGORIES = {
    "benign": "Benign",
    "ddos": "DDoS",
    "dos": "DoS",
    "recon": "Reconnaissance",
    "reconnaissance": "Reconnaissance",
    "bruteforce": "Brute_Force",
    "brute_force": "Brute_Force",
    "spoofing": "Spoofing_MITM",
    "spoofing_mitm": "Spoofing_MITM",
    "mirai": "Botnet_Malware",
    "botnet": "Botnet_Malware",
    "malware": "Botnet_Malware",
    "web": "Web_Attack",
    "web_attack": "Web_Attack",
    "maliciousdoh": "DNS_Tunneling",
    "dns_tunneling": "DNS_Tunneling",
}


@dataclass
class PacketRecord:
    timestamp_ns: int
    frame_length: int
    direction: int
    protocol: int
    flags: int
    payload: bytes
    payload_length: int
    ttl: int
    window: int
    ip_length: int
    ip_dscp_ecn: int
    ip_flags: int
    fragment_offset: int
    ip_fragment_id: int
    transport_header_length: int
    tcp_sequence: int
    tcp_acknowledgement: int
    sanitized_l4_header: bytes
    sanitized_l4_length: int
    protocol_hint: str = "Other"
    tls_record_types: tuple[int, ...] = ()
    tls_record_versions: tuple[int, ...] = ()
    tls_record_lengths: tuple[int, ...] = ()
    tls_handshake_types: tuple[int, ...] = ()
    quic_versions: tuple[int, ...] = ()


@dataclass(frozen=True)
class IPv6Envelope:
    src: bytes
    dst: bytes
    protocol: int
    hop_limit: int
    payload_length: int
    traffic_class: int
    data: Any
    fragment_offset: int = 0
    fragment_id: int = 0
    more_fragments: bool = False


@dataclass
class FlowState:
    key_material: bytes
    ip_version: int
    protocol: int
    endpoint_a: bytes
    endpoint_b: bytes
    port_a: int
    port_b: int
    segment_index: int
    packets: list[PacketRecord] = field(default_factory=list)
    payload_prefix: bytearray = field(default_factory=bytearray)
    sanitized_l4_prefix: bytearray = field(default_factory=bytearray)
    payload_histogram: list[int] = field(default_factory=lambda: [0] * 256)

    def add_packet(
        self,
        packet: PacketRecord,
        payload_prefix_bytes: int,
        sanitized_l4_prefix_bytes: int,
        retain_packet_payload: bool = False,
    ) -> None:
        payload_remaining = max(0, payload_prefix_bytes - len(self.payload_prefix))
        if payload_remaining:
            self.payload_prefix.extend(packet.payload[:payload_remaining])
        sanitized_remaining = max(
            0, sanitized_l4_prefix_bytes - len(self.sanitized_l4_prefix)
        )
        if sanitized_remaining:
            header = packet.sanitized_l4_header[:sanitized_remaining]
            self.sanitized_l4_prefix.extend(header)
            sanitized_remaining -= len(header)
            if sanitized_remaining:
                self.sanitized_l4_prefix.extend(packet.payload[:sanitized_remaining])
        for value in packet.payload:
            self.payload_histogram[value] += 1
        if not retain_packet_payload:
            packet.payload = b""
            packet.sanitized_l4_header = b""
        self.packets.append(packet)

    @property
    def first_timestamp_ns(self) -> int:
        return self.packets[0].timestamp_ns

    @property
    def last_timestamp_ns(self) -> int:
        return self.packets[-1].timestamp_ns


@dataclass(frozen=True)
class LabelRecord:
    status: str
    fine_label: str
    family_label: str
    binary_label: int

    @property
    def traffic_class(self) -> str:
        if self.binary_label == 0:
            return "Benign"
        if self.binary_label == 1:
            return "Malicious"
        return "Pending"

    @property
    def attack_category(self) -> str:
        if self.binary_label == 0:
            return "Benign"
        if self.binary_label != 1:
            return "Pending"
        normalized_family = normalized_label(self.family_label).lower()
        explicit = EXPLICIT_FAMILY_ATTACK_CATEGORIES.get(normalized_family)
        if explicit is not None:
            return explicit
        value = f"{self.family_label} {self.fine_label}".lower()
        if "ddos" in value:
            return "DDoS"
        if "dos" in value:
            return "DoS"
        if any(token in value for token in ("recon", "scan", "fingerprint")):
            return "Reconnaissance"
        if any(token in value for token in ("brute", "password", "dictionary")):
            return "Brute_Force"
        if any(token in value for token in ("spoof", "mitm")):
            return "Spoofing_MITM"
        if any(
            token in value
            for token in ("mirai", "botnet", "backdoor", "malware", "hijack")
        ):
            return "Botnet_Malware"
        if any(
            token in value
            for token in ("dns2tcp", "dnscat", "iodine", "maliciousdoh", "dns_tunnel")
        ):
            return "DNS_Tunneling"
        if any(token in value for token in ("sql", "xss", "injection", "upload", "web")):
            return "Web_Attack"
        return "Other_Attack"

    @property
    def attack_subcategory(self) -> str:
        return self.fine_label or "Pending"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_source_manifest(
    catalog: dict[str, Any], source_manifest: dict[str, Any]
) -> None:
    if not source_manifest.get("full_source_hashes_computed"):
        raise ValueError("full source SHA-256 manifest is required")
    if source_manifest.get("catalog_sha256") != canonical_json_hash(catalog):
        raise ValueError("source manifest catalog hash mismatch")
    catalog_by_id = {item["id"]: item for item in catalog["datasets"]}
    source_by_id = {item["id"]: item for item in source_manifest["datasets"]}
    if set(catalog_by_id) != set(source_by_id):
        raise ValueError("source manifest dataset set mismatch")
    for dataset_id, source_dataset in source_by_id.items():
        catalog_dataset = catalog_by_id[dataset_id]
        for field in (
            "source_root",
            "source_kind",
            "label_policy",
            "label_binding",
        ):
            if str(source_dataset[field]) != str(catalog_dataset[field]):
                raise ValueError(
                    f"source manifest {field} mismatch for {dataset_id}"
                )


def sequence(values: Iterable[int]) -> str:
    return ";".join(str(int(value)) for value in values)


def normalized_label(value: str) -> str:
    return "_".join(value.strip().replace("-", "_").split()).strip("_")


def ciciot2022_path_label(parts: tuple[str, ...]) -> LabelRecord:
    lowered_parts = tuple(part.lower() for part in parts)
    if any(
        part.startswith(("1-power", "2-idle", "3-interactions", "4-scenarios", "5-active"))
        for part in lowered_parts
    ):
        return LabelRecord("capture_path", "Benign", "Benign", 0)
    attack_index = next(
        (index for index, part in enumerate(lowered_parts) if part.startswith("6-attacks")),
        None,
    )
    if attack_index is None or attack_index + 1 >= len(parts):
        return LabelRecord("capture_path_unresolved", "", "", -1)

    category = parts[attack_index + 1]
    family = category.split("-", 1)[-1].strip()
    if family.lower() == "flood" and len(parts) >= attack_index + 4:
        fine = f"Flood-{parts[attack_index + 3]}"
    elif family.lower() == "rtsp brute force" and len(parts) >= attack_index + 3:
        fine = f"RTSP Brute Force-{parts[attack_index + 2]}"
    else:
        return LabelRecord("capture_path_unresolved", "", "", -1)
    return LabelRecord("capture_path", fine, family, 1)


def path_label(dataset: dict[str, Any], source_member: str) -> LabelRecord:
    policy = dataset["label_policy"]
    parts = Path(source_member).parts
    lowered = source_member.lower()
    if policy in {"deferred_flow_csv_join", "deferred_ground_truth_join"}:
        return LabelRecord("deferred_label_join", "", "", -1)
    if policy == "all_benign_application_capture":
        return LabelRecord("capture_path", "Benign", "Benign", 0)
    if policy == "relative_attack_directory":
        fine = parts[0] if len(parts) > 1 else Path(source_member).stem
        if fine == "Benign_Final":
            fine = "BenignTraffic"
        family = CICIOT2023_FAMILIES.get(fine, "Unmapped")
        binary = 0 if family == "Benign" else 1
        status = "capture_path" if family != "Unmapped" else "unmapped_path"
        return LabelRecord(status, fine, family, binary if family != "Unmapped" else -1)
    if policy == "bot_iot_attack_directory":
        family = normalized_label(parts[0]) if parts else "Unmapped"
        fine = normalized_label(parts[1]) if len(parts) > 2 else family
        binary = 0 if family.lower() in {"benign", "normal"} else 1
        return LabelRecord("capture_path", fine, family, binary)
    if policy == "edge_capture_name":
        if "normal traffic" in lowered:
            return LabelRecord("capture_path", "Benign", "Benign", 0)
        fine = normalized_label(Path(source_member).stem.replace("Attack", ""))
        family = "DDoS" if "ddos" in lowered else "Attack"
        return LabelRecord("capture_path_pending_csv_crosscheck", fine, family, 1)
    if policy == "relative_capture_taxonomy":
        return ciciot2022_path_label(parts)
    if policy == "archive_member_attack_name":
        fine = normalized_label(parts[-2] if len(parts) > 1 else Path(source_member).stem)
        return LabelRecord("archive_member_path_pending_csv_crosscheck", fine, "DDoS", 1)
    if policy == "doh_archive_taxonomy":
        malicious = "malicious" in lowered
        fine = normalized_label(parts[-2] if len(parts) > 1 else Path(source_member).stem)
        return LabelRecord(
            "archive_member_path", fine, "MaliciousDoH" if malicious else "Benign", 1 if malicious else 0
        )
    if policy in {"tor_domain_and_application", "vpn_domain_and_application"}:
        fine = normalized_label(parts[-2] if len(parts) > 1 else Path(source_member).stem)
        family = "Tor" if "tor" in lowered and "nontor" not in lowered else "NonTor"
        if policy == "vpn_domain_and_application":
            family = "VPN" if "vpn" in lowered and "nonvpn" not in lowered else "NonVPN"
        return LabelRecord("archive_member_domain_label", fine, family, 0)
    return LabelRecord("unmapped_policy", "", "", -1)


def canonical_flow(
    source_ip: bytes,
    destination_ip: bytes,
    source_port: int,
    destination_port: int,
    protocol: int,
) -> tuple[tuple[bytes, int], tuple[bytes, int], int, int]:
    source = (source_ip, source_port)
    destination = (destination_ip, destination_port)
    if source <= destination:
        return source, destination, protocol, 1
    return destination, source, protocol, -1


def decode_ipv6_transport(protocol: int, payload: bytes, fragment_offset: int) -> Any:
    import dpkt

    if fragment_offset:
        return payload
    decoder = {
        dpkt.ip.IP_PROTO_TCP: dpkt.tcp.TCP,
        dpkt.ip.IP_PROTO_UDP: dpkt.udp.UDP,
        dpkt.ip.IP_PROTO_ICMP6: dpkt.icmp6.ICMP6,
    }.get(protocol)
    if decoder is None:
        return payload
    try:
        return decoder(payload)
    except (ValueError, dpkt.dpkt.UnpackError):
        return payload


def decode_ipv6_fallback(packet: bytes) -> IPv6Envelope | None:
    """Decode IPv6 extension chains that trigger dpkt 1.9.8 issue #575."""
    if len(packet) < 40 or packet[0] >> 4 != 6:
        return None
    first_word, payload_length, next_header, hop_limit = struct.unpack(
        "!IHBB", packet[:8]
    )
    available = packet[40:]
    payload = available[:payload_length] if payload_length else available
    fragment_offset = 0
    fragment_id = 0
    more_fragments = False
    option_headers = {0, 43, 60}
    for _ in range(16):
        if next_header in option_headers:
            if len(payload) < 2:
                return None
            extension_length = (payload[1] + 1) * 8
        elif next_header == 44:
            if len(payload) < 8:
                return None
            extension_length = 8
            fragment_bits = int.from_bytes(payload[2:4], "big")
            fragment_offset = ((fragment_bits >> 3) & 0x1FFF) * 8
            more_fragments = bool(fragment_bits & 1)
            fragment_id = int.from_bytes(payload[4:8], "big")
        elif next_header == 51:
            if len(payload) < 2:
                return None
            extension_length = (payload[1] + 2) * 4
        else:
            break
        if extension_length > len(payload):
            return None
        next_header = payload[0]
        payload = payload[extension_length:]
    else:
        return None
    traffic_class = (first_word >> 20) & 0xFF
    return IPv6Envelope(
        src=packet[8:24],
        dst=packet[24:40],
        protocol=int(next_header),
        hop_limit=int(hop_limit),
        payload_length=int(payload_length),
        traffic_class=traffic_class,
        data=decode_ipv6_transport(int(next_header), payload, fragment_offset),
        fragment_offset=fragment_offset,
        fragment_id=fragment_id,
        more_fragments=more_fragments,
    )


def ipv6_payload_candidates(frame: bytes) -> Iterator[bytes]:
    if frame and frame[0] >> 4 == 6:
        yield frame
    if len(frame) >= 14:
        offset = 14
        ether_type = int.from_bytes(frame[12:14], "big")
        while ether_type in {0x8100, 0x88A8, 0x9100} and len(frame) >= offset + 4:
            ether_type = int.from_bytes(frame[offset + 2 : offset + 4], "big")
            offset += 4
        if ether_type == 0x86DD and len(frame) > offset:
            yield frame[offset:]
    if len(frame) >= 17 and int.from_bytes(frame[14:16], "big") == 0x86DD:
        yield frame[16:]
    if len(frame) >= 5 and frame[4] >> 4 == 6:
        yield frame[4:]


def ipv6_envelope_from_dpkt(ip: Any) -> IPv6Envelope:
    import dpkt

    fragment = getattr(ip, "extension_hdrs", {}).get(44)
    fragment_offset = int(getattr(fragment, "frag_off", 0)) * 8
    return IPv6Envelope(
        src=bytes(ip.src),
        dst=bytes(ip.dst),
        protocol=int(getattr(ip, "p", ip.nxt)),
        hop_limit=int(ip.hlim),
        payload_length=int(ip.plen),
        traffic_class=(int(ip.fc) << 4 | (int(ip.flow) >> 16)) & 0xFF,
        data=ip.data,
        fragment_offset=fragment_offset,
        fragment_id=int(getattr(fragment, "id", 0)),
        more_fragments=bool(getattr(fragment, "m_flag", 0)),
    )


def looks_like_linux_sll(frame: bytes) -> bool:
    if len(frame) < 16:
        return False
    packet_type = int.from_bytes(frame[0:2], "big")
    hardware_address_length = int.from_bytes(frame[4:6], "big")
    ether_type = int.from_bytes(frame[14:16], "big")
    return (
        packet_type <= 4
        and hardware_address_length <= 8
        and ether_type in {0x0800, 0x0806, 0x86DD}
    )


def unwrap_ip(frame: bytes) -> Any | None:
    import dpkt

    candidates: list[Any] = []
    if looks_like_linux_sll(frame):
        try:
            value = dpkt.sll.SLL(frame).data
            if isinstance(value, dpkt.ip.IP):
                return value
            if isinstance(value, dpkt.ip6.IP6):
                return ipv6_envelope_from_dpkt(value)
        except (ValueError, dpkt.dpkt.UnpackError, AttributeError):
            pass
    try:
        candidates.append(dpkt.ethernet.Ethernet(frame).data)
    except (ValueError, dpkt.dpkt.UnpackError, AttributeError):
        pass
    if not looks_like_linux_sll(frame):
        try:
            candidates.append(dpkt.sll.SLL(frame).data)
        except (ValueError, dpkt.dpkt.UnpackError, AttributeError):
            pass
    try:
        candidates.append(dpkt.loopback.Loopback(frame).data)
    except (ValueError, dpkt.dpkt.UnpackError, AttributeError):
        pass
    if frame:
        version = frame[0] >> 4
        try:
            if version == 4:
                candidates.append(dpkt.ip.IP(frame))
            elif version == 6:
                candidates.append(dpkt.ip6.IP6(frame))
        except (ValueError, dpkt.dpkt.UnpackError, AttributeError):
            pass
    for candidate in candidates:
        value = candidate
        while isinstance(value, dpkt.ethernet.VLANtag8021Q):
            value = value.data
        if isinstance(value, dpkt.ip.IP):
            return value
        if isinstance(value, dpkt.ip6.IP6):
            return ipv6_envelope_from_dpkt(value)
    for packet in ipv6_payload_candidates(frame):
        decoded = decode_ipv6_fallback(packet)
        if decoded is not None:
            return decoded
    return None


def parse_packet(timestamp: float, frame: bytes) -> tuple[tuple[Any, ...], PacketRecord, dict[str, Any]] | None:
    import dpkt

    try:
        ip = unwrap_ip(frame)
        if ip is None:
            return None
        if isinstance(ip, dpkt.ip.IP):
            ip_version = 4
            protocol = int(ip.p)
            ttl = int(ip.ttl)
            ip_length = int(ip.len) if int(ip.len) > 0 else len(bytes(ip))
            ip_dscp_ecn = int(ip.tos) & 0xFF
            ipv4_flags_offset = int.from_bytes(bytes(ip)[6:8], "big")
            ip_flags = (ipv4_flags_offset >> 13) & 0x07
            # dpkt exposes the RFC 791 offset in 8-byte units; the frozen CSV
            # contract stores the actual byte displacement used by TShark.
            fragment_offset = (ipv4_flags_offset & dpkt.ip.IP_OFFMASK) * 8
            ip_fragment_id = int(ip.id) & 0xFFFF
        else:
            ip_version = 6
            protocol = int(ip.protocol)
            ttl = int(ip.hop_limit)
            ip_length = 40 + int(ip.payload_length)
            ip_dscp_ecn = int(ip.traffic_class) & 0xFF
            ip_flags = 1 if ip.more_fragments else 0
            fragment_offset = int(ip.fragment_offset)
            ip_fragment_id = int(ip.fragment_id)
        transport = ip.data
        is_ip_fragment = bool(fragment_offset or (ip_flags & 1))
        is_noninitial_ip_fragment = fragment_offset > 0
        transport_flags = int(getattr(transport, "flags", 0)) & 0xFF
        transport_window = max(
            0, min(int(getattr(transport, "win", 0)), 65535)
        )
        source_port = 0 if is_ip_fragment else int(getattr(transport, "sport", 0))
        destination_port = (
            0 if is_ip_fragment else int(getattr(transport, "dport", 0))
        )
        endpoint_a, endpoint_b, protocol, direction = canonical_flow(
            bytes(ip.src), bytes(ip.dst), source_port, destination_port, protocol
        )
        if is_noninitial_ip_fragment:
            # A non-initial fragment has no L4 header. Its entire IP body is
            # continuation payload and must not be discarded as a fake header.
            body = bytes(transport)
            transport_bytes = bytearray()
            transport_header_length = 0
            tcp_sequence = 0
            tcp_acknowledgement = 0
            transport_flags = 0
            transport_window = 0
        elif is_ip_fragment:
            # Parse only the header bytes present in the first fragment. dpkt
            # may intentionally leave fragmented transports as raw bytes.
            transport_bytes = bytearray(bytes(transport))
            tcp_sequence = 0
            tcp_acknowledgement = 0
            if protocol == 6 and len(transport_bytes) >= 20:
                transport_header_length = max(20, (transport_bytes[12] >> 4) * 4)
                transport_header_length = min(transport_header_length, len(transport_bytes))
                tcp_sequence = int.from_bytes(transport_bytes[4:8], "big")
                tcp_acknowledgement = int.from_bytes(transport_bytes[8:12], "big")
                transport_flags = transport_bytes[13]
                transport_window = int.from_bytes(transport_bytes[14:16], "big")
                transport_bytes[16:18] = b"\0\0"
            elif protocol == 17 and len(transport_bytes) >= 8:
                transport_header_length = 8
                transport_bytes[6:8] = b"\0\0"
            elif protocol in {1, 58} and len(transport_bytes) >= 4:
                transport_header_length = 4
                transport_bytes[2:4] = b"\0\0"
            else:
                transport_header_length = 0
            body = bytes(transport)[transport_header_length:]
        else:
            body = getattr(transport, "data", b"")
            if not isinstance(body, (bytes, bytearray)):
                body = bytes(body)
            transport_bytes = bytearray(bytes(transport))
        if not is_ip_fragment and isinstance(transport, dpkt.tcp.TCP):
            transport_header_length = max(20, int(transport.off) * 4)
            tcp_sequence = int(transport.seq) & 0xFFFFFFFF
            tcp_acknowledgement = int(transport.ack) & 0xFFFFFFFF
            if len(transport_bytes) >= 18:
                transport_bytes[16:18] = b"\0\0"
        elif not is_ip_fragment and isinstance(transport, dpkt.udp.UDP):
            transport_header_length = 8
            tcp_sequence = 0
            tcp_acknowledgement = 0
            if len(transport_bytes) >= 8:
                transport_bytes[6:8] = b"\0\0"
        elif not is_ip_fragment:
            transport_header_length = max(0, len(transport_bytes) - len(body))
            tcp_sequence = 0
            tcp_acknowledgement = 0
            if protocol in {1, 58} and len(transport_bytes) >= 4:
                transport_bytes[2:4] = b"\0\0"
        key = (endpoint_a, endpoint_b, protocol)
        key_material = (
            endpoint_a[0]
            + endpoint_a[1].to_bytes(2, "big")
            + endpoint_b[0]
            + endpoint_b[1].to_bytes(2, "big")
            + protocol.to_bytes(1, "big")
        )
        record = PacketRecord(
            timestamp_ns=int(round(float(timestamp) * 1_000_000_000)),
            frame_length=min(len(frame), 65535),
            direction=direction,
            protocol=protocol,
            flags=transport_flags,
            payload=bytes(body),
            payload_length=len(body),
            ttl=max(0, min(ttl, 255)),
            window=transport_window,
            ip_length=max(0, min(ip_length, 65535)),
            ip_dscp_ecn=ip_dscp_ecn,
            ip_flags=ip_flags,
            fragment_offset=max(0, min(fragment_offset, 65535)),
            ip_fragment_id=ip_fragment_id,
            transport_header_length=max(0, min(transport_header_length, 255)),
            tcp_sequence=tcp_sequence,
            tcp_acknowledgement=tcp_acknowledgement,
            sanitized_l4_header=bytes(transport_bytes[:transport_header_length]),
            sanitized_l4_length=transport_header_length + len(body),
        )
        metadata = {
            "key_material": key_material,
            "ip_version": ip_version,
            "protocol": protocol,
            "endpoint_a": endpoint_a[0],
            "endpoint_b": endpoint_b[0],
            "port_a": endpoint_a[1],
            "port_b": endpoint_b[1],
        }
        return key, record, metadata
    except (ValueError, TypeError, IndexError, dpkt.dpkt.UnpackError):
        return None


def first_tshark_value(value: str) -> str:
    return value.split(";", 1)[0] if value else ""


def tshark_integer(value: str, default: int = 0) -> int:
    selected = first_tshark_value(value).strip()
    if not selected:
        return default
    try:
        return int(selected, 0)
    except ValueError:
        return int(selected, 10)


def tshark_integer_sequence(value: str) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(tshark_integer(item) for item in value.split(";") if item)


def tshark_boolean(value: str) -> bool:
    return first_tshark_value(value).strip().lower() in {"1", "true", "yes", "set"}


def tshark_hex_bytes(value: str) -> bytes:
    selected = first_tshark_value(value).replace(":", "").strip()
    if not selected:
        return b""
    return bytes.fromhex(selected)


def canonical_l4_header(
    protocol: int,
    source_port: int,
    destination_port: int,
    header_length: int,
    tcp_sequence: int,
    tcp_acknowledgement: int,
    flags: int,
    window: int,
    udp_length: int,
    icmp_type: int,
    icmp_code: int,
) -> bytes:
    if protocol == 6 and header_length >= 20:
        data_offset = min(max(header_length // 4, 5), 15)
        data_offset_and_ns = (data_offset << 4) | ((flags >> 8) & 0x01)
        header = struct.pack(
            "!HHIIBBHHH",
            source_port,
            destination_port,
            tcp_sequence,
            tcp_acknowledgement,
            data_offset_and_ns,
            flags & 0xFF,
            window,
            0,
            0,
        )
        return header + bytes(max(0, header_length - len(header)))
    if protocol == 17 and header_length >= 8:
        return struct.pack(
            "!HHHH",
            source_port,
            destination_port,
            min(65535, max(8, udp_length)),
            0,
        )
    if protocol in {1, 58} and header_length >= 4:
        return struct.pack("!BBH", icmp_type, icmp_code, 0)
    return b""


def parse_tshark_fields(values: list[str]) -> tuple[tuple[Any, ...], PacketRecord, dict[str, Any]] | None:
    if len(values) != len(TSHARK_FIELDS):
        raise ValueError(
            f"tshark field count {len(values)} != expected {len(TSHARK_FIELDS)}"
        )
    item = dict(zip(TSHARK_FIELDS, values))
    source_text = first_tshark_value(item["ip.src"]) or first_tshark_value(
        item["ipv6.src"]
    )
    destination_text = first_tshark_value(item["ip.dst"]) or first_tshark_value(
        item["ipv6.dst"]
    )
    if not source_text or not destination_text:
        return None
    source_ip = ipaddress.ip_address(source_text).packed
    destination_ip = ipaddress.ip_address(destination_text).packed
    ip_version = 4 if item["ip.src"] else 6
    if ip_version == 4:
        protocol = tshark_integer(item["ip.proto"])
        ip_length = tshark_integer(item["ip.len"])
        ip_dscp_ecn = tshark_integer(item["ip.dsfield"])
        ip_flags = (
            (4 if tshark_boolean(item["ip.flags.rb"]) else 0)
            | (2 if tshark_boolean(item["ip.flags.df"]) else 0)
            | (1 if tshark_boolean(item["ip.flags.mf"]) else 0)
        )
        fragment_offset = tshark_integer(item["ip.frag_offset"])
        fragment_id = tshark_integer(item["ip.id"])
        ttl = tshark_integer(item["ip.ttl"])
    else:
        protocol = tshark_integer(item["ipv6.fraghdr.nxt"]) or tshark_integer(
            item["ipv6.nxt"]
        )
        ip_length = 40 + tshark_integer(item["ipv6.plen"])
        ip_dscp_ecn = tshark_integer(item["ipv6.tclass"])
        ip_flags = 1 if tshark_boolean(item["ipv6.fraghdr.more"]) else 0
        fragment_offset = tshark_integer(item["ipv6.fraghdr.offset"])
        fragment_id = tshark_integer(item["ipv6.fraghdr.ident"])
        ttl = tshark_integer(item["ipv6.hlim"])

    is_fragment = bool(fragment_offset or (ip_flags & 1))
    is_noninitial_fragment = fragment_offset > 0
    tcp_source = tshark_integer(item["tcp.srcport"])
    tcp_destination = tshark_integer(item["tcp.dstport"])
    udp_source = tshark_integer(item["udp.srcport"])
    udp_destination = tshark_integer(item["udp.dstport"])
    if is_fragment:
        source_port = 0
        destination_port = 0
    elif protocol == 6:
        source_port, destination_port = tcp_source, tcp_destination
    elif protocol == 17:
        source_port, destination_port = udp_source, udp_destination
    else:
        source_port = destination_port = 0

    if is_noninitial_fragment:
        payload = tshark_hex_bytes(item["data.data"])
        transport_header_length = 0
    elif protocol == 6:
        payload = tshark_hex_bytes(item["tcp.payload"])
        transport_header_length = tshark_integer(item["tcp.hdr_len"])
    elif protocol == 17:
        payload = tshark_hex_bytes(item["udp.payload"])
        transport_header_length = 8 if item["udp.length"] else 0
    else:
        payload = tshark_hex_bytes(item["data.data"])
        transport_header_length = 4 if protocol in {1, 58} else 0

    tcp_sequence = tshark_integer(item["tcp.seq_raw"])
    tcp_acknowledgement = tshark_integer(item["tcp.ack_raw"])
    flags = tshark_integer(item["tcp.flags"])
    window = tshark_integer(item["tcp.window_size_value"])
    sanitized_l4_header = canonical_l4_header(
        protocol,
        source_port,
        destination_port,
        transport_header_length,
        tcp_sequence,
        tcp_acknowledgement,
        flags,
        window,
        tshark_integer(item["udp.length"]),
        tshark_integer(item["icmp.type"] or item["icmpv6.type"]),
        tshark_integer(item["icmp.code"] or item["icmpv6.code"]),
    )
    endpoint_a, endpoint_b, protocol, direction = canonical_flow(
        source_ip, destination_ip, source_port, destination_port, protocol
    )
    protocols = first_tshark_value(item["frame.protocols"]).lower().split(":")
    protocol_hint = "Other"
    if "quic" in protocols:
        protocol_hint = "QUIC"
    elif "tls" in protocols or "ssl" in protocols:
        protocol_hint = "TLS"
    timestamp_ns = int(Decimal(first_tshark_value(item["frame.time_epoch"])) * 1_000_000_000)
    record = PacketRecord(
        timestamp_ns=timestamp_ns,
        frame_length=min(tshark_integer(item["frame.len"]), 65535),
        direction=direction,
        protocol=protocol,
        flags=flags & 0xFF,
        payload=payload,
        payload_length=len(payload),
        ttl=max(0, min(ttl, 255)),
        window=max(0, min(window, 65535)),
        ip_length=max(0, min(ip_length, 65535)),
        ip_dscp_ecn=ip_dscp_ecn & 0xFF,
        ip_flags=ip_flags,
        fragment_offset=max(0, min(fragment_offset, 65535)),
        ip_fragment_id=max(0, min(fragment_id, 4_294_967_295)),
        transport_header_length=max(0, min(transport_header_length, 255)),
        tcp_sequence=tcp_sequence & 0xFFFFFFFF,
        tcp_acknowledgement=tcp_acknowledgement & 0xFFFFFFFF,
        sanitized_l4_header=sanitized_l4_header,
        sanitized_l4_length=len(sanitized_l4_header) + len(payload),
        protocol_hint=protocol_hint,
        tls_record_types=tshark_integer_sequence(item["tls.record.content_type"]),
        tls_record_versions=tshark_integer_sequence(item["tls.record.version"]),
        tls_record_lengths=tshark_integer_sequence(item["tls.record.length"]),
        tls_handshake_types=tshark_integer_sequence(item["tls.handshake.type"]),
        quic_versions=tshark_integer_sequence(item["quic.version"]),
    )
    key_material = (
        endpoint_a[0]
        + endpoint_a[1].to_bytes(2, "big")
        + endpoint_b[0]
        + endpoint_b[1].to_bytes(2, "big")
        + protocol.to_bytes(1, "big")
    )
    metadata = {
        "key_material": key_material,
        "ip_version": ip_version,
        "protocol": protocol,
        "endpoint_a": endpoint_a[0],
        "endpoint_b": endpoint_b[0],
        "port_a": endpoint_a[1],
        "port_b": endpoint_b[1],
    }
    return (endpoint_a, endpoint_b, protocol), record, metadata


def feed_tshark_stdin(source: BinaryIO, destination: BinaryIO) -> None:
    try:
        shutil.copyfileobj(source, destination, length=16 * 1024 * 1024)
    except BrokenPipeError:
        pass
    finally:
        destination.close()


def tshark_command(
    path: Path,
    member: str | None,
    tshark_binary: str,
    session_reset_packets: int,
) -> list[str]:
    if session_reset_packets < 0:
        raise ValueError("tshark session reset packet count cannot be negative")
    command = [
        tshark_binary,
        "-n",
        "-l",
    ]
    if session_reset_packets:
        command.extend(("-M", str(session_reset_packets)))
    for preference in TSHARK_STATE_PREFERENCES:
        command.extend(("-o", preference))
    command.extend(
        [
        "-r",
        "-" if member is not None else str(path),
        "-T",
        "fields",
        "-E",
        "separator=/t",
        "-E",
        "quote=d",
        "-E",
        "occurrence=a",
        "-E",
        "aggregator=;",
        ]
    )
    for name in TSHARK_FIELDS:
        command.extend(("-e", name))
    return command


def tshark_packet_reader(
    path: Path,
    member: str | None,
    tshark_binary: str,
    session_reset_packets: int,
) -> Iterator[tuple[tuple[Any, ...], PacketRecord, dict[str, Any]] | None]:
    command = tshark_command(
        path, member, tshark_binary, session_reset_packets
    )
    source_context = open_capture(path, member) if member is not None else nullcontext(None)
    with source_context as source, tempfile.TemporaryFile(mode="w+b") as error_log:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if source is not None else None,
            stdout=subprocess.PIPE,
            stderr=error_log,
            text=False,
        )
        feeder = None
        if source is not None:
            assert process.stdin is not None
            feeder = threading.Thread(
                target=feed_tshark_stdin,
                args=(source, process.stdin),
                daemon=True,
            )
            feeder.start()
        assert process.stdout is not None
        text_output = io.TextIOWrapper(process.stdout, encoding="utf-8", errors="replace")
        try:
            for values in csv.reader(text_output, delimiter="\t", quotechar='"'):
                yield parse_tshark_fields(values)
        finally:
            text_output.close()
            if feeder is not None:
                feeder.join()
            return_code = process.wait()
            if return_code:
                error_log.seek(0, os.SEEK_END)
                error_size = error_log.tell()
                error_log.seek(max(0, error_size - 4000))
                message = error_log.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"tshark failed for {path}::{member or ''}: {message}"
                )


def tshark_identity(tshark_binary: str) -> str:
    result = subprocess.run(
        [tshark_binary, "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()[0].strip()


def build_processing_policy(
    *,
    idle_seconds: float,
    maximum_packets: int,
    payload_prefix_bytes: int,
    sanitized_l4_prefix_bytes: int,
    maximum_active_flows: int,
    packet_decoder: str,
    packet_decoder_identity: str,
    tshark_session_reset_packets: int,
    preprocessor_code_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": "caeos_preprocessing_policy_v1",
        "flow_accumulator_version": "bounded_exact_payload_v1",
        "flow_idle_timeout_seconds": float(idle_seconds),
        "maximum_packets_per_segment": int(maximum_packets),
        "payload_prefix_bytes": int(payload_prefix_bytes),
        "sanitized_l4_prefix_bytes": int(sanitized_l4_prefix_bytes),
        "maximum_active_flows": int(maximum_active_flows),
        "activity_idle_threshold_us": ACTIVITY_IDLE_THRESHOLD_US,
        "packet_decoder": packet_decoder,
        "packet_decoder_identity": packet_decoder_identity,
        "preprocessor_code_sha256": preprocessor_code_sha256,
        "tshark": (
            {
                "fields": list(TSHARK_FIELDS),
                "session_reset_packets": int(tshark_session_reset_packets),
                "state_preferences": list(TSHARK_STATE_PREFERENCES),
            }
            if packet_decoder == "tshark"
            else None
        ),
    }


def packet_reader(handle: BinaryIO) -> Iterable[tuple[float, bytes]]:
    import dpkt

    buffered = handle if isinstance(handle, io.BufferedReader) else io.BufferedReader(handle)
    magic = bytes(buffered.peek(4)[:4])
    if magic == PCAPNG_MAGIC:
        return dpkt.pcapng.Reader(buffered)
    if magic in PCAP_MAGICS:
        return dpkt.pcap.Reader(buffered)
    raise ValueError(f"unsupported capture magic: {magic.hex()}")


@contextmanager
def open_capture(path: Path, member: str | None) -> Iterator[BinaryIO]:
    if member is None:
        with path.open("rb") as handle:
            yield handle
        return
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            with archive.open(member, "r") as handle:
                yield handle
        return
    with tarfile.open(path, "r:*") as archive:
        handle = archive.extractfile(member)
        if handle is None:
            raise FileNotFoundError(f"archive member is not a file: {member}")
        with handle:
            yield handle


def endpoint_hash(dataset_id: str, endpoint: bytes) -> str:
    return hashlib.sha256(dataset_id.encode("utf-8") + b"\0" + endpoint).hexdigest()[:16]


def numeric_summary(values: list[int], prefix: str) -> dict[str, float | int]:
    if not values:
        return {
            f"{prefix}_min": 0,
            f"{prefix}_max": 0,
            f"{prefix}_mean": 0.0,
            f"{prefix}_std": 0.0,
        }
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return {
        f"{prefix}_min": min(values),
        f"{prefix}_max": max(values),
        f"{prefix}_mean": mean,
        f"{prefix}_std": math.sqrt(variance),
    }


def distribution_summary(
    values: list[int], prefix: str, *, include_total: bool = False
) -> dict[str, float | int]:
    summary = numeric_summary(values, prefix)
    if not values:
        summary.update(
            {
                f"{prefix}_median": 0.0,
                f"{prefix}_variance": 0.0,
                f"{prefix}_skewness": 0.0,
                f"{prefix}_coefficient_of_variation": 0.0,
            }
        )
        if include_total:
            summary[f"{prefix}_total"] = 0
        return summary
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = (
        float(ordered[middle])
        if len(ordered) % 2
        else (ordered[middle - 1] + ordered[middle]) / 2.0
    )
    mean = float(summary[f"{prefix}_mean"])
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    standard_deviation = math.sqrt(variance)
    skewness = (
        sum((value - mean) ** 3 for value in values)
        / len(values)
        / (standard_deviation**3)
        if standard_deviation
        else 0.0
    )
    summary.update(
        {
            f"{prefix}_median": median,
            f"{prefix}_variance": variance,
            f"{prefix}_skewness": skewness,
            f"{prefix}_coefficient_of_variation": (
                standard_deviation / abs(mean) if mean else 0.0
            ),
        }
    )
    if include_total:
        summary[f"{prefix}_total"] = sum(values)
    return summary


def directional_iats(packets: list[PacketRecord], direction: int) -> list[int]:
    timestamps = [
        packet.timestamp_ns for packet in packets if packet.direction == direction
    ]
    return [
        min(max(0, (current - previous) // 1000), 4_294_967_295)
        for previous, current in zip(timestamps, timestamps[1:])
    ]


def activity_idle_durations(
    packets: list[PacketRecord], threshold_us: int = ACTIVITY_IDLE_THRESHOLD_US
) -> tuple[list[int], list[int]]:
    if not packets:
        return [], []
    active: list[int] = []
    idle: list[int] = []
    burst_start = packets[0].timestamp_ns
    previous = burst_start
    for packet in packets[1:]:
        gap_us = max(0, (packet.timestamp_ns - previous) // 1000)
        if gap_us > threshold_us:
            active.append(max(0, (previous - burst_start) // 1000))
            idle.append(min(gap_us, 4_294_967_295))
            burst_start = packet.timestamp_ns
        previous = packet.timestamp_ns
    active.append(max(0, (previous - burst_start) // 1000))
    return active, idle


def encrypted_protocol_metadata(packets: list[PacketRecord]) -> dict[str, Any]:
    record_types = [value for packet in packets for value in packet.tls_record_types]
    record_versions = [
        value for packet in packets for value in packet.tls_record_versions
    ]
    record_lengths = [value for packet in packets for value in packet.tls_record_lengths]
    handshake_types = [
        value for packet in packets for value in packet.tls_handshake_types
    ]
    quic_versions = [value for packet in packets for value in packet.quic_versions]
    hints = {packet.protocol_hint for packet in packets}
    if quic_versions:
        hint = "QUIC"
    elif record_types or "TLS" in hints:
        hint = "TLS"
    else:
        hint = "Other"
    return {
        "application_protocol_hint": hint,
        "tls_record_type_seq": sequence(record_types),
        "tls_record_version_seq": sequence(record_versions),
        "tls_record_length_seq": sequence(record_lengths),
        "tls_handshake_type_seq": sequence(handshake_types),
        "tls_client_hello_present": int(1 in handshake_types),
        "tls_server_hello_present": int(2 in handshake_types),
        "quic_long_header_packet_count": len(quic_versions),
        "quic_version_seq": sequence(quic_versions[:64]),
    }


def flow_row(
    dataset: dict[str, Any],
    label: LabelRecord,
    state: FlowState,
    capture_id: str,
    source_sha256: str,
    source_member: str,
    payload_prefix_bytes: int,
    sanitized_l4_prefix_bytes: int,
    label_source: str | None = None,
) -> dict[str, Any]:
    packets = state.packets
    payload_prefix = bytes(state.payload_prefix[:payload_prefix_bytes])
    sanitized_l4_prefix = bytes(
        state.sanitized_l4_prefix[:sanitized_l4_prefix_bytes]
    )
    histogram = state.payload_histogram
    flow_hash = hashlib.sha256(
        dataset["id"].encode("utf-8") + b"\0" + state.key_material
    ).hexdigest()
    sample_material = "|".join(
        [
            dataset["id"],
            source_sha256,
            source_member,
            flow_hash,
            str(state.first_timestamp_ns),
            str(state.segment_index),
        ]
    )
    iats = [0]
    for previous, current in zip(packets, packets[1:]):
        delta = max(0, (current.timestamp_ns - previous.timestamp_ns) // 1000)
        iats.append(min(delta, 4_294_967_295))
    packet_lengths = [packet.frame_length for packet in packets]
    payload_lengths = [packet.payload_length for packet in packets]
    forward_packets = [packet for packet in packets if packet.direction == 1]
    reverse_packets = [packet for packet in packets if packet.direction == -1]
    forward_packet_lengths = [packet.frame_length for packet in forward_packets]
    reverse_packet_lengths = [packet.frame_length for packet in reverse_packets]
    forward_iats = directional_iats(packets, 1)
    reverse_iats = directional_iats(packets, -1)
    active_durations, idle_durations = activity_idle_durations(packets)
    direction_switch_iats = [
        iat
        for previous, current, iat in zip(packets, packets[1:], iats[1:])
        if previous.direction != current.direction
    ]
    direction_switch_count = len(direction_switch_iats)
    duration_seconds = max(
        (state.last_timestamp_ns - state.first_timestamp_ns) / 1_000_000_000,
        0.0,
    )
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": dataset["id"],
        "dataset_role": dataset["role"],
        "sample_id": hashlib.sha256(sample_material.encode("utf-8")).hexdigest(),
        "capture_id": capture_id,
        "source_container_sha256": source_sha256,
        "source_member": source_member,
        "label_status": label.status,
        "label_source": label_source or dataset["label_binding"],
        "label_mapping_version": LABEL_MAPPING_VERSION,
        "dataset_native_label": label.fine_label or "Pending",
        "traffic_class": label.traffic_class,
        "attack_category": label.attack_category,
        "attack_subcategory": label.attack_subcategory,
        "fine_label": label.fine_label,
        "family_label": label.family_label,
        "binary_label": label.binary_label,
        "flow_segment_index": state.segment_index,
        "flow_key_hash": flow_hash,
        "flow_start_ns": state.first_timestamp_ns,
        "flow_end_ns": state.last_timestamp_ns,
        "duration_us": max(0, (state.last_timestamp_ns - state.first_timestamp_ns) // 1000),
        "ip_version": state.ip_version,
        "transport_protocol": state.protocol,
        "endpoint_a_hash": endpoint_hash(dataset["id"], state.endpoint_a),
        "endpoint_b_hash": endpoint_hash(dataset["id"], state.endpoint_b),
        "port_a": state.port_a,
        "port_b": state.port_b,
        "packet_count_total": len(packets),
        "packet_count_stored": len(packets),
        "forward_packet_count": len(forward_packets),
        "reverse_packet_count": len(reverse_packets),
        "packet_bytes_total": sum(packet_lengths),
        "forward_packet_bytes": sum(packet.frame_length for packet in forward_packets),
        "reverse_packet_bytes": sum(packet.frame_length for packet in reverse_packets),
        "payload_bytes_total": sum(payload_lengths),
        "forward_payload_bytes": sum(
            packet.payload_length for packet in forward_packets
        ),
        "reverse_payload_bytes": sum(
            packet.payload_length for packet in reverse_packets
        ),
        "forward_transport_header_bytes": sum(
            packet.transport_header_length for packet in forward_packets
        ),
        "reverse_transport_header_bytes": sum(
            packet.transport_header_length for packet in reverse_packets
        ),
        "reverse_forward_packet_ratio": (
            len(reverse_packets) / len(forward_packets) if forward_packets else 0.0
        ),
        "reverse_forward_byte_ratio": (
            sum(reverse_packet_lengths) / sum(forward_packet_lengths)
            if sum(forward_packet_lengths)
            else 0.0
        ),
        "direction_switch_count": direction_switch_count,
        "direction_switch_rate": (
            direction_switch_count / (len(packets) - 1) if len(packets) > 1 else 0.0
        ),
        "direction_switch_iat_us_mean": (
            sum(direction_switch_iats) / direction_switch_count
            if direction_switch_count
            else 0.0
        ),
        "direction_switch_iat_us_std": (
            float(numeric_summary(direction_switch_iats, "switch")["switch_std"])
            if direction_switch_count
            else 0.0
        ),
        "fragmented_packet_count": sum(
            int(bool(packet.fragment_offset or (packet.ip_flags & 1)))
            for packet in packets
        ),
        "noninitial_fragment_count": sum(
            int(packet.fragment_offset > 0) for packet in packets
        ),
        "payload_bytes_stored": len(payload_prefix),
        "payload_b64": base64.b64encode(payload_prefix).decode("ascii"),
        "sanitized_l4_bytes_total": sum(
            packet.sanitized_l4_length for packet in packets
        ),
        "sanitized_l4_bytes_stored": len(sanitized_l4_prefix),
        "sanitized_l4_b64": base64.b64encode(sanitized_l4_prefix).decode("ascii"),
        "packet_length_seq": sequence(packet.frame_length for packet in packets),
        "ip_length_seq": sequence(packet.ip_length for packet in packets),
        "packet_iat_us_seq": sequence(iats),
        "direction_seq": sequence(packet.direction for packet in packets),
        "packet_protocol_seq": sequence(packet.protocol for packet in packets),
        "tcp_flags_seq": sequence(packet.flags for packet in packets),
        "ip_dscp_ecn_seq": sequence(packet.ip_dscp_ecn for packet in packets),
        "ip_flags_seq": sequence(packet.ip_flags for packet in packets),
        "ip_fragment_offset_seq": sequence(packet.fragment_offset for packet in packets),
        "ip_fragment_id_seq": sequence(packet.ip_fragment_id for packet in packets),
        "transport_header_length_seq": sequence(
            packet.transport_header_length for packet in packets
        ),
        "tcp_sequence_seq": sequence(packet.tcp_sequence for packet in packets),
        "tcp_acknowledgement_seq": sequence(
            packet.tcp_acknowledgement for packet in packets
        ),
        "packet_payload_length_seq": sequence(
            packet.payload_length for packet in packets
        ),
        "sanitized_l4_packet_length_seq": sequence(
            packet.sanitized_l4_length for packet in packets
        ),
        "packet_ttl_seq": sequence(packet.ttl for packet in packets),
        "tcp_window_seq": sequence(packet.window for packet in packets),
        "payload_histogram": sequence(histogram),
        "packets_per_second": len(packets) / duration_seconds if duration_seconds else 0.0,
        "bytes_per_second": sum(packet_lengths) / duration_seconds if duration_seconds else 0.0,
        "tcp_fin_flag_count": sum(bool(packet.flags & 0x01) for packet in packets),
        "tcp_syn_flag_count": sum(bool(packet.flags & 0x02) for packet in packets),
        "tcp_rst_flag_count": sum(bool(packet.flags & 0x04) for packet in packets),
        "tcp_psh_flag_count": sum(bool(packet.flags & 0x08) for packet in packets),
        "tcp_ack_flag_count": sum(bool(packet.flags & 0x10) for packet in packets),
        "tcp_urg_flag_count": sum(bool(packet.flags & 0x20) for packet in packets),
        "tcp_ece_flag_count": sum(bool(packet.flags & 0x40) for packet in packets),
        "tcp_cwr_flag_count": sum(bool(packet.flags & 0x80) for packet in packets),
    }
    row.update(distribution_summary(packet_lengths, "packet_length"))
    row.update(
        distribution_summary(iats[1:], "packet_iat_us", include_total=True)
    )
    row.update(distribution_summary(payload_lengths, "packet_payload_length"))
    row.update(numeric_summary(forward_packet_lengths, "forward_packet_length"))
    row.update(numeric_summary(reverse_packet_lengths, "reverse_packet_length"))
    row.update(numeric_summary(forward_iats, "forward_packet_iat_us"))
    row["forward_packet_iat_us_total"] = sum(forward_iats)
    row.update(numeric_summary(reverse_iats, "reverse_packet_iat_us"))
    row["reverse_packet_iat_us_total"] = sum(reverse_iats)
    row.update(numeric_summary(active_durations, "active_duration_us"))
    row["active_duration_us_total"] = sum(active_durations)
    row.update(numeric_summary(idle_durations, "idle_duration_us"))
    row["idle_duration_us_total"] = sum(idle_durations)
    protocol_metadata = encrypted_protocol_metadata(packets)
    if protocol_metadata["application_protocol_hint"] == "Other":
        ports = {state.port_a, state.port_b}
        if ports & {53, 5353}:
            protocol_metadata["application_protocol_hint"] = "DNS"
        elif 443 in ports:
            protocol_metadata["application_protocol_hint"] = "HTTPS_or_encrypted"
        elif ports & {80, 8080}:
            protocol_metadata["application_protocol_hint"] = "HTTP"
    row.update(protocol_metadata)
    return row


def process_capture(task: dict[str, Any]) -> dict[str, Any]:
    dataset = task["dataset"]
    path = Path(task["path"])
    member = task.get("member")
    source_member = task.get("source_member_override") or member
    if source_member is None:
        source_member = path.relative_to(Path(dataset["source_root"])).as_posix()
    path_bound_label = path_label(dataset, source_member)
    label_resolver = None
    alignment = task.get("label_alignment")
    official_boundary_split = bool(
        alignment is not None and alignment.get("official_boundary_split", False)
    )
    external_label_precedence = bool(
        alignment is not None
        and alignment.get("external_label_precedence", False)
    )
    if alignment is not None:
        label_resolver = LabelResolver(
            Path(alignment["path"]),
            dataset["id"],
            alignment["sha256"],
            int(alignment.get("tolerance_ns", 0)),
            str(alignment.get("conflict_policy", "reject")),
            str(alignment.get("time_nonoverlap_policy", "reject")),
        )
    part_path = Path(task["part_path"])
    part_meta = part_path.with_suffix(part_path.suffix + ".json")
    packet_decoder = task.get("packet_decoder", "dpkt")
    packet_decoder_identity = task.get(
        "packet_decoder_identity", "dpkt-unit-test"
    )
    processing_policy = task.get("processing_policy") or build_processing_policy(
        idle_seconds=float(task["idle_seconds"]),
        maximum_packets=int(task["maximum_packets"]),
        payload_prefix_bytes=int(task["payload_prefix_bytes"]),
        sanitized_l4_prefix_bytes=int(task["sanitized_l4_prefix_bytes"]),
        maximum_active_flows=int(task["maximum_active_flows"]),
        packet_decoder=packet_decoder,
        packet_decoder_identity=packet_decoder_identity,
        tshark_session_reset_packets=int(
            task.get("tshark_session_reset_packets", 0)
        ),
        preprocessor_code_sha256=sha256_file(Path(__file__)),
    )
    processing_policy_sha256 = canonical_json_hash(processing_policy)
    supplied_policy_sha256 = task.get("processing_policy_sha256")
    if (
        supplied_policy_sha256 is not None
        and supplied_policy_sha256 != processing_policy_sha256
    ):
        raise ValueError("processing policy hash mismatch in capture task")
    if part_path.exists() and part_meta.exists():
        metadata = load_json(part_meta)
        if (
            metadata.get("source_container_sha256") == task["source_sha256"]
            and metadata.get("schema_sha256") == task["schema_sha256"]
            and metadata.get("packet_decoder_identity") == packet_decoder_identity
            and metadata.get("processing_policy_sha256")
            == processing_policy_sha256
        ):
            metadata["reused"] = True
            return metadata
        raise ValueError(f"stale resumable part exists: {part_path}")
    part_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = part_path.with_suffix(part_path.suffix + ".partial")
    active: OrderedDict[tuple[Any, ...], FlowState] = OrderedDict()
    continuation: dict[tuple[Any, ...], int] = {}
    counters: Counter[str] = Counter()
    idle_ns = int(float(task["idle_seconds"]) * 1_000_000_000)
    max_packets = int(task["maximum_packets"])
    maximum_active = int(task["maximum_active_flows"])

    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=task["columns"], extrasaction="raise")

        def finalize(key: tuple[Any, ...], reason: str) -> None:
            state = active.pop(key)
            if not state.packets:
                return
            counters["flows_finalized_total"] += 1
            label = path_bound_label
            label_source = dataset["label_binding"]
            if label_resolver is not None:
                resolution = label_resolver.resolve(
                    source_member,
                    state.endpoint_a,
                    state.port_a,
                    state.endpoint_b,
                    state.port_b,
                    state.protocol,
                    state.first_timestamp_ns,
                    state.last_timestamp_ns,
                )
                if (
                    resolution.status == "conflicting_label"
                    and official_boundary_split
                ):
                    split = label_resolver.split_packet_observations_by_official_labels(
                        source_member,
                        state.endpoint_a,
                        state.port_a,
                        state.endpoint_b,
                        state.port_b,
                        state.protocol,
                        [
                            (packet.timestamp_ns, packet.frame_length)
                            for packet in state.packets
                        ],
                    )
                    if split["resolved"]:
                        counters["official_boundary_split_source_flows"] += 1
                        counters["official_boundary_split_segments"] += len(
                            split["segments"]
                        )
                        counters["official_boundary_split_packets"] += int(
                            split["source_packet_count"]
                        )
                        counters["official_boundary_split_packet_bytes"] += int(
                            split["source_packet_bytes"]
                        )
                        for offset, segment in enumerate(split["segments"]):
                            split_state = FlowState(
                                key_material=state.key_material,
                                ip_version=state.ip_version,
                                protocol=state.protocol,
                                endpoint_a=state.endpoint_a,
                                endpoint_b=state.endpoint_b,
                                port_a=state.port_a,
                                port_b=state.port_b,
                                segment_index=state.segment_index + offset,
                            )
                            start_index = int(segment["observation_start_index"])
                            end_index = int(segment["observation_end_index"])
                            for packet in state.packets[start_index:end_index]:
                                split_state.add_packet(
                                    packet,
                                    int(task["payload_prefix_bytes"]),
                                    int(task["sanitized_l4_prefix_bytes"]),
                                )
                            split_label = LabelRecord(
                                "aligned_unique_flow_official_boundary_split",
                                str(segment["fine_label"]),
                                str(segment["family_label"]),
                                int(segment["binary_label"]),
                            )
                            if (
                                path_bound_label.binary_label in {0, 1}
                                and (
                                    path_bound_label.fine_label
                                    != split_label.fine_label
                                    or path_bound_label.family_label
                                    != split_label.family_label
                                    or path_bound_label.binary_label
                                    != split_label.binary_label
                                )
                            ):
                                if external_label_precedence:
                                    counters[
                                        "label_alignment::path_external_disagreement_official_retained"
                                    ] += 1
                                else:
                                    split_label = LabelRecord(
                                        "conflicting_path_and_external_label",
                                        "",
                                        "",
                                        -1,
                                    )
                            split_label_source = (
                                ";".join(segment["label_sources"])
                                + "#"
                                + ",".join(segment["record_ids"])
                            )
                            writer.writerow(
                                flow_row(
                                    dataset,
                                    split_label,
                                    split_state,
                                    task["capture_id"],
                                    task["source_sha256"],
                                    source_member,
                                    int(task["payload_prefix_bytes"]),
                                    int(task["sanitized_l4_prefix_bytes"]),
                                    split_label_source,
                                )
                            )
                            counters["rows"] += 1
                            counters[f"finalize::{reason}"] += 1
                            counters[
                                f"label_alignment::{split_label.status}"
                            ] += 1
                        if reason == "maximum_packets":
                            continuation[key] = (
                                state.segment_index + len(split["segments"])
                            )
                        else:
                            continuation.pop(key, None)
                        return
                label = LabelRecord(
                    resolution.status,
                    resolution.fine_label,
                    resolution.family_label,
                    resolution.binary_label,
                )
                label_source = resolution.label_source
                if resolution.status == "unmatched_label":
                    diagnosis = label_resolver.diagnose_unmatched(
                        source_member,
                        state.endpoint_a,
                        state.port_a,
                        state.endpoint_b,
                        state.port_b,
                        state.protocol,
                        state.first_timestamp_ns,
                        state.last_timestamp_ns,
                    )
                    diagnosis_reason = str(diagnosis["reason"])
                    counters[f"label_diagnosis::{diagnosis_reason}"] += 1
                    approved_drops = set(
                        alignment.get("drop_unmatched_reasons", [])
                        if alignment is not None
                        else []
                    )
                    if diagnosis_reason in approved_drops:
                        counters["rows_excluded_by_label_policy"] += 1
                        counters[
                            f"label_exclusion::{diagnosis_reason}"
                        ] += 1
                        counters[
                            f"label_exclusion::{diagnosis_reason}::protocol::{state.protocol}"
                        ] += 1
                        counters["packets_excluded_by_label_policy"] += len(
                            state.packets
                        )
                        counters["packet_bytes_excluded_by_label_policy"] += sum(
                            packet.frame_length for packet in state.packets
                        )
                        if reason == "maximum_packets":
                            continuation[key] = state.segment_index + 1
                        else:
                            continuation.pop(key, None)
                        return
                if (
                    path_bound_label.binary_label in {0, 1}
                    and resolution.binary_label in {0, 1}
                    and (
                        path_bound_label.fine_label != resolution.fine_label
                        or path_bound_label.family_label != resolution.family_label
                        or path_bound_label.binary_label != resolution.binary_label
                    )
                ):
                    if external_label_precedence:
                        counters[
                            "label_alignment::path_external_disagreement_official_retained"
                        ] += 1
                    else:
                        label = LabelRecord(
                            "conflicting_path_and_external_label", "", "", -1
                        )
                counters[f"label_alignment::{label.status}"] += 1
            writer.writerow(
                flow_row(
                    dataset,
                    label,
                    state,
                    task["capture_id"],
                    task["source_sha256"],
                    source_member,
                    int(task["payload_prefix_bytes"]),
                    int(task["sanitized_l4_prefix_bytes"]),
                    label_source,
                )
            )
            counters["rows"] += 1
            counters[f"finalize::{reason}"] += 1
            if reason == "maximum_packets":
                continuation[key] = state.segment_index + 1
            else:
                continuation.pop(key, None)

        if packet_decoder == "tshark":
            decoded_packets = tshark_packet_reader(
                path,
                member,
                task.get("tshark_binary", "/usr/bin/tshark"),
                int(task.get("tshark_session_reset_packets", 0)),
            )
        elif packet_decoder == "dpkt":

            def dpkt_packets() -> Iterator[
                tuple[tuple[Any, ...], PacketRecord, dict[str, Any]] | None
            ]:
                with open_capture(path, member) as capture_handle:
                    for timestamp, frame in packet_reader(capture_handle):
                        yield parse_packet(float(timestamp), bytes(frame))

            decoded_packets = dpkt_packets()
        else:
            raise ValueError(f"unsupported packet decoder: {packet_decoder}")

        for parsed in decoded_packets:
            counters["packets_read"] += 1
            if parsed is None:
                if packet_decoder == "tshark":
                    counters["packets_skipped_non_ip_or_missing_endpoint"] += 1
                else:
                    counters["parse_failures"] += 1
                continue
            key, packet, metadata = parsed
            counters["parsed_packets_total"] += 1
            counters["parsed_packet_bytes_total"] += int(packet.frame_length)
            state = active.get(key)
            if state is not None and packet.timestamp_ns - state.last_timestamp_ns > idle_ns:
                finalize(key, "idle_timeout")
                state = None
            if state is None:
                state = FlowState(
                    **metadata,
                    segment_index=continuation.pop(key, 0),
                )
                active[key] = state
            else:
                active.move_to_end(key)
            state.add_packet(
                packet,
                int(task["payload_prefix_bytes"]),
                int(task["sanitized_l4_prefix_bytes"]),
                retain_packet_payload=official_boundary_split,
            )
            counters["peak_active_flows"] = max(
                counters["peak_active_flows"], len(active)
            )
            counters["peak_continuation_entries"] = max(
                counters["peak_continuation_entries"], len(continuation)
            )
            if len(state.packets) >= max_packets:
                finalize(key, "maximum_packets")
            while len(active) > maximum_active:
                finalize(next(iter(active)), "active_flow_limit")
            if counters["packets_read"] % 65536 == 0:
                threshold = packet.timestamp_ns - idle_ns
                expired = [
                    flow_key
                    for flow_key, flow_state in active.items()
                    if flow_state.last_timestamp_ns < threshold
                ]
                for flow_key in expired:
                    finalize(flow_key, "idle_sweep")
        for key in list(active):
            finalize(key, "end_of_capture")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, part_path)
    if label_resolver is not None:
        label_resolver.close()
    excluded_flows = int(counters.get("rows_excluded_by_label_policy", 0))
    finalized_flows = int(counters.get("flows_finalized_total", 0))
    exclusion_reasons = {
        key.removeprefix("label_exclusion::"): value
        for key, value in sorted(counters.items())
        if key.startswith("label_exclusion::") and "::protocol::" not in key
    }
    metadata = {
        "schema_version": "caeos_unified_capture_part_v1",
        "schema_sha256": task["schema_sha256"],
        "dataset_id": dataset["id"],
        "capture_id": task["capture_id"],
        "source_path": task.get("original_source_path", str(path)),
        "source_member": source_member,
        "source_container_sha256": task["source_sha256"],
        "packet_decoder": packet_decoder,
        "packet_decoder_identity": packet_decoder_identity,
        "processing_policy": processing_policy,
        "processing_policy_sha256": processing_policy_sha256,
        "part_path": str(part_path),
        "part_size_bytes": part_path.stat().st_size,
        "part_sha256": sha256_file(part_path),
        "label": path_bound_label.__dict__,
        "path_bound_label": path_bound_label.__dict__,
        "label_alignment": alignment,
        "label_exclusion_summary": {
            "rule_version": "caeos_label_exclusion_v1",
            "rule": (
                "exclude only when external resolution is unmatched_label and "
                "diagnose_unmatched.reason is explicitly approved"
            ),
            "approved_reasons": sorted(
                alignment.get("drop_unmatched_reasons", [])
                if alignment is not None
                else []
            ),
            "total_finalized_flows": finalized_flows,
            "excluded_flows": excluded_flows,
            "excluded_flow_fraction": (
                excluded_flows / finalized_flows if finalized_flows else 0.0
            ),
            "excluded_packets": int(
                counters.get("packets_excluded_by_label_policy", 0)
            ),
            "total_parsed_packets": int(counters.get("parsed_packets_total", 0)),
            "excluded_packet_fraction": (
                int(counters.get("packets_excluded_by_label_policy", 0))
                / int(counters.get("parsed_packets_total", 0))
                if counters.get("parsed_packets_total", 0)
                else 0.0
            ),
            "excluded_packet_bytes": int(
                counters.get("packet_bytes_excluded_by_label_policy", 0)
            ),
            "total_parsed_packet_bytes": int(
                counters.get("parsed_packet_bytes_total", 0)
            ),
            "excluded_packet_byte_fraction": (
                int(counters.get("packet_bytes_excluded_by_label_policy", 0))
                / int(counters.get("parsed_packet_bytes_total", 0))
                if counters.get("parsed_packet_bytes_total", 0)
                else 0.0
            ),
            "reason_counts": exclusion_reasons,
            "source_pcaps_modified": False,
        },
        "counters": dict(sorted(counters.items())),
        "reused": False,
    }
    atomic_json(part_meta, metadata)
    return metadata


def materialize_tar_archive(
    dataset_id: str, source: dict[str, Any], output_root: Path
) -> dict[str, str]:
    path = Path(source["path"])
    members = {
        item["name"]: int(item["size_bytes"])
        for item in source.get("capture_members", [])
    }
    staging_root = (
        output_root
        / "_archive_staging"
        / dataset_id
        / source["sha256"][:16]
    )
    manifest_path = staging_root / "materialization.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        mapping = {
            item["member"]: item["path"] for item in manifest["members"]
        }
        if set(mapping) != set(members):
            raise ValueError(f"staged archive member set mismatch: {path}")
        for member, staged_path in mapping.items():
            if Path(staged_path).stat().st_size != members[member]:
                raise ValueError(f"staged archive member size mismatch: {member}")
        return mapping
    staging_root.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    with tarfile.open(path, "r:*") as archive:
        for info in archive:
            if not info.isfile() or info.name not in members:
                continue
            suffix = Path(info.name).suffix.lower() or ".pcap"
            target = staging_root / (
                hashlib.sha256(info.name.encode("utf-8")).hexdigest() + suffix
            )
            temporary = target.with_suffix(target.suffix + ".partial")
            source_handle = archive.extractfile(info)
            if source_handle is None:
                raise ValueError(f"cannot read archive member: {info.name}")
            with source_handle, temporary.open("wb") as output:
                shutil.copyfileobj(source_handle, output, length=16 * 1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
            if temporary.stat().st_size != members[info.name]:
                raise ValueError(f"materialized member size mismatch: {info.name}")
            os.replace(temporary, target)
            mapping[info.name] = str(target)
    if set(mapping) != set(members):
        missing = sorted(set(members) - set(mapping))
        raise ValueError(f"archive members not materialized from {path}: {missing[:10]}")
    atomic_json(
        manifest_path,
        {
            "schema_version": "caeos_tar_materialization_v1",
            "dataset_id": dataset_id,
            "source_path": str(path),
            "source_sha256": source["sha256"],
            "members": [
                {
                    "member": member,
                    "path": mapping[member],
                    "size_bytes": members[member],
                }
                for member in sorted(mapping)
            ],
        },
    )
    return mapping


def materialize_tar_archives(
    dataset: dict[str, Any],
    source_dataset: dict[str, Any],
    output_root: Path,
    io_threads: int,
) -> dict[tuple[str, str], str]:
    tar_sources = [
        source
        for source in source_dataset["source_files"]
        if source["kind"] == "archive" and not source["path"].lower().endswith(".zip")
    ]
    mapping: dict[tuple[str, str], str] = {}
    with ThreadPoolExecutor(max_workers=io_threads) as executor:
        futures = {
            executor.submit(
                materialize_tar_archive, dataset["id"], source, output_root
            ): source
            for source in tar_sources
        }
        for future in as_completed(futures):
            source = futures[future]
            for member, staged_path in future.result().items():
                mapping[(source["path"], member)] = staged_path
    return mapping


def capture_tasks(
    dataset: dict[str, Any],
    source_dataset: dict[str, Any],
    output_root: Path,
    schema: dict[str, Any],
    reservoir: dict[str, Any],
    maximum_active_flows: int,
    staged_members: dict[tuple[str, str], str] | None = None,
    packet_decoder: str = "dpkt",
    tshark_binary: str = "/usr/bin/tshark",
    packet_decoder_identity: str = "dpkt-unit-test",
    tshark_session_reset_packets: int = 0,
    preprocessor_code_sha256: str | None = None,
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    columns = [column["name"] for column in schema["columns"]]
    schema_sha256 = canonical_json_hash(schema)
    processing_policy = build_processing_policy(
        idle_seconds=float(reservoir["flow_idle_timeout_seconds"]),
        maximum_packets=int(reservoir["maximum_packets"]),
        payload_prefix_bytes=int(reservoir["payload_prefix_bytes"]),
        sanitized_l4_prefix_bytes=int(
            reservoir.get("sanitized_l4_prefix_bytes", 2048)
        ),
        maximum_active_flows=maximum_active_flows,
        packet_decoder=packet_decoder,
        packet_decoder_identity=packet_decoder_identity,
        tshark_session_reset_packets=tshark_session_reset_packets,
        preprocessor_code_sha256=(
            preprocessor_code_sha256 or sha256_file(Path(__file__))
        ),
    )
    processing_policy_sha256 = canonical_json_hash(processing_policy)
    for source in source_dataset["source_files"]:
        members = source.get("capture_members") or [None]
        for member_record in members:
            member = member_record["name"] if isinstance(member_record, dict) else None
            identity = f"{source['path']}::{member or ''}"
            capture_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
            staged_path = (
                staged_members.get((source["path"], member))
                if staged_members is not None and member is not None
                else None
            )
            tasks.append(
                {
                    "dataset": dataset,
                    "path": staged_path or source["path"],
                    "member": None if staged_path else member,
                    "source_member_override": member if staged_path else None,
                    "original_source_path": source["path"],
                    "capture_id": capture_hash,
                    "source_sha256": source["sha256"],
                    "part_path": str(output_root / "_parts" / dataset["id"] / f"{capture_hash}.part"),
                    "schema_sha256": schema_sha256,
                    "columns": columns,
                    "idle_seconds": reservoir["flow_idle_timeout_seconds"],
                    "maximum_packets": reservoir["maximum_packets"],
                    "payload_prefix_bytes": reservoir["payload_prefix_bytes"],
                    "sanitized_l4_prefix_bytes": reservoir.get(
                        "sanitized_l4_prefix_bytes", 2048
                    ),
                    "maximum_active_flows": maximum_active_flows,
                    "packet_decoder": packet_decoder,
                    "tshark_binary": tshark_binary,
                    "packet_decoder_identity": packet_decoder_identity,
                    "tshark_session_reset_packets": tshark_session_reset_packets,
                    "processing_policy": processing_policy,
                    "processing_policy_sha256": processing_policy_sha256,
                }
            )
    return tasks


def verify_csv(
    path: Path,
    columns: list[str],
    expected_rows: int,
    require_formal_labels: bool = False,
) -> dict[str, Any]:
    sequence_columns = [
        "packet_length_seq",
        "ip_length_seq",
        "packet_iat_us_seq",
        "direction_seq",
        "packet_protocol_seq",
        "tcp_flags_seq",
        "ip_dscp_ecn_seq",
        "ip_flags_seq",
        "ip_fragment_offset_seq",
        "ip_fragment_id_seq",
        "transport_header_length_seq",
        "tcp_sequence_seq",
        "tcp_acknowledgement_seq",
        "packet_payload_length_seq",
        "sanitized_l4_packet_length_seq",
        "packet_ttl_seq",
        "tcp_window_seq",
    ]
    counters: Counter[str] = Counter()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != columns:
            raise ValueError(f"CSV header differs from frozen schema: {path}")
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"extra CSV fields at row {row_number}: {path}")
            if row["schema_version"] != SCHEMA_VERSION:
                raise ValueError(f"schema version mismatch at row {row_number}")
            packet_count = int(row["packet_count_stored"])
            if not 1 <= packet_count <= 64:
                raise ValueError(f"invalid packet count at row {row_number}")
            for column in sequence_columns:
                values = row[column].split(";") if row[column] else []
                if len(values) != packet_count:
                    raise ValueError(
                        f"{column} length mismatch at row {row_number}"
                    )
            payload = base64.b64decode(row["payload_b64"], validate=True)
            if len(payload) != int(row["payload_bytes_stored"]):
                raise ValueError(f"payload length mismatch at row {row_number}")
            if len(payload) > 4096:
                raise ValueError(f"payload prefix overflow at row {row_number}")
            sanitized_l4 = base64.b64decode(row["sanitized_l4_b64"], validate=True)
            if len(sanitized_l4) != int(row["sanitized_l4_bytes_stored"]):
                raise ValueError(f"sanitized L4 length mismatch at row {row_number}")
            if len(sanitized_l4) > 2048:
                raise ValueError(f"sanitized L4 prefix overflow at row {row_number}")
            histogram = [int(value) for value in row["payload_histogram"].split(";")]
            if len(histogram) != 256:
                raise ValueError(f"payload histogram width mismatch at row {row_number}")
            if sum(histogram) != int(row["payload_bytes_total"]):
                raise ValueError(f"payload histogram sum mismatch at row {row_number}")
            if int(row["binary_label"]) not in {-1, 0, 1}:
                raise ValueError(f"invalid binary label at row {row_number}")
            if require_formal_labels:
                binary_label = int(row["binary_label"])
                expected_class = "Benign" if binary_label == 0 else "Malicious"
                if binary_label not in {0, 1} or row["traffic_class"] != expected_class:
                    raise ValueError(f"non-formal traffic label at row {row_number}")
                for label_column in (
                    "dataset_native_label",
                    "attack_category",
                    "attack_subcategory",
                    "fine_label",
                    "family_label",
                ):
                    if not row[label_column] or row[label_column] == "Pending":
                        raise ValueError(
                            f"missing formal {label_column} at row {row_number}"
                        )
                if row["attack_category"] not in ATTACK_CATEGORIES:
                    raise ValueError(f"invalid attack category at row {row_number}")
            if len(row["sample_id"]) != 64 or len(row["flow_key_hash"]) != 64:
                raise ValueError(f"invalid identity width at row {row_number}")
            counters["rows"] += 1
            if payload:
                counters["rows_with_payload"] += 1
            counters[f"label_status::{row['label_status']}"] += 1
    if counters["rows"] != expected_rows:
        raise ValueError(
            f"CSV row count {counters['rows']} != expected {expected_rows}: {path}"
        )
    return {
        "full_row_validation": True,
        "rows": counters["rows"],
        "rows_with_payload": counters["rows_with_payload"],
        "payload_row_fraction": (
            counters["rows_with_payload"] / counters["rows"]
            if counters["rows"]
            else 0.0
        ),
        "label_status_counts": {
            key.removeprefix("label_status::"): value
            for key, value in sorted(counters.items())
            if key.startswith("label_status::")
        },
    }


def merge_parts(
    dataset: dict[str, Any],
    parts: list[dict[str, Any]],
    output_root: Path,
    columns: list[str],
    schema_sha256: str,
    source_manifest_sha256: str,
    parser_processes: int,
) -> dict[str, Any]:
    if not parts:
        raise ValueError(f"dataset has no capture parts: {dataset['id']}")
    policy_hashes = {
        str(part.get("processing_policy_sha256", "")) for part in parts
    }
    if "" in policy_hashes or len(policy_hashes) != 1:
        raise ValueError(
            f"mixed or missing processing policies for dataset: {dataset['id']}"
        )
    processing_policy_sha256 = next(iter(policy_hashes))
    processing_policy = parts[0]["processing_policy"]
    if canonical_json_hash(processing_policy) != processing_policy_sha256:
        raise ValueError(f"invalid processing policy for dataset: {dataset['id']}")
    formal_label_ready = all(
        int(part["label"]["binary_label"]) in {0, 1}
        and "pending" not in str(part["label"]["status"])
        and "unmapped" not in str(part["label"]["status"])
        and "unresolved" not in str(part["label"]["status"])
        for part in parts
    )
    if formal_label_ready:
        final_path = output_root / f"{dataset['id']}.csv"
        manifest_path = output_root / f"{dataset['id']}.csv.manifest.json"
    else:
        final_path = output_root / "_pending_labels" / f"{dataset['id']}.features.part"
        manifest_path = final_path.with_suffix(".part.manifest.json")
    if final_path.exists() and manifest_path.exists():
        existing = load_json(manifest_path)
        if (
            existing.get("schema_sha256") != schema_sha256
            or existing.get("source_manifest_sha256") != source_manifest_sha256
            or existing.get("processing_policy_sha256")
            != processing_policy_sha256
            or existing.get("materialized_sha256") != sha256_file(final_path)
        ):
            raise ValueError(f"finalized dataset identity mismatch: {final_path}")
        existing["reused"] = True
        return existing
    if final_path.exists() or manifest_path.exists():
        raise ValueError(f"incomplete finalized dataset pair: {final_path}")
    temporary = final_path.with_suffix(".csv.partial")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    started = time.time()
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(columns)
        for part in sorted(parts, key=lambda item: item["capture_id"]):
            with Path(part["part_path"]).open("r", encoding="utf-8", newline="") as source:
                shutil.copyfileobj(source, output, length=16 * 1024 * 1024)
            rows += int(part["counters"].get("rows", 0))
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, final_path)
    verification = verify_csv(
        final_path,
        columns,
        rows,
        require_formal_labels=formal_label_ready,
    )
    label_status_counts = Counter(
        str(part["label"]["status"]) for part in parts
    )
    manifest: dict[str, Any] = {
        "schema_version": "caeos_unified_dataset_csv_manifest_v2",
        "dataset_id": dataset["id"],
        "dataset_role": dataset["role"],
        "csv_path": str(final_path) if formal_label_ready else None,
        "staged_feature_path": str(final_path) if not formal_label_ready else None,
        "materialized_size_bytes": final_path.stat().st_size,
        "materialized_sha256": sha256_file(final_path),
        "rows": rows,
        "capture_count": len(parts),
        "schema_sha256": schema_sha256,
        "source_manifest_sha256": source_manifest_sha256,
        "processing_policy": processing_policy,
        "processing_policy_sha256": processing_policy_sha256,
        "parser_processes": parser_processes,
        "label_status_counts_by_capture": dict(sorted(label_status_counts.items())),
        "formal_label_ready": formal_label_ready,
        "verification": verification,
        "parts": parts,
        "merge_seconds": time.time() - started,
        "features_materialized": True,
        "csv_materialized": formal_label_ready,
        "reused": False,
    }
    manifest["manifest_sha256"] = canonical_json_hash(manifest)
    atomic_json(manifest_path, manifest)
    return manifest


def prepare_dataset(
    dataset: dict[str, Any],
    source_dataset: dict[str, Any],
    output_root: Path,
    schema: dict[str, Any],
    reservoir: dict[str, Any],
    parser_processes: int,
    io_threads: int,
    maximum_active_flows: int,
    packet_decoder: str,
    tshark_binary: str,
    packet_decoder_identity: str,
    tshark_session_reset_packets: int,
    preprocessor_code_sha256: str,
) -> dict[str, Any]:
    staged_members = materialize_tar_archives(
        dataset, source_dataset, output_root, io_threads
    )
    tasks = capture_tasks(
        dataset,
        source_dataset,
        output_root,
        schema,
        reservoir,
        maximum_active_flows,
        staged_members=staged_members,
        packet_decoder=packet_decoder,
        tshark_binary=tshark_binary,
        packet_decoder_identity=packet_decoder_identity,
        tshark_session_reset_packets=tshark_session_reset_packets,
        preprocessor_code_sha256=preprocessor_code_sha256,
    )
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=parser_processes) as executor:
        futures = [executor.submit(process_capture, task) for task in tasks]
        for future in as_completed(futures):
            results.append(future.result())
    return merge_parts(
        dataset,
        results,
        output_root,
        [column["name"] for column in schema["columns"]],
        canonical_json_hash(schema),
        source_dataset["source_manifest_sha256"],
        parser_processes,
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--parser-processes", type=int, default=64)
    parser.add_argument("--io-threads", type=int, default=16)
    parser.add_argument("--maximum-active-flows", type=int, default=6000)
    parser.add_argument(
        "--packet-decoder", choices=("tshark", "dpkt"), default="tshark"
    )
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    parser.add_argument("--tshark-session-reset-packets", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.parser_processes < 1:
        raise ValueError("parser_processes must be positive")
    if args.maximum_active_flows < 1:
        raise ValueError("maximum_active_flows must be positive")
    if args.tshark_session_reset_packets < 0:
        raise ValueError("tshark-session-reset-packets cannot be negative")
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    preprocessor_code_sha256 = sha256_file(Path(__file__))
    if args.packet_decoder == "tshark":
        packet_decoder_identity = tshark_identity(args.tshark_binary)
    else:
        import dpkt

        packet_decoder_identity = f"dpkt {dpkt.__version__}"
    if schema.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported unified CSV schema")
    validate_source_manifest(catalog, source_manifest)
    catalog_by_id = {item["id"]: item for item in catalog["datasets"]}
    source_by_id = {item["id"]: item for item in source_manifest["datasets"]}
    summaries: list[dict[str, Any]] = []
    for dataset_id in args.dataset:
        if dataset_id not in catalog_by_id or dataset_id not in source_by_id:
            raise ValueError(f"dataset absent from catalog or source manifest: {dataset_id}")
        source_dataset = dict(source_by_id[dataset_id])
        source_dataset["source_manifest_sha256"] = source_manifest["manifest_sha256"]
        summaries.append(
            prepare_dataset(
                catalog_by_id[dataset_id],
                source_dataset,
                args.output_root,
                schema,
                catalog["feature_reservoir"],
                args.parser_processes,
                args.io_threads,
                args.maximum_active_flows,
                args.packet_decoder,
                args.tshark_binary,
                packet_decoder_identity,
                args.tshark_session_reset_packets,
                preprocessor_code_sha256,
            )
        )
    completion: dict[str, Any] = {
        "schema_version": "caeos_unified_preprocessing_completion_v1",
        "catalog_sha256": canonical_json_hash(catalog),
        "schema_sha256": canonical_json_hash(schema),
        "source_manifest_sha256": source_manifest["manifest_sha256"],
        "packet_decoder": args.packet_decoder,
        "packet_decoder_identity": packet_decoder_identity,
        "preprocessor_code_sha256": preprocessor_code_sha256,
        "tshark_session_reset_packets": args.tshark_session_reset_packets,
        "tshark_state_preferences": list(TSHARK_STATE_PREFERENCES),
        "processing_policy_sha256_by_dataset": {
            item["dataset_id"]: item["processing_policy_sha256"]
            for item in summaries
        },
        "datasets": summaries,
        "dataset_count": len(summaries),
        "all_csv_materialized": all(
            item["csv_materialized"] for item in summaries
        ),
        "all_formal_labels_ready": all(
            item["formal_label_ready"] for item in summaries
        ),
    }
    completion["completion_sha256"] = canonical_json_hash(completion)
    completion_path = args.output_root / "completion.json"
    if completion_path.exists():
        existing = load_json(completion_path)
        if existing.get("completion_sha256") != completion["completion_sha256"]:
            raise ValueError(f"completion identity mismatch: {completion_path}")
        print(json.dumps(existing, ensure_ascii=False, sort_keys=True))
        return
    atomic_json(completion_path, completion)
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

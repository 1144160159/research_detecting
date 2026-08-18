from __future__ import annotations

import csv
import socket
from pathlib import Path

import pytest

from prepare_strict_v4_cic_iot2023_pcap_multimodal import (
    canonical_flow_key,
    parse_ip_packet,
)
from prepare_strict_v4_unsw_surrogate_unknown_multimodal import (
    DEFAULT_ALLOWED_CATEGORIES,
    audit_pcap_matches,
    ground_truth_key,
    load_ground_truth,
    match_event,
    pcap_sort_key,
    protocol_number,
    validate_allowed_categories,
)


def write_ground_truth(path: Path) -> None:
    fields = [
        "Start time",
        "Last time",
        "Attack category",
        "Attack subcategory",
        "Protocol",
        "Source IP",
        "Source Port",
        "Destination IP",
        "Destination Port",
        "Attack Name",
        "Attack Reference",
        ".",
    ]
    rows = [
        {
            "Start time": "100",
            "Last time": "102",
            "Attack category": "Exploits",
            "Attack subcategory": "Browser",
            "Protocol": "tcp",
            "Source IP": "192.0.2.10",
            "Source Port": "1234",
            "Destination IP": "198.51.100.20",
            "Destination Port": "443",
        },
        {
            "Start time": "110",
            "Last time": "111",
            "Attack category": "DoS",
            "Attack subcategory": "Flood",
            "Protocol": "udp",
            "Source IP": "192.0.2.11",
            "Source Port": "2222",
            "Destination IP": "198.51.100.21",
            "Destination Port": "53",
        },
        {
            "Start time": "120",
            "Last time": "121",
            "Attack category": "Exploits",
            "Attack subcategory": "Unsupported",
            "Protocol": "arp",
            "Source IP": "192.0.2.12",
            "Source Port": "0",
            "Destination IP": "198.51.100.22",
            "Destination Port": "0",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_default_categories_exclude_direct_target_families() -> None:
    normalized = validate_allowed_categories(DEFAULT_ALLOWED_CATEGORIES)
    assert normalized == DEFAULT_ALLOWED_CATEGORIES
    with pytest.raises(ValueError, match="overlap target held-out"):
        validate_allowed_categories(("Exploits", "DoS"))


def test_protocol_and_ground_truth_key_are_bidirectional() -> None:
    assert protocol_number(" TCP ") == socket.IPPROTO_TCP
    assert protocol_number("not-a-protocol") is None
    row = {
        "Protocol": "tcp",
        "Source IP": "192.0.2.10",
        "Source Port": "1234",
        "Destination IP": "198.51.100.20",
        "Destination Port": "443",
    }
    expected = canonical_flow_key(
        socket.inet_pton(socket.AF_INET, "198.51.100.20"),
        socket.inet_pton(socket.AF_INET, "192.0.2.10"),
        443,
        1234,
        socket.IPPROTO_TCP,
    )
    assert ground_truth_key(row) == expected[:3]


def test_load_and_match_only_allowed_events(tmp_path: Path) -> None:
    ground_truth = tmp_path / "NUSW-NB15_GT.csv"
    write_ground_truth(ground_truth)
    loaded = load_ground_truth(ground_truth, ("Exploits",))
    assert loaded.rows_read == 3
    assert loaded.category_counts == {"Exploits": 2, "DoS": 1}
    assert loaded.allowed_category_counts == {"Exploits": 1}
    assert loaded.rows_rejected == 1

    key = next(iter(loaded.events_by_key))
    event = match_event(loaded.events_by_key, key, 99.25, 1.0)
    assert event is not None
    assert event.category == "Exploits"
    assert match_event(loaded.events_by_key, key, 98.0, 1.0) is None


def test_pcap_sort_key_orders_capture_date_then_numeric_file() -> None:
    paths = [
        Path("/data/pcap17-02-2015/2.pcap"),
        Path("/data/pcap22-01-2015/10.pcap"),
        Path("/data/pcap22-01-2015/2.pcap"),
    ]
    ordered = sorted(paths, key=pcap_sort_key)
    assert [path.as_posix() for path in ordered] == [
        "/data/pcap22-01-2015/2.pcap",
        "/data/pcap22-01-2015/10.pcap",
        "/data/pcap17-02-2015/2.pcap",
    ]


def test_empty_pcap_audit_is_explicit() -> None:
    assert audit_pcap_matches([], {}, 1.0, 100) == []


def test_linux_cooked_packet_is_parsed_when_dpkt_is_available() -> None:
    dpkt = pytest.importorskip("dpkt")
    tcp = dpkt.tcp.TCP(sport=1234, dport=443, flags=dpkt.tcp.TH_SYN)
    ip = dpkt.ip.IP(
        src=socket.inet_pton(socket.AF_INET, "192.0.2.10"),
        dst=socket.inet_pton(socket.AF_INET, "198.51.100.20"),
        p=socket.IPPROTO_TCP,
        data=tcp,
    )
    ip.len = len(ip)
    cooked = dpkt.sll.SLL(
        ethtype=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    parsed = parse_ip_packet(100.0, bytes(cooked))
    assert parsed is not None
    key, record = parsed
    assert key[2] == socket.IPPROTO_TCP
    assert record.frame_length == len(bytes(cooked))

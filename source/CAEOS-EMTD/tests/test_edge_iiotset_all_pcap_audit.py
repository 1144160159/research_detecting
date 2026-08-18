from __future__ import annotations

import argparse
import csv
import socket
from pathlib import Path

import dpkt

from audit_caeos_edge_iiotset_all_pcaps import run
from inventory_caeos_edge_iiotset_pcaps import inventory


FIELDS = [
    "frame.time",
    "ip.src_host",
    "ip.dst_host",
    "tcp.srcport",
    "tcp.dstport",
    "udp.port",
    "Attack_label",
    "Attack_type",
]


def write_pair(
    root: Path,
    pcap_relative: str,
    csv_relative: str,
    binary_label: int,
    attack_type: str,
    protocol: int = 6,
) -> None:
    pcap = root / pcap_relative
    packet_csv = root / csv_relative
    pcap.parent.mkdir(parents=True, exist_ok=True)
    packet_csv.parent.mkdir(parents=True, exist_ok=True)
    transport = (
        dpkt.tcp.TCP(sport=1387, dport=80, flags=dpkt.tcp.TH_SYN)
        if protocol == 6
        else dpkt.icmp.ICMP(type=8, code=0, data=b"probe")
    )
    ip = dpkt.ip.IP(
        src=socket.inet_aton("192.168.0.170"),
        dst=socket.inet_aton("192.168.0.128"),
        p=protocol,
        ttl=64,
        data=transport,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x06\x07\x08\x09\x0a\x0b",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        writer.writepkt(bytes(ethernet), ts=1_637_766_209.1)
        writer.close()
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "frame.time": "2021 16:03:29.100000000",
                "ip.src_host": "192.168.0.170",
                "ip.dst_host": "192.168.0.128",
                "tcp.srcport": "1387.0" if protocol == 6 else "0.0",
                "tcp.dstport": "80.0" if protocol == 6 else "0.0",
                "udp.port": "0.0",
                "Attack_label": str(binary_label),
                "Attack_type": attack_type,
            }
        )


def test_inventory_pairs_attack_names_and_excludes_aggregate_csvs(tmp_path: Path) -> None:
    write_pair(
        tmp_path,
        "Attack traffic/DDoS HTTP Flood Attacks.pcap",
        "Attack traffic/DDoS_HTTP_Flood_attack.csv",
        1,
        "DDoS_HTTP",
    )
    aggregate = tmp_path / "Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv"
    aggregate.parent.mkdir(parents=True)
    aggregate.write_text("aggregate\n", encoding="utf-8")
    report = inventory(tmp_path)
    assert report["passed"] is True
    assert report["pair_count"] == 1
    assert report["aggregate_only_csvs"] == [
        "Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv"
    ]


def test_single_fixture_pcap_exercises_full_aggregate_gate(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    run_root = tmp_path / "run"
    write_pair(
        data_root,
        "Attack traffic/Port Scanning attack.pcap",
        "Attack traffic/Port_Scanning_attack.csv",
        1,
        "Port_Scanning",
    )
    report = run(
        argparse.Namespace(
            data_root=data_root,
            run_root=run_root,
            idle_seconds=30.0,
            maximum_packets=1_000_000,
            maximum_unmatched_samples=10,
            stop_after=0,
            resume=False,
            verify_source_sha_on_resume=False,
        )
    )
    assert report["formal_label_gate_passed"] is True
    assert report["inventory_pair_count"] == 1
    assert report["complete_pcap_count"] == 1
    assert report["matched_flows"] == 1
    assert report["excluded_flows"] == 0
    assert report["full_label_index_validation"]["passed"] is True


def test_stop_after_keeps_dataset_formal_gate_closed(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    write_pair(
        data_root,
        "Attack traffic/Port Scanning attack.pcap",
        "Attack traffic/Port_Scanning_attack.csv",
        1,
        "Port_Scanning",
    )
    write_pair(
        data_root,
        "Normal traffic/Distance/Distance.pcap",
        "Normal traffic/Distance/Distance.csv",
        0,
        "Normal",
    )
    report = run(
        argparse.Namespace(
            data_root=data_root,
            run_root=tmp_path / "run",
            idle_seconds=30.0,
            maximum_packets=1_000_000,
            maximum_unmatched_samples=10,
            stop_after=1,
            resume=False,
            verify_source_sha_on_resume=False,
        )
    )
    assert report["inventory_pair_count"] == 2
    assert report["completed_pair_count"] == 1
    assert report["formal_label_gate_passed"] is False
    assert report["full_label_index"] is None


def test_all_icmp_capture_retains_official_malicious_label(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    write_pair(
        data_root,
        "Attack traffic/DDoS ICMP Flood Attacks.pcap",
        "Attack traffic/DDoS_ICMP_Flood_attack.csv",
        1,
        "DDoS_ICMP",
        protocol=1,
    )
    report = run(
        argparse.Namespace(
            data_root=data_root,
            run_root=tmp_path / "run",
            idle_seconds=30.0,
            maximum_packets=1_000_000,
            maximum_unmatched_samples=10,
            stop_after=0,
            resume=False,
            verify_source_sha_on_resume=False,
        )
    )
    pair = report["pair_summaries"][0]
    assert pair["zero_retained_supported_ip_flows"] is False
    assert pair["matched_flows"] == 1
    assert pair["excluded_flows"] == 0
    assert pair["effective_retained_flow_coverage"] == 1.0
    assert pair["pair_gate_passed"] is True


def test_completed_pair_is_resumed_with_source_sha_verification(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    run_root = tmp_path / "run"
    write_pair(
        data_root,
        "Attack traffic/Port Scanning attack.pcap",
        "Attack traffic/Port_Scanning_attack.csv",
        1,
        "Port_Scanning",
    )
    common = dict(
        data_root=data_root,
        run_root=run_root,
        idle_seconds=30.0,
        maximum_packets=1_000_000,
        maximum_unmatched_samples=10,
        stop_after=0,
        verify_source_sha_on_resume=True,
    )
    first = run(argparse.Namespace(**common, resume=False))
    second = run(argparse.Namespace(**common, resume=True))
    assert first["formal_label_gate_passed"] is True
    assert second["formal_label_gate_passed"] is True
    assert second["pair_summaries"][0]["reused"] is True

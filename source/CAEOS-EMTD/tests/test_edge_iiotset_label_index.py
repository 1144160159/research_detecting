from __future__ import annotations

import csv
import socket
from pathlib import Path

import dpkt
import pytest

from build_caeos_edge_iiotset_label_index import paired_records


FIELDS = [
    "frame.time",
    "ip.src_host",
    "ip.dst_host",
    "arp.dst.proto_ipv4",
    "arp.opcode",
    "arp.hw.size",
    "icmp.checksum",
    "icmp.seq_le",
    "icmp.transmit_timestamp",
    "icmp.unused",
    "tcp.srcport",
    "tcp.dstport",
    "udp.port",
    "Attack_label",
    "Attack_type",
]


def write_packet(writer: dpkt.pcap.Writer, timestamp: float, sport: int, dport: int) -> None:
    tcp = dpkt.tcp.TCP(sport=sport, dport=dport, flags=dpkt.tcp.TH_SYN)
    ip = dpkt.ip.IP(
        src=socket.inet_aton("192.168.0.170"),
        dst=socket.inet_aton("192.168.0.128"),
        p=dpkt.ip.IP_PROTO_TCP,
        ttl=64,
        data=tcp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x06\x07\x08\x09\x0a\x0b",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def write_background_udp(writer: dpkt.pcap.Writer, timestamp: float) -> None:
    udp = dpkt.udp.UDP(sport=5353, dport=5353, data=b"background")
    udp.ulen = len(udp)
    ip = dpkt.ip.IP(
        src=socket.inet_aton("192.168.0.129"),
        dst=socket.inet_aton("224.0.0.251"),
        p=dpkt.ip.IP_PROTO_UDP,
        ttl=1,
        data=udp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x01\x00\x5e\x00\x00\xfb",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def write_udp_packet(
    writer: dpkt.pcap.Writer,
    timestamp: float,
    source: str,
    destination: str,
    sport: int,
    dport: int,
) -> None:
    udp = dpkt.udp.UDP(sport=sport, dport=dport, data=b"attack")
    udp.ulen = len(udp)
    ip = dpkt.ip.IP(
        src=socket.inet_aton(source),
        dst=socket.inet_aton(destination),
        p=dpkt.ip.IP_PROTO_UDP,
        ttl=64,
        data=udp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x06\x07\x08\x09\x0a\x0b",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def write_arp_packet(
    writer: dpkt.pcap.Writer,
    timestamp: float,
    source: str,
    destination: str,
    opcode: int,
) -> None:
    arp = dpkt.arp.ARP(
        op=opcode,
        sha=b"\x00\x01\x02\x03\x04\x05",
        spa=socket.inet_aton(source),
        tha=b"\x00\x00\x00\x00\x00\x00",
        tpa=socket.inet_aton(destination),
    )
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\xff\xff\xff\xff\xff\xff",
        type=dpkt.ethernet.ETH_TYPE_ARP,
        data=arp,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def write_icmp_packet(
    writer: dpkt.pcap.Writer,
    timestamp: float,
    source: str,
    destination: str,
) -> None:
    icmp = dpkt.icmp.ICMP(type=3, code=3, data=b"quoted")
    ip = dpkt.ip.IP(
        src=socket.inet_aton(source),
        dst=socket.inet_aton(destination),
        p=dpkt.ip.IP_PROTO_ICMP,
        ttl=64,
        data=icmp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x06\x07\x08\x09\x0a\x0b",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def write_igmp_packet(
    writer: dpkt.pcap.Writer,
    timestamp: float,
    source: str,
    destination: str,
) -> None:
    ip = dpkt.ip.IP(
        src=socket.inet_aton(source),
        dst=socket.inet_aton(destination),
        p=2,
        ttl=1,
        data=b"\x11\x00\x00\x00\x00\x00\x00\x00",
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\x00\x01\x02\x03\x04\x05",
        dst=b"\x01\x00\x5e\x00\x00\x01",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    writer.writepkt(bytes(ethernet), ts=timestamp)


def make_pair(
    tmp_path: Path,
    second_label: str = "Port_Scanning",
    include_filtered_background: bool = False,
) -> tuple[Path, Path]:
    pcap = tmp_path / "Port Scanning attack.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_packet(writer, 1_637_766_209.1, 1387, 80)
        if include_filtered_background:
            write_background_udp(writer, 1_637_766_209.5)
        write_packet(writer, 1_637_766_210.1, 1387, 80)
        writer.close()
    packet_csv = tmp_path / "Port_Scanning_attack.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "frame.time": "2021 16:03:29.100000000",
                "ip.src_host": "192.168.0.170",
                "ip.dst_host": "192.168.0.128",
                "tcp.srcport": "1387.0",
                "tcp.dstport": "80.0",
                "udp.port": "0.0",
                "Attack_label": "1",
                "Attack_type": "Port_Scanning",
            }
        )
        writer.writerow(
            {
                "frame.time": "2021 16:03:30.100000000",
                "ip.src_host": "192.168.0.170",
                "ip.dst_host": "192.168.0.128",
                "tcp.srcport": "1387.0",
                "tcp.dstport": "80.0",
                "udp.port": "0.0",
                "Attack_label": "1",
                "Attack_type": second_label,
            }
        )
    return pcap, packet_csv


def test_paired_packet_rows_form_one_strict_flow_record(tmp_path: Path) -> None:
    pcap, packet_csv = make_pair(tmp_path)
    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/Port Scanning attack.pcap", 30.0
    )
    assert len(records) == 1
    assert records[0]["fine_label"] == "Port Scanning"
    assert records[0]["family_label"] == "Reconnaissance"
    assert records[0]["binary_label"] == 1
    assert audit["pairing_passed"] is True
    assert audit["counters"]["pcap_packets"] == 2


def test_out_of_order_packet_timestamps_are_normalized(tmp_path: Path) -> None:
    pcap = tmp_path / "Password attacks.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_packet(writer, 1_638_637_137.91, 33990, 80)
        write_packet(writer, 1_638_637_137.84, 33990, 80)
        writer.close()

    packet_csv = tmp_path / "Password_attack.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for frame_time in (
            "2021 00:05:37.910000000",
            "2021 00:05:37.840000000",
        ):
            writer.writerow(
                {
                    "frame.time": frame_time,
                    "ip.src_host": "192.168.0.170",
                    "ip.dst_host": "192.168.0.128",
                    "tcp.srcport": "33990.0",
                    "tcp.dstport": "80.0",
                    "udp.port": "0.0",
                    "Attack_label": "1",
                    "Attack_type": "Password",
                }
            )

    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/Password attacks.pcap", 30.0
    )

    assert len(records) == 1
    assert records[0]["start_ns"] < records[0]["end_ns"]
    assert audit["counters"]["pcap_timestamp_regressions_within_flow"] == 1


def test_packet_label_conflict_is_rejected(tmp_path: Path) -> None:
    pcap, packet_csv = make_pair(tmp_path, second_label="Backdoor")
    with pytest.raises(ValueError, match="labels conflict"):
        paired_records(
            pcap, packet_csv, "Attack traffic/Port Scanning attack.pcap", 30.0
        )


def test_filtered_background_packet_does_not_shift_official_rows(tmp_path: Path) -> None:
    pcap, packet_csv = make_pair(tmp_path, include_filtered_background=True)
    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/Port Scanning attack.pcap", 30.0
    )
    assert len(records) == 1
    assert audit["counters"]["official_csv_rows_consumed"] == 2
    assert audit["counters"][
        "pcap_unpaired_ip_identity_or_time_protocol::17"
    ] == 1


def test_verified_shifted_udp_layout_retains_official_rows(tmp_path: Path) -> None:
    pcap = tmp_path / "DDoS UDP Flood Attacks.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_udp_packet(
            writer, 1_637_792_830.1, "10.0.0.1", "192.168.0.128", 9999, 53
        )
        write_udp_packet(
            writer, 1_637_792_830.2, "255.16.17.190", "192.168.0.128", 12912, 0
        )
        write_udp_packet(
            writer, 1_637_792_830.3, "249.66.134.149", "192.168.0.128", 12913, 0
        )
        writer.close()

    packet_csv = tmp_path / "DDoS_UDP_Flood_attack.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for source, sport in (
            ("255.16.17.190", 12912),
            ("249.66.134.149", 12913),
        ):
            writer.writerow(
                {
                    "frame.time": source,
                    "ip.src_host": "192.168.0.128",
                    "ip.dst_host": "0",
                    "tcp.srcport": str(sport),
                    "tcp.dstport": "0.0",
                    "udp.port": "0.0",
                    "Attack_label": "1",
                    "Attack_type": "DDoS_UDP",
                }
            )

    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/DDoS UDP Flood Attacks.pcap", 30.0
    )

    assert len(records) == 2
    assert all(record["fine_label"] == "DDoS UDP" for record in records)
    assert audit["pairing_passed"] is True
    assert audit["official_csv_layout"] == "official_shifted_no_timestamp_ip_v1"
    assert audit["official_frame_clock_offset_from_pcap_ns"] is None
    assert audit["counters"]["official_csv_rows_consumed"] == 2
    assert audit["counters"][
        "official_csv_shifted_no_timestamp_udp_ip_rows_consumed"
    ] == 2
    assert audit["official_row_exclusion_summary"]["excluded_rows"] == 0
    assert audit["official_row_exclusion_summary"]["excluded_fraction"] == 0.0


def test_shifted_udp_layout_strictly_consumes_and_excludes_official_arp(
    tmp_path: Path,
) -> None:
    pcap = tmp_path / "DDoS UDP Flood Attacks.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_udp_packet(
            writer, 1_637_792_830.1, "255.16.17.190", "192.168.0.128", 12912, 0
        )
        write_igmp_packet(
            writer, 1_637_792_830.12, "0.0.0.0", "224.0.0.1"
        )
        write_icmp_packet(
            writer, 1_637_792_830.15, "192.168.0.128", "255.16.17.190"
        )
        write_arp_packet(
            writer, 1_637_792_830.2, "192.168.0.128", "192.168.0.1", 1
        )
        write_udp_packet(
            writer, 1_637_792_830.3, "249.66.134.149", "192.168.0.128", 12913, 0
        )
        writer.close()

    packet_csv = tmp_path / "DDoS_UDP_Flood_attack.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "frame.time": "255.16.17.190",
                "ip.src_host": "192.168.0.128",
                "ip.dst_host": "0",
                "tcp.srcport": "12912.0",
                "tcp.dstport": "0.0",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )
        writer.writerow(
            {
                "frame.time": "0.0.0.0",
                "ip.src_host": "224.0.0.1",
                "ip.dst_host": "0",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )
        writer.writerow(
            {
                "frame.time": "192.168.0.128",
                "ip.src_host": "255.16.17.190",
                "ip.dst_host": "255.16.17.190",
                "icmp.seq_le": "0x00000000",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )
        writer.writerow(
            {
                "frame.time": "0",
                "ip.src_host": "0",
                "ip.dst_host": "192.168.0.1",
                "arp.dst.proto_ipv4": "1.0",
                "arp.opcode": "6.0",
                "arp.hw.size": "192.168.0.128",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )
        writer.writerow(
            {
                "frame.time": "0",
                "ip.src_host": "0",
                "ip.dst_host": "0",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )
        writer.writerow(
            {
                "frame.time": "249.66.134.149",
                "ip.src_host": "192.168.0.128",
                "ip.dst_host": "0",
                "tcp.srcport": "12913.0",
                "tcp.dstport": "0.0",
                "Attack_label": "1",
                "Attack_type": "DDoS_UDP",
            }
        )

    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/DDoS UDP Flood Attacks.pcap", 30.0
    )

    assert len(records) == 4
    assert {record["protocol"] for record in records} == {1, 2, 17}
    assert audit["pairing_passed"] is True
    assert audit["counters"][
        "official_csv_shifted_no_timestamp_icmp_ip_rows_consumed"
    ] == 1
    assert audit["counters"][
        "official_csv_shifted_no_timestamp_igmp_ip_rows_consumed"
    ] == 1
    assert audit["counters"]["official_csv_shifted_arp_rows_consumed"] == 1
    assert audit["counters"][
        "official_csv_unidentifiable_non_ip_rows_consumed"
    ] == 1
    exclusions = audit["official_row_exclusion_summary"]
    assert exclusions["excluded_rows"] == 2
    assert exclusions["excluded_fraction"] == 1 / 3
    assert exclusions["reason_counts"] == {
        "official_arp_row_without_ip_five_tuple": 1,
        "official_row_without_any_join_identity": 1,
    }


def test_mitm_order_only_layout_requires_equal_packet_cardinality(
    tmp_path: Path,
) -> None:
    pcap = tmp_path / "MITM (ARP spoofing + DNS) Attack.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_udp_packet(
            writer, 1_638_035_454.1, "192.168.0.128", "224.0.0.251", 5353, 5353
        )
        write_arp_packet(
            writer, 1_638_035_454.2, "192.168.0.152", "192.168.0.128", 1
        )
        writer.close()

    packet_csv = tmp_path / "MITM_attack.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "frame.time": "0.0",
                "ip.src_host": "0",
                "ip.dst_host": "0.0",
                "tcp.srcport": "_ipps._tcp.local",
                "udp.port": "_ipp._tcp.local",
                "Attack_label": "1",
                "Attack_type": "MITM",
            }
        )
        writer.writerow(
            {
                "frame.time": "6.0",
                "ip.src_host": "192.168.0.152",
                "ip.dst_host": "0.0",
                "Attack_label": "1",
                "Attack_type": "MITM",
            }
        )

    records, audit = paired_records(
        pcap, packet_csv, "Attack traffic/MITM (ARP spoofing + DNS) Attack.pcap", 30.0
    )

    assert len(records) == 1
    assert records[0]["fine_label"] == "MITM"
    assert records[0]["family_label"] == "Man-in-the-Middle"
    assert audit["pairing_passed"] is True
    assert audit["official_csv_layout"] == "official_packet_order_only_mitm_v1"
    assert audit["packet_order_cardinality_passed"] is True
    assert audit["official_row_exclusion_summary"]["excluded_rows"] == 1
    assert audit["official_row_exclusion_summary"]["reason_counts"] == {
        "official_mitm_non_ip_row_without_five_tuple": 1
    }


def test_shifted_modbus_layout_matches_ports_across_mislabeled_columns(
    tmp_path: Path,
) -> None:
    pcap = tmp_path / "Modbus.pcap"
    with pcap.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, nano=True)
        write_background_udp(writer, 1_639_959_767.9)
        write_udp_packet(
            writer, 1_639_959_768.0, "192.168.0.128", "192.168.0.1", 55764, 53
        )
        writer.close()

    packet_csv = tmp_path / "Modbus.csv"
    with packet_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "frame.time": "192.168.0.128",
                "ip.src_host": "192.168.0.1",
                "ip.dst_host": "0",
                "tcp.srcport": "55764.0",
                "tcp.dstport": "0",
                "udp.port": "53.0",
                "icmp.unused": "inf",
                "Attack_label": "0",
                "Attack_type": "Normal",
            }
        )

    records, audit = paired_records(
        pcap, packet_csv, "Normal traffic/Modbus/Modbus.pcap", 30.0
    )

    assert len(records) == 1
    assert records[0]["binary_label"] == 0
    assert records[0]["fine_label"] == "Benign"
    assert audit["pairing_passed"] is True
    assert audit["official_csv_layout"] == "official_shifted_no_timestamp_ip_v1"
    assert audit["counters"][
        "official_csv_shifted_no_timestamp_udp_ip_rows_consumed"
    ] == 1

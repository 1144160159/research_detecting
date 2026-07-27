from __future__ import annotations

import io
import unittest

import dpkt

from create_parrot2025_no_decryption_canary_protocol import (
    feature_columns,
    select_captures,
)
from extract_parrot2025_no_decryption_canary import convert_sll2_to_ethernet


class Parrot2025NoDecryptionCanaryTests(unittest.TestCase):
    def test_feature_contract_preserves_modality_and_column_order(self) -> None:
        config = {
            "modalities": {
                "volume": ["a", "b"],
                "timing": ["c"],
                "transport": ["d", "e"],
            }
        }
        self.assertEqual(feature_columns(config), ["a", "b", "c", "d", "e"])

    def test_selects_smallest_capture_from_four_distinct_apps(self) -> None:
        captures = [
            self.capture("app-a", "a-large.pcap", 100),
            self.capture("app-a", "a-small.pcap", 20),
            self.capture("app-b", "b.pcap", 30),
            self.capture("app-c", "c.pcap", 40),
            self.capture("app-d", "d.pcap", 50),
            self.capture("app-e", "e.pcap", 60),
        ]
        selected = select_captures(captures, 4)
        self.assertEqual(
            [item["member"] for item in selected],
            ["a-small.pcap", "b.pcap", "c.pcap", "d.pcap"],
        )
        self.assertEqual(len({item["application"] for item in selected}), 4)

    def test_sll2_conversion_keeps_only_ip_packets(self) -> None:
        source = io.BytesIO()
        writer = dpkt.pcap.Writer(source, linktype=dpkt.pcap.DLT_LINUX_SLL2)
        writer.writepkt(self.sll2_packet(dpkt.ethernet.ETH_TYPE_IP), 1.0)
        writer.writepkt(self.sll2_packet(dpkt.ethernet.ETH_TYPE_ARP), 2.0)
        source.seek(0)
        destination = io.BytesIO()
        stats = convert_sll2_to_ethernet(source, destination)
        self.assertEqual(
            stats,
            {
                "input_packets": 2,
                "converted_ip_packets": 1,
                "skipped_non_ip_packets": 1,
                "malformed_packets": 0,
            },
        )
        destination.seek(0)
        reader = dpkt.pcap.Reader(destination)
        packets = list(reader)
        self.assertEqual(reader.datalink(), dpkt.pcap.DLT_EN10MB)
        self.assertEqual(len(packets), 1)
        ethernet = dpkt.ethernet.Ethernet(packets[0][1])
        self.assertEqual(ethernet.type, dpkt.ethernet.ETH_TYPE_IP)
        self.assertEqual(ethernet.src, b"\x00" * 6)
        self.assertEqual(ethernet.dst, b"\x00" * 6)

    @staticmethod
    def capture(app: str, member: str, size: int) -> dict[str, object]:
        return {
            "app": app,
            "pcap": member,
            "pcap_size_bytes": size,
            "pcap_crc32": "00000000",
            "pcap_header": {"linktype": dpkt.pcap.DLT_LINUX_SLL2},
        }

    @staticmethod
    def sll2_packet(ethertype: int) -> bytes:
        header = (
            int(ethertype).to_bytes(2, "big")
            + b"\x00\x00"
            + b"\x00\x00\x00\x01"
            + b"\x00\x01"
            + b"\x00"
            + b"\x06"
            + b"\x00" * 8
        )
        if ethertype == dpkt.ethernet.ETH_TYPE_IP:
            payload = bytes(
                dpkt.ip.IP(
                    src=b"\x7f\x00\x00\x01",
                    dst=b"\x7f\x00\x00\x01",
                    p=dpkt.ip.IP_PROTO_TCP,
                    data=dpkt.tcp.TCP(sport=1, dport=2),
                )
            )
        else:
            payload = b"\x00" * 28
        return header + payload


if __name__ == "__main__":
    unittest.main()

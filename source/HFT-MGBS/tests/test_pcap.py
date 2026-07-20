import io
import socket
import struct
import unittest

from hft_mgbs.pcap import PcapFormatError, PcapReader


def ipv4_tcp_frame(payload=b"abc", vlan=False):
    ethernet = b"\x00" * 12
    if vlan:
        ethernet += struct.pack("!HHH", 0x8100, 1, 0x0800)
    else:
        ethernet += struct.pack("!H", 0x0800)
    tcp = struct.pack("!HHIIHHHH", 12345, 443, 0, 0, (5 << 12) | 0x18, 1024, 0, 0)
    total_length = 20 + len(tcp) + len(payload)
    ip = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        total_length,
        1,
        0,
        64,
        6,
        0,
        socket.inet_aton("10.0.0.1"),
        socket.inet_aton("10.0.0.2"),
    )
    return ethernet + ip + tcp + payload


def pcap_bytes(frames):
    content = bytearray(b"\xd4\xc3\xb2\xa1")
    content.extend(struct.pack("<HHiIII", 2, 4, 0, 0, 65535, 1))
    for index, frame in enumerate(frames):
        content.extend(struct.pack("<IIII", 1, index * 1000, len(frame), len(frame)))
        content.extend(frame)
    return bytes(content)


class PcapReaderTests(unittest.TestCase):
    def test_streams_tcp_packet_and_caps_payload(self):
        reader = PcapReader(io.BytesIO(pcap_bytes([ipv4_tcp_frame(b"abcdef")])) , max_payload_bytes=3)
        packet = next(reader)
        self.assertEqual(packet.src_ip, "10.0.0.1")
        self.assertEqual(packet.dst_port, 443)
        self.assertEqual(packet.tcp_flags, 0x18)
        self.assertEqual(packet.payload, b"abc")
        self.assertEqual(reader.stats.parsed_packets, 1)

    def test_supports_vlan(self):
        packet = next(PcapReader(io.BytesIO(pcap_bytes([ipv4_tcp_frame(vlan=True)]))))
        self.assertEqual(packet.protocol, 6)

    def test_skips_non_ip_without_counting_it_as_malformed(self):
        arp = b"\x00" * 12 + struct.pack("!H", 0x0806) + b"\x00" * 28
        reader = PcapReader(io.BytesIO(pcap_bytes([arp, ipv4_tcp_frame()])))
        packet = next(reader)
        self.assertEqual(packet.dst_port, 443)
        self.assertEqual(reader.stats.skipped_non_ip, 1)
        self.assertEqual(reader.stats.malformed_packets, 0)

    def test_rejects_pcapng_or_unknown_magic(self):
        with self.assertRaises(PcapFormatError):
            PcapReader(io.BytesIO(b"\x0a\x0d\x0d\x0a" + b"\x00" * 20))


if __name__ == "__main__":
    unittest.main()

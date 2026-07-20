"""Streaming classic-PCAP reader for the HFT-MGBS correctness/performance path."""

from __future__ import annotations

import socket
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator, Optional

from .features import PacketRecord


@dataclass
class PcapReadStats:
    total_records: int = 0
    parsed_packets: int = 0
    skipped_non_ip: int = 0
    skipped_unsupported: int = 0
    truncated_records: int = 0
    malformed_packets: int = 0

    @property
    def rejected_records(self) -> int:
        return (
            self.skipped_non_ip
            + self.skipped_unsupported
            + self.truncated_records
            + self.malformed_packets
        )


class PcapFormatError(ValueError):
    pass


class PcapReader(Iterator[PacketRecord]):
    """Read Ethernet/IPv4/TCP-or-UDP packets without loading the capture into memory."""

    _MAGIC = {
        b"\xd4\xc3\xb2\xa1": ("<", 1_000_000.0),
        b"\xa1\xb2\xc3\xd4": (">", 1_000_000.0),
        b"\x4d\x3c\xb2\xa1": ("<", 1_000_000_000.0),
        b"\xa1\xb2\x3c\x4d": (">", 1_000_000_000.0),
    }

    def __init__(self, handle: BinaryIO, max_payload_bytes: int = 256) -> None:
        if max_payload_bytes < 0:
            raise ValueError("max_payload_bytes cannot be negative")
        self.handle = handle
        self.max_payload_bytes = max_payload_bytes
        self.stats = PcapReadStats()
        self.endian, self.timestamp_scale, self.link_type = self._read_global_header()

    def _read_global_header(self):
        magic = self.handle.read(4)
        if magic not in self._MAGIC:
            raise PcapFormatError("unsupported or missing classic-PCAP magic")
        endian, scale = self._MAGIC[magic]
        remainder = self.handle.read(20)
        if len(remainder) != 20:
            raise PcapFormatError("truncated PCAP global header")
        major, minor, _, _, _, link_type = struct.unpack(endian + "HHiIII", remainder)
        if major != 2 or minor != 4:
            raise PcapFormatError("unsupported PCAP version {}.{}".format(major, minor))
        if link_type != 1:
            raise PcapFormatError("only Ethernet link type is supported, got {}".format(link_type))
        return endian, scale, link_type

    def __iter__(self) -> "PcapReader":
        return self

    def __next__(self) -> PacketRecord:
        while True:
            header = self.handle.read(16)
            if not header:
                raise StopIteration
            if len(header) != 16:
                self.stats.truncated_records += 1
                raise StopIteration
            ts_sec, ts_fraction, captured_length, original_length = struct.unpack(
                self.endian + "IIII", header
            )
            frame = self.handle.read(captured_length)
            self.stats.total_records += 1
            if len(frame) != captured_length:
                self.stats.truncated_records += 1
                raise StopIteration
            timestamp = ts_sec + ts_fraction / self.timestamp_scale
            try:
                packet = self._parse_ethernet_ipv4(
                    frame, timestamp=timestamp, wire_length=original_length
                )
            except (IndexError, struct.error, ValueError):
                self.stats.malformed_packets += 1
                continue
            if packet is None:
                continue
            self.stats.parsed_packets += 1
            return packet

    def _parse_ethernet_ipv4(
        self, frame: bytes, timestamp: float, wire_length: int
    ) -> Optional[PacketRecord]:
        if len(frame) < 14:
            raise ValueError("truncated Ethernet header")
        offset = 14
        ether_type = struct.unpack_from("!H", frame, 12)[0]
        vlan_depth = 0
        while ether_type in (0x8100, 0x88A8):
            if len(frame) < offset + 4 or vlan_depth >= 2:
                raise ValueError("invalid VLAN header")
            ether_type = struct.unpack_from("!H", frame, offset + 2)[0]
            offset += 4
            vlan_depth += 1
        if ether_type != 0x0800:
            self.stats.skipped_non_ip += 1
            return None
        if len(frame) < offset + 20:
            raise ValueError("truncated IPv4 header")
        version_ihl = frame[offset]
        version, ihl = version_ihl >> 4, (version_ihl & 0x0F) * 4
        if version != 4 or ihl < 20 or len(frame) < offset + ihl:
            raise ValueError("invalid IPv4 header")
        total_length = struct.unpack_from("!H", frame, offset + 2)[0]
        if total_length < ihl:
            raise ValueError("invalid IPv4 total length")
        flags_fragment = struct.unpack_from("!H", frame, offset + 6)[0]
        if flags_fragment & 0x1FFF:
            self.stats.skipped_unsupported += 1
            return None
        protocol = frame[offset + 9]
        src_ip = socket.inet_ntoa(frame[offset + 12 : offset + 16])
        dst_ip = socket.inet_ntoa(frame[offset + 16 : offset + 20])
        ip_end = min(len(frame), offset + total_length)
        transport_offset = offset + ihl
        if protocol == 6:
            if ip_end < transport_offset + 20:
                raise ValueError("truncated TCP header")
            src_port, dst_port = struct.unpack_from("!HH", frame, transport_offset)
            tcp_header_length = (frame[transport_offset + 12] >> 4) * 4
            if tcp_header_length < 20 or ip_end < transport_offset + tcp_header_length:
                raise ValueError("invalid TCP header length")
            tcp_flags = frame[transport_offset + 13]
            payload_offset = transport_offset + tcp_header_length
        elif protocol == 17:
            if ip_end < transport_offset + 8:
                raise ValueError("truncated UDP header")
            src_port, dst_port = struct.unpack_from("!HH", frame, transport_offset)
            tcp_flags = 0
            payload_offset = transport_offset + 8
        else:
            self.stats.skipped_unsupported += 1
            return None
        payload = frame[payload_offset:ip_end]
        payload_length = len(payload)
        if self.max_payload_bytes:
            payload = payload[: self.max_payload_bytes]
        else:
            payload = b""
        return PacketRecord(
            timestamp=timestamp,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            wire_length=wire_length,
            payload=payload,
            tcp_flags=tcp_flags,
            payload_length=payload_length,
        )


class PcapFileReader(PcapReader):
    def __init__(self, path: Path, max_payload_bytes: int = 256) -> None:
        self.path = Path(path)
        self._owned_handle = self.path.open("rb")
        try:
            super().__init__(self._owned_handle, max_payload_bytes=max_payload_bytes)
        except Exception:
            self._owned_handle.close()
            raise

    def close(self) -> None:
        self._owned_handle.close()

    def __enter__(self) -> "PcapFileReader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

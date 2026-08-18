#!/usr/bin/env python3
"""Normalize a compatible multi-interface PCAPNG to classic PCAP.

The source is never modified.  A repair-manifest entry is published only after
an ordered, packet-level fingerprint and a full tshark scan both pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path
from typing import Any, BinaryIO


PCAP_MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("<", 1_000_000),
    b"\xa1\xb2\xc3\xd4": (">", 1_000_000),
    b"\x4d\x3c\xb2\xa1": ("<", 1_000_000_000),
    b"\xa1\xb2\x3c\x4d": (">", 1_000_000_000),
}
PCAPNG_SHB = 0x0A0D0D0A
PCAPNG_IDB = 0x00000001
PCAPNG_PB = 0x00000002
PCAPNG_SPB = 0x00000003
PCAPNG_EPB = 0x00000006


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


class PacketFingerprint:
    def __init__(self) -> None:
        self.digest = hashlib.sha256()
        self.packet_count = 0
        self.captured_bytes = 0
        self.wire_bytes = 0
        self.minimum_timestamp_ns: int | None = None
        self.maximum_timestamp_ns: int | None = None

    def add(
        self, timestamp_ns: int, captured_length: int, wire_length: int, packet: bytes
    ) -> None:
        if len(packet) != captured_length:
            raise ValueError("captured length does not match packet bytes")
        self.digest.update(struct.pack(">qII", timestamp_ns, captured_length, wire_length))
        self.digest.update(packet)
        self.packet_count += 1
        self.captured_bytes += captured_length
        self.wire_bytes += wire_length
        if self.minimum_timestamp_ns is None or timestamp_ns < self.minimum_timestamp_ns:
            self.minimum_timestamp_ns = timestamp_ns
        if self.maximum_timestamp_ns is None or timestamp_ns > self.maximum_timestamp_ns:
            self.maximum_timestamp_ns = timestamp_ns

    def result(self) -> dict[str, Any]:
        return {
            "packet_count": self.packet_count,
            "captured_bytes": self.captured_bytes,
            "wire_bytes": self.wire_bytes,
            "minimum_timestamp_ns": self.minimum_timestamp_ns,
            "maximum_timestamp_ns": self.maximum_timestamp_ns,
            "ordered_packet_sha256": self.digest.hexdigest(),
        }


def read_exact(handle: BinaryIO, size: int) -> bytes:
    value = handle.read(size)
    if len(value) != size:
        raise ValueError(f"truncated capture: expected {size} bytes, got {len(value)}")
    return value


def pcap_fingerprint(path: Path) -> dict[str, Any]:
    fingerprint = PacketFingerprint()
    with path.open("rb") as handle:
        header = read_exact(handle, 24)
        try:
            endian, timestamp_denominator = PCAP_MAGIC[header[:4]]
        except KeyError as exc:
            raise ValueError("not a classic PCAP") from exc
        _, _, _, _, snaplen, linktype = struct.unpack(f"{endian}HHIIII", header[4:])
        while True:
            record = handle.read(16)
            if not record:
                break
            if len(record) != 16:
                raise ValueError("truncated PCAP record header")
            seconds, fraction, captured_length, wire_length = struct.unpack(
                f"{endian}IIII", record
            )
            scaled = fraction * 1_000_000_000
            if scaled % timestamp_denominator:
                raise ValueError("PCAP timestamp cannot be represented exactly in nanoseconds")
            timestamp_ns = seconds * 1_000_000_000 + scaled // timestamp_denominator
            fingerprint.add(
                timestamp_ns,
                captured_length,
                wire_length,
                read_exact(handle, captured_length),
            )
    result = fingerprint.result()
    result.update(
        {
            "format": "pcap",
            "linktypes": [linktype],
            "snaplens": [snaplen],
            "timestamp_denominators": [timestamp_denominator],
        }
    )
    return result


def parse_idb_options(data: bytes, endian: str) -> tuple[int, int]:
    denominator = 1_000_000
    timestamp_offset_seconds = 0
    cursor = 0
    while cursor + 4 <= len(data):
        code, length = struct.unpack(f"{endian}HH", data[cursor : cursor + 4])
        cursor += 4
        if code == 0:
            break
        value = data[cursor : cursor + length]
        if len(value) != length:
            raise ValueError("truncated PCAPNG interface option")
        cursor += (length + 3) & ~3
        if code == 9 and length == 1:
            resolution = value[0]
            denominator = (
                2 ** (resolution & 0x7F)
                if resolution & 0x80
                else 10 ** resolution
            )
        elif code == 14 and length == 8:
            timestamp_offset_seconds = struct.unpack(f"{endian}q", value)[0]
    return denominator, timestamp_offset_seconds


def timestamp_ns(raw: int, denominator: int, offset_seconds: int) -> int:
    scaled = raw * 1_000_000_000
    if scaled % denominator:
        raise ValueError("PCAPNG timestamp cannot be represented exactly in nanoseconds")
    return offset_seconds * 1_000_000_000 + scaled // denominator


def pcapng_fingerprint(path: Path) -> dict[str, Any]:
    fingerprint = PacketFingerprint()
    interfaces: list[dict[str, int]] = []
    all_interfaces: list[dict[str, int]] = []
    endian: str | None = None
    with path.open("rb") as handle:
        while True:
            prefix = handle.read(12)
            if not prefix:
                break
            if len(prefix) != 12:
                raise ValueError("truncated PCAPNG block header")
            if prefix[:4] == struct.pack("<I", PCAPNG_SHB):
                byte_order_magic = prefix[8:12]
                if byte_order_magic == b"\x4d\x3c\x2b\x1a":
                    endian = "<"
                elif byte_order_magic == b"\x1a\x2b\x3c\x4d":
                    endian = ">"
                else:
                    raise ValueError("invalid PCAPNG byte-order magic")
                block_type = PCAPNG_SHB
                block_length = struct.unpack(f"{endian}I", prefix[4:8])[0]
                interfaces = []
            else:
                if endian is None:
                    raise ValueError("PCAPNG does not start with a section header")
                block_type, block_length = struct.unpack(f"{endian}II", prefix[:8])
            if block_length < 12 or block_length % 4:
                raise ValueError(f"invalid PCAPNG block length: {block_length}")
            block = prefix + read_exact(handle, block_length - 12)
            if struct.unpack(f"{endian}I", block[-4:])[0] != block_length:
                raise ValueError("PCAPNG block length trailer mismatch")
            if block_type == PCAPNG_IDB:
                linktype, _, snaplen = struct.unpack(f"{endian}HHI", block[8:16])
                denominator, offset = parse_idb_options(block[16:-4], endian)
                interface = {
                    "linktype": linktype,
                    "snaplen": snaplen,
                    "timestamp_denominator": denominator,
                    "timestamp_offset_seconds": offset,
                }
                interfaces.append(interface)
                all_interfaces.append(interface)
            elif block_type in {PCAPNG_EPB, PCAPNG_PB}:
                if block_type == PCAPNG_EPB:
                    interface_id, high, low, captured_length, wire_length = struct.unpack(
                        f"{endian}IIIII", block[8:28]
                    )
                else:
                    interface_id, _, high, low, captured_length, wire_length = struct.unpack(
                        f"{endian}HHIIII", block[8:28]
                    )
                try:
                    interface = interfaces[interface_id]
                except IndexError as exc:
                    raise ValueError(f"undefined PCAPNG interface: {interface_id}") from exc
                packet = block[28 : 28 + captured_length]
                raw_timestamp = (high << 32) | low
                fingerprint.add(
                    timestamp_ns(
                        raw_timestamp,
                        interface["timestamp_denominator"],
                        interface["timestamp_offset_seconds"],
                    ),
                    captured_length,
                    wire_length,
                    packet,
                )
            elif block_type == PCAPNG_SPB:
                raise ValueError("simple packet blocks lack timestamps and are not normalizable")
    if not all_interfaces:
        raise ValueError("PCAPNG contains no interface descriptions")
    result = fingerprint.result()
    result.update(
        {
            "format": "pcapng",
            "interface_count": len(all_interfaces),
            "linktypes": sorted({item["linktype"] for item in all_interfaces}),
            "snaplens": sorted({item["snaplen"] for item in all_interfaces}),
            "timestamp_denominators": sorted(
                {item["timestamp_denominator"] for item in all_interfaces}
            ),
            "interfaces": all_interfaces,
        }
    )
    return result


def capture_fingerprint(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        magic = handle.read(4)
    if magic in PCAP_MAGIC:
        return pcap_fingerprint(path)
    if magic == struct.pack("<I", PCAPNG_SHB):
        return pcapng_fingerprint(path)
    raise ValueError(f"unsupported capture format: {path}")


def packet_fields(fingerprint: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "packet_count",
        "captured_bytes",
        "wire_bytes",
        "minimum_timestamp_ns",
        "maximum_timestamp_ns",
        "ordered_packet_sha256",
    )
    return {key: fingerprint[key] for key in keys}


def run_text(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--editcap", default="editcap")
    parser.add_argument("--capinfos", default="capinfos")
    parser.add_argument("--tshark", default="tshark")
    args = parser.parse_args()

    source = args.source.resolve()
    original_sha256 = sha256_file(source)
    source_fingerprint = capture_fingerprint(source)
    if source_fingerprint["format"] != "pcapng":
        raise ValueError("source is not PCAPNG")
    if len(source_fingerprint["linktypes"]) != 1:
        raise ValueError(
            "PCAPNG interfaces use different link types and cannot be flattened to PCAP"
        )

    args.output_root.mkdir(parents=True, exist_ok=True)
    repaired = args.output_root / f"{original_sha256}.normalized.pcap"
    partial = repaired.with_suffix(repaired.suffix + ".partial")
    if repaired.exists() or partial.exists():
        raise FileExistsError(repaired if repaired.exists() else partial)

    conversion = run_text([args.editcap, "-F", "pcap", str(source), str(partial)])
    if conversion.returncode != 0:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"editcap failed: {conversion.stderr[-2000:]}")
    try:
        repaired_fingerprint = capture_fingerprint(partial)
        if source_fingerprint["linktypes"] != repaired_fingerprint["linktypes"]:
            raise RuntimeError("editcap changed the packet link type")
        if packet_fields(source_fingerprint) != packet_fields(repaired_fingerprint):
            raise RuntimeError("editcap changed ordered packet bytes or packet metadata")

        capinfos_source = run_text(
            [args.capinfos, "-I", "-c", "-s", "-d", "-a", "-e", str(source)]
        )
        capinfos_repaired = run_text(
            [args.capinfos, "-I", "-c", "-s", "-d", "-a", "-e", str(partial)]
        )
        scan = subprocess.run(
            [
                args.tshark,
                "-n",
                "-r",
                str(partial),
                "-T",
                "fields",
                "-e",
                "frame.number",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if capinfos_source.returncode or capinfos_repaired.returncode or scan.returncode:
            raise RuntimeError(
                "normalized PCAP validation failed: "
                f"source_capinfos={capinfos_source.returncode}, "
                f"repaired_capinfos={capinfos_repaired.returncode}, "
                f"tshark={scan.returncode}, stderr={scan.stderr[-1000:]}"
            )
        repaired_sha256 = sha256_file(partial)
        repaired_size = partial.stat().st_size
        os.replace(partial, repaired)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

    editcap_identity = run_text([args.editcap, "--version"])
    entry = {
        "dataset_id": args.dataset_id,
        "source_path": str(source),
        "source_member": None,
        "original_sha256": original_sha256,
        "original_size_bytes": source.stat().st_size,
        "repaired_path": str(repaired),
        "repaired_sha256": repaired_sha256,
        "repaired_size_bytes": repaired_size,
        "repair_tool": editcap_identity.stdout.splitlines()[0],
        "repair_script_sha256": sha256_file(Path(__file__)),
        "repair_mode": "pcapng_to_pcap_same_linktype_ordered_packet_exact",
        "source_capture_fingerprint": source_fingerprint,
        "repaired_capture_fingerprint": repaired_fingerprint,
        "exact_ordered_packets_preserved": True,
        "capinfos_source_validation": capinfos_source.stdout,
        "capinfos_validation": capinfos_repaired.stdout,
        "full_tshark_scan_passed": True,
    }
    manifest = (
        json.loads(args.manifest.read_text(encoding="utf-8"))
        if args.manifest.exists()
        else {"schema_version": "caeos_pcap_repair_manifest_v1", "repairs": []}
    )
    repairs = [
        item
        for item in manifest.get("repairs", [])
        if not (
            item["dataset_id"] == args.dataset_id
            and item["source_path"] == str(source)
            and item.get("source_member") is None
        )
    ]
    repairs.append(entry)
    manifest["repairs"] = sorted(
        repairs,
        key=lambda item: (
            item["dataset_id"],
            item["source_path"],
            item.get("source_member") or "",
        ),
    )
    manifest["repair_count"] = len(manifest["repairs"])
    manifest["all_repairs_fully_validated"] = all(
        item.get("full_tshark_scan_passed", False) for item in manifest["repairs"]
    )
    atomic_json(args.manifest, manifest)
    print(json.dumps(entry, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

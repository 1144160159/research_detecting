from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path
from typing import Any, BinaryIO

try:
    from .validate_splitpcap_integrity import capture_fingerprint
except ImportError:
    from validate_splitpcap_integrity import capture_fingerprint


MAGIC_ENDIAN = {
    b"\xd4\xc3\xb2\xa1": "<",
    b"\xa1\xb2\xc3\xd4": ">",
    b"\x4d\x3c\xb2\xa1": "<",
    b"\xa1\xb2\x3c\x4d": ">",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_prefix(path: Path, length: int) -> str:
    digest = hashlib.sha256()
    remaining = length
    with path.open("rb") as handle:
        while remaining:
            block = handle.read(min(16 * 1024 * 1024, remaining))
            if not block:
                raise EOFError(f"unexpected EOF with {remaining} prefix bytes remaining")
            digest.update(block)
            remaining -= len(block)
    return digest.hexdigest()


def source_identity(
    materialized_source: Path,
    source_container: Path | None = None,
    source_member: str | None = None,
) -> dict[str, Any]:
    if (source_container is None) != (source_member is None):
        raise ValueError("--source-container and --source-member must be supplied together")
    materialized_sha256 = sha256_file(materialized_source)
    if source_container is None:
        return {
            "source_path": str(materialized_source),
            "source_member": None,
            "original_sha256": materialized_sha256,
            "original_size_bytes": materialized_source.stat().st_size,
        }
    if not source_member:
        raise ValueError("--source-member cannot be empty")
    if not source_container.is_file():
        raise FileNotFoundError(source_container)
    return {
        "source_path": str(source_container),
        "source_member": source_member,
        "original_sha256": sha256_file(source_container),
        "original_size_bytes": source_container.stat().st_size,
        "materialized_member_sha256": materialized_sha256,
        "materialized_member_size_bytes": materialized_source.stat().st_size,
    }


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def copy_exact(source: BinaryIO, destination: BinaryIO, length: int) -> None:
    remaining = length
    while remaining:
        block = source.read(min(16 * 1024 * 1024, remaining))
        if not block:
            raise EOFError(f"unexpected EOF with {remaining} bytes remaining")
        destination.write(block)
        remaining -= len(block)


def inspect_truncated_final_record(source: Path) -> dict[str, int | str] | None:
    """Return recoverable final-record details without reading packet payloads."""
    source_size = source.stat().st_size
    packet_count = 0
    with source.open("rb") as handle:
        global_header = handle.read(24)
        if len(global_header) != 24 or global_header[:4] not in MAGIC_ENDIAN:
            return None
        endian = MAGIC_ENDIAN[global_header[:4]]
        snaplen = struct.unpack(f"{endian}I", global_header[16:20])[0]
        while handle.tell() < source_size:
            record_offset = handle.tell()
            header = handle.read(16)
            if len(header) != 16:
                if header and handle.tell() == source_size:
                    return {
                        "repair_kind": "drop_incomplete_final_record_header",
                        "record_header_offset": record_offset,
                        "packet_number": packet_count + 1,
                        "trailing_header_bytes_removed": len(header),
                    }
                raise ValueError("truncated PCAP record header")
            ts_sec, ts_fraction, captured_length, original_length = struct.unpack(
                f"{endian}IIII", header
            )
            available = source_size - handle.tell()
            packet_count += 1
            if captured_length > snaplen or captured_length > original_length:
                return {
                    "repair_kind": "pcapfix_deep_scan_required",
                    "record_header_offset": record_offset,
                    "packet_number": packet_count,
                    "declared_captured_length": captured_length,
                    "original_wire_length": original_length,
                    "global_snaplen": snaplen,
                }
            if captured_length <= available:
                handle.seek(captured_length, os.SEEK_CUR)
                continue
            if available <= 0 or available > original_length:
                raise ValueError("PCAP truncation is not a recoverable final record")
            return {
                "repair_kind": "correct_final_record_captured_length",
                "record_header_offset": record_offset,
                "packet_number": packet_count,
                "timestamp_seconds": ts_sec,
                "timestamp_fraction": ts_fraction,
                "declared_captured_length": captured_length,
                "corrected_captured_length": available,
                "original_wire_length": original_length,
            }
    return None


def repair_final_record(source: Path, destination: Path) -> dict[str, int | str]:
    source_size = source.stat().st_size
    temporary = destination.with_suffix(destination.suffix + ".partial")
    temporary.unlink(missing_ok=True)
    repaired: dict[str, int | str] | None = None
    packet_count = 0
    try:
        with source.open("rb") as src, temporary.open("wb") as dst:
            global_header = src.read(24)
            if len(global_header) != 24 or global_header[:4] not in MAGIC_ENDIAN:
                raise ValueError("unsupported or truncated classic PCAP global header")
            endian = MAGIC_ENDIAN[global_header[:4]]
            dst.write(global_header)
            while src.tell() < source_size:
                record_offset = src.tell()
                header = src.read(16)
                if len(header) != 16:
                    if repaired is not None or not header or src.tell() != source_size:
                        raise ValueError("truncated PCAP record header")
                    repaired = {
                        "repair_kind": "drop_incomplete_final_record_header",
                        "record_header_offset": record_offset,
                        "packet_number": packet_count + 1,
                        "trailing_header_bytes_removed": len(header),
                    }
                    break
                ts_sec, ts_fraction, captured_length, original_length = struct.unpack(
                    f"{endian}IIII", header
                )
                available = source_size - src.tell()
                if captured_length <= available:
                    dst.write(header)
                    copy_exact(src, dst, captured_length)
                    packet_count += 1
                    continue
                if repaired is not None or available <= 0:
                    raise ValueError("PCAP truncation is not a single recoverable final record")
                if available > original_length:
                    raise ValueError("available final bytes exceed the original wire length")
                corrected_header = struct.pack(
                    f"{endian}IIII",
                    ts_sec,
                    ts_fraction,
                    available,
                    original_length,
                )
                dst.write(corrected_header)
                copy_exact(src, dst, available)
                packet_count += 1
                repaired = {
                    "repair_kind": "correct_final_record_captured_length",
                    "record_header_offset": record_offset,
                    "packet_number": packet_count,
                    "timestamp_seconds": ts_sec,
                    "timestamp_fraction": ts_fraction,
                    "declared_captured_length": captured_length,
                    "corrected_captured_length": available,
                    "original_wire_length": original_length,
                }
            if repaired is None:
                raise ValueError("PCAP does not contain a truncated final record")
            dst.flush()
            os.fsync(dst.fileno())
        removed = int(repaired.get("trailing_header_bytes_removed", 0))
        if temporary.stat().st_size != source_size - removed:
            raise ValueError("repair produced an unexpected PCAP file size")
        os.replace(temporary, destination)
        return repaired
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-container", type=Path)
    parser.add_argument("--source-member")
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--tshark", default="/usr/bin/tshark")
    parser.add_argument("--capinfos", default="/usr/bin/capinfos")
    args = parser.parse_args()
    if not args.source.is_file():
        raise FileNotFoundError(args.source)

    args.output_root.mkdir(parents=True, exist_ok=True)
    identity = source_identity(args.source, args.source_container, args.source_member)
    repair_id = hashlib.sha256(
        (
            f"{args.dataset_id}\0{identity['source_path']}\0"
            f"{identity['source_member'] or ''}\0{identity['original_sha256']}\0"
            f"{identity.get('materialized_member_sha256', '')}"
        ).encode("utf-8")
    ).hexdigest()
    repaired = args.output_root / f"{repair_id}.repaired.pcap"
    repair_details = repair_final_record(args.source, repaired)
    repaired_fingerprint = capture_fingerprint([repaired])
    if repair_details.get("repair_kind") == "drop_incomplete_final_record_header":
        if sha256_prefix(args.source, repaired.stat().st_size) != sha256_file(repaired):
            repaired.unlink(missing_ok=True)
            raise RuntimeError("record-header removal changed the valid PCAP prefix")
        original_fingerprint = repaired_fingerprint
        fingerprint_validation = "exact_source_prefix_and_nonpacket_tail_removal"
    else:
        original_fingerprint = capture_fingerprint([args.source])
        if original_fingerprint != repaired_fingerprint:
            repaired.unlink(missing_ok=True)
            raise RuntimeError("record-header repair changed the captured packet multiset")
        fingerprint_validation = "original_and_repaired_packet_fingerprint_equal"

    capinfos = subprocess.run(
        [args.capinfos, "-c", "-s", "-a", "-e", str(repaired)],
        check=False,
        capture_output=True,
        text=True,
    )
    scan = subprocess.run(
        [args.tshark, "-n", "-r", str(repaired), "-T", "fields", "-e", "frame.number"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if capinfos.returncode != 0 or scan.returncode != 0:
        repaired.unlink(missing_ok=True)
        raise RuntimeError(
            f"repaired PCAP validation failed: capinfos={capinfos.returncode}, "
            f"tshark={scan.returncode}, stderr={scan.stderr[-1000:]}"
        )

    entry = {
        "dataset_id": args.dataset_id,
        **identity,
        "repaired_path": str(repaired),
        "repaired_sha256": sha256_file(repaired),
        "repaired_size_bytes": repaired.stat().st_size,
        "repair_tool": "caeos_truncated_final_record_repair_v1",
        "repair_script_sha256": sha256_file(Path(__file__)),
        "repair_mode": "correct_final_record_incl_len_to_available_bytes",
        "repair_details": repair_details,
        "captured_packet_fingerprint": original_fingerprint,
        "fingerprint_validation": fingerprint_validation,
        "exact_captured_packet_multiset_preserved": True,
        "capinfos_validation": capinfos.stdout,
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
            and item["source_path"] == identity["source_path"]
            and item.get("source_member") == identity["source_member"]
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

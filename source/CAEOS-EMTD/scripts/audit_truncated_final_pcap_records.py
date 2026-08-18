from __future__ import annotations

import argparse
import json
import mmap
import os
import struct
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any


MAGIC_ENDIAN = {
    b"\xd4\xc3\xb2\xa1": "<",
    b"\xa1\xb2\xc3\xd4": ">",
    b"\x4d\x3c\xb2\xa1": "<",
    b"\xa1\xb2\x3c\x4d": ">",
}
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"


def inspect_capture(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    result: dict[str, Any] = {
        "path": str(path),
        "size_bytes": size,
        "packet_count": 0,
    }
    if size < 24:
        return {**result, "status": "invalid", "reason": "truncated_global_header"}
    with path.open("rb") as handle, mmap.mmap(
        handle.fileno(), length=0, access=mmap.ACCESS_READ
    ) as data:
        magic = data[:4]
        if magic == PCAPNG_MAGIC:
            scan = subprocess.run(
                ["/usr/bin/capinfos", "-c", "-s", "-a", "-e", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            return {
                **result,
                "status": "valid_pcapng" if scan.returncode == 0 else "invalid_pcapng",
                "capinfos_returncode": scan.returncode,
                "capinfos_output": (scan.stdout + scan.stderr)[-2000:],
            }
        endian = MAGIC_ENDIAN.get(magic)
        if endian is None:
            return {**result, "status": "invalid", "reason": "unsupported_magic"}
        offset = 24
        packet_number = 0
        while offset < size:
            if size - offset < 16:
                return {
                    **result,
                    "status": "invalid",
                    "reason": "truncated_record_header",
                    "record_header_offset": offset,
                    "trailing_bytes": size - offset,
                    "packet_count": packet_number,
                }
            ts_sec, ts_fraction, captured_length, original_length = struct.unpack_from(
                f"{endian}IIII", data, offset
            )
            payload_offset = offset + 16
            available = size - payload_offset
            packet_number += 1
            if captured_length > available:
                return {
                    **result,
                    "status": "truncated_final_record",
                    "packet_count": packet_number,
                    "record_header_offset": offset,
                    "timestamp_seconds": ts_sec,
                    "timestamp_fraction": ts_fraction,
                    "declared_captured_length": captured_length,
                    "available_captured_length": available,
                    "original_wire_length": original_length,
                }
            offset = payload_offset + captured_length
        return {**result, "status": "valid", "packet_count": packet_number}


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not args.root.is_dir():
        raise NotADirectoryError(args.root)
    if args.workers < 1:
        raise ValueError("workers must be positive")
    captures = sorted(
        path
        for path in args.root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pcap", ".cap"}
    )
    if not captures:
        raise ValueError("no classic PCAP files found")
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(inspect_capture, path): path for path in captures}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    results.sort(key=lambda item: item["path"])
    counts: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        counts[status] = counts.get(status, 0) + 1
    report = {
        "schema_version": "caeos_truncated_final_pcap_audit_v1",
        "root": str(args.root),
        "capture_count": len(results),
        "status_counts": dict(sorted(counts.items())),
        "results": results,
        "complete": True,
    }
    atomic_json(args.output, report)
    print(json.dumps({key: report[key] for key in ("capture_count", "status_counts")}, sort_keys=True))


if __name__ == "__main__":
    main()

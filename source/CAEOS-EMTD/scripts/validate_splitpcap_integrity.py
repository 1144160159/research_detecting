from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prepare_caeos_unified_multimodal_csv import open_capture, packet_reader


MODULUS = 1 << 256


def timestamp_nanoseconds(value: Any) -> int:
    return int(Decimal(str(value)) * Decimal(1_000_000_000))


def capture_fingerprint(paths: Iterable[Path]) -> dict[str, Any]:
    count = 0
    captured_bytes = 0
    digest_sum = 0
    digest_xor = 0
    minimum_timestamp_ns = None
    maximum_timestamp_ns = None
    for path in paths:
        with open_capture(path, None) as handle:
            for timestamp, frame in packet_reader(handle):
                frame_bytes = bytes(frame)
                timestamp_ns = timestamp_nanoseconds(timestamp)
                digest = hashlib.sha256(
                    struct.pack(">qI", timestamp_ns, len(frame_bytes)) + frame_bytes
                ).digest()
                value = int.from_bytes(digest, "big")
                digest_sum = (digest_sum + value) % MODULUS
                digest_xor ^= value
                count += 1
                captured_bytes += len(frame_bytes)
                minimum_timestamp_ns = (
                    timestamp_ns
                    if minimum_timestamp_ns is None
                    else min(minimum_timestamp_ns, timestamp_ns)
                )
                maximum_timestamp_ns = (
                    timestamp_ns
                    if maximum_timestamp_ns is None
                    else max(maximum_timestamp_ns, timestamp_ns)
                )
    return {
        "packet_count": count,
        "captured_bytes": captured_bytes,
        "packet_digest_sum": f"{digest_sum:064x}",
        "packet_digest_xor": f"{digest_xor:064x}",
        "minimum_timestamp_ns": minimum_timestamp_ns,
        "maximum_timestamp_ns": maximum_timestamp_ns,
    }


def validate(source: Path, pieces: list[Path]) -> dict[str, Any]:
    if not pieces:
        raise ValueError("splitpcap produced no non-empty pieces")
    original = capture_fingerprint([source])
    split = capture_fingerprint(pieces)
    if original != split:
        raise ValueError(
            "splitpcap packet integrity mismatch: "
            + json.dumps({"source": original, "pieces": split}, sort_keys=True)
        )
    return {
        "schema_version": "caeos_splitpcap_integrity_v1",
        "source": str(source),
        "piece_count": len(pieces),
        "fingerprint": original,
        "exact_multiset_match": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--pieces-dir", required=True, type=Path)
    args = parser.parse_args()
    pieces = sorted(
        path
        for path in args.pieces_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".pcap", ".pcapng"}
        and path.stat().st_size > 24
    )
    print(json.dumps(validate(args.source, pieces), sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from prepare_caeos_unified_multimodal_csv import (
    TSHARK_FIELDS,
    TSHARK_STATE_PREFERENCES,
)


LEGACY_STATE_PREFERENCES = (
    "ip.defragment:FALSE",
    "ipv6.defragment:FALSE",
    "tcp.desegment_tcp_streams:FALSE",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="append", required=True, type=Path)
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    parser.add_argument("--packet-limit", type=int, default=250000)
    parser.add_argument("--optimized-reset-packets", type=int, default=50000)
    return parser.parse_args()


def command(
    capture: Path,
    tshark_binary: str,
    packet_limit: int,
    reset_packets: int,
    preferences: tuple[str, ...],
) -> list[str]:
    result = [
        tshark_binary,
        "-n",
        "-l",
        "-M",
        str(reset_packets),
        "-c",
        str(packet_limit),
    ]
    for preference in preferences:
        result.extend(("-o", preference))
    result.extend(
        (
            "-r",
            str(capture),
            "-T",
            "fields",
            "-E",
            "separator=/t",
            "-E",
            "quote=d",
            "-E",
            "occurrence=a",
            "-E",
            "aggregator=;",
        )
    )
    for field in TSHARK_FIELDS:
        result.extend(("-e", field))
    return result


def run(command_line: list[str], output: Path) -> dict[str, object]:
    with output.open("wb") as stdout, tempfile.TemporaryFile(mode="w+b") as stderr:
        completed = subprocess.run(command_line, stdout=stdout, stderr=stderr)
        if completed.returncode:
            stderr.seek(0, 2)
            size = stderr.tell()
            stderr.seek(max(0, size - 4000))
            message = stderr.read().decode("utf-8", errors="replace")
            raise RuntimeError(message)
    digest = hashlib.sha256()
    lines = 0
    with output.open("rb") as handle:
        for line in handle:
            digest.update(line)
            lines += 1
    return {"sha256": digest.hexdigest(), "lines": lines, "bytes": output.stat().st_size}


def first_difference(baseline: Path, optimized: Path) -> dict[str, object] | None:
    with baseline.open("rb") as left, optimized.open("rb") as right:
        line_number = 0
        while True:
            baseline_line = left.readline()
            optimized_line = right.readline()
            if not baseline_line and not optimized_line:
                return None
            line_number += 1
            if baseline_line != optimized_line:
                baseline_fields = baseline_line.rstrip(b"\r\n").split(b"\t")
                optimized_fields = optimized_line.rstrip(b"\r\n").split(b"\t")
                changed = [
                    TSHARK_FIELDS[index] if index < len(TSHARK_FIELDS) else str(index)
                    for index, values in enumerate(
                        zip(baseline_fields, optimized_fields)
                    )
                    if values[0] != values[1]
                ]
                if len(baseline_fields) != len(optimized_fields):
                    changed.append("field_count")
                return {
                    "line": line_number,
                    "changed_fields": changed,
                    "baseline_field_count": len(baseline_fields),
                    "optimized_field_count": len(optimized_fields),
                }


def main() -> None:
    args = parse_arguments()
    if args.packet_limit < 1 or args.optimized_reset_packets < 1:
        raise ValueError("packet counts must be positive")
    results = []
    with tempfile.TemporaryDirectory(prefix="caeos-tshark-equivalence-") as directory:
        root = Path(directory)
        for index, capture in enumerate(args.capture):
            if not capture.is_file():
                raise FileNotFoundError(capture)
            baseline = root / f"{index}.baseline.tsv"
            optimized = root / f"{index}.optimized.tsv"
            baseline_stats = run(
                command(
                    capture,
                    args.tshark_binary,
                    args.packet_limit,
                    args.packet_limit + 1,
                    LEGACY_STATE_PREFERENCES,
                ),
                baseline,
            )
            optimized_stats = run(
                command(
                    capture,
                    args.tshark_binary,
                    args.packet_limit,
                    args.optimized_reset_packets,
                    TSHARK_STATE_PREFERENCES,
                ),
                optimized,
            )
            difference = first_difference(baseline, optimized)
            result = {
                "capture": str(capture),
                "packet_limit": args.packet_limit,
                "optimized_reset_packets": args.optimized_reset_packets,
                "baseline": baseline_stats,
                "optimized": optimized_stats,
                "exact_selected_field_match": difference is None,
                "first_difference": difference,
            }
            results.append(result)
            if difference is not None:
                raise AssertionError(json.dumps(result, sort_keys=True))
    print(json.dumps({"status": "passed", "captures": results}, sort_keys=True))


if __name__ == "__main__":
    main()

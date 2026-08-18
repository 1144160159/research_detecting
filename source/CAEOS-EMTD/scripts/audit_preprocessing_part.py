#!/usr/bin/env python3
"""Read-only structural and arithmetic audit for a completed CAEOS CSV part."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import math
import os
import random
from collections import Counter
from pathlib import Path
from typing import Any


SEQUENCE_COLUMNS = (
    "packet_length_seq",
    "ip_length_seq",
    "packet_iat_us_seq",
    "direction_seq",
    "packet_protocol_seq",
    "tcp_flags_seq",
    "ip_dscp_ecn_seq",
    "ip_flags_seq",
    "ip_fragment_offset_seq",
    "ip_fragment_id_seq",
    "transport_header_length_seq",
    "tcp_sequence_seq",
    "tcp_acknowledgement_seq",
    "packet_payload_length_seq",
    "sanitized_l4_packet_length_seq",
    "packet_ttl_seq",
    "tcp_window_seq",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--part", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--prefix-rows", type=int, default=1000)
    parser.add_argument("--random-rows", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260801)
    return parser.parse_args()


def integers(value: str) -> list[int]:
    return [int(item) for item in value.split(";")] if value else []


def close_enough(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= max(1e-6, abs(expected) * 1e-9)


def numeric_summary(values: list[int]) -> tuple[int, int, float, float]:
    if not values:
        return 0, 0, 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return min(values), max(values), mean, math.sqrt(variance)


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    columns = [item["name"] for item in schema["columns"]]
    errors: list[dict[str, Any]] = []
    counters: Counter[str] = Counter()
    examples: list[dict[str, str]] = []

    def fail(tag: str, check: str, actual: Any = None, expected: Any = None) -> None:
        if len(errors) < 100:
            errors.append(
                {"row": tag, "check": check, "actual": actual, "expected": expected}
            )

    def check(values: list[str], tag: str) -> None:
        if len(values) != len(columns):
            fail(tag, "field_count", len(values), len(columns))
            return
        row = dict(zip(columns, values))
        counters["rows_checked"] += 1
        packet_count = int(row["packet_count_stored"])
        sequences = {
            name: integers(row[name]) for name in SEQUENCE_COLUMNS if name in row
        }
        for name, sequence in sequences.items():
            if len(sequence) != packet_count:
                fail(tag, f"{name}.length", len(sequence), packet_count)
        if int(row["packet_count_total"]) != packet_count:
            fail(tag, "packet_count_total")
        if int(row["forward_packet_count"]) + int(row["reverse_packet_count"]) != packet_count:
            fail(tag, "direction_packet_count")
        packet_lengths = sequences["packet_length_seq"]
        payload_lengths = sequences["packet_payload_length_seq"]
        if sum(packet_lengths) != int(row["packet_bytes_total"]):
            fail(tag, "packet_bytes_total")
        if sum(payload_lengths) != int(row["payload_bytes_total"]):
            fail(tag, "payload_bytes_total")
        if int(row["forward_packet_bytes"]) + int(row["reverse_packet_bytes"]) != int(
            row["packet_bytes_total"]
        ):
            fail(tag, "direction_packet_bytes")
        if int(row["forward_payload_bytes"]) + int(row["reverse_payload_bytes"]) != int(
            row["payload_bytes_total"]
        ):
            fail(tag, "direction_payload_bytes")

        payload = base64.b64decode(row["payload_b64"], validate=True)
        sanitized_l4 = base64.b64decode(row["sanitized_l4_b64"], validate=True)
        if len(payload) != int(row["payload_bytes_stored"]) or len(payload) > 4096:
            fail(tag, "payload_b64_length")
        if len(sanitized_l4) != int(row["sanitized_l4_bytes_stored"]) or len(
            sanitized_l4
        ) > 2048:
            fail(tag, "sanitized_l4_b64_length")
        histogram = integers(row["payload_histogram"])
        if len(histogram) != 256 or sum(histogram) != int(row["payload_bytes_total"]):
            fail(tag, "payload_histogram")

        if sequences["packet_iat_us_seq"][0] != 0:
            fail(tag, "first_iat")
        if any(value not in (-1, 1) for value in sequences["direction_seq"]):
            fail(tag, "direction_domain")
        protocol = int(row["transport_protocol"])
        if any(value != protocol for value in sequences["packet_protocol_seq"]):
            fail(tag, "protocol_sequence")
        duration_us = max(
            0, (int(row["flow_end_ns"]) - int(row["flow_start_ns"])) // 1000
        )
        if duration_us != int(row["duration_us"]):
            fail(tag, "duration_us", row["duration_us"], duration_us)

        sample_material = "|".join(
            [
                row["dataset_id"],
                row["source_container_sha256"],
                row["source_member"],
                row["flow_key_hash"],
                row["flow_start_ns"],
                row["flow_segment_index"],
            ]
        )
        expected_sample_id = hashlib.sha256(sample_material.encode("utf-8")).hexdigest()
        if row["sample_id"] != expected_sample_id:
            fail(tag, "sample_id")

        for prefix, sequence in (
            ("packet_length", packet_lengths),
            ("packet_iat_us", sequences["packet_iat_us_seq"][1:]),
            ("packet_payload_length", payload_lengths),
        ):
            minimum, maximum, mean, standard_deviation = numeric_summary(sequence)
            if int(row[f"{prefix}_min"]) != minimum:
                fail(tag, f"{prefix}_min")
            if int(row[f"{prefix}_max"]) != maximum:
                fail(tag, f"{prefix}_max")
            if not close_enough(float(row[f"{prefix}_mean"]), mean):
                fail(tag, f"{prefix}_mean")
            if not close_enough(float(row[f"{prefix}_std"]), standard_deviation):
                fail(tag, f"{prefix}_std")

        if int(row["payload_bytes_total"]) > 0:
            counters["rows_with_payload"] += 1
        if any(sequences["ip_fragment_offset_seq"]) or any(
            value & 1 for value in sequences["ip_flags_seq"]
        ):
            counters["rows_with_fragments"] += 1
        if "fragmented_packet_count" in row:
            fragmented = sum(
                int(bool(offset or (flags & 1)))
                for offset, flags in zip(
                    sequences["ip_fragment_offset_seq"], sequences["ip_flags_seq"]
                )
            )
            noninitial = sum(
                int(offset > 0) for offset in sequences["ip_fragment_offset_seq"]
            )
            if int(row["fragmented_packet_count"]) != fragmented:
                fail(tag, "fragmented_packet_count")
            if int(row["noninitial_fragment_count"]) != noninitial:
                fail(tag, "noninitial_fragment_count")
        counters[f"protocol::{protocol}"] += 1
        counters[f"label_status::{row['label_status']}"] += 1
        if len(examples) < 3:
            examples.append(
                {
                    name: row[name]
                    for name in (
                        "sample_id",
                        "flow_segment_index",
                        "packet_count_stored",
                        "packet_bytes_total",
                        "payload_bytes_total",
                        "payload_bytes_stored",
                        "transport_protocol",
                        "ip_version",
                        "duration_us",
                        "attack_category",
                        "attack_subcategory",
                        "application_protocol_hint",
                    )
                }
            )

    with args.part.open("r", encoding="utf-8", newline="") as handle:
        for index, values in enumerate(csv.reader(handle)):
            if index >= args.prefix_rows:
                break
            check(values, f"prefix:{index}")

    size = args.part.stat().st_size
    randomizer = random.Random(args.seed)
    with args.part.open("rb") as handle:
        for index in range(args.random_rows):
            offset = randomizer.randrange(0, size)
            handle.seek(offset)
            if offset:
                handle.readline()
            line = handle.readline()
            if not line:
                continue
            try:
                values = next(csv.reader([line.decode("utf-8")]))
                check(values, f"random:{index}@{offset}")
            except Exception as error:  # Report malformed sampled records without aborting.
                fail(f"random:{index}@{offset}", type(error).__name__, str(error))

    actual_sha256 = hashlib.sha256()
    with args.part.open("rb") as handle:
        chunk = handle.read(16 * 1024 * 1024)
        while chunk:
            actual_sha256.update(chunk)
            chunk = handle.read(16 * 1024 * 1024)
    expected_sha256 = metadata["part_sha256"]
    if actual_sha256.hexdigest() != expected_sha256:
        fail("file", "part_sha256", actual_sha256.hexdigest(), expected_sha256)
    if size != int(metadata["part_size_bytes"]):
        fail("file", "part_size_bytes", size, metadata["part_size_bytes"])

    result = {
        "part": str(args.part),
        "part_size_bytes": size,
        "schema_columns": len(columns),
        "sampled_rows": counters["rows_checked"],
        "counters": dict(sorted(counters.items())),
        "metadata_rows": metadata.get("counters", {}).get("rows"),
        "metadata_packets_read": metadata.get("counters", {}).get("packets_read"),
        "sha256_verified": actual_sha256.hexdigest() == expected_sha256,
        "errors_total": len(errors),
        "errors": errors,
        "examples": examples,
    }
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

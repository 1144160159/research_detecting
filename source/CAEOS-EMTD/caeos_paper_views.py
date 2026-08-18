from __future__ import annotations

import base64
import json
import math
import struct
from typing import Any, Mapping


PAYLOAD_TOKENS = 512
PACKET_COUNT = 16
PAD_TOKEN = 256


def parse_sequence(value: str) -> list[int]:
    return [int(item) for item in value.split(";")] if value else []


def padded(values: list[int], size: int, fill: int = 0) -> list[int]:
    return (values[:size] + [fill] * size)[:size]


def materialize_views(row: Mapping[str, str]) -> dict[str, list[int] | list[float]]:
    payload_bytes = base64.b64decode(row["payload_b64"], validate=True)
    payload = list(payload_bytes[:PAYLOAD_TOKENS])
    payload.extend([PAD_TOKEN] * (PAYLOAD_TOKENS - len(payload)))

    lengths = padded(parse_sequence(row["packet_length_seq"]), PACKET_COUNT)
    iats = padded(parse_sequence(row["packet_iat_us_seq"]), PACKET_COUNT)
    directions = padded(parse_sequence(row["direction_seq"]), PACKET_COUNT)
    protocols = padded(parse_sequence(row["packet_protocol_seq"]), PACKET_COUNT)
    flags = padded(parse_sequence(row["tcp_flags_seq"]), PACKET_COUNT)
    payload_lengths = padded(
        parse_sequence(row["packet_payload_length_seq"]), PACKET_COUNT
    )
    stored_packets = min(int(row["packet_count_stored"]), PACKET_COUNT)

    sequence: list[float] = []
    nodes: list[float] = []
    for index in range(PACKET_COUNT):
        if index >= stored_packets:
            sequence.extend([0.0] * 6)
            nodes.extend([0.0] * 5)
            continue
        length = min(1.0, math.log1p(lengths[index]) / math.log1p(65535))
        interval_ms = max(0.0, iats[index] / 1000.0)
        interval = min(1.0, math.log1p(interval_ms) / math.log1p(60000.0))
        direction = float(directions[index])
        protocol = {6: 1.0, 17: 0.5, 1: -0.5, 58: -0.5}.get(
            protocols[index], 0.0
        )
        flag = float(flags[index] & 0x3F) / 63.0
        payload_length = min(
            1.0, math.log1p(payload_lengths[index]) / math.log1p(1500)
        )
        sequence.extend(
            [length * direction, interval, direction, protocol, flag, payload_length]
        )
        nodes.extend([length, interval, direction, payload_length, 1.0])

    adjacency = [0.0] * (PACKET_COUNT * PACKET_COUNT)
    for index in range(PACKET_COUNT):
        adjacency[index * PACKET_COUNT + index] = 1.0
    for index in range(1, stored_packets):
        weight = 2.0 if directions[index - 1] == directions[index] else 1.0
        adjacency[(index - 1) * PACKET_COUNT + index] = weight
        adjacency[index * PACKET_COUNT + index - 1] = weight

    return {
        "payload": payload,
        "sequence": sequence,
        "graph": nodes + adjacency,
        "quality": [
            min(1.0, min(len(payload_bytes), PAYLOAD_TOKENS) / 128.0),
            min(1.0, stored_packets / 8.0),
            min(1.0, max(0, stored_packets - 1) / 7.0),
        ],
    }


def training_row_to_views(row: Mapping[str, str]) -> dict[str, list[int] | list[float]]:
    return materialize_views(row)


def deployment_json_to_views(value: bytes) -> dict[str, list[int] | list[float]]:
    row = json.loads(value.decode("utf-8"))
    if not isinstance(row, dict):
        raise ValueError("deployment input must decode to an object")
    return materialize_views(row)


def exact_view_bytes(views: Mapping[str, list[int] | list[float]]) -> bytes:
    payload = views["payload"]
    output = bytearray(struct.pack(f"!{len(payload)}H", *payload))
    for name in ("sequence", "graph", "quality"):
        values = views[name]
        output.extend(struct.pack(f"!{len(values)}d", *values))
    return bytes(output)

#!/usr/bin/env python3
"""Replay a capture until its first finalized segment and compare all CSV fields."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parser-module", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--part", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--maximum-active-flows", type=int, default=25000)
    return parser.parse_args()


def load_parser(path: Path) -> Any:
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("caeos_preprocessor_under_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parser module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def csv_strings(row: dict[str, Any], columns: list[str]) -> dict[str, str]:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="raise")
    writer.writerow(row)
    output.seek(0)
    values = next(csv.reader(output))
    return dict(zip(columns, values))


def main() -> None:
    args = parse_args()
    parser_module = load_parser(args.parser_module)
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    columns = [item["name"] for item in schema["columns"]]
    dataset = next(
        item for item in catalog["datasets"] if item["id"] == metadata["dataset_id"]
    )
    with args.part.open("r", encoding="utf-8", newline="") as handle:
        observed = dict(zip(columns, next(csv.reader(handle))))

    source_member = metadata["source_member"]
    label = parser_module.path_label(dataset, source_member)
    maximum_packets = int(schema["maximum_packets_stored"])
    idle_ns = int(float(schema["flow_idle_timeout_seconds"]) * 1_000_000_000)
    active: OrderedDict[tuple[Any, ...], Any] = OrderedDict()
    continuation: dict[tuple[Any, ...], int] = {}
    counters = {"packets_read": 0, "packets_skipped": 0}
    generated: Optional[dict[str, Any]] = None
    finalization_reason = ""

    def finalize(key: tuple[Any, ...], reason: str) -> None:
        nonlocal generated, finalization_reason
        state = active.pop(key)
        if not state.packets:
            return
        generated = parser_module.flow_row(
            dataset,
            label,
            state,
            metadata["capture_id"],
            metadata["source_container_sha256"],
            source_member,
            int(schema["payload_prefix_bytes"]),
            int(schema["sanitized_l4_prefix_bytes"]),
        )
        finalization_reason = reason

    source_path = Path(metadata["source_path"])
    with parser_module.open_capture(source_path, None) as capture_handle:
        for timestamp, frame in parser_module.packet_reader(capture_handle):
            counters["packets_read"] += 1
            parsed = parser_module.parse_packet(float(timestamp), bytes(frame))
            if parsed is None:
                counters["packets_skipped"] += 1
                continue
            key, packet, flow_metadata = parsed
            state = active.get(key)
            if state is not None and packet.timestamp_ns - state.last_timestamp_ns > idle_ns:
                finalize(key, "idle_timeout")
                if generated is not None:
                    break
                state = None
            if state is None:
                state = parser_module.FlowState(
                    **flow_metadata,
                    segment_index=continuation.pop(key, 0),
                )
                active[key] = state
            else:
                active.move_to_end(key)
            state.packets.append(packet)
            if len(state.packets) >= maximum_packets:
                finalize(key, "maximum_packets")
                if generated is not None:
                    break
            while len(active) > args.maximum_active_flows:
                finalize(next(iter(active)), "active_flow_limit")
                if generated is not None:
                    break
            if generated is not None:
                break
            if counters["packets_read"] % 65536 == 0 and active:
                threshold = packet.timestamp_ns - idle_ns
                expired = [
                    flow_key
                    for flow_key, flow_state in active.items()
                    if flow_state.last_timestamp_ns < threshold
                ]
                for flow_key in expired:
                    finalize(flow_key, "idle_sweep")
                    if generated is not None:
                        break
            if generated is not None:
                break

    if generated is None:
        for key in list(active):
            finalize(key, "end_of_capture")
            if generated is not None:
                break
    if generated is None:
        raise RuntimeError("capture produced no flow rows")

    expected = csv_strings(generated, columns)
    mismatches = {
        column: {"observed": observed[column], "replayed": expected[column]}
        for column in columns
        if observed[column] != expected[column]
    }
    print(
        json.dumps(
            {
                "capture": str(source_path),
                "packets_read_until_first_row": counters["packets_read"],
                "packets_skipped_until_first_row": counters["packets_skipped"],
                "finalization_reason": finalization_reason,
                "columns_compared": len(columns),
                "mismatch_count": len(mismatches),
                "mismatches": mismatches,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    raise SystemExit(1 if mismatches else 0)


if __name__ == "__main__":
    main()

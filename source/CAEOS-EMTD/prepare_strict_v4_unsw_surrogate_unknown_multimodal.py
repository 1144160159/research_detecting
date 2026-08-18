from __future__ import annotations

import argparse
import csv
import json
import socket
from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from prepare_strict_v4_cic_iot2023_pcap_multimodal import (
    GRAPH_NODE_FEATURES,
    PACKET_COUNT,
    PAYLOAD_TOKENS,
    SEQUENCE_FEATURES,
    FlowState,
    canonical_flow_key,
    iter_pcap,
    packet_features,
    parse_ip_packet,
    pcap_prefix_hash,
    source_stat,
)
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


DEFAULT_ALLOWED_CATEGORIES = (
    "Exploits",
    "Fuzzers",
    "Reconnaissance",
    "Shellcode",
)
DIRECT_TARGET_OVERLAP_CATEGORIES = frozenset({"ddos", "dos", "mirai"})
PROTOCOL_NUMBERS = {
    "icmp": socket.IPPROTO_ICMP,
    "icmp6": socket.IPPROTO_ICMPV6,
    "ipv6-icmp": socket.IPPROTO_ICMPV6,
    "tcp": socket.IPPROTO_TCP,
    "udp": socket.IPPROTO_UDP,
}

FlowKey = tuple[tuple[bytes, int], tuple[bytes, int], int]


@dataclass(frozen=True)
class GroundTruthEvent:
    event_id: int
    start_time: float
    end_time: float
    category: str
    key: FlowKey


@dataclass
class GroundTruthLoad:
    events_by_key: dict[FlowKey, list[GroundTruthEvent]]
    category_counts: Counter[str]
    allowed_category_counts: Counter[str]
    protocol_counts: Counter[str]
    rows_read: int
    rows_rejected: int


def protocol_number(value: str) -> int | None:
    return PROTOCOL_NUMBERS.get(value.strip().lower())


def packed_ip(value: str) -> bytes:
    text = value.strip()
    family = socket.AF_INET6 if ":" in text else socket.AF_INET
    return socket.inet_pton(family, text)


def parse_port(value: str) -> int:
    text = value.strip()
    if not text or text == "-":
        return 0
    return int(float(text))


def ground_truth_key(row: dict[str, str]) -> FlowKey | None:
    protocol = protocol_number(row.get("Protocol", ""))
    if protocol is None:
        return None
    first, second, protocol, _ = canonical_flow_key(
        packed_ip(row["Source IP"]),
        packed_ip(row["Destination IP"]),
        parse_port(row["Source Port"]),
        parse_port(row["Destination Port"]),
        protocol,
    )
    return first, second, protocol


def validate_allowed_categories(categories: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(dict.fromkeys(item.strip() for item in categories if item.strip()))
    if not normalized:
        raise ValueError("at least one external surrogate category is required")
    overlap = sorted(
        category
        for category in normalized
        if category.casefold() in DIRECT_TARGET_OVERLAP_CATEGORIES
    )
    if overlap:
        raise ValueError(
            "external surrogate categories overlap target held-out families: "
            + ", ".join(overlap)
        )
    return normalized


def load_ground_truth(
    path: Path,
    allowed_categories: tuple[str, ...],
) -> GroundTruthLoad:
    allowed = frozenset(validate_allowed_categories(allowed_categories))
    events_by_key: dict[FlowKey, list[GroundTruthEvent]] = {}
    category_counts: Counter[str] = Counter()
    allowed_category_counts: Counter[str] = Counter()
    protocol_counts: Counter[str] = Counter()
    rows_read = 0
    rows_rejected = 0
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.DictReader(handle)
        required = {
            "Start time",
            "Last time",
            "Attack category",
            "Protocol",
            "Source IP",
            "Source Port",
            "Destination IP",
            "Destination Port",
        }
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(
                "UNSW ground truth is missing columns: " + ", ".join(sorted(missing))
            )
        for event_id, row in enumerate(reader, start=1):
            rows_read += 1
            category = row["Attack category"].strip()
            category_counts[category] += 1
            protocol_counts[row["Protocol"].strip().lower()] += 1
            if category not in allowed:
                continue
            try:
                key = ground_truth_key(row)
                if key is None:
                    rows_rejected += 1
                    continue
                start_time = float(row["Start time"])
                end_time = max(start_time, float(row["Last time"]))
            except (KeyError, TypeError, ValueError, OSError):
                rows_rejected += 1
                continue
            event = GroundTruthEvent(
                event_id=event_id,
                start_time=start_time,
                end_time=end_time,
                category=category,
                key=key,
            )
            events_by_key.setdefault(key, []).append(event)
            allowed_category_counts[category] += 1
    for events in events_by_key.values():
        events.sort(key=lambda event: (event.start_time, event.end_time, event.event_id))
    return GroundTruthLoad(
        events_by_key=events_by_key,
        category_counts=category_counts,
        allowed_category_counts=allowed_category_counts,
        protocol_counts=protocol_counts,
        rows_read=rows_read,
        rows_rejected=rows_rejected,
    )


def match_event(
    events_by_key: dict[FlowKey, list[GroundTruthEvent]],
    key: FlowKey,
    timestamp: float,
    tolerance_seconds: float,
) -> GroundTruthEvent | None:
    candidates = events_by_key.get(key, ())
    matches = [
        event
        for event in candidates
        if event.start_time - tolerance_seconds
        <= timestamp
        <= event.end_time + tolerance_seconds
    ]
    if not matches:
        return None
    return min(
        matches,
        key=lambda event: (
            abs(timestamp - event.start_time),
            event.end_time - event.start_time,
            event.event_id,
        ),
    )


def pcap_sort_key(path: Path) -> tuple[int, int, int, int, str]:
    capture_date = None
    for part in path.parts:
        if part.lower().startswith("pcap"):
            try:
                capture_date = datetime.strptime(
                    part[4:], "%d-%m-%Y"
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    try:
        sequence = int(path.stem)
    except ValueError:
        sequence = 2**31 - 1
    timestamp = int(capture_date.timestamp()) if capture_date else 2**31 - 1
    return timestamp, sequence, len(path.parts), len(path.name), path.as_posix()


def selected_pcaps(pcap_root: Path, maximum_pcap_files: int) -> list[Path]:
    paths = sorted(
        (path.resolve() for path in pcap_root.rglob("*.pcap") if path.is_file()),
        key=pcap_sort_key,
    )
    if not paths:
        raise ValueError(f"no PCAP files found below {pcap_root}")
    if maximum_pcap_files > 0:
        paths = paths[:maximum_pcap_files]
    return paths


def quotas_complete(counts: Counter[str], quotas: dict[str, int]) -> bool:
    return all(counts[category] >= quota for category, quota in quotas.items())


def extract_labeled_pcap(
    path: Path,
    events_by_key: dict[FlowKey, list[GroundTruthEvent]],
    tolerance_seconds: float,
    minimum_packets_per_flow: int,
    maximum_packets: int,
    quotas: dict[str, int],
    counts: Counter[str],
    used_event_ids: set[int],
) -> tuple[list[tuple[GroundTruthEvent, tuple[np.ndarray, ...]]], dict[str, Any]]:
    active: OrderedDict[int, tuple[GroundTruthEvent, FlowState]] = OrderedDict()
    completed: list[tuple[GroundTruthEvent, tuple[np.ndarray, ...]]] = []
    packets_read = 0
    packets_matched = 0
    parse_failures = 0

    def finalize(event_id: int) -> None:
        event, state = active.pop(event_id)
        if event.event_id in used_event_ids:
            return
        if len(state.packets) < minimum_packets_per_flow:
            return
        if counts[event.category] >= quotas[event.category]:
            return
        completed.append((event, packet_features(state.packets)))
        used_event_ids.add(event.event_id)
        counts[event.category] += 1

    with path.open("rb") as handle:
        for timestamp, frame in iter_pcap(handle):
            packets_read += 1
            if maximum_packets > 0 and packets_read > maximum_packets:
                break
            parsed = parse_ip_packet(float(timestamp), bytes(frame))
            if parsed is None:
                parse_failures += 1
                continue
            key, record = parsed
            event = match_event(
                events_by_key, key, record.timestamp, tolerance_seconds
            )
            if event is None or event.event_id in used_event_ids:
                continue
            if counts[event.category] >= quotas[event.category]:
                continue
            packets_matched += 1
            current = active.get(event.event_id)
            if current is None:
                state = FlowState(key=key)
                active[event.event_id] = (event, state)
            else:
                _, state = current
                active.move_to_end(event.event_id)
            state.append(record)
            if len(state.packets) >= PACKET_COUNT:
                finalize(event.event_id)
            if quotas_complete(counts, quotas):
                break

    for event_id in list(active):
        finalize(event_id)
        if quotas_complete(counts, quotas):
            break
    return completed, {
        "packets_read": packets_read,
        "packets_matched": packets_matched,
        "parse_failures": parse_failures,
        "flows_extracted": len(completed),
        "flows_by_category": dict(
            sorted(Counter(event.category for event, _ in completed).items())
        ),
    }


def audit_payload(
    ground_truth: Path,
    allowed_categories: tuple[str, ...],
    loaded: GroundTruthLoad,
    pcap_audit: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": "strict_v4_unsw_ground_truth_audit_v1",
        "ground_truth": str(ground_truth.resolve()),
        "ground_truth_sha256": file_hash(ground_truth),
        "allowed_categories": list(allowed_categories),
        "rows_read": loaded.rows_read,
        "rows_rejected_in_allowed_categories": loaded.rows_rejected,
        "category_counts": dict(sorted(loaded.category_counts.items())),
        "allowed_category_counts": dict(
            sorted(loaded.allowed_category_counts.items())
        ),
        "protocol_counts": dict(sorted(loaded.protocol_counts.items())),
    }
    if pcap_audit is not None:
        payload["pcap_audit"] = pcap_audit
    return payload


def audit_pcap_matches(
    paths: list[Path],
    events_by_key: dict[FlowKey, list[GroundTruthEvent]],
    tolerance_seconds: float,
    maximum_packets: int,
) -> list[dict[str, Any]]:
    audits: list[dict[str, Any]] = []
    for path in paths:
        packets_read = 0
        packets_parsed = 0
        matched_events: set[int] = set()
        matched_categories: Counter[str] = Counter()
        first_timestamp: float | None = None
        last_timestamp: float | None = None
        with path.open("rb") as handle:
            for timestamp, frame in iter_pcap(handle):
                packets_read += 1
                value = float(timestamp)
                if first_timestamp is None:
                    first_timestamp = value
                last_timestamp = value
                parsed = parse_ip_packet(value, bytes(frame))
                if parsed is not None:
                    packets_parsed += 1
                    key, record = parsed
                    event = match_event(
                        events_by_key,
                        key,
                        record.timestamp,
                        tolerance_seconds,
                    )
                    if event is not None and event.event_id not in matched_events:
                        matched_events.add(event.event_id)
                        matched_categories[event.category] += 1
                if maximum_packets > 0 and packets_read >= maximum_packets:
                    break
        audits.append(
            {
                "path": str(path),
                "packets_read": packets_read,
                "packets_parsed": packets_parsed,
                "first_timestamp": first_timestamp,
                "last_timestamp": last_timestamp,
                "unique_events_matched": len(matched_events),
                "matched_categories": dict(sorted(matched_categories.items())),
            }
        )
    return audits


def build_cache(args: argparse.Namespace) -> dict[str, Any]:
    allowed_categories = validate_allowed_categories(
        tuple(args.allowed_category or DEFAULT_ALLOWED_CATEGORIES)
    )
    ground_truth = args.ground_truth.resolve()
    loaded = load_ground_truth(ground_truth, allowed_categories)
    if args.audit_only:
        pcap_audit = None
        if args.pcap_root is not None:
            paths = selected_pcaps(
                args.pcap_root.resolve(), args.maximum_pcap_files
            )
            pcap_audit = audit_pcap_matches(
                paths,
                loaded.events_by_key,
                args.tolerance_seconds,
                args.maximum_packets_per_pcap,
            )
        return audit_payload(
            ground_truth, allowed_categories, loaded, pcap_audit
        )

    pcap_root = args.pcap_root.resolve()
    output = args.output.resolve()
    quotas = {
        category: int(args.maximum_flows_per_category)
        for category in allowed_categories
    }
    counts: Counter[str] = Counter()
    used_event_ids: set[int] = set()
    records: dict[str, list[np.ndarray]] = {
        "payload": [],
        "sequence": [],
        "graph": [],
        "quality": [],
    }
    categories: list[str] = []
    families: list[str] = []
    capture_groups: list[str] = []
    event_ids: list[int] = []
    event_start_times: list[float] = []
    event_end_times: list[float] = []
    source_records: list[dict[str, Any]] = []

    for path in selected_pcaps(pcap_root, args.maximum_pcap_files):
        flows, extraction = extract_labeled_pcap(
            path=path,
            events_by_key=loaded.events_by_key,
            tolerance_seconds=args.tolerance_seconds,
            minimum_packets_per_flow=args.minimum_packets_per_flow,
            maximum_packets=args.maximum_packets_per_pcap,
            quotas=quotas,
            counts=counts,
            used_event_ids=used_event_ids,
        )
        capture_group = "UNSW-NB15::" + path.relative_to(pcap_root).as_posix()
        for event, (payload, sequence, graph, quality) in flows:
            records["payload"].append(payload)
            records["sequence"].append(sequence)
            records["graph"].append(graph)
            records["quality"].append(quality)
            categories.append(event.category)
            families.append("ExternalSurrogateUnknown")
            capture_groups.append(capture_group)
            event_ids.append(event.event_id)
            event_start_times.append(event.start_time)
            event_end_times.append(event.end_time)
        source_record = source_stat(path)
        source_record.update(
            {
                "relative_path": path.relative_to(pcap_root).as_posix(),
                "prefix_1mib_sha256": pcap_prefix_hash(path),
                **extraction,
            }
        )
        source_records.append(source_record)
        if quotas_complete(counts, quotas):
            break

    below_minimum = {
        category: counts[category]
        for category in allowed_categories
        if counts[category] < args.minimum_flows_per_category
    }
    if below_minimum:
        raise ValueError(
            "insufficient matched UNSW flows by category: "
            + json.dumps(below_minimum, sort_keys=True)
        )
    if not categories:
        raise ValueError("no labeled UNSW flows were extracted")
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        payload=np.stack(records["payload"]),
        sequence=np.stack(records["sequence"]),
        graph=np.stack(records["graph"]),
        quality=np.stack(records["quality"]),
        fine_label=np.asarray(categories),
        family=np.asarray(families),
        capture_group=np.asarray(capture_groups),
        event_id=np.asarray(event_ids, dtype=np.int64),
        event_start_time=np.asarray(event_start_times, dtype=np.float64),
        event_end_time=np.asarray(event_end_times, dtype=np.float64),
    )
    manifest: dict[str, Any] = {
        "schema_version": (
            "strict_v4_unsw_surrogate_unknown_multimodal_cache_manifest_v1"
        ),
        "source_dataset": "UNSW-NB15",
        "source_role": "training_only_external_surrogate_unknown",
        "source_root": str(pcap_root),
        "ground_truth": source_stat(ground_truth),
        "ground_truth_sha256": file_hash(ground_truth),
        "cache_path": str(output),
        "cache_sha256": file_hash(output),
        "samples": len(categories),
        "samples_by_category": dict(sorted(counts.items())),
        "allowed_categories": list(allowed_categories),
        "direct_target_overlap_categories_forbidden": sorted(
            DIRECT_TARGET_OVERLAP_CATEGORIES
        ),
        "maximum_flows_per_category": args.maximum_flows_per_category,
        "minimum_flows_per_category": args.minimum_flows_per_category,
        "minimum_packets_per_flow": args.minimum_packets_per_flow,
        "maximum_pcap_files": args.maximum_pcap_files,
        "maximum_packets_per_pcap": args.maximum_packets_per_pcap,
        "timestamp_tolerance_seconds": args.tolerance_seconds,
        "modalities": {
            "payload_semantics": {
                "shape": [PAYLOAD_TOKENS],
                "description": "transport payload byte tokens only",
                "network_addresses_and_ports_excluded": True,
            },
            "packet_behavior": {
                "shape": [PACKET_COUNT * SEQUENCE_FEATURES],
                "description": (
                    "ordered packet length, interval, direction, protocol, "
                    "flags, and payload length"
                ),
            },
            "packet_interaction_graph": {
                "shape": [
                    PACKET_COUNT * GRAPH_NODE_FEATURES
                    + PACKET_COUNT * PACKET_COUNT
                ],
                "description": (
                    "packet-node attributes and temporal/direction adjacency"
                ),
            },
        },
        "capture_group_binding": "UNSW-NB15 relative source PCAP path",
        "source_files": source_records,
        "implementation": {
            "adapter_path": str(Path(__file__).resolve()),
            "adapter_sha256": file_hash(Path(__file__).resolve()),
            "base_extractor_path": str(
                Path(
                    __file__
                ).resolve().with_name(
                    "prepare_strict_v4_cic_iot2023_pcap_multimodal.py"
                )
            ),
            "base_extractor_sha256": file_hash(
                Path(__file__).resolve().with_name(
                    "prepare_strict_v4_cic_iot2023_pcap_multimodal.py"
                )
            ),
        },
        "claim_boundary": {
            "official_unsw_ground_truth_time_and_five_tuple_matched": True,
            "one_sample_per_ground_truth_event": True,
            "target_ciciot2023_test_unknown_labels_accessed": False,
            "cache_role_is_training_only_not_evaluation": True,
            "source_pcap_full_hash_not_computed": True,
            "source_pcap_prefix_hash_and_stat_bound": True,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    atomic_json(output.with_suffix(output.suffix + ".manifest.json"), manifest)
    return manifest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap-root", type=Path)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allowed-category", action="append")
    parser.add_argument("--maximum-flows-per-category", type=int, default=256)
    parser.add_argument("--minimum-flows-per-category", type=int, default=64)
    parser.add_argument("--minimum-packets-per-flow", type=int, default=2)
    parser.add_argument("--maximum-pcap-files", type=int, default=8)
    parser.add_argument("--maximum-packets-per-pcap", type=int, default=0)
    parser.add_argument("--tolerance-seconds", type=float, default=1.0)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if not args.audit_only and args.pcap_root is None:
        parser.error("--pcap-root is required unless --audit-only is used")
    if not args.audit_only and args.output is None:
        parser.error("--output is required unless --audit-only is used")
    if args.output is not None and args.output.exists():
        parser.error(f"refusing to overwrite cache: {args.output}")
    return args


def main() -> None:
    manifest = build_cache(parse_arguments())
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

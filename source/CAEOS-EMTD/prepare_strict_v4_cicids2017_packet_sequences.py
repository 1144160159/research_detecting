from __future__ import annotations

import argparse
import bisect
import concurrent.futures
import csv
import hashlib
import heapq
import ipaddress
import json
import os
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

import numpy as np

from strict_v4_cicids2017_attack_family import (
    FINE_TO_FAMILY,
    atomic_json,
    canonical_hash,
    file_hash,
)


PCAP_BY_DAY = {
    "monday": "Monday-WorkingHours.pcap",
    "tuesday": "Tuesday-WorkingHours.pcap",
    "wednesday": "Wednesday-workingHours.pcap",
    "thursday": "Thursday-WorkingHours.pcap",
    "friday": "Friday-WorkingHours.pcap",
}

IDENTITY_COLUMNS = (
    "Flow ID",
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Flow Duration",
    "Label",
)

TIMESTAMP_FORMATS = (
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
)

PCAP_MAGIC = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
}
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"


@dataclass(frozen=True)
class LabelFlow:
    flow_id: str
    capture_id: str
    pcap_name: str
    source_ip: bytes
    source_port: int
    destination_ip: bytes
    destination_port: int
    protocol: int
    start_wall_us: int
    end_wall_us: int
    fine_label: str
    family: str
    priority: int
    timestamp_resolution_us: int = 1_000_000
    wall_clock_adjustment_us: int = 0

    @property
    def canonical_key(self) -> tuple[bytes, int, bytes, int, int]:
        return canonical_flow_key(
            self.source_ip,
            self.source_port,
            self.destination_ip,
            self.destination_port,
            self.protocol,
        )


def canonical_flow_key(
    source_ip: bytes,
    source_port: int,
    destination_ip: bytes,
    destination_port: int,
    protocol: int,
) -> tuple[bytes, int, bytes, int, int]:
    source = (source_ip, source_port)
    destination = (destination_ip, destination_port)
    first, second = sorted((source, destination))
    return first[0], first[1], second[0], second[1], protocol


def parse_timestamp_wall_us(value: str) -> int:
    cleaned = " ".join(str(value).strip().split())
    for timestamp_format in TIMESTAMP_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, timestamp_format)
        except ValueError:
            continue
        return int(parsed.replace(tzinfo=timezone.utc).timestamp() * 1_000_000)
    raise ValueError(f"unsupported CICIDS2017 timestamp: {value!r}")


def timestamp_resolution_us(value: str) -> int:
    cleaned = " ".join(str(value).strip().split())
    time_part = cleaned.rsplit(" ", 1)[-1]
    return 1_000_000 if time_part.count(":") >= 2 else 60_000_000


def capture_wall_clock_adjustment_us(capture_id: str, timestamp_value: str) -> int:
    """Restore PM hours omitted by CICIDS2017 afternoon label CSVs."""
    cleaned = " ".join(str(timestamp_value).strip().split())
    parsed = None
    for timestamp_format in TIMESTAMP_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, timestamp_format)
        except ValueError:
            continue
        break
    if parsed is None:
        raise ValueError(f"unsupported CICIDS2017 timestamp: {timestamp_value!r}")
    if "afternoon" in capture_id.lower() and parsed.hour < 12:
        return 12 * 3_600_000_000
    return 0


def pcap_name_for_label_file(path: Path) -> str:
    lowered = path.name.lower()
    for day, pcap_name in PCAP_BY_DAY.items():
        if lowered.startswith(day):
            return pcap_name
    raise ValueError(f"cannot map label CSV to PCAP day: {path.name}")


def cleaned_header(row: Iterable[str]) -> list[str]:
    return [str(value).strip().lstrip("\ufeff") for value in row]


def deterministic_priority(material: str, seed: int) -> int:
    digest = hashlib.sha256(f"{seed}\0{material}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def normalize_fine_label(value: str) -> str:
    label = " ".join(str(value).strip().split())
    lowered = label.lower()
    if lowered == "benign":
        return "Benign"
    if lowered.startswith("web attack"):
        if "brute force" in lowered:
            return "Web Attack - Brute Force"
        if "sql injection" in lowered:
            return "Web Attack - Sql Injection"
        if "xss" in lowered:
            return "Web Attack - XSS"
    return label


def parse_label_row(
    *,
    row: list[str],
    indices: dict[str, int],
    capture_id: str,
    pcap_name: str,
    seed: int,
) -> LabelFlow:
    def value(column: str) -> str:
        return str(row[indices[column]]).strip()

    fine_label = normalize_fine_label(value("Label"))
    if fine_label not in FINE_TO_FAMILY:
        raise ValueError(f"unmapped CICIDS2017 label: {fine_label!r}")
    source_ip = ipaddress.ip_address(value("Source IP")).packed
    destination_ip = ipaddress.ip_address(value("Destination IP")).packed
    source_port = int(float(value("Source Port")))
    destination_port = int(float(value("Destination Port")))
    protocol = int(float(value("Protocol")))
    timestamp_value = value("Timestamp")
    wall_clock_adjustment_us = capture_wall_clock_adjustment_us(
        capture_id, timestamp_value
    )
    start_wall_us = (
        parse_timestamp_wall_us(timestamp_value) + wall_clock_adjustment_us
    )
    resolution_us = timestamp_resolution_us(timestamp_value)
    duration_us = max(0, int(float(value("Flow Duration"))))
    material = "\0".join(
        (
            capture_id,
            value("Flow ID"),
            value("Timestamp"),
            value("Flow Duration"),
            fine_label,
        )
    )
    return LabelFlow(
        flow_id=hashlib.sha256(material.encode("utf-8")).hexdigest(),
        capture_id=capture_id,
        pcap_name=pcap_name,
        source_ip=source_ip,
        source_port=source_port,
        destination_ip=destination_ip,
        destination_port=destination_port,
        protocol=protocol,
        start_wall_us=start_wall_us,
        end_wall_us=start_wall_us + resolution_us + duration_us,
        fine_label=fine_label,
        family=FINE_TO_FAMILY[fine_label],
        priority=deterministic_priority(material, seed),
        timestamp_resolution_us=resolution_us,
        wall_clock_adjustment_us=wall_clock_adjustment_us,
    )


def iter_label_flows(
    labels_dir: Path,
    *,
    seed: int,
    counters: Counter[str] | None = None,
) -> Iterator[LabelFlow]:
    label_paths = sorted(path for path in labels_dir.glob("*.csv") if path.is_file())
    if not label_paths:
        raise FileNotFoundError(f"no CICIDS2017 label CSVs under {labels_dir}")
    for label_path in label_paths:
        pcap_name = pcap_name_for_label_file(label_path)
        capture_id = label_path.stem
        with label_path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.reader(handle)
            try:
                header = cleaned_header(next(reader))
            except StopIteration as error:
                raise ValueError(f"empty label CSV: {label_path}") from error
            indices = {name: index for index, name in enumerate(header)}
            missing = sorted(set(IDENTITY_COLUMNS) - set(indices))
            if missing:
                raise ValueError(f"{label_path.name} missing columns: {missing}")
            maximum_index = max(indices.values())
            for row in reader:
                if len(row) <= maximum_index:
                    if counters is not None:
                        counters["malformed_rows"] += 1
                    continue
                try:
                    flow = parse_label_row(
                        row=row,
                        indices=indices,
                        capture_id=capture_id,
                        pcap_name=pcap_name,
                        seed=seed,
                    )
                except (ValueError, TypeError, OverflowError):
                    if counters is not None:
                        counters["invalid_rows"] += 1
                    continue
                if counters is not None:
                    counters["valid_rows"] += 1
                    counters[f"fine::{flow.fine_label}"] += 1
                    counters[f"family::{flow.family}"] += 1
                    counters[f"pcap::{flow.pcap_name}"] += 1
                    counters[
                        f"timestamp_resolution_us::{flow.timestamp_resolution_us}"
                    ] += 1
                    counters[
                        f"wall_clock_adjustment_us::{flow.wall_clock_adjustment_us}"
                    ] += 1
                yield flow


def select_balanced_flows(
    labels_dir: Path,
    *,
    seed: int,
    maximum_per_family: int,
) -> tuple[list[LabelFlow], Counter[str]]:
    if maximum_per_family <= 0:
        raise ValueError("maximum_per_family must be positive")
    counters: Counter[str] = Counter()
    reservoirs: dict[str, list[tuple[int, str, int, LabelFlow]]] = defaultdict(list)
    for ordinal, flow in enumerate(
        iter_label_flows(labels_dir, seed=seed, counters=counters)
    ):
        heap = reservoirs[flow.family]
        item = (-flow.priority, flow.flow_id, ordinal, flow)
        if len(heap) < maximum_per_family:
            heapq.heappush(heap, item)
        elif flow.priority < -heap[0][0]:
            heapq.heapreplace(heap, item)
    expected = set(FINE_TO_FAMILY.values())
    missing = sorted(expected - set(reservoirs))
    if missing:
        raise ValueError(f"selected sequence source misses families: {missing}")
    selected = sorted(
        (item[3] for heap in reservoirs.values() for item in heap),
        key=lambda flow: (flow.pcap_name, flow.start_wall_us, flow.flow_id),
    )
    return selected, counters


def sampled_file_fingerprint(path: Path, sample_bytes: int = 1024 * 1024) -> dict[str, Any]:
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read(sample_bytes))
        if stat.st_size > sample_bytes:
            handle.seek(max(0, stat.st_size - sample_bytes))
            digest.update(handle.read(sample_bytes))
    return {
        "path": str(path.resolve()),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sample_bytes_per_edge": sample_bytes,
        "edge_sample_sha256": digest.hexdigest(),
        "full_file_sha256_computed": False,
    }


def capture_format_from_magic(magic: bytes) -> str:
    if magic == PCAPNG_MAGIC:
        return "pcapng"
    if magic in PCAP_MAGIC:
        return "pcap"
    return "unknown"


def packet_reader(handle: Any) -> Any:
    import dpkt

    magic = handle.read(4)
    handle.seek(0)
    capture_format = capture_format_from_magic(magic)
    if capture_format == "pcapng":
        return dpkt.pcapng.Reader(handle)
    if capture_format == "pcap":
        return dpkt.pcap.Reader(handle)
    raise ValueError(f"unsupported packet capture magic: {magic.hex()}")


def label_audit(
    *,
    labels_dir: Path,
    pcap_dir: Path,
    selected: list[LabelFlow],
    counters: Counter[str],
    seed: int,
    maximum_per_family: int,
) -> dict[str, Any]:
    selected_counts = Counter(flow.family for flow in selected)
    identity_samples = []
    for flow in selected[:8]:
        identity_samples.append(
            {
                "capture_id": flow.capture_id,
                "pcap_name": flow.pcap_name,
                "source_ip": str(ipaddress.ip_address(flow.source_ip)),
                "source_port": flow.source_port,
                "destination_ip": str(ipaddress.ip_address(flow.destination_ip)),
                "destination_port": flow.destination_port,
                "protocol": flow.protocol,
                "start_wall": datetime.fromtimestamp(
                    flow.start_wall_us / 1_000_000, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "duration_us": (
                    flow.end_wall_us
                    - flow.start_wall_us
                    - flow.timestamp_resolution_us
                ),
                "timestamp_resolution_us": flow.timestamp_resolution_us,
                "wall_clock_adjustment_us": flow.wall_clock_adjustment_us,
                "fine_label": flow.fine_label,
                "family": flow.family,
            }
        )
    label_files = [
        {
            "path": str(path.resolve()),
            "size": path.stat().st_size,
            "sha256": file_hash(path),
        }
        for path in sorted(labels_dir.glob("*.csv"))
        if path.is_file()
    ]
    pcap_files = []
    for pcap_name in sorted({flow.pcap_name for flow in selected}):
        pcap_path = pcap_dir / pcap_name
        if not pcap_path.is_file():
            raise FileNotFoundError(f"required PCAP missing: {pcap_path}")
        pcap_files.append(sampled_file_fingerprint(pcap_path))
    return {
        "schema_version": "strict_v4_cicids2017_packet_sequence_source_audit_v1",
        "state": "complete_remote_data_audit",
        "seed": seed,
        "maximum_per_family": maximum_per_family,
        "source_counts": dict(sorted(counters.items())),
        "selected_family_counts": dict(sorted(selected_counts.items())),
        "selected_rows": len(selected),
        "identity_samples": identity_samples,
        "label_files": label_files,
        "pcap_files": pcap_files,
        "claim_boundary": {
            "data_preparation_only": True,
            "model_effect_result": False,
            "pcap_full_sha256_computed": False,
            "pcap_edge_samples_are_not_full_content_hashes": True,
            "selection_balances_families_before_open_set_splitting": True,
            "minute_precision_timestamps_are_treated_as_start_buckets": True,
            "afternoon_files_with_pre_noon_hours_receive_explicit_12h_adjustment": True,
        },
    }


def packet_identity(buffer: bytes) -> tuple[
    tuple[bytes, int, bytes, int, int], bytes, int, int
] | None:
    import dpkt

    try:
        ethernet = dpkt.ethernet.Ethernet(buffer)
        ip_packet = ethernet.data
        if isinstance(ip_packet, dpkt.ip.IP):
            protocol = int(ip_packet.p)
            packet_length = int(ip_packet.len)
        elif isinstance(ip_packet, dpkt.ip6.IP6):
            protocol = int(ip_packet.nxt)
            packet_length = int(ip_packet.plen) + 40
        else:
            return None
        transport = ip_packet.data
        if not isinstance(transport, (dpkt.tcp.TCP, dpkt.udp.UDP)):
            return None
        source_port = int(transport.sport)
        destination_port = int(transport.dport)
        source_ip = bytes(ip_packet.src)
        destination_ip = bytes(ip_packet.dst)
    except (ValueError, TypeError, AttributeError, dpkt.dpkt.UnpackError):
        return None
    key = canonical_flow_key(
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol,
    )
    return key, source_ip, source_port, max(1, min(packet_length, 32767))


def interval_match(
    flows: list[LabelFlow],
    starts: list[int],
    wall_us: int,
    tolerance_us: int,
) -> LabelFlow | None:
    position = bisect.bisect_right(starts, wall_us + tolerance_us)
    candidates = flows[max(0, position - 4) : position]
    matches = [
        flow
        for flow in candidates
        if flow.start_wall_us - tolerance_us
        <= wall_us
        <= flow.end_wall_us + tolerance_us
    ]
    if not matches:
        return None
    return min(matches, key=lambda flow: abs(wall_us - flow.start_wall_us))


def build_interval_index(
    flows: Iterable[LabelFlow],
) -> dict[tuple[bytes, int, bytes, int, int], tuple[list[int], list[LabelFlow]]]:
    grouped: dict[
        tuple[bytes, int, bytes, int, int], list[LabelFlow]
    ] = defaultdict(list)
    for flow in flows:
        grouped[flow.canonical_key].append(flow)
    result = {}
    for key, key_flows in grouped.items():
        ordered = sorted(key_flows, key=lambda flow: flow.start_wall_us)
        result[key] = ([flow.start_wall_us for flow in ordered], ordered)
    return result


def infer_timezone_offset_hours(
    *,
    pcap_path: Path,
    flows: list[LabelFlow],
    tolerance_us: int,
    maximum_packets: int,
    minimum_unique_matches: int,
) -> tuple[int, dict[str, Any]]:
    import dpkt

    index = build_interval_index(flows)
    candidates = range(-12, 15)
    matched_ids: dict[int, set[str]] = {candidate: set() for candidate in candidates}
    inspected = 0
    parseable = 0
    with pcap_path.open("rb") as handle:
        reader = packet_reader(handle)
        for timestamp, buffer in reader:
            inspected += 1
            identity = packet_identity(buffer)
            if identity is None:
                if inspected >= maximum_packets:
                    break
                continue
            parseable += 1
            key = identity[0]
            interval = index.get(key)
            if interval is not None:
                starts, key_flows = interval
                packet_us = int(float(timestamp) * 1_000_000)
                for candidate in candidates:
                    flow = interval_match(
                        key_flows,
                        starts,
                        packet_us - candidate * 3_600_000_000,
                        tolerance_us,
                    )
                    if flow is not None:
                        matched_ids[candidate].add(flow.flow_id)
            if inspected >= maximum_packets:
                break
            ranking = sorted(
                ((len(values), candidate) for candidate, values in matched_ids.items()),
                reverse=True,
            )
            if (
                ranking[0][0] >= minimum_unique_matches
                and ranking[0][0] >= ranking[1][0] + max(5, ranking[0][0] // 5)
            ):
                break
    ranking = sorted(
        ((len(values), candidate) for candidate, values in matched_ids.items()),
        reverse=True,
    )
    if not ranking or ranking[0][0] < minimum_unique_matches:
        raise ValueError(
            f"insufficient PCAP/label matches for timezone inference: {ranking[:5]}"
        )
    if len(ranking) > 1 and ranking[0][0] == ranking[1][0]:
        raise ValueError(f"ambiguous PCAP timezone offset: {ranking[:5]}")
    selected_offset = ranking[0][1]
    report = {
        "pcap_path": str(pcap_path.resolve()),
        "inspected_packets": inspected,
        "parseable_tcp_udp_packets": parseable,
        "tolerance_us": tolerance_us,
        "candidate_unique_flow_matches": {
            str(candidate): len(matched_ids[candidate]) for candidate in candidates
        },
        "selected_offset_hours": selected_offset,
        "selected_unique_flow_matches": ranking[0][0],
    }
    return selected_offset, report


def extract_sequences(
    *,
    pcap_path: Path,
    flows: list[LabelFlow],
    timezone_offset_hours: int,
    sequence_length: int,
    tolerance_us: int,
    progress_path: Path | None = None,
    progress_interval_packets: int = 5_000_000,
) -> tuple[dict[str, tuple[list[int], list[float]]], dict[str, Any]]:
    import dpkt

    index = build_interval_index(flows)
    values: dict[str, tuple[list[int], list[float]]] = {
        flow.flow_id: ([], []) for flow in flows
    }
    flow_by_id = {flow.flow_id: flow for flow in flows}
    requested_family_counts = Counter(flow.family for flow in flows)
    assigned_family_packet_counts: Counter[str] = Counter()
    last_timestamp: dict[str, int] = {}
    assigned_packets = 0
    inspected_packets = 0
    parseable_packets = 0
    with pcap_path.open("rb") as handle:
        reader = packet_reader(handle)
        for timestamp, buffer in reader:
            inspected_packets += 1
            if (
                progress_path is not None
                and inspected_packets % progress_interval_packets == 0
            ):
                progress = {
                    "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
                    "state": "extracting_pcap",
                    "pcap_path": str(pcap_path.resolve()),
                    "inspected_packets": inspected_packets,
                    "parseable_tcp_udp_packets": parseable_packets,
                    "assigned_packets": assigned_packets,
                    "assigned_family_packet_counts": dict(
                        sorted(assigned_family_packet_counts.items())
                    ),
                    "matched_flows": sum(
                        bool(lengths) for lengths, _ in values.values()
                    ),
                    "matched_family_flow_counts": dict(
                        sorted(
                            Counter(
                                flow_by_id[flow_id].family
                                for flow_id, (lengths, _) in values.items()
                                if lengths
                            ).items()
                        )
                    ),
                    "requested_flows": len(flows),
                    "requested_family_flow_counts": dict(
                        sorted(requested_family_counts.items())
                    ),
                    "updated_unix_seconds": time.time(),
                }
                progress["manifest_sha256"] = canonical_hash(progress)
                atomic_json(progress_path, progress)
            identity = packet_identity(buffer)
            if identity is None:
                continue
            parseable_packets += 1
            key, source_ip, source_port, packet_length = identity
            interval = index.get(key)
            if interval is None:
                continue
            packet_us = int(float(timestamp) * 1_000_000)
            wall_us = packet_us - timezone_offset_hours * 3_600_000_000
            starts, key_flows = interval
            flow = interval_match(key_flows, starts, wall_us, tolerance_us)
            if flow is None:
                continue
            lengths, interarrivals = values[flow.flow_id]
            if len(lengths) >= sequence_length:
                continue
            forward = (
                source_ip == flow.source_ip and source_port == flow.source_port
            )
            lengths.append(packet_length if forward else -packet_length)
            previous = last_timestamp.get(flow.flow_id)
            delta = 0.0 if previous is None else float(max(0, packet_us - previous))
            interarrivals.append(min(delta, 1_000_000_000.0))
            last_timestamp[flow.flow_id] = packet_us
            assigned_packets += 1
            assigned_family_packet_counts[flow.family] += 1
    matched_flows = sum(bool(lengths) for lengths, _ in values.values())
    matched_family_flow_counts = Counter(
        flow_by_id[flow_id].family
        for flow_id, (lengths, _) in values.items()
        if lengths
    )
    return values, {
        "pcap_path": str(pcap_path.resolve()),
        "timezone_offset_hours": timezone_offset_hours,
        "inspected_packets": inspected_packets,
        "parseable_tcp_udp_packets": parseable_packets,
        "assigned_packets": assigned_packets,
        "assigned_family_packet_counts": dict(
            sorted(assigned_family_packet_counts.items())
        ),
        "matched_flows": matched_flows,
        "matched_family_flow_counts": dict(
            sorted(matched_family_flow_counts.items())
        ),
        "requested_flows": len(flows),
        "requested_family_flow_counts": dict(
            sorted(requested_family_counts.items())
        ),
    }


def process_pcap(
    *,
    pcap_path: Path,
    flows: list[LabelFlow],
    sequence_length: int,
    tolerance_us: int,
    offset_probe_packets: int,
    offset_minimum_unique_matches: int,
    progress_path: Path,
    progress_interval_packets: int,
) -> tuple[
    dict[str, tuple[list[int], list[float]]],
    dict[str, Any],
    dict[str, Any],
]:
    progress = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
        "state": "inferring_timezone_offset",
        "pcap_path": str(pcap_path.resolve()),
        "requested_flows": len(flows),
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    offset, timezone_report = infer_timezone_offset_hours(
        pcap_path=pcap_path,
        flows=flows,
        tolerance_us=tolerance_us,
        maximum_packets=offset_probe_packets,
        minimum_unique_matches=offset_minimum_unique_matches,
    )
    values, extraction_report = extract_sequences(
        pcap_path=pcap_path,
        flows=flows,
        timezone_offset_hours=offset,
        sequence_length=sequence_length,
        tolerance_us=tolerance_us,
        progress_path=progress_path,
        progress_interval_packets=progress_interval_packets,
    )
    progress = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
        "state": "pcap_complete",
        "pcap_path": str(pcap_path.resolve()),
        "timezone_inference": timezone_report,
        "extraction": extraction_report,
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    return values, timezone_report, extraction_report


def save_sequence_dataset(
    *,
    output_path: Path,
    selected: list[LabelFlow],
    values: dict[str, tuple[list[int], list[float]]],
    sequence_length: int,
    minimum_packets: int,
) -> dict[str, Any]:
    retained = [
        flow
        for flow in selected
        if len(values[flow.flow_id][0]) >= minimum_packets
    ]
    packet_lengths = np.zeros((len(retained), sequence_length), dtype=np.int16)
    interarrival_us = np.zeros((len(retained), sequence_length), dtype=np.float32)
    mask = np.zeros((len(retained), sequence_length), dtype=bool)
    for row_index, flow in enumerate(retained):
        lengths, interarrivals = values[flow.flow_id]
        count = min(sequence_length, len(lengths))
        packet_lengths[row_index, :count] = lengths[:count]
        interarrival_us[row_index, :count] = interarrivals[:count]
        mask[row_index, :count] = True
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(
            handle,
            packet_lengths=packet_lengths,
            interarrival_us=interarrival_us,
            mask=mask,
            flow_ids=np.asarray([flow.flow_id for flow in retained]),
            capture_ids=np.asarray([flow.capture_id for flow in retained]),
            fine_labels=np.asarray([flow.fine_label for flow in retained]),
            families=np.asarray([flow.family for flow in retained]),
        )
    os.replace(temporary, output_path)
    return {
        "rows": len(retained),
        "sequence_length": sequence_length,
        "minimum_packets": minimum_packets,
        "retained_family_counts": dict(
            sorted(Counter(flow.family for flow in retained).items())
        ),
        "retained_fine_counts": dict(
            sorted(Counter(flow.fine_label for flow in retained).items())
        ),
        "packet_count_summary": {
            "minimum": int(mask.sum(axis=1).min()) if len(retained) else 0,
            "median": float(np.median(mask.sum(axis=1))) if len(retained) else 0.0,
            "maximum": int(mask.sum(axis=1).max()) if len(retained) else 0,
        },
        "output_path": str(output_path.resolve()),
        "output_sha256": file_hash(output_path),
    }


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    labels_dir = args.labels_dir.resolve()
    pcap_dir = args.pcap_dir.resolve()
    output_path = args.output.resolve()
    audit_path = args.audit_output.resolve()
    selected, counters = select_balanced_flows(
        labels_dir,
        seed=args.seed,
        maximum_per_family=args.maximum_per_family,
    )
    audit = label_audit(
        labels_dir=labels_dir,
        pcap_dir=pcap_dir,
        selected=selected,
        counters=counters,
        seed=args.seed,
        maximum_per_family=args.maximum_per_family,
    )
    audit["manifest_sha256"] = canonical_hash(audit)
    atomic_json(audit_path, audit)
    progress_path = (
        args.progress_output.resolve()
        if args.progress_output is not None
        else output_path.with_suffix(output_path.suffix + ".progress.json")
    )
    progress: dict[str, Any] = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
        "state": "source_audit_complete",
        "selected_rows": len(selected),
        "completed_pcaps": [],
        "active_pcap": None,
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    if args.audit_only:
        return audit
    grouped: dict[str, list[LabelFlow]] = defaultdict(list)
    for flow in selected:
        grouped[flow.pcap_name].append(flow)
    all_values: dict[str, tuple[list[int], list[float]]] = {}
    timezone_reports = []
    extraction_reports = []
    progress_files = {
        pcap_name: progress_path.with_name(
            f"{progress_path.stem}.{Path(pcap_name).stem}.json"
        )
        for pcap_name in grouped
    }
    progress = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
        "state": "parallel_pcap_processing",
        "selected_rows": len(selected),
        "pcap_worker_count": min(args.pcap_workers, len(grouped)),
        "completed_pcaps": [],
        "pcap_progress_files": {
            name: str(path) for name, path in sorted(progress_files.items())
        },
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=min(args.pcap_workers, len(grouped))
    ) as executor:
        futures = {
            executor.submit(
                process_pcap,
                pcap_path=pcap_dir / pcap_name,
                flows=flows,
                sequence_length=args.sequence_length,
                tolerance_us=args.tolerance_us,
                offset_probe_packets=args.offset_probe_packets,
                offset_minimum_unique_matches=args.offset_minimum_unique_matches,
                progress_path=progress_files[pcap_name],
                progress_interval_packets=args.progress_interval_packets,
            ): pcap_name
            for pcap_name, flows in sorted(grouped.items())
        }
        for future in concurrent.futures.as_completed(futures):
            pcap_name = futures[future]
            values, timezone_report, extraction_report = future.result()
            all_values.update(values)
            timezone_reports.append(timezone_report)
            extraction_reports.append(extraction_report)
            progress = {
                "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
                "state": "parallel_pcap_processing",
                "selected_rows": len(selected),
                "pcap_worker_count": min(args.pcap_workers, len(grouped)),
                "completed_pcaps": sorted(
                    report["pcap_path"] for report in extraction_reports
                ),
                "pending_pcaps": sorted(
                    name
                    for name in grouped
                    if name
                    not in {
                        Path(report["pcap_path"]).name
                        for report in extraction_reports
                    }
                ),
                "pcap_progress_files": {
                    name: str(path)
                    for name, path in sorted(progress_files.items())
                },
                "latest_completed_pcap": pcap_name,
                "updated_unix_seconds": time.time(),
            }
            progress["manifest_sha256"] = canonical_hash(progress)
            atomic_json(progress_path, progress)
    timezone_reports.sort(key=lambda report: report["pcap_path"])
    extraction_reports.sort(key=lambda report: report["pcap_path"])
    dataset = save_sequence_dataset(
        output_path=output_path,
        selected=selected,
        values=all_values,
        sequence_length=args.sequence_length,
        minimum_packets=args.minimum_packets,
    )
    report: dict[str, Any] = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_dataset_v1",
        "state": "complete_remote_pcap_sequence_materialization",
        "seed": args.seed,
        "maximum_per_family": args.maximum_per_family,
        "sequence_length": args.sequence_length,
        "minimum_packets": args.minimum_packets,
        "tolerance_us": args.tolerance_us,
        "source_audit": {
            "path": str(audit_path),
            "file_sha256": file_hash(audit_path),
            "manifest_sha256": audit["manifest_sha256"],
        },
        "timezone_inference": timezone_reports,
        "extraction": extraction_reports,
        "dataset": dataset,
        "claim_boundary": {
            "data_preparation_only": True,
            "model_effect_result": False,
            "timestamps_in_labels_are_treated_as_local_wall_time": True,
            "afternoon_csv_rows_with_pre_noon_hours_receive_12h_adjustment": True,
            "timezone_offset_is_inferred_without_labels_from_test_metrics": True,
            "unknown_or_test_labels_used_for_model_fitting": False,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_path.with_suffix(output_path.suffix + ".json"), report)
    progress = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_progress_v1",
        "state": "complete",
        "selected_rows": len(selected),
        "retained_rows": dataset["rows"],
        "completed_pcaps": [
            report["pcap_path"] for report in extraction_reports
        ],
        "output_path": str(output_path),
        "output_sha256": dataset["output_sha256"],
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--pcap-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--progress-output", type=Path)
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--maximum-per-family", type=int, default=5000)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--minimum-packets", type=int, default=2)
    parser.add_argument("--tolerance-us", type=int, default=2_000_000)
    parser.add_argument("--offset-probe-packets", type=int, default=5_000_000)
    parser.add_argument("--offset-minimum-unique-matches", type=int, default=5)
    parser.add_argument("--progress-interval-packets", type=int, default=5_000_000)
    parser.add_argument("--pcap-workers", type=int, default=5)
    parser.add_argument("--audit-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    report = prepare(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

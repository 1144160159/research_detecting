from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

import dpkt

from caeos_label_alignment import LabelResolver
from caeos_unified_dataset import atomic_json
from prepare_caeos_unified_multimodal_csv import packet_reader, parse_packet


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--pcap", required=True, type=Path)
    parser.add_argument("--source-member", required=True)
    parser.add_argument("--label-index", required=True, type=Path)
    parser.add_argument("--label-index-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--maximum-packets", type=int, default=1_000_000)
    parser.add_argument("--idle-seconds", type=float, default=30.0)
    parser.add_argument("--tolerance-ns", type=int, default=0)
    parser.add_argument("--maximum-unmatched-samples", type=int, default=1000)
    parser.add_argument(
        "--conflict-policy",
        choices=("reject", "malicious_over_benign_bidirectional"),
        default="reject",
    )
    parser.add_argument("--drop-unmatched-reason", action="append", default=[])
    parser.add_argument(
        "--time-nonoverlap-policy",
        choices=("reject", "nearest_official_same_tuple"),
        default="reject",
    )
    parser.add_argument("--official-boundary-split", action="store_true")
    return parser.parse_args()


def audit(
    args: argparse.Namespace, resolver: LabelResolver | None = None
) -> dict[str, Any]:
    if args.maximum_packets < 1:
        raise ValueError("maximum-packets must be positive")
    owns_resolver = resolver is None
    if resolver is None:
        resolver = LabelResolver(
            args.label_index,
            args.dataset_id,
            args.label_index_sha256,
            args.tolerance_ns,
            args.conflict_policy,
            args.time_nonoverlap_policy,
        )
    official_boundary_split = bool(
        getattr(args, "official_boundary_split", False)
    )
    idle_ns = int(args.idle_seconds * 1_000_000_000)
    active: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
    counters: Counter[str] = Counter()
    unmatched_samples: list[dict[str, Any]] = []
    unmatched_sample_counts: Counter[str] = Counter()
    conflicting_samples: list[dict[str, Any]] = []
    official_boundary_split_samples: list[dict[str, Any]] = []
    packet_limit_reached = False

    def flow_key_hash(state: dict[str, Any]) -> str:
        flow_material = b"\0".join(
            (
                args.dataset_id.encode("utf-8"),
                state["endpoint_a"],
                struct.pack("!H", int(state["port_a"])),
                state["endpoint_b"],
                struct.pack("!H", int(state["port_b"])),
                struct.pack("!H", int(state["protocol"])),
            )
        )
        return hashlib.sha256(flow_material).hexdigest()

    def finalize(key: tuple[Any, ...], reason: str) -> None:
        state = active.pop(key)
        result = resolver.resolve(
            args.source_member,
            state["endpoint_a"],
            state["port_a"],
            state["endpoint_b"],
            state["port_b"],
            state["protocol"],
            state["start_ns"],
            state["end_ns"],
        )
        if result.status == "conflicting_label" and official_boundary_split:
            split = resolver.split_packet_observations_by_official_labels(
                args.source_member,
                state["endpoint_a"],
                state["port_a"],
                state["endpoint_b"],
                state["port_b"],
                state["protocol"],
                state["packet_observations"],
            )
            if split["resolved"]:
                segments = split["segments"]
                counters["official_boundary_split_source_flows"] += 1
                counters["official_boundary_split_segments"] += len(segments)
                counters["official_boundary_split_packets"] += int(
                    split["source_packet_count"]
                )
                counters["official_boundary_split_packet_bytes"] += int(
                    split["source_packet_bytes"]
                )
                for segment in segments:
                    status = "aligned_unique_flow_official_boundary_split"
                    counters["flows"] += 1
                    counters[f"status::{status}"] += 1
                    counters[
                        f"status::{status}::protocol::{state['protocol']}"
                    ] += 1
                    counters[f"status::{status}::finalize::{reason}"] += 1
                    counters[f"finalize::{reason}"] += 1
                    counters[
                        "official_boundary_split_label::"
                        f"{segment['family_label']}::{segment['fine_label']}"
                    ] += 1
                if (
                    len(official_boundary_split_samples)
                    < args.maximum_unmatched_samples
                ):
                    official_boundary_split_samples.append(
                        {
                            "flow_key_hash": flow_key_hash(state),
                            "protocol": int(state["protocol"]),
                            "port_a": int(state["port_a"]),
                            "port_b": int(state["port_b"]),
                            "flow_start_ns": int(state["start_ns"]),
                            "flow_end_ns": int(state["end_ns"]),
                            "finalize_reason": reason,
                            **split,
                        }
                    )
                return
        counters["flows"] += 1
        counters[f"status::{result.status}"] += 1
        counters[f"status::{result.status}::protocol::{state['protocol']}"] += 1
        counters[f"status::{result.status}::finalize::{reason}"] += 1
        counters[f"finalize::{reason}"] += 1
        if result.status == "unmatched_label":
            diagnosis = resolver.diagnose_unmatched(
                args.source_member,
                state["endpoint_a"],
                state["port_a"],
                state["endpoint_b"],
                state["port_b"],
                state["protocol"],
                state["start_ns"],
                state["end_ns"],
            )
            diagnosis_reason = str(diagnosis["reason"])
            counters[f"unmatched_reason::{diagnosis_reason}"] += 1
            counters[
                f"unmatched_reason::{diagnosis_reason}::protocol::{state['protocol']}"
            ] += 1
            counters[
                f"unmatched_reason::{diagnosis_reason}::packets"
            ] += int(state["packet_count"])
            counters[
                f"unmatched_reason::{diagnosis_reason}::packet_bytes"
            ] += int(state["packet_bytes"])
            if diagnosis_reason in set(args.drop_unmatched_reason):
                counters["policy_excluded_flows"] += 1
                counters["policy_excluded_packets"] += int(state["packet_count"])
                counters["policy_excluded_packet_bytes"] += int(
                    state["packet_bytes"]
                )
                counters[
                    f"policy_exclusion_reason::{diagnosis_reason}"
                ] += 1
            if unmatched_sample_counts[diagnosis_reason] < args.maximum_unmatched_samples:
                unmatched_samples.append(
                    {
                        "flow_key_hash": flow_key_hash(state),
                        "protocol": int(state["protocol"]),
                        "port_a": int(state["port_a"]),
                        "port_b": int(state["port_b"]),
                        "flow_start_ns": int(state["start_ns"]),
                        "flow_end_ns": int(state["end_ns"]),
                        "duration_ns": int(state["end_ns"] - state["start_ns"]),
                        "packet_count": int(state["packet_count"]),
                        "packet_bytes": int(state["packet_bytes"]),
                        "finalize_reason": reason,
                        **diagnosis,
                    }
                )
                unmatched_sample_counts[diagnosis_reason] += 1
        elif result.status == "conflicting_label":
            diagnosis = resolver.diagnose_conflict(
                args.source_member,
                state["endpoint_a"],
                state["port_a"],
                state["endpoint_b"],
                state["port_b"],
                state["protocol"],
                state["start_ns"],
                state["end_ns"],
            )
            counters["conflict_reason::overlapping_external_records_have_different_labels"] += 1
            if len(conflicting_samples) < args.maximum_unmatched_samples:
                conflicting_samples.append(
                    {
                        "flow_key_hash": flow_key_hash(state),
                        "protocol": int(state["protocol"]),
                        "port_a": int(state["port_a"]),
                        "port_b": int(state["port_b"]),
                        "flow_start_ns": int(state["start_ns"]),
                        "flow_end_ns": int(state["end_ns"]),
                        "duration_ns": int(state["end_ns"] - state["start_ns"]),
                        "packet_count": int(state["packet_count"]),
                        "packet_bytes": int(state["packet_bytes"]),
                        "finalize_reason": reason,
                        **diagnosis,
                    }
                )

    capture_read_error: dict[str, str] | None = None
    try:
        with args.pcap.open("rb") as handle:
            for timestamp, frame in packet_reader(handle):
                counters["packets_read"] += 1
                parsed = parse_packet(float(timestamp), bytes(frame))
                if parsed is None:
                    counters["packets_skipped"] += 1
                else:
                    key, packet, metadata = parsed
                    counters["parsed_packets"] += 1
                    counters["parsed_packet_bytes"] += int(packet.frame_length)
                    state = active.get(key)
                    if state is not None and packet.timestamp_ns - state["end_ns"] > idle_ns:
                        finalize(key, "idle_timeout")
                        state = None
                    if state is None:
                        state = {
                            "endpoint_a": metadata["endpoint_a"],
                            "port_a": metadata["port_a"],
                            "endpoint_b": metadata["endpoint_b"],
                            "port_b": metadata["port_b"],
                            "protocol": metadata["protocol"],
                            "start_ns": packet.timestamp_ns,
                            "end_ns": packet.timestamp_ns,
                            "packet_count": 0,
                            "packet_bytes": 0,
                            "packet_observations": (
                                [] if official_boundary_split else None
                            ),
                        }
                        active[key] = state
                    else:
                        if packet.timestamp_ns < state["end_ns"]:
                            counters["pcap_timestamp_regressions_within_flow"] += 1
                        state["start_ns"] = min(
                            state["start_ns"], packet.timestamp_ns
                        )
                        state["end_ns"] = max(
                            state["end_ns"], packet.timestamp_ns
                        )
                        active.move_to_end(key)
                    state["packet_count"] += 1
                    state["packet_bytes"] += int(packet.frame_length)
                    if state["packet_observations"] is not None:
                        state["packet_observations"].append(
                            (packet.timestamp_ns, int(packet.frame_length))
                        )
                if counters["packets_read"] >= args.maximum_packets:
                    packet_limit_reached = True
                    break
        for key in list(active):
            finalize(key, "sample_boundary")
    except dpkt.dpkt.NeedData as error:
        capture_read_error = {
            "exception_type": type(error).__name__,
            "message": str(error),
            "rule": "capture ended inside a PCAP record header or packet body",
        }
        counters["capture_read_errors"] += 1
        counters["capture_read_error::NeedData"] += 1
        for key in list(active):
            finalize(key, "truncated_capture_boundary")
    except ValueError as error:
        if not str(error).startswith("unsupported capture magic:"):
            raise
        capture_read_error = {
            "exception_type": type(error).__name__,
            "message": str(error),
            "rule": "capture is empty or does not begin with supported PCAP/PCAPNG magic",
        }
        counters["capture_read_errors"] += 1
        counters["capture_read_error::ValueError"] += 1
        for key in list(active):
            finalize(key, "invalid_capture_boundary")
    finally:
        if owns_resolver:
            resolver.close()

    matched = sum(
        value
        for key, value in counters.items()
        if key.startswith("status::aligned_unique_") and key.count("::") == 1
    )
    flows = counters["flows"]
    report = {
        "schema_version": "caeos_label_alignment_coverage_smoke_v1",
        "scope": (
            "bounded_packet_prefix_not_formal_full_coverage"
            if packet_limit_reached
            else (
                "incomplete_pcap_file_with_audited_read_error"
                if capture_read_error is not None
                else "complete_pcap_file_not_dataset_wide_formal_coverage"
            )
        ),
        "dataset_id": args.dataset_id,
        "pcap": str(args.pcap),
        "pcap_size": args.pcap.stat().st_size,
        "complete_pcap_read": not packet_limit_reached and capture_read_error is None,
        "capture_read_error": capture_read_error,
        "source_member": args.source_member,
        "label_index": str(args.label_index),
        "label_index_sha256": args.label_index_sha256,
        "maximum_packets": args.maximum_packets,
        "idle_seconds": args.idle_seconds,
        "tolerance_ns": args.tolerance_ns,
        "conflict_policy": args.conflict_policy,
        "time_nonoverlap_policy": args.time_nonoverlap_policy,
        "official_boundary_split": official_boundary_split,
        "label_exclusion_summary": {
            "rule_version": "caeos_label_exclusion_v1",
            "rule": (
                "exclude generated rows only when unmatched diagnosis reason is "
                "explicitly approved; source PCAP is unchanged"
            ),
            "approved_reasons": sorted(set(args.drop_unmatched_reason)),
            "total_finalized_flows": flows,
            "excluded_flows": int(counters.get("policy_excluded_flows", 0)),
            "excluded_flow_fraction": (
                int(counters.get("policy_excluded_flows", 0)) / flows
                if flows
                else 0.0
            ),
            "excluded_packets": int(counters.get("policy_excluded_packets", 0)),
            "excluded_packet_fraction": (
                int(counters.get("policy_excluded_packets", 0))
                / int(counters.get("parsed_packets", 0))
                if counters.get("parsed_packets", 0)
                else 0.0
            ),
            "excluded_packet_bytes": int(
                counters.get("policy_excluded_packet_bytes", 0)
            ),
            "excluded_packet_byte_fraction": (
                int(counters.get("policy_excluded_packet_bytes", 0))
                / int(counters.get("parsed_packet_bytes", 0))
                if counters.get("parsed_packet_bytes", 0)
                else 0.0
            ),
            "reason_counts": {
                key.removeprefix("policy_exclusion_reason::"): value
                for key, value in sorted(counters.items())
                if key.startswith("policy_exclusion_reason::")
            },
            "source_pcaps_modified": False,
        },
        "counters": dict(sorted(counters.items())),
        "unmatched_samples": unmatched_samples,
        "unmatched_samples_truncated": (
            counters["status::unmatched_label"] > len(unmatched_samples)
        ),
        "unmatched_samples_by_reason": dict(sorted(unmatched_sample_counts.items())),
        "unmatched_samples_truncated_by_reason": {
            key.removeprefix("unmatched_reason::"): (
                int(value)
                > int(
                    unmatched_sample_counts[
                        key.removeprefix("unmatched_reason::")
                    ]
                )
            )
            for key, value in sorted(counters.items())
            if key.startswith("unmatched_reason::") and key.count("::") == 1
        },
        "conflicting_samples": conflicting_samples,
        "conflicting_samples_truncated": (
            counters["status::conflicting_label"] > len(conflicting_samples)
        ),
        "official_boundary_split_samples": official_boundary_split_samples,
        "matched_flows": matched,
        "coverage_fraction": matched / flows if flows else 0.0,
        "formal_gate_passed": False,
        "formal_gate_reason": (
            "bounded packet prefix cannot replace all-flow coverage"
            if packet_limit_reached
            else (
                "capture parsing stopped before a complete physical EOF record"
                if capture_read_error is not None
                else "one complete PCAP file cannot replace dataset-wide coverage"
            )
        ),
    }
    atomic_json(args.output, report)
    return report


def main() -> None:
    print(json.dumps(audit(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

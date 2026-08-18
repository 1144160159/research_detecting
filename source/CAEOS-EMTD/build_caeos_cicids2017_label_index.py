from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file
from prepare_strict_v4_cicids2017_packet_sequences import (
    LabelFlow,
    infer_timezone_offset_hours,
    iter_label_flows,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-dir", required=True, type=Path)
    parser.add_argument("--pcap-dir", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--tolerance-us", type=int, default=2_000_000)
    parser.add_argument("--offset-probe-packets", type=int, default=5_000_000)
    parser.add_argument("--offset-minimum-unique-matches", type=int, default=5)
    return parser.parse_args()


def unique_pcap_by_name(pcap_dir: Path) -> dict[str, Path]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in pcap_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".pcap", ".pcapng"}:
            grouped[path.name.lower()].append(path)
    duplicates = {name: paths for name, paths in grouped.items() if len(paths) != 1}
    if duplicates:
        raise ValueError(f"ambiguous PCAP names: {sorted(duplicates)[:10]}")
    return {name: paths[0] for name, paths in grouped.items()}


def build(args: argparse.Namespace) -> dict[str, Any]:
    counters: Counter[str] = Counter()
    flows = list(iter_label_flows(args.labels_dir, seed=args.seed, counters=counters))
    by_pcap: dict[str, list[LabelFlow]] = defaultdict(list)
    for flow in flows:
        by_pcap[flow.pcap_name.lower()].append(flow)
    pcaps = unique_pcap_by_name(args.pcap_dir)
    missing = sorted(set(by_pcap) - set(pcaps))
    if missing:
        raise ValueError(f"label CSVs have no unique PCAP: {missing}")

    timezone_reports: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    base_flow_id_counts: Counter[str] = Counter()
    for pcap_name in sorted(by_pcap):
        pcap_path = pcaps[pcap_name]
        pcap_flows = by_pcap[pcap_name]
        offset_hours, report = infer_timezone_offset_hours(
            pcap_path=pcap_path,
            flows=pcap_flows,
            tolerance_us=args.tolerance_us,
            maximum_packets=args.offset_probe_packets,
            minimum_unique_matches=args.offset_minimum_unique_matches,
        )
        report["pcap_size_bytes"] = pcap_path.stat().st_size
        timezone_reports[pcap_path.name] = report
        source_member = str(pcap_path.relative_to(args.source_root)).replace("\\", "/")
        offset_us = offset_hours * 3_600_000_000
        for flow in pcap_flows:
            duplicate_ordinal = base_flow_id_counts[flow.flow_id]
            base_flow_id_counts[flow.flow_id] += 1
            record_id = hashlib.sha256(
                f"{flow.flow_id}\0{duplicate_ordinal}".encode("utf-8")
            ).hexdigest()
            records.append(
                {
                    "record_id": record_id,
                    "source_member": source_member,
                    "src_ip": flow.source_ip,
                    "src_port": flow.source_port,
                    "dst_ip": flow.destination_ip,
                    "dst_port": flow.destination_port,
                    "protocol": flow.protocol,
                    "start_ns": (flow.start_wall_us + offset_us) * 1_000,
                    "end_ns": (flow.end_wall_us + offset_us) * 1_000,
                    "fine_label": flow.fine_label,
                    "family_label": flow.family,
                    "binary_label": int(flow.family != "Benign"),
                    "label_source": (
                        f"{args.labels_dir}/{flow.capture_id}.csv#"
                        f"{flow.flow_id}:{duplicate_ordinal}"
                    ),
                }
            )

    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index, "cicids2017", records, registry_sha256
    )
    audit = {
        "schema_version": "caeos_cicids2017_label_index_audit_v1",
        "dataset_id": "cicids2017",
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "labels_dir": str(args.labels_dir),
        "pcap_dir": str(args.pcap_dir),
        "source_root": str(args.source_root),
        "label_csv_sha256": {
            str(path): sha256_file(path)
            for path in sorted(args.labels_dir.glob("*.csv"))
        },
        "input_counters": dict(sorted(counters.items())),
        "timezone_reports": timezone_reports,
        "flow_record_count": len(records),
        "distinct_content_flow_ids": len(base_flow_id_counts),
        "duplicate_content_rows": sum(
            count - 1 for count in base_flow_id_counts.values() if count > 1
        ),
        "fine_label_counts": dict(sorted(Counter(item["fine_label"] for item in records).items())),
        "family_label_counts": dict(
            sorted(Counter(item["family_label"] for item in records).items())
        ),
        "label_index": index,
        "resolver_tolerance_ns": args.tolerance_us * 1_000,
        "ready_for_coverage_dry_run": True,
    }
    audit["audit_sha256"] = hashlib.sha256(
        json.dumps(audit, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(args.audit_output, audit)
    return audit


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

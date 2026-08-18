from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from audit_caeos_label_alignment_coverage import audit
from caeos_label_alignment import LabelResolver
from caeos_unified_dataset import atomic_json


DATASET_ID = "cic_bot_iot"
APPROVED_EXCLUSIONS = (
    "five_tuple_absent_from_official_flow_labels",
    "five_tuple_present_but_time_not_overlapping",
    "protocol_outside_official_tcp_udp_flow_labels",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap-root", required=True, type=Path)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--label-index", required=True, type=Path)
    parser.add_argument("--label-index-sha256", required=True)
    parser.add_argument("--audit-dir", required=True, type=Path)
    parser.add_argument("--reuse-audit-dir", type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--tolerance-ns", type=int, default=1_000_000)
    parser.add_argument("--idle-seconds", type=float, default=30.0)
    parser.add_argument("--maximum-unmatched-samples", type=int, default=100)
    return parser.parse_args()


def audit_name(relative_member: str, ordinal: int) -> str:
    digest = hashlib.sha256(relative_member.encode("utf-8")).hexdigest()[:16]
    return f"{ordinal:04d}_{digest}.json"


def reusable(report: dict[str, Any], pcap: Path, index_sha256: str) -> bool:
    return bool(
        report.get("dataset_id") == DATASET_ID
        and report.get("label_index_sha256") == index_sha256
        and report.get("pcap") == str(pcap)
        and int(report.get("pcap_size", -1)) == pcap.stat().st_size
        and report.get("complete_pcap_read") is True
    )


def apply_exclusion_policy(report: dict[str, Any]) -> dict[str, Any]:
    counters = report.setdefault("counters", {})
    for key in list(counters):
        if key.startswith("policy_exclusion_reason::"):
            del counters[key]
    excluded_flows = 0
    excluded_packets = 0
    excluded_packet_bytes = 0
    reason_counts: dict[str, int] = {}
    for reason in APPROVED_EXCLUSIONS:
        count = int(counters.get(f"unmatched_reason::{reason}", 0))
        if not count:
            continue
        reason_counts[reason] = count
        counters[f"policy_exclusion_reason::{reason}"] = count
        excluded_flows += count
        excluded_packets += int(
            counters.get(f"unmatched_reason::{reason}::packets", 0)
        )
        excluded_packet_bytes += int(
            counters.get(f"unmatched_reason::{reason}::packet_bytes", 0)
        )
    counters["policy_excluded_flows"] = excluded_flows
    counters["policy_excluded_packets"] = excluded_packets
    counters["policy_excluded_packet_bytes"] = excluded_packet_bytes
    flows = int(counters.get("flows", 0))
    parsed_packets = int(counters.get("parsed_packets", 0))
    parsed_packet_bytes = int(counters.get("parsed_packet_bytes", 0))
    report["label_exclusion_summary"] = {
        "rule_version": "caeos_label_exclusion_v1",
        "rule": (
            "exclude generated rows only when unmatched diagnosis reason is "
            "explicitly approved; source PCAP is unchanged"
        ),
        "approved_reasons": sorted(APPROVED_EXCLUSIONS),
        "total_finalized_flows": flows,
        "excluded_flows": excluded_flows,
        "excluded_flow_fraction": excluded_flows / flows if flows else 0.0,
        "excluded_packets": excluded_packets,
        "excluded_packet_fraction": (
            excluded_packets / parsed_packets if parsed_packets else 0.0
        ),
        "excluded_packet_bytes": excluded_packet_bytes,
        "excluded_packet_byte_fraction": (
            excluded_packet_bytes / parsed_packet_bytes
            if parsed_packet_bytes
            else 0.0
        ),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_pcaps_modified": False,
    }
    report["policy_reclassified_from_complete_audit"] = True
    return report


def summarize(
    pcaps: list[Path],
    reports: list[dict[str, Any]],
    label_index: Path,
    label_index_sha256: str,
) -> dict[str, Any]:
    counters: Counter[str] = Counter()
    for report in reports:
        counters.update(
            {
                key: int(value)
                for key, value in report.get("counters", {}).items()
                if isinstance(value, int)
            }
        )
    flows = counters["flows"]
    matched = sum(int(report.get("matched_flows", 0)) for report in reports)
    excluded_flows = counters["policy_excluded_flows"]
    conflicts = counters["status::conflicting_label"]
    unmatched = counters["status::unmatched_label"]
    effective_denominator = flows - excluded_flows
    effective_coverage = (
        matched / effective_denominator if effective_denominator > 0 else 0.0
    )
    all_complete = len(reports) == len(pcaps) and all(
        report.get("complete_pcap_read") is True for report in reports
    )
    only_approved_unmatched = unmatched == excluded_flows
    formal_label_gate = bool(
        all_complete
        and conflicts == 0
        and only_approved_unmatched
        and effective_coverage == 1.0
    )
    return {
        "schema_version": "caeos_bot_iot_all_pcap_label_audit_v1",
        "dataset_id": DATASET_ID,
        "scope": "all_discovered_pcap_files",
        "pcap_file_count": len(pcaps),
        "processed_pcap_file_count": len(reports),
        "pcap_total_bytes": sum(path.stat().st_size for path in pcaps),
        "label_index": str(label_index),
        "label_index_sha256": label_index_sha256,
        "approved_exclusion_reasons": list(APPROVED_EXCLUSIONS),
        "counters": dict(sorted(counters.items())),
        "matched_flows": matched,
        "raw_coverage_fraction": matched / flows if flows else 0.0,
        "effective_coverage_fraction": effective_coverage,
        "excluded_flows": excluded_flows,
        "excluded_flow_fraction": excluded_flows / flows if flows else 0.0,
        "excluded_packets": counters["policy_excluded_packets"],
        "excluded_packet_fraction": (
            counters["policy_excluded_packets"] / counters["parsed_packets"]
            if counters["parsed_packets"]
            else 0.0
        ),
        "excluded_packet_bytes": counters["policy_excluded_packet_bytes"],
        "excluded_packet_byte_fraction": (
            counters["policy_excluded_packet_bytes"]
            / counters["parsed_packet_bytes"]
            if counters["parsed_packet_bytes"]
            else 0.0
        ),
        "conflicting_flows": conflicts,
        "unmatched_flows": unmatched,
        "all_pcaps_complete": all_complete,
        "all_unmatched_flows_have_approved_exclusion_reason": only_approved_unmatched,
        "formal_label_gate_passed": formal_label_gate,
        "formal_label_gate_reason": (
            "all discovered PCAP files read completely; every retained flow matched "
            "one official label and every excluded flow used an approved reason"
            if formal_label_gate
            else "dataset-wide PCAP processing or retained-flow label coverage incomplete"
        ),
        "source_pcaps_modified": False,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    pcaps = sorted(path.resolve() for path in args.pcap_root.rglob("*.pcap"))
    if not pcaps:
        raise ValueError(f"no PCAP files below {args.pcap_root}")
    args.audit_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    resolver = LabelResolver(
        args.label_index,
        DATASET_ID,
        args.label_index_sha256,
        args.tolerance_ns,
        "reject",
        "reject",
    )
    try:
        for ordinal, pcap in enumerate(pcaps, start=1):
            source_member = pcap.relative_to(args.dataset_root.resolve()).as_posix()
            audit_path = args.audit_dir / audit_name(source_member, ordinal)
            report: dict[str, Any] | None = None
            candidate_path = audit_path
            reuse_audit_dir = getattr(args, "reuse_audit_dir", None)
            if not candidate_path.is_file() and reuse_audit_dir is not None:
                candidate_path = reuse_audit_dir / audit_path.name
            if candidate_path.is_file():
                candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
                if reusable(candidate, pcap, args.label_index_sha256):
                    report = apply_exclusion_policy(candidate)
                    atomic_json(audit_path, report)
            if report is None:
                report = audit(
                    SimpleNamespace(
                        dataset_id=DATASET_ID,
                        pcap=pcap,
                        source_member=source_member,
                        label_index=args.label_index,
                        label_index_sha256=args.label_index_sha256,
                        output=audit_path,
                        maximum_packets=2**63 - 1,
                        idle_seconds=args.idle_seconds,
                        tolerance_ns=args.tolerance_ns,
                        maximum_unmatched_samples=args.maximum_unmatched_samples,
                        conflict_policy="reject",
                        drop_unmatched_reason=list(APPROVED_EXCLUSIONS),
                        time_nonoverlap_policy="reject",
                    ),
                    resolver=resolver,
                )
                report = apply_exclusion_policy(report)
                atomic_json(audit_path, report)
            reports.append(report)
            checkpoint = summarize(
                pcaps, reports, args.label_index, args.label_index_sha256
            )
            checkpoint["last_completed_ordinal"] = ordinal
            checkpoint["last_completed_pcap"] = str(pcap)
            checkpoint["per_pcap_audit_dir"] = str(args.audit_dir)
            atomic_json(args.summary_output, checkpoint)
            print(
                json.dumps(
                    {
                        "ordinal": ordinal,
                        "total": len(pcaps),
                        "pcap": str(pcap),
                        "flows": report["counters"]["flows"],
                        "coverage_fraction": report["coverage_fraction"],
                        "complete_pcap_read": report["complete_pcap_read"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
    finally:
        resolver.close()
    return summarize(pcaps, reports, args.label_index, args.label_index_sha256)


def main() -> None:
    args = parse_arguments()
    report = run(args)
    atomic_json(args.summary_output, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

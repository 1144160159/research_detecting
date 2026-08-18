from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from audit_caeos_label_alignment_coverage import audit
from caeos_label_alignment import LabelResolver
from caeos_unified_dataset import atomic_json


APPROVED_EXCLUSIONS = (
    "five_tuple_absent_from_official_flow_labels",
    "five_tuple_present_but_time_not_overlapping",
    "protocol_outside_official_tcp_udp_flow_labels",
)
APPROVED_CONFLICT_EXCLUSION = (
    "overlapping_official_records_binary_malicious_consensus_"
    "multiclass_ambiguous"
)
PCAP_SUFFIXES = (".pcap", ".pcapng", ".cap")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--pcap-root", action="append", default=[], type=Path)
    parser.add_argument("--archive-root", action="append", default=[], type=Path)
    parser.add_argument(
        "--archive-member-mode", choices=("pcap_suffix", "all_files"), default="pcap_suffix"
    )
    parser.add_argument("--label-index", required=True, type=Path)
    parser.add_argument("--label-index-sha256", required=True)
    parser.add_argument("--inventory-output", required=True, type=Path)
    parser.add_argument("--audit-dir", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--temporary-dir", required=True, type=Path)
    parser.add_argument("--tolerance-ns", type=int, default=1_000_000)
    parser.add_argument("--idle-seconds", type=float, default=30.0)
    parser.add_argument("--maximum-unmatched-samples", type=int, default=100)
    parser.add_argument(
        "--conflict-policy",
        choices=("reject", "malicious_over_benign_bidirectional"),
        default="reject",
    )
    parser.add_argument(
        "--conflict-exclusion-policy",
        choices=("reject", "binary_malicious_consensus_multiclass_ambiguous"),
        default="reject",
        help=(
            "Optionally exclude, rather than relabel, conflicting flows only when "
            "the complete stored conflict evidence proves that every candidate "
            "official record has binary_label=1 while fine/family labels disagree."
        ),
    )
    parser.add_argument(
        "--conflict-exclusion-evidence",
        type=Path,
        help="Immutable manifest for the complete per-flow conflict inventory.",
    )
    parser.add_argument(
        "--time-nonoverlap-policy",
        choices=("reject", "nearest_official_same_tuple"),
        default="reject",
    )
    parser.add_argument("--official-boundary-split", action="store_true")
    parser.add_argument(
        "--authority-granularity",
        choices=("official_flow_label", "documented_single_class_capture"),
        default="official_flow_label",
    )
    parser.add_argument(
        "--source-quality-policy",
        type=Path,
        help=(
            "Optional immutable allowlist for exact corrupt/empty sources. "
            "It enables a separate quality-adjusted gate and never changes "
            "formal_label_gate_passed."
        ),
    )
    parser.add_argument(
        "--summarize-existing-only",
        action="store_true",
        help=(
            "Validate and aggregate every cached per-source audit without "
            "opening PCAP data. Fails if any frozen source audit is missing "
            "or no longer reusable."
        ),
    )
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def direct_item(path: Path, dataset_root: Path) -> dict[str, Any]:
    stat = path.stat()
    logical = relative(path, dataset_root)
    return {
        "kind": "direct_pcap",
        "logical_source_member": logical,
        "source_member": logical,
        "path": str(path.resolve()),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def archive_items(
    archive: Path, dataset_root: Path, member_mode: str
) -> list[dict[str, Any]]:
    stat = archive.stat()
    archive_relative = relative(archive, dataset_root)
    result: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive) as handle:
        for info in handle.infolist():
            if info.is_dir():
                continue
            if member_mode == "pcap_suffix" and not info.filename.lower().endswith(
                PCAP_SUFFIXES
            ):
                continue
            logical = f"{archive_relative}::{info.filename}"
            result.append(
                {
                    "kind": "zip_member",
                    "logical_source_member": logical,
                    "source_member": logical,
                    "archive_path": str(archive.resolve()),
                    "archive_size": stat.st_size,
                    "archive_mtime_ns": stat.st_mtime_ns,
                    "member": info.filename,
                    "member_size": info.file_size,
                    "member_crc32": f"{info.CRC:08x}",
                    "size": info.file_size,
                }
            )
    return result


def build_inventory(args: argparse.Namespace) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for root in args.pcap_root:
        paths = sorted(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in PCAP_SUFFIXES
        )
        items.extend(direct_item(path, args.dataset_root) for path in paths)
    for root in args.archive_root:
        for archive in sorted(path for path in root.rglob("*.zip") if path.is_file()):
            items.extend(
                archive_items(archive, args.dataset_root, args.archive_member_mode)
            )
    items.sort(key=lambda item: item["logical_source_member"])
    logical = [item["logical_source_member"] for item in items]
    if not items:
        raise ValueError("no PCAP inputs discovered")
    if len(logical) != len(set(logical)):
        raise ValueError("duplicate logical PCAP source members discovered")
    payload = {
        "schema_version": "caeos_all_pcap_member_inventory_v1",
        "dataset_id": args.dataset_id,
        "dataset_root": str(args.dataset_root.resolve()),
        "archive_member_mode": args.archive_member_mode,
        "items": items,
    }
    payload["inventory_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload


def freeze_inventory(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    if path.is_file():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != candidate:
            raise ValueError(
                "source inventory drift detected; preserve the old manifest and start a new run root"
            )
        return existing
    atomic_json(path, candidate)
    return candidate


def audit_name(item: dict[str, Any], ordinal: int) -> str:
    digest = hashlib.sha256(
        item["logical_source_member"].encode("utf-8")
    ).hexdigest()[:16]
    return f"{ordinal:06d}_{digest}.json"


def stable_audited_read_failure(report: dict[str, Any]) -> bool:
    error = report.get("capture_read_error")
    counters = report.get("counters", {})
    failure = (
        error.get("exception_type"),
        error.get("rule"),
    ) if isinstance(error, dict) else (None, None)
    approved = {
        (
            "NeedData",
            "capture ended inside a PCAP record header or packet body",
        ),
        (
            "ValueError",
            "capture is empty or does not begin with supported PCAP/PCAPNG magic",
        ),
    }
    return bool(
        report.get("complete_pcap_read") is False
        and isinstance(error, dict)
        and failure in approved
        and int(counters.get("capture_read_errors", 0)) == 1
        and int(counters.get(f"capture_read_error::{failure[0]}", 0)) == 1
    )


def load_source_quality_policy(
    path: Path | None,
    *,
    dataset_id: str,
    inventory_sha256: str,
) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, None
    raw = path.read_bytes()
    policy = json.loads(raw.decode("utf-8"))
    if policy.get("schema_version") != "caeos_source_quality_policy_v1":
        raise ValueError("unsupported source quality policy schema")
    if policy.get("dataset_id") != dataset_id:
        raise ValueError("source quality policy dataset mismatch")
    if policy.get("inventory_sha256") != inventory_sha256:
        raise ValueError("source quality policy inventory mismatch")
    exceptions = policy.get("exceptions")
    if not isinstance(exceptions, list):
        raise ValueError("source quality policy exceptions must be a list")
    sources = [entry.get("source") for entry in exceptions]
    if any(not isinstance(source, str) or not source for source in sources):
        raise ValueError("every source quality exception needs a source")
    if len(sources) != len(set(sources)):
        raise ValueError("duplicate source quality exception")
    return policy, hashlib.sha256(raw).hexdigest()


def _mapping_matches(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def resolve_source_quality_exceptions(
    policy: dict[str, Any] | None,
    inventory: dict[str, Any],
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    report_by_source = {
        report.get("all_pcap_member_source", {}).get(
            "logical_source_member", report.get("source_member")
        ): report
        for report in reports
    }
    item_by_source = {
        item["logical_source_member"]: item for item in inventory["items"]
    }
    exception_by_source = {
        entry["source"]: entry for entry in (policy or {}).get("exceptions", [])
    }
    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for source, report in report_by_source.items():
        if report.get("capture_read_error") is None:
            continue
        item = item_by_source[source]
        exception = exception_by_source.get(source)
        reasons: list[str] = []
        if exception is None:
            reasons.append("source is not allowlisted")
        else:
            action = exception.get("action")
            expected_source = exception.get("expected_source", {})
            expected_error = exception.get("expected_error", {})
            expected_counters = exception.get("expected_counters", {})
            expected_report = exception.get("expected_report", {})
            if action not in {
                "retain_complete_records_before_truncated_tail",
                "retain_complete_flows_before_truncated_tail",
                "exclude_zero_length_archive_member",
            }:
                reasons.append("unsupported action")
            if not _mapping_matches(item, expected_source):
                reasons.append("source metadata mismatch")
            if not _mapping_matches(report.get("capture_read_error", {}), expected_error):
                reasons.append("capture error mismatch")
            if not _mapping_matches(report.get("counters", {}), expected_counters):
                reasons.append("counter evidence mismatch")
            if not _mapping_matches(report, expected_report):
                reasons.append("report evidence mismatch")
            if action in {
                "retain_complete_records_before_truncated_tail",
                "retain_complete_flows_before_truncated_tail",
            }:
                if report.get("capture_read_error", {}).get("exception_type") != "NeedData":
                    reasons.append("truncated-tail action requires NeedData")
                if int(report.get("counters", {}).get("parsed_packets", 0)) <= 0:
                    reasons.append("truncated-tail action requires recovered packets")
            if action == "retain_complete_flows_before_truncated_tail":
                counters = report.get("counters", {})
                total = int(counters.get("finalize::truncated_capture_boundary", 0))
                matched = int(
                    counters.get(
                        "status::aligned_unique_flow::finalize::truncated_capture_boundary",
                        0,
                    )
                )
                unmatched = int(
                    counters.get(
                        "status::unmatched_label::finalize::truncated_capture_boundary",
                        0,
                    )
                )
                if total <= 0 or matched + unmatched != total:
                    reasons.append(
                        "complete-flow action requires an exact truncated-boundary flow partition"
                    )
            if action == "exclude_zero_length_archive_member":
                if int(item.get("size", -1)) != 0:
                    reasons.append("zero-length action requires a zero-byte source")
                if int(report.get("counters", {}).get("flows", 0)) != 0:
                    reasons.append("zero-length action requires zero flows")
        record = {
            "source": source,
            "action": exception.get("action") if exception else None,
        }
        if reasons:
            record["reasons"] = reasons
            unresolved.append(record)
        else:
            record["justification"] = exception.get("justification")
            resolved.append(record)

    processed_sources = set(report_by_source)
    pending_allowlist_sources = sorted(set(exception_by_source) - processed_sources)
    unknown_allowlist_sources = sorted(set(exception_by_source) - set(item_by_source))
    if unknown_allowlist_sources:
        unresolved.extend(
            {
                "source": source,
                "action": exception_by_source[source].get("action"),
                "reasons": ["allowlisted source is absent from frozen inventory"],
            }
            for source in unknown_allowlist_sources
        )
    failure_sources = {
        source
        for source, report in report_by_source.items()
        if report.get("capture_read_error") is not None
    }
    resolved_sources = {record["source"] for record in resolved}
    return {
        "resolved": resolved,
        "unresolved": unresolved,
        "pending_allowlist_sources": pending_allowlist_sources,
        "all_failures_resolved": not unresolved
        and failure_sources == resolved_sources,
    }


def reusable(
    report: dict[str, Any],
    item: dict[str, Any],
    dataset_id: str,
    index_sha256: str,
    *,
    tolerance_ns: int | None = None,
    idle_seconds: float | None = None,
    conflict_policy: str | None = None,
    time_nonoverlap_policy: str | None = None,
    official_boundary_split: bool | None = None,
) -> bool:
    return bool(
        report.get("dataset_id") == dataset_id
        and report.get("label_index_sha256") == index_sha256
        and (
            report.get("complete_pcap_read") is True
            or stable_audited_read_failure(report)
        )
        and report.get("all_pcap_member_source") == item
        and (
            tolerance_ns is None
            or int(report.get("tolerance_ns", -1)) == int(tolerance_ns)
        )
        and (
            idle_seconds is None
            or float(report.get("idle_seconds", -1.0)) == float(idle_seconds)
        )
        and (
            conflict_policy is None
            or report.get("conflict_policy") == conflict_policy
        )
        and (
            time_nonoverlap_policy is None
            or report.get("time_nonoverlap_policy") == time_nonoverlap_policy
        )
        and (
            official_boundary_split is None
            or bool(report.get("official_boundary_split", False))
            == official_boundary_split
            or (
                official_boundary_split
                and int(
                    report.get("counters", {}).get(
                        "status::conflicting_label", 0
                    )
                )
                == 0
            )
        )
    )


def apply_exclusion_policy(
    report: dict[str, Any],
    source_quality_exception: dict[str, Any] | None = None,
    conflict_exclusion_policy: str = "reject",
) -> dict[str, Any]:
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
    excluded_unmatched_flows = excluded_flows
    excluded_conflicting_flows = 0
    if conflict_exclusion_policy not in {
        "reject",
        "binary_malicious_consensus_multiclass_ambiguous",
    }:
        raise ValueError(
            f"unsupported conflict exclusion policy: {conflict_exclusion_policy}"
        )
    conflict_count = int(counters.get("status::conflicting_label", 0))
    if (
        conflict_exclusion_policy
        == "binary_malicious_consensus_multiclass_ambiguous"
        and conflict_count
    ):
        samples = report.get("conflicting_samples", [])
        if report.get("conflicting_samples_truncated") or len(samples) != conflict_count:
            raise ValueError(
                "binary-malicious conflict exclusion requires complete per-flow "
                "conflict evidence"
            )
        conflict_packets = 0
        conflict_packet_bytes = 0
        for sample in samples:
            label_counts = sample.get("candidate_label_counts", {})
            if len(label_counts) < 2:
                raise ValueError(
                    "conflict exclusion evidence must contain multiple official labels"
                )
            binary_labels: set[int] = set()
            for label_key in label_counts:
                marker = "::binary="
                if marker not in label_key:
                    raise ValueError(
                        "conflict exclusion evidence is missing an official binary label"
                    )
                binary_labels.add(int(label_key.rsplit(marker, 1)[1]))
            if binary_labels != {1}:
                raise ValueError(
                    "conflict exclusion is allowed only for unanimous malicious "
                    "binary labels with ambiguous multiclass labels"
                )
            conflict_packets += int(sample.get("packet_count", 0))
            conflict_packet_bytes += int(sample.get("packet_bytes", 0))
        excluded_conflicting_flows = conflict_count
        excluded_flows += excluded_conflicting_flows
        excluded_packets += conflict_packets
        excluded_packet_bytes += conflict_packet_bytes
        reason_counts[APPROVED_CONFLICT_EXCLUSION] = excluded_conflicting_flows
        counters[
            f"policy_exclusion_reason::{APPROVED_CONFLICT_EXCLUSION}"
        ] = excluded_conflicting_flows
    excluded_matched_flows = 0
    if (
        source_quality_exception or {}
    ).get("action") == "retain_complete_flows_before_truncated_tail":
        truncated_flows = int(
            counters.get("finalize::truncated_capture_boundary", 0)
        )
        truncated_matched = int(
            counters.get(
                "status::aligned_unique_flow::finalize::truncated_capture_boundary",
                0,
            )
        )
        truncated_unmatched = int(
            counters.get(
                "status::unmatched_label::finalize::truncated_capture_boundary",
                0,
            )
        )
        if (
            truncated_flows <= 0
            or truncated_matched + truncated_unmatched != truncated_flows
            or truncated_unmatched > excluded_unmatched_flows
        ):
            raise ValueError(
                "truncated-boundary source policy does not match finalized-flow counters"
            )
        excluded_matched_flows = truncated_matched
        excluded_flows += excluded_matched_flows
        reason_counts["source_quality::truncated_capture_boundary"] = truncated_flows
        counters[
            "policy_exclusion_reason::source_quality::truncated_capture_boundary"
        ] = truncated_flows
    counters["policy_excluded_unmatched_flows"] = excluded_unmatched_flows
    counters["policy_excluded_conflicting_flows"] = excluded_conflicting_flows
    counters["policy_excluded_matched_flows"] = excluded_matched_flows
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
        "approved_reasons": sorted(
            list(APPROVED_EXCLUSIONS)
            + (
                [APPROVED_CONFLICT_EXCLUSION]
                if conflict_exclusion_policy
                == "binary_malicious_consensus_multiclass_ambiguous"
                else []
            )
        ),
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
        "excluded_unmatched_flows": excluded_unmatched_flows,
        "excluded_conflicting_flows": excluded_conflicting_flows,
        "excluded_matched_flows": excluded_matched_flows,
        "retained_flows": flows - excluded_flows,
        "source_pcaps_modified": False,
    }
    report["policy_reclassified_from_complete_audit"] = True
    return report


def advise_dontneed(path: Path) -> None:
    if not hasattr(os, "posix_fadvise") or not hasattr(os, "POSIX_FADV_DONTNEED"):
        return
    try:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.posix_fadvise(descriptor, 0, 0, os.POSIX_FADV_DONTNEED)
        finally:
            os.close(descriptor)
    except OSError:
        pass


def summarize(
    args: argparse.Namespace,
    inventory: dict[str, Any],
    reports: list[dict[str, Any]],
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
    excluded = counters["policy_excluded_flows"]
    excluded_matched = counters["policy_excluded_matched_flows"]
    excluded_unmatched = counters.get(
        "policy_excluded_unmatched_flows", excluded - excluded_matched
    )
    excluded_conflicting = counters.get("policy_excluded_conflicting_flows", 0)
    retained_matched = matched - excluded_matched
    conflicts = counters["status::conflicting_label"]
    unmatched = counters["status::unmatched_label"]
    denominator = flows - excluded
    effective_coverage = retained_matched / denominator if denominator > 0 else 0.0
    all_complete = len(reports) == len(inventory["items"]) and all(
        report.get("complete_pcap_read") is True for report in reports
    )
    source_read_failures = [
        {
            "source": report.get("all_pcap_member_source", {}).get(
                "logical_source_member", report.get("source_member")
            ),
            "capture_read_error": report.get("capture_read_error"),
        }
        for report in reports
        if report.get("capture_read_error") is not None
    ]
    policy = getattr(args, "source_quality_policy_data", None)
    policy_sha256 = getattr(args, "source_quality_policy_sha256", None)
    policy_path = getattr(args, "source_quality_policy", None)
    if policy is None and policy_path is not None:
        policy, policy_sha256 = load_source_quality_policy(
            policy_path,
            dataset_id=args.dataset_id,
            inventory_sha256=inventory["inventory_sha256"],
        )
    source_quality = resolve_source_quality_exceptions(policy, inventory, reports)
    conflict_evidence_path = getattr(args, "conflict_exclusion_evidence", None)
    conflict_evidence_sha256 = None
    if conflict_evidence_path is not None:
        conflict_evidence_path = Path(conflict_evidence_path)
        if not conflict_evidence_path.is_file():
            raise ValueError("conflict exclusion evidence manifest does not exist")
        conflict_evidence_sha256 = hashlib.sha256(
            conflict_evidence_path.read_bytes()
        ).hexdigest()
    if (
        getattr(args, "conflict_exclusion_policy", "reject") != "reject"
        and conflict_evidence_path is None
    ):
        raise ValueError(
            "an explicit conflict exclusion policy requires an immutable evidence manifest"
        )
    resolved_source_names = {
        record["source"] for record in source_quality["resolved"]
    }
    all_sources_usable_or_quarantined = (
        len(reports) == len(inventory["items"])
        and not source_quality["pending_allowlist_sources"]
        and all(
            report.get("complete_pcap_read") is True
            or report.get("all_pcap_member_source", {}).get(
                "logical_source_member", report.get("source_member")
            )
            in resolved_source_names
            for report in reports
        )
    )
    approved_unmatched = unmatched == excluded_unmatched
    approved_conflicts = conflicts == excluded_conflicting
    approved_only = approved_unmatched and approved_conflicts
    formal_gate = bool(
        all_complete
        and approved_conflicts
        and approved_only
        and effective_coverage == 1.0
    )
    source_quality_adjusted_gate = bool(
        all_sources_usable_or_quarantined
        and source_quality["all_failures_resolved"]
        and approved_conflicts
        and approved_only
        and effective_coverage == 1.0
    )
    return {
        "schema_version": "caeos_all_pcap_member_label_audit_v1",
        "dataset_id": args.dataset_id,
        "scope": "all_frozen_direct_pcaps_and_zip_members",
        "authority_granularity": args.authority_granularity,
        "inventory": str(args.inventory_output),
        "inventory_sha256": inventory["inventory_sha256"],
        "source_count": len(inventory["items"]),
        "processed_source_count": len(reports),
        "source_total_uncompressed_bytes": sum(
            int(item["size"]) for item in inventory["items"]
        ),
        "label_index": str(args.label_index),
        "label_index_sha256": args.label_index_sha256,
        "conflict_policy": getattr(args, "conflict_policy", "reject"),
        "conflict_exclusion_policy": getattr(
            args, "conflict_exclusion_policy", "reject"
        ),
        "conflict_exclusion_evidence": (
            str(conflict_evidence_path) if conflict_evidence_path is not None else None
        ),
        "conflict_exclusion_evidence_sha256": conflict_evidence_sha256,
        "time_nonoverlap_policy": getattr(
            args, "time_nonoverlap_policy", "reject"
        ),
        "official_boundary_split": bool(
            getattr(args, "official_boundary_split", False)
        ),
        "approved_exclusion_reasons": list(APPROVED_EXCLUSIONS)
        + (
            [APPROVED_CONFLICT_EXCLUSION]
            if getattr(args, "conflict_exclusion_policy", "reject")
            == "binary_malicious_consensus_multiclass_ambiguous"
            else []
        ),
        "counters": dict(sorted(counters.items())),
        "matched_flows": matched,
        "retained_matched_flows": retained_matched,
        "policy_excluded_matched_flows": excluded_matched,
        "policy_excluded_unmatched_flows": excluded_unmatched,
        "policy_excluded_conflicting_flows": excluded_conflicting,
        "raw_coverage_fraction": matched / flows if flows else 0.0,
        "effective_coverage_fraction": effective_coverage,
        "excluded_flows": excluded,
        "excluded_flow_fraction": excluded / flows if flows else 0.0,
        "excluded_packets": counters["policy_excluded_packets"],
        "excluded_packet_fraction": (
            counters["policy_excluded_packets"] / counters["parsed_packets"]
            if counters["parsed_packets"]
            else 0.0
        ),
        "excluded_packet_bytes": counters["policy_excluded_packet_bytes"],
        "excluded_packet_byte_fraction": (
            counters["policy_excluded_packet_bytes"] / counters["parsed_packet_bytes"]
            if counters["parsed_packet_bytes"]
            else 0.0
        ),
        "conflicting_flows": conflicts,
        "retained_conflicting_flows": conflicts - excluded_conflicting,
        "unmatched_flows": unmatched,
        "all_sources_complete": all_complete,
        "all_sources_usable_or_quarantined": all_sources_usable_or_quarantined,
        "source_read_failure_count": len(source_read_failures),
        "source_read_failures": source_read_failures[:100],
        "source_read_failures_truncated": len(source_read_failures) > 100,
        "all_unmatched_flows_have_approved_exclusion_reason": approved_only,
        "all_conflicting_flows_have_approved_exclusion_reason": approved_conflicts,
        "formal_label_gate_passed": formal_gate,
        "formal_label_gate_reason": (
            (
                "all frozen PCAP sources read completely; every retained flow matched "
                "the documented single-class capture label and every excluded flow used "
                "an approved exclusion reason"
                if args.authority_granularity == "documented_single_class_capture"
                else "all frozen PCAP sources read completely; every retained flow matched "
                "one official fine label and every unmatched or binary-malicious multiclass-"
                "ambiguous flow used an approved exclusion reason"
            )
            if formal_gate
            else "dataset-wide processing or retained-flow label coverage incomplete"
        ),
        "source_quality_policy": str(policy_path) if policy_path is not None else None,
        "source_quality_policy_sha256": policy_sha256,
        "source_quality_resolved_count": len(source_quality["resolved"]),
        "source_quality_resolutions": source_quality["resolved"],
        "source_quality_unresolved": source_quality["unresolved"],
        "source_quality_pending_allowlist_sources": source_quality[
            "pending_allowlist_sources"
        ],
        "source_quality_adjusted_gate_passed": source_quality_adjusted_gate,
        "source_quality_adjusted_gate_reason": (
            "all frozen sources were either read completely or matched an exact "
            "immutable source-quality exception; every retained recoverable flow "
            "matched one official fine label and every unmatched or binary-malicious "
            "multiclass-ambiguous flow used an approved exclusion reason"
            if source_quality_adjusted_gate
            else "source-quality exceptions, processing coverage, or retained-flow "
            "label coverage remain incomplete"
        ),
        "source_pcaps_modified": False,
        "temporary_zip_members_retained": False,
    }


class Materializer:
    def __init__(self, temporary_dir: Path):
        self.temporary_dir = temporary_dir
        self.current_path: Path | None = None
        self.current_archive: zipfile.ZipFile | None = None

    def close(self) -> None:
        if self.current_archive is not None:
            self.current_archive.close()
            assert self.current_path is not None
            advise_dontneed(self.current_path)
        self.current_archive = None
        self.current_path = None

    def path_for(self, item: dict[str, Any]) -> tuple[Path, bool]:
        if item["kind"] == "direct_pcap":
            self.close()
            return Path(item["path"]), False
        archive_path = Path(item["archive_path"])
        if self.current_path != archive_path:
            self.close()
            self.current_path = archive_path
            self.current_archive = zipfile.ZipFile(archive_path)
        assert self.current_archive is not None
        digest = hashlib.sha256(
            item["logical_source_member"].encode("utf-8")
        ).hexdigest()[:24]
        suffix = Path(item["member"]).suffix.lower()
        if suffix not in PCAP_SUFFIXES:
            suffix = ".pcap"
        target = self.temporary_dir / f"{digest}{suffix}"
        target.unlink(missing_ok=True)
        with self.current_archive.open(item["member"]) as source, target.open("wb") as out:
            shutil.copyfileobj(source, out, length=8 * 1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        if target.stat().st_size != int(item["member_size"]):
            target.unlink(missing_ok=True)
            raise IOError(f"incomplete ZIP member extraction: {item['logical_source_member']}")
        return target, True


def progress_record(
    report: dict[str, Any],
    item: dict[str, Any],
    ordinal: int,
    total: int,
) -> dict[str, Any]:
    """Build a progress row, including valid header-only PCAP members."""
    return {
        "ordinal": ordinal,
        "total": total,
        "source": item["logical_source_member"],
        "flows": report.get("counters", {}).get("flows", 0),
        "coverage_fraction": report.get("coverage_fraction", 0.0),
        "complete_pcap_read": report.get("complete_pcap_read", False),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    args.audit_dir.mkdir(parents=True, exist_ok=True)
    args.temporary_dir.mkdir(parents=True, exist_ok=True)
    inventory = freeze_inventory(args.inventory_output, build_inventory(args))
    (
        args.source_quality_policy_data,
        args.source_quality_policy_sha256,
    ) = load_source_quality_policy(
        getattr(args, "source_quality_policy", None),
        dataset_id=args.dataset_id,
        inventory_sha256=inventory["inventory_sha256"],
    )
    exception_by_source = {
        entry["source"]: entry
        for entry in (args.source_quality_policy_data or {}).get("exceptions", [])
    }
    if getattr(args, "summarize_existing_only", False):
        reports: list[dict[str, Any]] = []
        for ordinal, item in enumerate(inventory["items"], start=1):
            audit_path = args.audit_dir / audit_name(item, ordinal)
            if not audit_path.is_file():
                raise ValueError(
                    f"missing cached audit for frozen source: {item['logical_source_member']}"
                )
            candidate = json.loads(audit_path.read_text(encoding="utf-8"))
            if not reusable(
                candidate,
                item,
                args.dataset_id,
                args.label_index_sha256,
                tolerance_ns=args.tolerance_ns,
                idle_seconds=args.idle_seconds,
                conflict_policy=args.conflict_policy,
                time_nonoverlap_policy=args.time_nonoverlap_policy,
                official_boundary_split=args.official_boundary_split,
            ):
                raise ValueError(
                    f"cached audit is not reusable for frozen source: "
                    f"{item['logical_source_member']}"
                )
            reports.append(
                apply_exclusion_policy(
                    candidate,
                    exception_by_source.get(item["logical_source_member"]),
                    getattr(args, "conflict_exclusion_policy", "reject"),
                )
            )
        final = summarize(args, inventory, reports)
        final["summary_mode"] = "validated_existing_per_source_audits"
        final["per_source_audit_dir"] = str(args.audit_dir)
        atomic_json(args.summary_output, final)
        return final
    reports: list[dict[str, Any]] = []
    resolver = LabelResolver(
        args.label_index,
        args.dataset_id,
        args.label_index_sha256,
        args.tolerance_ns,
        args.conflict_policy,
        args.time_nonoverlap_policy,
    )
    materializer = Materializer(args.temporary_dir)
    try:
        for ordinal, item in enumerate(inventory["items"], start=1):
            audit_path = args.audit_dir / audit_name(item, ordinal)
            report: dict[str, Any] | None = None
            if audit_path.is_file():
                candidate = json.loads(audit_path.read_text(encoding="utf-8"))
                if reusable(
                    candidate,
                    item,
                    args.dataset_id,
                    args.label_index_sha256,
                    tolerance_ns=args.tolerance_ns,
                    idle_seconds=args.idle_seconds,
                    conflict_policy=args.conflict_policy,
                    time_nonoverlap_policy=args.time_nonoverlap_policy,
                    official_boundary_split=args.official_boundary_split,
                ):
                    report = apply_exclusion_policy(
                        candidate,
                        exception_by_source.get(item["logical_source_member"]),
                        getattr(args, "conflict_exclusion_policy", "reject"),
                    )
                    atomic_json(audit_path, report)
            if report is None:
                pcap, temporary = materializer.path_for(item)
                try:
                    report = audit(
                        SimpleNamespace(
                            dataset_id=args.dataset_id,
                            pcap=pcap,
                            source_member=item["source_member"],
                            label_index=args.label_index,
                            label_index_sha256=args.label_index_sha256,
                            output=audit_path,
                            maximum_packets=2**63 - 1,
                            idle_seconds=args.idle_seconds,
                            tolerance_ns=args.tolerance_ns,
                            maximum_unmatched_samples=args.maximum_unmatched_samples,
                            conflict_policy=args.conflict_policy,
                            drop_unmatched_reason=list(APPROVED_EXCLUSIONS),
                            time_nonoverlap_policy=args.time_nonoverlap_policy,
                            official_boundary_split=args.official_boundary_split,
                        ),
                        resolver=resolver,
                    )
                    report["all_pcap_member_source"] = item
                    report = apply_exclusion_policy(
                        report,
                        exception_by_source.get(item["logical_source_member"]),
                        getattr(args, "conflict_exclusion_policy", "reject"),
                    )
                    atomic_json(audit_path, report)
                finally:
                    if temporary:
                        advise_dontneed(pcap)
                        pcap.unlink(missing_ok=True)
                    else:
                        advise_dontneed(pcap)
                    gc.collect()
            reports.append(report)
            checkpoint = summarize(args, inventory, reports)
            checkpoint["last_completed_ordinal"] = ordinal
            checkpoint["last_completed_source"] = item["logical_source_member"]
            checkpoint["per_source_audit_dir"] = str(args.audit_dir)
            atomic_json(args.summary_output, checkpoint)
            print(
                json.dumps(
                    progress_record(report, item, ordinal, len(inventory["items"])),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
    finally:
        materializer.close()
        resolver.close()
        for residue in args.temporary_dir.glob("*"):
            if residue.is_file():
                residue.unlink(missing_ok=True)
    final = summarize(args, inventory, reports)
    atomic_json(args.summary_output, final)
    return final


def main() -> None:
    args = parse_arguments()
    report = run(args)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json, sha256_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize(args: argparse.Namespace) -> dict[str, Any]:
    reports = [load(path) for path in args.report]
    dataset_ids = {str(report["dataset_id"]) for report in reports}
    if len(dataset_ids) != 1:
        raise ValueError(f"reports must belong to one dataset, got {dataset_ids}")
    dataset_id = next(iter(dataset_ids))
    totals: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    protocols: Counter[str] = Counter()
    alignment_statuses: Counter[str] = Counter()
    exclusion_reasons: Counter[str] = Counter()
    reason_protocols: Counter[str] = Counter()
    absent_udp_ports: Counter[str] = Counter()
    absent_tcp_ports: Counter[str] = Counter()
    absent_tcp_samples: list[dict[str, Any]] = []
    nearest_labels: Counter[str] = Counter()
    time_gaps_ns: list[int] = []
    unique_flow_hashes: set[str] = set()
    captures: list[dict[str, Any]] = []
    samples_complete = True
    for path, report in zip(args.report, reports):
        counters = report["counters"]
        capture_reasons: dict[str, int] = {}
        for key, value in counters.items():
            if key.startswith("unmatched_reason::") and key.count("::") == 1:
                reason = key.removeprefix("unmatched_reason::")
                reasons[reason] += int(value)
                capture_reasons[reason] = int(value)
            if key.startswith("status::unmatched_label::protocol::"):
                protocol = key.rsplit("::", 1)[-1]
                protocols[protocol] += int(value)
        totals["packets_read"] += int(counters["packets_read"])
        totals["parsed_packets"] += int(counters.get("parsed_packets", 0))
        totals["parsed_packet_bytes"] += int(
            counters.get("parsed_packet_bytes", 0)
        )
        totals["flows"] += int(counters["flows"])
        totals["matched_flows"] += int(report["matched_flows"])
        totals["unmatched_flows"] += int(counters.get("status::unmatched_label", 0))
        totals["policy_excluded_flows"] += int(
            counters.get("policy_excluded_flows", 0)
        )
        totals["policy_excluded_packets"] += int(
            counters.get("policy_excluded_packets", 0)
        )
        totals["policy_excluded_packet_bytes"] += int(
            counters.get("policy_excluded_packet_bytes", 0)
        )
        for key, value in counters.items():
            if (
                key.startswith("status::aligned_")
                and "::protocol::" not in key
                and "::finalize::" not in key
            ):
                alignment_statuses[key.removeprefix("status::")] += int(value)
            if key.startswith("policy_exclusion_reason::"):
                exclusion_reasons[
                    key.removeprefix("policy_exclusion_reason::")
                ] += int(value)
        samples_complete = samples_complete and not bool(
            report.get("unmatched_samples_truncated")
        )
        for sample in report.get("unmatched_samples", []):
            unique_flow_hashes.add(sample["flow_key_hash"])
            reason = sample["reason"]
            reason_protocols[f"{reason}::protocol::{sample['protocol']}"] += 1
            if reason == "five_tuple_absent_from_official_flow_labels" and int(
                sample["protocol"]
            ) == 17:
                ports = sorted((int(sample["port_a"]), int(sample["port_b"])))
                absent_udp_ports[f"{ports[0]}:{ports[1]}"] += 1
            if reason == "five_tuple_absent_from_official_flow_labels" and int(
                sample["protocol"]
            ) == 6:
                ports = sorted((int(sample["port_a"]), int(sample["port_b"])))
                absent_tcp_ports[f"{ports[0]}:{ports[1]}"] += 1
                absent_tcp_samples.append(
                    {
                        "pcap": Path(report["pcap"]).name,
                        "flow_key_hash": sample["flow_key_hash"],
                        "ports": f"{ports[0]}:{ports[1]}",
                        "flow_start_ns": int(sample["flow_start_ns"]),
                        "flow_end_ns": int(sample["flow_end_ns"]),
                        "finalize_reason": sample["finalize_reason"],
                    }
                )
            if reason == "five_tuple_present_but_time_not_overlapping":
                time_gaps_ns.append(int(sample["nearest_gap_ns"]))
                nearest_labels[
                    f"{sample['nearest_family_label']}::{sample['nearest_fine_label']}::"
                    f"binary={sample['nearest_binary_label']}"
                ] += 1
        captures.append(
            {
                "pcap": Path(report["pcap"]).name,
                "report_path": str(path),
                "report_sha256": sha256_file(path),
                "packets_read": int(counters["packets_read"]),
                "flows": int(counters["flows"]),
                "matched_flows": int(report["matched_flows"]),
                "unmatched_flows": int(counters.get("status::unmatched_label", 0)),
                "coverage_fraction": float(report["coverage_fraction"]),
                "unmatched_reasons": dict(sorted(capture_reasons.items())),
                "alignment_status_counts": {
                    key.removeprefix("status::"): int(value)
                    for key, value in counters.items()
                    if key.startswith("status::aligned_")
                    and "::protocol::" not in key
                    and "::finalize::" not in key
                },
                "label_exclusion_summary": report.get("label_exclusion_summary"),
                "unmatched_samples_truncated": bool(
                    report.get("unmatched_samples_truncated")
                ),
            }
        )
    coverage = (
        totals["matched_flows"] / totals["flows"] if totals["flows"] else 0.0
    )
    retained_flows = totals["flows"] - totals["policy_excluded_flows"]
    retained_coverage = (
        totals["matched_flows"] / retained_flows if retained_flows else 0.0
    )
    unresolved_retained_flows = max(0, retained_flows - totals["matched_flows"])
    exclusion_summary = {
        "rule_version": "caeos_label_exclusion_v1",
        "rule": (
            "exclude generated rows only when unmatched diagnosis reason is "
            "explicitly approved; source PCAP is unchanged"
        ),
        "source_pcaps_modified": False,
        "total_finalized_flows": totals["flows"],
        "excluded_flows": totals["policy_excluded_flows"],
        "excluded_flow_fraction": (
            totals["policy_excluded_flows"] / totals["flows"]
            if totals["flows"]
            else 0.0
        ),
        "total_parsed_packets": totals["parsed_packets"],
        "excluded_packets": totals["policy_excluded_packets"],
        "excluded_packet_fraction": (
            totals["policy_excluded_packets"] / totals["parsed_packets"]
            if totals["parsed_packets"]
            else 0.0
        ),
        "total_parsed_packet_bytes": totals["parsed_packet_bytes"],
        "excluded_packet_bytes": totals["policy_excluded_packet_bytes"],
        "excluded_packet_byte_fraction": (
            totals["policy_excluded_packet_bytes"]
            / totals["parsed_packet_bytes"]
            if totals["parsed_packet_bytes"]
            else 0.0
        ),
        "reason_counts": dict(sorted(exclusion_reasons.items())),
    }
    gap_summary: dict[str, Any] = {"count": len(time_gaps_ns)}
    if time_gaps_ns:
        ordered = sorted(time_gaps_ns)
        gap_summary.update(
            {
                "minimum_seconds": ordered[0] / 1_000_000_000,
                "median_seconds": statistics.median(ordered) / 1_000_000_000,
                "maximum_seconds": ordered[-1] / 1_000_000_000,
            }
        )
    result = {
        "schema_version": "caeos_unmatched_diagnostic_summary_v2",
        "dataset_id": dataset_id,
        "scope": "five_pcaps_bounded_prefix_coverage_not_formal_full_coverage",
        "captures": captures,
        "totals": dict(sorted(totals.items())),
        "coverage_fraction": coverage,
        "retained_flow_label_coverage_fraction": retained_coverage,
        "retained_flows": retained_flows,
        "unresolved_retained_flows": unresolved_retained_flows,
        "alignment_status_counts": dict(sorted(alignment_statuses.items())),
        "label_exclusion_summary": exclusion_summary,
        "unmatched_reason_counts": dict(sorted(reasons.items())),
        "unmatched_protocol_counts": dict(sorted(protocols.items())),
        "diagnostic_sample_counts": dict(sorted(reason_protocols.items())),
        "diagnostic_samples_complete": samples_complete,
        "unique_unmatched_flow_key_hashes_in_samples": len(unique_flow_hashes),
        "top_absent_udp_port_pairs": [
            {"ports": ports, "count": count}
            for ports, count in absent_udp_ports.most_common(20)
        ],
        "absent_tcp_port_pairs": [
            {"ports": ports, "count": count}
            for ports, count in absent_tcp_ports.most_common()
        ],
        "absent_tcp_samples": absent_tcp_samples,
        "time_nonoverlap_gap": gap_summary,
        "time_nonoverlap_nearest_label_counts": dict(sorted(nearest_labels.items())),
        "formal_gate_passed": False,
        "formal_gate_reason": "bounded prefix diagnostics do not prove full coverage",
    }
    atomic_json(args.output, result)
    return result


def main() -> None:
    print(json.dumps(summarize(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

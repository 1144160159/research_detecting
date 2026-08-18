#!/usr/bin/env python3
"""Resumable sequential all-PCAP strict audit for CICIoT2023."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from audit_caeos_ciciot2023_prefix import inspect_pcap


APPROVED_EXCLUSIONS = {
    "five_tuple_absent_from_official_flow_labels",
    "protocol_outside_official_tcp_udp_flow_labels",
}


def source_token(source_id: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", source_id).strip("_")[:100]
    return f"{stem}-{hashlib.sha256(source_id.encode()).hexdigest()[:12]}"


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def accepted_audit(audit: dict) -> bool:
    exclusions = audit.get("excluded_packet_count_by_reason", {})
    return (
        audit.get("complete_pcap_read") is True
        and audit.get("source_size_verified") is True
        and audit.get("label_conflict_count") == 0
        and audit.get("time_nonoverlap_count") == 0
        and audit.get("protocol_policy_version") == "official_capture_tcp_udp_icmp_v2"
        and set(exclusions).issubset(APPROVED_EXCLUSIONS)
        and audit.get("matched_flow_count") == audit.get("retained_supported_ip_flow_count")
        and audit.get("capture_label_coverage") == 1.0
    )


def aggregate(inventory: dict, audits: list[dict], selected_count: int) -> dict:
    expected = inventory["summary"]["expected_source_count"]
    completed = sum(accepted_audit(item) for item in audits)
    full_scope = selected_count == expected
    expected_ids = {entry["source_id"] for entry in inventory["entries"]}
    audited_ids = {item.get("source_id") for item in audits}
    exact_source_coverage = audited_ids == expected_ids
    inventory_ready = inventory["summary"].get("inventory_ready") is True
    formal = inventory_ready and full_scope and exact_source_coverage and len(audits) == expected and completed == expected
    return {
        "schema": "caeos.ciciot2023.all_pcap_audit_summary.v2",
        "dataset_id": "CICIoT2023",
        "authority_granularity": "capture_member_not_official_flow_label",
        "expected_source_count": expected,
        "selected_source_count": selected_count,
        "audit_file_count": len(audits),
        "accepted_source_count": completed,
        "exact_inventory_source_id_coverage": exact_source_coverage,
        "inventory_ready": inventory_ready,
        "complete_packet_count": sum(item.get("processed_packets", 0) for item in audits),
        "retained_flow_count": sum(item.get("retained_supported_ip_flow_count", 0) for item in audits),
        "retained_icmp_flow_count": sum(item.get("retained_icmp_flow_count", 0) for item in audits),
        "excluded_packet_count_by_reason": {
            reason: sum(item.get("excluded_packet_count_by_reason", {}).get(reason, 0) for item in audits)
            for reason in sorted(APPROVED_EXCLUSIONS)
        },
        "full_inventory_scope": full_scope,
        "formal_dataset_gate_passed": formal,
        "formal_gate_reason": None if formal else f"all {expected} inventory sources must have accepted complete-read audits",
    }


def run(dataset_root: Path, inventory_path: Path, run_root: Path, include_regex: str | None = None) -> dict:
    inventory = json.loads(inventory_path.read_text())
    if inventory.get("schema") != "caeos.ciciot2023.all_pcap_inventory.v1":
        raise ValueError("unexpected inventory schema")
    entries = inventory["entries"]
    if include_regex:
        expression = re.compile(include_regex)
        entries = [entry for entry in entries if expression.search(entry["source_id"])]
    audit_dir = run_root / "audits"
    summary_path = run_root / "summary.json"
    audits = []
    for entry in entries:
        output = audit_dir / f"{source_token(entry['source_id'])}.json"
        if output.is_file():
            prior = json.loads(output.read_text())
            if prior.get("source_id") == entry["source_id"] and accepted_audit(prior):
                audits.append(prior)
                atomic_json(summary_path, aggregate(inventory, audits, len(entries)))
                continue
        source = dataset_root / entry["capture"]
        if not source.is_file() or source.stat().st_size != entry["pcap_bytes"]:
            raise ValueError(f"missing or size-changed PCAP: {entry['source_id']}")
        scan = inspect_pcap(source, 2_147_483_647)
        retained = scan["retained_supported_ip_flow_count"]
        audit = {
            "schema": "caeos.ciciot2023.all_pcap_member_audit.v2",
            "dataset_id": "CICIoT2023",
            "authority_granularity": "capture_member_not_official_flow_label",
            "source_id": entry["source_id"],
            "capture_label": entry["label"],
            "source_size_verified": True,
            **scan,
            "label_conflict_count": 0,
            "time_nonoverlap_count": 0,
            "time_overlap_policy": "not_applicable_capture_member_authoritative_label",
            "matched_flow_count": retained,
            "capture_label_coverage": 1.0,
            "zero_eligible_flow_capture": retained == 0,
        }
        atomic_json(output, audit)
        if not accepted_audit(audit):
            atomic_json(summary_path, aggregate(inventory, audits + [audit], len(entries)))
            raise RuntimeError(f"strict audit rejected {entry['source_id']}")
        audits.append(audit)
        atomic_json(summary_path, aggregate(inventory, audits, len(entries)))
    return aggregate(inventory, audits, len(entries))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--include-regex")
    args = parser.parse_args()
    summary = run(args.dataset_root, args.inventory, args.run_root, args.include_regex)
    atomic_json(args.run_root / "summary.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["accepted_source_count"] == summary["selected_source_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

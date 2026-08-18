#!/usr/bin/env python3
"""Resumable strict capture-label audit for the four benign-only datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

from audit_caeos_ciciot2022_prefix import inspect_pcap


DATASET_IDS = {
    "iscx_tor_nontor_2017",
    "iscx_vpn_nonvpn_2016",
    "parrot2025",
    "crossplatform_android_ios",
}
PCAP_SUFFIXES = (".pcap", ".pcapng", ".cap")
APP_TIMESTAMP = re.compile(r"^(?P<app>.+?)_\d{4}-\d{2}-\d{2}-")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_token(source_id: str, ordinal: int) -> str:
    digest = sha256_bytes(source_id.encode("utf-8"))[:16]
    return f"{ordinal:06d}_{digest}.json"


def normalized_application(stem: str) -> str:
    match = APP_TIMESTAMP.match(stem)
    return (match.group("app") if match else stem).strip()


def capture_label(dataset_id: str, source_path: str, member: str | None) -> dict[str, Any]:
    logical = member or source_path
    stem = Path(logical).stem
    domain = "Benign"
    platform = "unspecified"
    if dataset_id == "iscx_tor_nontor_2017":
        first = Path(logical).parts[0].lower() if Path(logical).parts else ""
        archive = Path(source_path).name.lower()
        domain = "NonTor" if first == "nontor" or archive.startswith("nontor") else "Tor"
    elif dataset_id == "iscx_vpn_nonvpn_2016":
        archive = Path(source_path).name.lower()
        domain = "NonVPN" if archive.startswith("nonvpn") else "VPN"
    elif dataset_id == "parrot2025":
        platform = "android"
    else:
        lowered = source_path.lower()
        if "crossplatform_android" in lowered:
            platform = "android"
        elif "crossplatform_ios" in lowered:
            platform = "ios"
        else:
            raise ValueError(f"cannot infer CrossPlatform platform: {source_path}")
        domain = platform
    application = normalized_application(stem)
    if dataset_id == "crossplatform_android_ios":
        application = Path(source_path).parent.name
    if not application:
        raise ValueError(f"empty application label: {logical}")
    return {
        "traffic_class": "Benign",
        "binary_label": 0,
        "attack_category": "Benign",
        "attack_subcategory": "Benign",
        "family_label": domain,
        "fine_label": application,
        "dataset_native_label": f"{domain}/{application}",
        "application_label": application,
        "domain_label": domain,
        "platform": platform,
    }


def manifest_dataset(manifest: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    matches = [item for item in manifest["datasets"] if item["id"] == dataset_id]
    if len(matches) != 1:
        raise ValueError(f"source manifest dataset count is not one: {dataset_id}")
    return matches[0]


def build_inventory(
    manifest_path: Path, dataset_id: str, run_root: Path
) -> dict[str, Any]:
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    dataset = manifest_dataset(manifest, dataset_id)
    entries: list[dict[str, Any]] = []
    for source in dataset["source_files"]:
        path = str(Path(source["path"]).resolve())
        members = source.get("capture_members") or []
        if members:
            for member in members:
                name = member["name"]
                if not name.lower().endswith(PCAP_SUFFIXES):
                    continue
                entries.append(
                    {
                        "source_type": "archive_member",
                        "source_id": f"{path}::{name}",
                        "archive_path": path,
                        "archive_size_bytes": int(source["size_bytes"]),
                        "member": name,
                        "pcap_bytes": int(member["size_bytes"]),
                        "member_crc32": member.get("crc32"),
                        "label": capture_label(dataset_id, path, name),
                    }
                )
        else:
            if not path.lower().endswith(PCAP_SUFFIXES):
                continue
            entries.append(
                {
                    "source_type": "direct_pcap",
                    "source_id": path,
                    "path": path,
                    "pcap_bytes": int(source["size_bytes"]),
                    "source_sha256": source.get("sha256"),
                    "source_mtime_ns": source.get("mtime_ns"),
                    "label": capture_label(dataset_id, path, None),
                }
            )
    entries.sort(key=lambda item: item["source_id"])
    excluded_entries: list[dict[str, Any]] = []
    if dataset_id == "crossplatform_android_ios":
        digest_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        without_digest: list[dict[str, Any]] = []
        for item in entries:
            digest = item.get("source_sha256")
            (digest_groups[digest] if digest else without_digest).append(item)
        retained = list(without_digest)
        for digest, group in sorted(digest_groups.items()):
            group.sort(key=lambda item: item["source_id"])
            native_labels = {item["label"]["dataset_native_label"] for item in group}
            if len(native_labels) > 1:
                excluded_entries.extend(
                    {
                        "source_id": item["source_id"],
                        "source_sha256": digest,
                        "dataset_native_label": item["label"]["dataset_native_label"],
                        "reason": "identical_pcap_has_conflicting_application_labels",
                    }
                    for item in group
                )
                continue
            retained.append(group[0])
            excluded_entries.extend(
                {
                    "source_id": item["source_id"],
                    "source_sha256": digest,
                    "dataset_native_label": item["label"]["dataset_native_label"],
                    "reason": "duplicate_pcap_same_label_noncanonical_copy",
                    "canonical_source_id": group[0]["source_id"],
                }
                for item in group[1:]
            )
        entries = sorted(retained, key=lambda item: item["source_id"])

    source_ids = [item["source_id"] for item in entries]
    checks: dict[str, Any] = {
        "nonempty": bool(entries),
        "unique_source_ids": len(source_ids) == len(set(source_ids)),
        "all_fixed_benign": all(
            item["label"]["traffic_class"] == "Benign"
            and item["label"]["binary_label"] == 0
            for item in entries
        ),
    }
    labels = Counter(item["label"]["dataset_native_label"] for item in entries)
    domains = Counter(item["label"]["domain_label"] for item in entries)
    applications = Counter(item["label"]["application_label"] for item in entries)
    metadata: dict[str, Any] = {
        "domain_counts": dict(sorted(domains.items())),
        "application_count": len(applications),
        "native_label_count": len(labels),
    }
    if dataset_id == "iscx_tor_nontor_2017":
        source_root = Path(dataset["source_root"]).parent
        csv_root = source_root / "CSVs"
        official_csvs = [
            csv_root / "Scenario-A-merged_5s.csv",
            csv_root / "Scenario-B-merged_5s.csv",
        ]
        checks["official_scenario_csvs_present"] = all(path.is_file() for path in official_csvs)
        checks["tor_and_nontor_present"] = set(domains) == {"Tor", "NonTor"}
        metadata["official_scenario_csvs"] = [str(path) for path in official_csvs]
    elif dataset_id == "iscx_vpn_nonvpn_2016":
        checks["vpn_and_nonvpn_present"] = set(domains) == {"VPN", "NonVPN"}
    elif dataset_id == "parrot2025":
        source_root = Path(dataset["source_root"])
        missing_keylogs = []
        for item in entries:
            stem = Path(item["path"]).stem
            keylog = source_root / f"sslkeylog_{stem}.txt"
            if not keylog.is_file():
                missing_keylogs.append(str(keylog))
        checks["all_pcap_keylog_pairs_present"] = not missing_keylogs
        checks["expected_320_captures"] = len(entries) == 320
        checks["expected_80_apps_four_captures_each"] = (
            len(applications) == 80 and set(applications.values()) == {4}
        )
        metadata["missing_keylogs"] = missing_keylogs[:100]
    else:
        checks["android_and_ios_present"] = set(domains) == {"android", "ios"}
        checks["duplicate_policy_applied"] = True
        metadata["pre_dedup_source_count"] = len(entries) + len(excluded_entries)
        metadata["retained_source_count"] = len(entries)
        metadata["excluded_duplicate_source_count"] = len(excluded_entries)
        metadata["excluded_duplicate_reason_counts"] = dict(
            sorted(Counter(item["reason"] for item in excluded_entries).items())
        )
        metadata["excluded_duplicate_examples"] = excluded_entries[:100]
    candidate = {
        "schema": "caeos.benign_capture_inventory.v1",
        "dataset_id": dataset_id,
        "source_manifest": str(manifest_path.resolve()),
        "source_manifest_sha256": sha256_bytes(raw),
        "expected_source_count": len(entries),
        "authority_granularity": "capture_or_archive_member_fixed_benign_label",
        "label_policy": dataset["label_policy"],
        "readiness_checks": checks,
        "inventory_ready": all(checks.values()),
        "metadata": metadata,
        "excluded_entries": excluded_entries,
        "entries": entries,
    }
    inventory_path = run_root / "inventory.json"
    if inventory_path.is_file():
        existing = json.loads(inventory_path.read_text(encoding="utf-8"))
        if existing != candidate:
            raise ValueError("frozen inventory drift; use a new run root")
        return existing
    atomic_json(inventory_path, candidate)
    return candidate


def accepted_audit(audit: dict[str, Any], inventory_sha256: str) -> bool:
    complete_read = bool(
        audit.get("complete_pcap_read") is True
        and audit.get("processed_packets") == audit.get("pcap_packets")
    )
    salvaged_tail = bool(
        audit.get("complete_pcap_read") is False
        and audit.get("source_quality_action")
        == "retain_complete_flows_before_truncated_tail"
        and audit.get("truncated_boundary_flows_excluded") is True
        and int(audit.get("truncated_boundary_flow_count", 0)) > 0
        and int(audit.get("recovered_valid_packet_count", 0))
        == int(audit.get("processed_packets", -1))
        and audit.get("capture_read_error", {}).get("exception_type")
        == "PcapTailCorruption"
    )
    return bool(
        audit.get("inventory_sha256") == inventory_sha256
        and (complete_read or salvaged_tail)
        and audit.get("source_size_verified") is True
        and audit.get("temporary_pcap_removed") is True
        and audit.get("label_conflict_count") == 0
        and audit.get("capture_label_coverage") == 1.0
        and audit.get("capture_label", {}).get("traffic_class") == "Benign"
        and audit.get("capture_label", {}).get("binary_label") == 0
        and audit.get("processed_packets") == audit.get("pcap_packets")
    )


def aggregate(inventory: dict[str, Any], audits: list[dict[str, Any]]) -> dict[str, Any]:
    expected_ids = {entry["source_id"] for entry in inventory["entries"]}
    audited_ids = {audit.get("source_id") for audit in audits}
    accepted = sum(
        accepted_audit(audit, inventory["source_manifest_sha256"]) for audit in audits
    )
    exact = audited_ids == expected_ids
    expected = inventory["expected_source_count"]
    formal = bool(
        inventory["inventory_ready"]
        and exact
        and len(audits) == expected
        and accepted == expected
    )
    return {
        "schema": "caeos.benign_capture_label_audit_summary.v1",
        "dataset_id": inventory["dataset_id"],
        "authority_granularity": inventory["authority_granularity"],
        "expected_source_count": expected,
        "audit_file_count": len(audits),
        "accepted_source_count": accepted,
        "source_quality_adjusted_source_count": sum(
            audit.get("source_quality_action")
            == "retain_complete_flows_before_truncated_tail"
            for audit in audits
        ),
        "exact_inventory_source_id_coverage": exact,
        "inventory_ready": inventory["inventory_ready"],
        "readiness_checks": inventory["readiness_checks"],
        "complete_packet_count": sum(audit.get("processed_packets", 0) for audit in audits),
        "retained_flow_count": sum(
            audit.get("retained_supported_ip_flow_count", 0) for audit in audits
        ),
        "retained_icmp_flow_count": sum(
            audit.get("retained_icmp_flow_count", 0) for audit in audits
        ),
        "excluded_packet_count_by_reason": {
            reason: sum(
                audit.get("excluded_packet_count_by_reason", {}).get(reason, 0)
                for audit in audits
            )
            for reason in (
                "five_tuple_absent_from_official_flow_labels",
                "protocol_outside_official_tcp_udp_flow_labels",
            )
        },
        "traffic_class_counts": {"Benign": accepted},
        "formal_dataset_gate_passed": formal,
        "formal_gate_reason": None
        if formal
        else "every frozen capture must pass complete-read and fixed-benign capture-label gates",
    }


def make_audit(
    inventory: dict[str, Any], entry: dict[str, Any], scan: dict[str, Any]
) -> dict[str, Any]:
    retained = scan["retained_supported_ip_flow_count"]
    return {
        "schema": "caeos.benign_capture_member_audit.v1",
        "dataset_id": inventory["dataset_id"],
        "inventory_sha256": inventory["source_manifest_sha256"],
        "source_id": entry["source_id"],
        "source_record": entry,
        "capture_label": entry["label"],
        "source_size_verified": True,
        **scan,
        "label_conflict_count": 0,
        "time_nonoverlap_count": 0,
        "time_overlap_policy": "not_applicable_capture_authoritative_fixed_benign_label",
        "matched_flow_count": retained,
        "capture_label_coverage": 1.0,
        "zero_eligible_flow_capture": retained == 0,
        "temporary_pcap_removed": True,
    }


def load_prior(
    audit_path: Path, entry: dict[str, Any], inventory: dict[str, Any]
) -> dict[str, Any] | None:
    if not audit_path.is_file():
        return None
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (
        audit.get("source_id") == entry["source_id"]
        and audit.get("source_record") == entry
        and accepted_audit(audit, inventory["source_manifest_sha256"])
    ):
        return audit
    return None


def materialized_direct(entry: dict[str, Any]) -> Iterator[tuple[Path, bool]]:
    path = Path(entry["path"])
    if not path.is_file() or path.stat().st_size != entry["pcap_bytes"]:
        raise ValueError(f"missing or size-changed PCAP: {entry['source_id']}")
    yield path, False


def audit_path(
    inventory: dict[str, Any], entry: dict[str, Any], path: Path
) -> dict[str, Any]:
    scan = inspect_pcap(path, 2_147_483_647)
    audit = make_audit(inventory, entry, scan)
    if not accepted_audit(audit, inventory["source_manifest_sha256"]):
        raise RuntimeError(f"strict benign-label audit rejected {entry['source_id']}")
    return audit


def run(args: argparse.Namespace) -> dict[str, Any]:
    args.run_root.mkdir(parents=True, exist_ok=True)
    args.temp_root.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(args.source_manifest, args.dataset_id, args.run_root)
    inventory_sha = inventory["source_manifest_sha256"]
    if not inventory["inventory_ready"]:
        raise RuntimeError(f"inventory readiness failed: {inventory['readiness_checks']}")
    if args.inventory_only:
        summary = aggregate(inventory, [])
        atomic_json(args.run_root / "summary.json", summary)
        return summary

    audit_dir = args.run_root / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audits: list[dict[str, Any]] = []
    pending: list[tuple[int, dict[str, Any], Path]] = []
    for ordinal, entry in enumerate(inventory["entries"], start=1):
        output = audit_dir / source_token(entry["source_id"], ordinal)
        prior = load_prior(output, entry, inventory)
        if prior is not None:
            audits.append(prior)
        else:
            pending.append((ordinal, entry, output))

    def save(ordinal: int, entry: dict[str, Any], output: Path, path: Path) -> None:
        audit = audit_path(inventory, entry, path)
        atomic_json(output, audit)
        audits.append(audit)
        if len(audits) % args.summary_interval == 0:
            atomic_json(args.run_root / "summary.json", aggregate(inventory, audits))

    direct = [record for record in pending if record[1]["source_type"] == "direct_pcap"]
    for ordinal, entry, output in direct:
        path = Path(entry["path"])
        if not path.is_file() or path.stat().st_size != entry["pcap_bytes"]:
            raise ValueError(f"missing or size-changed PCAP: {entry['source_id']}")
        save(ordinal, entry, output, path)

    archives: dict[str, list[tuple[int, dict[str, Any], Path]]] = defaultdict(list)
    for record in pending:
        if record[1]["source_type"] == "archive_member":
            archives[record[1]["archive_path"]].append(record)
    for archive_name in sorted(archives):
        records = archives[archive_name]
        archive_path = Path(archive_name)
        if not archive_path.is_file():
            raise ValueError(f"missing archive: {archive_path}")
        if archive_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                for ordinal, entry, output in records:
                    info = archive.getinfo(entry["member"])
                    if info.file_size != entry["pcap_bytes"]:
                        raise ValueError(f"archive member size changed: {entry['source_id']}")
                    temporary: Path | None = None
                    try:
                        with tempfile.NamedTemporaryFile(
                            prefix="caeos-benign-", suffix=Path(entry["member"]).suffix,
                            dir=args.temp_root, delete=False
                        ) as target:
                            temporary = Path(target.name)
                            if info.compress_type == 9:
                                result = subprocess.run(
                                    ["7z", "x", "-so", str(archive_path), entry["member"]],
                                    stdout=target,
                                    stderr=subprocess.PIPE,
                                    check=False,
                                )
                                if result.returncode:
                                    raise RuntimeError(
                                        f"7z Deflate64 extraction failed ({result.returncode}): "
                                        + result.stderr.decode("utf-8", errors="replace")[-2000:]
                                    )
                            else:
                                with archive.open(info) as source:
                                    shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
                        if temporary.stat().st_size != entry["pcap_bytes"]:
                            raise IOError(f"incomplete ZIP member extraction: {entry['source_id']}")
                        save(ordinal, entry, output, temporary)
                    finally:
                        if temporary is not None:
                            temporary.unlink(missing_ok=True)
        else:
            by_member = {entry["member"]: (ordinal, entry, output) for ordinal, entry, output in records}
            with tarfile.open(archive_path, "r:*") as archive:
                for member in archive:
                    record = by_member.get(member.name)
                    if record is None:
                        continue
                    ordinal, entry, output = record
                    if not member.isfile() or member.size != entry["pcap_bytes"]:
                        raise ValueError(f"archive member changed: {entry['source_id']}")
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError(f"cannot extract member: {entry['source_id']}")
                    temporary: Path | None = None
                    try:
                        with tempfile.NamedTemporaryFile(
                            prefix="caeos-benign-", suffix=Path(entry["member"]).suffix,
                            dir=args.temp_root, delete=False
                        ) as target:
                            temporary = Path(target.name)
                            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
                        save(ordinal, entry, output, temporary)
                    finally:
                        if temporary is not None:
                            temporary.unlink(missing_ok=True)
                    del by_member[member.name]
            if by_member:
                raise ValueError(f"archive members not encountered: {sorted(by_member)[:5]}")
    summary = aggregate(inventory, audits)
    atomic_json(args.run_root / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", choices=sorted(DATASET_IDS), required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--temp-root", type=Path, required=True)
    parser.add_argument("--summary-interval", type=int, default=25)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    if args.summary_interval <= 0:
        parser.error("--summary-interval must be positive")
    summary = run(args)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if args.inventory_only:
        return 0
    return 0 if summary["formal_dataset_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import ipaddress
import json
import zipfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


DATASET_ID = "cicddos2019"
REQUIRED = {
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Flow Duration",
    "Label",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-archive", action="append", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--timezone-offset-hours", required=True, type=int)
    parser.add_argument("--resolver-tolerance-ns", type=int, default=2_000_000)
    return parser.parse_args()


def normalize_fine(value: str) -> tuple[str, str, int]:
    cleaned = " ".join(str(value).strip().split())
    lowered = cleaned.lower().replace("_", "-")
    if lowered == "benign":
        return "Benign", "Benign", 0
    aliases = {
        "udp-lag": "UDP-lag",
        "udplag": "UDP-lag",
        "syn": "SYN Flood",
        "tftp": "TFTP",
        "udp": "UDP Flood",
        "ldap": "LDAP",
        "mssql": "MSSQL",
        "netbios": "NetBIOS",
        "portmap": "Portmap",
    }
    if lowered.startswith("drdos-"):
        service = cleaned.split("_", 1)[-1].split("-", 1)[-1]
        service = {"dns": "DNS", "ldap": "LDAP", "mssql": "MSSQL", "netbios": "NetBIOS", "ntp": "NTP", "snmp": "SNMP", "ssdp": "SSDP", "udp": "UDP"}.get(service.lower(), service)
        return f"DrDoS - {service}", "DDoS", 1
    return aliases.get(lowered, cleaned), "DDoS", 1


def timestamp_ns(value: str, offset_hours: int) -> int:
    cleaned = " ".join(str(value).strip().split())
    parsed = None
    for timestamp_format in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(cleaned, timestamp_format)
        except ValueError:
            continue
        break
    if parsed is None:
        raise ValueError(f"unsupported CICDDoS2019 timestamp: {value!r}")
    adjusted = parsed + timedelta(hours=offset_hours)
    return int(adjusted.replace(tzinfo=timezone.utc).timestamp() * 1_000_000_000)


def member_csvs(archive: zipfile.ZipFile) -> list[str]:
    return sorted(
        name
        for name in archive.namelist()
        if name.lower().endswith(".csv") and not Path(name).name.startswith(".~lock")
    )


def preflight_archives(paths: list[Path]) -> dict[str, list[str]]:
    inventory: dict[str, list[str]] = {}
    for archive_path in paths:
        with zipfile.ZipFile(archive_path) as archive:
            members = member_csvs(archive)
            if not members:
                raise ValueError(f"no CSV members in {archive_path}")
            inventory[str(archive_path)] = members
            for member in members:
                with archive.open(member) as raw, io.TextIOWrapper(
                    raw, encoding="utf-8-sig", errors="replace", newline=""
                ) as text_handle:
                    reader = csv.reader(text_handle)
                    try:
                        header = [value.strip() for value in next(reader)]
                    except StopIteration as error:
                        raise ValueError(
                            f"empty CSV member: {archive_path}::{member}"
                        ) from error
                missing = sorted(REQUIRED - set(header))
                if missing:
                    raise ValueError(
                        f"{archive_path}::{member} missing columns: {missing}"
                    )
    return inventory


def records(
    paths: list[Path], offset_hours: int, counters: Counter[str]
) -> Iterator[dict[str, Any]]:
    for archive_path in paths:
        with zipfile.ZipFile(archive_path) as archive:
            for member in member_csvs(archive):
                member_fine, _, _ = normalize_fine(Path(member).stem)
                with archive.open(member) as raw, io.TextIOWrapper(
                    raw, encoding="utf-8-sig", errors="replace", newline=""
                ) as text_handle:
                    reader = csv.reader(text_handle)
                    try:
                        header = [value.strip() for value in next(reader)]
                    except StopIteration as error:
                        raise ValueError(f"empty CSV member: {archive_path}::{member}") from error
                    indices = {name: index for index, name in enumerate(header)}
                    missing = sorted(REQUIRED - set(indices))
                    if missing:
                        raise ValueError(
                            f"{archive_path}::{member} missing columns: {missing}"
                        )
                    maximum_index = max(indices.values())
                    for row_number, row in enumerate(reader, start=2):
                        counters["rows"] += 1
                        if len(row) <= maximum_index:
                            counters["malformed_rows"] += 1
                            continue
                        try:
                            fine, family, binary = normalize_fine(row[indices["Label"]])
                            if binary and fine != member_fine:
                                counters["member_label_conflicts"] += 1
                            src_ip = str(
                                ipaddress.ip_address(row[indices["Source IP"]].strip())
                            )
                            dst_ip = str(
                                ipaddress.ip_address(
                                    row[indices["Destination IP"]].strip()
                                )
                            )
                            src_port = int(float(row[indices["Source Port"]]))
                            dst_port = int(float(row[indices["Destination Port"]]))
                            protocol = int(float(row[indices["Protocol"]]))
                            start_ns = timestamp_ns(
                                row[indices["Timestamp"]], offset_hours
                            )
                            duration_ns = max(
                                0,
                                int(float(row[indices["Flow Duration"]]) * 1_000),
                            )
                        except (ValueError, TypeError, OverflowError):
                            counters["invalid_rows"] += 1
                            continue
                        counters["valid_rows"] += 1
                        counters[f"fine::{fine}"] += 1
                        counters[f"family::{family}"] += 1
                        counters[f"protocol::{protocol}"] += 1
                        material = f"{archive_path.name}\0{member}\0{row_number}"
                        yield {
                            "record_id": hashlib.sha256(
                                material.encode("utf-8")
                            ).hexdigest(),
                            "source_member": None,
                            "src_ip": src_ip,
                            "src_port": src_port,
                            "dst_ip": dst_ip,
                            "dst_port": dst_port,
                            "protocol": protocol,
                            "start_ns": start_ns,
                            "end_ns": start_ns + duration_ns,
                            "fine_label": fine,
                            "family_label": family,
                            "binary_label": binary,
                            "label_source": (
                                f"{archive_path}::{member}#{row_number}"
                            ),
                        }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = sorted(path.resolve() for path in args.csv_archive)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing CICDDoS2019 CSV archives: {missing}")
    counters: Counter[str] = Counter()
    member_inventory = preflight_archives(paths)
    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index,
        DATASET_ID,
        records(paths, args.timezone_offset_hours, counters),
        registry_sha256,
    )
    report = {
        "schema_version": "caeos_cicddos2019_label_index_audit_v1",
        "dataset_id": DATASET_ID,
        "authority": "official CICFlowMeter CSV members streamed from official ZIP archives",
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "csv_archives": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in paths
        ],
        "csv_member_inventory": member_inventory,
        "input_counters": dict(sorted(counters.items())),
        "label_index": index,
        "timezone_policy": {
            "offset_hours": args.timezone_offset_hours,
            "status": "must_be_validated_by_real_pcap_five_tuple_coverage",
        },
        "source_member_scope": None,
        "source_member_scope_reason": (
            "official PCAP archive members are extensionless ordinal chunks, while "
            "official CSV members are attack-type partitions"
        ),
        "resolver_tolerance_ns": args.resolver_tolerance_ns,
        "member_name_label_consistency": {
            "authority": "row_level_Label_column",
            "member_name_role": "informational_partition_hint_only",
            "mismatch_count": counters["member_label_conflicts"],
            "gate": "informational_only",
            "reason": (
                "official CICDDoS2019 CSV members contain row-level labels that "
                "can differ from the member filename; the row Label remains the "
                "official flow authority"
            ),
        },
        "ready_for_pcap_coverage_dry_run": counters["valid_rows"] > 0,
        "ready_for_pcap_coverage_dry_run_reason": (
            "row-level official labels indexed; member-name mismatches are audited "
            "but do not override or block official row labels"
        ),
    }
    report["audit_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(args.audit_output, report)
    return report


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

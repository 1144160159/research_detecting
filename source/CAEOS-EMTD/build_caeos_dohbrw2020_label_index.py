from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from zoneinfo import ZoneInfo

from caeos_label_alignment import canonical_endpoints, create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


DATASET_ID = "dohbrw2020"
LABEL_TIMEZONE_NAME = "America/Halifax"
LABEL_TIMEZONE = ZoneInfo(LABEL_TIMEZONE_NAME)
REQUIRED = {
    "SourceIP",
    "DestinationIP",
    "SourcePort",
    "DestinationPort",
    "TimeStamp",
    "Duration",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-dir", required=True, type=Path)
    parser.add_argument("--tool-csv-root", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--resolver-tolerance-ns", type=int, default=1_000_000_000)
    return parser.parse_args()


def timestamp_ns(value: str) -> int:
    parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d %H:%M:%S")
    localized = parsed.replace(tzinfo=LABEL_TIMEZONE)
    return int(localized.astimezone(timezone.utc).timestamp() * 1_000_000_000)


def duration_ns(value: str) -> int:
    return max(0, int(round(float(str(value).strip()) * 1_000_000_000)))


def flow_identity(
    *,
    start_ns: int,
    duration: int,
    src_ip: str,
    src_port: int,
    dst_ip: str,
    dst_port: int,
) -> bytes:
    a_ip, a_port, b_ip, b_port = canonical_endpoints(
        ipaddress.ip_address(src_ip).packed,
        src_port,
        ipaddress.ip_address(dst_ip).packed,
        dst_port,
    )
    material = "\0".join(
        (
            str(start_ns),
            str(duration),
            a_ip.hex(),
            str(a_port),
            b_ip.hex(),
            str(b_port),
        )
    )
    return hashlib.sha256(material.encode("ascii")).digest()


def parsed_row(row: dict[str, str]) -> dict[str, Any]:
    src_ip = str(ipaddress.ip_address(row["SourceIP"].strip()))
    dst_ip = str(ipaddress.ip_address(row["DestinationIP"].strip()))
    src_port = int(float(row["SourcePort"]))
    dst_port = int(float(row["DestinationPort"]))
    start = timestamp_ns(row["TimeStamp"])
    duration = duration_ns(row["Duration"])
    return {
        "src_ip": src_ip,
        "src_port": src_port,
        "dst_ip": dst_ip,
        "dst_port": dst_port,
        "start_ns": start,
        "duration_ns": duration,
        "identity": flow_identity(
            start_ns=start,
            duration=duration,
            src_ip=src_ip,
            src_port=src_port,
            dst_ip=dst_ip,
            dst_port=dst_port,
        ),
    }


def preflight_csv(path: Path, label_column: str) -> list[str]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError(f"empty DoHBrw2020 CSV: {path}") from error
    missing = sorted((REQUIRED | {label_column}) - set(header))
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    return header


def iter_source(
    path: Path,
    *,
    fine_label: str,
    family_label: str,
    binary_label: int,
    expected_column: str,
    expected_value: str,
    counters: Counter[str],
    identities: Counter[bytes],
) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted((REQUIRED | {expected_column}) - set(reader.fieldnames or ()))
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        for row_number, row in enumerate(reader, start=2):
            counters["rows"] += 1
            try:
                actual_value = str(row[expected_column]).strip()
            except (KeyError, ValueError, TypeError, OverflowError):
                counters["invalid_rows"] += 1
                continue
            if actual_value.lower() != expected_value.lower():
                counters["rows_outside_authoritative_slice"] += 1
                counters[f"outside_slice::{expected_column}::{actual_value}"] += 1
                continue
            try:
                parsed = parsed_row(row)
            except (KeyError, ValueError, TypeError, OverflowError):
                counters["invalid_rows"] += 1
                continue
            counters["valid_rows"] += 1
            counters[f"fine::{fine_label}"] += 1
            counters[f"family::{family_label}"] += 1
            if parsed["src_port"] != 443 and parsed["dst_port"] != 443:
                counters["rows_without_https_port"] += 1
            identities[parsed["identity"]] += 1
            material = f"{path}\0{row_number}"
            yield {
                "record_id": hashlib.sha256(material.encode("utf-8")).hexdigest(),
                "source_member": None,
                "src_ip": parsed["src_ip"],
                "src_port": parsed["src_port"],
                "dst_ip": parsed["dst_ip"],
                "dst_port": parsed["dst_port"],
                "protocol": 6,
                "start_ns": parsed["start_ns"],
                "end_ns": parsed["start_ns"] + parsed["duration_ns"],
                "fine_label": fine_label,
                "family_label": family_label,
                "binary_label": binary_label,
                "label_source": f"{path}#{row_number}",
            }


def verification_identities(
    path: Path, expected_value: str, counters: Counter[str]
) -> Counter[bytes]:
    identities: Counter[bytes] = Counter()
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted((REQUIRED | {"Label"}) - set(reader.fieldnames or ()))
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        for row in reader:
            counters["rows"] += 1
            try:
                actual_value = str(row["Label"]).strip()
            except (KeyError, ValueError, TypeError, OverflowError):
                counters["invalid_rows"] += 1
                continue
            if actual_value.lower() != expected_value.lower():
                counters["label_conflict_rows"] += 1
                continue
            try:
                parsed = parsed_row(row)
            except (KeyError, ValueError, TypeError, OverflowError):
                counters["invalid_rows"] += 1
                continue
            identities[parsed["identity"]] += 1
            counters["valid_rows"] += 1
    return identities


def counter_difference(left: Counter[bytes], right: Counter[bytes]) -> int:
    return sum((left - right).values())


def build(args: argparse.Namespace) -> dict[str, Any]:
    nondoh = args.total_dir / "l1-nondoh.csv"
    doh = args.total_dir / "l1-doh.csv"
    benign = args.total_dir / "l2-benign.csv"
    malicious = args.total_dir / "l2-malicious.csv"
    tools = {
        "DNS2TCP": args.tool_csv_root / "dns2tcp" / "all.csv",
        "DNSCat2": args.tool_csv_root / "dnscat2" / "all.csv",
        "Iodine": args.tool_csv_root / "iodine" / "all.csv",
    }
    authoritative = [nondoh, benign, *tools.values()]
    verification = [doh, malicious]
    missing = [str(path) for path in authoritative + verification if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing DoHBrw2020 CSVs: {missing}")
    header_inventory = {
        str(nondoh): preflight_csv(nondoh, "Label"),
        str(doh): preflight_csv(doh, "Label"),
        str(benign): preflight_csv(benign, "Label"),
        str(malicious): preflight_csv(malicious, "Label"),
        **{str(path): preflight_csv(path, "DoH") for path in tools.values()},
    }
    counters: Counter[str] = Counter()
    nondoh_ids: Counter[bytes] = Counter()
    benign_ids: Counter[bytes] = Counter()
    tool_ids: Counter[bytes] = Counter()

    def all_records() -> Iterator[dict[str, Any]]:
        yield from iter_source(
            nondoh,
            fine_label="NonDoH",
            family_label="Benign",
            binary_label=0,
            expected_column="Label",
            expected_value="NonDoH",
            counters=counters,
            identities=nondoh_ids,
        )
        yield from iter_source(
            benign,
            fine_label="Benign DoH",
            family_label="Benign",
            binary_label=0,
            expected_column="Label",
            expected_value="Benign",
            counters=counters,
            identities=benign_ids,
        )
        for tool, path in tools.items():
            yield from iter_source(
                path,
                fine_label=f"Malicious DoH - {tool}",
                family_label="DNS Tunneling",
                binary_label=1,
                expected_column="DoH",
                expected_value="True",
                counters=counters,
                identities=tool_ids,
            )

    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index, DATASET_ID, all_records(), registry_sha256
    )
    verification_counters: Counter[str] = Counter()
    l1_doh_ids = verification_identities(doh, "DoH", verification_counters)
    l2_malicious_ids = verification_identities(
        malicious, "Malicious", verification_counters
    )
    l2_union = benign_ids + l2_malicious_ids
    malicious_missing = counter_difference(l2_malicious_ids, tool_ids)
    malicious_extra = counter_difference(tool_ids, l2_malicious_ids)
    doh_missing = counter_difference(l1_doh_ids, l2_union)
    doh_extra = counter_difference(l2_union, l1_doh_ids)
    separate_paths = list(args.tool_csv_root.glob("*/Separate/*.csv"))
    crosscheck_passed = not any(
        (malicious_missing, malicious_extra, doh_missing, doh_extra)
    )
    report = {
        "schema_version": "caeos_dohbrw2020_label_index_audit_v1",
        "dataset_id": DATASET_ID,
        "authority_precedence": [
            "tool-specific all.csv for malicious DoH fine labels",
            "l2-benign.csv for benign DoH",
            "l1-nondoh.csv for non-DoH benign traffic",
            "l2-malicious.csv and l1-doh.csv are verification-only aggregates",
            "Separate CSVs are duplicate component files and are not indexed",
        ],
        "authoritative_slice_policy": (
            "Rows outside an authoritative file's declared label slice are audited "
            "but not indexed; malformed rows and verification-label conflicts block readiness."
        ),
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "authoritative_files": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in authoritative
        ],
        "verification_files": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in verification
        ],
        "header_inventory": header_inventory,
        "separate_file_inventory": {
            "file_count": len(separate_paths),
            "empty_file_count": sum(path.stat().st_size == 0 for path in separate_paths),
            "total_bytes": sum(path.stat().st_size for path in separate_paths),
            "indexed": False,
        },
        "input_counters": dict(sorted(counters.items())),
        "verification_counters": dict(sorted(verification_counters.items())),
        "duplicate_precedence_crosscheck": {
            "l2_malicious_missing_from_tool_union": malicious_missing,
            "tool_union_extra_vs_l2_malicious": malicious_extra,
            "l1_doh_missing_from_l2_union": doh_missing,
            "l2_union_extra_vs_l1_doh": doh_extra,
            "passed": crosscheck_passed,
        },
        "label_index": index,
        "protocol_policy": "TCP is fixed by the official DoH flow construction",
        "label_timestamp_policy": {
            "input_timezone": LABEL_TIMEZONE_NAME,
            "normalized_timezone": "UTC",
            "dst_aware": True,
            "basis": (
                "Official CSV timestamps are UNB/Halifax local wall time; PCAP "
                "timestamps are Unix UTC epochs."
            ),
        },
        "source_member_scope": None,
        "resolver_tolerance_ns": args.resolver_tolerance_ns,
        "ready_for_pcap_coverage_dry_run": crosscheck_passed
        and counters["invalid_rows"] == 0
        and verification_counters["invalid_rows"] == 0
        and verification_counters["label_conflict_rows"] == 0,
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

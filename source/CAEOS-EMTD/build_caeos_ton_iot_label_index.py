from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from caeos_label_alignment import canonical_endpoints, create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


DATASET_ID = "cic_ton_iot"
PROTOCOLS = {"tcp": 6, "udp": 17, "icmp": 1, "icmp6": 58, "ipv6-icmp": 58}
FINE_LABELS = {
    "normal": ("Benign", "Benign", 0),
    "benign": ("Benign", "Benign", 0),
    "backdoor": ("Backdoor", "Malware", 1),
    "ddos": ("DDoS", "DDoS", 1),
    "dos": ("DoS", "DoS", 1),
    "injection": ("Injection", "Web Attack", 1),
    "mitm": ("MITM", "MITM", 1),
    "password": ("Password", "Brute Force", 1),
    "ransomware": ("Ransomware", "Malware", 1),
    "runsomware": ("Ransomware", "Malware", 1),
    "scanning": ("Scanning", "Reconnaissance", 1),
    "xss": ("XSS", "Web Attack", 1),
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", required=True, type=Path)
    parser.add_argument("--ground-truth-dir", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--ground-truth-missing-sample-limit", type=int, default=100)
    parser.add_argument("--resolver-tolerance-ns", type=int, default=1_000_000_000)
    return parser.parse_args()


def normalized_type(value: str) -> tuple[str, str, int]:
    key = " ".join(str(value).strip().lower().split())
    try:
        return FINE_LABELS[key]
    except KeyError as error:
        raise ValueError(f"unmapped ToN-IoT type: {value!r}") from error


def protocol_number(value: str) -> int:
    cleaned = str(value).strip().lower()
    if cleaned in PROTOCOLS:
        return PROTOCOLS[cleaned]
    return int(float(cleaned))


def epoch_ns(value: str) -> int:
    return int(round(float(str(value).strip()) * 1_000_000_000))


def port_number(value: str) -> int:
    cleaned = str(value).strip()
    if cleaned in {"", "-"}:
        return 0
    return int(float(cleaned))


def event_identity(
    *,
    start_ns: int,
    src_ip: str,
    src_port: int,
    dst_ip: str,
    dst_port: int,
    protocol: int,
    fine_label: str,
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
            a_ip.hex(),
            str(a_port),
            b_ip.hex(),
            str(b_port),
            str(protocol),
            fine_label,
        )
    )
    return material.encode("ascii") + b"\n"


def processed_records(
    paths: list[Path], counters: Counter[str]
) -> Iterator[dict[str, Any]]:
    for path in paths:
        relative = path.name
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {
                "ts",
                "src_ip",
                "src_port",
                "dst_ip",
                "dst_port",
                "proto",
                "duration",
                "label",
                "type",
            }
            missing = sorted(required - set(reader.fieldnames or ()))
            if missing:
                raise ValueError(f"{path} missing columns: {missing}")
            for row_number, row in enumerate(reader, start=2):
                counters["processed_rows"] += 1
                try:
                    fine, family, binary = normalized_type(row["type"])
                    official_binary = int(float(row["label"]))
                    if official_binary != binary:
                        counters["binary_type_conflicts"] += 1
                        continue
                    start_ns = epoch_ns(row["ts"])
                    duration_ns = max(0, epoch_ns(row["duration"]))
                    src_ip = str(ipaddress.ip_address(row["src_ip"].strip()))
                    dst_ip = str(ipaddress.ip_address(row["dst_ip"].strip()))
                    src_port = port_number(row["src_port"])
                    dst_port = port_number(row["dst_port"])
                    protocol = protocol_number(row["proto"])
                except (ValueError, TypeError, OverflowError):
                    counters["invalid_processed_rows"] += 1
                    continue
                material = f"{relative}\0{row_number}"
                counters["valid_processed_rows"] += 1
                counters[f"fine::{fine}"] += 1
                counters[f"family::{family}"] += 1
                counters[f"protocol::{protocol}"] += 1
                yield {
                    "record_id": hashlib.sha256(material.encode("utf-8")).hexdigest(),
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
                    "label_source": f"{path}#{row_number}",
                }


def build(args: argparse.Namespace) -> dict[str, Any]:
    numeric_suffix = lambda path: int(path.stem.rsplit("_", 1)[-1])
    processed_paths = sorted(
        args.processed_dir.glob("Network_dataset_*.csv"), key=numeric_suffix
    )
    ground_truth_paths = sorted(
        args.ground_truth_dir.glob("GroundTruth_Network_*.csv"), key=numeric_suffix
    )
    if not processed_paths:
        raise FileNotFoundError(f"no processed ToN-IoT CSVs under {args.processed_dir}")
    if not ground_truth_paths:
        raise FileNotFoundError(f"no ToN-IoT ground truth CSVs under {args.ground_truth_dir}")
    counters: Counter[str] = Counter()
    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index,
        DATASET_ID,
        processed_records(processed_paths, counters),
        registry_sha256,
    )
    official_coverage = {
        "status": "external_exact_set_inclusion_audit_required",
        "audit_script": "audit_caeos_ton_iot_official_event_coverage.py",
        "coverage_fraction": None,
        "reason": (
            "SecurityEvents are an unsorted, partially duplicated event subset; "
            "they are not a row-for-row sequence of the processed flow CSVs"
        ),
    }
    report = {
        "schema_version": "caeos_ton_iot_label_index_audit_v1",
        "dataset_id": DATASET_ID,
        "authority": (
            "processed network flow CSV supplies benign and malicious flow rows; "
            "official SecurityEvents rows must be covered exactly"
        ),
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "processed_dir": str(args.processed_dir),
        "ground_truth_dir": str(args.ground_truth_dir),
        "processed_files": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in processed_paths
        ],
        "ground_truth_files": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in ground_truth_paths
        ],
        "input_counters": dict(sorted(counters.items())),
        "official_ground_truth_coverage": official_coverage,
        "label_index": index,
        "source_member_scope": None,
        "source_member_scope_reason": (
            "official processed CSV shards are global chronological partitions and "
            "do not have a one-to-one filename mapping to the 64 scenario PCAPs"
        ),
        "resolver_tolerance_ns": args.resolver_tolerance_ns,
        "ready_for_pcap_coverage_dry_run": False,
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

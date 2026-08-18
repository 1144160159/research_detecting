from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file


DATASET_ID = "cic_bot_iot"
PROTOCOLS = {"tcp": 6, "udp": 17, "icmp": 1, "icmp6": 58, "ipv6-icmp": 58}
CATEGORY_FAMILIES = {
    "normal": "Benign",
    "ddos": "DDoS",
    "dos": "DoS",
    "reconnaissance": "Reconnaissance",
    "theft": "Data Theft",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth-dir", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--resolver-tolerance-ns", type=int, default=1_000_000)
    return parser.parse_args()


def clean_label(value: str) -> str:
    cleaned = " ".join(str(value).strip().replace("_", " ").split())
    aliases = {
        "ddos": "DDoS",
        "dos": "DoS",
        "http": "HTTP",
        "tcp": "TCP",
        "udp": "UDP",
        "os scan": "OS Scan",
        "os fingerprint": "OS Fingerprint",
        "service scan": "Service Scan",
        "data exfiltration": "Data Exfiltration",
        "keylogging": "Keylogging",
        "normal": "Normal",
        "reconnaissance": "Reconnaissance",
        "theft": "Theft",
    }
    return aliases.get(cleaned.lower(), cleaned.title())


def labels(attack: str, category: str, subcategory: str) -> tuple[str, str, int]:
    binary = int(float(str(attack).strip()))
    category_key = " ".join(str(category).strip().lower().split())
    if binary == 0:
        if category_key != "normal":
            raise ValueError("BoT-IoT benign row has non-Normal category")
        return "Benign", "Benign", 0
    if category_key == "normal":
        raise ValueError("BoT-IoT malicious row has Normal category")
    try:
        family = CATEGORY_FAMILIES[category_key]
    except KeyError as error:
        raise ValueError(f"unmapped BoT-IoT category: {category!r}") from error
    fine = f"{clean_label(category)} - {clean_label(subcategory)}"
    return fine, family, 1


def port_number(value: str) -> int:
    cleaned = str(value).strip()
    if not cleaned:
        return 0
    return int(cleaned, 0)


def protocol_number(value: str) -> int:
    cleaned = str(value).strip().lower()
    if cleaned not in PROTOCOLS:
        raise ValueError(f"protocol without supported IP flow identity: {value!r}")
    return PROTOCOLS[cleaned]


def epoch_ns(value: str) -> int:
    return int(round(float(str(value).strip()) * 1_000_000_000))


def expected_path_label(path: Path) -> tuple[str, str] | None:
    aliases = {
        "DDoS_HTTP": ("DDoS", "HTTP"),
        "DDoS_TCP": ("DDoS", "TCP"),
        "DDoS_UDP": ("DDoS", "UDP"),
        "DoS_HTTP": ("DoS", "HTTP"),
        "DoS_TCP": ("DoS", "TCP"),
        "DoS_UDP": ("DoS", "UDP"),
        "OS Scan": ("Reconnaissance", "OS Fingerprint"),
        "Service Scan": ("Reconnaissance", "Service Scan"),
        "Data Exfiltration": ("Theft", "Data Exfiltration"),
        "Keylogging": ("Theft", "Keylogging"),
    }
    return aliases.get(path.stem, aliases.get(clean_label(path.stem)))


def preflight_headers(paths: list[Path]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    required = {
        "stime",
        "ltime",
        "proto",
        "saddr",
        "sport",
        "daddr",
        "dport",
        "attack",
        "category",
    }
    for path in paths:
        with path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.reader(handle, delimiter=";")
            try:
                header = next(reader)
            except StopIteration as error:
                raise ValueError(f"empty BoT-IoT ground truth CSV: {path}") from error
        missing = sorted(required - set(header))
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        if "subcategory" in header:
            aliases[str(path)] = "subcategory"
        elif "subsubcategory" in header:
            aliases[str(path)] = "subsubcategory"
        else:
            raise ValueError(f"{path} has no subcategory column or official alias")
    return aliases


def records(
    paths: list[Path], counters: Counter[str], subcategory_columns: dict[str, str]
) -> Iterator[dict[str, Any]]:
    for path in paths:
        expected = expected_path_label(path)
        with path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.DictReader(handle, delimiter=";")
            subcategory_column = subcategory_columns[str(path)]
            for row_number, row in enumerate(reader, start=2):
                counters["rows"] += 1
                try:
                    fine, family, binary = labels(
                        row["attack"], row["category"], row[subcategory_column]
                    )
                    if binary and expected is not None:
                        actual = (
                            clean_label(row["category"]),
                            clean_label(row[subcategory_column]),
                        )
                        if actual != expected:
                            counters["path_label_conflicts"] += 1
                    protocol = protocol_number(row["proto"])
                    src_ip = str(ipaddress.ip_address(row["saddr"].strip()))
                    dst_ip = str(ipaddress.ip_address(row["daddr"].strip()))
                    src_port = port_number(row["sport"])
                    dst_port = port_number(row["dport"])
                    start_ns = epoch_ns(row["stime"])
                    end_ns = max(start_ns, epoch_ns(row["ltime"]))
                except (ValueError, TypeError, OverflowError) as error:
                    counters["excluded_rows_without_supported_ip_five_tuple"] += 1
                    counters[f"excluded_protocol::{str(row.get('proto', '')).lower()}"] += 1
                    if len(str(error)):
                        counters[f"excluded_error::{type(error).__name__}"] += 1
                    continue
                counters["valid_rows"] += 1
                counters[f"fine::{fine}"] += 1
                counters[f"family::{family}"] += 1
                counters[f"protocol::{protocol}"] += 1
                material = f"{path.name}\0{row_number}"
                yield {
                    "record_id": hashlib.sha256(material.encode("utf-8")).hexdigest(),
                    "source_member": None,
                    "src_ip": src_ip,
                    "src_port": src_port,
                    "dst_ip": dst_ip,
                    "dst_port": dst_port,
                    "protocol": protocol,
                    "start_ns": start_ns,
                    "end_ns": end_ns,
                    "fine_label": fine,
                    "family_label": family,
                    "binary_label": binary,
                    "label_source": f"{path}#{row_number}",
                }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = sorted(args.ground_truth_dir.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"no BoT-IoT ground truth CSVs under {args.ground_truth_dir}")
    counters: Counter[str] = Counter()
    subcategory_columns = preflight_headers(paths)
    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index,
        DATASET_ID,
        records(paths, counters, subcategory_columns),
        registry_sha256,
    )
    excluded = counters["excluded_rows_without_supported_ip_five_tuple"]
    report = {
        "schema_version": "caeos_bot_iot_label_index_audit_v1",
        "dataset_id": DATASET_ID,
        "authority": "official semicolon-delimited Ground Truth flow CSVs",
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "ground_truth_dir": str(args.ground_truth_dir),
        "ground_truth_files": [
            {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
            for path in paths
        ],
        "subcategory_columns": subcategory_columns,
        "input_counters": dict(sorted(counters.items())),
        "label_index": index,
        "source_member_scope": None,
        "resolver_tolerance_ns": args.resolver_tolerance_ns,
        "execution_policy": {
            "streaming_csv": True,
            "insert_batch_rows": 10_000,
            "sqlite_worker_threads": 8,
            "single_sqlite_writer": True,
        },
        "path_label_conflicts": counters["path_label_conflicts"],
        "exclusion_summary": {
            "rule": "exclude only official rows that cannot form a supported IP flow identity",
            "excluded_rows": excluded,
            "excluded_row_fraction": excluded / counters["rows"] if counters["rows"] else 0.0,
            "source_files_modified": False,
        },
        "ready_for_pcap_coverage_dry_run": counters["path_label_conflicts"] == 0,
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

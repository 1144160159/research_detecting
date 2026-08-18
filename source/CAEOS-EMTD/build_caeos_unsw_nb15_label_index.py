from __future__ import annotations

import argparse
import csv
import hashlib
import json
import socket
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import atomic_json, sha256_file
from intake_caeos_four_new_label_datasets import UNSW_COLUMNS


PROTOCOL_NUMBERS = {
    "icmp": 1,
    "igmp": 2,
    "tcp": 6,
    "udp": 17,
    "ipv6": 41,
    "ipv6-frag": 44,
    "ipv6-icmp": 58,
    "icmp6": 58,
    "ospf": 89,
    "sctp": 132,
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-dir", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    return parser.parse_args()


def port(value: str) -> int:
    text = value.strip()
    return 0 if not text or text == "-" else int(float(text))


def protocol_number(value: str) -> int | None:
    text = value.strip().lower()
    if text in PROTOCOL_NUMBERS:
        return PROTOCOL_NUMBERS[text]
    try:
        return socket.getprotobyname(text)
    except OSError:
        return None


def records(
    paths: list[Path], counters: Counter[str], fine_counts: Counter[str]
) -> Iterator[dict[str, Any]]:
    previous_last: tuple[str, ...] | None = None
    for path in paths:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            current_last: tuple[str, ...] | None = None
            for ordinal, values in enumerate(reader, start=1):
                counters["rows_read"] += 1
                current = tuple(values)
                if ordinal == 1 and previous_last is not None and current == previous_last:
                    counters["exact_split_boundary_duplicates"] += 1
                    current_last = current
                    continue
                if len(values) != len(UNSW_COLUMNS):
                    counters["rejected_rows"] += 1
                    current_last = current
                    continue
                row = dict(zip(UNSW_COLUMNS, values))
                try:
                    protocol = protocol_number(row["proto"])
                    if protocol is None:
                        counters[f"unsupported_protocol::{row['proto'].strip().lower()}"] += 1
                        continue
                    binary = int(row["label"].strip())
                    if binary not in {0, 1}:
                        raise ValueError("invalid binary label")
                    fine = row["attack_cat"].strip() if binary else "Benign"
                    if fine == "Backdoors":
                        fine = "Backdoor"
                        counters["normalized_backdoors_to_backdoor"] += 1
                    if not fine:
                        raise ValueError("empty attack category")
                    start_ns = int(round(float(row["stime"]) * 1_000_000_000))
                    end_ns = int(round(float(row["ltime"]) * 1_000_000_000))
                    if end_ns < start_ns:
                        end_ns = start_ns
                    record = {
                        "record_id": hashlib.sha256(
                            f"{path.name}\0{ordinal}".encode("utf-8")
                        ).hexdigest(),
                        "source_member": None,
                        "src_ip": row["srcip"].strip(),
                        "src_port": port(row["sport"]),
                        "dst_ip": row["dstip"].strip(),
                        "dst_port": port(row["dsport"]),
                        "protocol": protocol,
                        "start_ns": start_ns,
                        "end_ns": end_ns,
                        "fine_label": fine,
                        "family_label": fine,
                        "binary_label": binary,
                        "label_source": f"{path}#{ordinal}",
                    }
                except (KeyError, TypeError, ValueError, OSError):
                    counters["rejected_rows"] += 1
                    continue
                counters["indexed_rows"] += 1
                fine_counts[fine] += 1
                current_last = current
                yield record
            previous_last = current_last


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = [args.csv_dir / f"UNSW-NB15_{index}.csv" for index in range(1, 5)]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing UNSW full flow CSVs: {missing}")
    counters: Counter[str] = Counter()
    fine_counts: Counter[str] = Counter()
    registry_sha256 = sha256_file(args.registry)
    index = create_label_index(
        args.output_index,
        "unsw_nb15",
        records(paths, counters, fine_counts),
        registry_sha256,
    )
    expected_attacks = {
        "Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic",
        "Reconnaissance", "Shellcode", "Worms",
    }
    audit: dict[str, Any] = {
        "schema_version": "caeos_unsw_nb15_label_index_audit_v1",
        "dataset_id": "unsw_nb15",
        "csv_dir": str(args.csv_dir),
        "source_csv_sha256": {str(path): sha256_file(path) for path in paths},
        "registry_path": str(args.registry),
        "registry_sha256": registry_sha256,
        "counters": dict(sorted(counters.items())),
        "fine_label_counts": dict(sorted(fine_counts.items())),
        "all_nine_attack_categories_present": (
            set(fine_counts) - {"Benign"} == expected_attacks
        ),
        "all_supported_rows_indexed": counters["rejected_rows"] == 0,
        "unsupported_protocol_rows_are_explicitly_excluded": sum(
            value for key, value in counters.items() if key.startswith("unsupported_protocol::")
        ),
        "label_index": index,
        "ready_for_strict_pcap_alignment": True,
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

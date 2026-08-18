from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


SIGNATURE_FIELDS = (
    "dst_port",
    "protocol",
    "timestamp",
    "flow_duration",
    "total_fwd_packets",
    "total_bwd_packets",
    "total_fwd_bytes",
    "total_bwd_bytes",
    "fwd_packet_max",
    "fwd_packet_min",
    "bwd_packet_max",
    "bwd_packet_min",
    "fin_count",
    "syn_count",
    "rst_count",
    "psh_count",
    "ack_count",
    "urg_count",
    "init_fwd_window",
    "init_bwd_window",
    "fwd_active_packets",
    "fwd_segment_min",
)

SIGNATURE_PROFILES = {
    "full": SIGNATURE_FIELDS,
    "flow_core": (
        "dst_port",
        "protocol",
        "timestamp",
        "flow_duration",
        "total_fwd_packets",
        "total_bwd_packets",
        "total_fwd_bytes",
        "total_bwd_bytes",
    ),
    "packet_core": (
        "dst_port",
        "protocol",
        "timestamp",
        "total_fwd_packets",
        "total_bwd_packets",
        "total_fwd_bytes",
        "total_bwd_bytes",
    ),
    "count_core": (
        "dst_port",
        "protocol",
        "timestamp",
        "total_fwd_packets",
        "total_bwd_packets",
    ),
}

ALIASES = {
    "dst_port": {"dstport"},
    "protocol": {"protocol"},
    "timestamp": {"timestamp"},
    "flow_duration": {"flowduration"},
    "total_fwd_packets": {"totfwdpkts", "totalfwdpacket", "totalfwdpackets"},
    "total_bwd_packets": {"totbwdpkts", "totalbwdpacket", "totalbwdpackets"},
    "total_fwd_bytes": {"totlenfwdpkts", "totallengthoffwdpacket"},
    "total_bwd_bytes": {"totlenbwdpkts", "totallengthofbwdpacket"},
    "fwd_packet_max": {"fwdpktlenmax", "fwdpacketlengthmax"},
    "fwd_packet_min": {"fwdpktlenmin", "fwdpacketlengthmin"},
    "bwd_packet_max": {"bwdpktlenmax", "bwdpacketlengthmax"},
    "bwd_packet_min": {"bwdpktlenmin", "bwdpacketlengthmin"},
    "fin_count": {"finflagcnt", "finflagcount"},
    "syn_count": {"synflagcnt", "synflagcount"},
    "rst_count": {"rstflagcnt", "rstflagcount"},
    "psh_count": {"pshflagcnt", "pshflagcount"},
    "ack_count": {"ackflagcnt", "ackflagcount"},
    "urg_count": {"urgflagcnt", "urgflagcount"},
    "init_fwd_window": {"initfwdwinbyts", "fwdinitwinbytes"},
    "init_bwd_window": {"initbwdwinbyts", "bwdinitwinbytes"},
    "fwd_active_packets": {"fwdactdatapkts"},
    "fwd_segment_min": {"fwdsegsizemin"},
    "label": {"label"},
}


def normalized_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def field_indices(header: list[str], include_label: bool) -> dict[str, int]:
    available: dict[str, int] = {}
    for index, name in enumerate(header):
        token = normalized_header(name)
        for field, aliases in ALIASES.items():
            if token in aliases:
                available[field] = index
                break
    required = set(SIGNATURE_FIELDS)
    if include_label:
        required.add("label")
    missing = sorted(required - set(available))
    if missing:
        raise ValueError(f"required CICIDS2018 join columns missing: {missing}")
    return available


def normalized_number(value: str) -> str:
    try:
        number = Decimal(value.strip())
    except InvalidOperation as error:
        raise ValueError(f"invalid numeric join value: {value!r}") from error
    if not number.is_finite():
        raise ValueError(f"non-finite numeric join value: {value!r}")
    if number == number.to_integral_value():
        return str(int(number))
    return format(number.normalize(), "f")


def normalized_timestamp(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    for pattern in (
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %I:%M:%S.%f %p",
        "%d/%m/%Y %H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(cleaned, pattern).strftime("%Y%m%d%H%M%S.%f")
        except ValueError:
            continue
    raise ValueError(f"unsupported CICIDS2018 timestamp: {value!r}")


def row_signature(
    row: list[str], indices: dict[str, int], fields: tuple[str, ...] = SIGNATURE_FIELDS
) -> bytes:
    values = []
    for field in fields:
        raw = row[indices[field]]
        values.append(
            normalized_timestamp(raw) if field == "timestamp" else normalized_number(raw)
        )
    return hashlib.sha256("\0".join(values).encode("ascii")).digest()


def csv_rows(path: Path) -> tuple[list[str], Iterable[list[str]]]:
    handle = path.open("r", encoding="utf-8-sig", errors="strict", newline="")
    reader = csv.reader(handle)
    header = next(reader)

    def rows() -> Iterable[list[str]]:
        try:
            yield from reader
        finally:
            handle.close()

    return header, rows()


def audit_day(
    official_csv: Path,
    regenerated_dir: Path,
    maximum_generated_files: int = 0,
) -> dict[str, Any]:
    official_header, official_rows = csv_rows(official_csv)
    official_indices = field_indices(official_header, include_label=True)
    labels_by_profile: dict[str, dict[bytes, str | None]] = {
        profile: {} for profile in SIGNATURE_PROFILES
    }
    official_signature_counts: dict[str, Counter[bytes]] = {
        profile: Counter() for profile in SIGNATURE_PROFILES
    }
    official_label_counts: Counter[str] = Counter()
    counters: Counter[str] = Counter()
    for row in official_rows:
        counters["official_rows"] += 1
        if not row or normalized_header(row[-1]) == "label":
            counters["official_repeated_or_empty_rows"] += 1
            continue
        try:
            label = row[official_indices["label"]].strip()
        except (IndexError, ValueError):
            counters["official_invalid_rows"] += 1
            continue
        if not label:
            counters["official_invalid_rows"] += 1
            continue
        official_label_counts[label] += 1
        for profile, fields in SIGNATURE_PROFILES.items():
            signature = row_signature(row, official_indices, fields)
            official_signature_counts[profile][signature] += 1
            labels = labels_by_profile[profile]
            previous = labels.get(signature, label)
            labels[signature] = label if previous == label else None

    generated_files = sorted(regenerated_dir.glob("*Flow.csv"))
    if maximum_generated_files > 0:
        generated_files = generated_files[:maximum_generated_files]
    matched_label_counts: Counter[str] = Counter()
    unmatched_examples: list[dict[str, str]] = []
    generated_signature_counts: Counter[bytes] = Counter()
    profile_counters: dict[str, Counter[str]] = {
        profile: Counter() for profile in SIGNATURE_PROFILES
    }
    for path in generated_files:
        header, rows = csv_rows(path)
        indices = field_indices(header, include_label=False)
        for row in rows:
            counters["generated_rows"] += 1
            try:
                signature = row_signature(row, indices)
            except (IndexError, ValueError):
                counters["generated_invalid_rows"] += 1
                continue
            generated_signature_counts[signature] += 1
            for profile, fields in SIGNATURE_PROFILES.items():
                profile_signature = row_signature(row, indices, fields)
                labels = labels_by_profile[profile]
                if profile_signature not in labels:
                    profile_counters[profile]["unmatched"] += 1
                elif labels[profile_signature] is None:
                    profile_counters[profile]["conflicting"] += 1
                else:
                    profile_counters[profile]["matched"] += 1
            if signature not in labels_by_profile["full"]:
                counters["generated_unmatched_rows"] += 1
                if len(unmatched_examples) < 20:
                    unmatched_examples.append(
                        {
                            "file": str(path),
                            "timestamp": row[indices["timestamp"]],
                            "dst_port": row[indices["dst_port"]],
                            "protocol": row[indices["protocol"]],
                            "flow_duration": row[indices["flow_duration"]],
                        }
                    )
                continue
            label = labels_by_profile["full"][signature]
            if label is None:
                counters["generated_conflicting_label_rows"] += 1
                continue
            counters["generated_matched_rows"] += 1
            matched_label_counts[label] += 1

    generated_valid = counters["generated_rows"] - counters["generated_invalid_rows"]
    counters["official_unique_signatures"] = len(labels_by_profile["full"])
    counters["official_conflicting_signatures"] = sum(
        label is None for label in labels_by_profile["full"].values()
    )
    counters["official_duplicate_rows_same_signature"] = sum(
        count - 1 for count in official_signature_counts["full"].values() if count > 1
    )
    counters["generated_duplicate_rows_same_signature"] = sum(
        count - 1 for count in generated_signature_counts.values() if count > 1
    )
    profile_audit = {}
    for profile, profile_counts in profile_counters.items():
        labels = labels_by_profile[profile]
        valid = sum(profile_counts.values())
        profile_audit[profile] = {
            "fields": list(SIGNATURE_PROFILES[profile]),
            "official_unique_signatures": len(labels),
            "official_conflicting_signatures": sum(
                label is None for label in labels.values()
            ),
            "official_duplicate_rows_same_signature": sum(
                count - 1
                for count in official_signature_counts[profile].values()
                if count > 1
            ),
            "generated_counts": dict(sorted(profile_counts.items())),
            "generated_match_fraction": (
                profile_counts["matched"] / valid if valid else 0.0
            ),
        }
    return {
        "schema_version": "caeos_cicids2018_official_flow_join_audit_v1",
        "official_csv": str(official_csv),
        "regenerated_dir": str(regenerated_dir),
        "generated_file_count": len(generated_files),
        "signature_fields": list(SIGNATURE_FIELDS),
        "counters": dict(sorted(counters.items())),
        "official_label_counts": dict(sorted(official_label_counts.items())),
        "matched_label_counts": dict(sorted(matched_label_counts.items())),
        "generated_match_fraction": (
            counters["generated_matched_rows"] / generated_valid if generated_valid else 0.0
        ),
        "signature_profile_audit": profile_audit,
        "unmatched_examples": unmatched_examples,
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-csv", required=True, type=Path)
    parser.add_argument("--regenerated-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--maximum-generated-files", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    audit = audit_day(
        args.official_csv,
        args.regenerated_dir,
        args.maximum_generated_files,
    )
    atomic_json(args.output, audit)
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

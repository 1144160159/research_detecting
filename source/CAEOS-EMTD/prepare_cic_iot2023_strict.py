from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Sequence


FEATURE_COLUMNS = (
    "Header_Length",
    "Protocol Type",
    "Time_To_Live",
    "Rate",
    "fin_flag_number",
    "syn_flag_number",
    "rst_flag_number",
    "psh_flag_number",
    "ack_flag_number",
    "ece_flag_number",
    "cwr_flag_number",
    "ack_count",
    "syn_count",
    "fin_count",
    "rst_count",
    "HTTP",
    "HTTPS",
    "DNS",
    "Telnet",
    "SMTP",
    "SSH",
    "IRC",
    "TCP",
    "UDP",
    "DHCP",
    "ARP",
    "ICMP",
    "IGMP",
    "IPv",
    "LLC",
    "Tot sum",
    "Min",
    "Max",
    "AVG",
    "Std",
    "Tot size",
    "IAT",
    "Number",
    "Variance",
)

EXPECTED_SOURCE_LABELS = (
    "Backdoor_Malware",
    "Benign_Final",
    "BrowserHijacking",
    "CommandInjection",
    "DDoS-ACK_Fragmentation",
    "DDoS-HTTP_Flood",
    "DDoS-ICMP_Flood",
    "DDoS-ICMP_Fragmentation",
    "DDoS-PSHACK_FLOOD",
    "DDoS-RSTFINFLOOD",
    "DDoS-SYN_Flood",
    "DDoS-SlowLoris",
    "DDoS-SynonymousIP_Flood",
    "DDoS-TCP_Flood",
    "DDoS-UDP_Flood",
    "DDoS-UDP_Fragmentation",
    "DNS_Spoofing",
    "DictionaryBruteForce",
    "DoS-HTTP_Flood",
    "DoS-SYN_Flood",
    "DoS-TCP_Flood",
    "DoS-UDP_Flood",
    "MITM-ArpSpoofing",
    "Mirai-greeth_flood",
    "Mirai-greip_flood",
    "Mirai-udpplain",
    "Recon-HostDiscovery",
    "Recon-OSScan",
    "Recon-PingSweep",
    "Recon-PortScan",
    "SqlInjection",
    "Uploading_Attack",
    "VulnerabilityScan",
    "XSS",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a strict, grouped CICIoT2023 cache from original capture CSVs"
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", default="")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--max-per-class", type=int, default=1000)
    parser.add_argument("--group-rows", type=int, default=1000)
    parser.add_argument("--expected-source-files", type=int, default=309)
    return parser.parse_args()


def canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_label(source_label: str) -> str:
    return "Benign" if source_label == "Benign_Final" else source_label


def label_rng(seed: int, label: str) -> random.Random:
    material = hashlib.sha256(f"{seed}\0{label}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(material[:8], "big"))


def source_files(input_dir: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for label_dir in sorted(input_dir.iterdir(), key=lambda path: path.name):
        if not label_dir.is_dir() or label_dir.name == "MERGED_CSV":
            continue
        for path in sorted(label_dir.glob("*.csv"), key=lambda value: value.name):
            if path.is_file():
                files.append((label_dir.name, path))
    return files


def validate_sources(
    files: Sequence[tuple[str, Path]],
    expected_labels: set[str] | None,
    expected_source_files: int | None,
) -> None:
    if not files:
        raise FileNotFoundError("no original CICIoT2023 class CSV files found")
    observed_labels = {label for label, _ in files}
    if expected_labels is not None and observed_labels != expected_labels:
        raise ValueError(
            "CICIoT2023 source labels mismatch: "
            f"missing={sorted(expected_labels - observed_labels)}, "
            f"unexpected={sorted(observed_labels - expected_labels)}"
        )
    if expected_source_files is not None and len(files) != expected_source_files:
        raise ValueError(
            "CICIoT2023 source file count mismatch: "
            f"expected={expected_source_files}, actual={len(files)}"
        )


def capture_group(relative_path: str, row_index: int, group_rows: int) -> str:
    block_index = row_index // group_rows
    return hashlib.sha256(
        f"{relative_path}\0{block_index}".encode("utf-8")
    ).hexdigest()


def _row_from_line(raw: bytes) -> list[str]:
    decoded = raw.decode("utf-8-sig", errors="replace")
    return next(csv.reader([decoded]))


def build_cache(
    input_dir: str,
    output_path: str,
    seed: int,
    max_per_class: int,
    group_rows: int,
    metadata_path: str = "",
    expected_labels: set[str] | None = None,
    expected_source_files: int | None = None,
) -> dict[str, object]:
    if max_per_class <= 0:
        raise ValueError("max_per_class must be positive")
    if group_rows <= 0:
        raise ValueError("group_rows must be positive")
    source_root = Path(input_dir).resolve()
    files = source_files(source_root)
    validate_sources(files, expected_labels, expected_source_files)

    reservoirs: dict[str, list[tuple[tuple[str, ...], str]]] = {
        normalized_label(label): [] for label, _ in files
    }
    seen: Counter[str] = Counter()
    malformed: Counter[str] = Counter()
    random_by_label = {
        label: label_rng(seed, label) for label in reservoirs
    }
    source_reports: list[dict[str, object]] = []

    for source_label, path in files:
        label = normalized_label(source_label)
        relative = path.relative_to(source_root).as_posix()
        digest = hashlib.sha256()
        file_rows = 0
        file_malformed = 0
        with path.open("rb") as handle:
            try:
                raw_header = next(handle)
            except StopIteration as error:
                raise ValueError(f"empty CICIoT2023 source CSV: {path}") from error
            digest.update(raw_header)
            header = tuple(value.strip() for value in _row_from_line(raw_header))
            if header != FEATURE_COLUMNS:
                raise ValueError(
                    f"CICIoT2023 header mismatch in {path}: {header!r}"
                )
            for row_index, raw in enumerate(handle):
                digest.update(raw)
                row = _row_from_line(raw)
                if len(row) != len(FEATURE_COLUMNS):
                    file_malformed += 1
                    continue
                values = tuple(value.strip() for value in row)
                seen[label] += 1
                file_rows += 1
                group = capture_group(relative, row_index, group_rows)
                reservoir = reservoirs[label]
                if len(reservoir) < max_per_class:
                    reservoir.append((values, group))
                else:
                    replacement = random_by_label[label].randrange(seen[label])
                    if replacement < max_per_class:
                        reservoir[replacement] = (values, group)
        malformed[label] += file_malformed
        source_reports.append(
            {
                "path": relative,
                "source_label": source_label,
                "normalized_label": label,
                "size_bytes": path.stat().st_size,
                "sha256": digest.hexdigest(),
                "valid_rows": file_rows,
                "malformed_rows": file_malformed,
            }
        )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([*FEATURE_COLUMNS, "CaptureGroup", "Attack"])
        for label in sorted(reservoirs):
            for values, group in reservoirs[label]:
                writer.writerow([*values, group, label])

    source_identity = [
        {
            "path": report["path"],
            "size_bytes": report["size_bytes"],
            "sha256": report["sha256"],
        }
        for report in source_reports
    ]
    report: dict[str, object] = {
        "schema_version": "cic_iot2023_strict_cache_v1",
        "input_dir": str(source_root),
        "source_selection": {
            "pattern": "<class>/*.csv",
            "merged_csv_excluded": True,
            "source_file_count": len(files),
        },
        "source_manifest_sha256": canonical_hash(source_identity),
        "source_files": source_reports,
        "seed": seed,
        "max_per_class": max_per_class,
        "group_rows": group_rows,
        "sampling": "per-class deterministic Algorithm R reservoir",
        "rows_seen_per_class": dict(sorted(seen.items())),
        "rows_sampled_per_class": {
            label: len(rows) for label, rows in sorted(reservoirs.items())
        },
        "malformed_rows_per_class": dict(sorted(malformed.items())),
        "output_csv": str(output.resolve()),
        "output_rows": sum(len(rows) for rows in reservoirs.values()),
        "output_sha256": file_sha256(output),
        "feature_columns": list(FEATURE_COLUMNS),
        "label_column": "Attack",
        "benign_label": "Benign",
        "group_column": "CaptureGroup",
        "group_definition": (
            "sha256(relative original capture CSV path, contiguous source row block); "
            "label and feature values excluded"
        ),
    }
    metadata = (
        Path(metadata_path)
        if metadata_path
        else Path(f"{output}.json")
    )
    metadata.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    args = parse_arguments()
    report = build_cache(
        args.input_dir,
        args.output,
        args.seed,
        args.max_per_class,
        args.group_rows,
        args.metadata,
        expected_labels=set(EXPECTED_SOURCE_LABELS),
        expected_source_files=args.expected_source_files,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

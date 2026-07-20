from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence


IDENTITY_COLUMNS = (
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
)

FEATURE_COLUMNS = (
    "Source Port",
    "Destination Port",
    "Protocol",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Max",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Fwd Packet Length Std",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Fwd IAT Mean",
    "Fwd IAT Std",
    "Fwd IAT Max",
    "Fwd IAT Min",
    "Bwd IAT Total",
    "Bwd IAT Mean",
    "Bwd IAT Std",
    "Bwd IAT Max",
    "Bwd IAT Min",
    "Fwd PSH Flags",
    "Bwd PSH Flags",
    "Fwd URG Flags",
    "Bwd URG Flags",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "CWE Flag Count",
    "ECE Flag Count",
    "Down/Up Ratio",
    "Average Packet Size",
    "Avg Fwd Segment Size",
    "Avg Bwd Segment Size",
    "Subflow Fwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Bwd Packets",
    "Subflow Bwd Bytes",
    "Init_Win_bytes_forward",
    "Init_Win_bytes_backward",
    "act_data_pkt_fwd",
    "min_seg_size_forward",
    "Active Mean",
    "Active Std",
    "Active Max",
    "Active Min",
    "Idle Mean",
    "Idle Std",
    "Idle Max",
    "Idle Min",
)

PRIMARY_ATTACK_LABELS = (
    "Bot",
    "DDoS",
    "DoS GoldenEye",
    "DoS Hulk",
    "DoS Slowhttptest",
    "DoS slowloris",
    "FTP-Patator",
    "PortScan",
    "SSH-Patator",
    "Web Attack - Brute Force",
    "Web Attack - XSS",
)

LOW_SUPPORT_ATTACK_LABELS = (
    "Heartbleed",
    "Infiltration",
    "Web Attack - Sql Injection",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean and merge CIC-IDS2017 labelled-flow CSV files"
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", default="")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_label(value: str) -> str:
    label = " ".join(str(value).strip().split())
    if not label or label.lower() == "label":
        return ""
    lowered = label.lower()
    if lowered == "benign":
        return "Benign"
    if lowered.startswith("web attack"):
        if "brute force" in lowered:
            return "Web Attack - Brute Force"
        if "sql injection" in lowered:
            return "Web Attack - Sql Injection"
        if "xss" in lowered:
            return "Web Attack - XSS"
    return label


def header_index(header: Sequence[str]) -> dict[str, int]:
    indices: dict[str, int] = {}
    for index, value in enumerate(header):
        indices.setdefault(str(value).strip(), index)
    required = set(FEATURE_COLUMNS) | set(IDENTITY_COLUMNS) | {"Label"}
    missing = sorted(required - set(indices))
    if missing:
        raise ValueError(f"missing CIC-IDS2017 columns: {missing}")
    return indices


def _value(row: Sequence[str], indices: Mapping[str, int], column: str) -> str:
    index = indices[column]
    return str(row[index]).strip() if index < len(row) else ""


def flow_group(row: Sequence[str], indices: Mapping[str, int], capture: str) -> str:
    source = (
        _value(row, indices, "Source IP"),
        _value(row, indices, "Source Port"),
    )
    destination = (
        _value(row, indices, "Destination IP"),
        _value(row, indices, "Destination Port"),
    )
    first, second = sorted((source, destination))
    timestamp = _value(row, indices, "Timestamp")
    material = "\0".join(
        (
            capture,
            first[0],
            first[1],
            second[0],
            second[1],
            _value(row, indices, "Protocol"),
            timestamp,
            _value(row, indices, "Flow Duration"),
            _value(row, indices, "Total Fwd Packets"),
            _value(row, indices, "Total Backward Packets"),
            _value(row, indices, "Total Length of Fwd Packets"),
            _value(row, indices, "Total Length of Bwd Packets"),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _input_files(input_dir: Path) -> list[Path]:
    files = sorted(path for path in input_dir.rglob("*.csv") if path.is_file())
    if not files:
        raise FileNotFoundError(f"no CSV files found under {input_dir}")
    return files


def build_dataset(
    input_dir: str,
    output_path: str,
    metadata_path: str = "",
) -> dict[str, object]:
    source_root = Path(input_dir)
    files = _input_files(source_root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    label_counts: Counter[str] = Counter()
    file_reports = []
    skipped_blank_labels = 0
    malformed_rows = 0
    written_rows = 0

    with output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow([*FEATURE_COLUMNS, "Flow_Group", "Capture_ID", "Label"])
        for source in files:
            per_file: Counter[str] = Counter()
            file_blank = 0
            file_malformed = 0
            with source.open(
                "r", encoding="utf-8-sig", errors="replace", newline=""
            ) as handle:
                reader = csv.reader(handle)
                try:
                    indices = header_index(next(reader))
                except StopIteration as error:
                    raise ValueError(f"empty CIC-IDS2017 CSV: {source}") from error
                maximum_index = max(indices.values())
                for row in reader:
                    if len(row) <= maximum_index:
                        file_malformed += 1
                        continue
                    label = normalize_label(_value(row, indices, "Label"))
                    if not label:
                        file_blank += 1
                        continue
                    capture = source.stem
                    writer.writerow(
                        [
                            *[_value(row, indices, column) for column in FEATURE_COLUMNS],
                            flow_group(row, indices, capture),
                            capture,
                            label,
                        ]
                    )
                    per_file[label] += 1
                    written_rows += 1
            skipped_blank_labels += file_blank
            malformed_rows += file_malformed
            label_counts.update(per_file)
            file_reports.append(
                {
                    "path": str(source.resolve()),
                    "size_bytes": source.stat().st_size,
                    "sha256": sha256(source),
                    "written_rows": int(sum(per_file.values())),
                    "skipped_blank_labels": file_blank,
                    "malformed_rows": file_malformed,
                    "labels": dict(sorted(per_file.items())),
                }
            )

    observed_attacks = set(label_counts) - {"Benign"}
    declared_attacks = set(PRIMARY_ATTACK_LABELS) | set(LOW_SUPPORT_ATTACK_LABELS)
    report = {
        "schema_version": "cicids2017_strict_source_v1",
        "input_dir": str(source_root.resolve()),
        "files": file_reports,
        "output_csv": str(output.resolve()),
        "output_sha256": sha256(output),
        "rows": written_rows,
        "skipped_blank_labels": skipped_blank_labels,
        "malformed_rows": malformed_rows,
        "per_class": dict(sorted(label_counts.items())),
        "primary_attack_labels": list(PRIMARY_ATTACK_LABELS),
        "low_support_attack_labels": list(LOW_SUPPORT_ATTACK_LABELS),
        "undeclared_attack_labels": sorted(observed_attacks - declared_attacks),
        "missing_declared_attack_labels": sorted(declared_attacks - observed_attacks),
        "group_column": "Flow_Group",
        "group_definition": (
            "sha256(capture, unordered endpoint-port pair, protocol, exact timestamp, "
            "duration, bidirectional packet and byte counts); "
            "label excluded"
        ),
        "feature_columns": list(FEATURE_COLUMNS),
    }
    metadata = (
        Path(metadata_path)
        if metadata_path
        else output.with_suffix(output.suffix + ".json")
    )
    metadata.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    args = parse_arguments()
    report = build_dataset(args.input_dir, args.output, args.metadata)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

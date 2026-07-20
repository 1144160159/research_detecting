from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


IDENTITY_COLUMNS = ["SourcePcap", "CaptureGroup", "Attack"]
BASE_COLUMNS = [
    "src_port",
    "dst_port",
    "protocol",
    "ip_version",
    "vlan_id",
    "bidirectional_duration_ms",
    "bidirectional_packets",
    "bidirectional_bytes",
    "src2dst_duration_ms",
    "src2dst_packets",
    "src2dst_bytes",
    "dst2src_duration_ms",
    "dst2src_packets",
    "dst2src_bytes",
]
STAT_PREFIXES = ("bidirectional", "src2dst", "dst2src")
SIZE_STAT_COLUMNS = [
    f"{prefix}_{stat}_ps"
    for prefix in STAT_PREFIXES
    for stat in ("min", "mean", "stddev", "max")
]
PIAT_STAT_COLUMNS = [
    f"{prefix}_{stat}_piat_ms"
    for prefix in STAT_PREFIXES
    for stat in ("min", "mean", "stddev", "max")
]
FLAG_COLUMNS = [
    f"{prefix}_{flag}_packets"
    for prefix in STAT_PREFIXES
    for flag in ("syn", "cwr", "ece", "urg", "ack", "psh", "rst", "fin")
]
FEATURE_COLUMNS = BASE_COLUMNS + SIZE_STAT_COLUMNS + PIAT_STAT_COLUMNS + FLAG_COLUMNS
OUTPUT_COLUMNS = FEATURE_COLUMNS + IDENTITY_COLUMNS


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract leakage-resistant NFStream features from USTC-TFC2016"
    )
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--parts-dir", default="")
    parser.add_argument("--include", default=".*", help="Regex over relative PCAP paths")
    parser.add_argument("--group-window-ms", type=int, default=300000)
    parser.add_argument("--idle-timeout", type=int, default=120)
    parser.add_argument("--active-timeout", type=int, default=1800)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def label_for(relative_path: Path) -> str:
    if relative_path.parts[0].lower() == "benign":
        return "Benign"
    return relative_path.stem


def part_name(relative_path: Path) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", relative_path.as_posix())
    return f"{safe}.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_pcaps(root: Path, include: str) -> list[Path]:
    pattern = re.compile(include, re.IGNORECASE)
    return [
        path
        for path in sorted(root.rglob("*.pcap"))
        if pattern.search(path.relative_to(root).as_posix())
    ]


def extract_pcap(
    pcap: Path,
    root: Path,
    part: Path,
    group_window_ms: int,
    idle_timeout: int,
    active_timeout: int,
) -> int:
    from nfstream import NFStreamer

    relative = pcap.relative_to(root)
    label = label_for(relative)
    source = relative.as_posix()
    part.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with part.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        streamer = NFStreamer(
            source=str(pcap),
            statistical_analysis=True,
            splt_analysis=0,
            n_dissections=0,
            idle_timeout=idle_timeout,
            active_timeout=active_timeout,
        )
        for flow in streamer:
            first_seen = int(getattr(flow, "bidirectional_first_seen_ms", 0))
            window = first_seen // group_window_ms
            row = {column: getattr(flow, column, 0) for column in FEATURE_COLUMNS}
            row.update(
                {
                    "SourcePcap": source,
                    "CaptureGroup": f"{source}::window_{window}",
                    "Attack": label,
                }
            )
            writer.writerow(row)
            rows += 1
    return rows


def merge_parts(parts: Iterable[Path], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with output.open("w", encoding="utf-8", newline="") as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for part in parts:
            with part.open("r", encoding="utf-8", newline="") as part_handle:
                reader = csv.DictReader(part_handle)
                for row in reader:
                    writer.writerow(row)
                    total += 1
    return total


def main() -> None:
    args = parse_arguments()
    root = Path(args.input_root).resolve()
    output = Path(args.output).resolve()
    parts_dir = (
        Path(args.parts_dir).resolve()
        if args.parts_dir
        else output.parent / f"{output.stem}_parts"
    )
    pcaps = discover_pcaps(root, args.include)
    if not pcaps:
        raise ValueError(f"no PCAP files matched {args.include!r} under {root}")

    reports = []
    parts = []
    for pcap in pcaps:
        relative = pcap.relative_to(root)
        part = parts_dir / part_name(relative)
        if args.force or not part.exists():
            rows = extract_pcap(
                pcap,
                root,
                part,
                args.group_window_ms,
                args.idle_timeout,
                args.active_timeout,
            )
        else:
            with part.open("r", encoding="utf-8", newline="") as handle:
                rows = max(sum(1 for _ in handle) - 1, 0)
        parts.append(part)
        reports.append(
            {
                "source_pcap": relative.as_posix(),
                "source_size_bytes": pcap.stat().st_size,
                "label": label_for(relative),
                "rows": rows,
                "part": str(part),
            }
        )

    total_rows = merge_parts(parts, output)
    manifest = {
        "input_root": str(root),
        "output_csv": str(output),
        "output_sha256": sha256(output),
        "rows": total_rows,
        "group_window_ms": args.group_window_ms,
        "unknown_protocol": "leave one malware family PCAP out in full",
        "known_protocol": "group known flows by source PCAP and time window",
        "feature_columns": FEATURE_COLUMNS,
        "pcaps": reports,
    }
    manifest_path = output.with_suffix(output.suffix + ".json")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

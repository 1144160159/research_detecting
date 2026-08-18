from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json


AGGREGATE_CSV_NAMES = {
    "DNN-EdgeIIoT-dataset.csv",
    "ML-EdgeIIoT-dataset.csv",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def normalized_capture_name(path: Path) -> str:
    stem = path.stem.lower()
    if stem.startswith("mitm"):
        return "mitm"
    tokens = re.findall(r"[a-z0-9]+", stem)
    tokens = [token for token in tokens if token not in {"attack", "attacks"}]
    return "".join(tokens)


def inventory(data_root: Path) -> dict[str, Any]:
    data_root = data_root.resolve()
    pcaps = sorted(path for path in data_root.rglob("*") if path.is_file() and path.suffix.lower() == ".pcap")
    csvs = sorted(path for path in data_root.rglob("*") if path.is_file() and path.suffix.lower() == ".csv")
    aggregate_csvs = [path for path in csvs if path.name in AGGREGATE_CSV_NAMES]
    paired_csvs = [path for path in csvs if path not in aggregate_csvs]
    by_key: dict[tuple[str, str], list[Path]] = {}
    for path in paired_csvs:
        relative = path.relative_to(data_root)
        key = (relative.parent.as_posix().lower(), normalized_capture_name(path))
        by_key.setdefault(key, []).append(path)

    pairs: list[dict[str, Any]] = []
    unmatched_pcaps: list[str] = []
    consumed_csvs: set[Path] = set()
    ambiguous: list[dict[str, Any]] = []
    for pcap in pcaps:
        relative = pcap.relative_to(data_root)
        key = (relative.parent.as_posix().lower(), normalized_capture_name(pcap))
        candidates = by_key.get(key, [])
        if len(candidates) != 1:
            if not candidates:
                unmatched_pcaps.append(relative.as_posix())
            else:
                ambiguous.append(
                    {
                        "pcap": relative.as_posix(),
                        "csv_candidates": [
                            path.relative_to(data_root).as_posix()
                            for path in candidates
                        ],
                    }
                )
            continue
        packet_csv = candidates[0]
        consumed_csvs.add(packet_csv)
        pair_id = hashlib.sha256(relative.as_posix().encode("utf-8")).hexdigest()[:16]
        pairs.append(
            {
                "pair_id": pair_id,
                "source_member": relative.as_posix(),
                "pcap": str(pcap),
                "pcap_relative": relative.as_posix(),
                "pcap_size": pcap.stat().st_size,
                "packet_csv": str(packet_csv),
                "packet_csv_relative": packet_csv.relative_to(data_root).as_posix(),
                "packet_csv_size": packet_csv.stat().st_size,
            }
        )

    unmatched_csvs = [
        path.relative_to(data_root).as_posix()
        for path in paired_csvs
        if path not in consumed_csvs
    ]
    report = {
        "schema_version": "caeos_edge_iiotset_pcap_inventory_v1",
        "dataset_id": "edge_iiotset",
        "data_root": str(data_root),
        "pcap_count": len(pcaps),
        "paired_packet_csv_count": len(paired_csvs),
        "pair_count": len(pairs),
        "pairs": pairs,
        "aggregate_only_csvs": [
            path.relative_to(data_root).as_posix() for path in aggregate_csvs
        ],
        "unmatched_pcaps": unmatched_pcaps,
        "unmatched_packet_csvs": unmatched_csvs,
        "ambiguous_pairs": ambiguous,
        "passed": (
            len(pcaps) > 0
            and len(pairs) == len(pcaps) == len(paired_csvs)
            and not unmatched_pcaps
            and not unmatched_csvs
            and not ambiguous
        ),
    }
    report["inventory_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return report


def main() -> None:
    args = parse_arguments()
    report = inventory(args.data_root)
    atomic_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

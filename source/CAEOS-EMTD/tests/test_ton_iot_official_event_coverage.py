from __future__ import annotations

import argparse
import csv
from pathlib import Path

from audit_caeos_ton_iot_official_event_coverage import audit
from caeos_label_alignment import create_label_index
from caeos_unified_dataset import sha256_file


FIELDS = ["ts", "src_ip", "src_port", "dst_ip", "dst_port", "proto", "type"]


def write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_official_events_are_deduplicated_and_covered_as_set(tmp_path: Path) -> None:
    ground = tmp_path / "ground"
    event = {
        "ts": "10",
        "src_ip": "192.168.1.1",
        "src_port": "1000",
        "dst_ip": "192.168.1.2",
        "dst_port": "80",
        "proto": "tcp",
        "type": "scanning",
    }
    extra = dict(event, ts="11", src_port="1001", type="ddos")
    write(ground / "GroundTruth_Network_1.csv", [event])
    write(ground / "GroundTruth_Network_2.csv", [event])
    index_path = tmp_path / "labels.sqlite"
    create_label_index(
        index_path,
        "cic_ton_iot",
        [
            {
                "src_ip": item["src_ip"],
                "src_port": int(item["src_port"]),
                "dst_ip": item["dst_ip"],
                "dst_port": int(item["dst_port"]),
                "protocol": 6,
                "start_ns": int(item["ts"]) * 1_000_000_000,
                "end_ns": int(item["ts"]) * 1_000_000_000,
                "fine_label": "Scanning" if item["type"] == "scanning" else "DDoS",
                "family_label": "Reconnaissance" if item["type"] == "scanning" else "DDoS",
                "binary_label": 1,
                "label_source": "synthetic",
            }
            for item in (event, extra)
        ],
        "registry",
    )
    report = audit(
        argparse.Namespace(
            ground_truth_dir=ground,
            label_index=index_path,
            label_index_sha256=sha256_file(index_path),
            output=tmp_path / "coverage.json",
            missing_sample_limit=10,
            batch_size=2,
        )
    )
    assert report["official_unique_events"] == 1
    assert report["covered_unique_events"] == 1
    assert report["missing_unique_events"] == 0
    assert report["coverage_fraction"] == 1.0
    assert len(report["duplicate_ground_truth_files"]) == 1
    assert report["formal_gate_passed"] is False

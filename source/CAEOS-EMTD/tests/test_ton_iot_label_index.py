from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_caeos_ton_iot_label_index import build


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_builds_complete_ton_index_and_covers_official_events(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    ground_truth = tmp_path / "ground_truth"
    rows = [
        {
            "ts": "1556021522",
            "src_ip": "192.168.1.10",
            "src_port": "1234",
            "dst_ip": "192.168.1.20",
            "dst_port": "80",
            "proto": "tcp",
            "duration": "1.25",
            "label": "0",
            "type": "normal",
        },
        {
            "ts": "1556021523",
            "src_ip": "192.168.1.31",
            "src_port": "38140",
            "dst_ip": "192.168.1.49",
            "dst_port": "1185",
            "proto": "tcp",
            "duration": "0",
            "label": "1",
            "type": "ddos",
        },
    ]
    fields = list(rows[0])
    write_csv(processed / "Network_dataset_1.csv", fields, rows)
    event_fields = [
        "ts",
        "src_ip",
        "src_port",
        "dst_ip",
        "dst_port",
        "proto",
        "type",
    ]
    write_csv(
        ground_truth / "GroundTruth_Network_1.csv",
        event_fields,
        [{key: rows[1][key] for key in event_fields}],
    )
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    output_index = tmp_path / "ton.sqlite"
    audit_output = tmp_path / "ton.audit.json"
    report = build(
        argparse.Namespace(
            processed_dir=processed,
            ground_truth_dir=ground_truth,
            registry=registry,
            output_index=output_index,
            audit_output=audit_output,
            ground_truth_missing_sample_limit=10,
            resolver_tolerance_ns=1_000_000_000,
        )
    )
    assert report["label_index"]["record_count"] == 2
    assert report["official_ground_truth_coverage"]["coverage_fraction"] is None
    assert report["input_counters"]["family::Benign"] == 1
    assert report["input_counters"]["family::DDoS"] == 1
    assert report["ready_for_pcap_coverage_dry_run"] is False

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_caeos_bot_iot_label_index import build


FIELDS = [
    "stime",
    "ltime",
    "proto",
    "saddr",
    "sport",
    "daddr",
    "dport",
    "attack",
    "category",
    "subcategory",
]


def test_builds_bot_index_and_audits_non_ip_rows(tmp_path: Path) -> None:
    ground_truth = tmp_path / "ground_truth"
    ground_truth.mkdir()
    path = ground_truth / "DDoS_HTTP.csv"
    rows = [
        {
            "stime": "1528102921.344614",
            "ltime": "1528102927.751038",
            "proto": "tcp",
            "saddr": "192.168.100.150",
            "sport": "54110",
            "daddr": "192.168.100.3",
            "dport": "80",
            "attack": "1",
            "category": "DDoS",
            "subcategory": "HTTP",
        },
        {
            "stime": "1528102928",
            "ltime": "1528102929",
            "proto": "udp",
            "saddr": "192.168.100.1",
            "sport": "53",
            "daddr": "192.168.100.2",
            "dport": "53000",
            "attack": "0",
            "category": "Normal",
            "subcategory": "Normal",
        },
        {
            "stime": "1528102928",
            "ltime": "1528102929",
            "proto": "arp",
            "saddr": "192.168.100.1",
            "sport": "",
            "daddr": "192.168.100.2",
            "dport": "",
            "attack": "0",
            "category": "Normal",
            "subcategory": "Normal",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    report = build(
        argparse.Namespace(
            ground_truth_dir=ground_truth,
            registry=registry,
            output_index=tmp_path / "bot.sqlite",
            audit_output=tmp_path / "bot.audit.json",
            resolver_tolerance_ns=1_000_000,
        )
    )
    assert report["label_index"]["record_count"] == 2
    assert report["input_counters"]["family::DDoS"] == 1
    assert report["input_counters"]["family::Benign"] == 1
    assert report["exclusion_summary"]["excluded_rows"] == 1
    assert report["path_label_conflicts"] == 0


def test_os_scan_path_maps_to_official_os_fingerprint(tmp_path: Path) -> None:
    ground_truth = tmp_path / "ground_truth"
    ground_truth.mkdir()
    path = ground_truth / "OS_Scan.csv"
    row = {
        "stime": "1526983416.729573",
        "ltime": "1526983416.729944",
        "proto": "tcp",
        "saddr": "192.168.100.7",
        "sport": "3306",
        "daddr": "192.168.100.148",
        "dport": "53126",
        "attack": "1",
        "category": "Reconnaissance",
        "subcategory": "OS_Fingerprint",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerow(row)
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    report = build(
        argparse.Namespace(
            ground_truth_dir=ground_truth,
            registry=registry,
            output_index=tmp_path / "bot.sqlite",
            audit_output=tmp_path / "bot.audit.json",
            resolver_tolerance_ns=1_000_000,
        )
    )
    assert report["path_label_conflicts"] == 0
    assert report["input_counters"]["fine::Reconnaissance - OS Fingerprint"] == 1


def test_accepts_official_dos_http_subsubcategory_header(tmp_path: Path) -> None:
    ground_truth = tmp_path / "ground_truth"
    ground_truth.mkdir()
    path = ground_truth / "DoS_HTTP.csv"
    fields = ["subsubcategory" if field == "subcategory" else field for field in FIELDS]
    row = {
        "stime": "1528088465.750358",
        "ltime": "1528088466.0",
        "proto": "tcp",
        "saddr": "192.168.100.55",
        "sport": "8080",
        "daddr": "192.168.100.3",
        "dport": "80",
        "attack": "1",
        "category": "DoS",
        "subsubcategory": "HTTP",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerow(row)
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    report = build(
        argparse.Namespace(
            ground_truth_dir=ground_truth,
            registry=registry,
            output_index=tmp_path / "bot.sqlite",
            audit_output=tmp_path / "bot.audit.json",
            resolver_tolerance_ns=1_000_000,
        )
    )
    assert report["label_index"]["record_count"] == 1
    assert report["subcategory_columns"][str(path)] == "subsubcategory"
    assert report["path_label_conflicts"] == 0

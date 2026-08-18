from __future__ import annotations

import argparse
import csv
import json
import zipfile
from pathlib import Path

from build_caeos_cicddos2019_label_index import build
from reconcile_caeos_cicddos2019_audit import reconcile


FIELDS = [
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Flow Duration",
    "Label",
]


def test_streams_cicddos_csv_archive_into_index(tmp_path: Path) -> None:
    csv_path = tmp_path / "DrDoS_UDP.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "Source IP": "172.16.0.5",
                "Source Port": "58445",
                "Destination IP": "192.168.50.1",
                "Destination Port": "4463",
                "Protocol": "17",
                "Timestamp": "2018-12-01 13:04:45.928673",
                "Flow Duration": "1",
                "Label": "DrDoS_UDP",
            }
        )
        writer.writerow(
            {
                "Source IP": "172.16.0.5",
                "Source Port": "80",
                "Destination IP": "192.168.50.1",
                "Destination Port": "50000",
                "Protocol": "6",
                "Timestamp": "2018-12-01 13:04:46.000000",
                "Flow Duration": "20",
                "Label": "BENIGN",
            }
        )
        writer.writerow(
            {
                "Source IP": "172.16.0.5",
                "Source Port": "870",
                "Destination IP": "192.168.50.4",
                "Destination Port": "2908",
                "Protocol": "17",
                "Timestamp": "2018-12-01 13:04:47.000000",
                "Flow Duration": "1",
                "Label": "NetBIOS",
            }
        )
    archive = tmp_path / "CSV-01-12.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.write(csv_path, "01-12/DrDoS_UDP.csv")
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    report = build(
        argparse.Namespace(
            csv_archive=[archive],
            registry=registry,
            output_index=tmp_path / "ddos.sqlite",
            audit_output=tmp_path / "ddos.audit.json",
            timezone_offset_hours=2,
            resolver_tolerance_ns=2_000_000,
        )
    )
    assert report["label_index"]["record_count"] == 3
    assert report["input_counters"]["family::DDoS"] == 2
    assert report["input_counters"]["family::Benign"] == 1
    assert report["input_counters"]["member_label_conflicts"] == 1
    assert report["member_name_label_consistency"]["authority"] == (
        "row_level_Label_column"
    )
    assert report["member_name_label_consistency"]["gate"] == "informational_only"
    assert report["ready_for_pcap_coverage_dry_run"] is True
    assert report["timezone_policy"]["offset_hours"] == 2
    reconciled = reconcile(
        tmp_path / "ddos.audit.json", tmp_path / "ddos.reconciled.audit.json"
    )
    assert reconciled["member_name_label_consistency"]["mismatch_count"] == 1
    assert reconciled["ready_for_pcap_coverage_dry_run"] is True
    assert (tmp_path / "ddos.reconciled.audit.json").is_file()

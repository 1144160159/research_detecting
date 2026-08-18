from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from build_caeos_dohbrw2020_label_index import build, timestamp_ns


BASE_FIELDS = [
    "SourceIP",
    "DestinationIP",
    "SourcePort",
    "DestinationPort",
    "TimeStamp",
    "Duration",
]


def test_timestamp_normalizes_halifax_dst_to_utc() -> None:
    winter_utc = datetime(2020, 1, 14, 19, 49, 1, tzinfo=timezone.utc)
    summer_utc = datetime(2020, 4, 1, 0, 53, 58, tzinfo=timezone.utc)
    assert timestamp_ns("2020-01-14 15:49:01") == int(
        winter_utc.timestamp() * 1_000_000_000
    )
    assert timestamp_ns("2020-03-31 21:53:58") == int(
        summer_utc.timestamp() * 1_000_000_000
    )


def write(path: Path, label_column: str, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BASE_FIELDS + [label_column])
        writer.writeheader()
        writer.writerows(rows)


def test_builds_deduplicated_doh_index_and_crosschecks_aggregates(
    tmp_path: Path,
) -> None:
    total = tmp_path / "Total_CSVs"
    tools = tmp_path / "CSVs"
    nondoh = {
        "SourceIP": "1.1.1.1",
        "DestinationIP": "192.168.20.1",
        "SourcePort": "443",
        "DestinationPort": "50000",
        "TimeStamp": "2020-01-14 15:49:01",
        "Duration": "4.5",
        "Label": "NonDoH",
    }
    benign = dict(nondoh, TimeStamp="2020-01-14 15:49:11", Label="Benign")
    malicious = dict(
        nondoh,
        SourceIP="8.8.8.8",
        TimeStamp="2020-03-25 04:40:42",
        Duration="120.0",
        Label="Malicious",
    )
    write(total / "l1-nondoh.csv", "Label", [nondoh])
    write(total / "l1-doh.csv", "Label", [dict(benign, Label="DoH"), dict(malicious, Label="DoH")])
    write(total / "l2-benign.csv", "Label", [benign])
    write(total / "l2-malicious.csv", "Label", [malicious])
    write(
        tools / "dns2tcp" / "all.csv",
        "DoH",
        [
            {**{key: malicious[key] for key in BASE_FIELDS}, "DoH": "True"},
            {**{key: benign[key] for key in BASE_FIELDS}, "DoH": "False"},
        ],
    )
    write(tools / "dnscat2" / "all.csv", "DoH", [])
    write(tools / "iodine" / "all.csv", "DoH", [])
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({}), encoding="utf-8")
    report = build(
        argparse.Namespace(
            total_dir=total,
            tool_csv_root=tools,
            registry=registry,
            output_index=tmp_path / "doh.sqlite",
            audit_output=tmp_path / "doh.audit.json",
            resolver_tolerance_ns=1_000_000_000,
        )
    )
    assert report["label_index"]["record_count"] == 3
    assert report["input_counters"]["family::Benign"] == 2
    assert report["input_counters"]["family::DNS Tunneling"] == 1
    assert report["input_counters"]["rows_outside_authoritative_slice"] == 1
    assert report["input_counters"]["outside_slice::DoH::False"] == 1
    assert report["input_counters"].get("invalid_rows", 0) == 0
    assert report["duplicate_precedence_crosscheck"]["passed"] is True
    assert report["label_timestamp_policy"]["input_timezone"] == "America/Halifax"
    assert report["ready_for_pcap_coverage_dry_run"] is True

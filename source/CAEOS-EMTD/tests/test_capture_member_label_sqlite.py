from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from build_caeos_capture_member_label_sqlite import build
from caeos_label_alignment import LabelResolver
from caeos_unified_dataset import sha256_file
from prepare_caeos_unified_multimodal_csv import path_label


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def arguments(
    tmp_path: Path,
    dataset_id: str,
    source_manifest: Path,
    capture_index: Path,
    inventory: Path,
    coverage: Path,
) -> argparse.Namespace:
    registry = tmp_path / f"{dataset_id}.registry.json"
    dump(registry, {"datasets": {dataset_id: {}}})
    return argparse.Namespace(
        dataset_id=dataset_id,
        source_manifest=source_manifest,
        capture_index=capture_index,
        inventory=inventory,
        coverage_summary=coverage,
        registry=registry,
        output=tmp_path / f"{dataset_id}.sqlite",
        audit_output=tmp_path / f"{dataset_id}.audit.json",
    )


def test_ciciot2023_capture_index_becomes_resolvable_sqlite(tmp_path: Path) -> None:
    source_manifest = tmp_path / "source.json"
    dump(
        source_manifest,
        {
            "datasets": [
                {
                    "id": "ciciot2023",
                    "source_root": "/data/PCAP",
                    "source_files": [
                        {"kind": "pcap", "path": "/data/PCAP/Benign_Final/a.pcap"},
                        {"kind": "pcap", "path": "/data/PCAP/DDoS-TCP_Flood/b.pcap"},
                    ],
                }
            ]
        },
    )
    capture_index = tmp_path / "capture.json"
    dump(
        capture_index,
        {
            "dataset_id": "CICIoT2023",
            "authoritative_label_source": "official directory and CSV crosscheck",
            "authority_granularity": "capture_member_not_official_flow_label",
            "captures": [
                {
                    "capture": "PCAP/Benign_Final/a.pcap",
                    "attack_fine": "BenignTraffic",
                    "attack_family": "Benign",
                    "is_malicious": False,
                },
                {
                    "capture": "PCAP/DDoS-TCP_Flood/b.pcap",
                    "attack_fine": "DDoS-TCP_Flood",
                    "attack_family": "DDoS",
                    "is_malicious": True,
                },
            ],
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "CICIoT2023",
            "formal_dataset_gate_passed": True,
            "selected_source_count": 2,
        },
    )
    inventory = tmp_path / "inventory.json"
    dump(
        inventory,
        {
            "dataset_id": "CICIoT2023",
            "label_index_sha256": sha256_file(capture_index),
            "entries": [
                {"source_id": "PCAP/Benign_Final/a.pcap", "capture": "PCAP/Benign_Final/a.pcap", "label": {"attack_fine": "BenignTraffic", "attack_family": "Benign", "is_malicious": False}},
                {"source_id": "PCAP/DDoS-TCP_Flood/b.pcap", "capture": "PCAP/DDoS-TCP_Flood/b.pcap", "label": {"attack_fine": "DDoS-TCP_Flood", "attack_family": "DDoS", "is_malicious": True}},
            ],
        },
    )
    args = arguments(
        tmp_path, "ciciot2023", source_manifest, capture_index, inventory, coverage
    )
    audit = build(args)
    assert audit["indexed_source_count"] == 2
    resolver = LabelResolver(
        args.output, "ciciot2023", audit["label_index"]["sha256"]
    )
    try:
        result = resolver.resolve(
            "Benign_Final/a.pcap", b"\x01\x01\x01\x01", 1,
            b"\x02\x02\x02\x02", 2, 6, 1, 2
        )
    finally:
        resolver.close()
    assert result.status == "aligned_unique_capture"
    assert (result.fine_label, result.family_label, result.binary_label) == (
        "BenignTraffic", "Benign", 0
    )


def test_ciciot2022_ignores_appledouble_and_indexes_official_members(tmp_path: Path) -> None:
    source_manifest = tmp_path / "source.json"
    dump(
        source_manifest,
        {
            "datasets": [
                {
                    "id": "ciciot2022",
                    "source_root": "/data",
                    "source_files": [
                        {"kind": "pcap", "path": "/data/5-Active/active.pcap"},
                        {
                            "kind": "archive",
                            "path": "/data/1-Power.tar.gz",
                            "capture_members": [
                                {"name": "1-Power/device/real.pcap"},
                                {"name": "1-Power/device/._real.pcap"},
                            ],
                        },
                        {
                            "kind": "archive",
                            "path": "/data/6-Attacks.tar.gz",
                            "capture_members": [
                                {"name": "6-Attacks/1-Flood/device/UDP/attack.pcap"}
                            ],
                        },
                    ],
                }
            ]
        },
    )
    capture_index = tmp_path / "capture.json"
    dump(
        capture_index,
        {
            "dataset_id": "CICIoT2022",
            "authoritative_label_source": "official readme and member hierarchy",
            "authority_granularity": "capture_member_not_official_flow_label",
            "active_captures": [
                {
                    "capture": "5-Active/active.pcap",
                    "attack_fine": "Benign",
                    "attack_family": "Benign",
                    "is_malicious": False,
                }
            ],
            "attack_members": [
                {
                    "member": "6-Attacks/1-Flood/device/UDP/attack.pcap",
                    "attack_fine": "Flood-UDP",
                    "attack_family": "Flood",
                    "is_malicious": True,
                }
            ],
            "benign_archive_rules": [
                {
                    "archive": "1-Power.tar.gz",
                    "attack_fine": "Benign",
                    "attack_family": "Benign",
                    "is_malicious": False,
                }
            ],
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "CICIoT2022",
            "formal_dataset_gate_passed": True,
            "selected_source_count": 3,
        },
    )
    inventory = tmp_path / "inventory.json"
    dump(
        inventory,
        {
            "dataset_id": "CICIoT2022",
            "label_index_sha256": sha256_file(capture_index),
            "entries": [
                {"source_id": "5-Active/active.pcap", "capture": "5-Active/active.pcap", "label": {"attack_fine": "Benign", "attack_family": "Benign", "is_malicious": False}},
                {"source_id": "1-Power.tar.gz::1-Power/device/real.pcap", "member": "1-Power/device/real.pcap", "label": {"attack_fine": "Benign", "attack_family": "Benign", "is_malicious": False}},
                {"source_id": "6-Attacks.tar.gz::6-Attacks/1-Flood/device/UDP/attack.pcap", "member": "6-Attacks/1-Flood/device/UDP/attack.pcap", "label": {"attack_fine": "Flood-UDP", "attack_family": "Flood", "is_malicious": True}},
            ],
        },
    )
    args = arguments(
        tmp_path, "ciciot2022", source_manifest, capture_index, inventory, coverage
    )
    audit = build(args)
    connection = sqlite3.connect(args.output)
    try:
        rows = connection.execute(
            "SELECT source_member, fine_label, family_label, binary_label "
            "FROM labels ORDER BY source_member"
        ).fetchall()
    finally:
        connection.close()
    assert len(rows) == 3
    assert not any("._" in row[0] for row in rows)
    assert (
        "6-Attacks/1-Flood/device/UDP/attack.pcap",
        "Flood-UDP",
        "Flood",
        1,
    ) in rows
    assert audit["exact_source_member_coverage"] is True


def test_capture_path_taxonomy_matches_authoritative_member_labels() -> None:
    ciciot2023 = {"label_policy": "relative_attack_directory"}
    assert path_label(ciciot2023, "Benign_Final/a.pcap").fine_label == "BenignTraffic"

    ciciot2022 = {"label_policy": "relative_capture_taxonomy"}
    flood = path_label(ciciot2022, "6-Attacks/1-Flood/device/UDP/a.pcap")
    assert (flood.fine_label, flood.family_label, flood.binary_label) == (
        "Flood-UDP", "Flood", 1
    )
    rtsp = path_label(ciciot2022, "6-Attacks/2-RTSP Brute Force/Hydra/device/a.pcap")
    assert (rtsp.fine_label, rtsp.family_label, rtsp.binary_label) == (
        "RTSP Brute Force-Hydra", "RTSP Brute Force", 1
    )
    benign = path_label(ciciot2022, "3-Interactions/device/a.pcap")
    assert (benign.fine_label, benign.family_label, benign.binary_label) == (
        "Benign", "Benign", 0
    )

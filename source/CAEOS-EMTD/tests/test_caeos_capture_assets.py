from __future__ import annotations

import struct
import zipfile
from pathlib import Path

from audit_caeos_capture_assets import audit_dataset
from caeos_unified_dataset import archive_capture_members, validate_catalog


def write_minimal_pcap(path: Path) -> None:
    path.write_bytes(
        struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
        + struct.pack("<IIII", 1, 0, 4, 4)
        + b"test"
    )


def test_extensionless_zip_member_is_detected_by_magic(tmp_path: Path) -> None:
    capture = tmp_path / "capture.pcap"
    write_minimal_pcap(capture)
    archive_path = tmp_path / "captures.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(capture, "SAT-03-11-2018_0")

    members = archive_capture_members(archive_path)

    assert len(members) == 1
    assert members[0]["name"] == "SAT-03-11-2018_0"
    assert members[0]["capture_detection"] == "magic"


def test_audit_prefers_direct_pcap_and_counts_archive_members(tmp_path: Path) -> None:
    direct = tmp_path / "direct.pcap"
    write_minimal_pcap(direct)
    archive_path = tmp_path / "captures.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("nested.pcap", direct.read_bytes())
    dataset = {
        "id": "fixture",
        "source_root": str(tmp_path),
    }

    result = audit_dataset(dataset)

    assert result["status"] == "ready"
    assert result["discovery_route"] == "direct_pcap"
    assert result["direct_pcap_count"] == 1
    assert result["archive_count"] == 1
    assert result["archive_pcap_member_count"] == 1
    assert result["eligible_capture_count"] == 2


def test_catalog_validator_accepts_explicit_v5_contract() -> None:
    validate_catalog(
        {
            "schema_version": "caeos_unified_multimodal_catalog_v5",
            "datasets": [
                {
                    "id": "demo",
                    "source_root": "/data/demo",
                    "include_globs": ["**/*.pcap"],
                }
            ],
        }
    )

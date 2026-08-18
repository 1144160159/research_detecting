from __future__ import annotations

import struct
from pathlib import Path

from scripts.repair_truncated_final_pcap_record import (
    inspect_truncated_final_record,
    repair_final_record,
    sha256_file,
    sha256_prefix,
    source_identity,
)
from scripts.validate_splitpcap_integrity import capture_fingerprint


def test_repair_preserves_truncated_final_packet_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source.pcap"
    repaired = tmp_path / "repaired.pcap"
    first = b"a" * 64
    final = b"b" * 444
    with source.open("wb") as handle:
        handle.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        handle.write(struct.pack("<IIII", 1, 1, len(first), len(first)))
        handle.write(first)
        handle.write(struct.pack("<IIII", 2, 2, 1516, 1516))
        handle.write(final)

    details = repair_final_record(source, repaired)

    assert inspect_truncated_final_record(source) == details
    assert inspect_truncated_final_record(repaired) is None
    assert details["declared_captured_length"] == 1516
    assert details["corrected_captured_length"] == 444
    assert repaired.stat().st_size == source.stat().st_size
    assert capture_fingerprint([source]) == capture_fingerprint([repaired])


def test_archive_member_identity_uses_container_for_catalog_match(tmp_path: Path) -> None:
    container = tmp_path / "captures.zip"
    member = tmp_path / "member.pcap"
    container.write_bytes(b"container")
    member.write_bytes(b"member")

    identity = source_identity(member, container, "capture-0818.pcap")

    assert identity["source_path"] == str(container)
    assert identity["source_member"] == "capture-0818.pcap"
    assert identity["original_size_bytes"] == len(b"container")
    assert identity["materialized_member_size_bytes"] == len(b"member")
    assert identity["original_sha256"] != identity["materialized_member_sha256"]


def test_archive_member_identity_requires_complete_locator(tmp_path: Path) -> None:
    source = tmp_path / "member.pcap"
    source.write_bytes(b"member")

    try:
        source_identity(source, tmp_path / "captures.zip", None)
    except ValueError as error:
        assert "must be supplied together" in str(error)
    else:
        raise AssertionError("incomplete archive locator was accepted")


def test_repair_drops_only_an_incomplete_final_record_header(tmp_path: Path) -> None:
    source = tmp_path / "partial-header.pcap"
    repaired = tmp_path / "partial-header.repaired.pcap"
    packet = b"a" * 64
    with source.open("wb") as handle:
        handle.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        handle.write(struct.pack("<IIII", 1, 1, len(packet), len(packet)))
        handle.write(packet)
        handle.write(b"partial")

    details = repair_final_record(source, repaired)

    assert details["repair_kind"] == "drop_incomplete_final_record_header"
    assert details["trailing_header_bytes_removed"] == len(b"partial")
    assert repaired.stat().st_size == source.stat().st_size - len(b"partial")
    assert sha256_prefix(source, repaired.stat().st_size) == sha256_file(repaired)
    assert capture_fingerprint([repaired])["packet_count"] == 1


def test_inspection_routes_impossible_packet_length_to_deep_recovery(
    tmp_path: Path,
) -> None:
    source = tmp_path / "corrupt-length.pcap"
    with source.open("wb") as handle:
        handle.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        handle.write(struct.pack("<IIII", 1, 1, 1_000_000, 1_000_000))
        handle.write(b"payload")

    details = inspect_truncated_final_record(source)

    assert details is not None
    assert details["repair_kind"] == "pcapfix_deep_scan_required"
    assert details["global_snaplen"] == 65535

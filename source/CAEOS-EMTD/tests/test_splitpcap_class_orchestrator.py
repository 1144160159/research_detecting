from __future__ import annotations

import csv
import zipfile
import sqlite3
import json

import pytest
from pathlib import Path
from unittest.mock import Mock

import prepare_caeos_unified_multimodal_csv_frozen_87f_tcp_ns as tcp_ns_preprocessor
import prepare_caeos_splitpcap_class_csv as orchestrator

from prepare_caeos_splitpcap_class_csv import (
    aggregate_label_exclusion,
    bounded_workers,
    capture_member_allowlist,
    dataset_pcap_repair_policy,
    add_final_merge_exclusion,
    doh_official_label_for_source,
    final_merge_conflict_exclusion_reason,
    inspect_archive_member_for_runtime_repair,
    load_bot_iot_strict_label_gate,
    load_doh_source_quality_gate,
    load_official_label_lookup,
    load_pcap_repairs,
    materialized_capture,
    migrate_capture_marker_registry_rollup,
    official_record_ids,
    select_capture_candidates,
    split_capture,
    verify_reusable_capture,
)
from caeos_label_alignment import label_index_registry_sha256
from caeos_unified_dataset import canonical_json_hash, sha256_file


def test_workers_are_bounded_by_memory_cpu_and_piece_count() -> None:
    assert bounded_workers(24, 100, 190, 46, 6, 2) == 12
    assert bounded_workers(24, 3, 190, 46, 6, 2) == 3
    assert bounded_workers(4, 100, 190, 46, 6, 2) == 4


def test_tcp_ns_flag_is_encoded_without_overflow() -> None:
    header = tcp_ns_preprocessor.canonical_l4_header(
        protocol=6,
        source_port=1234,
        destination_port=80,
        header_length=20,
        tcp_sequence=1,
        tcp_acknowledgement=2,
        flags=0x102,
        window=4096,
        udp_length=0,
        icmp_type=0,
        icmp_code=0,
    )

    assert len(header) == 20
    assert header[12] == 0x51
    assert header[13] == 0x02


def test_only_unsw_official_label_conflicts_are_excluded_at_merge() -> None:
    sources = "official.csv#10;official.csv#11"
    assert (
        final_merge_conflict_exclusion_reason(
            "unsw_nb15", "Pending", -1, "conflicting_label", sources
        )
        == "official_label_conflict"
    )
    assert (
        final_merge_conflict_exclusion_reason(
            "cicids2018", "Pending", -1, "conflicting_label", sources
        )
        is None
    )
    assert (
        final_merge_conflict_exclusion_reason(
            "unsw_nb15", "DoS", 1, "aligned_unique_flow", sources
        )
        is None
    )


def test_final_merge_exclusion_updates_all_denominators() -> None:
    summary = {
        "approved_reasons": ["five_tuple_absent"],
        "total_finalized_flows": 100,
        "excluded_flows": 10,
        "total_parsed_packets": 1000,
        "excluded_packets": 100,
        "total_parsed_packet_bytes": 10000,
        "excluded_packet_bytes": 1000,
        "excluded_flow_fraction": 0.1,
        "excluded_packet_fraction": 0.1,
        "excluded_packet_byte_fraction": 0.1,
        "reason_counts": {"five_tuple_absent": 10},
    }

    updated = add_final_merge_exclusion(
        summary, "official_label_conflict", 2, 30, 400, "a" * 64
    )

    assert updated["excluded_flow_fraction"] == 0.12
    assert updated["excluded_packet_fraction"] == 0.13
    assert updated["excluded_packet_byte_fraction"] == 0.14
    assert updated["reason_counts"]["official_label_conflict"] == 2
    assert updated["final_merge_conflict_exclusion"]["excluded_packets"] == 30


def test_final_merge_exclusion_supports_audited_dataset_rule() -> None:
    summary = {
        "approved_reasons": [],
        "total_finalized_flows": 10,
        "excluded_flows": 0,
        "total_parsed_packets": 50,
        "excluded_packets": 0,
        "total_parsed_packet_bytes": 5000,
        "excluded_packet_bytes": 0,
        "excluded_flow_fraction": 0.0,
        "excluded_packet_fraction": 0.0,
        "excluded_packet_byte_fraction": 0.0,
        "reason_counts": {},
    }

    updated = add_final_merge_exclusion(
        summary,
        "audited_unmatched",
        2,
        5,
        500,
        "b" * 64,
        metadata_key="final_merge_doh_source_quality_exclusion",
        rule="official audit gate",
        extra_evidence={"audit_sha256": "c" * 64},
    )

    evidence = updated["final_merge_doh_source_quality_exclusion"]
    assert evidence["rule"] == "official audit gate"
    assert evidence["audit_sha256"] == "c" * 64
    assert updated["excluded_flow_fraction"] == 0.2


def test_doh_source_quality_gate_verifies_frozen_evidence(tmp_path: Path) -> None:
    policy_sha256 = "d" * 64
    label_index_sha256 = "e" * 64
    audit = {
        "dataset_id": "dohbrw2020",
        "source_quality_adjusted_gate_passed": True,
        "all_sources_usable_or_quarantined": True,
        "all_unmatched_flows_have_approved_exclusion_reason": True,
        "approved_exclusion_reasons": [
            "five_tuple_absent_from_official_flow_labels",
            "five_tuple_present_but_time_not_overlapping",
            "protocol_outside_official_tcp_udp_flow_labels",
        ],
        "source_quality_unresolved": [],
        "source_quality_pending_allowlist_sources": [],
        "source_count": 3,
        "processed_source_count": 3,
        "label_index_sha256": label_index_sha256,
        "effective_coverage_fraction": 1.0,
        "raw_coverage_fraction": 0.5,
        "source_quality_policy_sha256": policy_sha256,
        "unmatched_flows": 7,
        "policy_excluded_unmatched_flows": 7,
        "policy_excluded_matched_flows": 1,
    }
    evidence_path = tmp_path / "summary.json"
    evidence_path.write_text(json.dumps(audit, sort_keys=True), encoding="utf-8")
    alignment = {
        "id": "dohbrw2020",
        "admission_gate_passed": True,
        "admission_gate_types": ["source_quality_adjusted_flow_label"],
        "sha256": label_index_sha256,
        "coverage_evidence": [
            {
                "gate_type": "source_quality_adjusted_flow_label",
                "admission_gate_passed": True,
                "path": str(evidence_path),
                "sha256": sha256_file(evidence_path),
                "source_quality_policy_sha256": policy_sha256,
            }
        ],
    }

    gate = load_doh_source_quality_gate(alignment)

    assert gate["processed_source_count"] == 3
    assert gate["audited_policy_excluded_unmatched_flows"] == 7
    assert gate["audit_sha256"] == sha256_file(evidence_path)

    audit["approved_exclusion_reasons"] = ["five_tuple_absent_from_official_flow_labels"]
    evidence_path.write_text(json.dumps(audit, sort_keys=True), encoding="utf-8")
    alignment["coverage_evidence"][0]["sha256"] = sha256_file(evidence_path)
    with pytest.raises(ValueError, match="reason set differs"):
        load_doh_source_quality_gate(alignment)


def test_bot_iot_strict_label_gate_verifies_full_pcap_evidence(
    tmp_path: Path,
) -> None:
    label_index_sha256 = "e" * 64
    reasons = [
        "five_tuple_absent_from_official_flow_labels",
        "five_tuple_present_but_time_not_overlapping",
        "protocol_outside_official_tcp_udp_flow_labels",
    ]
    audit = {
        "dataset_id": "cic_bot_iot",
        "formal_label_gate_passed": True,
        "all_pcaps_complete": True,
        "all_unmatched_flows_have_approved_exclusion_reason": True,
        "approved_exclusion_reasons": reasons,
        "pcap_file_count": 344,
        "processed_pcap_file_count": 344,
        "label_index_sha256": label_index_sha256,
        "effective_coverage_fraction": 1.0,
        "raw_coverage_fraction": 0.99,
        "matched_flows": 1000,
        "conflicting_flows": 0,
        "unmatched_flows": 10,
        "excluded_flows": 10,
        "counters": {
            "policy_exclusion_reason::five_tuple_absent_from_official_flow_labels": 4,
            "policy_exclusion_reason::five_tuple_present_but_time_not_overlapping": 6,
        },
    }
    evidence_path = tmp_path / "summary.json"
    evidence_path.write_text(json.dumps(audit, sort_keys=True), encoding="utf-8")
    alignment = {
        "id": "cic_bot_iot",
        "admission_gate_passed": True,
        "formal_gate_passed": True,
        "admission_gate_types": ["strict_flow_label"],
        "sha256": label_index_sha256,
        "coverage_evidence": [
            {
                "gate_type": "strict_flow_label",
                "admission_gate_passed": True,
                "formal_gate_passed": True,
                "path": str(evidence_path),
                "sha256": sha256_file(evidence_path),
            }
        ],
    }

    gate = load_bot_iot_strict_label_gate(alignment)

    assert gate["pcap_file_count"] == 344
    assert gate["audited_unmatched_flows"] == 10
    assert gate["audited_reason_counts"] == {
        "five_tuple_absent_from_official_flow_labels": 4,
        "five_tuple_present_but_time_not_overlapping": 6,
    }

    audit["all_pcaps_complete"] = False
    evidence_path.write_text(json.dumps(audit, sort_keys=True), encoding="utf-8")
    alignment["coverage_evidence"][0]["sha256"] = sha256_file(evidence_path)
    with pytest.raises(ValueError, match="does not cover all PCAP"):
        load_bot_iot_strict_label_gate(alignment)


def test_bot_iot_final_merge_remaps_official_conflict_and_audits_unmatched_drop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record_id = "a" * 64
    index = tmp_path / "labels.sqlite"
    connection = sqlite3.connect(index)
    try:
        connection.execute(
            "CREATE TABLE labels (record_id TEXT, fine_label TEXT, "
            "family_label TEXT, binary_label INTEGER)"
        )
        connection.execute(
            "INSERT INTO labels VALUES (?, ?, ?, ?)",
            (record_id, "DDoS-TCP", "DDoS", 1),
        )
        connection.commit()
    finally:
        connection.close()
    index_sha256 = sha256_file(index)
    audit = {
        "dataset_id": "cic_bot_iot",
        "formal_label_gate_passed": True,
        "all_pcaps_complete": True,
        "all_unmatched_flows_have_approved_exclusion_reason": True,
        "approved_exclusion_reasons": [
            "five_tuple_absent_from_official_flow_labels",
            "five_tuple_present_but_time_not_overlapping",
            "protocol_outside_official_tcp_udp_flow_labels",
        ],
        "pcap_file_count": 1,
        "processed_pcap_file_count": 1,
        "label_index_sha256": index_sha256,
        "effective_coverage_fraction": 1.0,
        "raw_coverage_fraction": 0.5,
        "matched_flows": 1,
        "conflicting_flows": 0,
        "unmatched_flows": 1,
        "excluded_flows": 1,
        "counters": {
            "policy_exclusion_reason::five_tuple_absent_from_official_flow_labels": 1
        },
    }
    evidence_path = tmp_path / "summary.json"
    evidence_path.write_text(json.dumps(audit, sort_keys=True), encoding="utf-8")
    alignment = {
        "id": "cic_bot_iot",
        "path": str(index),
        "sha256": index_sha256,
        "admission_gate_passed": True,
        "formal_gate_passed": True,
        "admission_gate_types": ["strict_flow_label"],
        "coverage_evidence": [
            {
                "gate_type": "strict_flow_label",
                "admission_gate_passed": True,
                "formal_gate_passed": True,
                "path": str(evidence_path),
                "sha256": sha256_file(evidence_path),
            }
        ],
    }
    columns = [
        "attack_category",
        "dataset_native_label",
        "traffic_class",
        "attack_subcategory",
        "fine_label",
        "family_label",
        "binary_label",
        "label_status",
        "label_source",
        "packet_count_total",
        "packet_bytes_total",
    ]
    part = tmp_path / "capture.part"
    with part.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "-1",
                "conflicting_path_and_external_label",
                f"official.csv#10#{record_id}",
                "3",
                "300",
            ]
        )
        writer.writerow(
            [
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "Pending",
                "-1",
                "unmatched_label",
                "official_unmatched",
                "2",
                "200",
            ]
        )
    marker = {
        "capture_id": "capture-1",
        "parts": [{"part_path": str(part)}],
        "label_exclusion_summary": {
            "approved_reasons": [],
            "total_finalized_flows": 2,
            "excluded_flows": 0,
            "total_parsed_packets": 5,
            "excluded_packets": 0,
            "total_parsed_packet_bytes": 500,
            "excluded_packet_bytes": 0,
            "reason_counts": {},
        },
    }
    monkeypatch.setattr(
        orchestrator,
        "verify_csv_and_sha256_parallel",
        lambda path, expected_columns, expected_rows, require_formal_labels,
        workers, batch_rows: (
            {
                "full_row_validation": True,
                "rows": expected_rows,
            },
            sha256_file(path),
        ),
    )

    manifest = orchestrator.merge_class_csvs(
        {"id": "cic_bot_iot", "role": "test"},
        [marker],
        tmp_path / "output",
        columns,
        "b" * 64,
        "c" * 64,
        {"label_alignment": {"maximum_excluded_packet_fraction": 1.0}},
        {"test": True},
        alignment,
    )

    assert manifest["row_count"] == 1
    assert manifest["official_label_precedence_summary"]["remapped_flows"] == 1
    exclusion = manifest["label_exclusion_summary"]
    assert exclusion["excluded_flows"] == 1
    assert exclusion["excluded_packet_fraction"] == 0.4
    assert exclusion["final_merge_bot_iot_strict_label_exclusion"][
        "audited_reason_counts"
    ] == {"five_tuple_absent_from_official_flow_labels": 1}
    output = next((tmp_path / "output" / "cic_bot_iot").glob("*.csv"))
    with output.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["label_status"] == "aligned_unique_flow_official_precedence"
    assert row["attack_category"] == "DDoS"
    assert row["binary_label"] == "1"


def test_doh_official_label_lookup_uses_record_ids_from_label_source(
    tmp_path: Path,
) -> None:
    index = tmp_path / "labels.sqlite"
    record_id = "f" * 64
    connection = sqlite3.connect(index)
    try:
        connection.execute(
            "CREATE TABLE labels (record_id TEXT, fine_label TEXT, "
            "family_label TEXT, binary_label INTEGER)"
        )
        connection.execute(
            "INSERT INTO labels VALUES (?, ?, ?, ?)",
            (record_id, "NonDoH", "Benign", 0),
        )
        connection.commit()
    finally:
        connection.close()

    source = f"/official/l1-nondoh.csv#777672#{record_id}"
    lookup = load_official_label_lookup(index)

    assert official_record_ids(source) == (record_id,)
    assert doh_official_label_for_source(source, lookup) == (
        "NonDoH",
        "Benign",
        0,
        (record_id,),
    )


def test_split_integrity_mismatch_falls_back_to_editcap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.pcap"
    source.write_bytes(b"source")
    split_root = tmp_path / "pieces"
    splitpcap = tmp_path / "splitpcap"
    editcap = tmp_path / "editcap"
    splitpcap.write_bytes(b"binary")
    editcap.write_bytes(b"binary")
    validation_calls = 0

    def fake_run(command: list[str], **_: object) -> Mock:
        if command[0] == str(splitpcap):
            (split_root / "bad.pcap").write_bytes(b"bad-packet" * 4)
            return Mock(returncode=0, stdout="", stderr="")
        if command[0] == "/usr/bin/capinfos":
            return Mock(returncode=0, stdout="Number of packets: 2\n", stderr="")
        if command[0] == str(editcap):
            (split_root / "piece_00000.pcapng").write_bytes(b"good-packet-1" * 4)
            (split_root / "piece_00001.pcapng").write_bytes(b"good-packet-2" * 4)
            return Mock(returncode=0, stdout="", stderr="")
        raise AssertionError(command)

    def fake_validate(_: Path, pieces: list[Path]) -> dict[str, object]:
        nonlocal validation_calls
        validation_calls += 1
        if validation_calls == 1:
            raise ValueError("splitpcap packet integrity mismatch: evidence")
        assert [path.name for path in pieces] == [
            "piece_00000.pcapng",
            "piece_00001.pcapng",
        ]
        return {"exact_multiset_match": True, "piece_count": 2}

    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.subprocess.run", fake_run
    )
    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.validate_split", fake_validate
    )

    pieces, integrity = split_capture(
        splitpcap, editcap, source, split_root, target_piece_bytes=4, maximum_pieces=4
    )

    assert len(pieces) == 2
    assert integrity["exact_multiset_match"] is True
    assert (
        integrity["split_tool"]
        == "editcap_packet_count_after_splitpcap_integrity_mismatch"
    )


def test_split_capture_honors_minimum_piece_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "small.pcap"
    source.write_bytes(b"source-capture" * 4)
    split_root = tmp_path / "pieces"
    splitpcap = tmp_path / "splitpcap"
    editcap = tmp_path / "editcap"

    def fake_run(command: list[str], **_: object) -> Mock:
        assert command[-1] == "12"
        for index in range(12):
            (split_root / f"{index}.pcap").write_bytes(b"piece-payload" * 4)
        return Mock(returncode=0, stdout="", stderr="")

    def fake_validate(_: Path, pieces: list[Path]) -> dict[str, object]:
        assert len(pieces) == 12
        return {"exact_multiset_match": True, "piece_count": 12}

    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.subprocess.run", fake_run
    )
    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.validate_split", fake_validate
    )

    pieces, integrity = split_capture(
        splitpcap,
        editcap,
        source,
        split_root,
        target_piece_bytes=1024,
        maximum_pieces=256,
        minimum_pieces=12,
    )

    assert len(pieces) == 12
    assert integrity["minimum_pieces"] == 12
    assert integrity["requested_piece_count"] == 12


def test_cicids2018_nonfinal_corruption_routes_to_deep_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "corrupt.pcap"
    source.write_bytes(b"corrupt")

    def fail_inspection(_: Path) -> None:
        raise ValueError("PCAP truncation is not a recoverable final record")

    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.inspect_truncated_final_record",
        fail_inspection,
    )

    result = inspect_archive_member_for_runtime_repair("cicids2018", source)

    assert result == {
        "repair_kind": "pcapfix_deep_scan_required",
        "inspection_error": "PCAP truncation is not a recoverable final record",
    }


def test_non_cicids2018_nonfinal_corruption_remains_fatal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "corrupt.pcap"
    source.write_bytes(b"corrupt")

    def fail_inspection(_: Path) -> None:
        raise ValueError("PCAP truncation is not a recoverable final record")

    monkeypatch.setattr(
        "prepare_caeos_splitpcap_class_csv.inspect_truncated_final_record",
        fail_inspection,
    )

    with pytest.raises(ValueError, match="not a recoverable final record"):
        inspect_archive_member_for_runtime_repair("cicids2017", source)


def test_archive_member_is_materialized_one_at_a_time_and_deleted(tmp_path: Path) -> None:
    archive_path = tmp_path / "captures.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("nested/capture-without-extension", b"\xd4\xc3\xb2\xa1payload")
    staging = tmp_path / "staging"
    source = {"path": str(archive_path)}
    with materialized_capture(source, "nested/capture-without-extension", staging, "abc") as path:
        assert path.read_bytes() == b"\xd4\xc3\xb2\xa1payload"
        assert len(list(staging.iterdir())) == 1
    assert list(staging.iterdir()) == []


def test_label_exclusion_aggregation_records_all_denominators() -> None:
    summary = aggregate_label_exclusion(
        [
            {
                "label_exclusion_summary": {
                    "approved_reasons": ["five_tuple_absent"],
                    "total_finalized_flows": 100,
                    "excluded_flows": 2,
                    "total_parsed_packets": 1000,
                    "excluded_packets": 10,
                    "total_parsed_packet_bytes": 100_000,
                    "excluded_packet_bytes": 500,
                    "reason_counts": {"five_tuple_absent": 2},
                }
            },
            {
                "label_exclusion_summary": {
                    "approved_reasons": ["outside_protocol"],
                    "total_finalized_flows": 50,
                    "excluded_flows": 3,
                    "total_parsed_packets": 500,
                    "excluded_packets": 15,
                    "total_parsed_packet_bytes": 50_000,
                    "excluded_packet_bytes": 1000,
                    "reason_counts": {"outside_protocol": 3},
                }
            },
        ]
    )
    assert summary["excluded_flow_fraction"] == 5 / 150
    assert summary["excluded_packet_fraction"] == 25 / 1500
    assert summary["excluded_packet_byte_fraction"] == 1500 / 150_000
    assert summary["reason_counts"] == {
        "five_tuple_absent": 2,
        "outside_protocol": 3,
    }


def test_capture_member_allowlist_reads_frozen_inventory(tmp_path: Path) -> None:
    index = tmp_path / "labels.sqlite"
    connection = sqlite3.connect(index)
    try:
        connection.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
        connection.execute(
            "CREATE TABLE labels (source_member TEXT, endpoint_a BLOB)"
        )
        connection.execute(
            "INSERT INTO metadata VALUES ('dataset_id', 'ciciot2022')"
        )
        connection.executemany(
            "INSERT INTO labels VALUES (?, NULL)",
            [("5-Active/a.pcap",), ("6-Attacks/b.pcap",)],
        )
        connection.commit()
    finally:
        connection.close()
    alignment = {
        "path": str(index),
        "record_count": 2,
        "admission_gate_types": ["full_capture_member_inventory"],
    }
    assert capture_member_allowlist(alignment, "ciciot2022") == {
        "5-Active/a.pcap",
        "6-Attacks/b.pcap",
    }


def test_label_index_registry_sha_comes_from_frozen_sqlite(tmp_path: Path) -> None:
    index = tmp_path / "labels.sqlite"
    registry_sha256 = "ab" * 32
    connection = sqlite3.connect(index)
    try:
        connection.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
        connection.executemany(
            "INSERT INTO metadata VALUES (?, ?)",
            [
                ("schema_version", "caeos_label_alignment_sqlite_v1"),
                ("dataset_id", "cicddos2019"),
                ("registry_sha256", registry_sha256),
            ],
        )
        connection.commit()
    finally:
        connection.close()
    assert label_index_registry_sha256(index, "cicddos2019") == registry_sha256


def test_registry_rollup_only_marker_migration_preserves_part(tmp_path: Path) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"unchanged-feature-rows")
    schema_sha256 = "schema-v4"
    previous_policy = {
        "preprocessor_code_sha256": "code-v1",
        "label_alignment": {
            "path": "/labels.sqlite",
            "sha256": "labels-v1",
            "record_count": 123,
            "registry_sha256": "old-rollup",
        },
    }
    expected_policy = json.loads(json.dumps(previous_policy))
    expected_policy["label_alignment"]["registry_sha256"] = "new-rollup"
    marker = {
        "complete": True,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": schema_sha256,
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
                "label_alignment": dict(previous_policy["label_alignment"]),
            }
        ],
    }
    marker_path = tmp_path / "marker.json"
    migrated = migrate_capture_marker_registry_rollup(
        marker_path, marker, schema_sha256, expected_policy
    )
    assert part_path.read_bytes() == b"unchanged-feature-rows"
    assert migrated["parts"][0]["processing_policy"] == expected_policy
    assert migrated["parts"][0]["processing_policy_sha256"] == canonical_json_hash(
        expected_policy
    )
    assert migrated["policy_migrations"][0]["part_content_sha256_unchanged"]


def test_registry_rollup_migration_rejects_other_policy_changes(tmp_path: Path) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"rows")
    previous_policy = {
        "maximum_packets_per_segment": 64,
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "old-rollup",
        },
    }
    expected_policy = {
        "maximum_packets_per_segment": 32,
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "new-rollup",
        },
    }
    marker = {
        "complete": True,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }
    with pytest.raises(ValueError, match="stale capture marker processing policy"):
        migrate_capture_marker_registry_rollup(
            tmp_path / "marker.json",
            marker,
            "schema-v4",
            expected_policy,
        )


def test_completed_capture_can_migrate_tcp_ns_flag_fix(tmp_path: Path) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"unchanged-feature-rows")
    previous_policy = {
        "preprocessor_code_sha256": (
            "87f3701cf7f161e358e2d981e9667762140f4b9f3c95892a8b62a6f1d62e9306"
        ),
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "registry-v1",
        },
    }
    expected_policy = json.loads(json.dumps(previous_policy))
    expected_policy["preprocessor_code_sha256"] = (
        "b4c010c78fa768d16b348703216802dbaadfe042e9ccf459b1767d228018e9b9"
    )
    marker = {
        "complete": True,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }

    migrated = migrate_capture_marker_registry_rollup(
        tmp_path / "marker.json",
        marker,
        "schema-v4",
        expected_policy,
    )

    evidence = migrated["policy_migrations"][0]
    assert part_path.read_bytes() == b"unchanged-feature-rows"
    assert evidence["reason"] == "completed_capture_tcp_ns_flag_compatibility_fix"
    assert evidence["changed_paths"] == ["preprocessor_code_sha256"]
    assert evidence["part_content_sha256_unchanged"] is True
    assert "byte-identical" in evidence["compatibility_proof"]


def test_split_target_migration_preserves_completed_parts(tmp_path: Path) -> None:
    part_path = tmp_path / "part.csv"
    part_path.write_bytes(b"unchanged-feature-rows")
    previous_policy = {
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "registry-v1",
        },
        "splitpcap": {
            "commit": "splitpcap-v1",
            "binary_sha256": "binary-v1",
            "target_piece_bytes": 128 * 1024 * 1024,
            "exact_packet_multiset_validation": True,
        },
    }
    expected_policy = json.loads(json.dumps(previous_policy))
    expected_policy["splitpcap"]["target_piece_bytes"] = 64 * 1024 * 1024
    marker = {
        "complete": True,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }

    migrated = migrate_capture_marker_registry_rollup(
        tmp_path / "marker.json",
        marker,
        "schema-v4",
        expected_policy,
    )

    assert part_path.read_bytes() == b"unchanged-feature-rows"
    assert migrated["parts"][0]["processing_policy"] == expected_policy
    assert migrated["policy_migrations"][0]["changed_paths"] == [
        "splitpcap.target_piece_bytes"
    ]
    assert migrated["policy_migrations"][0]["part_content_sha256_unchanged"] is True


def test_unaffected_capture_can_migrate_dataset_repair_rollup(tmp_path: Path) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"rows")
    previous_policy = {
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "registry-v1",
        },
        "pcap_repair_set": {"repair_count": 0, "repairs_sha256": "empty"},
    }
    expected_policy = json.loads(json.dumps(previous_policy))
    expected_policy["pcap_repair_set"] = {
        "repair_count": 1,
        "repairs_sha256": "one-repair",
    }
    marker = {
        "complete": True,
        "pcap_repair": None,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }
    migrated = migrate_capture_marker_registry_rollup(
        tmp_path / "marker.json",
        marker,
        "schema-v4",
        expected_policy,
        current_repair=None,
    )
    assert migrated["policy_migrations"][0]["changed_paths"] == [
        "pcap_repair_set.repair_count",
        "pcap_repair_set.repairs_sha256",
    ]


def test_unrepaired_capture_can_migrate_legacy_global_repair_identity(
    tmp_path: Path,
) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"unchanged-feature-rows")
    previous_policy = {
        "preprocessor_code_sha256": "frozen-code",
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "old-rollup",
        },
        "pcap_repair_manifest_sha256": "legacy-global-manifest",
    }
    expected_policy = {
        "preprocessor_code_sha256": "frozen-code",
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "new-rollup",
        },
        "pcap_repair_set": {
            "schema_version": "caeos_dataset_pcap_repair_set_v1",
            "dataset_id": "cic_bot_iot",
            "repair_count": 0,
            "repairs_sha256": "empty",
        },
    }
    marker = {
        "complete": True,
        "pcap_repair": None,
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }

    migrated = migrate_capture_marker_registry_rollup(
        tmp_path / "marker.json",
        marker,
        "schema-v4",
        expected_policy,
        current_repair=None,
    )

    assert part_path.read_bytes() == b"unchanged-feature-rows"
    assert migrated["policy_migrations"][0]["changed_paths"] == [
        "label_alignment.registry_sha256",
        "pcap_repair_manifest_sha256",
        "pcap_repair_set",
    ]
    assert migrated["policy_migrations"][0]["part_content_sha256_unchanged"] is True


def test_legacy_repair_identity_migration_rejects_repaired_capture(
    tmp_path: Path,
) -> None:
    part_path = tmp_path / "piece.part"
    part_path.write_bytes(b"rows")
    previous_policy = {
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "registry-v1",
        },
        "pcap_repair_manifest_sha256": "legacy-global-manifest",
    }
    expected_policy = {
        "label_alignment": {
            "sha256": "labels-v1",
            "registry_sha256": "registry-v1",
        },
        "pcap_repair_set": {"repair_count": 1, "repairs_sha256": "repair"},
    }
    marker = {
        "complete": True,
        "pcap_repair": {"repair_tool": "pcapfix"},
        "parts": [
            {
                "part_path": str(part_path),
                "part_sha256": sha256_file(part_path),
                "schema_sha256": "schema-v4",
                "processing_policy": previous_policy,
                "processing_policy_sha256": canonical_json_hash(previous_policy),
            }
        ],
    }

    with pytest.raises(ValueError, match="stale capture marker processing policy"):
        migrate_capture_marker_registry_rollup(
            tmp_path / "marker.json",
            marker,
            "schema-v4",
            expected_policy,
            current_repair={"repair_tool": "pcapfix"},
        )


def test_capture_selection_records_outside_inventory_exclusion(tmp_path: Path) -> None:
    active = tmp_path / "5-Active" / "a.pcap"
    active.parent.mkdir()
    active.write_bytes(b"a" * 7)
    archive = tmp_path / "captures.tar.gz"
    dataset = {"source_root": str(tmp_path)}
    source_dataset = {
        "source_files": [
            {"path": str(active), "size_bytes": 7},
            {
                "path": str(archive),
                "capture_members": [
                    {"name": "6-Attacks/b.pcap", "size_bytes": 11},
                    {"name": "CSV files/extra.pcap", "size_bytes": 13},
                ],
            },
        ]
    }
    selected, scope = select_capture_candidates(
        dataset,
        source_dataset,
        {"5-Active/a.pcap", "6-Attacks/b.pcap"},
    )
    assert [(member or Path(source["path"]).name) for source, member in selected] == [
        "a.pcap",
        "6-Attacks/b.pcap",
    ]
    assert scope["candidate_capture_count"] == 3
    assert scope["scheduled_capture_count"] == 2
    assert scope["excluded_capture_count"] == 1
    assert scope["excluded_capture_bytes"] == 13
    assert scope["excluded_capture_fraction"] == 1 / 3
    assert scope["excluded_reason_counts"] == {
        "outside_frozen_capture_member_label_inventory": 1
    }


def test_capture_selection_excludes_direct_non_capture_source(tmp_path: Path) -> None:
    capture = tmp_path / "capture.pcap"
    labels = tmp_path / "labels.zip"
    capture.write_bytes(b"capture")
    labels.write_bytes(b"labels")
    dataset = {"source_root": str(tmp_path)}
    source_dataset = {
        "source_files": [
            {"path": str(capture), "size_bytes": 7},
            {"path": str(labels), "size_bytes": 6},
        ]
    }

    selected, scope = select_capture_candidates(dataset, source_dataset, None)

    assert [(Path(source["path"]).name, member) for source, member in selected] == [
        ("capture.pcap", None)
    ]
    assert scope["scheduled_capture_count"] == 1
    assert scope["excluded_reason_counts"] == {"non_capture_source_file": 1}


def test_capture_selection_records_member_removed_by_zip_repair(tmp_path: Path) -> None:
    archive_path = tmp_path / "captures.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("valid.pcap", b"capture")
    source_dataset = {
        "source_files": [
            {
                "path": str(archive_path),
                "size_bytes": archive_path.stat().st_size + 270,
                "capture_members": [
                    {"name": "missing-zero-byte.pcap", "size_bytes": 0},
                    {"name": "valid.pcap", "size_bytes": 7},
                ],
            }
        ]
    }

    selected, scope = select_capture_candidates(
        {"source_root": str(tmp_path)}, source_dataset, None
    )

    assert [member for _, member in selected] == ["valid.pcap"]
    assert scope["candidate_capture_count"] == 2
    assert scope["scheduled_capture_count"] == 1
    assert scope["excluded_capture_count"] == 1
    assert scope["excluded_capture_bytes"] == 0
    assert scope["excluded_reason_counts"] == {
        "archive_member_missing_from_current_source": 1
    }
    assert scope["excluded_sources"][0]["rule"] == (
        "exclude_manifest_member_absent_from_current_zip_inventory"
    )
    assert scope["excluded_sources"][0]["current_source_size_bytes"] == (
        archive_path.stat().st_size
    )


def test_pcap_repair_manifest_and_capture_marker_are_identity_bound(
    tmp_path: Path,
) -> None:
    repaired = tmp_path / "repaired.pcap"
    repaired.write_bytes(b"pcap")
    manifest = tmp_path / "repairs.json"
    manifest.write_text(
        json.dumps(
            {
                "repairs": [
                    {
                        "dataset_id": "edge_iiotset",
                        "source_path": "/data/corrupt.pcap",
                        "source_member": None,
                        "original_sha256": "a" * 64,
                        "repaired_path": str(repaired),
                        "repaired_sha256": sha256_file(repaired),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    repairs, manifest_sha256 = load_pcap_repairs(manifest)
    assert len(repairs) == 1
    assert manifest_sha256 == sha256_file(manifest)

    part = tmp_path / "part.csv"
    part.write_text("row\n", encoding="utf-8")
    marker = {
        "complete": True,
        "parts": [
            {
                "part_path": str(part),
                "part_sha256": sha256_file(part),
                "schema_sha256": "schema-v4",
                "processing_policy_sha256": "policy-v4",
            }
        ],
    }
    verify_reusable_capture(marker, "schema-v4", "policy-v4")
    with pytest.raises(ValueError, match="stale capture marker schema"):
        verify_reusable_capture(marker, "schema-v3", "policy-v4")


def test_pcap_repair_policy_is_scoped_to_dataset() -> None:
    target_entry = {
        "dataset_id": "cic_ton_iot",
        "source_path": "/data/ton.pcap",
        "source_member": None,
        "original_sha256": "a" * 64,
        "repaired_sha256": "b" * 64,
    }
    unrelated_entry = {
        "dataset_id": "edge_iiotset",
        "source_path": "/data/edge.pcap",
        "source_member": None,
        "original_sha256": "c" * 64,
        "repaired_sha256": "d" * 64,
    }
    target_only = {"ton": target_entry}
    with_unrelated = {"ton": target_entry, "edge": unrelated_entry}

    target_policy, target_repairs = dataset_pcap_repair_policy(
        target_only, "cic_ton_iot"
    )
    unchanged_policy, unchanged_repairs = dataset_pcap_repair_policy(
        with_unrelated, "cic_ton_iot"
    )

    assert unchanged_policy == target_policy
    assert unchanged_repairs == target_repairs
    assert target_policy["repair_count"] == 1
    empty_policy, empty_repairs = dataset_pcap_repair_policy(
        with_unrelated, "ciciot2022"
    )
    assert empty_policy["repair_count"] == 0
    assert empty_repairs == {}

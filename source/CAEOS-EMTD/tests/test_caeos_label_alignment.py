from __future__ import annotations

from pathlib import Path

import pytest

import caeos_label_alignment
from caeos_label_alignment import LabelResolver, create_label_index, packed_ip


def record(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "record_id": "row-1",
        "source_member": "capture.pcap",
        "src_ip": "10.0.0.1",
        "src_port": 1234,
        "dst_ip": "10.0.0.2",
        "dst_port": 443,
        "protocol": 6,
        "start_ns": 1_000,
        "end_ns": 2_000,
        "fine_label": "Web_Attack_XSS",
        "family_label": "Web_Attack",
        "binary_label": 1,
        "label_source": "labels.csv:2",
    }
    value.update(overrides)
    return value


def resolver(
    tmp_path: Path,
    records: list[dict[str, object]],
    conflict_policy: str = "reject",
    time_nonoverlap_policy: str = "reject",
) -> LabelResolver:
    metadata = create_label_index(
        tmp_path / "labels.sqlite", "fixture", records, "registry-sha"
    )
    return LabelResolver(
        Path(metadata["path"]),
        "fixture",
        str(metadata["sha256"]),
        tolerance_ns=50,
        conflict_policy=conflict_policy,
        time_nonoverlap_policy=time_nonoverlap_policy,
    )


def test_bidirectional_flow_and_time_overlap_resolve_uniquely(tmp_path: Path) -> None:
    index = resolver(tmp_path, [record()])
    try:
        assert index.sqlite_mmap_size >= 0
        assert index.sqlite_cache_kib == 512 * 1024
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.2"),
            443,
            packed_ip("10.0.0.1"),
            1234,
            6,
            1_950,
            2_050,
        )
    finally:
        index.close()
    assert result.status == "aligned_unique_flow"
    assert result.binary_label == 1
    assert result.record_ids == ("row-1",)
    assert "labels.csv:2#row-1" == result.label_source


def test_unmatched_flow_is_not_silently_path_labeled(tmp_path: Path) -> None:
    index = resolver(tmp_path, [record()])
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.9"),
            9,
            packed_ip("10.0.0.8"),
            8,
            17,
            1_000,
            2_000,
        )
    finally:
        index.close()
    assert result.status == "unmatched_label"
    assert result.binary_label == -1


def test_conflicting_external_rows_are_rejected(tmp_path: Path) -> None:
    index = resolver(
        tmp_path,
        [
            record(),
            record(
                record_id="row-2",
                fine_label="Benign",
                family_label="Benign",
                binary_label=0,
                label_source="labels.csv:3",
            ),
        ],
    )
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
        diagnosis = index.diagnose_conflict(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert result.status == "conflicting_label"
    assert result.binary_label == -1
    assert result.record_ids == ("row-1", "row-2")
    assert diagnosis["candidate_record_count"] == 2
    assert diagnosis["candidate_label_counts"] == {
        "Benign::Benign::binary=0": 1,
        "Web_Attack::Web_Attack_XSS::binary=1": 1,
    }


def test_conflict_diagnosis_includes_dataset_scope_rows(tmp_path: Path) -> None:
    index = resolver(
        tmp_path,
        [
            record(source_member=None),
            record(
                record_id="row-2",
                source_member=None,
                fine_label="Benign",
                family_label="Benign",
                binary_label=0,
                label_source="labels.csv:3",
            ),
        ],
    )
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
        diagnosis = index.diagnose_conflict(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert result.status == "conflicting_label"
    assert diagnosis["candidate_record_count"] == 2
    assert diagnosis["candidate_label_counts"] == {
        "Benign::Benign::binary=0": 1,
        "Web_Attack::Web_Attack_XSS::binary=1": 1,
    }


def test_conflict_can_split_packets_at_official_label_boundaries(
    tmp_path: Path,
) -> None:
    index = resolver(
        tmp_path,
        [
            record(end_ns=1_499, fine_label="MSSQL", family_label="DDoS"),
            record(
                record_id="row-2",
                start_ns=1_500,
                end_ns=2_000,
                fine_label="UDP Flood",
                family_label="DDoS",
                label_source="labels.csv:3",
            ),
        ],
    )
    try:
        split = index.split_packet_observations_by_official_labels(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            [(1_100, 100), (1_400, 110), (1_600, 120), (1_900, 130)],
        )
    finally:
        index.close()
    assert split["resolved"] is True
    assert [segment["fine_label"] for segment in split["segments"]] == [
        "MSSQL",
        "UDP Flood",
    ]
    assert [segment["packet_count"] for segment in split["segments"]] == [2, 2]
    assert sum(segment["packet_bytes"] for segment in split["segments"]) == 460


def test_flow_label_has_priority_over_capture_label(tmp_path: Path) -> None:
    index = resolver(
        tmp_path,
        [
            record(),
            record(
                record_id="capture-label",
                src_ip=None,
                fine_label="Benign",
                family_label="Benign",
                binary_label=0,
                start_ns=None,
                end_ns=None,
                label_source="capture.log:1",
            ),
        ],
    )
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert result.status == "aligned_unique_flow"
    assert result.binary_label == 1


def test_explicit_bidirectional_policy_selects_single_malicious_label(
    tmp_path: Path,
) -> None:
    index = resolver(
        tmp_path,
        [
            record(
                fine_label="FTP-Patator",
                family_label="BruteForce",
                binary_label=1,
            ),
            record(
                record_id="reverse-benign",
                fine_label="Benign",
                family_label="Benign",
                binary_label=0,
            ),
        ],
        conflict_policy="malicious_over_benign_bidirectional",
    )
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert result.status == "aligned_unique_flow_malicious_over_benign"
    assert result.fine_label == "FTP-Patator"
    assert result.family_label == "BruteForce"
    assert result.binary_label == 1


def test_label_index_sha256_is_mandatory(tmp_path: Path) -> None:
    metadata = create_label_index(
        tmp_path / "labels.sqlite", "fixture", [record()], "registry-sha"
    )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        LabelResolver(Path(metadata["path"]), "fixture", "0" * 64)


def test_publication_accepts_verified_target_after_fsync_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_fsync = caeos_label_alignment.os.fsync
    attempts = 0

    def flaky_fsync(file_descriptor: int) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError(5, "synthetic transient I/O error")
        real_fsync(file_descriptor)

    monkeypatch.setattr(caeos_label_alignment.os, "fsync", flaky_fsync)
    metadata = create_label_index(
        tmp_path / "labels.sqlite", "fixture", [record()], "registry-sha"
    )
    assert metadata["publication_attempts"] == 1
    assert metadata["publication_verified_by_target_reread"] is True
    assert metadata["publication_fsync_confirmed"] is False
    assert metadata["publication_integrity_basis"] == (
        "target_reread_sha256_after_fsync_error"
    )
    assert metadata["publication_fsync_errors"]
    assert Path(metadata["path"]).is_file()


def test_explicit_nearest_official_policy_resolves_time_nonoverlap(
    tmp_path: Path,
) -> None:
    index = resolver(
        tmp_path,
        [record()],
        time_nonoverlap_policy="nearest_official_same_tuple",
    )
    try:
        result = index.resolve(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            9_000,
            10_000,
        )
    finally:
        index.close()
    assert result.status == "aligned_unique_flow_nearest_official_time_nonoverlap"
    assert result.fine_label == "Web_Attack_XSS"
    assert result.binary_label == 1
    assert "nearest_gap_ns=7000" in result.label_source


def test_unmatched_diagnosis_distinguishes_time_scope_tuple_and_protocol(
    tmp_path: Path,
) -> None:
    index = resolver(
        tmp_path,
        [
            record(),
            record(
                record_id="row-udp",
                src_ip="10.0.0.3",
                src_port=53,
                dst_ip="10.0.0.4",
                dst_port=5353,
                protocol=17,
            ),
        ],
    )
    try:
        time_gap = index.diagnose_unmatched(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            9_000,
            10_000,
        )
        other_scope = index.diagnose_unmatched(
            "other.pcap",
            packed_ip("10.0.0.1"),
            1234,
            packed_ip("10.0.0.2"),
            443,
            6,
            1_100,
            1_900,
        )
        absent = index.diagnose_unmatched(
            "capture.pcap",
            packed_ip("10.0.0.9"),
            9,
            packed_ip("10.0.0.8"),
            8,
            17,
            1_100,
            1_900,
        )
        protocol = index.diagnose_unmatched(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            0,
            packed_ip("10.0.0.2"),
            0,
            1,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert time_gap["reason"] == "five_tuple_present_but_time_not_overlapping"
    assert time_gap["nearest_gap_ns"] == 7_000
    assert other_scope["reason"] == "five_tuple_present_only_in_other_capture_scope"
    assert absent["reason"] == "five_tuple_absent_from_official_flow_labels"
    assert protocol["reason"] == "protocol_outside_official_tcp_udp_flow_labels"
    assert protocol["official_protocols"] == [6, 17]


def test_unmatched_diagnosis_uses_protocols_present_in_official_index(
    tmp_path: Path,
) -> None:
    index = resolver(
        tmp_path,
        [
            record(
                src_port=3,
                dst_port=3,
                protocol=1,
                fine_label="Ransomware",
                family_label="Malware",
            )
        ],
    )
    try:
        time_gap = index.diagnose_unmatched(
            "capture.pcap",
            packed_ip("10.0.0.1"),
            3,
            packed_ip("10.0.0.2"),
            3,
            1,
            9_000,
            10_000,
        )
        absent = index.diagnose_unmatched(
            "capture.pcap",
            packed_ip("10.0.0.9"),
            3,
            packed_ip("10.0.0.8"),
            3,
            1,
            1_100,
            1_900,
        )
    finally:
        index.close()
    assert time_gap["reason"] == "five_tuple_present_but_time_not_overlapping"
    assert absent["reason"] == "five_tuple_absent_from_official_flow_labels"

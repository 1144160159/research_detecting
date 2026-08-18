import argparse
import json
from pathlib import Path

import dpkt

import audit_caeos_label_alignment_coverage as target


def test_truncated_pcap_tail_is_audited_instead_of_aborting_dataset(
    tmp_path: Path, monkeypatch
) -> None:
    pcap = tmp_path / "truncated.pcap"
    pcap.write_bytes(b"not-used-by-mocked-reader")
    output = tmp_path / "audit.json"

    def broken_reader(_handle):
        if False:
            yield 0.0, b""
        raise dpkt.dpkt.NeedData("got 5, 16 needed at least")

    monkeypatch.setattr(target, "packet_reader", broken_reader)
    args = argparse.Namespace(
        dataset_id="example",
        pcap=pcap,
        source_member="truncated.pcap",
        label_index=tmp_path / "labels.sqlite",
        label_index_sha256="index-sha",
        output=output,
        maximum_packets=2**63 - 1,
        idle_seconds=30.0,
        tolerance_ns=1_000_000,
        maximum_unmatched_samples=10,
        conflict_policy="reject",
        drop_unmatched_reason=[],
        time_nonoverlap_policy="reject",
        official_boundary_split=False,
    )

    report = target.audit(args, resolver=object())

    assert report["complete_pcap_read"] is False
    assert report["capture_read_error"]["exception_type"] == "NeedData"
    assert report["counters"]["capture_read_errors"] == 1
    assert json.loads(output.read_text(encoding="utf-8")) == report


def test_empty_capture_is_audited_instead_of_aborting_dataset(
    tmp_path: Path,
) -> None:
    pcap = tmp_path / "empty.pcap"
    pcap.write_bytes(b"")
    output = tmp_path / "audit.json"
    args = argparse.Namespace(
        dataset_id="example",
        pcap=pcap,
        source_member="empty.pcap",
        label_index=tmp_path / "labels.sqlite",
        label_index_sha256="index-sha",
        output=output,
        maximum_packets=2**63 - 1,
        idle_seconds=30.0,
        tolerance_ns=1_000_000,
        maximum_unmatched_samples=10,
        conflict_policy="reject",
        drop_unmatched_reason=[],
        time_nonoverlap_policy="reject",
        official_boundary_split=False,
    )

    report = target.audit(args, resolver=object())

    assert report["complete_pcap_read"] is False
    assert report["pcap_size"] == 0
    assert report["capture_read_error"] == {
        "exception_type": "ValueError",
        "message": "unsupported capture magic: ",
        "rule": "capture is empty or does not begin with supported PCAP/PCAPNG magic",
    }
    assert report["counters"]["capture_read_error::ValueError"] == 1
    assert json.loads(output.read_text(encoding="utf-8")) == report

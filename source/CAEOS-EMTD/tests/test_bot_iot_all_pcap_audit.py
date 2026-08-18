from pathlib import Path

from audit_caeos_bot_iot_all_pcaps import (
    apply_exclusion_policy,
    reusable,
    summarize,
)


def report(path: Path, *, matched: int, excluded: int) -> dict:
    flows = matched + excluded
    return {
        "dataset_id": "cic_bot_iot",
        "label_index_sha256": "index-sha",
        "pcap": str(path),
        "pcap_size": path.stat().st_size,
        "complete_pcap_read": True,
        "matched_flows": matched,
        "counters": {
            "flows": flows,
            "parsed_packets": flows * 2,
            "parsed_packet_bytes": flows * 100,
            "status::unmatched_label": excluded,
            "policy_excluded_flows": excluded,
            "policy_excluded_packets": excluded * 2,
            "policy_excluded_packet_bytes": excluded * 100,
        },
    }


def test_summarizes_complete_dataset_and_reuses_verified_audits(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.pcap"
    second = tmp_path / "second.pcap"
    first.write_bytes(b"pcap-one")
    second.write_bytes(b"pcap-two")
    reports = [report(first, matched=3, excluded=0), report(second, matched=2, excluded=1)]
    assert reusable(reports[0], first, "index-sha") is True
    summary = summarize(
        [first, second], reports, tmp_path / "labels.sqlite", "index-sha"
    )
    assert summary["processed_pcap_file_count"] == 2
    assert summary["matched_flows"] == 5
    assert summary["excluded_flows"] == 1
    assert summary["effective_coverage_fraction"] == 1.0
    assert summary["formal_label_gate_passed"] is True


def test_reclassifies_time_nonoverlap_from_complete_audit(tmp_path: Path) -> None:
    pcap = tmp_path / "capture.pcap"
    pcap.write_bytes(b"pcap")
    value = report(pcap, matched=8, excluded=0)
    value["counters"].update(
        {
            "flows": 10,
            "status::unmatched_label": 2,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping": 2,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packets": 4,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packet_bytes": 200,
        }
    )

    reclassified = apply_exclusion_policy(value)

    assert reclassified["counters"]["policy_excluded_flows"] == 2
    assert reclassified["label_exclusion_summary"]["reason_counts"] == {
        "five_tuple_present_but_time_not_overlapping": 2
    }

import argparse
import json
import zipfile
from pathlib import Path

import pytest

from audit_caeos_all_pcap_members import (
    Materializer,
    apply_exclusion_policy,
    build_inventory,
    freeze_inventory,
    progress_record,
    reusable,
    summarize,
)


def arguments(tmp_path: Path, *, member_mode: str = "pcap_suffix") -> argparse.Namespace:
    dataset = tmp_path / "dataset"
    return argparse.Namespace(
        dataset_id="example",
        dataset_root=dataset,
        pcap_root=[dataset / "direct"],
        archive_root=[dataset / "archives"],
        archive_member_mode=member_mode,
        label_index=tmp_path / "labels.sqlite",
        label_index_sha256="index-sha",
        inventory_output=tmp_path / "inventory.json",
    )


def test_inventory_covers_direct_and_zip_sources_and_freezes_drift(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    direct = args.pcap_root[0]
    archives = args.archive_root[0]
    direct.mkdir(parents=True)
    archives.mkdir(parents=True)
    (direct / "one.pcap").write_bytes(b"direct")
    with zipfile.ZipFile(archives / "members.zip", "w") as handle:
        handle.writestr("two.pcap", b"zip-pcap")
        handle.writestr("README.txt", b"not a pcap")
    inventory = build_inventory(args)
    assert [item["kind"] for item in inventory["items"]] == [
        "zip_member",
        "direct_pcap",
    ]
    assert inventory["items"][0]["member"] == "two.pcap"
    freeze_inventory(args.inventory_output, inventory)
    assert json.loads(args.inventory_output.read_text(encoding="utf-8")) == inventory
    (direct / "three.pcap").write_bytes(b"drift")
    with pytest.raises(ValueError, match="inventory drift"):
        freeze_inventory(args.inventory_output, build_inventory(args))


def test_all_files_mode_covers_extensionless_cicddos_members(tmp_path: Path) -> None:
    args = arguments(tmp_path, member_mode="all_files")
    args.pcap_root = []
    args.archive_root[0].mkdir(parents=True)
    with zipfile.ZipFile(args.archive_root[0] / "pcaps.zip", "w") as handle:
        handle.writestr("SAT-03-11-2018_0", b"pcap-without-suffix")
    inventory = build_inventory(args)
    assert len(inventory["items"]) == 1
    assert inventory["items"][0]["member"] == "SAT-03-11-2018_0"


def test_materializer_extracts_one_extensionless_member_to_temporary_pcap(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path, member_mode="all_files")
    args.pcap_root = []
    args.archive_root[0].mkdir(parents=True)
    with zipfile.ZipFile(args.archive_root[0] / "pcaps.zip", "w") as handle:
        handle.writestr("SAT-03-11-2018_0", b"pcap-payload")
    item = build_inventory(args)["items"][0]
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    materializer = Materializer(temporary)
    try:
        path, should_delete = materializer.path_for(item)
        assert should_delete is True
        assert path.suffix == ".pcap"
        assert path.read_bytes() == b"pcap-payload"
    finally:
        materializer.close()


def test_summary_requires_every_frozen_source_and_approved_exclusions(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    inventory = {
        "inventory_sha256": "inventory-sha",
        "items": [
            {"logical_source_member": "one", "size": 10},
            {"logical_source_member": "two", "size": 20},
        ],
    }
    item = inventory["items"][0]
    report = {
        "dataset_id": "example",
        "label_index_sha256": "index-sha",
        "complete_pcap_read": True,
        "all_pcap_member_source": item,
        "matched_flows": 3,
        "counters": {
            "flows": 4,
            "parsed_packets": 8,
            "parsed_packet_bytes": 800,
            "status::unmatched_label": 1,
            "policy_excluded_flows": 1,
            "policy_excluded_packets": 2,
            "policy_excluded_packet_bytes": 200,
        },
    }
    assert reusable(report, item, "example", "index-sha") is True
    assert reusable(
        report,
        item,
        "example",
        "index-sha",
        conflict_policy="malicious_over_benign_bidirectional",
    ) is False
    assert reusable(
        report,
        item,
        "example",
        "index-sha",
        official_boundary_split=True,
    ) is True
    report["counters"]["status::conflicting_label"] = 1
    assert reusable(
        report,
        item,
        "example",
        "index-sha",
        official_boundary_split=True,
    ) is False
    report["counters"]["status::conflicting_label"] = 0
    assert summarize(args, inventory, [report])["formal_label_gate_passed"] is False
    complete = summarize(args, inventory, [report, report | {"all_pcap_member_source": inventory["items"][1]}])
    assert complete["effective_coverage_fraction"] == 1.0
    assert complete["formal_label_gate_passed"] is True


def test_reclassifies_time_nonoverlap_from_complete_member_audit() -> None:
    report = {
        "counters": {
            "flows": 2,
            "parsed_packets": 4,
            "parsed_packet_bytes": 400,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping": 2,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packets": 4,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packet_bytes": 400,
        }
    }

    reclassified = apply_exclusion_policy(report)

    assert reclassified["counters"]["policy_excluded_flows"] == 2
    assert reclassified["label_exclusion_summary"]["reason_counts"] == {
        "five_tuple_present_but_time_not_overlapping": 2
    }


def test_truncated_tail_policy_excludes_boundary_flows_but_retains_complete_flows() -> None:
    report = {
        "matched_flows": 3,
        "counters": {
            "flows": 4,
            "parsed_packets": 8,
            "parsed_packet_bytes": 800,
            "status::unmatched_label": 1,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping": 1,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packets": 2,
            "unmatched_reason::five_tuple_present_but_time_not_overlapping::packet_bytes": 200,
            "finalize::truncated_capture_boundary": 3,
            "status::aligned_unique_flow::finalize::truncated_capture_boundary": 2,
            "status::unmatched_label::finalize::truncated_capture_boundary": 1,
        },
    }

    reclassified = apply_exclusion_policy(
        report,
        {"action": "retain_complete_flows_before_truncated_tail"},
    )

    assert reclassified["counters"]["policy_excluded_unmatched_flows"] == 1
    assert reclassified["counters"]["policy_excluded_matched_flows"] == 2
    assert reclassified["counters"]["policy_excluded_flows"] == 3
    assert reclassified["label_exclusion_summary"]["retained_flows"] == 1


def test_binary_malicious_multiclass_conflicts_are_excluded_with_complete_evidence(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    args.conflict_exclusion_policy = (
        "binary_malicious_consensus_multiclass_ambiguous"
    )
    evidence = tmp_path / "conflict-manifest.json"
    evidence.write_text("{}", encoding="utf-8")
    args.conflict_exclusion_evidence = evidence
    item = {"logical_source_member": "one.pcap", "size": 100}
    inventory = {"inventory_sha256": "inventory-sha", "items": [item]}
    report = {
        "dataset_id": "example",
        "complete_pcap_read": True,
        "all_pcap_member_source": item,
        "matched_flows": 3,
        "conflicting_samples_truncated": False,
        "conflicting_samples": [
            {
                "candidate_label_counts": {
                    "DoS::DoS::binary=1": 2,
                    "Exploits::Exploits::binary=1": 1,
                },
                "packet_count": 2,
                "packet_bytes": 200,
            }
        ],
        "counters": {
            "flows": 4,
            "parsed_packets": 8,
            "parsed_packet_bytes": 800,
            "status::conflicting_label": 1,
        },
    }

    classified = apply_exclusion_policy(
        report,
        conflict_exclusion_policy=args.conflict_exclusion_policy,
    )
    result = summarize(args, inventory, [classified])

    assert result["conflicting_flows"] == 1
    assert result["policy_excluded_conflicting_flows"] == 1
    assert result["retained_conflicting_flows"] == 0
    assert result["effective_coverage_fraction"] == 1.0
    assert result["all_conflicting_flows_have_approved_exclusion_reason"] is True
    assert result["formal_label_gate_passed"] is True


def test_conflict_exclusion_rejects_mixed_binary_or_incomplete_evidence() -> None:
    base = {
        "conflicting_samples_truncated": False,
        "conflicting_samples": [
            {
                "candidate_label_counts": {
                    "Benign::Benign::binary=0": 1,
                    "Exploits::Exploits::binary=1": 1,
                },
                "packet_count": 2,
                "packet_bytes": 200,
            }
        ],
        "counters": {
            "flows": 1,
            "parsed_packets": 2,
            "parsed_packet_bytes": 200,
            "status::conflicting_label": 1,
        },
    }
    with pytest.raises(ValueError, match="unanimous malicious"):
        apply_exclusion_policy(
            base,
            conflict_exclusion_policy=(
                "binary_malicious_consensus_multiclass_ambiguous"
            ),
        )

    incomplete = json.loads(json.dumps(base))
    incomplete["conflicting_samples"] = []
    with pytest.raises(ValueError, match="complete per-flow conflict evidence"):
        apply_exclusion_policy(
            incomplete,
            conflict_exclusion_policy=(
                "binary_malicious_consensus_multiclass_ambiguous"
            ),
        )


def test_summary_records_capture_read_failure_without_passing_gate(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    item = {"logical_source_member": "truncated.pcap", "size": 100}
    inventory = {"inventory_sha256": "inventory-sha", "items": [item]}
    report = {
        "dataset_id": "example",
        "source_member": "truncated.pcap",
        "all_pcap_member_source": item,
        "complete_pcap_read": False,
        "capture_read_error": {
            "exception_type": "NeedData",
            "message": "got 5, 16 needed at least",
        },
        "matched_flows": 0,
        "counters": {"capture_read_errors": 1},
    }

    result = summarize(args, inventory, [report])

    assert result["processed_source_count"] == 1
    assert result["source_read_failure_count"] == 1
    assert result["source_read_failures"][0]["source"] == "truncated.pcap"
    assert result["all_sources_complete"] is False
    assert result["formal_label_gate_passed"] is False


def test_exact_source_quality_policy_enables_only_the_adjusted_gate(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    truncated = {
        "logical_source_member": "truncated.pcap",
        "source_member": "truncated.pcap",
        "kind": "zip_member",
        "size": 100,
        "member_size": 100,
        "member_crc32": "abcdef01",
    }
    empty = {
        "logical_source_member": "empty.pcap",
        "source_member": "empty.pcap",
        "kind": "zip_member",
        "size": 0,
        "member_size": 0,
        "member_crc32": "00000000",
    }
    inventory = {
        "inventory_sha256": "inventory-sha",
        "items": [truncated, empty],
    }
    reports = [
        {
            "dataset_id": "example",
            "source_member": "truncated.pcap",
            "all_pcap_member_source": truncated,
            "complete_pcap_read": False,
            "capture_read_error": {
                "exception_type": "NeedData",
                "message": "got 5, 16 needed at least",
                "rule": "capture ended inside a PCAP record header or packet body",
            },
            "matched_flows": 1,
            "counters": {
                "capture_read_errors": 1,
                "capture_read_error::NeedData": 1,
                "flows": 2,
                "parsed_packets": 3,
                "parsed_packet_bytes": 300,
                "status::unmatched_label": 1,
                "policy_excluded_flows": 1,
                "policy_excluded_packets": 1,
                "policy_excluded_packet_bytes": 100,
            },
        },
        {
            "dataset_id": "example",
            "source_member": "empty.pcap",
            "all_pcap_member_source": empty,
            "complete_pcap_read": False,
            "capture_read_error": {
                "exception_type": "ValueError",
                "message": "unsupported capture magic: ",
                "rule": "capture is empty or does not begin with supported PCAP/PCAPNG magic",
            },
            "matched_flows": 0,
            "counters": {
                "capture_read_errors": 1,
                "capture_read_error::ValueError": 1,
            },
        },
    ]
    policy = {
        "schema_version": "caeos_source_quality_policy_v1",
        "dataset_id": "example",
        "inventory_sha256": "inventory-sha",
        "exceptions": [
            {
                "source": "truncated.pcap",
                "action": "retain_complete_records_before_truncated_tail",
                "expected_source": {
                    "kind": "zip_member",
                    "member_size": 100,
                    "member_crc32": "abcdef01",
                },
                "expected_error": {
                    "exception_type": "NeedData",
                    "message": "got 5, 16 needed at least",
                    "rule": "capture ended inside a PCAP record header or packet body",
                },
                "expected_counters": {
                    "parsed_packets": 3,
                    "capture_read_errors": 1,
                },
                "expected_report": {"matched_flows": 1},
                "justification": "retain every complete physical record before the tail",
            },
            {
                "source": "empty.pcap",
                "action": "exclude_zero_length_archive_member",
                "expected_source": {
                    "kind": "zip_member",
                    "member_size": 0,
                    "member_crc32": "00000000",
                },
                "expected_error": {
                    "exception_type": "ValueError",
                    "message": "unsupported capture magic: ",
                    "rule": "capture is empty or does not begin with supported PCAP/PCAPNG magic",
                },
                "expected_counters": {"capture_read_errors": 1},
                "expected_report": {"matched_flows": 0},
                "justification": "the official archive member contains zero bytes",
            },
        ],
    }
    policy_path = tmp_path / "source_quality_policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    args.source_quality_policy = policy_path

    result = summarize(args, inventory, reports)

    assert result["formal_label_gate_passed"] is False
    assert result["all_sources_complete"] is False
    assert result["all_sources_usable_or_quarantined"] is True
    assert result["source_quality_resolved_count"] == 2
    assert result["source_quality_unresolved"] == []
    assert result["source_quality_adjusted_gate_passed"] is True

    policy["exceptions"][0]["expected_counters"]["parsed_packets"] = 4
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    mismatch = summarize(args, inventory, reports)
    assert mismatch["source_quality_adjusted_gate_passed"] is False
    assert mismatch["source_quality_unresolved"][0]["reasons"] == [
        "counter evidence mismatch"
    ]


def test_stable_needdata_report_is_reused_without_becoming_complete(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    item = {
        "logical_source_member": "truncated.pcap",
        "source_member": "truncated.pcap",
        "kind": "direct_pcap",
        "path": str(args.pcap_root[0] / "truncated.pcap"),
        "size": 100,
    }
    report = {
        "dataset_id": args.dataset_id,
        "label_index_sha256": "index-sha",
        "all_pcap_member_source": item,
        "complete_pcap_read": False,
        "capture_read_error": {
            "exception_type": "NeedData",
            "message": "got 5, 16 needed at least",
            "rule": "capture ended inside a PCAP record header or packet body",
        },
        "counters": {
            "capture_read_errors": 1,
            "capture_read_error::NeedData": 1,
        },
        "tolerance_ns": 1_000_000,
        "idle_seconds": 30.0,
        "conflict_policy": "reject",
        "time_nonoverlap_policy": "reject",
        "official_boundary_split": False,
    }

    assert reusable(
        report,
        item,
        args.dataset_id,
        "index-sha",
        tolerance_ns=1_000_000,
        idle_seconds=30.0,
        conflict_policy="reject",
        time_nonoverlap_policy="reject",
        official_boundary_split=False,
    ) is True
    assert report["complete_pcap_read"] is False


def test_stable_empty_capture_report_is_reused_without_becoming_complete(
    tmp_path: Path,
) -> None:
    args = arguments(tmp_path)
    item = {
        "logical_source_member": "empty.pcap",
        "source_member": "empty.pcap",
        "kind": "direct_pcap",
        "path": str(args.pcap_root[0] / "empty.pcap"),
        "size": 0,
    }
    report = {
        "dataset_id": args.dataset_id,
        "label_index_sha256": "index-sha",
        "all_pcap_member_source": item,
        "complete_pcap_read": False,
        "capture_read_error": {
            "exception_type": "ValueError",
            "message": "unsupported capture magic: ",
            "rule": "capture is empty or does not begin with supported PCAP/PCAPNG magic",
        },
        "counters": {
            "capture_read_errors": 1,
            "capture_read_error::ValueError": 1,
        },
        "tolerance_ns": 1_000_000,
        "idle_seconds": 30.0,
        "conflict_policy": "reject",
        "time_nonoverlap_policy": "reject",
        "official_boundary_split": False,
    }

    assert reusable(
        report,
        item,
        args.dataset_id,
        "index-sha",
        tolerance_ns=1_000_000,
        idle_seconds=30.0,
        conflict_policy="reject",
        time_nonoverlap_policy="reject",
        official_boundary_split=False,
    ) is True
    assert report["complete_pcap_read"] is False


def test_progress_record_accepts_valid_header_only_pcap() -> None:
    item = {"logical_source_member": "empty-but-valid.pcap"}
    report = {
        "complete_pcap_read": True,
        "coverage_fraction": 0.0,
        "counters": {
            "policy_excluded_flows": 0,
            "policy_excluded_packets": 0,
        },
    }

    progress = progress_record(report, item, ordinal=7, total=10)

    assert progress == {
        "ordinal": 7,
        "total": 10,
        "source": "empty-but-valid.pcap",
        "flows": 0,
        "coverage_fraction": 0.0,
        "complete_pcap_read": True,
    }

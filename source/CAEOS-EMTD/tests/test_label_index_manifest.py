from __future__ import annotations

import argparse
import json
from pathlib import Path

from assemble_caeos_label_index_manifest import build


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_manifest_keeps_multiple_coverage_evidence_and_uses_retained_gate(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    dump(
        registry,
        {
            "datasets": {
                "sample": {"status": "adapter_required"},
            }
        },
    )
    index_audit = tmp_path / "index.json"
    dump(
        index_audit,
        {
            "dataset_id": "sample",
            "resolver_tolerance_ns": 10,
            "label_index": {
                "path": "/data/sample.sqlite",
                "sha256": "abc",
                "record_count": 10,
            },
        },
    )
    official = tmp_path / "official.json"
    dump(
        official,
        {
            "dataset_id": "sample",
            "scope": "full_official_event_set",
            "coverage_fraction": 1.0,
            "formal_gate_passed": False,
            "formal_gate_reason": "PCAP gate pending",
        },
    )
    pcap = tmp_path / "pcap.json"
    dump(
        pcap,
        {
            "dataset_id": "sample",
            "scope": "bounded_packet_prefix_not_formal_full_coverage",
            "coverage_fraction": 0.8,
            "matched_flows": 8,
            "label_exclusion_summary": {
                "total_finalized_flows": 10,
                "excluded_flows": 2,
            },
            "formal_gate_passed": False,
            "formal_gate_reason": "sampled smoke",
        },
    )
    report = build(
        argparse.Namespace(
            registry=registry,
            output=tmp_path / "manifest.json",
            exclusion_policy=None,
            index_audit=[index_audit],
            coverage_audit=[official, pcap],
        )
    )
    dataset = report["datasets"][0]
    assert len(dataset["coverage_evidence"]) == 2
    assert dataset["effective_coverage_fraction"] == 1.0
    assert dataset["formal_gate_passed"] is False
    assert dataset["status"] == "index_ready_sampled_coverage_only"


def test_capture_inventory_gate_is_ready_without_claiming_strict_flow_gate(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    dump(registry, {"datasets": {"ciciot2023": {"status": "adapter_required"}}})
    index_audit = tmp_path / "index.json"
    dump(
        index_audit,
        {
            "dataset_id": "ciciot2023",
            "label_index": {
                "path": "/data/ciciot2023.sqlite",
                "sha256": "abc",
                "record_count": 309,
            },
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "CICIoT2023",
            "accepted_source_count": 309,
            "expected_source_count": 309,
            "formal_dataset_gate_passed": True,
            "authority_granularity": "capture_member_not_official_flow_label",
        },
    )
    report = build(
        argparse.Namespace(
            registry=registry,
            output=tmp_path / "manifest.json",
            exclusion_policy=None,
            index_audit=[index_audit],
            coverage_audit=[coverage],
        )
    )
    dataset = report["datasets"][0]
    assert dataset["status"] == "ready"
    assert dataset["admission_gate_passed"] is True
    assert dataset["formal_gate_passed"] is False
    assert dataset["admission_gate_types"] == ["full_capture_member_inventory"]


def test_documented_single_class_capture_uses_capture_inventory_gate(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    dump(registry, {"datasets": {"5gad_2022": {"status": "adapter_required"}}})
    index_audit = tmp_path / "index.json"
    dump(
        index_audit,
        {
            "dataset_id": "5gad_2022",
            "label_index": {
                "path": "/data/5gad_2022.sqlite",
                "sha256": "abc",
                "record_count": 25,
            },
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "5gad_2022",
            "authority_granularity": "documented_single_class_capture",
            "all_sources_complete": True,
            "effective_coverage_fraction": 1.0,
            "raw_coverage_fraction": 1.0,
            "formal_label_gate_passed": True,
        },
    )
    report = build(
        argparse.Namespace(
            registry=registry,
            output=tmp_path / "manifest.json",
            exclusion_policy=None,
            index_audit=[index_audit],
            coverage_audit=[coverage],
        )
    )
    dataset = report["datasets"][0]
    assert dataset["status"] == "ready"
    assert dataset["admission_gate_passed"] is True
    assert dataset["formal_gate_passed"] is False
    assert dataset["admission_gate_types"] == ["full_capture_member_inventory"]


def test_source_quality_gate_requires_immutable_exception_policy(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    dump(registry, {"datasets": {"dohbrw2020": {"status": "adapter_required"}}})
    index_audit = tmp_path / "index.json"
    dump(
        index_audit,
        {
            "dataset_id": "dohbrw2020",
            "label_index": {
                "path": "/data/doh.sqlite",
                "sha256": "abc",
                "record_count": 10,
            },
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "dohbrw2020",
            "effective_coverage_fraction": 1.0,
            "formal_label_gate_passed": False,
            "all_sources_usable_or_quarantined": True,
            "source_quality_adjusted_gate_passed": True,
            "source_quality_policy_sha256": "policy-sha",
        },
    )
    report = build(
        argparse.Namespace(
            registry=registry,
            output=tmp_path / "manifest.json",
            exclusion_policy=None,
            index_audit=[index_audit],
            coverage_audit=[coverage],
        )
    )
    dataset = report["datasets"][0]
    assert dataset["status"] == "ready"
    assert dataset["admission_gate_passed"] is True
    assert dataset["formal_gate_passed"] is False
    assert dataset["admission_gate_types"] == ["source_quality_adjusted_flow_label"]


def test_strict_flow_gate_takes_precedence_over_unused_quality_gate(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    dump(registry, {"datasets": {"unsw_nb15": {"status": "adapter_required"}}})
    index_audit = tmp_path / "index.json"
    dump(
        index_audit,
        {
            "dataset_id": "unsw_nb15",
            "label_index": {
                "path": "/data/unsw.sqlite",
                "sha256": "abc",
                "record_count": 10,
            },
        },
    )
    coverage = tmp_path / "coverage.json"
    dump(
        coverage,
        {
            "dataset_id": "unsw_nb15",
            "effective_coverage_fraction": 1.0,
            "formal_label_gate_passed": True,
            "source_quality_adjusted_gate_passed": True,
            "all_sources_usable_or_quarantined": True,
        },
    )
    report = build(
        argparse.Namespace(
            registry=registry,
            output=tmp_path / "manifest.json",
            exclusion_policy=None,
            index_audit=[index_audit],
            coverage_audit=[coverage],
        )
    )
    dataset = report["datasets"][0]
    assert dataset["status"] == "ready"
    assert dataset["formal_gate_passed"] is True
    assert dataset["admission_gate_types"] == ["strict_flow_label"]

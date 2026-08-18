from __future__ import annotations

import argparse
from pathlib import Path

from caeos_label_alignment import create_label_index
from validate_caeos_label_index import validate


def test_validates_complete_label_index(tmp_path: Path) -> None:
    path = tmp_path / "labels.sqlite"
    create_label_index(
        path,
        "sample",
        [
            {
                "src_ip": "192.0.2.1",
                "src_port": 1234,
                "dst_ip": "192.0.2.2",
                "dst_port": 443,
                "protocol": 6,
                "start_ns": 1,
                "end_ns": 2,
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "synthetic",
            }
        ],
        "registry",
    )
    report = validate(
        argparse.Namespace(
            path=path,
            dataset_id="sample",
            output=tmp_path / "validation.json",
            group_counts=True,
            require_protocol_distribution=True,
        )
    )
    assert report["passed"] is True
    assert report["actual_record_count"] == 1
    assert report["group_counts"]["family_label"] == {"Benign": 1}
    assert report["protocol_distribution_gate"] == {
        "required": True,
        "present": True,
        "record_count": 1,
        "sums_to_all_records": True,
        "protocol_values_valid": True,
    }


def test_rejects_invalid_protocol_distribution(tmp_path: Path) -> None:
    path = tmp_path / "labels.sqlite"
    create_label_index(
        path,
        "sample",
        [
            {
                "src_ip": "192.0.2.1",
                "src_port": 1234,
                "dst_ip": "192.0.2.2",
                "dst_port": 443,
                "protocol": 999,
                "start_ns": 1,
                "end_ns": 2,
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "synthetic",
            }
        ],
        "registry",
    )
    report = validate(
        argparse.Namespace(
            path=path,
            dataset_id="sample",
            output=tmp_path / "validation.json",
            group_counts=True,
            require_protocol_distribution=True,
        )
    )
    assert report["passed"] is False
    assert report["checks"]["protocol_values_valid"] is False

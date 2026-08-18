from __future__ import annotations

import hashlib
from pathlib import Path

from caeos_label_alignment import LabelResolver, create_label_index, packed_ip


def test_endpoint_time_rule_precedes_benign_capture_fallback(tmp_path: Path) -> None:
    index = tmp_path / "labels.sqlite"
    report = create_label_index(
        index,
        "cicids2018",
        [
            {
                "record_id": "attack",
                "src_ip": "10.0.0.1",
                "dst_ip": "10.0.0.2",
                "src_port": None,
                "dst_port": None,
                "protocol": 6,
                "start_ns": 100,
                "end_ns": 200,
                "fine_label": "DoS-GoldenEye",
                "family_label": "DoS",
                "binary_label": 1,
                "label_source": "official schedule",
            },
            {
                "record_id": "benign",
                "source_member": None,
                "protocol": 6,
                "start_ns": 0,
                "end_ns": 1000,
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "official schedule fallback",
            },
        ],
        "registry",
    )
    assert report["record_count"] == 2
    resolver = LabelResolver(index, "cicids2018", hashlib.sha256(index.read_bytes()).hexdigest())
    try:
        attack = resolver.resolve(
            "capture", packed_ip("10.0.0.1"), 12345, packed_ip("10.0.0.2"), 80, 6, 120, 130
        )
        benign = resolver.resolve(
            "capture", packed_ip("10.0.0.3"), 12345, packed_ip("10.0.0.2"), 80, 6, 120, 130
        )
        unsupported = resolver.resolve(
            "capture", packed_ip("10.0.0.3"), 0, packed_ip("10.0.0.2"), 0, 1, 120, 130
        )
    finally:
        resolver.close()
    assert attack.status == "aligned_unique_flow"
    assert attack.fine_label == "DoS-GoldenEye"
    assert benign.status == "aligned_unique_capture"
    assert benign.fine_label == "Benign"
    assert unsupported.status == "unmatched_label"

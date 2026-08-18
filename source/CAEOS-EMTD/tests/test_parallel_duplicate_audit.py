from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_caeos_flow_duplicates import build_report, build_report_parallel


FIELDS = [
    "sample_id",
    "capture_id",
    "packet_length_seq",
    "packet_iat_us_seq",
    "direction_seq",
    "packet_protocol_seq",
    "tcp_flags_seq",
    "packet_payload_length_seq",
    "payload_b64",
    "traffic_class",
    "attack_category",
    "attack_subcategory",
    "fine_label",
    "family_label",
    "binary_label",
]


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def row(sample: str, capture: str, content: str, label: str) -> dict[str, str]:
    return {
        "sample_id": digest(sample),
        "capture_id": digest(capture),
        "packet_length_seq": content,
        "packet_iat_us_seq": "0,1",
        "direction_seq": "0,1",
        "packet_protocol_seq": "6,6",
        "tcp_flags_seq": "2,16",
        "packet_payload_length_seq": "0,4",
        "payload_b64": "dGVzdA==",
        "traffic_class": label,
        "attack_category": label,
        "attack_subcategory": label,
        "fine_label": label,
        "family_label": label,
        "binary_label": "1",
    }


def write_class(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def manifest(tmp_path: Path) -> dict[str, object]:
    first = [row(f"a-{index}", "c1", f"x-{index}", "A") for index in range(24)]
    second = [row(f"b-{index}", "c2", f"y-{index}", "B") for index in range(24)]
    first[-1] = row("a-0", "c1", "x-23", "A")
    second[-1] = row("b-23", "c2", "x-0", "B")
    paths = [tmp_path / "A.csv", tmp_path / "B.csv"]
    write_class(paths[0], first)
    write_class(paths[1], second)
    classes = []
    for category, path, rows in zip(("A", "B"), paths, (first, second)):
        classes.append(
            {
                "attack_category": category,
                "path": str(path),
                "rows": len(rows),
                "size_bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "f" * 64,
        "row_count": len(first) + len(second),
        "class_csvs": classes,
    }


def test_parallel_audit_matches_sequential_across_classes_and_shards(tmp_path: Path) -> None:
    value = manifest(tmp_path)
    sequential = build_report(value, tmp_path / "sequential", 8)
    parallel = build_report_parallel(
        value,
        tmp_path / "parallel",
        bucket_count=8,
        class_parallelism=2,
        shards_per_class=8,
        resume=True,
    )
    assert parallel["row_count"] == sequential["row_count"]
    assert parallel["identity"] == sequential["identity"]
    assert parallel["content"] == sequential["content"]
    assert parallel["gate_pass"] == sequential["gate_pass"] is False


def test_parallel_audit_resumes_completed_shards(tmp_path: Path) -> None:
    value = manifest(tmp_path)
    scratch = tmp_path / "parallel"
    first = build_report_parallel(value, scratch, 8, 2, 8, True)
    second = build_report_parallel(value, scratch, 8, 2, 8, True)
    assert second["identity"] == first["identity"]
    assert second["content"] == first["content"]

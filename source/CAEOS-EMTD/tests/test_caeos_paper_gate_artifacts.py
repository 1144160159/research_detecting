from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from audit_caeos_flow_duplicates import build_report, build_report_parallel
from audit_caeos_train_deploy_equivalence import build_report as build_equivalence
from build_caeos_paper_d0_p0_artifacts import manifest_passes
from caeos_paper_views import (
    deployment_json_to_views,
    exact_view_bytes,
    training_row_to_views,
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def row(sample: str, capture: str, label: str = "Attack") -> dict[str, str]:
    return {
        "sample_id": digest(sample),
        "capture_id": digest(capture),
        "flow_key_hash": digest("flow-" + sample),
        "flow_start_ns": "1",
        "flow_end_ns": "2",
        "packet_length_seq": "60;70",
        "packet_iat_us_seq": "0;1",
        "direction_seq": "1;-1",
        "packet_protocol_seq": "6;6",
        "tcp_flags_seq": "2;16",
        "packet_payload_length_seq": "10;20",
        "payload_b64": "YWJj",
        "traffic_class": "Malicious",
        "attack_category": "Other_Attack",
        "attack_subcategory": label,
        "fine_label": label,
        "family_label": label,
        "binary_label": "1",
    }


def test_duplicate_audit_passes_unique_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "Attack.csv"
    write_csv(csv_path, [row("a", "c1"), row("b", "c2")])
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": 2,
        "class_csvs": [{"path": str(csv_path)}],
    }
    report = build_report(manifest, tmp_path / "scratch", 4)
    assert report["gate_pass"] is True
    assert report["identity"]["duplicate_key_count"] == 0


def test_duplicate_audit_accepts_large_valid_csv_field(tmp_path: Path) -> None:
    csv_path = tmp_path / "Attack.csv"
    value = row("large", "c1")
    value["payload_b64"] = "A" * 200_000
    write_csv(csv_path, [value])
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": 1,
        "class_csvs": [{"path": str(csv_path)}],
    }

    report = build_report(manifest, tmp_path / "scratch", 4)

    assert report["gate_pass"] is True
    assert report["row_count"] == 1


def test_duplicate_audit_rejects_duplicate_sample_id(tmp_path: Path) -> None:
    csv_path = tmp_path / "Attack.csv"
    write_csv(csv_path, [row("a", "c1"), row("a", "c1")])
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": 2,
        "class_csvs": [{"path": str(csv_path)}],
    }
    report = build_report(manifest, tmp_path / "scratch", 4)
    assert report["gate_pass"] is False
    assert report["identity"]["duplicate_key_count"] == 1
    assert report["identity"]["duplicate_examples"][0]["key_sha256"] == digest("a")


def test_duplicate_audit_rejects_exact_model_content_with_different_labels(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "Attack.csv"
    first = row("a", "c1", "Attack-A")
    second = row("b", "c2", "Attack-B")
    write_csv(csv_path, [first, second])
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": 2,
        "class_csvs": [{"path": str(csv_path)}],
    }
    report = build_report(manifest, tmp_path / "scratch", 4)
    assert report["gate_pass"] is False
    assert report["content"]["cross_label_key_count"] == 1
    assert report["content"]["cross_label_examples"][0]["first_sample_id"] == digest(
        "a"
    )


def test_duplicate_audit_does_not_treat_narrow_projection_as_exact_content(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "Attack.csv"
    first = row("a", "c1", "Attack-A")
    second = row("b", "c2", "Attack-B")
    first["duration_us"] = "1"
    second["duration_us"] = "2"
    write_csv(csv_path, [first, second])
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": 2,
        "class_csvs": [{"path": str(csv_path)}],
    }
    report = build_report(manifest, tmp_path / "scratch", 4)
    assert report["gate_pass"] is True
    assert report["content"]["cross_label_key_count"] == 0


def test_parallel_duplicate_audit_matches_sequential_counts(tmp_path: Path) -> None:
    csv_path = tmp_path / "Attack.csv"
    rows = [row(f"sample-{index}", f"capture-{index % 3}") for index in range(20)]
    rows.append(dict(rows[3]))
    write_csv(csv_path, rows)
    manifest = {
        "complete": True,
        "dataset_id": "test",
        "manifest_sha256": "a" * 64,
        "row_count": len(rows),
        "class_csvs": [
            {
                "path": str(csv_path),
                "attack_category": "Other_Attack",
                "size_bytes": csv_path.stat().st_size,
                "sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
                "rows": len(rows),
            }
        ],
    }
    sequential = build_report(manifest, tmp_path / "sequential", 4)
    parallel = build_report_parallel(
        manifest,
        tmp_path / "parallel",
        bucket_count=4,
        class_parallelism=1,
        shards_per_class=2,
        resume=False,
    )
    assert parallel["row_count"] == sequential["row_count"]
    for section in ("identity", "content"):
        for field in (
            "duplicate_rows_after_first",
            "duplicate_key_count",
            "cross_label_key_count",
            "cross_capture_key_count",
        ):
            assert parallel[section][field] == sequential[section][field]


def test_manifest_gate_rejects_non_admitted_labels() -> None:
    manifest = {
        "complete": True,
        "row_count": 1,
        "class_csvs": [
            {
                "rows": 1,
                "verification": {
                    "full_row_validation": True,
                    "label_status_counts": {"unmatched_flow": 1},
                },
            }
        ],
    }
    assert manifest_passes(manifest) is False


def test_train_deploy_materialization_is_exact() -> None:
    value = row("a", "c1")
    value["packet_count_stored"] = "2"
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    training = exact_view_bytes(training_row_to_views(value))
    deployment = exact_view_bytes(deployment_json_to_views(serialized))
    assert training == deployment


def test_equivalence_report_covers_each_class(tmp_path: Path) -> None:
    csv_path = tmp_path / "Attack.csv"
    value = row("a", "c1")
    value["packet_count_stored"] = "2"
    write_csv(csv_path, [value])
    report = build_equivalence(
        {
            "complete": True,
            "dataset_id": "test",
            "manifest_sha256": "a" * 64,
            "class_csvs": [
                {"attack_category": "Other_Attack", "path": str(csv_path)}
            ],
        },
        1,
    )
    assert report["gate_pass"] is True
    assert report["sample_count"] == 1

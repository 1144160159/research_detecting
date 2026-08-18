from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import audit_caeos_flow_duplicates as AUDIT  # noqa: E402
import build_caeos_content_conflict_policy as POLICY  # noqa: E402
import rebuild_caeos_dataset_completion as COMPLETION  # noqa: E402


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


def row(sample: int, capture: int, content: str, label: str) -> dict[str, str]:
    malicious = label != "Benign"
    return {
        "sample_id": f"{sample:064x}",
        "capture_id": f"{capture:064x}",
        "packet_length_seq": content,
        "packet_iat_us_seq": "0;10",
        "direction_seq": "1;-1",
        "packet_protocol_seq": "6;6",
        "tcp_flags_seq": "2;16",
        "packet_payload_length_seq": "0;4",
        "payload_b64": "dGVzdA==",
        "traffic_class": "Malicious" if malicious else "Benign",
        "attack_category": "DDoS" if malicious else "Benign",
        "attack_subcategory": label,
        "fine_label": label,
        "family_label": label,
        "binary_label": "1" if malicious else "0",
    }


def fixture(tmp_path: Path) -> tuple[dict, Path, list[dict[str, str]]]:
    rows = [
        row(1, 11, "10;20", "Benign"),
        row(2, 12, "10;20", "UDP_Flood"),
        row(3, 13, "30;40", "Benign"),
        row(4, 14, "30;40", "Benign"),
    ]
    csv_path = tmp_path / "Mixed.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    csv_sha256 = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "caeos_dataset_class_csv_manifest_v1",
        "dataset_id": "fixture",
        "complete": True,
        "row_count": len(rows),
        "manifest_sha256": "a" * 64,
        "class_csvs": [
            {
                "attack_category": "Mixed",
                "path": str(csv_path),
                "rows": len(rows),
                "size_bytes": csv_path.stat().st_size,
                "sha256": csv_sha256,
            }
        ],
    }
    manifest_path = tmp_path / "dataset.manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest, manifest_path, rows


def test_cross_label_content_is_quarantined_without_mutating_source(tmp_path: Path) -> None:
    manifest, manifest_path, rows = fixture(tmp_path)
    source_before = Path(manifest["class_csvs"][0]["path"]).read_bytes()
    scratch = tmp_path / "scratch"
    audit = AUDIT.build_report_parallel(
        manifest,
        scratch,
        bucket_count=4,
        class_parallelism=1,
        shards_per_class=2,
        resume=True,
    )
    assert audit["identity"]["duplicate_key_count"] == 0
    assert audit["content"]["cross_label_key_count"] == 1
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit), encoding="utf-8")

    output = tmp_path / "policy"
    result = POLICY.build_policy(
        manifest_path=manifest_path,
        audit_path=audit_path,
        scratch=scratch,
        output_dir=output,
        workers=2,
        bucket_count=4,
        resume=True,
        reuse_partitions=True,
        repair_proof=None,
        cleanup_owned_scratch=False,
    )

    assert result["ambiguous_content_key_count"] == 1
    assert result["ambiguous_row_count"] == 2
    assert result["model_eligible_row_count"] == 2
    assert result["retained_cross_label_key_count"] == 0
    assert result["model_view_gate_pass"] is True
    assert Path(manifest["class_csvs"][0]["path"]).read_bytes() == source_before

    keys = POLICY.load_ambiguous_content_keys(output / "policy.json")
    assert not POLICY.row_is_model_eligible(rows[0], FIELDS, keys)
    assert not POLICY.row_is_model_eligible(rows[1], FIELDS, keys)
    assert POLICY.row_is_model_eligible(rows[2], FIELDS, keys)
    assert POLICY.row_is_model_eligible(rows[3], FIELDS, keys)


def test_policy_rejects_audit_count_mismatch(tmp_path: Path) -> None:
    manifest, manifest_path, _ = fixture(tmp_path)
    scratch = tmp_path / "scratch"
    audit = AUDIT.build_report_parallel(
        manifest,
        scratch,
        bucket_count=4,
        class_parallelism=1,
        shards_per_class=2,
        resume=True,
    )
    audit["content"]["cross_label_key_count"] = 2
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit), encoding="utf-8")

    try:
        POLICY.build_policy(
            manifest_path=manifest_path,
            audit_path=audit_path,
            scratch=scratch,
            output_dir=tmp_path / "policy",
            workers=2,
            bucket_count=4,
            resume=True,
            reuse_partitions=True,
            repair_proof=None,
            cleanup_owned_scratch=False,
        )
    except ValueError as error:
        assert "differs from audit" in str(error)
    else:
        raise AssertionError("policy accepted a mismatched conflict count")


def test_completion_rebuild_rehashes_bound_class_csv(tmp_path: Path) -> None:
    manifest, manifest_path, _ = fixture(tmp_path)
    manifest.update(
        {
            "schema_sha256": "b" * 64,
            "source_manifest_sha256": "c" * 64,
            "processing_policy_sha256": "d" * 64,
        }
    )
    manifest["class_csvs"][0]["verification"] = {
        "full_row_validation": True,
        "rows": manifest["row_count"],
    }
    manifest.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = COMPLETION.canonical_json_hash(manifest)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    template = {
        "schema_version": COMPLETION.SCHEMA_VERSION,
        "catalog_sha256": "e" * 64,
        "schema_sha256": manifest["schema_sha256"],
        "source_manifest_sha256": manifest["source_manifest_sha256"],
        "pcap_repair_manifest_sha256_at_start": "f" * 64,
        "processing_policy_sha256_by_dataset": {"template": "1" * 64},
        "label_index_manifest_sha256": "2" * 64,
        "datasets": [{"dataset_id": "template"}],
        "dataset_count": 1,
        "all_complete": True,
    }
    template["completion_sha256"] = COMPLETION.canonical_json_hash(template)
    template_path = tmp_path / "template.json"
    template_path.write_text(json.dumps(template), encoding="utf-8")

    output = tmp_path / "completion.json"
    result = COMPLETION.rebuild_completion(
        manifest_path, template_path, output, workers=2
    )
    assert result["all_complete"] is True
    assert result["datasets"] == [manifest]
    assert result["completion_reconstruction"]["class_csv_hashes_recomputed"] is True
    assert COMPLETION.verified_embedded_hash(result, "completion_sha256")

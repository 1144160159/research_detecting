from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from caeos.unified_data import (
    CsvSchemaContract,
    DataContractError,
    RawDataRecord,
    SplitPlan,
    TrainOnlySampler,
    TrainingSamplingPolicy,
    UnifiedDatasetLoader,
    canonical_json_hash,
    digest_fields,
    sha256_file,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "configs" / "unified_multimodal_v4.schema.json"
FEATURE_VIEWS_PATH = PROJECT_ROOT / "configs" / "unified_multimodal_v5.feature_views.json"
DATASET_ID = "synthetic_contract"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def with_hash(value: dict[str, object], field: str) -> dict[str, object]:
    output = dict(value)
    output[field] = canonical_json_hash(output)
    return output


def token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def base_row(
    schema: CsvSchemaContract,
    name: str,
    capture_id: str,
    family: str,
    category: str,
) -> dict[str, str]:
    row: dict[str, str] = {}
    for spec in schema.columns:
        if spec.values:
            row[spec.name] = str(spec.values[0])
        elif spec.type_name in {"sha256_hex", "hex64"}:
            row[spec.name] = token(f"{name}:{spec.name}")
        elif spec.type_name == "string":
            row[spec.name] = "value"
        elif spec.type_name == "base64":
            row[spec.name] = ""
        elif spec.type_name == "uint32_sequence_256":
            row[spec.name] = ";".join("0" for _ in range(256))
        elif spec.type_name.endswith("_sequence"):
            row[spec.name] = ""
        else:
            row[spec.name] = "0"
    row.update(
        {
            "schema_version": "caeos_unified_multimodal_csv_schema_v4",
            "dataset_id": DATASET_ID,
            "dataset_role": "synthetic_test",
            "sample_id": token(name),
            "capture_id": capture_id,
            "source_member": f"{name}.pcap",
            "label_status": "aligned_unique_flow",
            "label_source": "synthetic_official",
            "label_mapping_version": "test-v1",
            "dataset_native_label": family,
            "traffic_class": "Benign" if category == "Benign" else "Malicious",
            "attack_category": category,
            "attack_subcategory": category,
            "fine_label": family,
            "family_label": family,
            "binary_label": "0" if category == "Benign" else "1",
            "duration_us": str(100 + sum(name.encode("utf-8"))),
            "packet_count_stored": "3",
            "packet_count_total": "3",
            "payload_b64": "AQIDBA==",
            "payload_bytes_total": "4",
            "payload_bytes_stored": "4",
            "forward_payload_bytes": "3",
            "reverse_payload_bytes": "1",
            "packet_length_seq": "100;80;60",
            "ip_length_seq": "100;80;60",
            "packet_iat_us_seq": "0;10;20",
            "direction_seq": "1;-1;1",
            "packet_protocol_seq": "6;6;6",
            "tcp_flags_seq": "2;18;16",
            "ip_dscp_ecn_seq": "0;0;0",
            "ip_flags_seq": "2;2;2",
            "ip_fragment_offset_seq": "0;0;0",
            "ip_fragment_id_seq": "1;1;1",
            "transport_header_length_seq": "20;20;20",
            "tcp_sequence_seq": "1;2;3",
            "tcp_acknowledgement_seq": "0;2;3",
            "packet_payload_length_seq": "20;10;5",
            "sanitized_l4_packet_length_seq": "40;30;25",
            "packet_ttl_seq": "64;64;63",
            "tcp_window_seq": "1024;2048;2048",
        }
    )
    return row


def build_fixture(tmp_path: Path) -> dict[str, object]:
    schema = CsvSchemaContract.load(SCHEMA_PATH)
    captures = {name: token(f"capture:{name}") for name in "abcdef"}
    rows = [
        base_row(schema, "benign-a", captures["a"], "Benign", "Benign"),
        base_row(schema, "benign-b", captures["b"], "Benign", "Benign"),
        base_row(schema, "recon-a", captures["c"], "Recon", "Reconnaissance"),
        base_row(schema, "recon-b", captures["d"], "Recon", "Reconnaissance"),
        base_row(schema, "ddos-a", captures["e"], "DDoS", "DDoS"),
        base_row(schema, "ddos-conflict", captures["f"], "DDoS", "DDoS"),
    ]
    dataset_dir = tmp_path / DATASET_ID
    entries: list[dict[str, object]] = []
    for category in ("Benign", "Reconnaissance", "DDoS"):
        category_rows = [row for row in rows if row["attack_category"] == category]
        csv_path = dataset_dir / f"{category}.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=schema.column_names)
            writer.writeheader()
            writer.writerows(category_rows)
        entries.append(
            {
                "attack_category": category,
                "path": str(csv_path),
                "rows": len(category_rows),
                "size_bytes": csv_path.stat().st_size,
                "sha256": sha256_file(csv_path),
                "verification": {
                    "full_row_validation": True,
                    "rows": len(category_rows),
                    "label_status_counts": {"aligned_unique_flow": len(category_rows)},
                },
            }
        )

    manifest_path = tmp_path / "control" / "dataset.manifest.json"
    manifest = with_hash(
        {
            "schema_version": "caeos_dataset_class_csv_manifest_v1",
            "dataset_id": DATASET_ID,
            "complete": True,
            "schema_sha256": schema.sha256,
            "row_count": len(rows),
            "class_csvs": entries,
        },
        "manifest_sha256",
    )
    write_json(manifest_path, manifest)

    excluded = [
        "schema_version",
        "dataset_id",
        "dataset_role",
        "sample_id",
        "capture_id",
        "source_container_sha256",
        "source_member",
        "label_status",
        "label_source",
        "label_mapping_version",
        "dataset_native_label",
        "flow_key_hash",
        "flow_start_ns",
        "flow_end_ns",
        "endpoint_a_hash",
        "endpoint_b_hash",
        "flow_segment_index",
        "traffic_class",
        "attack_category",
        "attack_subcategory",
        "fine_label",
        "family_label",
        "binary_label",
        "port_a",
        "port_b",
        "application_protocol_hint",
    ]
    fingerprint = {
        "algorithm": "sha256_ordered_column_name_value_nul",
        "excluded_non_model_columns": excluded,
    }
    duplicate_path = tmp_path / "control" / "duplicates.json"
    duplicate = {
        "schema_version": "caeos_flow_duplicate_audit_v2",
        "dataset_id": DATASET_ID,
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "row_count": len(rows),
        "gate_pass": False,
        "fingerprint_contract": fingerprint,
        "content": {
            "capture_equivalence_edges": [[captures["a"], captures["b"]]],
        },
    }
    write_json(duplicate_path, duplicate)

    content_columns = tuple(name for name in schema.column_names if name not in excluded)
    ambiguous_key = digest_fields(rows[-1], content_columns)
    ambiguous_path = tmp_path / "control" / "ambiguous.sha256.bin"
    ambiguous_path.write_bytes(ambiguous_key)
    policy_path = tmp_path / "control" / "policy.json"
    policy = with_hash(
        {
            "schema_version": "caeos_content_conflict_policy_v1",
            "dataset_id": DATASET_ID,
            "dataset_manifest_sha256": manifest["manifest_sha256"],
            "source_duplicate_audit_sha256": sha256_file(duplicate_path),
            "decision": "exclude_all_rows_whose_model_content_sha256_is_cross_label",
            "model_view_gate_pass": True,
            "model_eligible_row_count": len(rows) - 1,
            "ambiguous_content_path": str(ambiguous_path),
            "ambiguous_content_size_bytes": ambiguous_path.stat().st_size,
            "ambiguous_content_sha256": sha256_file(ambiguous_path),
            "ambiguous_content_key_count": 1,
            "fingerprint_contract": fingerprint,
        },
        "policy_sha256",
    )
    write_json(policy_path, policy)

    registry_path = tmp_path / "registry.json"
    write_json(
        registry_path,
        {
            "schema_version": "caeos_unified_data_access_policy_v1",
            "defaults": {
                "label_status_prefixes": ["aligned_unique_"],
                "require_content_conflict_policy": True,
            },
            "datasets": {
                DATASET_ID: {
                    "manifest": str(manifest_path.relative_to(tmp_path)),
                    "duplicate_audit": str(duplicate_path.relative_to(tmp_path)),
                    "content_conflict_policy": str(policy_path.relative_to(tmp_path)),
                    "dataset_role": "synthetic_test",
                }
            },
        },
    )
    return {
        "root": tmp_path,
        "schema": schema,
        "registry": registry_path,
        "manifest": manifest_path,
        "policy": policy_path,
        "captures": captures,
        "rows": rows,
    }


def open_fixture(fixture: dict[str, object]) -> UnifiedDatasetLoader:
    return UnifiedDatasetLoader.open(
        output_root=fixture["root"],
        schema_path=SCHEMA_PATH,
        feature_views_path=FEATURE_VIEWS_PATH,
        policy_registry_path=fixture["registry"],
        dataset_id=DATASET_ID,
        integrity="sha256",
        row_validation="full",
    )


def test_loader_executes_manifest_schema_label_and_conflict_contracts(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    loader = open_fixture(fixture)
    strategy = loader.strategy()
    rows = list(strategy.iter_eligible_rows())
    assert len(rows) == 5
    assert token("ddos-conflict") not in {row["sample_id"] for row in rows}
    assert strategy.last_load_audit.raw_rows == 6
    assert strategy.last_load_audit.excluded_rows == {"cross_label_model_content": 1}
    assert loader.metadata_report()["gate_pass"] is True


def test_strategy_groups_duplicate_captures_and_isolates_unknown_family(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    loader = open_fixture(fixture)
    strategy = loader.strategy()
    split = strategy.build_split_plan(
        unknown_families=("DDoS",),
        seed=17,
        train_ratio=0.5,
        validation_ratio=0.25,
        test_ratio=0.25,
    )
    captures = fixture["captures"]
    assert split.partition_for(captures["a"]) == split.partition_for(captures["b"])
    assert split.partition_for(captures["e"]) == "unknown_test"
    assert "DDoS" not in {
        record.row["family_label"]
        for record in strategy.iter_records(
            split, partitions=("train", "known_validation", "known_test")
        )
    }
    assert split.summary["group_leakage_count"] == 0
    split_path = tmp_path / "split.json"
    write_json(split_path, split.to_dict())
    reloaded = SplitPlan.load(split_path)
    assert reloaded.split_plan_sha256 == split.split_plan_sha256
    assert reloaded.assignments == split.assignments


def test_three_modality_projection_contains_no_forbidden_columns(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    loader = open_fixture(fixture)
    row = next(loader.strategy().iter_eligible_rows())
    views = loader.materializer.materialize(row)
    assert set(views) == {
        "payload_semantics",
        "packet_behavior",
        "packet_interaction_graph",
    }
    assert views["payload_semantics"]["payload_b64"] == b"\x01\x02\x03\x04"
    assert len(views["packet_interaction_graph"]["nodes"]) == 3
    assert views["packet_interaction_graph"]["edges"]
    projected = set(views["payload_semantics"]) | set(views["packet_behavior"])
    assert not projected.intersection(loader.feature_views.forbidden_columns)


def test_sampler_is_train_only_bounded_and_order_independent() -> None:
    rows = [
        {
            "sample_id": token(f"sample-{index}"),
            "capture_id": token(f"capture-{index // 2}"),
            "flow_key_hash": token(f"flow-{index}"),
            "family_label": "A" if index < 8 else "B",
        }
        for index in range(12)
    ]
    records = [RawDataRecord(DATASET_ID, "train", row) for row in rows]
    sampler = TrainOnlySampler(TrainingSamplingPolicy(seed=9, default_class_cap=3))
    forward = sampler.select(records)
    reverse = sampler.select(reversed(records))
    assert [record.sample_id for record in forward.records] == [
        record.sample_id for record in reverse.records
    ]
    assert forward.audit["selected_rows_by_class"] == {"A": 3, "B": 3}
    with pytest.raises(DataContractError, match="train-only sampler"):
        sampler.select([RawDataRecord(DATASET_ID, "known_validation", rows[0])])


def test_stale_content_policy_is_rejected(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    policy_path = fixture["policy"]
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["dataset_manifest_sha256"] = "0" * 64
    policy.pop("policy_sha256")
    write_json(policy_path, with_hash(policy, "policy_sha256"))
    with pytest.raises(DataContractError, match="stale"):
        open_fixture(fixture)

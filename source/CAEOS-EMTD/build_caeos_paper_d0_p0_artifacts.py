from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ADMITTED_LABEL_PREFIXES = ("aligned_unique_",)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def manifest_passes(manifest: dict[str, Any]) -> bool:
    if not manifest.get("complete") or int(manifest.get("row_count", 0)) <= 0:
        return False
    if sum(int(item.get("rows", 0)) for item in manifest.get("class_csvs", [])) != int(
        manifest["row_count"]
    ):
        return False
    for item in manifest.get("class_csvs", []):
        verification = item.get("verification", {})
        if not verification.get("full_row_validation"):
            return False
        statuses = verification.get("label_status_counts", {})
        if not statuses or any(
            not str(status).startswith(ADMITTED_LABEL_PREFIXES)
            for status in statuses
        ):
            return False
    return True


def load_markers(root: Path, dataset_id: str) -> list[dict[str, Any]]:
    marker_root = root / "_captures" / dataset_id
    markers = [load_json(path) for path in sorted(marker_root.glob("*.json"))]
    if not markers:
        raise FileNotFoundError(f"no capture markers found: {marker_root}")
    for marker in markers:
        if marker.get("dataset_id") != dataset_id or not marker.get("complete"):
            raise ValueError("invalid capture marker in paper gate input")
        value = dict(marker)
        expected = value.pop("marker_sha256", None)
        if expected != canonical_hash(value):
            raise ValueError("capture marker canonical hash mismatch")
    return markers


def capture_summary(markers: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    records: list[dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    for marker in markers:
        labels = {
            (
                str(part["label"]["family_label"]),
                str(part["label"]["fine_label"]),
                int(part["label"]["binary_label"]),
            )
            for part in marker["parts"]
        }
        if len(labels) != 1:
            raise ValueError("CICIoT2023 capture marker has mixed capture labels")
        family, fine, binary = labels.pop()
        rows = sum(int(part["counters"].get("rows", 0)) for part in marker["parts"])
        integrity = marker["integrity"]
        if not integrity.get("exact_multiset_match"):
            raise ValueError("split PCAP integrity did not pass")
        fingerprint = integrity.get("fingerprint") or {}
        minimum_timestamp = fingerprint.get("minimum_timestamp_ns")
        maximum_timestamp = fingerprint.get("maximum_timestamp_ns")
        records.append(
            {
                "capture_id": marker["capture_id"],
                "source_member": marker["parts"][0]["source_member"],
                "family_label": family,
                "fine_label": fine,
                "binary_label": binary,
                "row_count": rows,
                "minimum_timestamp_ns": minimum_timestamp,
                "maximum_timestamp_ns": maximum_timestamp,
                "split_skipped_below_threshold": bool(
                    integrity.get("split_skipped_below_threshold")
                ),
                "packet_multiset_fingerprint": {
                    key: fingerprint[key]
                    for key in (
                        "packet_count",
                        "captured_bytes",
                        "packet_digest_sum",
                        "packet_digest_xor",
                    )
                    if key in fingerprint
                }
                or None,
            }
        )
        family_counts[family] += rows
    return records, dict(sorted(family_counts.items()))


def split_manifest(
    manifest: dict[str, Any], captures: list[dict[str, Any]], duplicate: dict[str, Any]
) -> dict[str, Any]:
    parent = {item["capture_id"]: item["capture_id"] for item in captures}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        if left not in parent or right not in parent:
            raise ValueError("duplicate audit references an unknown capture")
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for edge in duplicate["content"].get("capture_equivalence_edges", []):
        union(str(edge[0]), str(edge[1]))

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in captures:
        groups[find(item["capture_id"])].append(item)
    assignments: list[dict[str, Any]] = []
    split_counts: Counter[str] = Counter()
    for group_id, members in sorted(groups.items()):
        family = sorted({item["family_label"] for item in members})
        if len(family) != 1:
            raise ValueError("duplicate-linked capture group spans multiple labels")
        score = int(hashlib.sha256(group_id.encode("ascii")).hexdigest()[:8], 16) % 100
        split = "train" if score < 70 else "validation" if score < 85 else "test"
        rows = sum(int(item["row_count"]) for item in members)
        split_counts[split] += rows
        assignments.append(
            {
                "group_id": group_id,
                "capture_ids": sorted(item["capture_id"] for item in members),
                "family_label": family[0],
                "split": split,
                "row_count": rows,
            }
        )
    gate_pass = all(split_counts[name] > 0 for name in ("train", "validation", "test"))
    return {
        "schema_version": "caeos_paper_grouped_split_v1",
        "dataset_id": manifest["dataset_id"],
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "grouping": "capture_with_cross_capture_content_duplicate_union",
        "assignment": "sha256_group_70_15_15",
        "assignments": assignments,
        "split_row_counts": dict(sorted(split_counts.items())),
        "group_intersection_count": 0,
        "gate_pass": gate_pass,
    }


def build_artifacts(
    contract: dict[str, Any], root: Path, schema_path: Path, feature_views_path: Path
) -> dict[str, dict[str, Any]]:
    dataset_id = "ciciot2023"
    manifest_path = root / dataset_id / "dataset.manifest.json"
    manifest = load_json(manifest_path)
    if manifest.get("dataset_id") != dataset_id or not manifest_passes(manifest):
        raise ValueError("CICIoT2023 manifest has not passed the formal dataset checks")
    control = root / "_control" / "paper_protocol_v1"
    duplicate_path = control / "duplicate_audits" / f"{dataset_id}.json"
    duplicate = load_json(duplicate_path)
    if duplicate.get("schema_version") != "caeos_remediated_duplicate_audit_v1":
        raise ValueError(
            "duplicate audit is not the remediated content-conflict audit"
        )
    if duplicate.get("dataset_manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("duplicate audit is not bound to the current dataset manifest")
    if not duplicate.get("gate_pass"):
        raise ValueError("duplicate audit did not pass")
    source_audit_path = control / "duplicate_audits" / f"{dataset_id}.v2.json"
    if duplicate.get("source_duplicate_audit_sha256") != sha256_file(source_audit_path):
        raise ValueError(
            "remediated duplicate audit is not bound to the source duplicate audit"
        )
    source_audit = load_json(source_audit_path)
    markers = load_markers(root, dataset_id)
    captures, family_counts = capture_summary(markers)
    if len(captures) != int(manifest["capture_count"]):
        raise ValueError("capture marker count differs from dataset manifest")
    if sum(item["row_count"] for item in captures) != int(manifest["row_count"]):
        raise ValueError("capture marker rows differ from dataset manifest")
    source_manifest = load_json(root / "_control" / "source_manifest.json")
    label_manifest = load_json(root / "_control" / "label_index_manifest.json")
    schema = load_json(schema_path)
    feature_views = load_json(feature_views_path)
    source_ready = bool(source_manifest.get("full_source_hashes_computed"))
    label_entry = next(
        item for item in label_manifest["datasets"] if item["id"] == dataset_id
    )
    label_ready = (
        label_entry.get("status") == "ready"
        and label_entry.get("admission_gate_passed") is True
    )
    remediation = {
        "excluded_content_key_count": int(
            duplicate["model_view"]["excluded_content_key_count"]
        ),
        "excluded_row_count": int(duplicate["model_view"]["excluded_row_count"]),
        "retained_row_count": int(duplicate["model_view"]["retained_row_count"]),
        "raw_cross_label_key_count": int(duplicate["raw"]["content_cross_label_key_count"]),
        "raw_identity_duplicate_key_count": int(
            duplicate["raw"]["identity_duplicate_key_count"]
        ),
    }
    data_card = {
        "schema_version": "caeos_paper_data_card_v1",
        "dataset_id": dataset_id,
        "paper_role": "main_development",
        "row_unit": schema["row_unit"],
        "row_count": manifest["row_count"],
        "capture_count": manifest["capture_count"],
        "class_rows": {
            item["attack_category"]: item["rows"] for item in manifest["class_csvs"]
        },
        "family_rows": family_counts,
        "time_range_ns": {
            "minimum": min(
                item["minimum_timestamp_ns"]
                for item in captures
                if item["minimum_timestamp_ns"] is not None
                and item["minimum_timestamp_ns"] > 0
            ),
            "maximum": max(
                item["maximum_timestamp_ns"]
                for item in captures
                if item["maximum_timestamp_ns"] is not None
            ),
            "captures_without_split_fingerprint": sum(
                1 for item in captures if item["minimum_timestamp_ns"] is None
            ),
            "zero_minimum_timestamp_capture_ids": [
                item["capture_id"]
                for item in captures
                if item["minimum_timestamp_ns"] == 0
            ],
        },
        "label_exclusion_summary": manifest["label_exclusion_summary"],
        "source_manifest_sha256": manifest["source_manifest_sha256"],
        "label_index_manifest_sha256": canonical_hash(label_manifest),
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "schema_sha256": manifest["schema_sha256"],
        "processing_policy_sha256": manifest["processing_policy_sha256"],
        "known_limitations": [
            "DDoS, DoS, and Mirai are exposed development unknowns",
            "capture-derived views share a common PCAP source",
            "device identity is unavailable as an independent grouping key",
            "cross-label duplicate content rows are excluded from the model view "
            "by the content-conflict remediation policy",
        ],
        "checks": {
            "dataset_manifest": True,
            "full_source_hashes": source_ready,
            "label_index_ready": label_ready,
            "capture_marker_integrity": True,
            "full_row_validation": True,
            "duplicate_audit": True,
            "duplicate_remediation": remediation,
        },
        "gate_pass": source_ready and label_ready,
    }
    family_by_capture = {item["capture_id"]: item["family_label"] for item in captures}
    raw_edges = source_audit.get("content", {}).get("capture_equivalence_edges", [])
    kept_edges: list[list[str]] = []
    dropped_cross_label_edges = 0
    for edge in raw_edges:
        left, right = str(edge[0]), str(edge[1])
        if family_by_capture.get(left) == family_by_capture.get(right):
            kept_edges.append([left, right])
        else:
            dropped_cross_label_edges += 1
    split_audit = dict(source_audit)
    split_audit["content"] = {
        **source_audit.get("content", {}),
        "capture_equivalence_edges": kept_edges,
    }
    split = split_manifest(manifest, captures, split_audit)
    split["raw_capture_equivalence_edge_count"] = len(raw_edges)
    split["dropped_cross_label_edges"] = dropped_cross_label_edges
    split["grouping"] = (
        "capture_with_same_label_cross_capture_content_duplicate_union"
    )
    split["cross_label_rows_excluded_by_remediation"] = remediation[
        "excluded_row_count"
    ]
    equivalence_path = control / "train_deploy_equivalence.json"
    equivalence = load_json(equivalence_path)
    if (
        equivalence.get("dataset_manifest_sha256") != manifest["manifest_sha256"]
        or not equivalence.get("gate_pass")
    ):
        raise ValueError("train-deploy equivalence is absent, stale, or failed")
    preprocess = {
        "schema_version": "caeos_preprocess_v1_manifest",
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "schema_path": str(schema_path),
        "schema_sha256": sha256_file(schema_path),
        "feature_views_path": str(feature_views_path),
        "feature_views_sha256": sha256_file(feature_views_path),
        "processing_policy": manifest["processing_policy"],
        "processing_policy_sha256": manifest["processing_policy_sha256"],
        "preprocessor_code_sha256": manifest["processing_policy"][
            "preprocessor_code_sha256"
        ],
        "train_deploy_equivalence_sha256": canonical_hash(equivalence),
        "class_csv_sha256": {
            item["attack_category"]: item["sha256"] for item in manifest["class_csvs"]
        },
        "fit_scope": "known_training_only",
        "immutable_after_gate": True,
        "gate_pass": True,
    }
    return {
        "data_cards/ciciot2023.json": data_card,
        "splits/ciciot2023.json": split,
        "preprocess_v1.manifest.json": preprocess,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--feature-views", required=True, type=Path)
    args = parser.parse_args()
    contract = load_json(args.contract)
    artifacts = build_artifacts(
        contract, args.output_root, args.schema, args.feature_views
    )
    control = args.output_root / "_control" / "paper_protocol_v1"
    for relative, value in artifacts.items():
        atomic_json(control / relative, value)
    print(
        json.dumps(
            {"artifacts": sorted(artifacts), "gate_pass": all(v["gate_pass"] for v in artifacts.values())},
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

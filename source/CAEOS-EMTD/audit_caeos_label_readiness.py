from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json
from prepare_caeos_unified_multimodal_csv import load_json, path_label, validate_source_manifest


BLOCKING_STATUS_TOKENS = ("pending", "unmapped", "unresolved", "deferred")


def audit_dataset(dataset: dict[str, Any], source_dataset: dict[str, Any]) -> dict[str, Any]:
    statuses: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    binary_labels: Counter[int] = Counter()
    examples: dict[str, list[str]] = {}
    capture_count = 0
    for source in source_dataset["source_files"]:
        members = source.get("capture_members") or [None]
        for member_record in members:
            member = member_record["name"] if isinstance(member_record, dict) else None
            source_member = (
                member
                if member is not None
                else str(Path(source["path"]).relative_to(Path(dataset["source_root"])))
            )
            label = path_label(dataset, source_member)
            statuses[label.status] += 1
            categories[label.attack_category] += 1
            binary_labels[label.binary_label] += 1
            capture_count += 1
            if any(token in label.status.lower() for token in BLOCKING_STATUS_TOKENS):
                examples.setdefault(label.status, [])
                if len(examples[label.status]) < 5:
                    examples[label.status].append(source_member)
    blocking = sum(
        count
        for status, count in statuses.items()
        if any(token in status.lower() for token in BLOCKING_STATUS_TOKENS)
    )
    return {
        "id": dataset["id"],
        "label_policy": dataset["label_policy"],
        "capture_count": capture_count,
        "formal_capture_count": capture_count - blocking,
        "blocking_capture_count": blocking,
        "formal_label_ready": capture_count > 0 and blocking == 0,
        "label_status_counts": dict(sorted(statuses.items())),
        "attack_category_counts": dict(sorted(categories.items())),
        "binary_label_counts": {str(key): value for key, value in sorted(binary_labels.items())},
        "blocking_examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    catalog = load_json(args.catalog)
    source_manifest = load_json(args.source_manifest)
    validate_source_manifest(catalog, source_manifest)
    catalog_by_id = {item["id"]: item for item in catalog["datasets"]}
    records = [
        audit_dataset(catalog_by_id[item["id"]], item)
        for item in source_manifest["datasets"]
    ]
    result = {
        "schema_version": "caeos_label_readiness_audit_v1",
        "dataset_count": len(records),
        "formal_label_ready_dataset_count": sum(item["formal_label_ready"] for item in records),
        "datasets": records,
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

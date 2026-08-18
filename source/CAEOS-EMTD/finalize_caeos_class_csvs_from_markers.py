from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import prepare_caeos_splitpcap_class_csv as orchestrator
from caeos_unified_dataset import atomic_json, canonical_json_hash, sha256_file


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_rows_by_category(markers: list[dict[str, Any]]) -> dict[str, int]:
    rows: dict[str, int] = {}
    for marker in markers:
        marker_rows = 0
        for part in marker["parts"]:
            count = int(part["counters"]["rows"])
            label = part["label"]
            record = orchestrator._preprocessor.LabelRecord(
                str(label["status"]),
                str(label["fine_label"]),
                str(label["family_label"]),
                int(label["binary_label"]),
            )
            category = record.attack_category
            if category not in orchestrator.ATTACK_CATEGORIES or category == "Pending":
                raise ValueError(f"non-formal marker category: {category}")
            rows[category] = rows.get(category, 0) + count
            marker_rows += count
        if marker_rows != int(marker["rows"]):
            raise ValueError(f"marker row count mismatch: {marker['capture_id']}")
    return rows


def file_for_category(dataset_dir: Path, category: str) -> tuple[Path, Path]:
    final_path = dataset_dir / f"{category}.csv"
    partial_path = dataset_dir / f"{category}.csv.partial"
    existing = [path for path in (final_path, partial_path) if path.is_file()]
    if len(existing) != 1:
        raise ValueError(
            f"expected exactly one final or partial CSV for {category}: {existing}"
        )
    return existing[0], final_path


def checkpoint_matches(item: dict[str, Any], source_path: Path) -> bool:
    stat = source_path.stat()
    return (
        item.get("source_path") == str(source_path)
        and int(item.get("size_bytes", -1)) == stat.st_size
        and int(item.get("mtime_ns", -1)) == stat.st_mtime_ns
        and bool(item.get("verification", {}).get("full_row_validation"))
        and len(str(item.get("sha256", ""))) == 64
    )


def validate_category(
    category: str,
    source_path: Path,
    final_path: Path,
    columns: list[str],
    expected_rows: int,
    row_workers: int,
    batch_rows: int,
) -> dict[str, Any]:
    verification, digest = orchestrator.verify_csv_and_sha256_parallel(
        source_path,
        columns,
        expected_rows,
        require_formal_labels=True,
        workers=row_workers,
        batch_rows=batch_rows,
    )
    stat = source_path.stat()
    return {
        "attack_category": category,
        "source_path": str(source_path),
        "path": str(final_path),
        "rows": expected_rows,
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": digest,
        "verification": verification,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--label-index-manifest", required=True, type=Path)
    parser.add_argument("--pcap-repair-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--completion-path", required=True, type=Path)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--class-workers", type=int, default=2)
    parser.add_argument("--row-workers", type=int, default=4)
    parser.add_argument("--batch-rows", type=int, default=2048)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if min(args.class_workers, args.row_workers, args.batch_rows) < 1:
        raise ValueError("worker and batch values must be positive")

    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    label_index_manifest = load_json(args.label_index_manifest)
    dataset = next(item for item in catalog["datasets"] if item["id"] == args.dataset)
    source_dataset = next(
        item for item in source_manifest["datasets"] if item["id"] == args.dataset
    )
    alignment = next(
        item
        for item in label_index_manifest["datasets"]
        if item["id"] == args.dataset
    )
    if alignment.get("status") != "ready":
        raise ValueError("formal label index is not ready")
    index_path = Path(alignment["path"])
    if not index_path.is_file() or sha256_file(index_path) != alignment["sha256"]:
        raise ValueError("label index identity mismatch")

    marker_dir = args.output_root / "_captures" / args.dataset
    markers = [load_json(path) for path in sorted(marker_dir.glob("*.json"))]
    allowlist = orchestrator.capture_member_allowlist(alignment, args.dataset)
    selected, scheduling_scope = orchestrator.select_capture_candidates(
        dataset, source_dataset, allowlist
    )
    if len(markers) != len(selected):
        raise ValueError(f"marker coverage mismatch: {len(markers)} != {len(selected)}")
    if allowlist is not None and len(markers) != len(allowlist):
        raise ValueError(f"allowlist coverage mismatch: {len(markers)} != {len(allowlist)}")

    all_parts = [part for marker in markers for part in marker["parts"]]
    policy_hashes = {str(part["processing_policy_sha256"]) for part in all_parts}
    if len(policy_hashes) != 1:
        raise ValueError(f"mixed marker processing policies: {policy_hashes}")
    policy = all_parts[0]["processing_policy"]
    policy_hash = next(iter(policy_hashes))
    if canonical_json_hash(policy) != policy_hash:
        raise ValueError("marker processing policy identity mismatch")
    schema_hash = canonical_json_hash(schema)
    if any(part["schema_sha256"] != schema_hash for part in all_parts):
        raise ValueError("marker schema identity mismatch")

    dataset_dir = args.output_root / args.dataset
    expected = expected_rows_by_category(markers)
    paths = {
        category: file_for_category(dataset_dir, category)
        for category in sorted(expected)
    }
    plan = {
        "dataset_id": args.dataset,
        "capture_count": len(markers),
        "row_count": sum(expected.values()),
        "class_workers": min(args.class_workers, len(expected)),
        "row_workers_per_class": args.row_workers,
        "batch_rows": args.batch_rows,
        "classes": [
            {
                "attack_category": category,
                "rows": expected[category],
                "source_path": str(paths[category][0]),
                "size_bytes": paths[category][0].stat().st_size,
            }
            for category in sorted(expected)
        ],
    }
    print(json.dumps({"event": "finalization_plan", **plan}, sort_keys=True), flush=True)
    if args.plan_only:
        return

    checkpoint = load_json(args.checkpoint) if args.checkpoint.is_file() else {}
    completed = dict(checkpoint.get("completed", {}))
    results: dict[str, dict[str, Any]] = {}
    tasks = []
    for category, (source_path, final_path) in paths.items():
        saved = completed.get(category)
        if isinstance(saved, dict) and checkpoint_matches(saved, source_path):
            results[category] = saved
            continue
        tasks.append(
            (
                category,
                source_path,
                final_path,
                [item["name"] for item in schema["columns"]],
                expected[category],
                args.row_workers,
                args.batch_rows,
            )
        )
    tasks.sort(key=lambda item: item[1].stat().st_size, reverse=True)

    with ThreadPoolExecutor(max_workers=min(args.class_workers, len(tasks) or 1)) as pool:
        futures = {pool.submit(validate_category, *task): task[0] for task in tasks}
        for future in as_completed(futures):
            category = futures[future]
            results[category] = future.result()
            completed[category] = results[category]
            atomic_json(
                args.checkpoint,
                {
                    "schema_version": "caeos_parallel_class_finalization_checkpoint_v1",
                    "dataset_id": args.dataset,
                    "processing_policy_sha256": policy_hash,
                    "schema_sha256": schema_hash,
                    "completed": completed,
                },
            )
            print(
                json.dumps(
                    {"event": "class_validated", "attack_category": category},
                    sort_keys=True,
                ),
                flush=True,
            )

    if set(results) != set(expected):
        raise ValueError("not all classes completed validation")
    for category in sorted(results):
        source_path, final_path = paths[category]
        if source_path != final_path:
            os.replace(source_path, final_path)

    class_csvs = []
    for category in sorted(results):
        item = dict(results[category])
        item.pop("source_path", None)
        item.pop("mtime_ns", None)
        item["path"] = str(paths[category][1])
        class_csvs.append(item)
    manifest = {
        "schema_version": "caeos_dataset_class_csv_manifest_v1",
        "dataset_id": args.dataset,
        "dataset_role": dataset["role"],
        "schema_sha256": schema_hash,
        "source_manifest_sha256": source_manifest["manifest_sha256"],
        "processing_policy": policy,
        "processing_policy_sha256": policy_hash,
        "scheduling_scope": scheduling_scope,
        "capture_count": len(markers),
        "row_count": sum(expected.values()),
        "label_exclusion_summary": orchestrator.aggregate_label_exclusion(markers),
        "official_label_precedence_summary": None,
        "class_csvs": class_csvs,
        "finalization": {
            "class_parallelism": min(args.class_workers, len(expected)),
            "row_validation_parallelism_per_class": args.row_workers,
            "row_validation_batch_rows": args.batch_rows,
            "full_validation": True,
            "sha256": True,
            "validation_and_sha256_single_pass": True,
            "single_sequential_read_per_class": True,
            "all_classes_validated_before_rename": True,
            "resumed_from_persisted_capture_markers": True,
        },
        "complete": True,
        "reused": False,
    }
    manifest["manifest_sha256"] = canonical_json_hash(manifest)
    atomic_json(dataset_dir / "dataset.manifest.json", manifest)

    completion = {
        "schema_version": "caeos_split_class_preprocessing_completion_v1",
        "catalog_sha256": canonical_json_hash(catalog),
        "schema_sha256": schema_hash,
        "source_manifest_sha256": source_manifest["manifest_sha256"],
        "pcap_repair_manifest_sha256_at_start": sha256_file(
            args.pcap_repair_manifest
        ),
        "processing_policy_sha256_by_dataset": {args.dataset: policy_hash},
        "label_index_manifest_sha256": canonical_json_hash(label_index_manifest),
        "datasets": [manifest],
        "dataset_count": 1,
        "all_complete": True,
    }
    completion["completion_sha256"] = canonical_json_hash(completion)
    atomic_json(args.completion_path, completion)
    atomic_json(
        args.checkpoint,
        {
            "schema_version": "caeos_parallel_class_finalization_checkpoint_v1",
            "dataset_id": args.dataset,
            "processing_policy_sha256": policy_hash,
            "schema_sha256": schema_hash,
            "completed": completed,
            "all_complete": True,
            "dataset_manifest_sha256": manifest["manifest_sha256"],
            "completion_sha256": completion["completion_sha256"],
        },
    )
    print(
        json.dumps(
            {
                "event": "dataset_finalized",
                "dataset_id": args.dataset,
                "row_count": manifest["row_count"],
                "class_csv_count": len(class_csvs),
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

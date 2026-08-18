from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json
from prepare_caeos_unified_multimodal_csv import load_json


LABEL_MEMBER_SUFFIXES = {".csv", ".log", ".json", ".jsonl", ".txt", ".tsv", ".parquet"}


def member_record(name: str, size_bytes: int) -> dict[str, Any] | None:
    if Path(name).suffix.lower() not in LABEL_MEMBER_SUFFIXES:
        return None
    return {"name": name, "suffix": Path(name).suffix.lower(), "size_bytes": size_bytes}


def inspect_archive(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                record = None if info.is_dir() else member_record(info.filename, info.file_size)
                if record is not None:
                    records.append(record)
    return records


def audit_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    root = Path(dataset.get("label_search_root", dataset["source_root"]))
    archives = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name.lower().endswith(".zip")
    )
    archive_records = []
    errors = []
    for path in archives:
        try:
            members = inspect_archive(path)
        except Exception as error:
            errors.append({"path": str(path), "error": repr(error)})
            continue
        if members:
            archive_records.append(
                {
                    "path": str(path),
                    "relative_path": str(path.relative_to(root)),
                    "size_bytes": path.stat().st_size,
                    "label_candidate_member_count": len(members),
                    "label_candidate_member_bytes": sum(item["size_bytes"] for item in members),
                    "members": members,
                }
            )
    return {
        "id": dataset["id"],
        "archive_count": len(archives),
        "archive_with_label_candidate_count": len(archive_records),
        "label_candidate_member_count": sum(item["label_candidate_member_count"] for item in archive_records),
        "archives": archive_records,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    catalog = load_json(args.catalog)
    datasets = [audit_dataset(item) for item in catalog["datasets"] if item["preprocess_enabled"]]
    result = {
        "schema_version": "caeos_label_archive_audit_v1",
        "datasets": datasets,
        "dataset_count": len(datasets),
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

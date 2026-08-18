from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json
from prepare_caeos_unified_multimodal_csv import load_json


LABEL_SUFFIXES = {".csv", ".log", ".json", ".jsonl", ".txt", ".tsv", ".parquet"}


def header_preview(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {}
    if path.suffix.lower() not in {".csv", ".tsv", ".log", ".txt"}:
        return record
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            line = handle.readline(16384).strip("\r\n")
        record["first_line"] = line[:4096]
        if path.suffix.lower() in {".csv", ".tsv"} and line:
            dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
            record["header_fields"] = next(csv.reader([line], dialect=dialect))[:256]
    except OSError as error:
        record["preview_error"] = repr(error)
    return record


def audit_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    root = Path(dataset.get("label_search_root", dataset["source_root"]))
    if not root.is_dir():
        return {"id": dataset["id"], "label_search_root": str(root), "status": "missing"}
    candidates = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in LABEL_SUFFIXES
    )
    records = []
    for path in candidates:
        record = {
            "path": str(path),
            "relative_path": str(path.relative_to(root)),
            "suffix": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
        }
        record.update(header_preview(path))
        records.append(record)
    return {
        "id": dataset["id"],
        "label_search_root": str(root.resolve()),
        "status": "candidates_found" if records else "no_label_candidate",
        "candidate_file_count": len(records),
        "candidate_size_bytes": sum(item["size_bytes"] for item in records),
        "candidates": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    catalog = load_json(args.catalog)
    datasets = [audit_dataset(item) for item in catalog["datasets"] if item["preprocess_enabled"]]
    result = {
        "schema_version": "caeos_label_asset_audit_v1",
        "dataset_count": len(datasets),
        "dataset_with_candidates_count": sum(item["status"] == "candidates_found" for item in datasets),
        "datasets": datasets,
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

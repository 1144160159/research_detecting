from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "caeos_split_class_preprocessing_completion_v1"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_embedded_hash(value: dict[str, Any], field: str) -> str:
    observed = str(value.get(field, ""))
    unsigned = json.loads(json.dumps(value))
    unsigned.pop(field, None)
    expected = canonical_json_hash(unsigned)
    if observed != expected:
        raise ValueError(f"invalid embedded {field}: {observed} != {expected}")
    return observed


def atomic_json(path: Path, value: Any) -> None:
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


def verify_class_csv(item: dict[str, Any]) -> dict[str, Any]:
    path = Path(item["path"])
    if not path.is_file():
        raise FileNotFoundError(f"class CSV absent: {path}")
    size = path.stat().st_size
    if size != int(item["size_bytes"]):
        raise ValueError(f"class CSV size differs from manifest: {path}")
    observed = sha256_file(path)
    if observed != item["sha256"]:
        raise ValueError(f"class CSV SHA-256 differs from manifest: {path}")
    verification = item.get("verification", {})
    if verification.get("full_row_validation") is not True:
        raise ValueError(f"class CSV lacks full row validation: {path}")
    if int(verification.get("rows", -1)) != int(item["rows"]):
        raise ValueError(f"class CSV validation row count differs: {path}")
    return {
        "attack_category": item["attack_category"],
        "path": str(path),
        "size_bytes": size,
        "rows": int(item["rows"]),
        "sha256": observed,
    }


def rebuild_completion(
    manifest_path: Path,
    template_path: Path,
    output_path: Path,
    workers: int,
) -> dict[str, Any]:
    if workers < 1 or workers > 16:
        raise ValueError("workers must be between 1 and 16")
    manifest = load_json(manifest_path)
    template = load_json(template_path)
    verified_embedded_hash(manifest, "manifest_sha256")
    verified_embedded_hash(template, "completion_sha256")
    if manifest.get("complete") is not True:
        raise ValueError("dataset manifest is not complete")
    if template.get("all_complete") is not True:
        raise ValueError("template completion is not complete")
    if template.get("schema_sha256") != manifest.get("schema_sha256"):
        raise ValueError("template and manifest schema hashes differ")
    if template.get("source_manifest_sha256") != manifest.get("source_manifest_sha256"):
        raise ValueError("template and manifest source manifest hashes differ")
    started = time.time()
    class_items = list(manifest.get("class_csvs", []))
    if not class_items:
        raise ValueError("dataset manifest has no class CSVs")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=min(workers, len(class_items))
    ) as executor:
        verified = list(executor.map(verify_class_csv, class_items))
    if sum(item["rows"] for item in verified) != int(manifest["row_count"]):
        raise ValueError("verified class rows differ from dataset manifest")
    completion = {
        "schema_version": SCHEMA_VERSION,
        "catalog_sha256": template["catalog_sha256"],
        "schema_sha256": manifest["schema_sha256"],
        "source_manifest_sha256": manifest["source_manifest_sha256"],
        "processing_policy_sha256_by_dataset": {
            manifest["dataset_id"]: manifest["processing_policy_sha256"]
        },
        "label_index_manifest_sha256": template["label_index_manifest_sha256"],
        "datasets": [manifest],
        "dataset_count": 1,
        "all_complete": True,
        "completion_reconstruction": {
            "reason": "missing_feature_extraction_completion_wrapper",
            "dataset_manifest_path": str(manifest_path),
            "dataset_manifest_sha256": manifest["manifest_sha256"],
            "template_completion_path": str(template_path),
            "template_completion_sha256": template["completion_sha256"],
            "class_csv_count": len(verified),
            "class_csv_rows": sum(item["rows"] for item in verified),
            "class_csv_bytes": sum(item["size_bytes"] for item in verified),
            "class_csv_hashes_recomputed": True,
            "full_row_validation_reused_from_bound_manifest": True,
            "workers": min(workers, len(class_items)),
            "elapsed_seconds": time.time() - started,
        },
    }
    if "pcap_repair_manifest_sha256_at_start" in template:
        completion["pcap_repair_manifest_sha256_at_start"] = template[
            "pcap_repair_manifest_sha256_at_start"
        ]
    completion["completion_sha256"] = canonical_json_hash(completion)
    if output_path.exists():
        existing = load_json(output_path)
        verified_embedded_hash(existing, "completion_sha256")
        if existing != completion:
            raise ValueError(f"refusing to overwrite a different completion: {output_path}")
        return existing
    atomic_json(output_path, completion)
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-manifest", required=True, type=Path)
    parser.add_argument("--template-completion", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    completion = rebuild_completion(
        args.dataset_manifest, args.template_completion, args.output, args.workers
    )
    print(
        json.dumps(
            {
                "dataset_id": completion["datasets"][0]["dataset_id"],
                "all_complete": completion["all_complete"],
                "completion_sha256": completion["completion_sha256"],
                "workers": completion["completion_reconstruction"]["workers"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()

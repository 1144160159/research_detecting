from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from caeos_unified_dataset import canonical_json_hash, sha256_file
from prepare_caeos_splitpcap_class_csv import (
    cleanup_dataset_intermediates,
    merge_class_csvs,
    process_original_capture,
    processing_policy,
)
from prepare_caeos_unified_multimodal_csv import load_json, tshark_identity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--splitpcap-binary", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    args = parser.parse_args()
    if args.work_root.exists():
        raise ValueError(f"refusing existing benchmark work root: {args.work_root}")
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    dataset = next(item for item in catalog["datasets"] if item["id"] == args.dataset)
    source_dataset = next(item for item in source_manifest["datasets"] if item["id"] == args.dataset)
    source = next(
        item for item in source_dataset["source_files"] if Path(item["path"]) == args.source
    )
    decoder_identity = tshark_identity(args.tshark_binary)
    code_sha256 = sha256_file(PROJECT_ROOT / "prepare_caeos_unified_multimodal_csv.py")
    policy = processing_policy(
        catalog["feature_reservoir"],
        6000,
        "tshark",
        decoder_identity,
        0,
        code_sha256,
        args.splitpcap_binary,
        "fca18e270fe49d0cf1ba37ffd2bab901a797401a",
        128 * 1024 * 1024,
    )
    runtime = SimpleNamespace(
        split_threshold_bytes=256 * 1024 * 1024,
        target_piece_bytes=128 * 1024 * 1024,
        maximum_pieces_per_capture=256,
        splitpcap_binary=args.splitpcap_binary,
        cpu_worker_cap=24,
        memory_budget_gib=190.0,
        memory_reserve_gib=46.0,
        estimated_worker_gib=6.0,
        memory_safety_factor=2.0,
        maximum_active_flows=6000,
        packet_decoder="tshark",
        tshark_binary=args.tshark_binary,
        packet_decoder_identity=decoder_identity,
        tshark_session_reset_packets=0,
    )
    started = time.time()
    try:
        marker = process_original_capture(
            dataset,
            source,
            None,
            runtime,
            args.work_root,
            schema,
            catalog["feature_reservoir"],
            policy,
        )
        summary = merge_class_csvs(
            dataset,
            [marker],
            args.work_root,
            [item["name"] for item in schema["columns"]],
            canonical_json_hash(schema),
            source_manifest["manifest_sha256"],
            policy,
            {
                "candidate_capture_count": 1,
                "candidate_capture_bytes": args.source.stat().st_size,
                "scheduled_capture_count": 1,
                "scheduled_capture_bytes": args.source.stat().st_size,
                "excluded_capture_count": 0,
                "excluded_capture_bytes": 0,
                "excluded_capture_fraction": 0.0,
                "excluded_reason_counts": {},
                "excluded_sources": [],
                "excluded_sources_sha256": canonical_json_hash([]),
            },
        )
        cleanup_dataset_intermediates(args.work_root, args.dataset)
        elapsed = time.time() - started
        result = {
            "schema_version": "caeos_split_pipeline_benchmark_v1",
            "dataset_id": args.dataset,
            "source": str(args.source),
            "source_size_bytes": args.source.stat().st_size,
            "elapsed_seconds": elapsed,
            "source_gib_per_hour": args.source.stat().st_size / (1024**3) / elapsed * 3600,
            "workers": marker["workers"],
            "piece_count": marker["integrity"]["piece_count"],
            "packet_integrity": marker["integrity"]["exact_multiset_match"],
            "rows": summary["row_count"],
            "class_csv_count": len(summary["class_csvs"]),
            "output_size_bytes": sum(item["size_bytes"] for item in summary["class_csvs"]),
        }
        print(json.dumps(result, sort_keys=True))
    finally:
        shutil.rmtree(args.work_root, ignore_errors=True)


if __name__ == "__main__":
    main()

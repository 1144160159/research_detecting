from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from caeos_unified_dataset import canonical_json_hash, sha256_file
from prepare_caeos_unified_multimodal_csv import (
    build_processing_policy,
    load_json,
    process_capture,
    tshark_identity,
)
from scripts.validate_splitpcap_integrity import validate as validate_split


MODULUS = 1 << 256


def row_fingerprint(paths: list[Path]) -> dict[str, Any]:
    count = 0
    digest_sum = 0
    digest_xor = 0
    for path in paths:
        with path.open("rb") as handle:
            for line in handle:
                digest = int.from_bytes(hashlib.sha256(line).digest(), "big")
                digest_sum = (digest_sum + digest) % MODULUS
                digest_xor ^= digest
                count += 1
    return {
        "row_count": count,
        "row_digest_sum": f"{digest_sum:064x}",
        "row_digest_xor": f"{digest_xor:064x}",
    }


def task(
    dataset: dict[str, Any],
    source_path: Path,
    source_member: str,
    source_sha256: str,
    capture_id: str,
    part_path: Path,
    schema: dict[str, Any],
    reservoir: dict[str, Any],
    decoder: str,
    decoder_identity: str,
    tshark_binary: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "path": str(source_path),
        "member": None,
        "source_member_override": source_member,
        "original_source_path": str(source_path),
        "capture_id": capture_id,
        "source_sha256": source_sha256,
        "part_path": str(part_path),
        "schema_sha256": canonical_json_hash(schema),
        "columns": [item["name"] for item in schema["columns"]],
        "idle_seconds": reservoir["flow_idle_timeout_seconds"],
        "maximum_packets": reservoir["maximum_packets"],
        "payload_prefix_bytes": reservoir["payload_prefix_bytes"],
        "sanitized_l4_prefix_bytes": reservoir.get("sanitized_l4_prefix_bytes", 2048),
        "maximum_active_flows": 6000,
        "packet_decoder": decoder,
        "tshark_binary": tshark_binary,
        "packet_decoder_identity": decoder_identity,
        "tshark_session_reset_packets": 0,
        "processing_policy": policy,
        "processing_policy_sha256": canonical_json_hash(policy),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-member", required=True)
    parser.add_argument("--splitpcap-binary", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--pieces", type=int, default=4)
    parser.add_argument("--decoder", choices=("tshark", "dpkt"), default="tshark")
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    args = parser.parse_args()
    if args.work_root.exists():
        raise ValueError(f"refusing existing work root: {args.work_root}")
    args.work_root.mkdir(parents=True)
    try:
        catalog = load_json(args.catalog)
        schema = load_json(args.schema)
        dataset = next(item for item in catalog["datasets"] if item["id"] == args.dataset)
        reservoir = catalog["feature_reservoir"]
        decoder_identity = (
            tshark_identity(args.tshark_binary)
            if args.decoder == "tshark"
            else f"dpkt {__import__('dpkt').__version__}"
        )
        policy = build_processing_policy(
            idle_seconds=float(reservoir["flow_idle_timeout_seconds"]),
            maximum_packets=int(reservoir["maximum_packets"]),
            payload_prefix_bytes=int(reservoir["payload_prefix_bytes"]),
            sanitized_l4_prefix_bytes=int(reservoir.get("sanitized_l4_prefix_bytes", 2048)),
            maximum_active_flows=6000,
            packet_decoder=args.decoder,
            packet_decoder_identity=decoder_identity,
            tshark_session_reset_packets=0,
            preprocessor_code_sha256=sha256_file(PROJECT_ROOT / "prepare_caeos_unified_multimodal_csv.py"),
        )
        source_sha256 = sha256_file(args.source)
        capture_id = hashlib.sha256(
            f"{args.source}::{args.source_member}".encode("utf-8")
        ).hexdigest()
        unsplit = process_capture(
            task(
                dataset,
                args.source,
                args.source_member,
                source_sha256,
                capture_id,
                args.work_root / "unsplit" / "capture.part",
                schema,
                reservoir,
                args.decoder,
                decoder_identity,
                args.tshark_binary,
                policy,
            )
        )
        split_dir = args.work_root / "pieces"
        result = subprocess.run(
            [str(args.splitpcap_binary), str(args.source), str(split_dir), str(args.pieces)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"splitpcap failed: {result.returncode}")
        pieces = sorted(path for path in split_dir.glob("*.pcap") if path.stat().st_size > 24)
        integrity = validate_split(args.source, pieces)
        split_parts = []
        for index, piece in enumerate(pieces):
            split_parts.append(
                process_capture(
                    task(
                        dataset,
                        piece,
                        args.source_member,
                        source_sha256,
                        capture_id,
                        args.work_root / "split" / f"piece-{index:05d}.part",
                        schema,
                        reservoir,
                        args.decoder,
                        decoder_identity,
                        args.tshark_binary,
                        policy,
                    )
                )
            )
        direct_fingerprint = row_fingerprint([Path(unsplit["part_path"])])
        split_fingerprint = row_fingerprint([Path(item["part_path"]) for item in split_parts])
        if direct_fingerprint != split_fingerprint:
            raise ValueError(
                "split feature rows differ: "
                + json.dumps(
                    {"direct": direct_fingerprint, "split": split_fingerprint},
                    sort_keys=True,
                )
            )
        print(
            json.dumps(
                {
                    "schema_version": "caeos_split_feature_equivalence_v1",
                    "dataset_id": args.dataset,
                    "source": str(args.source),
                    "piece_count": len(pieces),
                    "packet_integrity": integrity,
                    "row_fingerprint": direct_fingerprint,
                    "exact_row_multiset_match": True,
                },
                sort_keys=True,
            )
        )
    finally:
        shutil.rmtree(args.work_root, ignore_errors=True)


if __name__ == "__main__":
    main()

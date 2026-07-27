from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zipfile import ZipFile

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from extract_parrot2025_no_decryption_canary import extract_capture
from summarize_parrot2025_full_no_decryption_features import (
    load_json,
    summarize,
    validate_shard,
    verify_protocol,
)


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def completed_shard(
    *,
    protocol: dict[str, Any],
    capture: dict[str, Any],
    shard_root: Path,
) -> bool:
    manifest = shard_root / "manifest.json"
    csv_path = shard_root / "features.csv"
    if not manifest.exists() and not csv_path.exists():
        return False
    if not manifest.is_file() or not csv_path.is_file():
        raise ValueError(f"partial PARROT shard must not be overwritten: {shard_root}")
    validate_shard(protocol=protocol, capture=capture, shard_root=shard_root)
    return True


def write_shard(
    *,
    archive: ZipFile,
    protocol: dict[str, Any],
    capture: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    shard_root = output_root / "shards" / capture["capture_id"]
    shard_root.parent.mkdir(parents=True, exist_ok=True)
    if completed_shard(
        protocol=protocol, capture=capture, shard_root=shard_root
    ):
        return load_json(shard_root / "manifest.json")
    temporary_shard = shard_root.parent / f".{capture['capture_id']}.{os.getpid()}.tmp"
    if temporary_shard.exists():
        raise ValueError(f"temporary PARROT shard already exists: {temporary_shard}")
    temporary_shard.mkdir()
    temp_root_parent = output_root / "temporary"
    temp_root_parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=temp_root_parent) as temporary:
        frame, evidence = extract_capture(
            archive=archive,
            capture=capture,
            protocol=protocol,
            temp_root=Path(temporary),
        )
    csv_path = temporary_shard / "features.csv"
    frame.to_csv(csv_path, index=False)
    manifest: dict[str, Any] = {
        "schema_version": "parrot2025_no_decryption_feature_shard_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "capture": capture,
        "flow_row_count": int(len(frame)),
        "feature_count": protocol["feature_count"],
        "packet_accounting": {
            key: int(evidence[key])
            for key in (
                "input_packets",
                "converted_ip_packets",
                "skipped_non_ip_packets",
                "malformed_packets",
            )
        },
        "missing_feature_count": int(evidence["missing_feature_count"]),
        "nonfinite_feature_count": int(evidence["nonfinite_feature_count"]),
        "features_csv_sha256": file_hash(csv_path),
        "forbidden_data_or_model_use_observed": False,
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    atomic_text(
        temporary_shard / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    temporary_shard.replace(shard_root)
    return manifest


def run(
    *,
    protocol_path: Path,
    project_root: Path,
    output_root: Path,
    start_index: int,
    maximum_captures: int,
    summarize_when_complete: bool,
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    verify_protocol(protocol, project_root)
    if file_hash(Path(protocol["archive"])) != protocol["archive_sha256"]:
        raise ValueError("PARROT archive changed after full protocol freeze")
    output_root.mkdir(parents=True, exist_ok=True)
    captures = protocol["captures"]
    stop = len(captures)
    if maximum_captures > 0:
        stop = min(stop, start_index + maximum_captures)
    selected = captures[start_index:stop]
    with ZipFile(protocol["archive"]) as archive:
        for offset, capture in enumerate(selected, start=start_index + 1):
            manifest = write_shard(
                archive=archive,
                protocol=protocol,
                capture=capture,
                output_root=output_root,
            )
            print(
                "capture=%d/%d id=%s rows=%d"
                % (
                    offset,
                    len(captures),
                    capture["capture_id"],
                    manifest["flow_row_count"],
                ),
                flush=True,
            )
    completed = len(
        list((output_root / "shards").glob("*/manifest.json"))
    )
    value: dict[str, Any] = {
        "selected_capture_count": len(selected),
        "completed_shard_count": completed,
        "expected_shard_count": len(captures),
        "summary_generated": False,
    }
    if completed == len(captures) and summarize_when_complete:
        summary = summarize(
            protocol_path=protocol_path,
            project_root=project_root,
            output_root=output_root,
        )
        value["summary_generated"] = True
        value["summary_manifest_sha256"] = summary["manifest_sha256"]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--maximum-captures", type=int, default=0)
    parser.add_argument(
        "--no-summarize-when-complete", action="store_true"
    )
    args = parser.parse_args()
    if args.start_index < 0 or args.maximum_captures < 0:
        raise ValueError("capture indices must be non-negative")
    value = run(
        protocol_path=args.protocol,
        project_root=args.project_root,
        output_root=args.output_root,
        start_index=args.start_index,
        maximum_captures=args.maximum_captures,
        summarize_when_complete=not args.no_summarize_when_complete,
    )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()

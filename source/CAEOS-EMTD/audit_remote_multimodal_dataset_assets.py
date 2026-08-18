from __future__ import annotations

import argparse
import csv
import gzip
import json
import lzma
import os
import tarfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
)


RAW_BYTE_TOKENS = (
    "payload",
    "raw_data",
    "raw_packet",
    "packet_data",
    "packet_bytes",
    "byte_sequence",
    "bytes_sequence",
    "hex_dump",
)
BEHAVIOR_TOKENS = (
    "frame.time",
    "frame_time",
    "packet_length",
    "pkt_len",
    "tcp.len",
    "tcp_len",
    "length_sequence",
    "packet_sequence",
    "iat",
    "inter_arrival",
    "time_delta",
    "direction",
    "tcp.flags",
    "tcp_flags",
)
GRAPH_TOKENS = (
    "adjacency",
    "edge_index",
    "graph",
    "src_ip",
    "dst_ip",
    "source_ip",
    "destination_ip",
    "src_host",
    "dst_host",
)
TRACKED_SUFFIXES = {
    ".pcap",
    ".pcapng",
    ".csv",
    ".npy",
    ".npz",
    ".jsonl",
    ".parquet",
    ".zip",
    ".7z",
    ".gz",
    ".xz",
    ".tar",
    ".rar",
    ".tgz",
    ".txz",
    ".bz2",
    ".tbz2",
}
PCAP_SUFFIXES = {".pcap", ".pcapng"}
PCAP_MAGICS = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
    b"\x0a\x0d\x0d\x0a",
}
ARCHIVE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.xz",
    ".txz",
    ".tar.bz2",
    ".tbz2",
    ".pcap.gz",
    ".pcap.xz",
)


def normalized_columns(columns: list[str]) -> list[str]:
    return [
        column.strip().lower().replace(" ", "_").replace("-", "_")
        for column in columns
    ]


def matching_columns(
    columns: list[str], tokens: tuple[str, ...]
) -> list[str]:
    normalized = normalized_columns(columns)
    return sorted(
        {
            original
            for original, value in zip(columns, normalized)
            if any(token in value for token in tokens)
        }
    )


def read_csv_columns(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        first_line = handle.readline()
    if not first_line:
        return []
    return next(csv.reader([first_line]))


def array_sample(path: Path) -> dict[str, Any]:
    try:
        value = np.load(path, allow_pickle=False, mmap_mode="r")
        if isinstance(value, np.ndarray):
            return {
                "path": str(path),
                "shape": list(value.shape),
                "dtype": str(value.dtype),
            }
        names = sorted(value.files)
        arrays = {
            name: {
                "shape": list(value[name].shape),
                "dtype": str(value[name].dtype),
            }
            for name in names[:10]
        }
        value.close()
        return {"path": str(path), "arrays": arrays}
    except (OSError, ValueError) as exc:
        return {"path": str(path), "error": str(exc)}


def has_pcap_magic(prefix: bytes) -> bool:
    return prefix[:4] in PCAP_MAGICS


def is_supported_archive(path: Path) -> bool:
    return path.name.lower().endswith(ARCHIVE_SUFFIXES)


def inspect_zip_archive(path: Path, maximum_examples: int) -> dict[str, Any]:
    examples: list[str] = []
    magic_probe_budget = 10
    members_seen = 0
    with zipfile.ZipFile(path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        for member in members:
            members_seen += 1
            member_suffix = Path(member.filename).suffix.lower()
            if member_suffix in PCAP_SUFFIXES:
                if len(examples) < maximum_examples:
                    examples.append(member.filename)
                continue
            if magic_probe_budget > 0 and "pcap" in str(path).lower():
                magic_probe_budget -= 1
                with archive.open(member) as handle:
                    if (
                        has_pcap_magic(handle.read(4))
                        and len(examples) < maximum_examples
                    ):
                        examples.append(member.filename)
        return {
            "path": str(path),
            "archive_kind": "zip",
            "members_seen": members_seen,
            "capture_member_examples": examples,
            "verified_capture_present": bool(examples),
            "member_scan_complete": True,
        }


def inspect_tar_archive(path: Path, maximum_examples: int) -> dict[str, Any]:
    examples: list[str] = []
    members_seen = 0
    scan_complete = True
    with tarfile.open(path, mode="r:*") as archive:
        for member in archive:
            if not member.isfile():
                continue
            members_seen += 1
            member_suffix = Path(member.name).suffix.lower()
            capture = member_suffix in PCAP_SUFFIXES
            if not capture and "pcap" in str(path).lower():
                handle = archive.extractfile(member)
                capture = handle is not None and has_pcap_magic(handle.read(4))
                if handle is not None:
                    handle.close()
            if capture and len(examples) < maximum_examples:
                examples.append(member.name)
            if len(examples) >= maximum_examples:
                scan_complete = False
                break
    return {
        "path": str(path),
        "archive_kind": "tar",
        "members_seen": members_seen,
        "capture_member_examples": examples,
        "verified_capture_present": bool(examples),
        "member_scan_complete": scan_complete,
    }


def inspect_single_compressed_capture(path: Path) -> dict[str, Any]:
    opener = gzip.open if path.name.lower().endswith(".gz") else lzma.open
    with opener(path, "rb") as handle:
        capture = has_pcap_magic(handle.read(4))
    return {
        "path": str(path),
        "archive_kind": "single_compressed_capture",
        "members_seen": 1,
        "capture_member_examples": [path.name] if capture else [],
        "verified_capture_present": capture,
        "member_scan_complete": True,
    }


def inspect_archive(path: Path, maximum_examples: int = 5) -> dict[str, Any]:
    try:
        lower_name = path.name.lower()
        if lower_name.endswith(".zip"):
            return inspect_zip_archive(path, maximum_examples)
        if lower_name.endswith(
            (
                ".tar",
                ".tar.gz",
                ".tgz",
                ".tar.xz",
                ".txz",
                ".tar.bz2",
                ".tbz2",
            )
        ):
            return inspect_tar_archive(path, maximum_examples)
        if lower_name.endswith((".pcap.gz", ".pcap.xz")):
            return inspect_single_compressed_capture(path)
        raise ValueError("unsupported archive type")
    except (
        OSError,
        EOFError,
        tarfile.TarError,
        zipfile.BadZipFile,
        ValueError,
    ) as exc:
        return {
            "path": str(path),
            "archive_kind": "unknown",
            "capture_member_examples": [],
            "verified_capture_present": False,
            "member_scan_complete": False,
            "error": str(exc),
        }


def audit_dataset(
    root: Path,
    maximum_csv_headers: int,
    maximum_array_samples: int,
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    total_bytes: Counter[str] = Counter()
    csv_evidence = []
    array_evidence = []
    pcap_examples = []
    archive_evidence = []
    for directory, _subdirectories, filenames in os.walk(root):
        directory_path = Path(directory)
        for filename in filenames:
            path = directory_path / filename
            suffix = path.suffix.lower()
            if suffix not in TRACKED_SUFFIXES:
                continue
            counts[suffix] += 1
            try:
                total_bytes[suffix] += path.stat().st_size
            except OSError:
                pass
            if suffix in PCAP_SUFFIXES and len(pcap_examples) < 5:
                pcap_examples.append(str(path))
            elif is_supported_archive(path):
                archive_evidence.append(inspect_archive(path))
            elif suffix == ".csv" and len(csv_evidence) < maximum_csv_headers:
                try:
                    columns = read_csv_columns(path)
                except OSError as exc:
                    csv_evidence.append(
                        {"path": str(path), "error": str(exc)}
                    )
                    continue
                csv_evidence.append(
                    {
                        "path": str(path),
                        "columns": columns,
                        "byte_columns": matching_columns(
                            columns, RAW_BYTE_TOKENS
                        ),
                        "behavior_columns": matching_columns(
                            columns, BEHAVIOR_TOKENS
                        ),
                        "graph_columns": matching_columns(
                            columns, GRAPH_TOKENS
                        ),
                    }
                )
            elif (
                suffix in {".npy", ".npz"}
                and len(array_evidence) < maximum_array_samples
            ):
                array_evidence.append(array_sample(path))
    direct_pcap_count = counts[".pcap"] + counts[".pcapng"]
    verified_archive_capture_count = sum(
        bool(item.get("verified_capture_present"))
        for item in archive_evidence
    )
    raw_capture_present = (
        direct_pcap_count > 0 or verified_archive_capture_count > 0
    )
    csv_byte = any(item.get("byte_columns") for item in csv_evidence)
    csv_behavior = any(
        item.get("behavior_columns") for item in csv_evidence
    )
    csv_graph = any(item.get("graph_columns") for item in csv_evidence)
    return {
        "root": str(root.resolve()),
        "file_counts": dict(sorted(counts.items())),
        "tracked_bytes": dict(sorted(total_bytes.items())),
        "pcap_examples": pcap_examples,
        "archive_evidence": archive_evidence,
        "csv_header_evidence": csv_evidence,
        "array_evidence": array_evidence,
        "capability": {
            "raw_capture_present": raw_capture_present,
            "raw_capture_direct_present": direct_pcap_count > 0,
            "raw_capture_archive_present": verified_archive_capture_count > 0,
            "verified_capture_archive_count": verified_archive_capture_count,
            "only_csv_without_raw_capture": (
                counts[".csv"] > 0 and not raw_capture_present
            ),
            "csv_byte_or_payload_fields_observed": csv_byte,
            "csv_packet_behavior_fields_observed": csv_behavior,
            "csv_graph_or_endpoint_fields_observed": csv_graph,
            "three_modalities_reconstructable_from_raw_capture": (
                raw_capture_present
            ),
            "three_modalities_claimable_from_csv_alone": (
                csv_byte and csv_behavior and csv_graph
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-csv-headers", type=int, default=30)
    parser.add_argument("--maximum-array-samples", type=int, default=5)
    args = parser.parse_args()
    datasets = []
    for parent in args.root:
        parent = parent.resolve()
        if not parent.is_dir():
            raise ValueError(f"dataset root does not exist: {parent}")
        for child in sorted(parent.iterdir()):
            if child.is_dir():
                datasets.append(
                    audit_dataset(
                        child,
                        args.maximum_csv_headers,
                        args.maximum_array_samples,
                    )
                )
    result: dict[str, Any] = {
        "schema_version": "remote_multimodal_dataset_asset_audit_v2",
        "roots": [str(path.resolve()) for path in args.root],
        "datasets": datasets,
        "claim_boundary": {
            "file_and_header_inventory_only": True,
            "labels_and_split_quality_require_separate_audit": True,
            "raw_capture_enables_reconstruction_not_native_modalities": True,
            "csv_statistics_without_bytes_are_not_payload_semantics": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

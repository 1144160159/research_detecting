from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, BinaryIO

from caeos_label_alignment import SCHEMA_VERSION
from caeos_unified_dataset import atomic_json


COPY_BLOCK_BYTES = 16 * 1024 * 1024


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--chunk-size-mib", type=int, default=512)
    parser.add_argument("--maximum-attempts", type=int, default=5)
    return parser.parse_args()


def hash_stream(handle: BinaryIO, length: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = length
    while remaining is None or remaining > 0:
        size = COPY_BLOCK_BYTES if remaining is None else min(COPY_BLOCK_BYTES, remaining)
        block = handle.read(size)
        if not block:
            if remaining not in {None, 0}:
                raise OSError("unexpected end of artifact while hashing")
            break
        digest.update(block)
        if remaining is not None:
            remaining -= len(block)
    return digest.hexdigest()


def hash_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hash_stream(handle)


def hash_range(handle: BinaryIO, offset: int, length: int) -> str:
    handle.seek(offset)
    return hash_stream(handle, length)


def same_prefix(source: Path, partial: Path) -> bool:
    length = partial.stat().st_size
    if length > source.stat().st_size:
        return False
    with source.open("rb") as source_handle, partial.open("rb") as partial_handle:
        return hash_stream(source_handle, length) == hash_stream(partial_handle)


def preserved_name(path: Path, reason: str) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    candidate = path.with_name(f"{path.name}.{reason}.{stamp}")
    counter = 0
    while candidate.exists():
        counter += 1
        candidate = path.with_name(f"{path.name}.{reason}.{stamp}.{counter}")
    return candidate


def sqlite_metadata(path: Path, dataset_id: str) -> dict[str, Any]:
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported label index schema")
        if metadata.get("dataset_id") != dataset_id:
            raise ValueError(
                f"label index dataset mismatch: {metadata.get('dataset_id')} != {dataset_id}"
            )
        if connection.execute("SELECT 1 FROM labels LIMIT 1").fetchone() is None:
            raise ValueError("label index is empty")
        return {
            "schema_version": metadata["schema_version"],
            "registry_sha256": metadata["registry_sha256"],
            "record_count": int(metadata["record_count"]),
        }
    finally:
        connection.close()


def persist(
    dataset_id: str,
    source: Path,
    destination: Path,
    audit_output: Path,
    chunk_size_bytes: int = 512 * 1024 * 1024,
    maximum_attempts: int = 5,
) -> dict[str, Any]:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if chunk_size_bytes <= 0 or maximum_attempts <= 0:
        raise ValueError("chunk size and maximum attempts must be positive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    audit_output.parent.mkdir(parents=True, exist_ok=True)

    source_size = source.stat().st_size
    source_sha256 = hash_file(source)
    status = "published"
    preserved_paths: list[str] = []
    resumed_bytes = 0
    fsync_errors: list[str] = []
    reused_chunk_count = 0
    repaired_chunk_count = 0

    if destination.is_file():
        if destination.stat().st_size == source_size and hash_file(destination) == source_sha256:
            status = "reused_verified"
        else:
            preserved = preserved_name(destination, "superseded")
            os.replace(destination, preserved)
            preserved_paths.append(str(preserved))

    if status != "reused_verified":
        partial = destination.with_name(destination.name + ".partial")
        if partial.exists() and not partial.is_file():
            raise ValueError(f"partial destination is not a file: {partial}")
        if partial.is_file() and partial.stat().st_size > source_size:
            preserved = preserved_name(partial, "invalid")
            os.replace(partial, preserved)
            preserved_paths.append(str(preserved))

        original_size = partial.stat().st_size if partial.is_file() else 0
        resumed_bytes = min(original_size, source_size)
        mode = "r+b" if partial.is_file() else "w+b"
        with source.open("rb") as source_handle, partial.open(mode) as target:
            target.truncate(source_size)
            for offset in range(0, source_size, chunk_size_bytes):
                length = min(chunk_size_bytes, source_size - offset)
                expected = hash_range(source_handle, offset, length)
                if original_size >= offset + length:
                    actual = hash_range(target, offset, length)
                    if actual == expected:
                        reused_chunk_count += 1
                        continue

                last_error: BaseException | None = None
                for attempt in range(1, maximum_attempts + 1):
                    try:
                        source_handle.seek(offset)
                        target.seek(offset)
                        remaining = length
                        while remaining:
                            block = source_handle.read(min(COPY_BLOCK_BYTES, remaining))
                            if not block:
                                raise OSError("unexpected end of source during chunk repair")
                            target.write(block)
                            remaining -= len(block)
                        target.flush()
                        try:
                            os.fsync(target.fileno())
                        except OSError as error:
                            fsync_errors.append(repr(error))
                        if hash_range(target, offset, length) != expected:
                            raise OSError("persistent label index chunk SHA-256 mismatch")
                        repaired_chunk_count += 1
                        break
                    except OSError as error:
                        last_error = error
                        if attempt < maximum_attempts:
                            time.sleep(5 * attempt)
                else:
                    raise OSError(
                        f"persistent label index chunk at {offset} failed after "
                        f"{maximum_attempts} attempts: {last_error}"
                    ) from last_error
        if partial.stat().st_size != source_size:
            raise OSError("persistent label index size mismatch")
        if hash_file(partial) != source_sha256:
            raise OSError("persistent label index target reread SHA-256 mismatch")
        os.replace(partial, destination)

    metadata = sqlite_metadata(destination, dataset_id)
    report = {
        "schema_version": "caeos_persistent_label_index_audit_v1",
        "dataset_id": dataset_id,
        "status": status,
        "source_path": str(source),
        "source_retained": True,
        "preserved_paths": preserved_paths,
        "resumed_bytes": resumed_bytes,
        "chunk_size_bytes": chunk_size_bytes,
        "reused_chunk_count": reused_chunk_count,
        "repaired_chunk_count": repaired_chunk_count,
        "publication_fsync_errors": fsync_errors,
        "publication_verified_by_target_reread": True,
        "label_index": {
            "schema_version": metadata["schema_version"],
            "dataset_id": dataset_id,
            "registry_sha256": metadata["registry_sha256"],
            "record_count": metadata["record_count"],
            "path": str(destination),
            "size_bytes": destination.stat().st_size,
            "sha256": source_sha256,
        },
    }
    atomic_json(audit_output, report)
    return report


def main() -> None:
    args = parse_arguments()
    report = persist(
        args.dataset_id,
        args.source,
        args.destination,
        args.audit_output,
        args.chunk_size_mib * 1024 * 1024,
        args.maximum_attempts,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

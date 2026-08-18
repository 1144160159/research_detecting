from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, BinaryIO


COPY_BLOCK_BYTES = 16 * 1024 * 1024


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination-dir", required=True, type=Path)
    parser.add_argument("--chunk-size-mib", type=int, default=512)
    parser.add_argument("--maximum-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=10.0)
    return parser.parse_args()


def hash_range(handle: BinaryIO, offset: int, length: int) -> str:
    handle.seek(offset)
    remaining = length
    digest = hashlib.sha256()
    while remaining:
        block = handle.read(min(COPY_BLOCK_BYTES, remaining))
        if not block:
            raise OSError("unexpected end of source artifact")
        digest.update(block)
        remaining -= len(block)
    return digest.hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(COPY_BLOCK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_range(
    source: BinaryIO, offset: int, length: int, destination: Path
) -> str | None:
    source.seek(offset)
    remaining = length
    fsync_error: str | None = None
    with destination.open("wb") as target:
        while remaining:
            block = source.read(min(COPY_BLOCK_BYTES, remaining))
            if not block:
                raise OSError("unexpected end of source artifact during publication")
            target.write(block)
            remaining -= len(block)
        target.flush()
        try:
            os.fsync(target.fileno())
        except OSError as error:
            fsync_error = repr(error)
    return fsync_error


def atomic_manifest(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    temporary = path.with_name(path.name + ".partial")
    temporary.unlink(missing_ok=True)
    fsync_error: OSError | None = None
    with temporary.open("wb") as handle:
        handle.write(encoded)
        handle.flush()
        try:
            os.fsync(handle.fileno())
        except OSError as error:
            fsync_error = error
    if temporary.read_bytes() != encoded:
        raise OSError("chunk manifest target reread mismatch") from fsync_error
    os.replace(temporary, path)


def publish(
    source: Path,
    destination_dir: Path,
    chunk_size_bytes: int,
    maximum_attempts: int,
    retry_delay_seconds: float,
) -> dict[str, Any]:
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if chunk_size_bytes <= 0:
        raise ValueError("chunk size must be positive")
    if maximum_attempts <= 0:
        raise ValueError("maximum attempts must be positive")
    destination_dir.mkdir(parents=True, exist_ok=True)
    source_size = source.stat().st_size
    chunks: list[dict[str, Any]] = []

    with source.open("rb") as source_handle:
        for index, offset in enumerate(range(0, source_size, chunk_size_bytes)):
            length = min(chunk_size_bytes, source_size - offset)
            expected_sha256 = hash_range(source_handle, offset, length)
            final = destination_dir / f"{source.name}.part{index:05d}"
            temporary = final.with_name(final.name + ".partial")
            status = "published"
            attempts = 0
            fsync_errors: list[str] = []
            if (
                final.is_file()
                and final.stat().st_size == length
                and hash_file(final) == expected_sha256
            ):
                status = "reused_verified"
            else:
                final.unlink(missing_ok=True)
                last_error: BaseException | None = None
                for attempts in range(1, maximum_attempts + 1):
                    temporary.unlink(missing_ok=True)
                    try:
                        fsync_error = copy_range(
                            source_handle, offset, length, temporary
                        )
                        if fsync_error is not None:
                            fsync_errors.append(fsync_error)
                        if temporary.stat().st_size != length:
                            raise OSError("published chunk size mismatch")
                        if hash_file(temporary) != expected_sha256:
                            raise OSError("published chunk SHA-256 mismatch")
                        os.replace(temporary, final)
                        break
                    except OSError as error:
                        last_error = error
                        temporary.unlink(missing_ok=True)
                        if attempts < maximum_attempts:
                            time.sleep(retry_delay_seconds * attempts)
                else:
                    raise OSError(
                        f"chunk {index} publication failed after "
                        f"{maximum_attempts} attempts: {last_error}"
                    ) from last_error
            chunks.append(
                {
                    "index": index,
                    "offset": offset,
                    "size": length,
                    "sha256": expected_sha256,
                    "path": str(final),
                    "status": status,
                    "attempts": attempts,
                    "fsync_errors": fsync_errors,
                    "verified_by_target_reread": True,
                }
            )

    report = {
        "schema_version": "caeos_chunked_artifact_manifest_v1",
        "status": "complete",
        "source_path": str(source),
        "source_size": source_size,
        "source_sha256": hash_file(source),
        "source_retained": True,
        "chunk_size_bytes": chunk_size_bytes,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "reconstruction_rule": "concatenate chunks in ascending index order",
    }
    manifest = destination_dir / f"{source.name}.chunks.json"
    atomic_manifest(manifest, report)
    report["manifest_path"] = str(manifest)
    return report


def main() -> None:
    args = parse_arguments()
    report = publish(
        args.source,
        args.destination_dir,
        args.chunk_size_mib * 1024 * 1024,
        args.maximum_attempts,
        args.retry_delay_seconds,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

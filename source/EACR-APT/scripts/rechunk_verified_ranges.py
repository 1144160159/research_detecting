#!/usr/bin/env python3
"""Subdivide already verified range chunks for a smaller download chunk size.

The source chunks are left untouched. A target chunk is created atomically only
when one existing, size-valid source chunk fully covers the requested range.
This lets the range downloader change chunk size without downloading bytes that
are already present on the GPU server.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
import os
from pathlib import Path
import re


CHUNK_RE = re.compile(r"(\d{12})-(\d{12})\.chunk")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk_dir", type=Path)
    parser.add_argument("--total-bytes", type=int, required=True)
    parser.add_argument("--target-chunk-size", type=int, required=True)
    return parser.parse_args()


def valid_chunks(chunk_dir: Path, total: int) -> list[tuple[int, int, Path]]:
    chunks: list[tuple[int, int, Path]] = []
    for path in chunk_dir.glob("*.chunk"):
        match = CHUNK_RE.fullmatch(path.name)
        if not match:
            continue
        start, end = (int(value) for value in match.groups())
        if start < 0 or start > end or end >= total:
            continue
        if path.is_file() and path.stat().st_size == end - start + 1:
            chunks.append((start, end, path))
    return sorted(chunks)


def main() -> int:
    args = parse_args()
    if args.total_bytes <= 0 or args.target_chunk_size <= 0:
        raise SystemExit("total-bytes and target-chunk-size must be positive")

    chunk_dir = args.chunk_dir.resolve()
    if not chunk_dir.is_dir():
        raise SystemExit(f"chunk directory does not exist: {chunk_dir}")

    sources = valid_chunks(chunk_dir, args.total_bytes)
    source_starts = [start for start, _, _ in sources]
    widest_prefix: list[tuple[int, int, Path]] = []
    widest: tuple[int, int, Path] | None = None
    for source in sources:
        if widest is None or source[1] > widest[1]:
            widest = source
        widest_prefix.append(widest)
    created = 0
    created_bytes = 0
    already_present = 0

    for target_start in range(0, args.total_bytes, args.target_chunk_size):
        target_end = min(
            args.total_bytes - 1,
            target_start + args.target_chunk_size - 1,
        )
        target = chunk_dir / f"{target_start:012d}-{target_end:012d}.chunk"
        expected = target_end - target_start + 1
        if target.is_file() and target.stat().st_size == expected:
            already_present += 1
            continue

        source_index = bisect_right(source_starts, target_start) - 1
        if source_index < 0:
            continue
        source_start, source_end, source_path = widest_prefix[source_index]
        if source_end < target_end:
            continue
        temporary = target.with_name(f".{target.name}.rechunk.{os.getpid()}")
        temporary.unlink(missing_ok=True)
        with source_path.open("rb") as source, temporary.open("xb") as output:
            source.seek(target_start - source_start)
            payload = source.read(expected)
            if len(payload) != expected:
                raise RuntimeError(
                    f"short read from {source_path}: {len(payload)}/{expected}"
                )
            output.write(payload)
            output.flush()
        os.replace(temporary, target)
        created += 1
        created_bytes += expected

    print(
        f"source_chunks={len(sources)} created_chunks={created} "
        f"created_bytes={created_bytes} already_present={already_present}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

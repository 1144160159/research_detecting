#!/usr/bin/env python3
"""Resumable, range-verified Google Drive manifest collector.

Payloads are written only under ``--root``.  The manifest and this script contain
no credentials.  Existing ``.part`` files are treated as immutable prefixes;
missing ranges are downloaded into separate chunk files and the final archive is
assembled atomically only after every range has been verified.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import logging
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import threading
import time
from typing import Any, Iterable
from urllib.parse import urlparse


LOGGER = logging.getLogger("gdrive-chunked")
CONTENT_RANGE_RE = re.compile(r"content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)", re.I)
CHUNK_FILE_RE = re.compile(r"(\d{12})-(\d{12})\.chunk")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.tmp.{os.getpid()}.{threading.get_ident()}"
    )
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def safe_relative_name(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Unsafe manifest filename: {value!r}")
    return path.as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("files"), list):
        raise ValueError("Manifest must be an object with a files list")
    files = []
    for raw in value["files"]:
        name = safe_relative_name(str(raw["name"]))
        url = str(raw["url"])
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {
            "drive.usercontent.google.com",
            "drive.google.com",
        }:
            raise ValueError(f"Unsupported Google Drive URL for {name!r}: {url!r}")
        expected = int(raw["expected_bytes"])
        if expected <= 0:
            raise ValueError(f"expected_bytes must be positive for {name!r}")
        item = dict(raw)
        item.update(name=name, url=url, expected_bytes=expected)
        files.append(item)
    expected_files = int(value.get("expected_files", len(files)))
    expected_bytes = int(
        value.get("expected_bytes", sum(item["expected_bytes"] for item in files))
    )
    actual_bytes = sum(item["expected_bytes"] for item in files)
    if len(files) != expected_files or actual_bytes != expected_bytes:
        raise ValueError(
            "Manifest invariant failed: "
            f"files {len(files)}/{expected_files}, bytes {actual_bytes}/{expected_bytes}"
        )
    result = dict(value)
    result.update(files=files, expected_files=expected_files, expected_bytes=expected_bytes)
    return result


def plan_chunks(start: int, total: int, chunk_size: int) -> list[tuple[int, int]]:
    if start < 0 or total < 0 or start > total:
        raise ValueError("Require 0 <= start <= total")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    chunks = []
    offset = start
    while offset < total:
        end = min(total - 1, offset + chunk_size - 1)
        chunks.append((offset, end))
        offset = end + 1
    return chunks


def covered_bytes(
    chunk_dir: Path, total: int, prefix_size: int = 0
) -> int:
    """Return unique verified bytes, accounting for overlapping chunk sizes."""
    ranges: list[tuple[int, int]] = []
    if prefix_size > 0:
        ranges.append((0, min(prefix_size, total) - 1))
    if chunk_dir.is_dir():
        for path in chunk_dir.glob("*.chunk"):
            match = CHUNK_FILE_RE.fullmatch(path.name)
            if not match:
                continue
            start, end = (int(value) for value in match.groups())
            if start < 0 or start > end or end >= total:
                continue
            if not path.is_file() or path.stat().st_size != end - start + 1:
                continue
            ranges.append((start, end))
    ranges.sort()
    merged: list[list[int]] = []
    for start, end in ranges:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        elif end > merged[-1][1]:
            merged[-1][1] = end
    return sum(end - start + 1 for start, end in merged)


def order_chunks(
    ranges: list[tuple[int, int]], order: str
) -> list[tuple[int, int]]:
    """Choose request order without changing the canonical assembly order."""
    if order == "forward":
        return list(ranges)
    if order == "reverse":
        return list(reversed(ranges))
    if order == "spread":
        result: list[tuple[int, int]] = []
        pending = [(0, len(ranges))]
        while pending:
            lower, upper = pending.pop(0)
            if lower >= upper:
                continue
            middle = (lower + upper - 1) // 2
            result.append(ranges[middle])
            pending.append((lower, middle))
            pending.append((middle + 1, upper))
        return result
    raise ValueError(f"Unsupported chunk order: {order}")


def parse_content_range(headers: str) -> tuple[int, int, int] | None:
    matches = CONTENT_RANGE_RE.findall(headers.replace("\r", ""))
    if not matches:
        return None
    start, end, total = matches[-1]
    return int(start), int(end), int(total)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(16 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def matches_magic(path: Path, magic_hex: str | None) -> bool:
    if not magic_hex:
        return True
    expected = bytes.fromhex(magic_hex)
    with path.open("rb") as handle:
        return handle.read(len(expected)) == expected


def archive_test(path: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if path.name.endswith((".tar.gz", ".tgz")):
        command = ["tar", "-tzf", str(path)]
    elif path.name.endswith(".tar"):
        command = ["tar", "-tf", str(path)]
    elif path.name.endswith(".zip"):
        command = ["unzip", "-tq", str(path)]
    else:
        raise ValueError(f"No archive validator configured for {path.name!r}")
    with log_path.open("ab") as handle:
        handle.write(f"[{utc_now()}] {' '.join(command)}\n".encode())
        subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, check=True)


def copy_file(source: Path, destination_handle: Any) -> None:
    with source.open("rb") as source_handle:
        shutil.copyfileobj(source_handle, destination_handle, length=16 * 1024 * 1024)


class Collector:
    def __init__(self, args: argparse.Namespace, manifest: dict[str, Any]):
        self.args = args
        self.manifest = manifest
        self.root = args.root.resolve()
        self.raw = self.root / "raw" / "json"
        self.manifest_dir = self.root / "manifests"
        self.state_dir = self.root / "state"
        self.log_dir = self.root / "logs"
        self.chunk_root = self.root / "tmp" / "chunks"
        self.quarantine = self.root / "quarantine"
        for directory in (
            self.raw,
            self.manifest_dir,
            self.state_dir,
            self.log_dir,
            self.chunk_root,
            self.quarantine,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.state_stem = args.state_stem
        self.verified_path = self.state_dir / f"{self.state_stem}_verified_files.json"
        self.retries_path = self.state_dir / f"{self.state_stem}_chunk_retries.json"
        self.collection_state_path = self.state_dir / f"{self.state_stem}_state.json"
        self.verified = self._load_json(self.verified_path, {})
        self.retries = self._load_json(
            self.retries_path,
            {"updated_at": utc_now(), "retry_events_total": 0, "files": {}},
        )

    @staticmethod
    def _load_json(path: Path, default: Any) -> Any:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

    @staticmethod
    def state_id(item: dict[str, Any]) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", item["name"])

    def final_path(self, item: dict[str, Any]) -> Path:
        return self.raw.joinpath(*PurePosixPath(item["name"]).parts)

    def part_path(self, item: dict[str, Any]) -> Path:
        return Path(f"{self.final_path(item)}.part")

    def preserved_prefix_size(self, item: dict[str, Any]) -> int:
        """Return a usable prefix size, quarantining invalid prefixes with evidence."""
        part_path = self.part_path(item)
        prefix_size = part_path.stat().st_size if part_path.exists() else 0
        if prefix_size > item["expected_bytes"]:
            quarantine = self.quarantine / f"{part_path.name}.oversize.{int(time.time())}"
            os.replace(part_path, quarantine)
            return 0
        if prefix_size and not matches_magic(part_path, item.get("magic_hex")):
            with part_path.open("rb") as handle:
                first_32_hex = handle.read(32).hex()
            digest = sha256_file(part_path)
            quarantine = self.quarantine / f"{part_path.name}.wrong-magic.{int(time.time())}"
            os.replace(part_path, quarantine)
            evidence_path = self.state_dir / f"{self.state_stem}_prefix_quarantine.json"
            evidence = self._load_json(evidence_path, {"files": []})
            evidence["files"].append(
                {
                    "filename": item["name"],
                    "reason": "existing prefix failed configured magic check",
                    "expected_magic_hex": item.get("magic_hex"),
                    "first_32_hex": first_32_hex,
                    "bytes": prefix_size,
                    "sha256": digest,
                    "quarantine_path": str(quarantine),
                    "quarantined_at": utc_now(),
                }
            )
            evidence["updated_at"] = utc_now()
            atomic_json(evidence_path, evidence)
            LOGGER.warning(
                "quarantined invalid prefix file=%s bytes=%d sha256=%s path=%s",
                item["name"],
                prefix_size,
                digest,
                quarantine,
            )
            return 0
        return prefix_size

    def chunk_dir(self, item: dict[str, Any]) -> Path:
        return self.chunk_root / self.state_id(item)

    def verified_entry_is_current(self, item: dict[str, Any]) -> bool:
        entry = self.verified.get(item["name"], {})
        path = self.final_path(item)
        return bool(
            entry.get("complete")
            and entry.get("expected_bytes") == item["expected_bytes"]
            and path.is_file()
            and path.stat().st_size == item["expected_bytes"]
            and matches_magic(path, item.get("magic_hex"))
        )

    def file_present_bytes(self, item: dict[str, Any]) -> int:
        final_path = self.final_path(item)
        if final_path.is_file() and final_path.stat().st_size == item["expected_bytes"]:
            return item["expected_bytes"]
        part_path = self.part_path(item)
        prefix_size = (
            min(part_path.stat().st_size, item["expected_bytes"])
            if part_path.is_file()
            else 0
        )
        return covered_bytes(
            self.chunk_dir(item), item["expected_bytes"], prefix_size
        )

    def update_collection_state(self, active_file: str | None = None) -> None:
        with self.lock:
            rows = []
            for item in self.manifest["files"]:
                entry = self.verified.get(item["name"], {})
                complete = self.verified_entry_is_current(item)
                rows.append(
                    {
                        "filename": item["name"],
                        "google_drive_id": item.get("google_drive_id"),
                        "selection_tier": item.get("selection_tier", "extended"),
                        "expected_bytes": item["expected_bytes"],
                        "present_bytes": self.file_present_bytes(item),
                        "complete": complete,
                        "sha256": entry.get("sha256") if complete else None,
                        "archive_integrity": entry.get("archive_integrity", "pending"),
                    }
                )
            core_rows = [row for row in rows if row["selection_tier"] == "core"]
            extended_rows = [
                row for row in rows if row["selection_tier"] == "extended"
            ]
            state = {
                "dataset": self.manifest.get("dataset_id", "gdrive_manifest"),
                "source": self.manifest.get("source"),
                "source_folder_id": self.manifest.get("source_folder_id"),
                "selection": self.manifest.get("selection_note"),
                "updated_at": utc_now(),
                "active_file": active_file,
                "workers": self.args.workers,
                "chunk_size": self.args.chunk_size,
                "expected_file_count": self.manifest["expected_files"],
                "expected_bytes": self.manifest["expected_bytes"],
                "completed_file_count": sum(row["complete"] for row in rows),
                "completed_bytes": sum(
                    row["expected_bytes"] for row in rows if row["complete"]
                ),
                "core_expected_file_count": len(core_rows),
                "core_expected_bytes": sum(row["expected_bytes"] for row in core_rows),
                "core_completed_file_count": sum(row["complete"] for row in core_rows),
                "core_completed_bytes": sum(
                    row["expected_bytes"] for row in core_rows if row["complete"]
                ),
                "core_selection_complete": bool(core_rows)
                and all(row["complete"] for row in core_rows),
                "extended_expected_file_count": len(extended_rows),
                "extended_expected_bytes": sum(
                    row["expected_bytes"] for row in extended_rows
                ),
                "extended_completed_file_count": sum(
                    row["complete"] for row in extended_rows
                ),
                "extended_completed_bytes": sum(
                    row["expected_bytes"] for row in extended_rows if row["complete"]
                ),
                "extended_selection_complete": bool(extended_rows)
                and all(row["complete"] for row in extended_rows),
                "downloaded_or_partial_bytes": sum(row["present_bytes"] for row in rows),
                "retry_events_total": int(self.retries.get("retry_events_total", 0)),
                "currently_failed_chunks": sum(
                    1
                    for file_state in self.retries.get("files", {}).values()
                    for chunk in file_state.values()
                    if not chunk.get("resolved", False)
                ),
                "complete": all(row["complete"] for row in rows),
                "files": rows,
            }
            atomic_json(self.collection_state_path, state)

    def record_retry(
        self,
        item: dict[str, Any],
        start: int,
        end: int,
        attempt: int,
        reason: str,
    ) -> None:
        with self.lock:
            file_state = self.retries.setdefault("files", {}).setdefault(item["name"], {})
            key = f"{start}-{end}"
            old = file_state.get(key, {})
            file_state[key] = {
                "attempts": max(int(old.get("attempts", 0)), attempt),
                "last_error": reason[:2000],
                "last_failed_at": utc_now(),
                "resolved": False,
            }
            self.retries["retry_events_total"] = int(
                self.retries.get("retry_events_total", 0)
            ) + 1
            self.retries["updated_at"] = utc_now()
            atomic_json(self.retries_path, self.retries)

    def record_chunk_success(
        self, item: dict[str, Any], start: int, end: int, attempt: int
    ) -> None:
        with self.lock:
            file_state = self.retries.setdefault("files", {}).setdefault(item["name"], {})
            key = f"{start}-{end}"
            if key in file_state or attempt > 1:
                old = file_state.get(key, {})
                file_state[key] = {
                    "attempts": max(int(old.get("attempts", 0)), attempt - 1),
                    "last_error": old.get("last_error"),
                    "last_failed_at": old.get("last_failed_at"),
                    "resolved": True,
                    "resolved_at": utc_now(),
                }
                self.retries["updated_at"] = utc_now()
                atomic_json(self.retries_path, self.retries)

    def curl_command(
        self, item: dict[str, Any], start: int, end: int, output: Path, headers: Path
    ) -> list[str]:
        command = [
            "curl",
            "--http1.1",
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--connect-timeout",
            str(self.args.connect_timeout),
            "--max-time",
            str(self.args.request_timeout),
            "--speed-limit",
            "1024",
            "--speed-time",
            "60",
            "--range",
            f"{start}-{end}",
            "--dump-header",
            str(headers),
            "--output",
            str(output),
        ]
        if self.args.limit_rate:
            command.extend(["--limit-rate", self.args.limit_rate])
        if self.args.proxy:
            command.extend(["--proxy", self.args.proxy])
        command.append(item["url"])
        return command

    def download_chunk_once(
        self, item: dict[str, Any], start: int, end: int, attempt: int
    ) -> Path | None:
        chunk_dir = self.chunk_dir(item)
        chunk_dir.mkdir(parents=True, exist_ok=True)
        target = chunk_dir / f"{start:012d}-{end:012d}.chunk"
        expected = end - start + 1
        if target.is_file() and target.stat().st_size == expected:
            return target
        if target.exists():
            target.unlink()
        unique = f"{os.getpid()}.{threading.get_ident()}.{attempt}"
        temporary = chunk_dir / f".{target.name}.download.{unique}"
        headers_path = chunk_dir / f".{target.name}.headers.{unique}"
        try:
            result = subprocess.run(
                self.curl_command(item, start, end, temporary, headers_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            header_text = (
                headers_path.read_text(encoding="utf-8", errors="replace")
                if headers_path.exists()
                else ""
            )
            content_range = parse_content_range(header_text)
            actual = temporary.stat().st_size if temporary.exists() else 0
            valid = (
                result.returncode == 0
                and actual == expected
                and content_range == (start, end, item["expected_bytes"])
            )
            if valid:
                os.replace(temporary, target)
                self.record_chunk_success(item, start, end, attempt)
                return target
            reason = (
                f"curl_rc={result.returncode}; bytes={actual}/{expected}; "
                f"content_range={content_range}; stderr={result.stderr.strip()}"
            )
            self.record_retry(item, start, end, attempt, reason)
            LOGGER.warning(
                "chunk retry file=%s range=%d-%d attempt=%d reason=%s",
                item["name"],
                start,
                end,
                attempt,
                reason,
            )
            return None
        finally:
            temporary.unlink(missing_ok=True)
            headers_path.unlink(missing_ok=True)

    def download_chunk(self, item: dict[str, Any], start: int, end: int) -> Path:
        attempt = 0
        while True:
            attempt += 1
            target = self.download_chunk_once(item, start, end, attempt)
            if target is not None:
                return target
            if self.args.max_attempts and attempt >= self.args.max_attempts:
                raise RuntimeError(
                    f"Chunk {item['name']} {start}-{end} failed after {attempt} attempts"
                )
            time.sleep(self.args.retry_wait)

    def download_chunks_rotating(
        self,
        item: dict[str, Any],
        canonical_ranges: list[tuple[int, int]],
        request_ranges: list[tuple[int, int]],
    ) -> list[tuple[int, int, Path]]:
        completed: dict[tuple[int, int], Path] = {}
        attempts = {chunk_range: 0 for chunk_range in canonical_ranges}
        round_number = 0
        while len(completed) < len(canonical_ranges):
            round_number += 1
            pending = [chunk_range for chunk_range in request_ranges if chunk_range not in completed]
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.args.workers,
                thread_name_prefix="gdrive-rotate",
            ) as executor:
                future_map = {}
                for start, end in pending:
                    attempts[(start, end)] += 1
                    future = executor.submit(
                        self.download_chunk_once,
                        item,
                        start,
                        end,
                        attempts[(start, end)],
                    )
                    future_map[future] = (start, end)
                for future in concurrent.futures.as_completed(future_map):
                    start, end = future_map[future]
                    target = future.result()
                    if target is not None:
                        completed[(start, end)] = target
                    elif self.args.max_attempts and attempts[(start, end)] >= self.args.max_attempts:
                        raise RuntimeError(
                            f"Chunk {item['name']} {start}-{end} failed after "
                            f"{attempts[(start, end)]} rotating attempts"
                        )
            self.update_collection_state(active_file=item["name"])
            LOGGER.info(
                "rotating chunk round file=%s round=%d completed=%d/%d",
                item["name"],
                round_number,
                len(completed),
                len(canonical_ranges),
            )
            if len(completed) < len(canonical_ranges):
                time.sleep(self.args.retry_wait)
        return [
            (start, end, completed[(start, end)])
            for start, end in canonical_ranges
        ]

    def download_missing_chunks(
        self, item: dict[str, Any], prefix_size: int
    ) -> list[tuple[int, int, Path]]:
        ranges = plan_chunks(prefix_size, item["expected_bytes"], self.args.chunk_size)
        request_ranges = order_chunks(ranges, self.args.chunk_order)
        LOGGER.info(
            "chunk plan file=%s prefix=%d chunks=%d remaining=%d order=%s",
            item["name"],
            prefix_size,
            len(ranges),
            item["expected_bytes"] - prefix_size,
            self.args.chunk_order,
        )
        if self.args.rotate_failures:
            return self.download_chunks_rotating(item, ranges, request_ranges)
        completed: dict[tuple[int, int], Path] = {}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.args.workers,
            thread_name_prefix="gdrive-range",
        ) as executor:
            future_map = {
                executor.submit(self.download_chunk, item, start, end): (start, end)
                for start, end in request_ranges
            }
            for index, future in enumerate(
                concurrent.futures.as_completed(future_map), start=1
            ):
                start, end = future_map[future]
                completed[(start, end)] = future.result()
                if (
                    index % self.args.state_update_every == 0
                    or index == len(ranges)
                ):
                    self.update_collection_state(active_file=item["name"])
                    LOGGER.info(
                        "chunk progress file=%s completed=%d/%d",
                        item["name"],
                        index,
                        len(ranges),
                    )
        return [(start, end, completed[(start, end)]) for start, end in ranges]

    def validate_and_record(self, item: dict[str, Any], candidate: Path) -> str:
        if candidate.stat().st_size != item["expected_bytes"]:
            raise RuntimeError(
                f"Size mismatch for {candidate}: {candidate.stat().st_size}/{item['expected_bytes']}"
            )
        if not matches_magic(candidate, item.get("magic_hex")):
            raise RuntimeError(f"Magic mismatch for {candidate}")
        archive_log = self.log_dir / "archive_tests" / f"{self.state_id(item)}.log"
        archive_test(candidate, archive_log)
        digest = sha256_file(candidate)
        self.verified[item["name"]] = {
            "complete": True,
            "expected_bytes": item["expected_bytes"],
            "sha256": digest,
            "archive_integrity": "pass",
            "verified_at": utc_now(),
        }
        atomic_json(self.verified_path, self.verified)
        return digest

    def collect_file(self, item: dict[str, Any]) -> None:
        final_path = self.final_path(item)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if self.verified_entry_is_current(item):
            LOGGER.info("verified file already present: %s", item["name"])
            return
        if final_path.exists() and final_path.stat().st_size != item["expected_bytes"]:
            quarantine = self.quarantine / f"{final_path.name}.wrong-size.{int(time.time())}"
            os.replace(final_path, quarantine)
        if final_path.is_file():
            digest = self.validate_and_record(item, final_path)
            LOGGER.info("verified existing final file=%s sha256=%s", item["name"], digest)
            self.update_collection_state(active_file=item["name"])
            return

        part_path = self.part_path(item)
        prefix_size = self.preserved_prefix_size(item)

        chunks = self.download_missing_chunks(item, prefix_size)
        assembling = Path(f"{final_path}.assembling.{os.getpid()}")
        assembling.unlink(missing_ok=True)
        LOGGER.info("assembly start file=%s", item["name"])
        with assembling.open("wb") as output:
            if prefix_size:
                copy_file(part_path, output)
            for start, end, chunk_path in chunks:
                expected = end - start + 1
                if chunk_path.stat().st_size != expected:
                    raise RuntimeError(f"Chunk size drift before assembly: {chunk_path}")
                copy_file(chunk_path, output)
            output.flush()
            os.fsync(output.fileno())
        digest = self.validate_and_record(item, assembling)
        os.replace(assembling, final_path)
        part_path.unlink(missing_ok=True)
        shutil.rmtree(self.chunk_dir(item), ignore_errors=True)
        (self.manifest_dir / f"{final_path.name}.sha256").write_text(
            f"{digest}  {final_path.name}\n", encoding="utf-8"
        )
        LOGGER.info("verified file=%s sha256=%s", item["name"], digest)
        self.update_collection_state(active_file=item["name"])

    def write_final_manifest(self) -> None:
        self.update_collection_state(active_file=None)
        state = json.loads(self.collection_state_path.read_text(encoding="utf-8"))
        if not state["complete"]:
            raise RuntimeError("Collection finished without reaching complete state")
        result = {
            "dataset": self.manifest.get("dataset_id"),
            "source": self.manifest.get("source"),
            "source_folder_id": self.manifest.get("source_folder_id"),
            "selection": self.manifest.get("selection_note"),
            "completed_at": utc_now(),
            "file_count": state["completed_file_count"],
            "total_bytes": state["completed_bytes"],
            "retry_events_total": state["retry_events_total"],
            "core_selection_complete": state["core_selection_complete"],
            "extended_selection_complete": state["extended_selection_complete"],
            "files": state["files"],
        }
        atomic_json(self.manifest_dir / f"{self.state_stem}_manifest.json", result)
        (self.state_dir / f"{self.state_stem}.COMPLETE").write_text(
            result["completed_at"] + "\n", encoding="utf-8"
        )

    def run(self) -> None:
        # Quarantine unusable legacy prefixes before progress accounting, even
        # when the affected file belongs to the lower-priority extended tier.
        for item in self.manifest["files"]:
            self.preserved_prefix_size(item)
        self.update_collection_state(active_file=None)
        for item in sorted(
            self.manifest["files"],
            key=lambda value: (
                0 if value.get("selection_tier") == "core" else 1,
                int(value.get("priority", 10_000)),
                value["expected_bytes"],
            ),
        ):
            self.collect_file(item)
        self.write_final_manifest()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--state-stem",
        default="darpa_tc_e3_json",
        help="Safe basename for state/manifest files; chunk paths remain keyed by payload filename",
    )
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=32 * 1024 * 1024)
    parser.add_argument(
        "--state-update-every",
        type=int,
        default=8,
        help="Refresh the full collection state after this many completed chunks.",
    )
    parser.add_argument(
        "--chunk-order",
        choices=("forward", "reverse", "spread"),
        default="forward",
        help="Request ranges forward, reverse, or breadth-first spread; assembly remains forward.",
    )
    parser.add_argument(
        "--rotate-failures",
        action="store_true",
        help="Attempt every missing range once per round so quota failures cannot pin workers.",
    )
    parser.add_argument("--limit-rate", default="12M")
    parser.add_argument("--connect-timeout", type=int, default=30)
    parser.add_argument("--request-timeout", type=int, default=240)
    parser.add_argument("--retry-wait", type=float, default=10.0)
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="0 retries forever; a positive value fails the collector after that many attempts",
    )
    args = parser.parse_args(argv)
    if args.workers < 1 or args.workers > 16:
        parser.error("--workers must be between 1 and 16")
    if args.state_update_every < 1:
        parser.error("--state-update-every must be positive")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.state_stem):
        parser.error("--state-stem must contain only letters, digits, dot, underscore, or dash")
    if args.proxy and urlparse(args.proxy).scheme not in {"socks5", "socks5h"}:
        parser.error("--proxy must use socks5:// or socks5h://")
    return args


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(threadName)s %(message)s",
    )
    manifest = load_manifest(args.manifest.resolve())
    Collector(args, manifest).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Low-frequency Google Drive quota recovery for one manifest file.

Each round sends exactly one 1 MiB range gate.  A quota/HTML response ends the
round and sleeps for the configured cooldown (60 minutes by default).  When the
gate succeeds, missing chunks are attempted once, sequentially; the first
failure ends the round.  Existing verified chunks are never rewritten.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Iterable

try:
    from collect_gdrive_manifest_chunked import (
        atomic_json,
        load_manifest,
        parse_content_range,
        plan_chunks,
    )
except ImportError:  # pragma: no cover - package import path
    from scripts.collect_gdrive_manifest_chunked import (
        atomic_json,
        load_manifest,
        parse_content_range,
        plan_chunks,
    )


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_id(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def chunk_path(chunk_dir: Path, start: int, end: int) -> Path:
    return chunk_dir / f"{start:012d}-{end:012d}.chunk"


def missing_ranges(
    chunk_dir: Path, expected_bytes: int, chunk_size: int
) -> list[tuple[int, int]]:
    missing = []
    for start, end in plan_chunks(0, expected_bytes, chunk_size):
        path = chunk_path(chunk_dir, start, end)
        if not path.is_file() or path.stat().st_size != end - start + 1:
            missing.append((start, end))
    return missing


def response_is_valid(
    returncode: int,
    actual_bytes: int,
    headers: str,
    start: int,
    end: int,
    total: int,
) -> bool:
    return (
        returncode == 0
        and actual_bytes == end - start + 1
        and parse_content_range(headers) == (start, end, total)
    )


def response_reason(
    returncode: int,
    actual_bytes: int,
    headers: str,
    body_preview: bytes,
    start: int,
    end: int,
    total: int,
    stderr: str,
) -> str:
    text = (headers + "\n" + body_preview.decode("utf-8", errors="replace")).lower()
    if "quota exceeded" in text or "too many users" in text:
        return "google_drive_quota_exceeded"
    return (
        f"range_gate_failed rc={returncode} bytes={actual_bytes}/{end-start+1} "
        f"content_range={parse_content_range(headers)} expected=({start},{end},{total}) "
        f"stderr={stderr.strip()[:500]}"
    )


class HourlyRecovery:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.manifest = load_manifest(args.manifest.resolve())
        if self.manifest["expected_files"] != 1:
            raise ValueError("Hourly quota recovery requires a one-file manifest")
        self.item = self.manifest["files"][0]
        self.root = args.root.resolve()
        self.raw = self.root / "raw" / "json"
        self.chunk_dir = (
            self.root / "tmp" / "chunks" / safe_id(self.item["name"])
        )
        self.state_dir = self.root / "state"
        self.gate_dir = self.state_dir / "quota_gate" / args.state_stem
        self.lock_dir = self.state_dir / "locks"
        self.state_path = (
            self.state_dir / f"{args.state_stem}_quota_recovery_state.json"
        )
        self.lock_path = self.lock_dir / f"{args.state_stem}_quota_recovery.lock"
        for directory in (
            self.raw,
            self.chunk_dir,
            self.state_dir,
            self.gate_dir,
            self.lock_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        self.round_count = 0
        if self.state_path.exists():
            old = json.loads(self.state_path.read_text(encoding="utf-8"))
            self.round_count = int(old.get("round_count", 0))

    def acquire_lock(self) -> None:
        try:
            descriptor = os.open(
                self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
            )
        except FileExistsError:
            old = self.lock_path.read_text(encoding="utf-8", errors="replace").strip()
            try:
                old_pid = int(old)
                os.kill(old_pid, 0)
            except (ValueError, ProcessLookupError):
                self.lock_path.unlink(missing_ok=True)
                return self.acquire_lock()
            raise RuntimeError(f"Recovery wrapper already active with PID {old_pid}")
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"{os.getpid()}\n")

    def release_lock(self) -> None:
        self.lock_path.unlink(missing_ok=True)

    def verified_summary(self) -> dict[str, int]:
        ranges = plan_chunks(
            0, self.item["expected_bytes"], self.args.chunk_size
        )
        complete = []
        for start, end in ranges:
            path = chunk_path(self.chunk_dir, start, end)
            if path.is_file() and path.stat().st_size == end - start + 1:
                complete.append(path)
        verified_bytes = sum(path.stat().st_size for path in complete)
        return {
            "verified_chunk_count": len(complete),
            "verified_chunk_bytes": verified_bytes,
            "missing_chunk_count": len(ranges) - len(complete),
            "missing_bytes": self.item["expected_bytes"] - verified_bytes,
        }

    def write_state(self, status: str, **extra: Any) -> None:
        state = {
            "status": status,
            "dataset": self.manifest.get("dataset_id"),
            "filename": self.item["name"],
            "google_drive_id": self.item.get("google_drive_id"),
            "expected_bytes": self.item["expected_bytes"],
            "round_count": self.round_count,
            "cooldown_seconds": self.args.interval_seconds,
            "updated_at": utc_now(),
            "pid": os.getpid(),
            **self.verified_summary(),
            **extra,
        }
        atomic_json(self.state_path, state)

    def curl_range(
        self, start: int, end: int, output: Path, headers_path: Path
    ) -> tuple[bool, str]:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        headers_path.unlink(missing_ok=True)
        command = [
            "curl",
            "--http1.1",
            "--location",
            "--silent",
            "--show-error",
            "--connect-timeout",
            str(self.args.connect_timeout),
            "--max-time",
            str(self.args.request_timeout),
            "--range",
            f"{start}-{end}",
            "--dump-header",
            str(headers_path),
            "--output",
            str(output),
        ]
        if self.args.proxy:
            command.extend(["--proxy", self.args.proxy])
        command.append(self.item["url"])
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        headers = (
            headers_path.read_text(encoding="utf-8", errors="replace")
            if headers_path.exists()
            else ""
        )
        actual = output.stat().st_size if output.exists() else 0
        with output.open("rb") if output.exists() else open(os.devnull, "rb") as handle:
            preview = handle.read(4096)
        valid = response_is_valid(
            result.returncode,
            actual,
            headers,
            start,
            end,
            self.item["expected_bytes"],
        )
        reason = (
            "pass"
            if valid
            else response_reason(
                result.returncode,
                actual,
                headers,
                preview,
                start,
                end,
                self.item["expected_bytes"],
                result.stderr,
            )
        )
        return valid, reason

    def gate(self, start: int, end: int) -> tuple[bool, str, Path, Path]:
        gate_end = min(end, start + self.args.gate_bytes - 1)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        body = self.gate_dir / f"round_{self.round_count:04d}_{stamp}.body"
        headers = self.gate_dir / f"round_{self.round_count:04d}_{stamp}.headers"
        valid, reason = self.curl_range(start, gate_end, body, headers)
        if valid:
            body.unlink(missing_ok=True)
        return valid, reason, body, headers

    def download_missing_once(self) -> tuple[bool, str, Path | None, Path | None]:
        missing = missing_ranges(
            self.chunk_dir, self.item["expected_bytes"], self.args.chunk_size
        )
        for start, end in missing:
            target = chunk_path(self.chunk_dir, start, end)
            temporary = Path(f"{target}.cooldown.tmp")
            headers = Path(f"{target}.cooldown.headers")
            valid, reason = self.curl_range(start, end, temporary, headers)
            if not valid:
                return False, f"chunk {start}-{end}: {reason}", temporary, headers
            os.replace(temporary, target)
            os.replace(headers, target.with_suffix(".headers"))
            self.write_state(
                "active_range_recovery",
                last_completed_range=[start, end],
            )
        return True, "all_chunks_present", None, None

    def finalize(self) -> None:
        command = [
            sys.executable,
            str(self.args.collector_script.resolve()),
            "--manifest",
            str(self.args.manifest.resolve()),
            "--root",
            str(self.root),
            "--state-stem",
            self.args.state_stem,
            "--workers",
            "1",
            "--chunk-size",
            str(self.args.chunk_size),
            "--max-attempts",
            "1",
        ]
        if self.args.proxy:
            command.extend(["--proxy", self.args.proxy])
        subprocess.run(command, check=True)
        self.write_state("complete", completed_at=utc_now(), next_retry_at=None)

    def sleep_or_exit(self, reason: str, evidence_body: Path, evidence_headers: Path) -> int:
        next_retry = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            seconds=self.args.interval_seconds
        )
        self.write_state(
            "cooldown_quota",
            last_failure=reason,
            evidence_body=str(evidence_body),
            evidence_headers=str(evidence_headers),
            next_retry_at=next_retry.isoformat(),
        )
        if self.args.once:
            return 2
        time.sleep(self.args.interval_seconds)
        return 0

    def run(self) -> int:
        self.acquire_lock()
        try:
            while True:
                self.round_count += 1
                final_path = self.raw / self.item["name"]
                if final_path.is_file() and final_path.stat().st_size == self.item["expected_bytes"]:
                    self.finalize()
                    return 0
                missing = missing_ranges(
                    self.chunk_dir,
                    self.item["expected_bytes"],
                    self.args.chunk_size,
                )
                if not missing:
                    self.finalize()
                    return 0
                start, end = missing[0]
                valid, reason, body, headers = self.gate(start, end)
                if not valid:
                    result = self.sleep_or_exit(reason, body, headers)
                    if result:
                        return result
                    continue
                self.write_state(
                    "gate_pass",
                    gate_range=[start, min(end, start + self.args.gate_bytes - 1)],
                    gate_headers=str(headers),
                )
                completed, reason, failure_body, failure_headers = self.download_missing_once()
                if completed:
                    self.finalize()
                    return 0
                result = self.sleep_or_exit(
                    reason,
                    failure_body or self.gate_dir / "missing_failure_body",
                    failure_headers or self.gate_dir / "missing_failure_headers",
                )
                if result:
                    return result
        finally:
            self.release_lock()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--collector-script", type=Path, required=True)
    parser.add_argument("--state-stem", required=True)
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--interval-seconds", type=int, default=3600)
    parser.add_argument("--gate-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--chunk-size", type=int, default=32 * 1024 * 1024)
    parser.add_argument("--connect-timeout", type=int, default=30)
    parser.add_argument("--request-timeout", type=int, default=240)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    if args.interval_seconds < 60 and not args.once:
        parser.error("--interval-seconds must be at least 60 outside --once tests")
    if args.gate_bytes != 1024 * 1024:
        parser.error("--gate-bytes is fixed at exactly 1 MiB for quota recovery")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.state_stem):
        parser.error("unsafe --state-stem")
    return args


def main(argv: Iterable[str] | None = None) -> int:
    return HourlyRecovery(parse_args(argv)).run()


if __name__ == "__main__":
    raise SystemExit(main())

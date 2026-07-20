#!/usr/bin/env python3
"""Resume OpTC downloads by Google Drive file ID from the saved manifest."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ROOT = Path(
    "/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc"
)
DEFAULT_RCLONE = Path(
    "/opt/data/private/wangwt/ParkAttackKE/tools/rclone/v1.74.3/"
    "rclone-v1.74.3-linux-amd64/rclone"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def append_jsonl(path: Path, value: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def is_present(output: Path, relative: Path) -> bool:
    return (output / relative).is_file() or (output / "OpTCNCR" / relative).is_file()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--rclone", type=Path, default=DEFAULT_RCLONE)
    parser.add_argument("--config", type=Path, default=Path("/root/.config/rclone/rclone.conf"))
    parser.add_argument("--remote", default="optc_gdrive:")
    parser.add_argument("--proxy", default="socks5://127.0.0.1:9998")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--retries", type=int, default=20)
    args = parser.parse_args()

    manifest_path = args.root / "manifests" / "gdrive_file_tree.json"
    output = args.root / "raw_original"
    state_dir = args.root / "state"
    log_dir = args.root / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest["files"]
    missing = [item for item in files if not is_present(output, Path(item["path"]))]
    if args.limit > 0:
        missing = missing[: args.limit]

    state_path = state_dir / "original_manifest_download_state.json"
    events_path = log_dir / "original_manifest_download_events.jsonl"
    state = {
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "manifest_total": len(files),
        "initially_missing": len(missing),
        "attempted": 0,
        "downloaded": 0,
        "failed": 0,
        "remaining": len(missing),
        "complete": False,
    }
    atomic_json(state_path, state)

    environment = os.environ.copy()
    environment.update(
        {
            "ALL_PROXY": args.proxy,
            "HTTPS_PROXY": args.proxy,
            "HTTP_PROXY": args.proxy,
        }
    )

    failures: list[dict] = []
    for index, item in enumerate(missing, start=1):
        relative = Path(item["path"])
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(args.rclone),
            "backend",
            "copyid",
            args.remote,
            item["id"],
            str(destination),
            "--config",
            str(args.config),
            "--drive-acknowledge-abuse",
            "--retries",
            str(args.retries),
            "--low-level-retries",
            str(args.retries),
            "--contimeout",
            "30s",
            "--timeout",
            "10m",
        ]
        started = time.monotonic()
        result = subprocess.run(
            command,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        event = {
            "time": utc_now(),
            "index": index,
            "total": len(missing),
            "id": item["id"],
            "path": item["path"],
            "seconds": round(time.monotonic() - started, 3),
            "returncode": result.returncode,
        }
        state["attempted"] = index
        if result.returncode == 0 and destination.is_file():
            state["downloaded"] += 1
            event["status"] = "downloaded"
            event["size"] = destination.stat().st_size
        else:
            state["failed"] += 1
            event["status"] = "failed"
            event["output"] = result.stdout[-2000:]
            failures.append(event)
        state["remaining"] = len(missing) - index
        state["updated_at"] = utc_now()
        append_jsonl(events_path, event)
        atomic_json(state_path, state)
        print(
            f"[{index}/{len(missing)}] {event['status']} {item['path']}",
            flush=True,
        )

    remaining_after = sum(
        1 for item in files if not is_present(output, Path(item["path"]))
    )
    state["remaining_after_audit"] = remaining_after
    state["complete"] = remaining_after == 0
    state["finished_at"] = utc_now()
    state["updated_at"] = utc_now()
    atomic_json(state_path, state)
    if failures:
        atomic_json(state_dir / "original_manifest_download_failures.json", {"files": failures})
    return 0 if state["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

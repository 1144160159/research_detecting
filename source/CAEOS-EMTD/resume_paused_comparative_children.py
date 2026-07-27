from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import time
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def process_status(pid: int, proc_root: Path = Path("/proc")) -> dict[str, Any] | None:
    path = proc_root / str(pid) / "status"
    if not path.is_file():
        return None
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key] = value.strip()
    return {
        "pid": pid,
        "name": fields.get("Name"),
        "state": fields.get("State", "").split(maxsplit=1)[0],
        "ppid": int(fields.get("PPid", "-1")),
    }


def direct_children(parent_pid: int, proc_root: Path = Path("/proc")) -> list[int]:
    result = []
    for path in proc_root.iterdir():
        if not path.name.isdigit():
            continue
        status = process_status(int(path.name), proc_root)
        if status is not None and status["ppid"] == parent_pid:
            result.append(int(path.name))
    return sorted(result)


def validate_run_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("schema_version") != "strict_v4_comparative_parallel_run_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError("parallel run manifest validation failed")
    return value


def write_record(path: Path, value: dict[str, Any]) -> None:
    payload = dict(value)
    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--child-pids", type=int, nargs="+", required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--effective-active-workers", type=int, required=True)
    parser.add_argument("--peak-load-one", type=float, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"resume record already exists: {args.output}")
    if args.poll_seconds < 1:
        raise ValueError("poll interval must be at least one second")
    if len(set(args.child_pids)) != len(args.child_pids):
        raise ValueError("paused child PIDs must be unique")

    run_manifest = validate_run_manifest(args.run_manifest.resolve())
    expected = sorted(args.child_pids)
    started = time.time()
    while True:
        parent = process_status(args.parent_pid)
        children = direct_children(args.parent_pid)
        expected_status = {
            pid: process_status(pid)
            for pid in expected
        }
        if parent is None:
            write_record(
                args.output,
                {
                    "schema_version": "strict_v4_comparative_resume_record_v1",
                    "status": "failed_parent_exited_before_resume",
                    "parent_pid": args.parent_pid,
                    "paused_child_pids": expected,
                    "run_manifest_sha256": run_manifest["manifest_sha256"],
                    "monitor_sha256": file_hash(Path(__file__)),
                    "started_at_unix": started,
                    "finished_at_unix": time.time(),
                },
            )
            raise RuntimeError("parallel parent exited before paused children resumed")
        invalid = {
            pid: status
            for pid, status in expected_status.items()
            if status is None
            or status["ppid"] != args.parent_pid
            or status["state"] != "T"
        }
        if invalid:
            write_record(
                args.output,
                {
                    "schema_version": "strict_v4_comparative_resume_record_v1",
                    "status": "failed_paused_child_identity",
                    "parent_pid": args.parent_pid,
                    "paused_child_pids": expected,
                    "invalid_status": invalid,
                    "run_manifest_sha256": run_manifest["manifest_sha256"],
                    "monitor_sha256": file_hash(Path(__file__)),
                    "started_at_unix": started,
                    "finished_at_unix": time.time(),
                },
            )
            raise RuntimeError("paused child identity changed before resume")
        other_children = sorted(set(children) - set(expected))
        if not other_children:
            for pid in expected:
                os.kill(pid, signal.SIGCONT)
            write_record(
                args.output,
                {
                    "schema_version": "strict_v4_comparative_resume_record_v1",
                    "status": "resumed",
                    "parent_pid": args.parent_pid,
                    "paused_child_pids": expected,
                    "run_manifest_sha256": run_manifest["manifest_sha256"],
                    "monitor_sha256": file_hash(Path(__file__)),
                    "effective_active_workers_before_resume": (
                        args.effective_active_workers
                    ),
                    "recorded_peak_load_one": args.peak_load_one,
                    "other_direct_children_before_resume": other_children,
                    "started_at_unix": started,
                    "resumed_at_unix": time.time(),
                },
            )
            return
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()

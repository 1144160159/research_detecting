from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from snapshot_strict_v4_rrc_csr_progress import (
    build_snapshot,
    file_hash,
    load,
    write_atomic,
)


SCHEMA = "strict_v4_rrc_csr_realtime_progress_watcher_state_v1"
TERMINAL_SCHEMAS = {
    "summary.json": "strict_v4_rrc_csr_confirmation_summary_v1",
    "audit.json": "strict_v4_rrc_csr_confirmation_audit_v1",
    "execution_complete.json": "strict_v4_rrc_csr_execution_complete_v1",
}


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pid_path = path / "pid"
    try:
        path.mkdir()
    except FileExistsError:
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pid = -1
        if pid > 0 and process_exists(pid):
            raise RuntimeError("RRC realtime watcher is already active")
        try:
            pid_path.unlink()
        except FileNotFoundError:
            pass
        path.rmdir()
        path.mkdir()
    pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    return path


def release_lock(path: Path) -> None:
    try:
        (path / "pid").unlink()
    except FileNotFoundError:
        pass
    try:
        path.rmdir()
    except FileNotFoundError:
        pass


def runner_pids() -> list[int]:
    pids = []
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            command = path.read_bytes().replace(b"\0", b" ").decode(
                "utf-8", errors="replace"
            )
        except OSError:
            continue
        if "run_strict_v4_rrc_csr_confirmation.py" in command:
            pids.append(int(path.parent.name))
    return sorted(pids)


def terminal_evidence(result_root: Path) -> dict[str, Any]:
    files = {}
    valid = True
    for name, schema in TERMINAL_SCHEMAS.items():
        path = result_root / name
        if not path.is_file():
            files[name] = {"exists": False}
            valid = False
            continue
        try:
            value = load(path)
            canonical = bool(
                value.get("schema_version") == schema
                and value.get("manifest_sha256") == canonical_hash(value)
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            canonical = False
        files[name] = {
            "exists": True,
            "file_sha256": file_hash(path),
            "canonical_valid": canonical,
        }
        valid = valid and canonical
    return {"complete": valid, "files": files}


def observe_once(
    *,
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
    output_path: Path,
    state_path: Path,
) -> dict[str, Any]:
    snapshot = build_snapshot(protocol_path, run_root)
    write_atomic(output_path, snapshot)
    terminal = terminal_evidence(result_root)
    pids = runner_pids()
    state: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": (
            "terminal_rrc_evidence_available"
            if terminal["complete"]
            else "rrc_running_valid_partial_progress"
            if pids
            else "rrc_runner_absent_before_terminal"
        ),
        "snapshot_manifest_sha256": snapshot["manifest_sha256"],
        "snapshot_file_sha256": file_hash(output_path),
        "snapshot_state": snapshot["state"],
        "observed_at_utc": snapshot["observed_at_utc"],
        "counts": {
            name: {
                "present": item["present_count"],
                "expected": item["expected_count"],
                "pending": item["pending_count"],
                "invalid": item["invalid_count"],
            }
            for name, item in snapshot["inventory"].items()
        },
        "runner_pids": pids,
        "terminal_evidence": terminal,
        "partial_effect_aggregation_performed": False,
        "partial_effect_claim_authorized": False,
    }
    state["manifest_sha256"] = canonical_hash(state)
    write_atomic(state_path, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    lock = acquire_lock(args.state.with_suffix(".lock.d"))
    try:
        while True:
            state = observe_once(
                protocol_path=args.protocol,
                run_root=args.run_root,
                result_root=args.result_root,
                output_path=args.output,
                state_path=args.state,
            )
            print(json.dumps(state, sort_keys=True), flush=True)
            if args.once or state["state"] == "terminal_rrc_evidence_available":
                return
            time.sleep(max(10, int(args.interval_seconds)))
    finally:
        release_lock(lock)


if __name__ == "__main__":
    main()

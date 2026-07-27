from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


EXPECTED_COMMAND = "wait_and_run_strict_v4_medaf_tabular_pilot.sh"


def process_state(pid: int) -> str:
    status = Path(f"/proc/{int(pid)}/status").read_text(encoding="utf-8")
    for line in status.splitlines():
        if line.startswith("State:"):
            return line.split()[1]
    raise ValueError("process state is missing")


def process_command(pid: int) -> str:
    raw = Path(f"/proc/{int(pid)}/cmdline").read_bytes()
    return raw.replace(b"\0", b" ").decode("utf-8", errors="replace").strip()


def validate_paused_medaf(pid: int) -> Dict[str, str]:
    command = process_command(pid)
    state = process_state(pid)
    if EXPECTED_COMMAND not in command:
        raise ValueError("target PID is not the MEDAF watcher")
    if state != "T":
        raise ValueError("MEDAF watcher must be stopped before monitoring")
    return {"command": command, "state": state}


def resume(
    pid: int,
    branch_marker: Path,
    output: Path,
    poll_seconds: float,
) -> Dict[str, object]:
    initial = validate_paused_medaf(pid)
    while not branch_marker.is_file():
        if not Path(f"/proc/{int(pid)}").exists():
            raise RuntimeError("paused MEDAF watcher exited before MDR branch")
        time.sleep(float(poll_seconds))
    before = validate_paused_medaf(pid)
    marker_sha256 = hashlib.sha256(branch_marker.read_bytes()).hexdigest()
    os.kill(int(pid), signal.SIGCONT)
    deadline = time.monotonic() + 30.0
    after_state = process_state(pid)
    while after_state == "T" and time.monotonic() < deadline:
        time.sleep(0.1)
        after_state = process_state(pid)
    if after_state == "T":
        raise RuntimeError("MEDAF watcher did not resume")
    value: Dict[str, object] = {
        "schema_version": (
            "strict_v4_medaf_after_mdr_confirmation_resume_record_v1"
        ),
        "state": "resumed",
        "medaf_watcher_pid": int(pid),
        "expected_command": EXPECTED_COMMAND,
        "initial": initial,
        "before_resume": before,
        "after_resume_state": after_state,
        "mdr_branch_marker": str(branch_marker),
        "mdr_branch_marker_sha256": marker_sha256,
        "resumed_utc": datetime.now(timezone.utc).isoformat(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--medaf-pid", type=int, required=True)
    parser.add_argument("--mdr-branch-marker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    args = parser.parse_args()
    value = resume(
        args.medaf_pid,
        args.mdr_branch_marker.resolve(),
        args.output.resolve(),
        args.poll_seconds,
    )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()

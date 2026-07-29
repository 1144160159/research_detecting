from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def pid_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return pid > 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--child-pid", type=int, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--launcher-state", type=Path, required=True)
    args = parser.parse_args()
    if args.launcher_state.is_file():
        previous = load(args.launcher_state)
        if pid_is_alive(int(previous.get("pid", -1))):
            previous["reused_existing_process"] = True
            print(json.dumps(previous, ensure_ascii=False, sort_keys=True))
            return
    project_root = args.project_root.resolve()
    command = [
        str(args.python.resolve()),
        str(project_root / "reschedule_strict_v4_rrc_at_task_boundary.py"),
        "--project-root",
        str(project_root),
        "--parent-pid",
        str(args.parent_pid),
        "--child-pid",
        str(args.child_pid),
        "--state",
        str(args.state.resolve()),
        "--log",
        str(args.log.resolve()),
    ]
    log_path = args.launcher_state.parent / "boundary_rescheduler.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab", buffering=0) as log:
        process = subprocess.Popen(
            command,
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    state: dict[str, Any] = {
        "schema_version": "strict_v4_rrc_boundary_rescheduler_launcher_v1",
        "pid": process.pid,
        "launched_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "log_path": str(log_path),
        "reused_existing_process": False,
    }
    args.launcher_state.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.launcher_state.with_suffix(args.launcher_state.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, args.launcher_state)
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

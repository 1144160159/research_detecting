from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def launch(
    *,
    project_root: Path,
    protocol_path: Path,
    python: str,
    state_path: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol_path = protocol_path.resolve()
    protocol = load(protocol_path)
    result_root = project_root / protocol["execution"]["result_root"]
    if (result_root / "completion.json").exists():
        raise ValueError("confirmation is already complete")
    if state_path.is_file():
        previous = load(state_path)
        previous_pid = int(previous.get("pid", -1))
        if pid_is_alive(previous_pid):
            return {**previous, "reused_existing_process": True}

    result_root.mkdir(parents=True, exist_ok=True)
    log_path = result_root / "runner.log"
    command = [
        python,
        str(project_root / "run_strict_v4_core_warning_confirmation.py"),
        "--project-root",
        str(project_root),
        "--protocol",
        str(protocol_path),
        "--python",
        python,
    ]
    environment = dict(os.environ)
    environment.update(
        {
            str(key): str(value)
            for key, value in protocol["execution"]["thread_limits"].items()
        }
    )
    with log_path.open("ab", buffering=0) as log:
        process = subprocess.Popen(
            command,
            cwd=project_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    state: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_launcher_state_v1",
        "pid": process.pid,
        "launched_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "project_root": str(project_root),
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "log_path": str(log_path),
        "reused_existing_process": False,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, state_path)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    state = launch(
        project_root=args.project_root,
        protocol_path=args.protocol,
        python=str(args.python),
        state_path=args.state,
    )
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

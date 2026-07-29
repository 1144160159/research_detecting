from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


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
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    if args.state.is_file():
        previous = load(args.state)
        if pid_is_alive(int(previous.get("pid", -1))):
            previous["reused_existing_process"] = True
            print(json.dumps(previous, ensure_ascii=False, sort_keys=True))
            return
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = load(protocol_path)
    runner = project_root / protocol["execution"]["runner_file"]
    result_root = project_root / protocol["result_root"]
    result_root.mkdir(parents=True, exist_ok=True)
    command = [
        str(args.python.resolve()),
        str(runner),
        "--project-root",
        str(project_root),
        "--protocol",
        str(protocol_path),
        "--python",
        str(args.python.resolve()),
    ]
    log_path = result_root / "runner.log"
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
        "schema_version": "strict_v4_xgboost_warning_parallel_launcher_v1",
        "pid": process.pid,
        "launched_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "command": command,
        "log_path": str(log_path),
        "reused_existing_process": False,
    }
    state["manifest_sha256"] = canonical_hash(state)
    args.state.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.state.with_suffix(args.state.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, args.state)
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

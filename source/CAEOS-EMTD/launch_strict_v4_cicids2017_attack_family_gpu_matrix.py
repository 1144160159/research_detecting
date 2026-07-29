from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    state_path = args.state.resolve()
    if state_path.is_file():
        previous = json.loads(state_path.read_text(encoding="utf-8"))
        previous_pid = int(previous.get("pid", 0))
        if previous_pid and process_alive(previous_pid):
            previous["reused_existing_process"] = True
            print(json.dumps(previous, ensure_ascii=False, sort_keys=True))
            return
    project_root = args.project_root.resolve()
    command = [
        str(args.python.resolve()),
        str(
            project_root
            / "run_strict_v4_cicids2017_attack_family_gpu_matrix.py"
        ),
        "--project-root",
        str(project_root),
        "--protocol",
        str(args.protocol.resolve()),
        "--python",
        str(args.python.resolve()),
    ]
    args.log.resolve().parent.mkdir(parents=True, exist_ok=True)
    log = args.log.resolve().open("a", encoding="utf-8")
    environment = dict(os.environ)
    environment["CUDA_VISIBLE_DEVICES"] = "0"
    process = subprocess.Popen(
        command,
        cwd=project_root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    state = {
        "schema_version": "strict_v4_attack_family_gpu_launcher_v1",
        "launched_at_utc": datetime.now(timezone.utc).isoformat(),
        "pid": process.pid,
        "command": command,
        "cuda_visible_devices": environment["CUDA_VISIBLE_DEVICES"],
        "log_path": str(args.log.resolve()),
        "reused_existing_process": False,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

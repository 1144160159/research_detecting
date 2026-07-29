from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from launch_strict_v4_cicids2017_packet_sequence_materialization import (
    process_is_alive,
)
from strict_v4_cicids2017_attack_family import atomic_json, canonical_hash, file_hash


def launch(args: argparse.Namespace) -> dict[str, Any]:
    state_path = args.launch_state.resolve()
    if state_path.is_file():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        pid = int(existing.get("pid", -1))
        if existing.get("state") == "launched" and process_is_alive(pid):
            raise RuntimeError(f"development coordinator already runs as PID {pid}")
    project_root = args.project_root.resolve()
    coordinator = (
        project_root / "coordinate_strict_v4_packet_sequence_fusion_development.py"
    )
    command = [
        str(args.python.resolve()),
        str(coordinator),
        "--python",
        str(args.python.resolve()),
        "--project-root",
        str(project_root),
        "--sequence-dataset",
        str(args.sequence_dataset.resolve()),
        "--result-root",
        str(args.result_root.resolve()),
        "--run-root",
        str(args.run_root.resolve()),
        "--state-output",
        str(args.coordinator_state.resolve()),
        "--maximum-parallel-tasks",
        str(args.maximum_parallel_tasks),
        "--poll-seconds",
        str(args.poll_seconds),
        "--maximum-wait-seconds",
        str(args.maximum_wait_seconds),
    ]
    args.log.resolve().parent.mkdir(parents=True, exist_ok=True)
    log_handle = args.log.resolve().open("ab", buffering=0)
    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log_handle.close()
    state: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_launch_v1",
        "state": "launched",
        "pid": process.pid,
        "started_unix_seconds": time.time(),
        "command": command,
        "log": str(args.log.resolve()),
        "coordinator_state": str(args.coordinator_state.resolve()),
        "source": {
            "coordinator": str(coordinator),
            "coordinator_sha256": file_hash(coordinator),
        },
        "claim_boundary": {
            "development_only": True,
            "confirmation_seeds_read_or_launched": False,
        },
    }
    state["manifest_sha256"] = canonical_hash(state)
    atomic_json(state_path, state)
    return state


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--launch-state", type=Path, required=True)
    parser.add_argument("--coordinator-state", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--maximum-parallel-tasks", type=int, default=4)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--maximum-wait-seconds", type=float, default=21600.0)
    return parser.parse_args()


def main() -> None:
    state = launch(parse_arguments())
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

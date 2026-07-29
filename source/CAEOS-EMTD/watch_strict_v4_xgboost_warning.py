from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def parent_ready(project_root: Path, protocol: dict[str, Any]) -> bool:
    parent_protocol = load(project_root / protocol["parent_protocol"]["path"])
    completion = (
        project_root
        / parent_protocol["execution"]["result_root"]
        / "completion.json"
    )
    if not completion.is_file():
        return False
    payload = load(completion)
    return payload.get("state") == "complete" and payload.get(
        "integrity_passes"
    ) is True


def watcher_state(
    project_root: Path, protocol: dict[str, Any], status: str
) -> dict[str, Any]:
    run_root = project_root / protocol["run_root"]
    result_root = project_root / protocol["result_root"]
    return {
        "schema_version": "strict_v4_xgboost_warning_watcher_state_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "metrics_count": (
            len(list(run_root.rglob("metrics.json"))) if run_root.exists() else 0
        ),
        "expected_task_count": protocol["expected_task_count"],
        "summary_exists": (result_root / "summary.json").is_file(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = load(protocol_path)
    result_root = project_root / protocol["result_root"]
    while True:
        if (result_root / "summary.json").is_file():
            atomic_write(
                args.state, watcher_state(project_root, protocol, "complete")
            )
            return
        if parent_ready(project_root, protocol):
            atomic_write(
                args.state, watcher_state(project_root, protocol, "running")
            )
            subprocess.run(
                [
                    str(args.python),
                    str(project_root / "run_strict_v4_xgboost_warning_matrix.py"),
                    "--project-root",
                    str(project_root),
                    "--protocol",
                    str(protocol_path),
                    "--python",
                    str(args.python),
                ],
                cwd=project_root,
                check=True,
            )
            atomic_write(
                args.state, watcher_state(project_root, protocol, "complete")
            )
            return
        atomic_write(
            args.state,
            watcher_state(
                project_root, protocol, "waiting_for_pairwise_confirmation"
            ),
        )
        if args.once:
            return
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()

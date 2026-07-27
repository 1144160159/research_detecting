from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

from create_strict_v4_external_confirmation_protocol import canonical_hash


HEAVY_PROCESS_MARKERS = (
    "run_strict_v4_comp_confirmation.sh",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "run_strict_v4_krc_csr_confirmation.py",
    "capture_krc_csr_confirmation_runtime.py",
    "evaluate_krc_csr_confirmation_runtime.py",
    "train_mdr_caeos_open_set.py",
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def process_commands(proc_root: Path = Path("/proc")) -> list[str]:
    commands: list[str] = []
    if not proc_root.is_dir():
        return commands
    for child in proc_root.iterdir():
        if not child.name.isdigit():
            continue
        try:
            raw = (child / "cmdline").read_bytes()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        command = raw.replace(b"\0", b" ").decode("utf-8", errors="replace")
        if command:
            commands.append(command)
    return commands


def busy_commands(
    commands: Iterable[str],
    markers: tuple[str, ...] = HEAVY_PROCESS_MARKERS,
) -> list[str]:
    return sorted(
        command
        for command in commands
        if any(marker in command for marker in markers)
        and "watch_strict_v4_comp_cross_suite_confirmation.py" not in command
    )


def run_logged(command: list[str], log_path: Path, root: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            cwd=root,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def wait_for_idle(
    interval_seconds: int,
    required_idle_polls: int,
    status_path: Path,
) -> None:
    idle_polls = 0
    while idle_polls < required_idle_polls:
        busy = busy_commands(process_commands())
        idle_polls = idle_polls + 1 if not busy else 0
        status = {
            "schema_version": (
                "strict_v4_comp_cross_suite_resource_wait_v1"
            ),
            "state": "idle_confirming" if not busy else "busy",
            "idle_polls": idle_polls,
            "required_idle_polls": required_idle_polls,
            "busy_process_count": len(busy),
            "busy_commands": busy,
        }
        temporary = status_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(status, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(status_path)
        if idle_polls < required_idle_polls:
            time.sleep(interval_seconds)


def validate_activation(path: Path) -> str:
    activation = load(path)
    if (
        activation.get("schema_version")
        != "strict_v4_comp_cross_suite_activation_v1"
        or activation.get("manifest_sha256") != canonical_hash(activation)
        or activation.get("state")
        not in {
            "positive_activation",
            "negative_not_required_retain_pairwise",
        }
    ):
        raise ValueError("canonical terminal activation required")
    return str(activation["state"])


def watch(
    root: Path,
    interval_seconds: int,
    required_idle_polls: int,
) -> str:
    result_root = (
        root / "results/strict_v4_comp_cross_suite_confirmation_v1"
    )
    pilot_confirmation = (
        root / "results/strict_v4_comp_confirmation_v1/confirmation.json"
    )
    activation = result_root / "activation_decision.json"
    protocol = result_root / "execution_protocol.json"
    result_root.mkdir(parents=True, exist_ok=True)

    while not pilot_confirmation.is_file():
        time.sleep(interval_seconds)
    run_logged(
        [
            sys.executable,
            str(root / "write_strict_v4_comp_cross_suite_activation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_activation.log",
        root,
    )
    state = validate_activation(activation)
    if state == "negative_not_required_retain_pairwise":
        return state

    run_logged(
        [
            sys.executable,
            str(
                root
                / "create_strict_v4_comp_cross_suite_execution_protocol.py"
            ),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_protocol.log",
        root,
    )
    if not protocol.is_file():
        raise ValueError("positive activation did not create a protocol")
    wait_for_idle(
        interval_seconds,
        required_idle_polls,
        result_root / "resource_wait.json",
    )
    run_logged(
        [
            sys.executable,
            str(root / "run_strict_v4_comp_cross_suite_confirmation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_runner.log",
        root,
    )
    completion = result_root / "execution_complete.json"
    if not completion.is_file():
        raise ValueError("runner exited without canonical completion")
    return "complete"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--required-idle-polls", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.interval_seconds <= 0 or args.required_idle_polls <= 0:
        raise ValueError("positive watcher timing controls required")
    root = args.project_root.resolve()
    result_root = (
        root / "results/strict_v4_comp_cross_suite_confirmation_v1"
    )
    lock = result_root / "watcher.lock.d"
    result_root.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        print("state=watcher_already_active")
        return
    try:
        state = watch(
            root,
            args.interval_seconds,
            args.required_idle_polls,
        )
        print(f"state={state}")
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

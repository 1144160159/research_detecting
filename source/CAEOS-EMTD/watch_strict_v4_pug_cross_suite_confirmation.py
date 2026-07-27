from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from create_strict_v4_external_confirmation_protocol import canonical_hash


BUSY_PATTERNS = (
    "run_strict_v4_krc_csr_confirmation.py",
    "capture_krc_csr_confirmation_runtime.py",
    "evaluate_krc_csr_confirmation_runtime.py",
    "run_strict_v4_krc_external_malicious.py",
    "run_strict_v4_krc_selected_system.py",
    "run_strict_v4_krc_opendetect_efficiency.py",
    "run_strict_v4_krc_parrot_safety.py",
    "wait_and_run_strict_v4_rrc_csr_confirmation.sh",
    "run_strict_v4_rrc_csr_confirmation.py",
    "run_strict_v4_rrc_csr_capture_pipeline.py",
    "materialize_rrc_csr_runtime.py",
    "evaluate_rrc_csr_runtime.py",
    "certify_rrc_csr_scenario.py",
    "run_strict_v4_pug_confirmation.sh",
    "watch_strict_v4_pug_confirmation.py",
    "run_strict_v4_pug_cross_suite_confirmation.py",
    "run_strict_v4_mdr",
    "run_strict_v4_comp",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "train_mdr_caeos_open_set.py",
)


def load(path: Path) -> dict[str, Any]:
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
        command = raw.replace(b"\0", b" ").decode(
            "utf-8", errors="replace"
        )
        if command:
            commands.append(command)
    return commands


def busy_commands(
    commands: Iterable[str],
    markers: tuple[str, ...] = BUSY_PATTERNS,
) -> list[str]:
    return sorted(
        {
            command
            for command in commands
            if any(marker in command for marker in markers)
            and "watch_strict_v4_pug_cross_suite_confirmation.py"
            not in command
        }
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open(
        "w", encoding="utf-8", newline="\n"
    ) as destination:
        destination.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def run_logged(command: list[str], log_path: Path, root: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            cwd=root,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def validate_activation(path: Path) -> str:
    activation = load(path)
    if (
        activation.get("schema_version")
        != "strict_v4_pug_cross_suite_activation_v1"
        or activation.get("manifest_sha256") != canonical_hash(activation)
        or activation.get("state")
        not in {
            "positive_activation",
            "negative_not_required_retain_upstream_incumbent",
        }
    ):
        raise ValueError("canonical terminal PUG activation required")
    return str(activation["state"])


def pilot_confirmation_ready(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        confirmation = load(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return False
    return bool(
        confirmation.get("schema_version")
        == "strict_v4_pug_confirmation_v1"
        and confirmation.get("manifest_sha256")
        == canonical_hash(confirmation)
        and confirmation.get("task_count") == 18
        and isinstance(confirmation.get("decision", {}).get("passes"), bool)
    )


def resource_state(
    *,
    prior_idle_count: int,
    required_idle_polls: int,
    commands: Iterable[str] | None = None,
) -> tuple[dict[str, Any], int]:
    busy = busy_commands(
        process_commands() if commands is None else commands
    )
    idle_count = 0 if busy else prior_idle_count + 1
    return (
        {
            "state": "waiting_for_resources" if busy else "resources_idle",
            "busy_process_count": len(busy),
            "busy_processes": busy,
            "idle_consecutive_polls": idle_count,
            "required_idle_consecutive_polls": required_idle_polls,
            "launched": False,
        },
        idle_count,
    )


def inspect_once(
    root: Path,
    *,
    prior_idle_count: int = 0,
    required_idle_polls: int = 3,
    commands: Iterable[str] | None = None,
) -> tuple[dict[str, Any], int]:
    result_root = (
        root / "results/strict_v4_pug_cross_suite_confirmation_v1"
    )
    pilot = root / "results/strict_v4_pug_confirmation_v1/confirmation.json"
    activation = result_root / "activation_decision.json"
    protocol = result_root / "execution_protocol.json"
    completion = result_root / "execution_complete.json"
    if completion.is_file():
        return {"state": "terminal_completion_present", "launched": False}, 0
    if not pilot_confirmation_ready(pilot):
        return {"state": "waiting_for_pilot_confirmation", "launched": False}, 0
    if not activation.is_file():
        return {"state": "pilot_complete_activation_pending", "launched": False}, 0
    state = validate_activation(activation)
    if state == "negative_not_required_retain_upstream_incumbent":
        return {"state": state, "launched": False}, 0
    if not protocol.is_file():
        return {
            "state": "positive_activation_protocol_pending",
            "launched": False,
        }, 0
    return resource_state(
        prior_idle_count=prior_idle_count,
        required_idle_polls=required_idle_polls,
        commands=commands,
    )


def wait_for_idle(
    interval_seconds: int,
    required_idle_polls: int,
    status_path: Path,
) -> None:
    idle_polls = 0
    while idle_polls < required_idle_polls:
        state, idle_polls = resource_state(
            prior_idle_count=idle_polls,
            required_idle_polls=required_idle_polls,
        )
        write_json(status_path, state)
        if idle_polls < required_idle_polls:
            time.sleep(interval_seconds)


def watch(
    root: Path,
    interval_seconds: int,
    required_idle_polls: int,
) -> str:
    result_root = (
        root / "results/strict_v4_pug_cross_suite_confirmation_v1"
    )
    pilot = root / "results/strict_v4_pug_confirmation_v1/confirmation.json"
    activation = result_root / "activation_decision.json"
    protocol = result_root / "execution_protocol.json"
    result_root.mkdir(parents=True, exist_ok=True)

    while not pilot_confirmation_ready(pilot):
        write_json(
            result_root / "watcher_state.json",
            {"state": "waiting_for_pilot_confirmation", "launched": False},
        )
        time.sleep(interval_seconds)
    run_logged(
        [
            sys.executable,
            str(root / "write_strict_v4_pug_cross_suite_activation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_activation.log",
        root,
    )
    state = validate_activation(activation)
    if state == "negative_not_required_retain_upstream_incumbent":
        write_json(
            result_root / "watcher_state.json",
            {"state": state, "launched": False},
        )
        return state

    run_logged(
        [
            sys.executable,
            str(
                root
                / "create_strict_v4_pug_cross_suite_execution_protocol.py"
            ),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_protocol.log",
        root,
    )
    if not protocol.is_file():
        raise ValueError("positive PUG activation did not create a protocol")
    wait_for_idle(
        interval_seconds,
        required_idle_polls,
        result_root / "resource_wait.json",
    )
    run_logged(
        [
            sys.executable,
            str(root / "run_strict_v4_pug_cross_suite_confirmation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "watcher_runner.log",
        root,
    )
    completion = result_root / "execution_complete.json"
    if not completion.is_file():
        raise ValueError("runner exited without canonical completion")
    write_json(
        result_root / "watcher_state.json",
        {"state": "complete", "launched": True},
    )
    return "complete"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--required-idle-polls", type=int, default=3)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.interval_seconds <= 0 or args.required_idle_polls <= 0:
        raise ValueError("positive watcher timing controls required")
    root = args.project_root.resolve()
    result_root = (
        root / "results/strict_v4_pug_cross_suite_confirmation_v1"
    )
    result_root.mkdir(parents=True, exist_ok=True)
    if args.once:
        state, _idle = inspect_once(
            root,
            required_idle_polls=args.required_idle_polls,
        )
        if not args.no_launch and state["state"] == "resources_idle":
            raise ValueError("--once launch is forbidden; use persistent mode")
        write_json(result_root / "watcher_state.json", state)
        print(json.dumps(state, sort_keys=True))
        return

    lock = result_root / "watcher.lock.d"
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

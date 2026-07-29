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
from run_strict_v4_krc_csr_confirmation import validate_capture


SCHEMA = "strict_v4_krc_coordinator_recovery_watcher_state_v1"
WATCHER_NAME = "watch_strict_v4_krc_coordinator_recovery.py"
COORDINATOR_NAME = "run_strict_v4_krc_csr_confirmation.py"
WORKER_NAMES = (
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "train_hybrid_open_set.py",
    "train_mdr_caeos_open_set.py",
    "evaluate_krc_csr_confirmation_runtime.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def state_value(state: str, **values: Any) -> dict[str, Any]:
    output: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": state,
        **values,
    }
    output["manifest_sha256"] = canonical_hash(output)
    return output


def process_commands(proc_root: Path = Path("/proc")) -> list[str]:
    commands = []
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


def relevant_commands(commands: Iterable[str]) -> dict[str, list[str]]:
    observed = [
        command for command in commands if WATCHER_NAME not in command
    ]
    return {
        "coordinator": sorted(
            {
                command
                for command in observed
                if COORDINATOR_NAME in command
            }
        ),
        "workers": sorted(
            {
                command
                for command in observed
                if any(name in command for name in WORKER_NAMES)
            }
        ),
    }


def capture_root(run_root: Path, task: dict[str, Any]) -> Path:
    return (
        run_root
        / "captures"
        / task["suite"]
        / task["scenario"]
        / f"seed{int(task['training_seed'])}"
    )


def scan_captures(
    protocol: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    weight = float(
        protocol["confirmation"]["fixed_augmentation_weight"]
    )
    completed = 0
    partial = []
    absent = 0
    for task in protocol["confirmation"]["tasks"]:
        directory = capture_root(run_root, task)
        manifest = directory / "capture_manifest.json"
        if validate_capture(
            manifest,
            suite=task["suite"],
            scenario=task["scenario"],
            training_seed=int(task["training_seed"]),
            weight=weight,
        ):
            completed += 1
        elif directory.is_dir() and any(directory.iterdir()):
            partial.append(
                str(directory.relative_to(run_root)).replace("\\", "/")
            )
        else:
            absent += 1
    return {
        "expected_capture_count": len(
            protocol["confirmation"]["tasks"]
        ),
        "complete_capture_count": completed,
        "absent_capture_count": absent,
        "partial_capture_count": len(partial),
        "partial_capture_paths": partial,
    }


def recovery_decision(
    *,
    process_state: dict[str, list[str]],
    capture_state: dict[str, Any],
    terminal_outputs_present: bool,
    prior_idle_count: int,
    required_idle_polls: int,
) -> tuple[dict[str, Any], int]:
    if required_idle_polls <= 0:
        raise ValueError("positive idle poll requirement required")
    base = {
        "coordinator_process_count": len(
            process_state["coordinator"]
        ),
        "worker_process_count": len(process_state["workers"]),
        "coordinator_processes": process_state["coordinator"],
        "worker_processes": process_state["workers"],
        **capture_state,
        "required_idle_consecutive_polls": required_idle_polls,
        "restart_admitted": False,
    }
    if terminal_outputs_present:
        return state_value(
            "terminal_krc_outputs_present_no_restart", **base
        ), 0
    if (
        process_state["coordinator"]
        or process_state["workers"]
    ):
        return state_value(
            "waiting_for_existing_krc_processes_to_drain",
            **base,
            idle_consecutive_polls=0,
        ), 0
    if int(capture_state["partial_capture_count"]) > 0:
        return state_value(
            "manual_partial_capture_intervention_required",
            **base,
            idle_consecutive_polls=0,
        ), 0
    idle_count = prior_idle_count + 1
    admitted = idle_count >= required_idle_polls
    return state_value(
        (
            "clean_drain_restart_admitted"
            if admitted
            else "clean_drain_waiting_for_stability"
        ),
        **{**base, "restart_admitted": admitted},
        idle_consecutive_polls=idle_count,
    ), idle_count


def terminal_outputs_present(result_root: Path) -> bool:
    summary = result_root / "summary.json"
    audit = result_root / "audit.json"
    if not summary.is_file() or not audit.is_file():
        return False
    summary_value = load(summary)
    audit_value = load(audit)
    return bool(
        summary_value.get("manifest_sha256")
        == canonical_hash(summary_value)
        and audit_value.get("manifest_sha256")
        == canonical_hash(audit_value)
        and audit_value.get("summary_manifest_sha256")
        == summary_value["manifest_sha256"]
    )


def inspect_once(
    *,
    protocol: dict[str, Any],
    run_root: Path,
    result_root: Path,
    prior_idle_count: int = 0,
    required_idle_polls: int = 3,
    commands: Iterable[str] | None = None,
) -> tuple[dict[str, Any], int]:
    process_state = relevant_commands(
        process_commands() if commands is None else commands
    )
    if process_state["coordinator"] or process_state["workers"]:
        expected = len(protocol["confirmation"]["tasks"])
        manifest_count = sum(
            (
                capture_root(run_root, task)
                / "capture_manifest.json"
            ).is_file()
            for task in protocol["confirmation"]["tasks"]
        )
        capture_state = {
            "expected_capture_count": expected,
            "complete_capture_count": manifest_count,
            "absent_capture_count": expected - manifest_count,
            "partial_capture_count": 0,
            "partial_capture_paths": [],
            "capture_validation_deferred_while_processes_active": True,
        }
    else:
        capture_state = scan_captures(protocol, run_root)
        capture_state[
            "capture_validation_deferred_while_processes_active"
        ] = False
    return recovery_decision(
        process_state=process_state,
        capture_state=capture_state,
        terminal_outputs_present=terminal_outputs_present(result_root),
        prior_idle_count=prior_idle_count,
        required_idle_polls=required_idle_polls,
    )


def launch_coordinator(
    *,
    python: str,
    project_root: Path,
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
    workers: int,
    log_path: Path,
) -> tuple[int, list[str]]:
    command = [
        python,
        str(project_root / COORDINATOR_NAME),
        "--protocol",
        str(protocol_path),
        "--project-root",
        str(project_root),
        "--run-root",
        str(run_root),
        "--result-root",
        str(result_root),
        "--workers",
        str(workers),
    ]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("a", encoding="utf-8", newline="\n")
    log.write("$ " + " ".join(command) + "\n")
    log.flush()
    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log.close()
    return int(process.pid), command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/strict_v4_krc_csr_confirmation_v1"),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/strict_v4_krc_csr_confirmation_v1"),
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--required-idle-polls", type=int, default=3)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (
        args.workers <= 0
        or args.workers > 4
        or args.interval_seconds <= 0
        or args.required_idle_polls <= 0
    ):
        raise ValueError("valid recovery controls required")
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    run_root = resolve(args.run_root)
    result_root = resolve(args.result_root)
    protocol = load(protocol_path)
    status_path = result_root / "coordinator_recovery_watcher_state.json"
    if args.once:
        state, _idle = inspect_once(
            protocol=protocol,
            run_root=run_root,
            result_root=result_root,
            required_idle_polls=args.required_idle_polls,
        )
        if not args.no_launch and state["restart_admitted"]:
            raise ValueError("--once launch is forbidden")
        write_json(status_path, state)
        print(json.dumps(state, sort_keys=True))
        return
    lock = result_root / "coordinator_recovery_watcher.lock.d"
    try:
        lock.mkdir()
    except FileExistsError:
        print("state=recovery_watcher_already_active")
        return
    idle_count = 0
    try:
        while True:
            state, idle_count = inspect_once(
                protocol=protocol,
                run_root=run_root,
                result_root=result_root,
                prior_idle_count=idle_count,
                required_idle_polls=args.required_idle_polls,
            )
            write_json(status_path, state)
            if (
                state["state"]
                == "manual_partial_capture_intervention_required"
            ):
                print(json.dumps(state, sort_keys=True))
                return
            if state["state"] == "terminal_krc_outputs_present_no_restart":
                print(json.dumps(state, sort_keys=True))
                return
            if state["restart_admitted"]:
                pid, command = launch_coordinator(
                    python=args.python,
                    project_root=root,
                    protocol_path=protocol_path,
                    run_root=run_root,
                    result_root=result_root,
                    workers=args.workers,
                    log_path=(
                        result_root / "coordinator_recovery_watcher.log"
                    ),
                )
                launched = state_value(
                    "coordinator_restarted_after_clean_drain",
                    previous_state_manifest_sha256=state[
                        "manifest_sha256"
                    ],
                    restarted_pid=pid,
                    command=command,
                    complete_capture_count=state[
                        "complete_capture_count"
                    ],
                    partial_capture_count=0,
                    restart_admitted=True,
                )
                write_json(status_path, launched)
                print(json.dumps(launched, sort_keys=True))
                return
            time.sleep(args.interval_seconds)
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

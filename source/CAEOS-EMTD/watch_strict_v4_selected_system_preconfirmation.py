from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_design import ALGORITHMS
from create_strict_v4_selected_system_preconfirmation_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
    require_canonical,
    write_json,
)
from run_strict_v4_selected_system_preconfirmation import COMPLETION_SCHEMA


SCHEMA = "strict_v4_selected_system_preconfirmation_watcher_state_v1"
BUSY_PATTERNS = (
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "evaluate_mlp_mahalanobis_pp.py",
    "run_strict_v4_",
)
WATCHER_NAME = Path(__file__).name


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


def busy_commands(commands: Iterable[str]) -> list[str]:
    return sorted(
        {
            command
            for command in commands
            if WATCHER_NAME not in command
            and "watch_strict_v4_" not in command
            and any(marker in command for marker in BUSY_PATTERNS)
        }
    )


def gpu_compute_pids() -> list[int] | None:
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    result = []
    for line in completed.stdout.splitlines():
        try:
            result.append(int(line.strip()))
        except ValueError:
            continue
    return sorted(set(result))


def resource_state(
    *,
    prior_idle_count: int,
    required_idle_polls: int,
    max_load_fraction: float,
    commands: Iterable[str] | None = None,
    load1: float | None = None,
    logical_cpu_count: int | None = None,
    gpu_pids: list[int] | None = None,
) -> tuple[dict[str, Any], int]:
    busy = busy_commands(
        process_commands() if commands is None else commands
    )
    cpu_count = int(
        os.cpu_count()
        if logical_cpu_count is None
        else logical_cpu_count
    )
    observed_load = (
        float(os.getloadavg()[0])
        if load1 is None and hasattr(os, "getloadavg")
        else load1
    )
    observed_gpu = gpu_compute_pids() if gpu_pids is None else gpu_pids
    load_limit = cpu_count * float(max_load_fraction)
    idle = bool(
        not busy
        and observed_load is not None
        and observed_load <= load_limit
        and observed_gpu == []
    )
    idle_count = prior_idle_count + 1 if idle else 0
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "resources_idle" if idle else "waiting_for_resources",
        "busy_process_count": len(busy),
        "busy_processes": busy,
        "load1": observed_load,
        "logical_cpu_count": cpu_count,
        "max_load_fraction": float(max_load_fraction),
        "load1_limit": load_limit,
        "load_gate_passes": bool(
            observed_load is not None and observed_load <= load_limit
        ),
        "gpu_compute_pids": observed_gpu,
        "gpu_gate_observable": observed_gpu is not None,
        "gpu_gate_passes": observed_gpu == [],
        "idle_consecutive_polls": idle_count,
        "required_idle_consecutive_polls": required_idle_polls,
        "launch_admitted": idle_count >= required_idle_polls,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value, idle_count


def prerequisite_state(root: Path) -> dict[str, Any]:
    result_root = (
        root / "results/strict_v4_selected_system_preconfirmation_v1"
    )
    completion_path = result_root / "execution_complete.json"
    if completion_path.is_file():
        completion = load(completion_path)
        require_canonical(
            completion, COMPLETION_SCHEMA, "preconfirmation completion"
        )
        if (
            completion.get("state") != "complete"
            or completion.get("integrity_passes") is not True
        ):
            raise ValueError("invalid preconfirmation terminal completion")
        return {
            "state": "terminal_completion_present",
            "launch_admitted": False,
            "selected_algorithm": completion["selected_algorithm"],
            "all_three_effect_gates_pass": completion[
                "all_three_effect_gates_pass"
            ],
            "completion_manifest_sha256": completion["manifest_sha256"],
        }
    goal_path = root / "results/strict_v4_current_goal_status_v1/audit.json"
    if not goal_path.is_file():
        return {
            "state": "waiting_for_final_self_algorithm_selection",
            "launch_admitted": False,
        }
    goal = load(goal_path)
    require_canonical(
        goal, "strict_v4_current_goal_status_audit_v1", "current goal audit"
    )
    requirement = goal.get("requirements", {}).get(
        "best_self_algorithm_finally_selected", {}
    )
    selection = goal.get("evidence", {}).get(
        "self_algorithm_selection", {}
    )
    selected = goal.get("selected_algorithm")
    if (
        requirement.get("satisfied") is not True
        or selection.get("final") is not True
    ):
        return {
            "state": "waiting_for_final_self_algorithm_selection",
            "launch_admitted": False,
        }
    if (
        selected not in ALGORITHMS
        or requirement.get("current_incumbent") != selected
        or selection.get("selected_algorithm") != selected
    ):
        raise ValueError("final selected algorithm fields disagree")
    ronetc_path = (
        root / "results/strict_v4_ronetc_full102_seed7/execution_complete.json"
    )
    if not ronetc_path.is_file():
        return {
            "state": "waiting_for_ronetc_domain_nearest_completion",
            "launch_admitted": False,
            "selected_algorithm": selected,
        }
    ronetc = load(ronetc_path)
    if (
        ronetc.get("manifest_sha256") != canonical_hash(ronetc)
        or ronetc.get("state") != "complete"
        or ronetc.get("integrity_passes") is not True
        or ronetc.get("scenario_count") != 102
    ):
        raise ValueError("invalid RoNeTC terminal completion")
    return {
        "state": "prerequisites_complete_waiting_for_resources",
        "launch_admitted": False,
        "selected_algorithm": selected,
        "selection_goal_manifest_sha256": goal["manifest_sha256"],
        "ronetc_completion_manifest_sha256": ronetc["manifest_sha256"],
    }


def run_logged(
    command: list[str],
    *,
    root: Path,
    log_path: Path,
    environment: dict[str, str] | None = None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            cwd=root,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def execution_commands(root: Path, python: str) -> list[tuple[str, list[str]]]:
    result = root / "results/strict_v4_selected_system_preconfirmation_v1"
    goal = root / "results/strict_v4_current_goal_status_v1/audit.json"
    design = (
        root
        / "results/strict_v4_selected_system_preconfirmation_design_v1/"
        "design.json"
    )
    return [
        (
            "activation",
            [
                python,
                str(
                    root
                    / "write_strict_v4_selected_system_preconfirmation_activation.py"
                ),
                "--goal-audit",
                str(goal),
                "--design",
                str(design),
                "--output",
                str(result / "activation.json"),
            ],
        ),
        (
            "protocol",
            [
                python,
                str(
                    root
                    / "create_strict_v4_selected_system_preconfirmation_protocol.py"
                ),
                "--project-root",
                str(root),
            ],
        ),
        (
            "execution",
            [
                python,
                str(root / "run_strict_v4_selected_system_preconfirmation.py"),
                "--project-root",
                str(root),
                "--python",
                python,
            ],
        ),
        (
            "goal_audit",
            [
                python,
                str(root / "audit_strict_v4_current_goal_status.py"),
                "--project-root",
                str(root),
                "--output",
                str(goal),
            ],
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--required-idle-polls", type=int, default=3)
    parser.add_argument("--max-load-fraction", type=float, default=0.25)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (
        args.interval_seconds <= 0
        or args.required_idle_polls <= 0
        or not 0.0 < args.max_load_fraction <= 1.0
    ):
        raise ValueError("valid positive watcher controls required")
    root = args.project_root.resolve()
    result_root = (
        root / "results/strict_v4_selected_system_preconfirmation_v1"
    )
    result_root.mkdir(parents=True, exist_ok=True)
    state_path = result_root / "watcher_state.json"
    if args.once:
        state = prerequisite_state(root)
        if state["state"] == "prerequisites_complete_waiting_for_resources":
            state, _count = resource_state(
                prior_idle_count=0,
                required_idle_polls=args.required_idle_polls,
                max_load_fraction=args.max_load_fraction,
            )
        if state.get("launch_admitted") and not args.no_launch:
            raise ValueError("--once launch is forbidden")
        write_json(state_path, state)
        print(json.dumps(state, sort_keys=True))
        return

    lock = result_root / "watcher.lock.d"
    try:
        lock.mkdir()
    except FileExistsError:
        print("state=watcher_already_active")
        return
    try:
        while True:
            state = prerequisite_state(root)
            write_json(state_path, state)
            if state["state"] == "terminal_completion_present":
                print(json.dumps(state, sort_keys=True))
                return
            if state["state"] == "prerequisites_complete_waiting_for_resources":
                break
            time.sleep(args.interval_seconds)
        idle_count = 0
        while idle_count < args.required_idle_polls:
            state, idle_count = resource_state(
                prior_idle_count=idle_count,
                required_idle_polls=args.required_idle_polls,
                max_load_fraction=args.max_load_fraction,
            )
            write_json(state_path, state)
            if idle_count < args.required_idle_polls:
                time.sleep(args.interval_seconds)
        environment = dict(os.environ)
        environment[
            "SELECTED_SYSTEM_PRECONFIRMATION_EXCLUSIVE_MACHINE_GATE"
        ] = "passed"
        for name, command in execution_commands(root, args.python):
            run_logged(
                command,
                root=root,
                log_path=result_root / f"watcher_{name}.log",
                environment=environment,
            )
        final = prerequisite_state(root)
        if final["state"] != "terminal_completion_present":
            raise ValueError("preconfirmation completion was not produced")
        final["goal_audit_refreshed"] = True
        write_json(state_path, final)
        print(json.dumps(final, sort_keys=True))
    except Exception as error:
        write_json(
            state_path,
            {
                "schema_version": SCHEMA,
                "state": "failed_closed",
                "launch_admitted": False,
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        raise
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

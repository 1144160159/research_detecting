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
from create_strict_v4_self_algorithm_direct_tournament_execution_protocol import (
    create_execution_protocol,
    write_protocol,
)
from write_strict_v4_self_algorithm_direct_tournament_activation import (
    write_activation,
)


SCHEMA = "strict_v4_self_algorithm_direct_tournament_watcher_state_v1"
ACTIVATION_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_activation_v1"
)
PROTOCOL_SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
COMPLETION_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_completion_v1"
)
WATCHER_NAME = (
    "watch_strict_v4_self_algorithm_direct_tournament_confirmation.py"
)
BUSY_PATTERNS = (
    "run_strict_v4_krc_csr_confirmation.py",
    "capture_krc_csr_confirmation_runtime.py",
    "evaluate_krc_csr_confirmation_runtime.py",
    "run_strict_v4_rrc_csr_confirmation.py",
    "run_strict_v4_rrc_csr_capture_pipeline.py",
    "capture_csr_caeos_runtime.py",
    "materialize_rrc_csr_runtime.py",
    "evaluate_rrc_csr_runtime.py",
    "certify_rrc_csr_scenario.py",
    "run_strict_v4_pug_confirmation.py",
    "run_strict_v4_pug_cross_suite_confirmation.py",
    "run_strict_v4_self_algorithm_direct_tournament_confirmation.py",
    "run_strict_v4_selected_system",
    "run_strict_v4_krc_external_malicious.py",
    "run_strict_v4_krc_parrot_safety.py",
    "run_strict_v4_krc_opendetect_efficiency.py",
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


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


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


def busy_commands(
    commands: Iterable[str],
    markers: tuple[str, ...] = BUSY_PATTERNS,
) -> list[str]:
    return sorted(
        {
            command
            for command in commands
            if WATCHER_NAME not in command
            and any(marker in command for marker in markers)
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
    pids = []
    for line in completed.stdout.splitlines():
        if line.strip():
            try:
                pids.append(int(line.strip()))
            except ValueError:
                return None
    return sorted(set(pids))


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
    if (
        required_idle_polls <= 0
        or not 0.0 < float(max_load_fraction) <= 1.0
    ):
        raise ValueError("valid resource controls required")
    busy = busy_commands(
        process_commands() if commands is None else commands
    )
    cpu_count = (
        int(os.cpu_count() or 0)
        if logical_cpu_count is None
        else int(logical_cpu_count)
    )
    observed_load = (
        float(os.getloadavg()[0])
        if load1 is None and hasattr(os, "getloadavg")
        else load1
    )
    observed_gpu_pids = (
        gpu_compute_pids() if gpu_pids is None else list(gpu_pids)
    )
    limit = float(cpu_count) * float(max_load_fraction)
    load_idle = bool(
        cpu_count > 0
        and observed_load is not None
        and float(observed_load) <= limit
    )
    gpu_idle = observed_gpu_pids == []
    idle = not busy and load_idle and gpu_idle
    idle_count = prior_idle_count + 1 if idle else 0
    return (
        state_value(
            "resources_idle" if idle else "waiting_for_resources",
            busy_process_count=len(busy),
            busy_processes=busy,
            load1=observed_load,
            logical_cpu_count=cpu_count,
            load1_limit=limit,
            load_gate_passes=load_idle,
            gpu_compute_pids=observed_gpu_pids,
            gpu_gate_observable=observed_gpu_pids is not None,
            gpu_gate_passes=gpu_idle,
            idle_consecutive_polls=idle_count,
            required_idle_consecutive_polls=required_idle_polls,
            launch_admitted=idle_count >= required_idle_polls,
        ),
        idle_count,
    )


def prerequisite_state(root: Path) -> dict[str, Any]:
    result_root = (
        root / "results/strict_v4_self_algorithm_direct_tournament_v1"
    )
    completion_path = result_root / "execution_complete.json"
    if completion_path.is_file():
        completion = load(completion_path)
        require_canonical(
            completion, COMPLETION_SCHEMA, "tournament completion"
        )
        return state_value(
            "terminal_completion_present",
            launch_admitted=False,
            selected_algorithm=completion["selected_algorithm"],
        )
    activation_path = result_root / "activation.json"
    if not activation_path.is_file():
        return state_value(
            "waiting_for_dual_positive_activation",
            launch_admitted=False,
        )
    activation = load(activation_path)
    require_canonical(
        activation, ACTIVATION_SCHEMA, "tournament activation"
    )
    protocol_path = result_root / "protocol.json"
    if not protocol_path.is_file():
        return state_value(
            "activation_complete_protocol_pending",
            launch_admitted=False,
        )
    protocol = load(protocol_path)
    require_canonical(protocol, PROTOCOL_SCHEMA, "tournament protocol")
    if (
        protocol.get("execution_admitted") is not True
        or protocol.get("input_manifest_sha256", {}).get("activation")
        != activation["manifest_sha256"]
    ):
        raise ValueError("tournament protocol activation binding failed")
    return state_value(
        "prerequisites_complete_waiting_for_resources",
        launch_admitted=False,
        incumbent_algorithm=protocol["incumbent_algorithm"],
        challenger_algorithm=protocol["challenger_algorithm"],
    )


def prepare(root: Path, python: str) -> dict[str, Any]:
    result_root = (
        root / "results/strict_v4_self_algorithm_direct_tournament_v1"
    )
    subprocess.run(
        [
            python,
            str(root / "audit_strict_v4_current_goal_status.py"),
            "--project-root",
            str(root),
        ],
        cwd=root,
        stdout=subprocess.DEVNULL,
        check=True,
    )
    activation = write_activation(
        goal_audit_path=(
            root / "results/strict_v4_current_goal_status_v1/audit.json"
        ),
        design_path=(
            root
            / "results/strict_v4_self_algorithm_direct_tournament_design_v1/"
            "design.json"
        ),
        result_root=result_root,
        output=result_root / "activation.json",
    )
    if activation.get("activation_required") is False:
        return state_value(
            "waiting_for_dual_positive_activation",
            launch_admitted=False,
            incumbent=activation.get("incumbent"),
            challenger=activation.get("challenger"),
        )
    protocol_path = result_root / "protocol.json"
    if not protocol_path.is_file():
        protocol = create_execution_protocol(
            project_root=root,
            activation_path=result_root / "activation.json",
            design_path=(
                root
                / "results/"
                "strict_v4_self_algorithm_direct_tournament_design_v1/"
                "design.json"
            ),
            krc_protocol_path=(
                root
                / "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
            ),
            pug_protocol_path=(
                root
                / "results/strict_v4_pug_cross_suite_confirmation_v1/"
                "execution_protocol.json"
            ),
            pug_completion_path=(
                root
                / "results/strict_v4_pug_cross_suite_confirmation_v1/"
                "execution_complete.json"
            ),
            result_root=result_root,
        )
        write_protocol(protocol_path, protocol)
    return prerequisite_state(root)


def inspect_once(
    root: Path,
    *,
    prior_idle_count: int = 0,
    required_idle_polls: int = 3,
    max_load_fraction: float = 0.25,
    commands: Iterable[str] | None = None,
    load1: float | None = None,
    logical_cpu_count: int | None = None,
    gpu_pids: list[int] | None = None,
) -> tuple[dict[str, Any], int]:
    state = prerequisite_state(root)
    if state["state"] != "prerequisites_complete_waiting_for_resources":
        return state, 0
    return resource_state(
        prior_idle_count=prior_idle_count,
        required_idle_polls=required_idle_polls,
        max_load_fraction=max_load_fraction,
        commands=commands,
        load1=load1,
        logical_cpu_count=logical_cpu_count,
        gpu_pids=gpu_pids,
    )


def run_tournament(
    root: Path,
    *,
    python: str,
    workers: int,
    log_path: Path,
) -> None:
    command = [
        python,
        str(
            root
            / "run_strict_v4_self_algorithm_direct_tournament_confirmation.py"
        ),
        "--project-root",
        str(root),
        "--python",
        python,
        "--workers",
        str(workers),
    ]
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--required-idle-polls", type=int, default=3)
    parser.add_argument("--max-load-fraction", type=float, default=0.25)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (
        args.interval_seconds <= 0
        or args.required_idle_polls <= 0
        or args.workers <= 0
        or args.workers > 4
        or not 0.0 < args.max_load_fraction <= 1.0
    ):
        raise ValueError("valid positive watcher controls required")
    root = args.project_root.resolve()
    result_root = (
        root / "results/strict_v4_self_algorithm_direct_tournament_v1"
    )
    result_root.mkdir(parents=True, exist_ok=True)
    if args.once:
        state, _idle = inspect_once(
            root,
            required_idle_polls=args.required_idle_polls,
            max_load_fraction=args.max_load_fraction,
        )
        if not args.no_launch and state.get("launch_admitted") is True:
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
    idle_count = 0
    try:
        while True:
            state = prepare(root, args.python)
            if state["state"] == "terminal_completion_present":
                write_json(result_root / "watcher_state.json", state)
                print(json.dumps(state, sort_keys=True))
                return
            if (
                state["state"]
                != "prerequisites_complete_waiting_for_resources"
            ):
                idle_count = 0
            else:
                state, idle_count = inspect_once(
                    root,
                    prior_idle_count=idle_count,
                    required_idle_polls=args.required_idle_polls,
                    max_load_fraction=args.max_load_fraction,
                )
            write_json(result_root / "watcher_state.json", state)
            if state.get("launch_admitted") is True:
                run_tournament(
                    root,
                    python=args.python,
                    workers=args.workers,
                    log_path=result_root / "watcher_execution.log",
                )
                subprocess.run(
                    [
                        args.python,
                        str(root / "audit_strict_v4_current_goal_status.py"),
                        "--project-root",
                        str(root),
                    ],
                    cwd=root,
                    check=True,
                )
                terminal = prerequisite_state(root)
                write_json(result_root / "watcher_state.json", terminal)
                print(json.dumps(terminal, sort_keys=True))
                return
            time.sleep(args.interval_seconds)
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

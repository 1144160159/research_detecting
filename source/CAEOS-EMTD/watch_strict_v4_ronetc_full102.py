from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash as goal_canonical_hash,
)
from summarize_strict_v4_ronetc_full102 import canonical_hash, file_hash


SCHEMA = "strict_v4_ronetc_full102_watcher_state_v1"
PROTOCOL_SCHEMA = "strict_v4_ronetc_full102_protocol_v1"
PROTOCOL_AUDIT_SCHEMA = "strict_v4_ronetc_full102_protocol_audit_v1"
COMPLETION_SCHEMA = "strict_v4_ronetc_full102_completion_v1"
GOAL_SCHEMA = "strict_v4_current_goal_status_audit_v1"
SELECTED_ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
WATCHER_NAME = "watch_strict_v4_ronetc_full102.py"
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")
BUSY_PATTERNS = (
    "run_strict_v4_krc_csr_confirmation.py",
    "capture_krc_csr_confirmation_runtime.py",
    "evaluate_krc_csr_confirmation_runtime.py",
    "run_strict_v4_rrc_csr_confirmation.py",
    "run_strict_v4_rrc_csr_capture_pipeline.py",
    "run_strict_v4_pug_confirmation.py",
    "run_strict_v4_pug_cross_suite_confirmation.py",
    "run_strict_v4_self_algorithm_direct_tournament",
    "watch_strict_v4_selected_system_downstream.py",
    "run_strict_v4_selected_system_",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
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


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def validate_protocol(
    protocol_path: Path, protocol_audit_path: Path
) -> dict[str, Any]:
    protocol = load(protocol_path)
    require_canonical(protocol, PROTOCOL_SCHEMA, "RoNeTC protocol")
    tasks = protocol.get("tasks", [])
    identities = {
        (
            task.get("suite"),
            task.get("scenario"),
            task.get("model"),
            task.get("seed"),
        )
        for task in tasks
    }
    command = protocol.get("command", [])
    if (
        protocol.get("state") != "frozen_zero_result"
        or len(tasks) != 102
        or len(identities) != 102
        or any(task.get("model") != "ronetc" for task in tasks)
        or any(task.get("seed") != 7 for task in tasks)
        or not isinstance(command, list)
        or len(command) < 2
        or command[1] != "run_neural_baseline_matrix.py"
        or "--models" not in command
        or command[command.index("--models") + 1] != "ronetc"
    ):
        raise ValueError("invalid frozen RoNeTC full102 execution protocol")

    audit = load(protocol_audit_path)
    claimed_audit = audit.get("audit_manifest_sha256")
    if (
        audit.get("schema_version") != PROTOCOL_AUDIT_SCHEMA
        or claimed_audit
        != canonical_hash(audit, field="audit_manifest_sha256")
        or audit.get("passed") is not True
        or not all(audit.get("checks", {}).values())
        or audit.get("protocol_file_sha256") != file_hash(protocol_path)
        or audit.get("protocol_manifest_sha256_claimed")
        != protocol["manifest_sha256"]
        or audit.get("protocol_manifest_sha256_recomputed")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("valid passing RoNeTC protocol audit required")
    return protocol


def artifact_state(protocol: dict[str, Any]) -> dict[str, Any]:
    complete = 0
    resumable = 0
    absent = 0
    invalid = []
    counts = {artifact: 0 for artifact in REQUIRED_ARTIFACTS}
    for task in protocol["tasks"]:
        directory = Path(task["output_dir"])
        present = {
            artifact: (directory / artifact).is_file()
            for artifact in REQUIRED_ARTIFACTS
        }
        for artifact, exists in present.items():
            counts[artifact] += int(exists)
        if all(present.values()):
            complete += 1
        elif not any(present.values()):
            absent += 1
        elif present["provenance.json"]:
            resumable += 1
        else:
            invalid.append(str(directory))
    return {
        "complete_task_count": complete,
        "resumable_task_count": resumable,
        "absent_task_count": absent,
        "invalid_task_count": len(invalid),
        "invalid_task_directories": invalid[:20],
        "artifact_counts": counts,
    }


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
        try:
            pids.append(int(line.strip()))
        except ValueError:
            continue
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
        raise ValueError("valid resource gate controls required")
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
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "resources_idle" if idle else "waiting_for_resources",
        "busy_process_count": len(busy),
        "busy_processes": busy,
        "load1": observed_load,
        "logical_cpu_count": cpu_count,
        "max_load_fraction": float(max_load_fraction),
        "load1_limit": limit,
        "load_gate_passes": load_idle,
        "gpu_compute_pids": observed_gpu_pids,
        "gpu_gate_observable": observed_gpu_pids is not None,
        "gpu_gate_passes": gpu_idle,
        "idle_consecutive_polls": idle_count,
        "required_idle_consecutive_polls": required_idle_polls,
        "launch_admitted": idle_count >= required_idle_polls,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value, idle_count


def result_paths(root: Path) -> tuple[Path, Path, Path]:
    result_root = root / "results/strict_v4_ronetc_full102_seed7"
    return (
        result_root,
        result_root / "protocol.json",
        result_root / "protocol_audit.json",
    )


def prerequisite_state(root: Path) -> dict[str, Any]:
    result_root, protocol_path, protocol_audit_path = result_paths(root)
    completion_path = result_root / "execution_complete.json"
    if completion_path.is_file():
        completion = load(completion_path)
        require_canonical(completion, COMPLETION_SCHEMA, "RoNeTC completion")
        if (
            completion.get("state") != "complete"
            or completion.get("scenario_count") != 102
            or completion.get("integrity_passes") is not True
        ):
            raise ValueError("invalid RoNeTC terminal completion")
        return {
            "state": "terminal_completion_present",
            "launch_admitted": False,
            "completion_manifest_sha256": completion["manifest_sha256"],
        }

    protocol = validate_protocol(protocol_path, protocol_audit_path)
    artifacts = artifact_state(protocol)
    if artifacts["invalid_task_count"]:
        return {
            "state": "manual_partial_result_intervention_required",
            "launch_admitted": False,
            **artifacts,
        }

    goal_path = root / "results/strict_v4_current_goal_status_v1/audit.json"
    if not goal_path.is_file():
        return {
            "state": "waiting_for_final_self_algorithm_selection",
            "launch_admitted": False,
            **artifacts,
        }
    goal = load(goal_path)
    if (
        goal.get("schema_version") != GOAL_SCHEMA
        or goal.get("manifest_sha256") != goal_canonical_hash(goal)
    ):
        raise ValueError("canonical current goal audit required")
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
            **artifacts,
        }
    if (
        selected not in SELECTED_ALGORITHMS
        or requirement.get("current_incumbent") != selected
        or selection.get("selected_algorithm") != selected
    ):
        raise ValueError("final self-algorithm selection fields disagree")
    return {
        "state": "prerequisites_complete_waiting_for_resources",
        "launch_admitted": False,
        "selected_algorithm": selected,
        "selection_goal_manifest_sha256": goal["manifest_sha256"],
        **artifacts,
    }


def run_logged(
    command: list[str], *, root: Path, log_path: Path
) -> None:
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


def execution_commands(
    root: Path, protocol: dict[str, Any]
) -> list[list[str]]:
    result_root, protocol_path, protocol_audit_path = result_paths(root)
    run_root = Path(protocol["tasks"][0]["output_dir"]).parents[1]
    analysis = protocol["analysis_contract"]
    summary_path = result_root / "summary.json"
    return [
        [sys.executable, *map(str, protocol["command"][1:])],
        [
            sys.executable,
            str(root / "summarize_strict_v4_ronetc_full102.py"),
            "--protocol",
            str(protocol_path),
            "--protocol-audit",
            str(protocol_audit_path),
            "--result-root",
            str(run_root),
            "--opendetect-root",
            str(analysis["opendetect_root"]),
            "--baseline-manifest",
            str(analysis["baseline_manifest"]),
            "--full-summary",
            str(analysis["full103_summary"]),
            "--project-root",
            str(root),
            "--output-json",
            str(summary_path),
            "--output-md",
            str(result_root / "summary.md"),
        ],
        [
            sys.executable,
            str(root / "audit_strict_v4_ronetc_full102.py"),
            "--protocol",
            str(protocol_path),
            "--protocol-audit",
            str(protocol_audit_path),
            "--summary",
            str(summary_path),
            "--result-root",
            str(run_root),
            "--opendetect-root",
            str(analysis["opendetect_root"]),
            "--baseline-manifest",
            str(analysis["baseline_manifest"]),
            "--full-summary",
            str(analysis["full103_summary"]),
            "--project-root",
            str(root),
            "--output-audit",
            str(result_root / "audit.json"),
            "--output-completion",
            str(result_root / "execution_complete.json"),
        ],
        [
            sys.executable,
            str(root / "audit_strict_v4_current_goal_status.py"),
            "--project-root",
            str(root),
            "--output",
            str(
                root / "results/strict_v4_current_goal_status_v1/audit.json"
            ),
        ],
    ]


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
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
    result_root, protocol_path, protocol_audit_path = result_paths(root)
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
    try:
        while True:
            state = prerequisite_state(root)
            write_json(result_root / "watcher_state.json", state)
            if state["state"] == "terminal_completion_present":
                print("state=terminal_completion_present")
                return
            if state["state"] == "manual_partial_result_intervention_required":
                raise ValueError(state["state"])
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
            write_json(result_root / "watcher_state.json", state)
            if idle_count < args.required_idle_polls:
                time.sleep(args.interval_seconds)

        protocol = validate_protocol(protocol_path, protocol_audit_path)
        names = ("execution", "summary", "audit", "goal_audit")
        for name, command in zip(names, execution_commands(root, protocol)):
            run_logged(
                command,
                root=root,
                log_path=result_root / f"watcher_{name}.log",
            )
        completion = load(result_root / "execution_complete.json")
        require_canonical(completion, COMPLETION_SCHEMA, "RoNeTC completion")
        if completion.get("integrity_passes") is not True:
            raise ValueError("RoNeTC completion failed integrity audit")
        final_state = {
            "state": "complete",
            "launch_admitted": False,
            "completion_manifest_sha256": completion["manifest_sha256"],
            "goal_audit_refreshed": True,
        }
        write_json(result_root / "watcher_state.json", final_state)
        print(json.dumps(final_state, sort_keys=True))
    except Exception as error:
        write_json(
            result_root / "watcher_state.json",
            {
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

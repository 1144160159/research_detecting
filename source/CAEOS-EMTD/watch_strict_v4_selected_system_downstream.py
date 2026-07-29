from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Iterable

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


SCHEMA = "strict_v4_selected_system_downstream_watcher_state_v1"
COMPLETION_SCHEMA = (
    "strict_v4_selected_system_downstream_execution_complete_v1"
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
    "run_strict_v4_self_algorithm_direct_tournament.py",
    "run_strict_v4_mdr",
    "run_strict_v4_comp",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "train_mdr_caeos_open_set.py",
)
WATCHER_NAME = "watch_strict_v4_selected_system_downstream.py"


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
    output = []
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if stripped:
            try:
                output.append(int(stripped))
            except ValueError:
                return None
    return sorted(set(output))


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
    load_limit = float(cpu_count) * float(max_load_fraction)
    process_idle = not busy
    load_idle = bool(
        cpu_count > 0
        and observed_load is not None
        and float(observed_load) <= load_limit
    )
    gpu_idle = observed_gpu_pids == []
    idle = process_idle and load_idle and gpu_idle
    idle_count = prior_idle_count + 1 if idle else 0
    state = {
        "schema_version": SCHEMA,
        "state": "resources_idle" if idle else "waiting_for_resources",
        "busy_process_count": len(busy),
        "busy_processes": busy,
        "load1": observed_load,
        "logical_cpu_count": cpu_count,
        "max_load_fraction": float(max_load_fraction),
        "load1_limit": load_limit,
        "load_gate_passes": load_idle,
        "gpu_compute_pids": observed_gpu_pids,
        "gpu_gate_observable": observed_gpu_pids is not None,
        "gpu_gate_passes": gpu_idle,
        "idle_consecutive_polls": idle_count,
        "required_idle_consecutive_polls": required_idle_polls,
        "launch_admitted": idle_count >= required_idle_polls,
    }
    state["manifest_sha256"] = canonical_hash(state)
    return state, idle_count


def validate_activation(path: Path) -> dict[str, Any]:
    value = load(path)
    require_canonical(
        value,
        "strict_v4_selected_system_activation_v1",
        "selected-system activation",
    )
    snapshot = value.get("selection_snapshot", {})
    if (
        value.get("execution_admitted") is not True
        or snapshot.get("final") is not True
        or snapshot.get("selected_algorithm")
        != value.get("selected_algorithm")
        or value.get("selection_snapshot_sha256")
        != canonical_hash(snapshot)
    ):
        raise ValueError("invalid selected-system activation")
    return value


def freeze_goal_snapshot(
    root: Path, result_root: Path, activation: dict[str, Any]
) -> Path:
    source = root / "results/strict_v4_current_goal_status_v1/audit.json"
    target = result_root / "activation_goal_audit.json"
    expected_manifest = activation["input_manifest_sha256"][
        "current_goal_audit"
    ]
    expected_file = activation["input_file_sha256"][
        "current_goal_audit"
    ]
    if target.is_file():
        value = load(target)
        if (
            value.get("manifest_sha256") != expected_manifest
            or file_hash(target) != expected_file
        ):
            raise ValueError("frozen activation goal snapshot drifted")
        return target
    value = load(source)
    if (
        value.get("manifest_sha256") != expected_manifest
        or file_hash(source) != expected_file
    ):
        raise ValueError(
            "current goal audit no longer matches activation binding"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    shutil.copyfile(source, temporary)
    os.replace(temporary, target)
    if file_hash(target) != expected_file:
        raise ValueError("goal snapshot copy changed bytes")
    return target


def expected_source_capture_count(root: Path) -> tuple[int, int]:
    protocol_path = (
        root / "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
    )
    if not protocol_path.is_file():
        return 0, 306
    protocol = load(protocol_path)
    tasks = protocol.get("confirmation", {}).get("tasks", [])
    capture_root = root / "runs/strict_v4_krc_csr_confirmation_v1/captures"
    present = 0
    for task in tasks:
        path = (
            capture_root
            / str(task["suite"])
            / str(task["scenario"])
            / f"seed{int(task['training_seed'])}"
            / "capture_manifest.json"
        )
        present += int(path.is_file())
    return present, 306


def prerequisite_state(root: Path, result_root: Path) -> dict[str, Any]:
    activation_path = result_root / "activation.json"
    completion_path = result_root / "execution_complete.json"
    if completion_path.is_file():
        completion = load(completion_path)
        require_canonical(
            completion, COMPLETION_SCHEMA, "downstream completion"
        )
        return {
            "state": "terminal_completion_present",
            "launch_admitted": False,
        }
    if not activation_path.is_file():
        return {
            "state": "waiting_for_final_selection_activation",
            "launch_admitted": False,
        }
    activation = validate_activation(activation_path)
    snapshot = result_root / "activation_goal_audit.json"
    if not snapshot.is_file():
        return {
            "state": "activation_goal_snapshot_pending",
            "launch_admitted": False,
            "selected_algorithm": activation["selected_algorithm"],
        }
    goal = load(snapshot)
    if (
        goal.get("manifest_sha256")
        != activation["input_manifest_sha256"]["current_goal_audit"]
        or file_hash(snapshot)
        != activation["input_file_sha256"]["current_goal_audit"]
    ):
        raise ValueError("activation goal snapshot binding mismatch")
    external_input = (
        root
        / "results/strict_v4_krc_external_malicious_input_protocol_v2/"
        "protocol.json"
    )
    if not external_input.is_file():
        return {
            "state": "waiting_for_external_input_protocol",
            "launch_admitted": False,
        }
    feature_summary = (
        root
        / "results/parrot2025_full_no_decryption_features_v1/"
        "feature_shard_manifest.json"
    )
    if not feature_summary.is_file():
        return {
            "state": "waiting_for_parrot_feature_summary",
            "launch_admitted": False,
        }
    present, expected = expected_source_capture_count(root)
    if present != expected:
        return {
            "state": "waiting_for_complete_306_source_capture_matrix",
            "source_capture_count": present,
            "expected_source_capture_count": expected,
            "launch_admitted": False,
        }
    return {
        "state": "prerequisites_complete_waiting_for_resources",
        "selected_algorithm": activation["selected_algorithm"],
        "source_capture_count": present,
        "launch_admitted": False,
    }


def run_logged(
    command: list[str],
    *,
    root: Path,
    log_path: Path,
    exclusive_gate: bool = False,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    if exclusive_gate:
        environment["SELECTED_SYSTEM_EXCLUSIVE_MACHINE_GATE"] = "passed"
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


def goal_audit_refresh_command(root: Path) -> list[str]:
    return [
        sys.executable,
        str(root / "audit_strict_v4_current_goal_status.py"),
        "--project-root",
        str(root),
        "--output",
        str(root / "results/strict_v4_current_goal_status_v1/audit.json"),
    ]


def wait_for_prerequisites(
    root: Path,
    result_root: Path,
    interval_seconds: int,
) -> dict[str, Any]:
    while True:
        run_logged(
            goal_audit_refresh_command(root),
            root=root,
            log_path=result_root / "watcher_goal_audit.log",
        )
        activation_path = result_root / "activation.json"
        if not activation_path.is_file():
            run_logged(
                [
                    sys.executable,
                    str(
                        root
                        / "write_strict_v4_selected_system_activation.py"
                    ),
                    "--project-root",
                    str(root),
                ],
                root=root,
                log_path=result_root / "watcher_activation.log",
            )
        if activation_path.is_file():
            activation = validate_activation(activation_path)
            freeze_goal_snapshot(root, result_root, activation)
        state = prerequisite_state(root, result_root)
        write_json(result_root / "watcher_state.json", state)
        if state["state"] == "prerequisites_complete_waiting_for_resources":
            return state
        if state["state"] == "terminal_completion_present":
            return state
        time.sleep(interval_seconds)


def wait_for_resources(
    *,
    result_root: Path,
    interval_seconds: int,
    required_idle_polls: int,
    max_load_fraction: float,
) -> None:
    idle_count = 0
    while idle_count < required_idle_polls:
        state, idle_count = resource_state(
            prior_idle_count=idle_count,
            required_idle_polls=required_idle_polls,
            max_load_fraction=max_load_fraction,
        )
        write_json(result_root / "resource_wait.json", state)
        if idle_count < required_idle_polls:
            time.sleep(interval_seconds)


def validate_branch_completion(
    path: Path, schema: str, activation: dict[str, Any]
) -> dict[str, Any]:
    value = load(path)
    require_canonical(value, schema, f"branch completion {path}")
    if value.get("protocol_manifest_sha256") is None:
        raise ValueError("branch completion lacks protocol binding")
    selected = value.get("selected_algorithm")
    if selected not in (None, activation["selected_algorithm"]):
        raise ValueError("branch completion algorithm mismatch")
    return value


def execute_downstream(
    *,
    root: Path,
    result_root: Path,
    interval_seconds: int,
    required_idle_polls: int,
    max_load_fraction: float,
) -> dict[str, Any]:
    activation = validate_activation(result_root / "activation.json")
    external_root = result_root / "external"
    parrot_root = result_root / "parrot"
    efficiency_root = result_root / "efficiency"
    branches = (
        (
            "external",
            external_root / "execution_complete.json",
            "strict_v4_selected_system_external_execution_complete_v1",
            [
                [
                    sys.executable,
                    str(
                        root
                        / "run_strict_v4_selected_system_external_malicious.py"
                    ),
                    "--mode",
                    "prepare",
                    "--project-root",
                    str(root),
                    "--protocol",
                    str(result_root / "external_malicious_protocol.json"),
                    "--run-root",
                    str(external_root),
                ],
                [
                    sys.executable,
                    str(
                        root
                        / "run_strict_v4_selected_system_external_malicious.py"
                    ),
                    "--mode",
                    "run",
                    "--project-root",
                    str(root),
                    "--protocol",
                    str(result_root / "external_malicious_protocol.json"),
                    "--run-root",
                    str(external_root),
                ],
            ],
        ),
        (
            "parrot",
            parrot_root / "execution_complete.json",
            "strict_v4_selected_system_parrot_execution_complete_v1",
            [
                [
                    sys.executable,
                    str(
                        root
                        / "run_strict_v4_selected_system_parrot_safety.py"
                    ),
                    "--project-root",
                    str(root),
                    "--protocol",
                    str(result_root / "parrot_safety_protocol.json"),
                    "--run-root",
                    str(parrot_root),
                    "--execute",
                ]
            ],
        ),
        (
            "efficiency",
            efficiency_root / "execution_complete.json",
            (
                "strict_v4_selected_system_efficiency_execution_complete_v1"
            ),
            [
                [
                    sys.executable,
                    str(
                        root
                        / "run_strict_v4_selected_system_efficiency.py"
                    ),
                    "--project-root",
                    str(root),
                    "--protocol-output",
                    str(result_root / "efficiency_protocol.json"),
                    "--run-root",
                    str(efficiency_root),
                    "--execute",
                ]
            ],
        ),
    )
    completions = {}
    for name, completion_path, schema, commands in branches:
        if not completion_path.is_file():
            wait_for_resources(
                result_root=result_root,
                interval_seconds=interval_seconds,
                required_idle_polls=required_idle_polls,
                max_load_fraction=max_load_fraction,
            )
            for command in commands:
                run_logged(
                    command,
                    root=root,
                    log_path=result_root / f"watcher_{name}.log",
                    exclusive_gate=True,
                )
        completions[name] = validate_branch_completion(
            completion_path, schema, activation
        )
    integrated_path = result_root / "integrated_audit.json"
    if not integrated_path.is_file():
        command = [
            sys.executable,
            str(root / "audit_strict_v4_selected_system_integrated.py"),
            "--project-root",
            str(root),
            "--activation",
            str(result_root / "activation.json"),
            "--adapter-design",
            str(
                root
                / "results/strict_v4_selected_system_downstream_adapter_"
                "design_v1/design.json"
            ),
            "--current-goal-audit",
            str(result_root / "activation_goal_audit.json"),
            "--external-protocol",
            str(result_root / "external_malicious_protocol.json"),
            "--external-summary",
            str(external_root / "summary.json"),
            "--external-audit",
            str(external_root / "audit.json"),
            "--parrot-protocol",
            str(result_root / "parrot_safety_protocol.json"),
            "--parrot-summary",
            str(parrot_root / "summary.json"),
            "--parrot-audit",
            str(parrot_root / "audit.json"),
            "--efficiency-protocol",
            str(result_root / "efficiency_protocol.json"),
            "--efficiency-summary",
            str(efficiency_root / "summary.json"),
            "--efficiency-audit",
            str(efficiency_root / "audit.json"),
            "--output",
            str(integrated_path),
        ]
        run_logged(
            command,
            root=root,
            log_path=result_root / "watcher_integrated_audit.log",
        )
    integrated = load(integrated_path)
    require_canonical(
        integrated,
        "strict_v4_selected_system_integrated_audit_v1",
        "selected-system integrated audit",
    )
    value: dict[str, Any] = {
        "schema_version": COMPLETION_SCHEMA,
        "state": "complete",
        "selected_algorithm": activation["selected_algorithm"],
        "activation_manifest_sha256": activation["manifest_sha256"],
        "branch_completion_manifest_sha256": {
            name: completion["manifest_sha256"]
            for name, completion in completions.items()
        },
        "integrated_audit_manifest_sha256": integrated["manifest_sha256"],
        "integrity_passes": integrated["passes"],
        "claim_tier": integrated["claim_tier"],
        "comprehensive_sota_confirmed": integrated[
            "comprehensive_sota_confirmed"
        ],
        "resource_gate": {
            "required_idle_consecutive_polls": required_idle_polls,
            "max_load_fraction": max_load_fraction,
            "gpu_compute_processes_required_zero": True,
            "exclusive_environment_marker_set_only_after_gate": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(result_root / "execution_complete.json", value)
    write_json(
        result_root / "watcher_state.json",
        {
            "state": "complete",
            "launched": True,
            "completion_manifest_sha256": value["manifest_sha256"],
            "comprehensive_sota_confirmed": value[
                "comprehensive_sota_confirmed"
            ],
        },
    )
    return value


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
    result_root = (
        root / "results/strict_v4_selected_system_downstream_adapter_v1"
    )
    state = prerequisite_state(root, result_root)
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
    result_root = (
        root / "results/strict_v4_selected_system_downstream_adapter_v1"
    )
    result_root.mkdir(parents=True, exist_ok=True)
    if args.once:
        state, _idle = inspect_once(
            root,
            required_idle_polls=args.required_idle_polls,
            max_load_fraction=args.max_load_fraction,
        )
        if (
            not args.no_launch
            and state.get("launch_admitted") is True
        ):
            raise ValueError("--once launch is forbidden; use persistent mode")
        write_json(result_root / "watcher_state.json", state)
        print(json.dumps(state, sort_keys=True))
        return
    lock = result_root / "downstream_watcher.lock.d"
    try:
        lock.mkdir()
    except FileExistsError:
        print("state=watcher_already_active")
        return
    try:
        state = wait_for_prerequisites(
            root, result_root, args.interval_seconds
        )
        if state["state"] == "terminal_completion_present":
            print("state=terminal_completion_present")
            return
        wait_for_resources(
            result_root=result_root,
            interval_seconds=args.interval_seconds,
            required_idle_polls=args.required_idle_polls,
            max_load_fraction=args.max_load_fraction,
        )
        completion = execute_downstream(
            root=root,
            result_root=result_root,
            interval_seconds=args.interval_seconds,
            required_idle_polls=args.required_idle_polls,
            max_load_fraction=args.max_load_fraction,
        )
        print(
            json.dumps(
                {
                    "state": "complete",
                    "claim_tier": completion["claim_tier"],
                    "comprehensive_sota_confirmed": completion[
                        "comprehensive_sota_confirmed"
                    ],
                    "manifest_sha256": completion["manifest_sha256"],
                },
                sort_keys=True,
            )
        )
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

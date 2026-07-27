from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


BUSY_PATTERNS = (
    "run_strict_v4_krc_csr_confirmation.py",
    "capture_krc_csr_confirmation_runtime.py",
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


def validate_protocol(protocol: dict[str, Any], root: Path) -> None:
    if (
        protocol.get("schema_version") != "strict_v4_pug_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(protocol.get("tasks", [])) != 18
    ):
        raise ValueError("canonical PUG execution protocol required")
    for relative, expected in protocol.get("implementation_sha256", {}).items():
        path = root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"frozen implementation drifted: {relative}")


def process_snapshot() -> list[str]:
    result = subprocess.run(
        ["ps", "-eo", "pid=,args="],
        check=True,
        capture_output=True,
        text=True,
    )
    own_pid = os.getpid()
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and not line.lstrip().startswith(str(own_pid) + " ")
    ]


def busy_processes(lines: list[str]) -> list[str]:
    return sorted(
        {
            line
            for line in lines
            if any(pattern in line for pattern in BUSY_PATTERNS)
            and "watch_strict_v4_pug_confirmation.py" not in line
        }
    )


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def check_once(
    *,
    protocol: dict[str, Any],
    root: Path,
    result_root: Path,
    state_path: Path,
    prior_idle_count: int,
    launch: bool,
) -> tuple[dict[str, Any], int]:
    if (result_root / "confirmation_complete").is_file():
        state = {
            "state": "terminal_confirmation_present",
            "idle_consecutive_polls": prior_idle_count,
            "launched": False,
        }
        write_state(state_path, state)
        return state, prior_idle_count
    busy = busy_processes(process_snapshot())
    idle_count = 0 if busy else prior_idle_count + 1
    required = int(protocol["execution"]["resource_idle_consecutive_polls"])
    state: dict[str, Any] = {
        "state": "waiting_for_resources" if busy else "resources_idle",
        "busy_process_count": len(busy),
        "busy_processes": busy,
        "idle_consecutive_polls": idle_count,
        "required_idle_consecutive_polls": required,
        "launched": False,
    }
    if not busy and idle_count >= required and launch:
        log = result_root / "runner.nohup.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("ab") as destination:
            process = subprocess.Popen(
                ["bash", str(root / "scripts/run_strict_v4_pug_confirmation.sh")],
                cwd=root,
                env={**os.environ, "PROJECT_ROOT": str(root)},
                stdin=subprocess.DEVNULL,
                stdout=destination,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        state.update(
            {
                "state": "runner_launched",
                "launched": True,
                "runner_pid": process.pid,
            }
        )
    write_state(state_path, state)
    return state, idle_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/strict_v4_pug_confirmation_v1"),
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("results/strict_v4_pug_confirmation_v1/watcher_state.json"),
    )
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol = load(resolve(args.protocol))
    validate_protocol(protocol, root)
    result_root = resolve(args.result_root)
    state_path = resolve(args.state)
    idle_count = 0
    while True:
        state, idle_count = check_once(
            protocol=protocol,
            root=root,
            result_root=result_root,
            state_path=state_path,
            prior_idle_count=idle_count,
            launch=not args.no_launch,
        )
        print(json.dumps(state, sort_keys=True), flush=True)
        if args.once or state["state"] in {
            "runner_launched",
            "terminal_confirmation_present",
        }:
            return
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()

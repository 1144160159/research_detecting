from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def step_complete(step: dict[str, Any]) -> bool:
    expected = step.get("expected_files")
    return bool(expected) and all(Path(path).is_file() for path in expected)


def active_gpu_processes() -> list[str]:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,process_name",
            "--format=csv,noheader",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def run_step(step: dict[str, Any], cwd: Path, log_root: Path) -> None:
    if step_complete(step):
        return
    role = str(step["role"])
    command = [str(value) for value in step["command"]]
    log_root.mkdir(parents=True, exist_ok=True)
    log = log_root / f"{role}.log"
    with log.open("a", encoding="utf-8") as handle:
        subprocess.run(command, cwd=cwd, check=True, stdout=handle, stderr=subprocess.STDOUT)
    if not step_complete(step):
        raise RuntimeError(f"step completed without expected files: {role}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan.get("schema_version") != "strict_v4_final_efficiency_execution_plan_v2":
        raise ValueError("unexpected efficiency execution plan schema")
    if plan.get("manifest_sha256") != canonical_hash(plan):
        raise ValueError("efficiency execution plan SHA mismatch")
    if plan.get("implementation_sha256", {}).get(
        "efficiency_execution_plan_executor"
    ) != file_hash(Path(__file__)):
        raise ValueError("active efficiency executor SHA mismatch")
    output_root = Path(plan["output_root"])
    lock = output_root / "executor.lock.d"
    output_root.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError("efficiency execution plan is already active")
    try:
        active = active_gpu_processes()
        if active:
            raise RuntimeError("exclusive GPU gate failed: " + "; ".join(active))
        for block in plan["training_blocks"]:
            log_root = (
                output_root
                / "logs"
                / "training"
                / block["suite"]
                / block["scenario"]
                / f"rep{block['repetition']}"
            )
            for step in block["steps"]:
                run_step(step, args.project_root, log_root)
        for block in plan["inference_blocks"]:
            log_root = output_root / "logs" / "inference" / block["suite"] / block["scenario"]
            for step in block["steps"]:
                run_step(step, args.project_root, log_root)
        (output_root / "execution_complete").touch()
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()

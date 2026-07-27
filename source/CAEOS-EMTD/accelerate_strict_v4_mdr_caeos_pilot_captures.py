from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import traceback
from typing import Any

from accelerate_strict_v4_comparative_corruption import write_json
from accelerate_strict_v4_comparative_final_gap import process_snapshot
from capture_pairwise_runtime import file_hash
from run_strict_v4_mdr_caeos_pilot import (
    load,
    validate_capture,
    validate_protocol,
    weight_directory,
)


def validate_paused_pilot_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("state") not in {"T", "t"}:
        raise ValueError("MDR pilot runner is not stopped")
    if "run_strict_v4_mdr_caeos_pilot.py" not in str(
        snapshot.get("cmdline", "")
    ):
        raise ValueError("unexpected MDR pilot runner command")
    active_children = [
        child
        for child in snapshot.get("direct_children", [])
        if child.get("state") != "Z"
    ]
    if active_children:
        raise ValueError("MDR pilot runner still has active children")


def task_matrix(
    protocol: dict[str, Any], design: dict[str, Any]
) -> list[dict[str, Any]]:
    sources = {
        (str(record["suite"]), str(record["scenario"])): record
        for record in protocol["source_registry"]
    }
    weights = [
        float(value)
        for value in design["mechanism"][
            "training_augmentation_weight_grid"
        ]
    ]
    tasks = []
    index = 0
    for suite, scenarios in sorted(design["pilot"]["scenarios"].items()):
        for scenario in scenarios:
            source = sources[(suite, scenario)]
            for weight in weights:
                tasks.append(
                    {
                        "index": index,
                        "suite": str(suite),
                        "scenario": str(scenario),
                        "weight": float(weight),
                        "source": source,
                    }
                )
                index += 1
    expected = int(design["pilot"]["scenario_count"]) * len(weights)
    if len(tasks) != expected or expected != 42:
        raise ValueError("MDR pilot capture matrix must contain 42 tasks")
    return tasks


def validate_implementations(
    protocol: dict[str, Any], project_root: Path
) -> None:
    for name, relative in protocol["implementation"].items():
        actual = file_hash(project_root / relative)
        expected = protocol["implementation_sha256"][name]
        if actual != expected:
            raise ValueError(
                f"MDR pilot implementation SHA mismatch: {name}"
            )


def capture_command(
    *,
    protocol: dict[str, Any],
    design: dict[str, Any],
    project_root: Path,
    capture_dir: Path,
    task: dict[str, Any],
) -> list[str]:
    return [
        sys.executable,
        str(project_root / protocol["implementation"]["capture"]),
        "--clean-trainer",
        str(project_root / protocol["implementation"]["clean_trainer"]),
        "--robust-trainer",
        str(project_root / protocol["implementation"]["robust_trainer"]),
        "--capture-dir",
        str(capture_dir),
        "--suite",
        task["suite"],
        "--scenario",
        task["scenario"],
        "--weight",
        str(task["weight"]),
        "--sample-fraction",
        str(design["mechanism"]["training_sample_fraction"]),
        "--training-seed",
        str(design["pilot"]["training_seed"]),
        "--augmentation-seed",
        str(design["pilot"]["training_seed"]),
        "--health-quantile",
        str(design["mechanism"]["health_gate"]["quantile"]),
        "--validation-corruption-seed",
        str(design["pilot"]["corruption_seed"]),
        "--",
        *task["source"]["base_trainer_arguments"],
    ]


def execute_task(
    *,
    serial_runner_pid: int,
    protocol: dict[str, Any],
    design: dict[str, Any],
    project_root: Path,
    captures_root: Path,
    claims_root: Path,
    failures_root: Path,
    task: dict[str, Any],
) -> dict[str, Any]:
    validate_paused_pilot_snapshot(process_snapshot(serial_runner_pid))
    capture_dir = (
        captures_root
        / task["suite"]
        / task["scenario"]
        / weight_directory(task["weight"])
    )
    manifest = capture_dir / "capture_manifest.json"
    if validate_capture(
        manifest, task["suite"], task["scenario"], task["weight"]
    ):
        return {"index": task["index"], "status": "already_complete"}
    if capture_dir.exists() and any(capture_dir.iterdir()):
        raise ValueError(f"unclaimed partial MDR capture: {capture_dir}")
    claim = claims_root / f"{int(task['index']):02d}.lock.d"
    try:
        claim.mkdir(parents=True)
    except FileExistsError:
        return {"index": task["index"], "status": "already_claimed"}
    owner = {
        "schema_version": "strict_v4_mdr_pilot_parallel_claim_v1",
        "task": {
            key: task[key]
            for key in ("index", "suite", "scenario", "weight")
        },
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_unix": time.time(),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
    }
    write_json(claim / "owner.json", owner)
    try:
        capture_dir.mkdir(parents=True, exist_ok=True)
        log_path = capture_dir / "parallel_capture.log"
        with log_path.open("w", encoding="utf-8") as log:
            subprocess.run(
                capture_command(
                    protocol=protocol,
                    design=design,
                    project_root=project_root,
                    capture_dir=capture_dir,
                    task=task,
                ),
                cwd=project_root,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        validate_capture(
            manifest, task["suite"], task["scenario"], task["weight"]
        )
        (claim / "owner.json").unlink()
        claim.rmdir()
        return {
            "index": task["index"],
            "status": "completed",
            "suite": task["suite"],
            "scenario": task["scenario"],
            "weight": task["weight"],
            "capture_manifest_file_sha256": file_hash(manifest),
        }
    except Exception as error:
        failure = {
            "schema_version": "strict_v4_mdr_pilot_parallel_failure_v1",
            "task": {
                key: task[key]
                for key in ("index", "suite", "scenario", "weight")
            },
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
        write_json(
            failures_root / f"{int(task['index']):02d}.json", failure
        )
        return {
            "index": task["index"],
            "status": "failed",
            "error_type": type(error).__name__,
            "error": str(error),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--serial-runner-pid", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= int(args.workers) <= 4:
        raise ValueError("MDR pilot workers must be between 1 and 4")
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    run_root = args.run_root.resolve()
    protocol = load(protocol_path)
    validate_protocol(protocol)
    design = load(project_root / protocol["design_path"])
    if design["manifest_sha256"] != protocol["design_manifest_sha256"]:
        raise ValueError("MDR pilot design binding mismatch")
    validate_implementations(protocol, project_root)
    snapshot = process_snapshot(int(args.serial_runner_pid))
    validate_paused_pilot_snapshot(snapshot)
    tasks = task_matrix(protocol, design)
    captures_root = run_root / "captures"
    captures_root.mkdir(parents=True, exist_ok=True)
    pending = []
    for task in tasks:
        manifest = (
            captures_root
            / task["suite"]
            / task["scenario"]
            / weight_directory(task["weight"])
            / "capture_manifest.json"
        )
        if validate_capture(
            manifest, task["suite"], task["scenario"], task["weight"]
        ):
            continue
        capture_dir = manifest.parent
        if capture_dir.exists() and any(capture_dir.iterdir()):
            continue
        pending.append(task)
    if not pending:
        raise ValueError("no non-frontier MDR pilot captures selected")

    parallel_root = run_root / "parallel_runs" / str(args.run_id)
    try:
        parallel_root.mkdir(parents=True)
    except FileExistsError:
        raise RuntimeError(f"MDR pilot run id exists: {args.run_id}")
    claims_root = run_root / "parallel_claims"
    failures_root = parallel_root / "failures"
    manifest = {
        "schema_version": "strict_v4_mdr_pilot_parallel_run_v1",
        "run_id": str(args.run_id),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "accelerator_sha256": file_hash(Path(__file__)),
        "serial_runner_preflight": snapshot,
        "workers": int(args.workers),
        "selected_task_indices": [task["index"] for task in pending],
        "selected_task_count": len(pending),
        "frontier_partial_capture_excluded": True,
        "requires_stopped_serial_runner_before_every_task": True,
        "uses_frozen_capture_command": True,
        "changes_training_arguments": False,
        "created_at_unix": time.time(),
    }
    write_json(parallel_root / "manifest.json", manifest)
    results = []
    with ThreadPoolExecutor(max_workers=int(args.workers)) as executor:
        futures = {
            executor.submit(
                execute_task,
                serial_runner_pid=int(args.serial_runner_pid),
                protocol=protocol,
                design=design,
                project_root=project_root,
                captures_root=captures_root,
                claims_root=claims_root,
                failures_root=failures_root,
                task=task,
            ): task["index"]
            for task in pending
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    complete_count = 0
    for task in tasks:
        manifest = (
            captures_root
            / task["suite"]
            / task["scenario"]
            / weight_directory(task["weight"])
            / "capture_manifest.json"
        )
        complete_count += int(
            validate_capture(
                manifest,
                task["suite"],
                task["scenario"],
                task["weight"],
            )
        )
    summary = {
        "schema_version": "strict_v4_mdr_pilot_parallel_summary_v1",
        "run_manifest_sha256": load(
            parallel_root / "manifest.json"
        )["manifest_sha256"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "result_count": len(results),
        "status_counts": status_counts,
        "failed": status_counts.get("failed", 0),
        "complete_capture_count": complete_count,
        "expected_capture_count": 42,
        "results": sorted(results, key=lambda item: int(item["index"])),
    }
    write_json(parallel_root / "summary.json", summary)
    if summary["failed"] or complete_count != 42:
        raise RuntimeError("MDR pilot parallel capture completion failed")


if __name__ == "__main__":
    main()

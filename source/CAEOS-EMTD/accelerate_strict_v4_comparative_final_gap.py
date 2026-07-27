from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import time
from typing import Any

from accelerate_strict_v4_comparative_corruption import (
    block_path,
    contiguous_completed,
    execute_source,
    load_protocol,
    validate_block,
    validate_implementations,
    write_json,
)
from create_strict_v4_external_confirmation_protocol import file_hash


def process_snapshot(pid: int) -> dict[str, Any]:
    proc = Path("/proc")
    stat_path = proc / str(int(pid)) / "stat"
    cmdline_path = proc / str(int(pid)) / "cmdline"
    if not stat_path.is_file() or not cmdline_path.is_file():
        raise ValueError("serial runner process does not exist")
    stat = stat_path.read_text(encoding="utf-8").split()
    state = stat[2]
    cmdline = cmdline_path.read_bytes().replace(b"\x00", b" ").decode(
        "utf-8", errors="replace"
    )
    children = []
    for child_stat_path in proc.glob("[0-9]*/stat"):
        try:
            child_stat = child_stat_path.read_text(
                encoding="utf-8"
            ).split()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if len(child_stat) > 3 and int(child_stat[3]) == int(pid):
            children.append(
                {
                    "pid": int(child_stat[0]),
                    "state": child_stat[2],
                }
            )
    return {
        "pid": int(pid),
        "state": state,
        "cmdline": cmdline,
        "direct_children": sorted(children, key=lambda item: item["pid"]),
    }


def validate_paused_serial_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("state") not in {"T", "t"}:
        raise ValueError("serial runner is not stopped")
    if "run_strict_v4_comparative_corruption.py" not in str(
        snapshot.get("cmdline", "")
    ):
        raise ValueError("unexpected serial runner command")
    active_children = [
        child
        for child in snapshot.get("direct_children", [])
        if child.get("state") != "Z"
    ]
    if active_children:
        raise ValueError("serial runner still has active direct children")


def pending_indices(
    protocol: dict[str, Any],
    output_root: Path,
    minimum_source_index: int,
) -> list[int]:
    output = []
    for index in range(
        len(protocol["source_registry"]) - 1,
        int(minimum_source_index) - 1,
        -1,
    ):
        source = protocol["source_registry"][index]
        result = block_path(output_root, source) / "paired_corruption.json"
        if result.is_file():
            validate_block(result, protocol, source)
        else:
            output.append(index)
    return output


def guarded_execute(
    *,
    serial_runner_pid: int,
    execution_arguments: dict[str, Any],
) -> dict[str, Any]:
    validate_paused_serial_snapshot(
        process_snapshot(int(serial_runner_pid))
    )
    return execute_source(
        **execution_arguments,
        minimum_frontier_gap=0,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--minimum-source-index", type=int, required=True)
    parser.add_argument("--serial-runner-pid", type=int, required=True)
    args = parser.parse_args()
    if not 1 <= int(args.workers) <= 4:
        raise ValueError("final-gap workers must be between 1 and 4")
    if int(args.minimum_source_index) < 0:
        raise ValueError("minimum source index must be nonnegative")

    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    output_root = args.output_root.resolve()
    protocol = load_protocol(protocol_path)
    validate_implementations(protocol, project_root)
    snapshot = process_snapshot(int(args.serial_runner_pid))
    validate_paused_serial_snapshot(snapshot)
    frontier = contiguous_completed(protocol, output_root)
    if int(args.minimum_source_index) <= frontier:
        raise ValueError(
            "final-gap accelerator must leave the serial-frontier task "
            "to the paused runner"
        )
    indices = pending_indices(
        protocol, output_root, int(args.minimum_source_index)
    )
    if not indices:
        raise ValueError("no final-gap tasks selected")

    run_root = (
        output_root / "parallel_runs" / str(args.run_id)
    )
    try:
        run_root.mkdir(parents=True)
    except FileExistsError:
        raise RuntimeError(f"parallel run id already exists: {args.run_id}")
    claims_root = output_root / "parallel_claims"
    failures_root = run_root / "failures"
    manifest = {
        "schema_version": (
            "strict_v4_comparative_final_gap_parallel_run_v1"
        ),
        "run_id": str(args.run_id),
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "final_gap_accelerator_sha256": file_hash(Path(__file__)),
        "shared_accelerator_sha256": file_hash(
            project_root
            / "accelerate_strict_v4_comparative_corruption.py"
        ),
        "workers": int(args.workers),
        "minimum_source_index": int(args.minimum_source_index),
        "serial_contiguous_frontier_at_start": frontier,
        "serial_runner_preflight": snapshot,
        "selected_source_indices_descending": indices,
        "selected_task_count": len(indices),
        "serial_frontier_task_is_excluded": True,
        "requires_stopped_serial_runner_before_every_task": True,
        "uses_frozen_capture_and_evaluator_commands": True,
        "changes_training_or_evaluation_arguments_other_than_output_dir": (
            False
        ),
        "created_at_unix": time.time(),
    }
    write_json(run_root / "manifest.json", manifest)
    results = []
    with ThreadPoolExecutor(max_workers=int(args.workers)) as executor:
        futures = {}
        for index in indices:
            arguments = {
                "index": index,
                "protocol": protocol,
                "protocol_path": protocol_path,
                "output_root": output_root,
                "project_root": project_root,
                "claims_root": claims_root,
                "failures_root": failures_root,
            }
            future = executor.submit(
                guarded_execute,
                serial_runner_pid=int(args.serial_runner_pid),
                execution_arguments=arguments,
            )
            futures[future] = index
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    summary = {
        "schema_version": (
            "strict_v4_comparative_final_gap_parallel_summary_v1"
        ),
        "run_manifest_sha256": json.loads(
            (run_root / "manifest.json").read_text(encoding="utf-8")
        )["manifest_sha256"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "result_count": len(results),
        "status_counts": status_counts,
        "failed": status_counts.get("failed", 0),
        "serial_contiguous_frontier_at_end": contiguous_completed(
            protocol, output_root
        ),
        "results": sorted(results, key=lambda item: int(item["index"])),
    }
    write_json(run_root / "summary.json", summary)
    if summary["failed"]:
        raise RuntimeError(
            f"final-gap comparative tasks failed: {summary['failed']}"
        )


if __name__ == "__main__":
    main()

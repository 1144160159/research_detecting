from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import socket
import sys
import time
import traceback
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_final_efficiency_execution_plan_v2 import replace_option
from run_strict_v4_comparative_corruption import provenance_arguments, run


PROTOCOL_SCHEMA = "strict_v4_comparative_corruption_protocol_v2"
BLOCK_SCHEMA = "strict_v4_comparative_corruption_block_v1"
EXPECTED_SOURCE_COUNT = 306


def load_protocol(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("schema_version") != PROTOCOL_SCHEMA
        or value.get("manifest_sha256") != canonical_hash(value)
        or len(value.get("source_registry", [])) != EXPECTED_SOURCE_COUNT
    ):
        raise ValueError("comparative corruption protocol validation failed")
    return value


def block_path(root: Path, source: dict[str, Any]) -> Path:
    return (
        root
        / "blocks"
        / str(source["suite"])
        / str(source["scenario"])
        / f"seed{int(source['seed'])}"
    )


def validate_block(
    path: Path,
    protocol: dict[str, Any],
    source: dict[str, Any],
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    families = set(protocol["corruption_conditions"]["families"])
    if (
        value.get("schema_version") != BLOCK_SCHEMA
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("suite") != source["suite"]
        or value.get("scenario") != source["scenario"]
        or int(value.get("seed", -1)) != int(source["seed"])
        or value.get("source_split_fingerprint")
        != source["split_fingerprint"]
        or value.get("candidate_comparator_input_arrays_equal") is not True
        or value.get(
            "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation"
        )
        is not False
        or {item.get("family") for item in value.get("conditions", [])}
        != families
    ):
        raise ValueError(f"paired corruption block validation failed: {path}")
    return value


def validate_block_with_retry(
    path: Path,
    protocol: dict[str, Any],
    source: dict[str, Any],
    attempts: int = 10,
    delay_seconds: float = 0.2,
) -> dict[str, Any]:
    error: Exception | None = None
    for _ in range(attempts):
        try:
            return validate_block(path, protocol, source)
        except (json.JSONDecodeError, OSError) as current:
            error = current
            time.sleep(delay_seconds)
    if error is not None:
        raise error
    raise RuntimeError("block validation retry exhausted without an error")


def contiguous_completed(
    protocol: dict[str, Any],
    root: Path,
) -> int:
    completed = 0
    for source in protocol["source_registry"]:
        output = block_path(root, source) / "paired_corruption.json"
        if not output.is_file():
            break
        validate_block_with_retry(output, protocol, source)
        completed += 1
    return completed


def select_pending_indices(
    protocol: dict[str, Any],
    root: Path,
    minimum_source_index: int,
    minimum_frontier_gap: int,
    max_tasks: int | None,
) -> tuple[int, list[int]]:
    frontier = contiguous_completed(protocol, root)
    if minimum_source_index < frontier + minimum_frontier_gap:
        raise ValueError(
            "minimum source index does not preserve the required serial-frontier gap"
        )
    pending: list[int] = []
    for index in range(len(protocol["source_registry"]) - 1, minimum_source_index - 1, -1):
        source = protocol["source_registry"][index]
        output = block_path(root, source) / "paired_corruption.json"
        if output.is_file():
            validate_block(output, protocol, source)
            continue
        pending.append(index)
        if max_tasks is not None and len(pending) >= max_tasks:
            break
    return frontier, pending


def validate_implementations(
    protocol: dict[str, Any],
    project_root: Path,
) -> None:
    active_paths = {
        "candidate_trainer": project_root / "train_hybrid_open_set.py",
        "candidate_runtime": project_root / "caeos" / "pairwise_runtime.py",
        "candidate_capture": project_root / "capture_pairwise_runtime.py",
        "comparator_runtime": project_root / "caeos" / "open_detect_runtime.py",
        "comparator_capture": project_root / "capture_opendetect_runtime.py",
        "evaluator": project_root / "evaluate_strict_v4_comparative_corruption.py",
        "runner": project_root / "run_strict_v4_comparative_corruption.py",
    }
    expected = protocol["implementation_sha256"]
    for name, path in active_paths.items():
        if file_hash(path) != expected[name]:
            raise ValueError(
                f"active comparative corruption implementation SHA mismatch: {name}"
            )


def ensure_no_unclaimed_partial_block(block: Path) -> None:
    output = block / "paired_corruption.json"
    if output.is_file():
        return
    partial_markers = (
        block / "candidate_capture.log",
        block / "comparator_capture.log",
        block / "evaluation.log",
    )
    partial_directories = (
        block / "candidate_refit",
        block / "candidate_capture",
        block / "comparator_capture",
    )
    if any(path.exists() for path in (*partial_markers, *partial_directories)):
        raise RuntimeError(f"unclaimed partial comparative block exists: {block}")


def write_json(path: Path, value: dict[str, Any]) -> None:
    payload = dict(value)
    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def execute_source(
    *,
    index: int,
    protocol: dict[str, Any],
    protocol_path: Path,
    output_root: Path,
    project_root: Path,
    claims_root: Path,
    failures_root: Path,
    minimum_frontier_gap: int,
) -> dict[str, Any]:
    source = protocol["source_registry"][index]
    suite = str(source["suite"])
    scenario = str(source["scenario"])
    seed = int(source["seed"])
    block = block_path(output_root, source)
    output = block / "paired_corruption.json"
    if output.is_file():
        validate_block(output, protocol, source)
        return {"index": index, "status": "already_complete"}

    frontier = contiguous_completed(protocol, output_root)
    if index < frontier + minimum_frontier_gap:
        return {
            "index": index,
            "status": "deferred_frontier_gap",
            "frontier": frontier,
        }

    claim = claims_root / f"{index:03d}.lock.d"
    try:
        claim.mkdir(parents=True)
    except FileExistsError:
        return {"index": index, "status": "already_claimed"}

    owner = {
        "schema_version": "strict_v4_comparative_parallel_claim_v1",
        "source_index": index,
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_unix": time.time(),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
    }
    write_json(claim / "owner.json", owner)
    try:
        if output.is_file():
            validate_block(output, protocol, source)
            (claim / "owner.json").unlink()
            claim.rmdir()
            return {"index": index, "status": "completed_after_claim"}
        ensure_no_unclaimed_partial_block(block)

        candidate_capture = block / "candidate_capture"
        comparator_capture = block / "comparator_capture"
        candidate_root = Path(source["candidate_root"])
        comparator_root = Path(source["comparator_root"])
        trainer_args = provenance_arguments(
            candidate_root / "provenance.json",
            suite,
            scenario,
            seed,
        )
        trainer_args = replace_option(
            trainer_args,
            "--output-dir",
            str(block / "candidate_refit"),
        )
        run(
            [
                sys.executable,
                "capture_pairwise_runtime.py",
                "--trainer",
                "train_hybrid_open_set.py",
                "--capture-dir",
                str(candidate_capture),
                "--",
                *trainer_args,
            ],
            project_root,
            block / "candidate_capture.log",
        )
        run(
            [
                sys.executable,
                "capture_opendetect_runtime.py",
                "--source-run",
                str(comparator_root),
                "--capture-dir",
                str(comparator_capture),
                "--device",
                "cpu",
                "--absolute-tolerance",
                "1e-12",
                "--equivalence-mode",
                "same_device_shadow",
            ],
            project_root,
            block / "comparator_capture.log",
        )
        run(
            [
                sys.executable,
                "evaluate_strict_v4_comparative_corruption.py",
                "--protocol",
                str(protocol_path),
                "--suite",
                suite,
                "--scenario",
                scenario,
                "--seed",
                str(seed),
                "--candidate-capture",
                str(candidate_capture),
                "--comparator-capture",
                str(comparator_capture),
                "--output",
                str(output),
            ],
            project_root,
            block / "evaluation.log",
        )
        value = validate_block(output, protocol, source)
        (claim / "owner.json").unlink()
        claim.rmdir()
        return {
            "index": index,
            "status": "completed",
            "suite": suite,
            "scenario": scenario,
            "seed": seed,
            "block_manifest_sha256": value["manifest_sha256"],
        }
    except Exception as error:
        failure = {
            "schema_version": "strict_v4_comparative_parallel_failure_v1",
            "source_index": index,
            "suite": suite,
            "scenario": scenario,
            "seed": seed,
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
        write_json(failures_root / f"{index:03d}.json", failure)
        return {
            "index": index,
            "status": "failed",
            "error_type": type(error).__name__,
            "error": str(error),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", type=int, required=True)
    parser.add_argument("--minimum-source-index", type=int, required=True)
    parser.add_argument("--minimum-frontier-gap", type=int, default=32)
    parser.add_argument("--max-tasks", type=int)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 16:
        raise ValueError("workers must be between 1 and 16")
    if args.minimum_source_index < 0:
        raise ValueError("minimum source index must be nonnegative")
    if args.minimum_frontier_gap < 16:
        raise ValueError("minimum frontier gap must be at least 16")
    if args.max_tasks is not None and args.max_tasks < 1:
        raise ValueError("max tasks must be positive")

    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    output_root = args.output_root.resolve()
    protocol = load_protocol(protocol_path)
    validate_implementations(protocol, project_root)
    frontier, indices = select_pending_indices(
        protocol,
        output_root,
        args.minimum_source_index,
        args.minimum_frontier_gap,
        args.max_tasks,
    )
    run_root = output_root / "parallel_runs" / args.run_id
    try:
        run_root.mkdir(parents=True)
    except FileExistsError:
        raise RuntimeError(f"parallel run id already exists: {args.run_id}")
    claims_root = output_root / "parallel_claims"
    failures_root = run_root / "failures"
    manifest = {
        "schema_version": "strict_v4_comparative_parallel_run_v1",
        "run_id": args.run_id,
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "accelerator_sha256": file_hash(Path(__file__)),
        "workers": args.workers,
        "minimum_source_index": args.minimum_source_index,
        "minimum_frontier_gap": args.minimum_frontier_gap,
        "max_tasks": args.max_tasks,
        "serial_contiguous_frontier_at_start": frontier,
        "selected_source_indices_descending": indices,
        "selected_task_count": len(indices),
        "uses_frozen_capture_and_evaluator_commands": True,
        "changes_training_or_evaluation_arguments_other_than_output_dir": False,
        "parallel_results_require_original_block_manifest_validation": True,
        "created_at_unix": time.time(),
    }
    write_json(run_root / "manifest.json", manifest)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                execute_source,
                index=index,
                protocol=protocol,
                protocol_path=protocol_path,
                output_root=output_root,
                project_root=project_root,
                claims_root=claims_root,
                failures_root=failures_root,
                minimum_frontier_gap=args.minimum_frontier_gap,
            ): index
            for index in indices
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    summary = {
        "schema_version": "strict_v4_comparative_parallel_summary_v1",
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
        raise RuntimeError(f"parallel comparative tasks failed: {summary['failed']}")


if __name__ == "__main__":
    main()

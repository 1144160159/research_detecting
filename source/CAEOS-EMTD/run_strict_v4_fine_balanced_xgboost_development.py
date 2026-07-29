from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from run_strict_v4_packet_sequence_fusion_development import (
    ResourceSampler,
    resource_summary,
    slug,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def task_command(
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    unknown_family: str,
    output_dir: Path,
) -> list[str]:
    training = protocol["training"]
    execution = protocol["execution"]
    return [
        str(python.resolve()),
        str(
            project_root
            / "train_strict_v4_fine_balanced_xgboost_task_cuda.py"
        ),
        "--cache-csv",
        protocol["fine_balanced_cache"]["path"],
        "--config",
        protocol["fine_balanced_cache"]["config_path"],
        "--unknown-family",
        unknown_family,
        "--seed",
        str(protocol["development_seed"]),
        "--output-dir",
        str(output_dir),
        "--required-gpu-uuid",
        execution["required_gpu_uuid"],
        "--xgboost-root",
        execution["xgboost_root"],
        "--max-per-class",
        str(protocol["fine_balanced_cache"]["maximum_per_fine_class"]),
        "--chunksize",
        str(training["chunksize"]),
        "--estimators",
        str(training["estimators"]),
        "--max-depth",
        str(training["max_depth"]),
        "--learning-rate",
        str(training["learning_rate"]),
        "--subsample",
        str(training["subsample"]),
        "--colsample-bytree",
        str(training["colsample_bytree"]),
        "--early-stopping-rounds",
        str(training["early_stopping_rounds"]),
        "--jobs",
        str(training["jobs"]),
        "--gpu-sample-interval-seconds",
        str(execution["gpu_sample_interval_seconds"]),
    ]


def run_one(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    unknown_family: str,
    run_root: Path,
) -> dict[str, Any]:
    output_dir = run_root / (
        f"unknown_{slug(unknown_family)}_seed{protocol['development_seed']}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "execution.log"
    with log_path.open("wb") as log:
        completed = subprocess.run(
            task_command(
                python,
                project_root,
                protocol,
                unknown_family,
                output_dir,
            ),
            cwd=project_root,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"fine-balanced XGBoost task {unknown_family} "
            f"exited {completed.returncode}"
        )
    metrics = load_canonical(
        output_dir / "metrics.json", "fine-balanced XGBoost task metrics"
    )
    gpu = load_canonical(
        output_dir / "gpu_execution.json", "fine-balanced GPU evidence"
    )
    if (
        metrics.get("state") != "complete"
        or metrics.get("task", {}).get("unknown_family") != unknown_family
        or not metrics.get("gpu_execution", {}).get("passes")
        or not gpu.get("passes")
        or not gpu.get("xgboost_cuda_model_configs_verified")
        or gpu.get("gpu_identity", {}).get("uuid")
        != protocol["execution"]["required_gpu_uuid"]
    ):
        raise ValueError(
            f"fine-balanced XGBoost CUDA evidence failed for {unknown_family}"
        )
    artifact_sha256 = {
        "metrics.json": file_hash(output_dir / "metrics.json"),
        "gpu_execution.json": file_hash(output_dir / "gpu_execution.json"),
    }
    for artifact in metrics["artifacts"].values():
        path = output_dir / artifact["file"]
        if file_hash(path) != artifact["sha256"]:
            raise ValueError(f"task artifact drifted: {path}")
        artifact_sha256[artifact["file"]] = artifact["sha256"]
    return {
        "unknown_family": unknown_family,
        "output_dir": str(output_dir),
        "artifact_sha256": artifact_sha256,
        "gpu_peak_utilization_percent": gpu["peak_gpu_utilization_percent"],
        "gpu_peak_memory_mib": gpu["peak_gpu_memory_mib"],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = load_canonical(protocol_path, "FB-FSX-CAEOS protocol")
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"implementation drifted after protocol freeze: {name}")
    run_root = Path(protocol["paths"]["run_root"])
    result_root = Path(protocol["paths"]["result_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    result_root.mkdir(parents=True, exist_ok=True)
    progress_path = result_root / "realtime_progress.json"
    completed_tasks = {}
    failures = {}
    sampler = ResourceSampler()
    sampler.start()
    started = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=protocol["execution"]["maximum_parallel_tasks"]
        ) as executor:
            futures = {
                executor.submit(
                    run_one,
                    python=args.python,
                    project_root=project_root,
                    protocol=protocol,
                    unknown_family=family,
                    run_root=run_root,
                ): family
                for family in protocol["unknown_families"]
            }
            for future in concurrent.futures.as_completed(futures):
                family = futures[future]
                try:
                    completed_tasks[family] = future.result()
                except Exception as error:
                    failures[family] = f"{type(error).__name__}: {error}"
                progress: dict[str, Any] = {
                    "schema_version": (
                        "strict_v4_fine_balanced_xgboost_progress_v1"
                    ),
                    "state": "running",
                    "completed_tasks": sorted(completed_tasks),
                    "failures": failures,
                    "pending_tasks": sorted(
                        set(protocol["unknown_families"])
                        - set(completed_tasks)
                        - set(failures)
                    ),
                    "updated_unix_seconds": time.time(),
                }
                progress["manifest_sha256"] = canonical_hash(progress)
                atomic_json(progress_path, progress)
    finally:
        sampler.stop()
    passed = len(completed_tasks) == protocol["expected_task_count"] and not failures
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fine_balanced_xgboost_completion_v1"
        ),
        "state": "complete" if passed else "failed",
        "seed": protocol["development_seed"],
        "expected_task_count": protocol["expected_task_count"],
        "completed_task_count": len(completed_tasks),
        "failure_count": len(failures),
        "failures": failures,
        "task_artifacts": dict(sorted(completed_tasks.items())),
        "elapsed_seconds": time.time() - started,
        "gpu_execution": {
            "all_tasks_passed": passed,
            "required_gpu_uuid": protocol["execution"]["required_gpu_uuid"],
        },
        "resource_utilization": resource_summary(sampler),
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "claim_boundary": {
            "development_only": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "formal_training_backend": "xgboost_cuda",
            "numpy_input_requires_host_to_device_transfer": True,
        },
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    atomic_json(args.output.resolve(), completion)
    if not passed:
        raise RuntimeError(
            f"FB-FSX-CAEOS development failed: {failures}"
        )
    return completion


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    completion = run(parse_arguments())
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

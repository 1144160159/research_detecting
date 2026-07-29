from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)
from verify_xgboost_cuda_backend import query_gpu


def slug(value: str) -> str:
    return value.lower().replace(" ", "_")


def read_cpu_counters() -> tuple[int, int]:
    fields = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()
    values = [int(value) for value in fields[1:]]
    total = sum(values)
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return total, idle


class ResourceSampler:
    def __init__(self, interval_seconds: float = 0.5) -> None:
        self.interval_seconds = interval_seconds
        self.samples: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=max(2.0, self.interval_seconds * 4))

    def _run(self) -> None:
        previous_total, previous_idle = read_cpu_counters()
        while not self._stop.wait(self.interval_seconds):
            try:
                total, idle = read_cpu_counters()
                total_delta = total - previous_total
                idle_delta = idle - previous_idle
                cpu_busy = (
                    100.0 * (total_delta - idle_delta) / total_delta
                    if total_delta > 0
                    else 0.0
                )
                previous_total, previous_idle = total, idle
                gpu = query_gpu()
                self.samples.append(
                    {
                        "sampled_at_utc": gpu["sampled_at_utc"],
                        "cpu_busy_percent": cpu_busy,
                        "gpu_utilization_percent": gpu[
                            "utilization_percent"
                        ],
                        "gpu_memory_used_mib": gpu["memory_used_mib"],
                        "gpu_power_draw_watts": gpu["power_draw_watts"],
                        "gpu_compute_processes": gpu["compute_processes"],
                    }
                )
            except Exception as error:
                self.errors.append(f"{type(error).__name__}: {error}")


def task_command(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    unknown_family: str,
    output_dir: Path,
) -> list[str]:
    training = protocol["training"]
    execution = protocol["execution"]
    command = [
        str(python.resolve()),
        str(project_root / "train_strict_v4_packet_sequence_fusion_task_cuda.py"),
        "--sequence-dataset",
        protocol["sequence_dataset"]["path"],
        "--unknown-family",
        unknown_family,
        "--seed",
        str(protocol["development_seed"]),
        "--output-dir",
        str(output_dir),
        "--required-gpu-uuid",
        execution["required_gpu_uuid"],
        "--gpu-index",
        str(execution["gpu_index"]),
        "--epochs",
        str(training["epochs"]),
        "--batch-size",
        str(training["batch_size"]),
        "--inference-batch-size",
        str(training["inference_batch_size"]),
        "--learning-rate",
        str(training["learning_rate"]),
        "--weight-decay",
        str(training["weight_decay"]),
        "--attack-loss-weight",
        str(training["attack_loss_weight"]),
        "--knownness-loss-weight",
        str(training["knownness_loss_weight"]),
        "--boundary-mix-loss-weight",
        str(training["boundary_mix_loss_weight"]),
        "--early-stopping-patience",
        str(training["early_stopping_patience"]),
        "--minimum-improvement",
        str(training["minimum_improvement"]),
        "--gpu-sample-interval-seconds",
        str(execution["gpu_sample_interval_seconds"]),
    ]
    if training.get("require_flow_statistics"):
        command.append("--require-flow-statistics")
    return command


def verify_completed_task(
    *,
    output_dir: Path,
    unknown_family: str,
    required_gpu_uuid: str,
) -> dict[str, Any]:
    metrics = load_canonical(output_dir / "metrics.json", "sequence task metrics")
    gpu = load_canonical(
        output_dir / "gpu_execution.json", "sequence task GPU evidence"
    )
    if (
        metrics.get("task", {}).get("unknown_family") != unknown_family
        or metrics.get("state") != "complete"
        or not metrics.get("gpu_execution", {}).get("passes")
        or not gpu.get("passes")
        or gpu.get("gpu_identity", {}).get("uuid") != required_gpu_uuid
        or not gpu.get("compute_process_observed_by_nvidia_smi")
        or float(gpu.get("torch_peak_memory_allocated_mib", 0.0)) <= 1.0
    ):
        raise ValueError(f"task evidence did not pass for {unknown_family}")
    artifact_sha256 = {
        "metrics.json": file_hash(output_dir / "metrics.json"),
        "gpu_execution.json": file_hash(output_dir / "gpu_execution.json"),
    }
    for artifact in metrics["artifacts"].values():
        artifact_path = output_dir / artifact["file"]
        if file_hash(artifact_path) != artifact["sha256"]:
            raise ValueError(f"task artifact drifted: {artifact_path}")
        artifact_sha256[artifact["file"]] = artifact["sha256"]
    return {
        "unknown_family": unknown_family,
        "output_dir": str(output_dir),
        "artifact_sha256": artifact_sha256,
        "gpu_peak_utilization_percent": gpu[
            "peak_gpu_utilization_percent"
        ],
        "gpu_peak_memory_mib": gpu["peak_gpu_memory_mib"],
    }


def run_one(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    unknown_family: str,
    run_root: Path,
) -> dict[str, Any]:
    output_dir = run_root / f"unknown_{slug(unknown_family)}_seed{protocol['development_seed']}"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        return verify_completed_task(
            output_dir=output_dir,
            unknown_family=unknown_family,
            required_gpu_uuid=protocol["execution"]["required_gpu_uuid"],
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError):
        pass
    command = task_command(
        python=python,
        project_root=project_root,
        protocol=protocol,
        unknown_family=unknown_family,
        output_dir=output_dir,
    )
    log_path = output_dir / "task.log"
    with log_path.open("w", encoding="utf-8") as log_handle:
        completed = subprocess.run(
            command,
            cwd=project_root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if completed.returncode != 0:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        raise RuntimeError(
            f"{unknown_family} exited {completed.returncode}: "
            + " | ".join(lines[-8:])
        )
    return verify_completed_task(
        output_dir=output_dir,
        unknown_family=unknown_family,
        required_gpu_uuid=protocol["execution"]["required_gpu_uuid"],
    )


def resource_summary(sampler: ResourceSampler) -> dict[str, Any]:
    samples = sampler.samples
    if not samples:
        return {
            "sample_count": 0,
            "sample_errors": sampler.errors,
            "passes_observation": False,
        }
    cpu = [sample["cpu_busy_percent"] for sample in samples]
    gpu = [sample["gpu_utilization_percent"] for sample in samples]
    memory = [sample["gpu_memory_used_mib"] for sample in samples]
    return {
        "sample_count": len(samples),
        "sample_errors": sampler.errors,
        "cpu_busy_percent": {
            "mean": sum(cpu) / len(cpu),
            "peak": max(cpu),
            "fraction_at_least_50_percent": sum(value >= 50 for value in cpu)
            / len(cpu),
            "fraction_at_least_80_percent": sum(value >= 80 for value in cpu)
            / len(cpu),
        },
        "gpu_utilization_percent": {
            "mean": sum(gpu) / len(gpu),
            "peak": max(gpu),
            "fraction_at_least_50_percent": sum(value >= 50 for value in gpu)
            / len(gpu),
            "fraction_at_least_80_percent": sum(value >= 80 for value in gpu)
            / len(gpu),
        },
        "gpu_memory_mib": {"peak": max(memory)},
        "passes_observation": not sampler.errors,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    protocol_path = args.protocol.resolve()
    protocol = load_canonical(protocol_path, "packet-sequence protocol")
    if protocol.get("state") != "frozen_development_protocol":
        raise ValueError("packet-sequence development protocol is not frozen")
    project_root = Path(protocol["paths"]["project_root"])
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"implementation drifted after freeze: {name}")
    dataset_path = Path(protocol["sequence_dataset"]["path"])
    if file_hash(dataset_path) != protocol["sequence_dataset"]["sha256"]:
        raise ValueError("sequence dataset drifted after protocol freeze")
    result_root = Path(protocol["paths"]["result_root"])
    run_root = Path(protocol["paths"]["run_root"])
    result_root.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    progress_path = result_root / "realtime_progress.json"
    completed_tasks: dict[str, dict[str, Any]] = {}
    failures: dict[str, str] = {}
    sampler = ResourceSampler()
    sampler.start()
    started = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=int(protocol["execution"]["maximum_parallel_tasks"])
        ) as executor:
            futures = {
                executor.submit(
                    run_one,
                    python=args.python,
                    project_root=project_root,
                    protocol=protocol,
                    unknown_family=unknown_family,
                    run_root=run_root,
                ): unknown_family
                for unknown_family in protocol["unknown_families"]
            }
            for future in concurrent.futures.as_completed(futures):
                unknown_family = futures[future]
                try:
                    completed_tasks[unknown_family] = future.result()
                except Exception as error:
                    failures[unknown_family] = f"{type(error).__name__}: {error}"
                progress: dict[str, Any] = {
                    "schema_version": "strict_v4_packet_sequence_fusion_progress_v1",
                    "state": "running",
                    "completed_families": sorted(completed_tasks),
                    "failed_families": failures,
                    "pending_families": sorted(
                        set(protocol["unknown_families"])
                        - set(completed_tasks)
                        - set(failures)
                    ),
                    "resource_samples": len(sampler.samples),
                    "updated_unix_seconds": time.time(),
                }
                progress["manifest_sha256"] = canonical_hash(progress)
                atomic_json(progress_path, progress)
    finally:
        sampler.stop()
    all_gpu_passed = (
        len(completed_tasks) == protocol["expected_task_count"] and not failures
    )
    completion: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_completion_v1",
        "state": "complete" if all_gpu_passed else "failed",
        "seed": protocol["development_seed"],
        "expected_task_count": protocol["expected_task_count"],
        "completed_task_count": len(completed_tasks),
        "failure_count": len(failures),
        "failures": failures,
        "task_artifacts": dict(sorted(completed_tasks.items())),
        "elapsed_seconds": time.time() - started,
        "gpu_execution": {
            "all_tasks_passed": all_gpu_passed,
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
            "formal_training_backend": "pytorch_cuda",
        },
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path = result_root / "completion.json"
    atomic_json(completion_path, completion)
    progress = {
        "schema_version": "strict_v4_packet_sequence_fusion_progress_v1",
        "state": completion["state"],
        "completed_families": sorted(completed_tasks),
        "failed_families": failures,
        "completion_path": str(completion_path),
        "completion_manifest_sha256": completion["manifest_sha256"],
        "updated_unix_seconds": time.time(),
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    atomic_json(progress_path, progress)
    return completion


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    completion = run(parse_arguments())
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))
    if completion["state"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

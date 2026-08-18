from __future__ import annotations

import argparse
import json
import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
    gpu_sample,
    summarize_samples,
)


REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "model.pt",
    "gpu_execution.json",
    "provenance.json",
)


def run_task(
    *,
    project_root: Path,
    python_executable: Path,
    protocol: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    output_dir = Path(task["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    training = protocol["training"]
    command = [
        str(python_executable),
        str(
            project_root
            / "train_strict_v4_benign_autoencoder_warning_task_cuda.py"
        ),
        "--pairwise-task-dir",
        task["anchor_dir"],
        "--cache-csv",
        task["cache_csv"],
        "--config",
        task["config"],
        "--output-dir",
        str(output_dir),
        "--required-gpu-uuid",
        training["required_gpu_uuid"],
        "--validation-benign-fpr-budget",
        str(training["validation_benign_fpr_budget"]),
        "--latent-dim",
        str(training["latent_dim"]),
        "--epochs",
        str(training["epochs"]),
        "--batch-size",
        str(training["batch_size"]),
        "--learning-rate",
        str(training["learning_rate"]),
        "--weight-decay",
        str(training["weight_decay"]),
        "--patience",
        str(training["patience"]),
        "--minimum-delta",
        str(training["minimum_delta"]),
        "--gpu-sample-interval-seconds",
        str(training["gpu_sample_interval_seconds"]),
    ]
    with (output_dir / "execution.log").open(
        "w", encoding="utf-8", newline="\n"
    ) as log_handle:
        result = subprocess.run(
            command,
            cwd=project_root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(f"trainer return code {result.returncode}")
    missing = [
        name
        for name in REQUIRED_ARTIFACTS
        if not (output_dir / name).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"missing autoencoder artifacts: {missing}")
    evidence = load_canonical(
        output_dir / "gpu_execution.json", "autoencoder GPU evidence"
    )
    if (
        evidence.get("passes") is not True
        or evidence.get("gpu_identity", {}).get("uuid")
        != training["required_gpu_uuid"]
        or evidence.get("model_parameter_device") != "cuda:0"
    ):
        raise ValueError("autoencoder task lacks valid CUDA evidence")
    return {
        "identity": task["identity"],
        "output_dir": str(output_dir),
        "artifact_sha256": {
            name: file_hash(output_dir / name)
            for name in REQUIRED_ARTIFACTS
        },
        "gpu_execution_manifest_sha256": evidence["manifest_sha256"],
        "peak_gpu_utilization_percent": float(
            evidence["peak_gpu_utilization_percent"]
        ),
        "peak_gpu_memory_mib": float(evidence["peak_gpu_memory_mib"]),
    }


def run_protocol(
    *,
    project_root: Path,
    protocol_path: Path,
    python_executable: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "autoencoder protocol")
    for name, expected_hash in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected_hash:
            raise ValueError(f"implementation hash mismatch: {name}")
    completion_path = Path(protocol["completion_path"])
    if completion_path.exists():
        raise ValueError(f"refusing to overwrite completion: {completion_path}")

    samples = [gpu_sample(protocol["training"]["required_gpu_uuid"])]
    failures = {}
    artifacts = {}
    started = time.time()
    with ThreadPoolExecutor(
        max_workers=int(protocol["training"]["parallel_tasks"])
    ) as executor:
        futures: dict[Future[dict[str, Any]], str] = {
            executor.submit(
                run_task,
                project_root=project_root,
                python_executable=python_executable.resolve(),
                protocol=protocol,
                task=task,
            ): identity
            for identity, task in protocol["tasks"].items()
        }
        pending = set(futures)
        interval = float(
            protocol["resource_contract"]["sample_interval_seconds"]
        )
        while pending:
            time.sleep(interval)
            try:
                samples.append(
                    gpu_sample(protocol["training"]["required_gpu_uuid"])
                )
            except (OSError, subprocess.SubprocessError, RuntimeError):
                pass
            done = {future for future in pending if future.done()}
            for future in done:
                identity = futures[future]
                try:
                    artifacts[identity] = future.result()
                except Exception as exc:
                    failures[identity] = f"{type(exc).__name__}: {exc}"
            pending -= done
    finished = time.time()
    expected = int(protocol["expected_task_count"])
    resource = summarize_samples(samples)
    minimum = float(
        protocol["resource_contract"][
            "minimum_mean_gpu_utilization_percent"
        ]
    )
    preferred = float(
        protocol["resource_contract"][
            "preferred_mean_gpu_utilization_percent"
        ]
    )
    resource["minimum_mean_utilization_passed"] = (
        resource["mean_gpu_utilization_percent"] >= minimum
    )
    resource["preferred_mean_utilization_met"] = (
        resource["mean_gpu_utilization_percent"] >= preferred
    )
    task_coverage_passed = len(artifacts) == expected and not failures
    execution_passed = (
        task_coverage_passed
        and resource["minimum_mean_utilization_passed"]
    )
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_benign_autoencoder_warning_development_completion_v1"
        ),
        "state": (
            "complete_gpu_development"
            if execution_passed
            else "complete_effect_resource_gate_failed"
            if task_coverage_passed
            else "failed"
        ),
        "execution_passed": execution_passed,
        "effect_execution_passed": task_coverage_passed,
        "started_at_unix": started,
        "finished_at_unix": finished,
        "duration_seconds": finished - started,
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "task_coverage": {
            "expected": expected,
            "complete": len(artifacts),
            "failed": len(failures),
            "passed": task_coverage_passed,
        },
        "task_artifacts": dict(sorted(artifacts.items())),
        "failures": dict(sorted(failures.items())),
        "resource_observed": resource,
        "claim_boundary": protocol["claim_boundary"],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path.parent.mkdir(parents=True, exist_ok=True)
    completion_path.write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    completion = run_protocol(
        project_root=args.project_root,
        protocol_path=args.protocol,
        python_executable=args.python,
    )
    print(
        json.dumps(
            {
                "effect_execution_passed": completion[
                    "effect_execution_passed"
                ],
                "execution_passed": completion["execution_passed"],
                "manifest_sha256": completion["manifest_sha256"],
                "resource_observed": completion["resource_observed"],
                "state": completion["state"],
                "task_coverage": completion["task_coverage"],
            },
            sort_keys=True,
        )
    )
    if not completion["effect_execution_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

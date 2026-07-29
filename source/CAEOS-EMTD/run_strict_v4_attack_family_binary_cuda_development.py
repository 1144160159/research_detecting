from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from evaluate_strict_v4_cicids2017_attack_family_gpu_hybrid import verify_chain
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


REQUIRED = (
    "metrics.json",
    "scores.npz",
    "model.ubj",
    "gpu_execution.json",
    "provenance.json",
)


def run_task(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    source_task: dict[str, Any],
    identity: str,
    output_root: Path,
) -> tuple[str, dict[str, Any]]:
    output_dir = output_root / identity
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {name: output_dir / name for name in REQUIRED}
    cache_path = (
        Path(protocol["paths"]["cache_root"])
        / (
            f"seed{source_task['seed']}_max"
            f"{protocol['cache_policy']['maximum_per_family']}.csv"
        )
    )
    parameters = protocol["xgboost_known_expert"]
    command = [
        str(python),
        str(
            project_root
            / "train_strict_v4_xgboost_binary_warning_task_cuda.py"
        ),
        "--pairwise-task-dir",
        source_task["pairwise_dir"],
        "--cache-csv",
        str(cache_path),
        "--config",
        protocol["source"]["config"],
        "--output-dir",
        str(output_dir),
        "--xgboost-root",
        parameters["package_root"],
        "--required-gpu-uuid",
        parameters["required_gpu_uuid"],
        "--validation-benign-fpr-budget",
        "0.04",
        "--estimators",
        str(parameters["estimators"]),
        "--max-depth",
        str(parameters["max_depth"]),
        "--learning-rate",
        str(parameters["learning_rate"]),
        "--subsample",
        str(parameters["subsample"]),
        "--colsample-bytree",
        str(parameters["colsample_bytree"]),
        "--early-stopping-rounds",
        str(parameters["early_stopping_rounds"]),
        "--jobs",
        str(parameters["jobs_per_task"]),
        "--gpu-sample-interval-seconds",
        str(parameters["gpu_sample_interval_seconds"]),
    ]
    if not all(path.is_file() for path in paths.values()):
        with (output_dir / "execution.log").open(
            "a", encoding="utf-8", newline="\n"
        ) as log:
            log.write("$ " + " ".join(command) + "\n")
            log.flush()
            subprocess.run(
                command,
                cwd=project_root,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{identity}: missing {missing}")
    evidence = load_canonical(
        paths["gpu_execution.json"], f"binary CUDA evidence {identity}"
    )
    if (
        not evidence.get("passes")
        or evidence.get("gpu_identity", {}).get("uuid")
        != parameters["required_gpu_uuid"]
        or not any(
            str(value).startswith("cuda")
            for value in evidence.get("booster_device_values", [])
        )
    ):
        raise ValueError(f"{identity}: invalid binary CUDA evidence")
    return identity, {
        "state": "complete",
        "output_dir": str(output_dir),
        "artifact_sha256": {
            name: file_hash(path) for name, path in paths.items()
        },
        "gpu_execution_manifest_sha256": evidence["manifest_sha256"],
        "peak_gpu_utilization_percent": evidence[
            "peak_gpu_utilization_percent"
        ],
        "peak_gpu_memory_mib": evidence["peak_gpu_memory_mib"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    completion_path = args.completion.resolve()
    protocol, completion = verify_chain(
        project_root, protocol_path, completion_path
    )
    if protocol["stage"] != "development":
        raise ValueError("binary CUDA exploration is development-only")
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    tasks: dict[str, Any] = {}
    failures: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(
                run_task,
                python=args.python.resolve(),
                project_root=project_root,
                protocol=protocol,
                source_task=task,
                identity=identity,
                output_root=output_root,
            ): identity
            for identity, task in completion["task_artifacts"].items()
        }
        for future in as_completed(futures):
            identity = futures[future]
            try:
                returned_identity, report = future.result()
                if returned_identity != identity:
                    raise ValueError("task identity mismatch")
                tasks[identity] = report
            except Exception as exc:
                failures[identity] = f"{type(exc).__name__}: {exc}"
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_binary_cuda_development_v1",
        "state": "failed" if failures else "complete",
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(tasks),
        "failure_count": len(failures),
        "failures": dict(sorted(failures.items())),
        "task_artifacts": dict(sorted(tasks.items())),
        "gpu_execution": {
            "all_tasks_passed": not failures
            and len(tasks) == protocol["expected_task_count"],
            "peak_gpu_utilization_percent": max(
                (
                    float(value["peak_gpu_utilization_percent"])
                    for value in tasks.values()
                ),
                default=0.0,
            ),
            "peak_gpu_memory_mib": max(
                (
                    float(value["peak_gpu_memory_mib"])
                    for value in tasks.values()
                ),
                default=0.0,
            ),
        },
        "binding": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "completion_manifest_sha256": completion["manifest_sha256"],
            "runner_sha256": file_hash(Path(__file__).resolve()),
            "trainer_sha256": file_hash(
                project_root
                / "train_strict_v4_xgboost_binary_warning_task_cuda.py"
            ),
        },
        "claim_boundary": {
            "development_seed_only": True,
            "fresh_confirmation_results_read": False,
            "not_a_confirmation_result": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    atomic_json(args.result.resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
    load_canonical,
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    body = dict(payload)
    body["manifest_sha256"] = canonical_hash(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def canonical_cuda_task_complete(task_dir: Path) -> bool:
    metrics_path = task_dir / "metrics.json"
    evidence_path = task_dir / "gpu_execution.json"
    if not metrics_path.is_file() or not evidence_path.is_file():
        return False
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    for payload in (metrics, evidence):
        declared = payload.get("manifest_sha256")
        body = dict(payload)
        body.pop("manifest_sha256", None)
        if not isinstance(declared, str) or canonical_hash(body) != declared:
            return False
    return bool(
        metrics.get("state") == "complete"
        and metrics.get("model", {}).get("device") == "cuda"
        and metrics.get("gpu_execution", {}).get("passes")
        and evidence.get("passes")
    )


def train_one(
    *,
    project_root: Path,
    protocol: dict[str, Any],
    python_executable: Path,
    scenario: str,
    seed: int,
) -> tuple[str, str]:
    identity = f"{scenario}_seed{seed}"
    output_dir = Path(protocol["xgboost_root"]) / identity
    if canonical_cuda_task_complete(output_dir):
        return identity, "reused_complete"
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"noncanonical task directory exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    training = protocol["training"]["xgboost_cuda"]
    command = [
        str(python_executable),
        str(project_root / "train_strict_v4_xgboost_warning_task_cuda.py"),
        "--pairwise-task-dir",
        str(Path(protocol["pairwise_root"]) / identity),
        "--cache-csv",
        str(
            Path(protocol["cache_root"])
            / f"seed{seed}_max5000.csv"
        ),
        "--config",
        protocol["config_path"],
        "--output-dir",
        str(output_dir),
        "--xgboost-root",
        training["package_root"],
        "--validation-benign-fpr-budget",
        str(training["validation_benign_fpr_budget"]),
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
        str(training["jobs_per_task"]),
    ]
    with (output_dir / "execution.log").open(
        "w", encoding="utf-8", newline="\n"
    ) as log_handle:
        log_handle.write("$ " + " ".join(command) + "\n")
        log_handle.flush()
        subprocess.run(
            command,
            cwd=project_root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            check=True,
        )
    if not canonical_cuda_task_complete(output_dir):
        raise ValueError(f"CUDA task evidence failed: {identity}")
    return identity, "trained"


def run_batch(
    project_root: Path,
    protocol_path: Path,
    python_executable: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol = load_canonical(protocol_path.resolve())
    result_root = Path(protocol["result_root"])
    progress_path = result_root / "xgboost_cuda_progress.json"
    started_at = datetime.now(timezone.utc).isoformat()
    task_states: dict[str, str] = {}
    failures: dict[str, str] = {}

    def write_progress(state: str) -> None:
        atomic_json(
            progress_path,
            {
                "schema_version": (
                    "strict_v4_xgboost_cuda_qualification_progress_v1"
                ),
                "state": state,
                "started_at_utc": started_at,
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "expected_task_count": protocol["expected_task_count"],
                "complete_task_count": len(task_states),
                "task_states": dict(sorted(task_states.items())),
                "failure_count": len(failures),
                "failures": dict(sorted(failures.items())),
            },
        )

    write_progress("running")
    workers = int(protocol["training"]["xgboost_cuda"]["parallel_tasks"])
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                train_one,
                project_root=project_root,
                protocol=protocol,
                python_executable=python_executable.resolve(),
                scenario=scenario,
                seed=int(seed),
            ): f"{scenario}_seed{seed}"
            for seed in protocol["seeds"]
            for scenario in protocol["scenarios"]
        }
        for future in as_completed(futures):
            identity = futures[future]
            try:
                _, task_state = future.result()
                task_states[identity] = task_state
            except Exception as exc:
                failures[identity] = f"{type(exc).__name__}: {exc}"
            write_progress("failed" if failures else "running")
    state = "complete" if not failures else "failed"
    write_progress(state)
    if failures:
        raise RuntimeError(f"{len(failures)} XGBoost CUDA tasks failed")
    return {
        "state": state,
        "complete_task_count": len(task_states),
        "expected_task_count": protocol["expected_task_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run_batch(args.project_root, args.protocol, args.python),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

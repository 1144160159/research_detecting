from __future__ import annotations

import argparse
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_strict_v4_xgboost_warning_matrix import verify_protocol


def canonical_task_complete(path: Path) -> bool:
    metrics_path = path / "metrics.json"
    if not metrics_path.is_file():
        return False
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("state") != "complete":
        return False
    from run_strict_v4_xgboost_warning_matrix import canonical_hash

    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    return isinstance(declared, str) and canonical_hash(body) == declared


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    from run_strict_v4_xgboost_warning_matrix import canonical_hash

    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def progress_payload(
    protocol: dict[str, Any],
    *,
    started_at: str,
    task_states: dict[str, str],
    failures: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": "strict_v4_xgboost_warning_parallel_progress_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_utc": started_at,
        "state": "failed" if failures else "running",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(task_states),
        "task_states": dict(sorted(task_states.items())),
        "failure_count": len(failures),
        "failures": dict(sorted(failures.items())),
    }


def train_one(
    *,
    project_root: Path,
    protocol: dict[str, Any],
    python: Path,
    scenario: str,
    seed: int,
) -> tuple[str, str]:
    identity = f"{scenario}_seed{seed}"
    pairwise_task = (
        project_root
        / protocol["pairwise_run_root"]
        / "cicids2017"
        / identity
    )
    output = (
        project_root / protocol["run_root"] / "cicids2017" / identity
    )
    if canonical_task_complete(output):
        return identity, "reused_complete"
    output.mkdir(parents=True, exist_ok=True)
    parameters = protocol["xgboost"]
    command = [
        str(python),
        str(project_root / "train_strict_v4_xgboost_warning_task.py"),
        "--pairwise-task-dir",
        str(pairwise_task),
        "--cache-csv",
        str(
            project_root
            / protocol["cache_root"]
            / f"seed{seed}_max5000.csv"
        ),
        "--config",
        str(protocol["config"]),
        "--output-dir",
        str(output),
        "--xgboost-root",
        str(parameters["package_root"]),
        "--validation-benign-fpr-budget",
        str(protocol["validation_benign_fpr_budget"]),
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
        str(parameters["jobs"]),
    ]
    with (output / "execution.log").open(
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
    if not canonical_task_complete(output):
        raise ValueError(f"non-canonical task output: {identity}")
    return identity, "trained"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = verify_protocol(project_root, protocol_path)
    if protocol.get("execution", {}).get("runner_file") != Path(__file__).name:
        raise ValueError("parallel runner is not bound by the protocol")
    pairwise_root = project_root / protocol["pairwise_run_root"] / "cicids2017"
    if len(list(pairwise_root.glob("*/metrics.json"))) != protocol[
        "expected_task_count"
    ]:
        raise ValueError("Pairwise fresh confirmation is not complete")
    result_root = project_root / protocol["result_root"]
    progress_path = result_root / "progress.json"
    started_at = datetime.now(timezone.utc).isoformat()
    task_states: dict[str, str] = {}
    failures: dict[str, str] = {}
    atomic_write(
        progress_path,
        progress_payload(
            protocol,
            started_at=started_at,
            task_states=task_states,
            failures=failures,
        ),
    )
    with ThreadPoolExecutor(
        max_workers=int(protocol["xgboost"]["parallel_tasks"])
    ) as executor:
        futures = {
            executor.submit(
                train_one,
                project_root=project_root,
                protocol=protocol,
                python=args.python.resolve(),
                scenario=scenario,
                seed=int(seed),
            ): f"{scenario}_seed{seed}"
            for seed in protocol["seeds"]
            for scenario in protocol["scenarios"]
        }
        for future in as_completed(futures):
            identity = futures[future]
            try:
                _, state = future.result()
                task_states[identity] = state
            except Exception as exc:
                failures[identity] = f"{type(exc).__name__}: {exc}"
            atomic_write(
                progress_path,
                progress_payload(
                    protocol,
                    started_at=started_at,
                    task_states=task_states,
                    failures=failures,
                ),
            )
    if failures:
        raise RuntimeError(f"{len(failures)} XGBoost tasks failed")
    result_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(args.python.resolve()),
            str(project_root / "summarize_strict_v4_xgboost_warning.py"),
            "--project-root",
            str(project_root),
            "--protocol",
            str(protocol_path),
            "--output",
            str(result_root / "summary.json"),
        ],
        cwd=project_root,
        check=True,
    )
    final_progress = progress_payload(
        protocol,
        started_at=started_at,
        task_states=task_states,
        failures=failures,
    )
    final_progress["state"] = "complete"
    atomic_write(progress_path, final_progress)


if __name__ == "__main__":
    main()

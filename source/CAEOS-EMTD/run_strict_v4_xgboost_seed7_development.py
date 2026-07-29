from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], label: str) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def verify_protocol(project_root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = load(protocol_path)
    verify_canonical(protocol, "development protocol")
    for relative, expected in protocol["implementation_sha256"].items():
        path = project_root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"implementation hash drifted: {relative}")
    if file_hash(project_root / protocol["cache_csv"]) != protocol["source_sha256"][
        "cache_csv"
    ]:
        raise ValueError("cache hash drifted")
    if file_hash(project_root / protocol["config"]) != protocol["source_sha256"][
        "config"
    ]:
        raise ValueError("config hash drifted")
    pairwise_root = project_root / protocol["pairwise_run_root"]
    for scenario, expected_artifacts in protocol["source_sha256"][
        "pairwise_tasks"
    ].items():
        task_dir = pairwise_root / f"{scenario}_seed{protocol['seed']}"
        for name, expected in expected_artifacts.items():
            path = task_dir / name
            if not path.is_file() or file_hash(path) != expected:
                raise ValueError(f"pairwise source hash drifted: {scenario}/{name}")
    return protocol


def existing_task_is_valid(path: Path) -> bool:
    metrics = path / "metrics.json"
    if not metrics.is_file():
        return False
    payload = load(metrics)
    try:
        verify_canonical(payload, str(metrics))
    except ValueError:
        return False
    return payload.get("state") == "complete"


def train_one(
    *,
    project_root: Path,
    python: Path,
    protocol: dict[str, Any],
    scenario: str,
) -> tuple[str, str]:
    seed = int(protocol["seed"])
    output = project_root / protocol["run_root"] / "cicids2017" / (
        f"{scenario}_seed{seed}"
    )
    if existing_task_is_valid(output):
        return scenario, "reused_complete"
    output.mkdir(parents=True, exist_ok=True)
    pairwise_task = (
        project_root
        / protocol["pairwise_run_root"]
        / f"{scenario}_seed{seed}"
    )
    parameters = protocol["xgboost"]
    command = [
        str(python),
        str(project_root / "train_strict_v4_xgboost_warning_task.py"),
        "--pairwise-task-dir",
        str(pairwise_task),
        "--cache-csv",
        str(project_root / protocol["cache_csv"]),
        "--config",
        str(project_root / protocol["config"]),
        "--output-dir",
        str(output),
        "--xgboost-root",
        str(parameters["package_root"]),
        "--validation-benign-fpr-budget",
        str(protocol["threshold_development"]["training_budget"]),
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
    if not existing_task_is_valid(output):
        raise ValueError(f"task did not produce canonical metrics: {scenario}")
    return scenario, "trained"


def progress_payload(
    protocol: dict[str, Any],
    *,
    started_at: str,
    states: dict[str, str],
    failures: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": "strict_v4_xgboost_seed7_development_progress_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_utc": started_at,
        "state": "failed" if failures else "running",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(states),
        "task_states": dict(sorted(states.items())),
        "failure_count": len(failures),
        "failures": dict(sorted(failures.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = verify_protocol(project_root, protocol_path)
    result_root = project_root / protocol["result_root"]
    progress_path = result_root / "progress.json"
    started_at = datetime.now(timezone.utc).isoformat()
    states: dict[str, str] = {}
    failures: dict[str, str] = {}
    atomic_write(
        progress_path,
        progress_payload(
            protocol, started_at=started_at, states=states, failures=failures
        ),
    )
    with ThreadPoolExecutor(
        max_workers=int(protocol["xgboost"]["parallel_tasks"])
    ) as executor:
        futures = {
            executor.submit(
                train_one,
                project_root=project_root,
                python=args.python.resolve(),
                protocol=protocol,
                scenario=scenario,
            ): scenario
            for scenario in protocol["scenarios"]
        }
        for future in as_completed(futures):
            scenario = futures[future]
            try:
                _, state = future.result()
                states[scenario] = state
            except Exception as exc:
                failures[scenario] = f"{type(exc).__name__}: {exc}"
            atomic_write(
                progress_path,
                progress_payload(
                    protocol,
                    started_at=started_at,
                    states=states,
                    failures=failures,
                ),
            )
    if failures:
        raise RuntimeError(f"{len(failures)} development tasks failed")
    subprocess.run(
        [
            str(args.python.resolve()),
            str(project_root / "summarize_strict_v4_xgboost_seed7_development.py"),
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
        protocol, started_at=started_at, states=states, failures=failures
    )
    final_progress["state"] = "complete"
    final_progress["summary_sha256"] = file_hash(result_root / "summary.json")
    atomic_write(progress_path, final_progress)


if __name__ == "__main__":
    main()

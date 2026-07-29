from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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


def verify_protocol(project_root: Path, path: Path) -> dict[str, Any]:
    protocol = load(path)
    declared = protocol.get("manifest_sha256")
    body = dict(protocol)
    body.pop("manifest_sha256", None)
    if canonical_hash(body) != declared:
        raise ValueError("XGBoost protocol canonical mismatch")
    for relative, expected in protocol["implementation_sha256"].items():
        implementation = project_root / relative
        if not implementation.is_file() or file_hash(implementation) != expected:
            raise ValueError(f"implementation hash drifted: {relative}")
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol = verify_protocol(project_root, args.protocol.resolve())
    pairwise_root = project_root / protocol["pairwise_run_root"] / "cicids2017"
    if len(list(pairwise_root.glob("*/metrics.json"))) != protocol[
        "expected_task_count"
    ]:
        raise ValueError("Pairwise fresh confirmation is not complete")
    run_root = project_root / protocol["run_root"] / "cicids2017"
    run_root.mkdir(parents=True, exist_ok=True)
    parameters = protocol["xgboost"]
    for seed in protocol["seeds"]:
        cache = (
            project_root
            / protocol["cache_root"]
            / f"seed{seed}_max5000.csv"
        )
        for scenario in protocol["scenarios"]:
            pairwise_task = pairwise_root / f"{scenario}_seed{seed}"
            output = run_root / f"{scenario}_seed{seed}"
            if (output / "metrics.json").is_file():
                continue
            command = [
                str(args.python),
                str(project_root / "train_strict_v4_xgboost_warning_task.py"),
                "--pairwise-task-dir",
                str(pairwise_task),
                "--cache-csv",
                str(cache),
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
            subprocess.run(command, cwd=project_root, check=True)
    result_root = project_root / protocol["result_root"]
    result_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(args.python),
            str(project_root / "summarize_strict_v4_xgboost_warning.py"),
            "--project-root",
            str(project_root),
            "--protocol",
            str(args.protocol.resolve()),
            "--output",
            str(result_root / "summary.json"),
        ],
        cwd=project_root,
        check=True,
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


IMPLEMENTATION_FILES = (
    "train_strict_v4_xgboost_warning_task.py",
    "run_strict_v4_xgboost_warning_matrix.py",
    "summarize_strict_v4_xgboost_warning.py",
)


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


def verify_canonical(payload: dict[str, Any]) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError("parent execution protocol canonical mismatch")


def create_protocol(
    *,
    project_root: Path,
    parent_protocol_path: Path,
    xgboost_root: Path,
    xgboost_version: str,
    run_root: Path,
    result_root: Path,
    runner_file: str = "run_strict_v4_xgboost_warning_matrix.py",
    parallel_tasks: int = 1,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    parent = load(parent_protocol_path)
    verify_canonical(parent)
    if (
        parent.get("schema_version")
        != "strict_v4_core_warning_execution_protocol_v1"
        or parent.get("status")
        != "frozen_zero_result_before_fresh_confirmation"
    ):
        raise ValueError("invalid parent core confirmation protocol")
    if run_root.exists() and any(run_root.rglob("metrics.json")):
        raise ValueError("XGBoost formal results must be zero at freeze")
    if (result_root / "summary.json").exists():
        raise ValueError("XGBoost summary must be zero at freeze")
    if parallel_tasks <= 0:
        raise ValueError("parallel_tasks must be positive")
    implementation_files = (
        "train_strict_v4_xgboost_warning_task.py",
        runner_file,
        "summarize_strict_v4_xgboost_warning.py",
    )
    implementation_sha256 = {}
    for relative in implementation_files:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation_sha256[relative] = file_hash(path)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_warning_protocol_v1",
        "status": "frozen_zero_result_waiting_for_pairwise_confirmation",
        "parent_protocol": {
            "path": parent_protocol_path.resolve().relative_to(
                project_root
            ).as_posix(),
            "file_sha256": file_hash(parent_protocol_path),
            "manifest_sha256": parent["manifest_sha256"],
        },
        "suite": "cicids2017",
        "seeds": parent["seeds"],
        "scenarios": parent["scenarios"],
        "expected_task_count": parent["expected_task_count"],
        "pairwise_run_root": parent["execution"]["run_root"],
        "cache_root": parent["data"]["cache_root"],
        "config": parent["data"]["config"],
        "validation_benign_fpr_budget": parent["development_selection"][
            "selected_validation_benign_fpr_budget"
        ],
        "run_root": run_root.resolve().relative_to(project_root).as_posix(),
        "result_root": result_root.resolve().relative_to(project_root).as_posix(),
        "xgboost": {
            "package_root": str(xgboost_root.resolve()),
            "version": xgboost_version,
            "estimators": 1000,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "early_stopping_rounds": 30,
            "jobs": 8,
            "parallel_tasks": parallel_tasks,
            "tree_method": "hist",
            "class_weighting": "balanced_training_sample_weight",
            "iteration_selection": "known_validation_mlogloss_only",
        },
        "baseline_role": {
            "warning_and_known_type_anchor": True,
            "unknown_label_capability": False,
            "eligible_for_basic_warning_gate": True,
            "eligible_for_full_open_set_gate": False,
        },
        "anti_leakage": {
            "same_pairwise_split_arrays_required": True,
            "threshold_uses_validation_benign_only": True,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "no_result_dependent_hyperparameter_search": True,
        },
        "claim_boundary": {
            "xgboost_is_not_an_open_set_baseline": True,
            "xgboost_basic_gate_pass_does_not_prove_unknown_labeling": True,
            "comparison_is_first_stage_and_known_type_only": True,
        },
        "implementation_sha256": implementation_sha256,
        "execution": {
            "runner_file": runner_file,
            "parallel_tasks": parallel_tasks,
            "declared_cpu_slots": parallel_tasks * 8,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--xgboost-version", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument(
        "--runner-file",
        default="run_strict_v4_xgboost_warning_matrix.py",
    )
    parser.add_argument("--parallel-tasks", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        project_root=args.project_root,
        parent_protocol_path=args.parent_protocol,
        xgboost_root=args.xgboost_root,
        xgboost_version=str(args.xgboost_version),
        run_root=args.run_root,
        result_root=args.result_root,
        runner_file=str(args.runner_file),
        parallel_tasks=int(args.parallel_tasks),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()

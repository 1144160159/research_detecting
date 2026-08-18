from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    canonical_hash,
    file_hash,
    load_canonical,
)


def canonical_cuda_task(task_dir: Path) -> dict[str, str]:
    paths = {
        "metrics": task_dir / "metrics.json",
        "scores": task_dir / "scores.npz",
        "gpu_execution": task_dir / "gpu_execution.json",
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    evidence = load_canonical(paths["gpu_execution"], "XGBoost GPU evidence")
    metrics = load_canonical(paths["metrics"], "XGBoost metrics")
    if not (
        evidence.get("passes")
        and metrics.get("gpu_execution", {}).get("passes")
        and metrics.get("model", {}).get("device") == "cuda"
    ):
        raise ValueError(f"XGBoost CUDA task did not pass: {task_dir}")
    return {name: file_hash(path) for name, path in paths.items()}


def build_recovery_protocol(
    *,
    project_root: Path,
    parent_protocol_path: Path,
    failed_completion_path: Path,
    source_csv: Path,
    neural_cache_dir: Path,
    previous_recovery_launch_path: Path | None,
    output: Path,
    neural_output_root: Path | None = None,
    scheduling_workers: int | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    parent_protocol_path = parent_protocol_path.resolve()
    failed_completion_path = failed_completion_path.resolve()
    source_csv = source_csv.resolve()
    neural_cache_dir = neural_cache_dir.resolve()
    output = output.resolve()
    parent = load_canonical(parent_protocol_path, "parent protocol")
    failed = load_canonical(failed_completion_path, "failed completion")
    if scheduling_workers is None:
        scheduling_workers = int(parent["training"]["neural"]["workers"])
    if scheduling_workers < 1:
        raise ValueError("scheduling workers must be positive")
    if neural_output_root is None:
        neural_output_root = Path(parent["matrix_output_root"])
    neural_output_root = neural_output_root.resolve()
    if failed.get("execution_passed") is not False:
        raise ValueError("recovery requires a failed parent completion")
    if failed.get("return_codes", {}).get("neural_matrix") == 0:
        raise ValueError("parent neural matrix was not the failed component")
    if failed.get("return_codes", {}).get("xgboost_cuda_batch") != 0:
        raise ValueError("parent XGBoost CUDA batch did not complete")
    if (
        failed.get("protocol", {}).get("manifest_sha256")
        != parent["manifest_sha256"]
    ):
        raise ValueError("failed completion is not bound to parent protocol")
    if not source_csv.is_file():
        raise FileNotFoundError(source_csv)
    neural_root = Path(parent["neural_root"])
    if any(neural_root.rglob("metrics.json")):
        raise ValueError("neural effect result must remain zero at recovery freeze")
    if neural_output_root.exists() and any(neural_output_root.iterdir()):
        raise ValueError("recovery neural output root must be new or empty")
    previous_recovery_failure = None
    if previous_recovery_launch_path is not None:
        previous_recovery_launch_path = previous_recovery_launch_path.resolve()
        previous = json.loads(
            previous_recovery_launch_path.read_text(encoding="utf-8")
        )
        if not isinstance(previous, dict) or previous.get("state") != "completed":
            raise ValueError("previous recovery launch is not a failed run")
        return_code = int(previous.get("return_code", 0))
        completion_evidence = None
        failure_class = "cache_directory_must_contain_seed_caches"
        if return_code == 0:
            completion_path = Path(previous.get("completion_path", ""))
            completion = load_canonical(
                completion_path, "previous recovery completion"
            )
            resource = completion.get("resource_observed", {})
            if (
                completion.get("execution_passed") is not False
                or resource.get("minimum_mean_utilization_passed") is not False
            ):
                raise ValueError("previous recovery did not fail resource gate")
            completion_evidence = {
                "path": str(completion_path),
                "file_sha256": file_hash(completion_path),
                "manifest_sha256": completion["manifest_sha256"],
            }
            failure_class = "gpu_resource_utilization_below_minimum"
        previous_recovery_failure = {
            "path": str(previous_recovery_launch_path),
            "file_sha256": file_hash(previous_recovery_launch_path),
            "return_code": return_code,
            "failure_class": failure_class,
            "completion": completion_evidence,
        }

    xgboost_sha256 = {}
    xgboost_root = Path(parent["xgboost_root"])
    for seed in parent["seeds"]:
        seed_hashes = {}
        for scenario in parent["scenarios"]:
            seed_hashes[scenario] = canonical_cuda_task(
                xgboost_root / f"{scenario}_seed{seed}"
            )
        xgboost_sha256[str(seed)] = seed_hashes

    implementation_names = (
        "run_neural_baseline_matrix.py",
        "train_neural_open_set.py",
        "run_strict_v4_neural_empirical_tail_hybrid_recovery.py",
    )
    recovery_suffix = output.stem.removeprefix("recovery_protocol")
    recovery_completion_name = f"completion_recovery{recovery_suffix}.json"
    recovery: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_recovery_protocol_v1"
        ),
        "state": "frozen_infrastructure_recovery_before_neural_effect",
        "parent_protocol": {
            "path": str(parent_protocol_path),
            "file_sha256": file_hash(parent_protocol_path),
            "manifest_sha256": parent["manifest_sha256"],
        },
        "failed_completion": {
            "path": str(failed_completion_path),
            "file_sha256": file_hash(failed_completion_path),
            "manifest_sha256": failed["manifest_sha256"],
            "failure_class": "relative_source_csv_missing_from_release",
            "neural_return_code": failed["return_codes"]["neural_matrix"],
            "xgboost_return_code": failed["return_codes"][
                "xgboost_cuda_batch"
            ],
        },
        "previous_recovery_failure": previous_recovery_failure,
        "repair": {
            "source_csv": str(source_csv),
            "source_csv_sha256": file_hash(source_csv),
            "neural_cache_dir": str(neural_cache_dir),
            "neural_output_root": str(neural_output_root),
            "scheduling_workers": scheduling_workers,
            "effect_configuration_changed": False,
            "training_semantics_changed": False,
            "seeds_changed": False,
            "scenarios_changed": False,
            "thresholds_changed": False,
            "split_policy_changed": False,
        },
        "xgboost_cuda_reuse": {
            "task_count": parent["expected_task_count"],
            "source_sha256": xgboost_sha256,
            "effect_metrics_read_for_recovery_decision": False,
        },
        "fresh_neural_result_count_at_freeze": 0,
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in implementation_names
        },
        "resource_contract": parent["resource_contract"],
        "recovery_completion_path": str(
            output.parent / recovery_completion_name
        ),
        "claim_boundary": {
            "infrastructure_recovery_is_not_effect_selection": True,
            "xgboost_effect_values_were_not_used_to_change_candidate": True,
            "recovery_preserves_failed_attempt_logs": True,
            "three_seed_qualification_is_not_formal_confirmation": True,
            "scheduling_concurrency_is_not_effect_selection": True,
        },
    }
    recovery["manifest_sha256"] = canonical_hash(recovery)
    return recovery


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--failed-completion", type=Path, required=True)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--neural-cache-dir", type=Path, required=True)
    parser.add_argument("--neural-output-root", type=Path)
    parser.add_argument("--scheduling-workers", type=int)
    parser.add_argument("--previous-recovery-launch", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    recovery = build_recovery_protocol(
        project_root=args.project_root,
        parent_protocol_path=args.parent_protocol,
        failed_completion_path=args.failed_completion,
        source_csv=args.source_csv,
        neural_cache_dir=args.neural_cache_dir,
        previous_recovery_launch_path=args.previous_recovery_launch,
        output=args.output,
        neural_output_root=args.neural_output_root,
        scheduling_workers=args.scheduling_workers,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(recovery, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": recovery["manifest_sha256"],
                "output": str(args.output.resolve()),
                "state": recovery["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

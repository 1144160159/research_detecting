from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCENARIOS = [
    "bot",
    "ddos",
    "dos_goldeneye",
    "dos_hulk",
    "dos_slowhttptest",
    "dos_slowloris",
    "ftp_patator",
    "heartbleed",
    "infiltration",
    "portscan",
    "ssh_patator",
    "web_bruteforce",
    "web_sql_injection",
    "web_xss",
]
REQUIRED_PAIRWISE_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


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


def build_protocol(project_root: Path) -> dict[str, Any]:
    pairwise_root = (
        project_root
        / "runs/strict_v4_full103_pairwise_caeos_seed7/cicids2017"
    )
    task_sources: dict[str, dict[str, str]] = {}
    for scenario in SCENARIOS:
        task_dir = pairwise_root / f"{scenario}_seed7"
        artifacts: dict[str, str] = {}
        for artifact in REQUIRED_PAIRWISE_ARTIFACTS:
            path = task_dir / artifact
            if not path.is_file():
                raise FileNotFoundError(path)
            artifacts[artifact] = file_hash(path)
        task_sources[scenario] = artifacts

    implementation_names = [
        "create_strict_v4_xgboost_seed7_development_protocol.py",
        "run_strict_v4_xgboost_seed7_development.py",
        "summarize_strict_v4_xgboost_seed7_development.py",
        "train_strict_v4_xgboost_warning_task.py",
    ]
    implementation_sha256 = {}
    for name in implementation_names:
        path = project_root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation_sha256[name] = file_hash(path)

    cache = Path(
        "/opt/data/private/wangwt/ParkAttackKE/"
        "CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/"
        "cicids2017/stratified/seed7_max5000.csv"
    )
    config = project_root / "configs/cicids2017_strict.json"
    if not cache.is_file():
        raise FileNotFoundError(cache)
    if not config.is_file():
        raise FileNotFoundError(config)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_seed7_development_protocol_v1",
        "state": "frozen_zero_result_development_only",
        "purpose": (
            "Use a completed hash-bound seed7 split to identify a defensible "
            "benign-FPR budget interval while filling otherwise idle CPU capacity."
        ),
        "suite": "cicids2017",
        "seed": 7,
        "scenarios": SCENARIOS,
        "expected_task_count": len(SCENARIOS),
        "pairwise_run_root": str(pairwise_root.relative_to(project_root)),
        "run_root": "runs/strict_v4_xgboost_seed7_development_v1",
        "result_root": "results/strict_v4_xgboost_seed7_development_v1",
        "cache_csv": str(cache),
        "config": str(config.relative_to(project_root)),
        "source_sha256": {
            "cache_csv": file_hash(cache),
            "config": file_hash(config),
            "pairwise_tasks": task_sources,
        },
        "implementation_sha256": implementation_sha256,
        "xgboost": {
            "version": "2.1.4",
            "package_root": "/opt/data/private/wangwt/python_packages/xgboost-2.1.4",
            "estimators": 1000,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "early_stopping_rounds": 30,
            "jobs_per_task": 8,
            "parallel_tasks": 8,
            "tree_method": "hist",
            "class_weighting": "balanced_training_sample_weight",
        },
        "threshold_development": {
            "validation_benign_fpr_budgets": [0.01, 0.025, 0.04],
            "training_budget": 0.04,
            "threshold_source": "known_validation_benign_only",
            "test_or_unknown_labels_used_for_selection": False,
        },
        "resource_policy": {
            "logical_cpu_count": 80,
            "memory_gib": 512,
            "gpu_memory_gib": 49,
            "minimum_total_cpu_busy_fraction": 0.5,
            "preferred_total_cpu_busy_fraction": 0.8,
            "declared_xgboost_cpu_slots": 64,
            "runs_concurrently_with_core_confirmation_v2": True,
        },
        "execution": {
            "runner_file": "run_strict_v4_xgboost_seed7_development.py",
            "parallel_tasks": 8,
            "declared_cpu_slots": 64,
        },
        "claim_boundary": {
            "development_seed_only": True,
            "may_select_validation_benign_fpr_budget_for_fresh_confirmation": True,
            "may_replace_fresh_three_seed_confirmation": False,
            "may_prove_unknown_attack_labeling": False,
            "may_prove_sota": False,
            "results_must_not_select_the_self_algorithm": True,
        },
        "formal_output_counts_at_freeze": {
            "metrics": 0,
            "summary": 0,
            "completion": 0,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol = build_protocol(project_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

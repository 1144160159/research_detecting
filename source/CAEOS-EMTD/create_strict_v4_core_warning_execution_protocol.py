from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SEEDS = (907, 911, 919)
SCENARIOS = (
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
)
DEVELOPMENT_BUDGETS = (0.01, 0.025, 0.04)
SELECTED_BUDGET = 0.04
IMPLEMENTATION_FILES = (
    "prepare_stratified_cache.py",
    "run_nested_gate_matrix.py",
    "evaluate_strict_v4_benign_calibrated_warning.py",
    "audit_strict_v4_core_warning_confirmation.py",
    "snapshot_strict_v4_core_warning_progress.py",
    "run_strict_v4_core_warning_confirmation.py",
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


def verify_canonical(payload: dict[str, Any], path: Path) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"canonical manifest mismatch: {path}")


def _relative(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def create_protocol(
    *,
    project_root: Path,
    core_protocol_path: Path,
    candidate_manifest_path: Path,
    source_csv_path: Path,
    config_path: Path,
    development_evidence_paths: list[Path],
    run_root: Path,
    result_root: Path,
    cache_root: Path,
    workers: int = 1,
    model_jobs: int = 8,
    estimators: int = 80,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    core = load(core_protocol_path)
    verify_canonical(core, core_protocol_path)
    if (
        core.get("schema_version") != "strict_v4_core_warning_protocol_v1"
        or core.get("status") != "frozen_before_fresh_seed_confirmation"
        or core.get("core_confirmation", {}).get("fresh_seeds") != list(SEEDS)
        or core.get("core_confirmation", {}).get("datasets") != ["cicids2017"]
    ):
        raise ValueError("core warning protocol boundary drifted")

    candidate = load(candidate_manifest_path)
    candidate_values = candidate.get("candidate")
    required_candidate = {
        "maximum_alpha",
        "minimum_fold_gain",
        "hard_pseudo_fraction",
        "interpolation",
        "max_per_task",
        "training_objective",
    }
    if not isinstance(candidate_values, dict) or not required_candidate.issubset(
        candidate_values
    ):
        raise ValueError("pairwise candidate manifest is incomplete")

    if len(development_evidence_paths) != len(DEVELOPMENT_BUDGETS):
        raise ValueError("exactly three development sensitivity files are required")
    development_evidence = []
    observed_budgets = []
    for path in development_evidence_paths:
        payload = load(path)
        verify_canonical(payload, path)
        budget = float(payload.get("validation_benign_fpr_budget", -1.0))
        observed_budgets.append(budget)
        if (
            payload.get("alert_mode") != "hierarchical_probability"
            or payload.get("suites") != ["cicids2017"]
            or payload.get("scenario_count") != len(SCENARIOS)
            or payload.get("observed_seeds", [7]) != [7]
        ):
            raise ValueError(f"invalid seed7 development evidence: {path}")
        development_evidence.append(
            {
                "path": _relative(project_root, path),
                "file_sha256": file_hash(path),
                "manifest_sha256": payload["manifest_sha256"],
                "validation_benign_fpr_budget": budget,
                "suite_equal_mean": payload["suite_equal_mean"],
                "aggregate_gates": payload["aggregate_gates"],
            }
        )
    if sorted(observed_budgets) != list(DEVELOPMENT_BUDGETS):
        raise ValueError("development sensitivity budget set drifted")

    for path in (source_csv_path, config_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    implementation_sha256 = {}
    for relative in IMPLEMENTATION_FILES:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation_sha256[relative] = file_hash(path)

    if run_root.exists() and any(run_root.rglob("metrics.json")):
        raise ValueError("formal run root already contains metrics")
    forbidden_results = (
        result_root / "evaluation.json",
        result_root / "audit.json",
        result_root / "completion.json",
    )
    if any(path.exists() for path in forbidden_results):
        raise ValueError("formal result files must be zero before freezing")
    if workers < 1 or model_jobs < 1 or estimators < 1:
        raise ValueError("execution resource values must be positive")

    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_execution_protocol_v1",
        "status": "frozen_zero_result_before_fresh_confirmation",
        "parent_protocol": {
            "path": _relative(project_root, core_protocol_path),
            "file_sha256": file_hash(core_protocol_path),
            "manifest_sha256": core["manifest_sha256"],
        },
        "suite": "cicids2017",
        "scenarios": list(SCENARIOS),
        "scenario_count_per_seed": len(SCENARIOS),
        "seeds": list(SEEDS),
        "expected_task_count": len(SEEDS) * len(SCENARIOS),
        "development_selection": {
            "development_seed": 7,
            "sensitivity_evidence": development_evidence,
            "selected_validation_benign_fpr_budget": SELECTED_BUDGET,
            "selection_rule": (
                "use the largest predeclared validation-benign budget below "
                "five percent to maximize attack recall; freeze before fresh seeds"
            ),
            "seed7_is_development_only": True,
            "fresh_seed_results_used_for_budget_selection": False,
        },
        "data": {
            "source_csv": str(source_csv_path.resolve()),
            "source_csv_size_bytes": source_csv_path.stat().st_size,
            "source_csv_sha256": file_hash(source_csv_path),
            "config": str(config_path.resolve()),
            "config_sha256": file_hash(config_path),
            "cache_root": _relative(project_root, cache_root),
            "cache_max_per_class": 5000,
            "cache_seed_specific": True,
            "split_rule": "capture_grouped",
        },
        "algorithm": {
            "name": "hierarchical_pairwise",
            "risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
            "risk_policy_name": "strict_v4_core_warning_pairwise_fresh_v1",
            "pairwise_candidate_manifest": {
                "path": _relative(project_root, candidate_manifest_path),
                "file_sha256": file_hash(candidate_manifest_path),
            },
            "candidate": {
                key: candidate_values[key] for key in sorted(required_candidate)
            },
            "alert_mode": "hierarchical_probability",
        },
        "execution": {
            "run_root": _relative(project_root, run_root),
            "result_root": _relative(project_root, result_root),
            "workers": workers,
            "model_jobs": model_jobs,
            "estimators": estimators,
            "resource_policy": {
                "logical_cpu_count": 80,
                "memory_gib": 512,
                "gpu_memory_gib": 49,
                "minimum_target_cpu_utilization_fraction": 0.50,
                "preferred_cpu_utilization_fraction": 0.80,
                "declared_parallel_job_slots": workers * model_jobs,
                "runtime_utilization_must_be_observed_not_inferred": True,
            },
            "thread_limits": {
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
            },
            "resume_completed_tasks": True,
        },
        "acceptance": {
            "all_three_fresh_seeds_must_pass_basic_warning_gate": True,
            "per_seed_scenario_count": len(SCENARIOS),
            "alert_accuracy_min": 0.95,
            "alert_precision_min": 0.95,
            "attack_recall_min": 0.95,
            "known_attack_type_accuracy_min": 0.95,
            "benign_fpr_strict_max": 0.05,
            "unknown_attack_alert_recall_min_for_full_gate": 0.95,
            "unknown_label_recall_min_for_full_gate": 0.95,
        },
        "anti_leakage": {
            "threshold_uses_validation_benign_only": True,
            "unknown_or_test_labels_used_for_threshold": False,
            "fresh_seed_test_metrics_used_for_selection": False,
            "all_failed_or_partial_tasks_remain_reportable": True,
        },
        "claim_boundary": {
            "basic_gate_pass_does_not_prove_full_open_set_gate": True,
            "single_suite_does_not_prove_cross_dataset_generalization": True,
            "single_suite_does_not_prove_comprehensive_sota": True,
            "confirmation_requires_independent_recomputation_audit": True,
        },
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--core-protocol", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--development-evidence", type=Path, action="append", required=True
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--model-jobs", type=int, default=8)
    parser.add_argument("--estimators", type=int, default=80)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        project_root=args.project_root,
        core_protocol_path=args.core_protocol,
        candidate_manifest_path=args.candidate_manifest,
        source_csv_path=args.source_csv,
        config_path=args.config,
        development_evidence_paths=args.development_evidence,
        run_root=args.run_root,
        result_root=args.result_root,
        cache_root=args.cache_root,
        workers=args.workers,
        model_jobs=args.model_jobs,
        estimators=args.estimators,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()

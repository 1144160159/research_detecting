from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    FAMILY_SCENARIOS,
    FINE_TO_FAMILY,
    canonical_hash,
    file_hash,
    load_canonical,
)


STAGE_SEEDS = {
    "development": (7,),
    "confirmation": (929, 937, 941),
}


def build_protocol(
    *,
    project_root: Path,
    stage: str,
    source_csv: Path,
    config_path: Path,
    cache_root: Path,
    run_root: Path,
    result_root: Path,
    development_result_path: Path | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    source_csv = source_csv.resolve()
    config_path = config_path.resolve()
    cache_root = cache_root.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    if stage not in STAGE_SEEDS:
        raise ValueError(f"unsupported stage: {stage}")
    if not source_csv.is_file() or not config_path.is_file():
        raise FileNotFoundError("source CSV and config are required")
    formal_names = ("completion.json", "development.json", "confirmation.json")
    existing_formal = [
        name for name in formal_names if (result_root / name).is_file()
    ]
    if existing_formal:
        raise ValueError(f"formal outputs must be zero at freeze: {existing_formal}")
    selected_configuration = None
    selection_source = None
    if stage == "confirmation":
        if development_result_path is None:
            raise ValueError("confirmation requires a development result")
        development_result_path = development_result_path.resolve()
        development = load_canonical(
            development_result_path, "attack-family development result"
        )
        if (
            development.get("state")
            != "complete_seed7_attack_family_development"
            or development.get("claim_boundary", {}).get("authorized_level")
            != "attack_family"
        ):
            raise ValueError("invalid attack-family development result")
        selected_configuration = development["selected"]["configuration"]
        selection_source = {
            "development_result_path": str(development_result_path),
            "development_result_file_sha256": file_hash(development_result_path),
            "development_result_manifest_sha256": development["manifest_sha256"],
            "selection_seed": 7,
        }
    implementations = (
        "strict_v4_cicids2017_attack_family.py",
        "create_strict_v4_cicids2017_attack_family_protocol.py",
        "run_strict_v4_cicids2017_attack_family_matrix.py",
        "launch_strict_v4_cicids2017_attack_family_matrix.py",
        "evaluate_strict_v4_cicids2017_attack_family_hybrid.py",
        "evaluate_strict_v4_hybrid_self_algorithm_development.py",
        "train_hybrid_open_set.py",
        "train_strict_v4_xgboost_warning_task.py",
    )
    implementation_sha256 = {
        name: file_hash(project_root / name) for name in implementations
    }
    seeds = STAGE_SEEDS[stage]
    task_identities = [
        f"{scenario}_seed{seed}"
        for seed in seeds
        for scenario in FAMILY_SCENARIOS
    ]
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_cicids2017_attack_family_protocol_v1",
        "state": f"frozen_zero_result_{stage}",
        "stage": stage,
        "suite": "cicids2017_attack_family",
        "authorized_level": "attack_family",
        "benign_family": "Benign",
        "fine_to_family": FINE_TO_FAMILY,
        "scenarios": FAMILY_SCENARIOS,
        "seeds": list(seeds),
        "fresh_confirmation_seeds": stage == "confirmation",
        "expected_task_count": len(task_identities),
        "task_identities": task_identities,
        "source": {
            "csv": str(source_csv),
            "csv_sha256": file_hash(source_csv),
            "config": str(config_path),
            "config_sha256": file_hash(config_path),
        },
        "paths": {
            "cache_root": str(cache_root),
            "run_root": str(run_root),
            "result_root": str(result_root),
        },
        "cache_policy": {
            "maximum_per_family": 5000,
            "chunksize": 50000,
            "balance_level": "attack_family",
            "preserve_fine_label_for_audit_only": True,
            "test_labels_used_for_sampling": False,
        },
        "pairwise_caeos": {
            "estimators": 80,
            "jobs_per_task": 8,
            "split_strategy": "capture_grouped",
            "risk_selection": (
                "nested_boundary_pairwise_pseudo_unknown_blend"
            ),
            "risk_policy_name": (
                "strict_v4_attack_family_pairwise_caeos_v1"
            ),
            "modality_gate_minimum_gain": 0.02,
            "conflict_fallback_minimum_gain": 0.055,
            "joint_fallback_minimum_gain": 0.055,
            "density_gate_minimum_gain": 0.02,
            "density_gate_minimum_known_classes": 8,
            "density_gate_blend_weight": 0.05,
            "pseudo_unknown_max_alpha": 0.5,
            "pseudo_unknown_min_fold_gain": -0.05,
            "pseudo_unknown_local_rank_bins": 5,
            "pseudo_unknown_local_rank_beta": 1.0,
            "boundary_hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "boundary_training_objective": "pairwise",
            "structural_gate_minimum_gain": 0.02,
        },
        "xgboost_known_expert": {
            "version": "2.1.4",
            "package_root": "/opt/data/private/wangwt/python_packages/xgboost-2.1.4",
            "validation_benign_fpr_budget": 0.04,
            "estimators": 1000,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "early_stopping_rounds": 30,
            "jobs_per_task": 8,
        },
        "hybrid_candidate_space": {
            "alert_variants": ["xgb_attack", "tail_max", "tail_noisy_or"],
            "alert_budgets": [0.01, 0.02, 0.03, 0.04],
            "open_variants": ["risk_tail", "tail_max", "tail_noisy_or"],
            "open_budgets": [0.005, 0.01, 0.02, 0.03, 0.04],
            "candidate_count": 180,
            "single_global_configuration": True,
        },
        "selected_configuration": selected_configuration,
        "selection_source": selection_source,
        "implementation_sha256": implementation_sha256,
        "resource_contract": {
            "gpu_server_only": True,
            "logical_cpu_count": 80,
            "memory_gib": 512,
            "gpu_memory_gib": 49,
            "outer_workers": 7,
            "model_jobs_per_task": 8,
            "declared_cpu_slots": 56,
            "minimum_total_cpu_busy_fraction": 0.5,
            "preferred_total_cpu_busy_fraction": 0.8,
            "runs_concurrently_with_rrc_workers4": True,
        },
        "target_contract": {
            "self_algorithm_only": True,
            "alert_accuracy_at_least": 0.95,
            "benign_fpr_strictly_below": 0.05,
            "known_attack_family_accuracy_at_least": 0.95,
            "unknown_attack_family_recall_at_least": 0.95,
            "all_fresh_confirmation_seeds_must_pass": True,
        },
        "claim_boundary": {
            "family_level_only": True,
            "fine_subtype_claim_authorized": False,
            "development_seed7_may_select_configuration": stage == "development",
            "confirmation_test_or_unknown_labels_may_select_nothing": True,
            "xgboost_alone_is_a_baseline_not_the_self_algorithm": True,
        },
        "formal_output_counts_at_freeze": {
            "completion": 0,
            "evaluation": 0,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument(
        "--stage", choices=tuple(STAGE_SEEDS), required=True
    )
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--development-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        stage=args.stage,
        source_csv=args.source_csv,
        config_path=args.config,
        cache_root=args.cache_root,
        run_root=args.run_root,
        result_root=args.result_root,
        development_result_path=args.development_result,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()

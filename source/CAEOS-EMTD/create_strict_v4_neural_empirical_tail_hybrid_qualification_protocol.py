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
SELECTED_CONFIGURATION = {
    "alert_budget": 0.04,
    "alert_variant": "xgb_attack",
    "open_budget": 0.04,
    "open_variant": "tail_noisy_or",
    "risk_name": "knn",
}


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


def load_canonical(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    declared = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")
    return value


def source_task_hashes(
    pairwise_dir: Path, cache_path: Path
) -> dict[str, str]:
    paths = {
        "pairwise_metrics": pairwise_dir / "metrics.json",
        "pairwise_scores": pairwise_dir / "scores.npz",
        "pairwise_provenance": pairwise_dir / "provenance.json",
        "cache_csv": cache_path,
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    return {name: file_hash(path) for name, path in paths.items()}


def build_protocol(
    *,
    project_root: Path,
    screening_path: Path,
    pairwise_root: Path,
    cache_root: Path,
    config_path: Path,
    source_csv: Path,
    neural_cache_dir: Path,
    xgboost_package_root: Path,
    xgboost_output_root: Path,
    matrix_output_root: Path,
    result_root: Path,
    required_gpu_uuid: str,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    screening_path = screening_path.resolve()
    pairwise_root = pairwise_root.resolve()
    cache_root = cache_root.resolve()
    config_path = config_path.resolve()
    source_csv = source_csv.resolve()
    neural_cache_dir = neural_cache_dir.resolve()
    xgboost_package_root = xgboost_package_root.resolve()
    xgboost_output_root = xgboost_output_root.resolve()
    matrix_output_root = matrix_output_root.resolve()
    result_root = result_root.resolve()
    neural_root = matrix_output_root / "cicids2017"
    xgboost_root = xgboost_output_root / "cicids2017"
    if not source_csv.is_file():
        raise FileNotFoundError(source_csv)

    screening = load_canonical(screening_path, "development screening")
    if (
        screening.get("state")
        != "complete_architecture_screening_diagnostic"
        or screening.get("selected", {}).get("configuration")
        != SELECTED_CONFIGURATION
    ):
        raise ValueError("screening does not bind the frozen candidate")
    if (result_root / "qualification.json").is_file():
        raise ValueError("qualification result must be zero at protocol freeze")
    if neural_root.exists() and any(neural_root.rglob("metrics.json")):
        raise ValueError("fresh neural result must be zero at protocol freeze")
    if xgboost_root.exists() and any(xgboost_root.rglob("metrics.json")):
        raise ValueError("fresh XGBoost CUDA result must be zero at protocol freeze")

    input_sha256: dict[str, dict[str, dict[str, str]]] = {}
    for seed in SEEDS:
        seed_hashes = {}
        for scenario in SCENARIOS:
            seed_hashes[scenario] = source_task_hashes(
                pairwise_root / f"{scenario}_seed{seed}",
                cache_root / f"seed{seed}_max5000.csv",
            )
        input_sha256[str(seed)] = seed_hashes

    implementation_names = (
        "run_neural_baseline_matrix.py",
        "train_neural_open_set.py",
        "train_strict_v4_xgboost_warning_task.py",
        "train_strict_v4_xgboost_warning_task_cuda.py",
        "run_strict_v4_xgboost_cuda_qualification_batch.py",
        "run_strict_v4_neural_empirical_tail_hybrid_qualification.py",
        "evaluate_strict_v4_neural_empirical_tail_hybrid_qualification.py",
    )
    implementation_sha256 = {
        name: file_hash(project_root / name) for name in implementation_names
    }
    contract_path = (
        project_root / "contracts" / "caeos_delivery_contract_v1.json"
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_qualification_protocol_v1"
        ),
        "state": "frozen_zero_result_gpu_qualification",
        "delivery_line": "engineering",
        "algorithm": (
            "Neural Empirical-Tail Hybrid CAEOS: XGBoost CUDA attack expert "
            "plus MLP empirical-tail open-set head"
        ),
        "selected_configuration": dict(SELECTED_CONFIGURATION),
        "selection_source": {
            "screening_path": str(screening_path),
            "screening_file_sha256": file_hash(screening_path),
            "screening_manifest_sha256": screening["manifest_sha256"],
            "development_seed": 7,
            "outer_unknown_labels_used_for_development_selection": True,
        },
        "suite": "cicids2017",
        "seeds": list(SEEDS),
        "scenarios": list(SCENARIOS),
        "expected_task_count": len(SEEDS) * len(SCENARIOS),
        "stage": "qualification",
        "matrix_output_root": str(matrix_output_root),
        "neural_root": str(neural_root),
        "xgboost_output_root": str(xgboost_output_root),
        "xgboost_root": str(xgboost_root),
        "pairwise_root": str(pairwise_root),
        "cache_root": str(cache_root),
        "config_path": str(config_path),
        "source_csv": str(source_csv),
        "neural_cache_dir": str(neural_cache_dir),
        "result_root": str(result_root),
        "training": {
            "neural": {
                "model": "mlp",
                "epochs": 35,
                "patience": 10,
                "workers": 12,
                "device": "cuda",
            },
            "xgboost_cuda": {
                "package_root": str(xgboost_package_root),
                "estimators": 1000,
                "max_depth": 8,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "early_stopping_rounds": 30,
                "jobs_per_task": 4,
                "parallel_tasks": 8,
                "validation_benign_fpr_budget": 0.04,
                "device": "cuda",
            },
            "formal_local_execution_forbidden": True,
        },
        "resource_contract": {
            "required_gpu_uuid": required_gpu_uuid,
            "minimum_mean_gpu_utilization_percent": 50.0,
            "preferred_mean_gpu_utilization_percent": 80.0,
            "sample_interval_seconds": 2.0,
        },
        "acceptance_contract": {
            "contract_path": str(contract_path),
            "contract_file_sha256": file_hash(contract_path),
            "engineering_gate": "engineering_safety_95_5",
            "paper_gate": "paper_full_open_set_95_5",
            "all_fresh_seeds_must_pass_point_estimates": True,
            "confirmation_requires_at_least_five_seeds": True,
        },
        "anti_leakage": {
            "configuration_is_frozen_from_seed7_development": True,
            "fresh_unknown_or_test_labels_used_for_training": False,
            "fresh_unknown_or_test_labels_used_for_thresholds": False,
            "fresh_unknown_or_test_labels_used_for_selection": False,
            "thresholds_use_known_only_validation": True,
        },
        "source_sha256": {
            "split_and_cache_inputs": input_sha256,
            "source_csv": file_hash(source_csv),
            "fresh_neural_result_count_at_freeze": 0,
            "fresh_xgboost_cuda_result_count_at_freeze": 0,
        },
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "three_seed_qualification_is_not_formal_confirmation": True,
            "point_estimate_pass_is_not_confidence_acceptance": True,
            "single_suite_is_not_cross_dataset_generalization": True,
            "engineering_candidate_is_not_the_paper_multimodal_claim": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--screening", type=Path, required=True)
    parser.add_argument("--pairwise-root", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--neural-cache-dir", type=Path, required=True)
    parser.add_argument("--xgboost-package-root", type=Path, required=True)
    parser.add_argument("--xgboost-output-root", type=Path, required=True)
    parser.add_argument("--matrix-output-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--required-gpu-uuid", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        screening_path=args.screening,
        pairwise_root=args.pairwise_root,
        cache_root=args.cache_root,
        config_path=args.config,
        source_csv=args.source_csv,
        neural_cache_dir=args.neural_cache_dir,
        xgboost_package_root=args.xgboost_package_root,
        xgboost_output_root=args.xgboost_output_root,
        matrix_output_root=args.matrix_output_root,
        result_root=args.result_root,
        required_gpu_uuid=args.required_gpu_uuid,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": protocol["manifest_sha256"],
                "output": str(args.output.resolve()),
                "task_count": protocol["expected_task_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

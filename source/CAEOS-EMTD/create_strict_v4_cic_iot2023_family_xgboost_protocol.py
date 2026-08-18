from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from strict_v4_cic_iot2023_attack_family import (
    ATTACK_FAMILIES,
    FINE_TO_FAMILY,
    atomic_json,
    canonical_hash,
    file_hash,
)


GPU_UUID = "GPU-a186fd29-e5be-496b-d374-4baeada258ee"
IMPLEMENTATIONS = (
    "strict_v4_cic_iot2023_attack_family.py",
    "train_strict_v4_fine_balanced_xgboost_task_cuda.py",
    "create_strict_v4_cic_iot2023_family_xgboost_protocol.py",
    "run_strict_v4_fine_balanced_xgboost_development.py",
    "evaluate_strict_v4_fine_balanced_xgboost_development.py",
    "evaluate_strict_v4_packet_sequence_fusion_development.py",
)


def cache_audit(
    cache_csv: Path,
    label_column: str,
    maximum_per_fine_class: int,
) -> dict[str, Any]:
    frame = pd.read_csv(
        cache_csv,
        usecols=[label_column],
        dtype={label_column: str},
        low_memory=False,
    )
    labels = frame[label_column].astype(str).str.strip()
    observed = set(labels)
    unknown = sorted(observed - set(FINE_TO_FAMILY))
    missing = sorted(set(FINE_TO_FAMILY) - observed)
    if unknown:
        raise ValueError(f"CICIoT2023 cache has unmapped labels: {unknown}")
    if missing:
        raise ValueError(f"CICIoT2023 cache misses labels: {missing}")
    counts = {
        str(label): int(count)
        for label, count in labels.value_counts().sort_index().items()
    }
    if any(count > maximum_per_fine_class for count in counts.values()):
        raise ValueError("CICIoT2023 cache exceeds per-class maximum")
    return {"rows": int(len(frame)), "fine_class_counts": counts}


def build_protocol(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    cache_csv = args.cache_csv.resolve()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    label_column = str(config["label_column"])
    group_column = str(config.get("group_column", "")).strip()
    if not group_column:
        raise ValueError("capture-grouped protocol requires config group_column")
    audit = cache_audit(
        cache_csv,
        label_column,
        args.maximum_per_fine_class,
    )
    if audit["rows"] != args.expected_rows:
        raise ValueError(
            f"CICIoT2023 cache row count is {audit['rows']}, "
            f"expected {args.expected_rows}"
        )
    implementation_hashes = {
        name: file_hash(project_root / name) for name in IMPLEMENTATIONS
    }
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_cic_iot2023_family_xgboost_development_protocol_v1"
        ),
        "state": "frozen_before_development_effects",
        "stage": "development",
        "algorithm": {
            "name": "CAEOS-EMTD family-held-out CUDA branch",
            "architecture": "fine_grained_dual_xgboost_cuda_v1",
        },
        "taxonomy": "cic_iot2023",
        "classification_level": args.classification_level,
        "fine_balanced_cache": {
            "path": str(cache_csv),
            "sha256": file_hash(cache_csv),
            "config_path": str(config_path),
            "config_sha256": file_hash(config_path),
            "rows": audit["rows"],
            "fine_class_counts": audit["fine_class_counts"],
            "maximum_per_fine_class": args.maximum_per_fine_class,
            "group_column": group_column,
            "split_strategy": "capture_grouped",
            "fine_to_family_mapping": FINE_TO_FAMILY,
        },
        "development_seed": args.development_seed,
        "confirmation_seeds": [331, 337, 347],
        "confirmation_seed_access": (
            "forbidden_until_development_full_gate_passes"
        ),
        "unknown_families": list(ATTACK_FAMILIES),
        "expected_task_count": len(ATTACK_FAMILIES),
        "training": {
            "estimators": 1200,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "early_stopping_rounds": 40,
            "jobs": 8,
            "chunksize": 100000,
            "preprocessing": "training_split_median_mean_std_clip_12",
        },
        "execution": {
            "backend": "xgboost_cuda",
            "required_gpu_uuid": GPU_UUID,
            "xgboost_root": str(args.xgboost_root.resolve()),
            "maximum_parallel_tasks": args.maximum_parallel_tasks,
            "gpu_sample_interval_seconds": 0.2,
            "formal_training_on_gpu_server_only": True,
            "minimum_end_to_end_gpu_mean_percent": 50.0,
            "preferred_end_to_end_gpu_mean_percent": 80.0,
        },
        "evaluation": {
            "three_layers": {
                "known": ["known_macro_f1", "balanced_accuracy"],
                "unknown": [
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "unknown_f1",
                ],
                "joint": ["oscr"],
            },
            "safety_target": {
                "alert_accuracy_minimum": 0.95,
                "alert_precision_minimum": 0.95,
                "attack_recall_minimum": 0.95,
                "benign_fpr_strictly_below": 0.05,
                "known_attack_type_accuracy_minimum": 0.95,
                "unknown_attack_alert_recall_minimum": 0.95,
                "unknown_label_recall_minimum": 0.95,
            },
            "development_configuration_search_uses_true_unknown": True,
            "fresh_confirmation_required": True,
        },
        "paths": {
            "project_root": str(project_root),
            "run_root": str(args.run_root.resolve()),
            "result_root": str(args.result_root.resolve()),
        },
        "implementation_sha256": implementation_hashes,
        "claim_boundary": {
            "development_only": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "all_training_tasks_require_xgboost_cuda_evidence": True,
            "unknown_family_fine_classes_excluded_from_train_and_validation": True,
            "known_prediction_granularity": args.classification_level,
            "fine_grained_classification_reported_separately": (
                args.classification_level == "family"
            ),
            "dataset_family_holdout_is_not_cross_dataset_generalization": True,
            "paper_multimodal_claim_not_established_by_this_branch": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--cache-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--expected-rows", type=int, default=33000)
    parser.add_argument("--maximum-per-fine-class", type=int, default=1000)
    parser.add_argument("--development-seed", type=int, default=283)
    parser.add_argument(
        "--classification-level",
        choices=("fine", "family"),
        default="family",
    )
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-parallel-tasks", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite frozen protocol: {output}")
    result_root = args.result_root.resolve()
    forbidden = (
        result_root / "completion.json",
        result_root / "evaluation.json",
    )
    if any(path.exists() for path in forbidden):
        raise ValueError("development effects exist before protocol freeze")
    protocol = build_protocol(args)
    atomic_json(output, protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


GPU_UUID = "GPU-a186fd29-e5be-496b-d374-4baeada258ee"
DATASET_SHA256 = (
    "82cccd6d8022a576f65b9931c614a856c66d205b039210c4c7a69972bdcf7716"
)
TASKS = (
    {"split_seed": 43, "model_seeds": [131, 137, 139]},
    {"split_seed": 47, "model_seeds": [149, 151, 157]},
)
FIXED_CONFIGURATION = {
    "attack_source": "family",
    "attack_aggregation": "maximum",
    "alert_budget": 0.04,
    "open_aggregation": "maximum",
    "open_budget": 0.04,
    "type_rule": "validation_best_macro_f1_member",
}
IMPLEMENTATIONS = (
    "train_strict_v4_fhmm_stable_task_cuda.py",
    "evaluate_strict_v4_fhmm_calibrated_aggregation_development.py",
    "evaluate_strict_v4_fhmm_calibrated_aggregation_development_v2.py",
    "evaluate_strict_v4_fhmm_stable_confirmation.py",
    "complete_strict_v4_fhmm_stable_confirmation.py",
    "create_strict_v4_fhmm_stable_confirmation_protocol.py",
    "strict_v4_open_set_metric_contract_v2.py",
    "audit_strict_v4_gpu_execution_resource.py",
    "scripts/run_strict_v4_fhmm_stable_confirmation_v1.sh",
)


def require_empty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"fresh confirmation target is not empty: {path}")


def build_protocol(
    *,
    project_root: Path,
    sequence_dataset: Path,
    development_result: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    sequence_dataset = sequence_dataset.resolve()
    development_result = development_result.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    if file_hash(sequence_dataset) != DATASET_SHA256:
        raise ValueError("confirmation dataset hash drifted")
    development = load_canonical(
        development_result,
        "calibrated aggregation development v2",
    )
    if (
        development["schema_version"]
        != "strict_v4_fhmm_calibrated_aggregation_development_v2"
        or development["selected"]["configuration"] != FIXED_CONFIGURATION
    ):
        raise ValueError("development result does not bind fixed candidate")
    with np.load(sequence_dataset, allow_pickle=False) as source:
        rows = int(source["families"].shape[0])
        families = sorted(
            str(value) for value in np.unique(source["families"]).tolist()
        )
    require_empty(run_root)
    require_empty(result_root)
    implementation_hashes = {}
    for name in IMPLEMENTATIONS:
        path = project_root / name
        if not path.is_file():
            raise FileNotFoundError(f"implementation missing: {path}")
        implementation_hashes[name] = file_hash(path)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_stable_confirmation_protocol_v1",
        "state": "frozen_before_fresh_training",
        "algorithm": {
            "name": "FHMM-SR-CAEOS",
            "training": (
                "stable FP32 first-order family-held-out meta learner"
            ),
            "decision": (
                "validation-calibrated robust multi-initialization routing"
            ),
        },
        "dataset": {
            "path": str(sequence_dataset),
            "sha256": DATASET_SHA256,
            "rows": rows,
            "families": families,
        },
        "tasks": list(TASKS),
        "training": {
            "epochs_requested": 120,
            "batch_size": 512,
            "inference_batch_size": 4096,
            "learning_rate": 0.002,
            "weight_decay": 0.0001,
            "attack_loss_weight": 1.0,
            "knownness_loss_weight": 0.2,
            "family_contrastive_loss_weight": 0.10,
            "attack_contrastive_loss_weight": 0.30,
            "pseudo_mix_loss_weight": 0.25,
            "episodic_margin_loss_weight": 0.15,
            "statistic_modality_dropout_probability": 0.5,
            "meta_heldout_loss_weight": 0.5,
            "meta_inner_learning_rate": 0.02,
            "meta_inner_gradient_clip_norm": 1.0,
            "outer_gradient_clip_norm": 5.0,
            "meta_episode_rows_per_class": 64,
            "contrastive_temperature": 0.12,
            "pseudo_mix_lambda": 0.5,
            "cosine_scale": 16.0,
            "known_similarity_margin": 0.35,
            "pseudo_unknown_similarity_margin": 0.15,
            "early_stopping_patience": 24,
            "minimum_improvement": 0.0001,
            "gpu_sample_interval_seconds": 0.2,
        },
        "fixed_configuration": FIXED_CONFIGURATION,
        "evaluation_targets": {
            "alert_accuracy_minimum": 0.95,
            "benign_fpr_strictly_below": 0.05,
            "known_attack_type_accuracy_minimum": 0.95,
            "unknown_attack_alert_recall_minimum": 0.85,
            "unknown_attack_rejection_recall_minimum": 0.30,
            "unknown_auroc_minimum": 0.88,
            "oscr_minimum": 0.87,
        },
        "execution": {
            "backend": "pytorch_cuda",
            "required_gpu_uuid": GPU_UUID,
            "parallel_members_per_split": 3,
            "minimum_mean_gpu_utilization_percent_each_member": 50.0,
            "maximum_peak_gpu_memory_mib_each_member": 45000.0,
        },
        "development_source": {
            "path": str(development_result),
            "file_sha256": file_hash(development_result),
            "manifest_sha256": development["manifest_sha256"],
            "true_unknown_was_used_for_development_selection": True,
        },
        "paths": {
            "project_root": str(project_root),
            "run_root": str(run_root),
            "result_root": str(result_root),
        },
        "implementation_sha256": implementation_hashes,
        "claim_boundary": {
            "split43_and_split47_unread_before_protocol_freeze": True,
            "unknown_or_test_labels_for_threshold_selection": False,
            "configuration_and_targets_frozen_before_training": True,
            "two_split_confirmation_is_not_formal_five_seed_evidence": True,
            "formal_training_on_gpu_server_only": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--development-result", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite protocol: {output}")
    protocol = build_protocol(
        project_root=args.project_root,
        sequence_dataset=args.sequence_dataset,
        development_result=args.development_result,
        run_root=args.run_root,
        result_root=args.result_root,
    )
    atomic_json(output, protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

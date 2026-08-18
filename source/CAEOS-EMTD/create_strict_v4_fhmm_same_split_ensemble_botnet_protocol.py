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
)


GPU_UUID = "GPU-a186fd29-e5be-496b-d374-4baeada258ee"
DATASET_SHA256 = (
    "82cccd6d8022a576f65b9931c614a856c66d205b039210c4c7a69972bdcf7716"
)
SPLIT_MODELS = {
    37: [101, 103, 107],
    41: [109, 113, 127],
}
IMPLEMENTATIONS = (
    "train_strict_v4_dual_metric_contrastive_task_cuda.py",
    "train_strict_v4_fhmm_same_split_member_cuda.py",
    "evaluate_strict_v4_fhmm_same_split_ensemble.py",
    "strict_v4_open_set_metric_contract_v2.py",
    "audit_strict_v4_gpu_execution_resource.py",
    "complete_strict_v4_fhmm_same_split_ensemble_botnet_pilot.py",
    "create_strict_v4_fhmm_same_split_ensemble_botnet_protocol.py",
    "scripts/run_strict_v4_fhmm_same_split_ensemble_botnet_pilot_v1.sh",
)


def _require_empty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"pre-registration target must be empty: {path}")


def build_protocol(
    *,
    project_root: Path,
    sequence_dataset: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    sequence_dataset = sequence_dataset.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    if file_hash(sequence_dataset) != DATASET_SHA256:
        raise ValueError("sequence dataset differs from frozen dataset hash")
    with np.load(sequence_dataset, allow_pickle=False) as source:
        families = sorted(
            str(value) for value in np.unique(source["families"]).tolist()
        )
        row_count = int(source["families"].shape[0])
    if families != [
        "Benign",
        "Botnet",
        "BruteForce",
        "DDoS",
        "DoS",
        "Exploit",
        "Reconnaissance",
        "WebAttack",
    ]:
        raise ValueError(f"unexpected dataset families: {families}")
    _require_empty(run_root)
    _require_empty(result_root)
    implementation_hashes = {}
    for name in IMPLEMENTATIONS:
        path = project_root / name
        if not path.is_file():
            raise FileNotFoundError(f"implementation missing: {path}")
        implementation_hashes[name] = file_hash(path)
    tasks = [
        {
            "unknown_family": "Botnet",
            "split_seed": split_seed,
            "model_seeds": model_seeds,
        }
        for split_seed, model_seeds in SPLIT_MODELS.items()
    ]
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fhmm_same_split_ensemble_botnet_protocol_v1"
        ),
        "state": "frozen_before_any_member_training",
        "stage": "development_replicability_pilot",
        "algorithm": {
            "name": "FHMM-CAEOS-MI3",
            "description": (
                "fixed three-initialization ensemble of the unchanged "
                "family-held-out malicious-boundary meta learner"
            ),
            "member_count": 3,
        },
        "dataset": {
            "path": str(sequence_dataset),
            "sha256": DATASET_SHA256,
            "rows": row_count,
            "families": families,
        },
        "tasks": tasks,
        "split": {
            "method": "sha256_seed_nul_flow_id",
            "split_seed_is_independent_of_model_seed": True,
            "known_train_validation_test_fraction": [0.6, 0.2, 0.2],
            "unknown_family_train_rows": 0,
            "unknown_family_validation_rows": 0,
            "unknown_family_test_fraction": 1.0,
        },
        "training": {
            "epochs": 120,
            "batch_size": 512,
            "inference_batch_size": 4096,
            "learning_rate": 0.002,
            "weight_decay": 0.0001,
            "statistic_modality_dropout_probability": 0.5,
            "meta_heldout_loss_weight": 1.0,
            "meta_inner_learning_rate": 0.05,
            "meta_episode_rows_per_class": 64,
            "configuration_selection": "none_fixed_before_test",
        },
        "ensemble": {
            "attack_aggregation": "arithmetic_mean_probability",
            "open_aggregation": "arithmetic_mean_member_open_max",
            "type_aggregation": (
                "three_member_hard_majority_vote_lowest_class_tie_break"
            ),
        },
        "evaluation": {
            "alert_threshold_source": "known_only_validation_benign",
            "alert_budget": 0.049,
            "open_threshold_source": "known_only_validation_known_attack",
            "open_budget": 0.04,
            "unknown_or_test_labels_used_for_threshold": False,
            "operational_expansion_gate_each_split": {
                "alert_accuracy_minimum": 0.95,
                "benign_fpr_strictly_below": 0.05,
                "known_attack_type_accuracy_minimum": 0.95,
                "unknown_attack_alert_recall_minimum": (
                    0.6036585365853659
                ),
            },
            "research_main_metrics": [
                "known_macro_f1",
                "known_balanced_accuracy",
                "unknown_auroc",
                "unknown_aupr_out",
                "fpr_known_at_95_unknown_tpr",
                "oscr_exact_v2",
            ],
            "expand_only_if_both_split_repeats_pass": True,
        },
        "execution": {
            "backend": "pytorch_cuda",
            "required_gpu_uuid": GPU_UUID,
            "gpu_index": 0,
            "parallel_members_per_split": 3,
            "minimum_mean_gpu_utilization_percent_each_member": 50.0,
            "maximum_peak_gpu_memory_mib_each_member": 45000.0,
            "formal_training_on_gpu_server_only": True,
        },
        "paths": {
            "project_root": str(project_root),
            "run_root": str(run_root),
            "result_root": str(result_root),
        },
        "implementation_sha256": implementation_hashes,
        "claim_boundary": {
            "development_pilot_only": True,
            "true_unknown_used_for_training_or_threshold_selection": False,
            "effect_gate_is_pre_registered": True,
            "fresh_confirmation_effect_claim_authorized": False,
            "flow_id_hash_split_is_not_capture_grouped": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--sequence-dataset", type=Path, required=True)
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
        run_root=args.run_root,
        result_root=args.result_root,
    )
    atomic_json(output, protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

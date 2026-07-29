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
DEVELOPMENT_SEED = 29
IMPLEMENTATIONS = (
    "train_strict_v4_dual_metric_contrastive_task_cuda.py",
    "create_strict_v4_dual_metric_contrastive_protocol.py",
    "run_strict_v4_dual_metric_contrastive_development.py",
    "evaluate_strict_v4_dual_metric_contrastive_development.py",
    "evaluate_strict_v4_packet_sequence_fusion_development.py",
)


def build_protocol(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    dataset = args.sequence_dataset.resolve()
    metadata_path = dataset.with_suffix(dataset.suffix + ".json")
    metadata = load_canonical(metadata_path, "packet/statistic dataset")
    if (
        metadata.get("state")
        != "complete_remote_packet_sequence_statistic_augmentation"
        or file_hash(dataset) != metadata["dataset"]["output_sha256"]
    ):
        raise ValueError("packet/statistic dataset provenance failed")
    with np.load(dataset, allow_pickle=False) as source:
        families = sorted(str(value) for value in np.unique(source["families"]))
        rows = int(source["families"].shape[0])
        sequence_length = int(source["packet_lengths"].shape[1])
        statistic_dimension = int(source["flow_statistics"].shape[1])
    unknown_families = [value for value in families if value != "Benign"]
    if len(unknown_families) != 7:
        raise ValueError("expected seven attack families")
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_dual_metric_contrastive_protocol_v1"
        ),
        "state": "frozen_development_protocol",
        "stage": "development",
        "algorithm": {
            "name": "DMC-CAEOS",
            "architecture": "dual_metric_contrastive_packet_statistic_v1",
        },
        "sequence_dataset": {
            "path": str(dataset),
            "sha256": file_hash(dataset),
            "metadata_path": str(metadata_path),
            "metadata_sha256": file_hash(metadata_path),
            "metadata_manifest_sha256": metadata["manifest_sha256"],
            "rows": rows,
            "sequence_length": sequence_length,
            "flow_statistic_dimension": statistic_dimension,
        },
        "development_seed": DEVELOPMENT_SEED,
        "confirmation_seeds": [953, 967, 971],
        "confirmation_seed_access": (
            "forbidden_until_development_full_gate_passes"
        ),
        "unknown_families": unknown_families,
        "expected_task_count": len(unknown_families),
        "training": {
            "epochs": 160,
            "batch_size": 1024,
            "inference_batch_size": 4096,
            "learning_rate": 0.002,
            "weight_decay": 0.0001,
            "attack_loss_weight": 1.0,
            "knownness_loss_weight": 0.2,
            "family_contrastive_loss_weight": 0.10,
            "attack_contrastive_loss_weight": 0.30,
            "pseudo_mix_loss_weight": 0.25,
            "episodic_margin_loss_weight": 0.15,
            "contrastive_temperature": 0.12,
            "pseudo_mix_lambda": 0.5,
            "cosine_scale": 16.0,
            "known_similarity_margin": 0.35,
            "pseudo_unknown_similarity_margin": 0.15,
            "early_stopping_patience": 24,
            "minimum_improvement": 0.0001,
            "flow_statistic_scaling": "training_split_median_iqr_clip_10",
        },
        "execution": {
            "backend": "pytorch_cuda",
            "required_gpu_uuid": GPU_UUID,
            "gpu_index": 0,
            "maximum_parallel_tasks": args.maximum_parallel_tasks,
            "gpu_sample_interval_seconds": 0.2,
            "formal_training_on_gpu_server_only": True,
            "resource_target": {
                "preferred_gpu_utilization_percent": 80.0,
                "minimum_mean_gpu_utilization_percent": 50.0,
            },
        },
        "evaluation": {
            "attack_probability_variants": [
                "attack_head",
                "family",
                "maximum",
                "noisy_or",
            ],
            "target": {
                "alert_accuracy_minimum": 0.95,
                "alert_precision_minimum": 0.95,
                "alert_recall_minimum": 0.95,
                "benign_fpr_strictly_below": 0.05,
                "known_attack_type_accuracy_minimum": 0.95,
                "unknown_attack_recall_minimum": 0.95,
            },
        },
        "paths": {
            "project_root": str(project_root),
            "run_root": str(args.run_root.resolve()),
            "result_root": str(args.result_root.resolve()),
        },
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATIONS
        },
        "claim_boundary": {
            "development_only": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "true_unknown_absent_from_training_and_early_stopping": True,
            "pseudo_unknowns_use_known_training_families_only": True,
            "all_formal_training_must_pass_pytorch_cuda_audit": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-parallel-tasks", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    protocol = build_protocol(args)
    atomic_json(args.output.resolve(), protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

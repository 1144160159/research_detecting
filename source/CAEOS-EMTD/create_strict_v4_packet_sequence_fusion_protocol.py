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
    "prepare_strict_v4_cicids2017_packet_sequences.py",
    "augment_strict_v4_cicids2017_packet_sequence_statistics.py",
    "train_strict_v4_packet_sequence_fusion_task_cuda.py",
    "evaluate_strict_v4_packet_sequence_fusion_development.py",
    "create_strict_v4_packet_sequence_fusion_protocol.py",
    "run_strict_v4_packet_sequence_fusion_development.py",
    "verify_xgboost_cuda_backend.py",
)


def build_protocol(
    *,
    project_root: Path,
    sequence_dataset: Path,
    result_root: Path,
    run_root: Path,
    maximum_parallel_tasks: int,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    sequence_dataset = sequence_dataset.resolve()
    metadata_path = sequence_dataset.with_suffix(sequence_dataset.suffix + ".json")
    metadata = load_canonical(metadata_path, "packet-sequence dataset metadata")
    if metadata.get("state") not in {
        "complete_remote_pcap_sequence_materialization",
        "complete_remote_packet_sequence_statistic_augmentation",
    }:
        raise ValueError("packet-sequence dataset preparation is incomplete")
    if file_hash(sequence_dataset) != metadata["dataset"]["output_sha256"]:
        raise ValueError("packet-sequence dataset hash differs from metadata")
    with np.load(sequence_dataset, allow_pickle=False) as source:
        families = sorted(str(value) for value in np.unique(source["families"]))
        rows = int(source["families"].shape[0])
        sequence_length = int(source["packet_lengths"].shape[1])
        if "flow_statistics" not in source.files:
            raise ValueError("PSF-CAEOS-F requires flow statistics")
        flow_statistics = np.asarray(source["flow_statistics"])
        flow_statistic_names = np.asarray(
            source["flow_statistic_names"]
        ).astype(str)
        if (
            flow_statistics.ndim != 2
            or flow_statistics.shape[0] != rows
            or flow_statistic_names.size != flow_statistics.shape[1]
        ):
            raise ValueError("flow statistic arrays are inconsistent")
    if "Benign" not in families:
        raise ValueError("packet-sequence dataset lacks the benign safety class")
    unknown_families = [family for family in families if family != "Benign"]
    if len(unknown_families) != 7:
        raise ValueError(f"expected seven attack families, found {unknown_families}")
    implementation_hashes = {}
    for name in IMPLEMENTATIONS:
        path = project_root / name
        if not path.is_file():
            raise FileNotFoundError(f"implementation missing: {path}")
        implementation_hashes[name] = file_hash(path)
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_protocol_v1",
        "state": "frozen_development_protocol",
        "stage": "development",
        "algorithm": {
            "name": "PSF-CAEOS-F",
            "expanded_name": (
                "Packet-Sequence and Flow-Statistic Fusion with "
                "Conflict-Aware Evidence and Open-Set Supervision"
            ),
            "architecture": (
                "residual_dilated_cnn_statistic_mlp_multitask_boundary_mix_v2"
            ),
        },
        "sequence_dataset": {
            "path": str(sequence_dataset),
            "sha256": file_hash(sequence_dataset),
            "metadata_path": str(metadata_path),
            "metadata_sha256": file_hash(metadata_path),
            "metadata_manifest_sha256": metadata["manifest_sha256"],
            "rows": rows,
            "sequence_length": sequence_length,
            "flow_statistic_dimension": int(flow_statistics.shape[1]),
            "flow_statistic_names": flow_statistic_names.tolist(),
        },
        "development_seed": DEVELOPMENT_SEED,
        "confirmation_seeds": [953, 967, 971],
        "confirmation_seed_access": "forbidden_until_development_full_gate_passes",
        "unknown_families": unknown_families,
        "expected_task_count": len(unknown_families),
        "split": {
            "known_family_train_fraction": 0.6,
            "known_family_validation_fraction": 0.2,
            "known_family_test_fraction": 0.2,
            "unknown_family_train_rows": 0,
            "unknown_family_validation_rows": 0,
            "unknown_family_test_fraction": 1.0,
            "deterministic_identity_hash": "sha256(seed NUL flow_id)",
        },
        "training": {
            "epochs": 160,
            "batch_size": 2048,
            "inference_batch_size": 4096,
            "learning_rate": 0.002,
            "weight_decay": 0.0001,
            "attack_loss_weight": 1.0,
            "knownness_loss_weight": 0.2,
            "boundary_mix_loss_weight": 0.4,
            "early_stopping_patience": 20,
            "minimum_improvement": 0.0001,
            "flow_statistic_scaling": "training_split_median_iqr_clip_10",
            "require_flow_statistics": True,
        },
        "execution": {
            "backend": "pytorch_cuda",
            "required_gpu_uuid": GPU_UUID,
            "gpu_index": 0,
            "maximum_parallel_tasks": maximum_parallel_tasks,
            "gpu_sample_interval_seconds": 0.2,
            "formal_training_on_gpu_server_only": True,
        },
        "evaluation": {
            "alert_budgets": [0.04, 0.045, 0.049],
            "open_budgets": [0.04, 0.045, 0.049],
            "open_evidence_includes_benign_prototype_distance": True,
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
            "run_root": str(run_root.resolve()),
            "result_root": str(result_root.resolve()),
        },
        "implementation_sha256": implementation_hashes,
        "claim_boundary": {
            "development_only": True,
            "true_unknown_may_be_used_for_development_selection": True,
            "fresh_confirmation_required_for_effect_claim": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "all_formal_model_training_must_pass_cuda_audit": True,
            "data_materialization_is_cpu_preprocessing": True,
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
    parser.add_argument("--maximum-parallel-tasks", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    protocol = build_protocol(
        project_root=args.project_root,
        sequence_dataset=args.sequence_dataset,
        result_root=args.result_root,
        run_root=args.run_root,
        maximum_parallel_tasks=args.maximum_parallel_tasks,
    )
    atomic_json(args.output.resolve(), protocol)
    print(json.dumps(protocol, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

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
    "train_strict_v4_flow_statistic_xgboost_task_cuda.py",
    "create_strict_v4_flow_statistic_xgboost_protocol.py",
    "run_strict_v4_flow_statistic_xgboost_development.py",
    "evaluate_strict_v4_packet_sequence_fusion_development.py",
)


def build_protocol(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    dataset = args.sequence_dataset.resolve()
    metadata_path = dataset.with_suffix(dataset.suffix + ".json")
    metadata = load_canonical(metadata_path, "statistic-fusion dataset")
    if (
        metadata.get("state")
        != "complete_remote_packet_sequence_statistic_augmentation"
        or file_hash(dataset) != metadata["dataset"]["output_sha256"]
    ):
        raise ValueError("statistic-fusion dataset did not pass provenance checks")
    with np.load(dataset, allow_pickle=False) as source:
        families = sorted(str(value) for value in np.unique(source["families"]))
        rows = int(source["families"].shape[0])
        statistic_dimension = int(source["flow_statistics"].shape[1])
    unknown_families = [value for value in families if value != "Benign"]
    if len(unknown_families) != 7:
        raise ValueError("expected seven attack families")
    implementation_hashes = {
        name: file_hash(project_root / name) for name in IMPLEMENTATIONS
    }
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_flow_statistic_xgboost_protocol_v1",
        "state": "frozen_development_protocol",
        "stage": "development",
        "algorithm": {
            "name": "FSX-CAEOS",
            "architecture": "dual_xgboost_cuda_open_evidence_v1",
        },
        "sequence_dataset": {
            "path": str(dataset),
            "sha256": file_hash(dataset),
            "metadata_path": str(metadata_path),
            "metadata_sha256": file_hash(metadata_path),
            "metadata_manifest_sha256": metadata["manifest_sha256"],
            "rows": rows,
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
            "estimators": 1200,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "early_stopping_rounds": 40,
            "jobs": 8,
            "flow_statistic_scaling": "training_split_median_iqr_clip_10",
        },
        "execution": {
            "backend": "xgboost_cuda",
            "required_gpu_uuid": GPU_UUID,
            "xgboost_root": str(args.xgboost_root.resolve()),
            "maximum_parallel_tasks": args.maximum_parallel_tasks,
            "gpu_sample_interval_seconds": 0.2,
            "formal_training_on_gpu_server_only": True,
        },
        "evaluation": {
            "target": {
                "alert_accuracy_minimum": 0.95,
                "alert_precision_minimum": 0.95,
                "alert_recall_minimum": 0.95,
                "benign_fpr_strictly_below": 0.05,
                "known_attack_type_accuracy_minimum": 0.95,
                "unknown_attack_recall_minimum": 0.95,
            }
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
            "all_formal_training_must_pass_xgboost_cuda_audit": True,
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
    parser.add_argument("--xgboost-root", type=Path, required=True)
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

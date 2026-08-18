from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import train_strict_v4_fhmm_stable_task_cuda as stable
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)
from train_strict_v4_packet_sequence_fusion_task_cuda import (
    BENIGN_FAMILY,
    hash_rank,
)


def stratified_open_set_split_70_10_20(
    flow_ids: np.ndarray,
    families: np.ndarray,
    *,
    unknown_family: str,
    seed: int,
) -> dict[str, np.ndarray]:
    train: list[int] = []
    validation: list[int] = []
    test: list[int] = []
    unique_families = sorted(str(value) for value in np.unique(families))
    if unknown_family not in unique_families or unknown_family == BENIGN_FAMILY:
        raise ValueError(f"invalid unknown attack family: {unknown_family}")
    for family in unique_families:
        indices = np.flatnonzero(families == family).tolist()
        indices.sort(key=lambda index: hash_rank(str(flow_ids[index]), seed))
        if family == unknown_family:
            test.extend(indices)
            continue
        count = len(indices)
        if count < 10:
            raise ValueError(
                f"known family {family} has fewer than ten flows"
            )
        train_count = max(1, int(math.floor(count * 0.7)))
        validation_count = max(1, int(math.floor(count * 0.1)))
        if train_count + validation_count >= count:
            validation_count = max(1, count - train_count - 1)
        train.extend(indices[:train_count])
        validation.extend(indices[train_count : train_count + validation_count])
        test.extend(indices[train_count + validation_count :])
    return {
        "train": np.asarray(sorted(train), dtype=np.int64),
        "validation": np.asarray(sorted(validation), dtype=np.int64),
        "test": np.asarray(sorted(test), dtype=np.int64),
    }


def train_task(args: Any) -> dict[str, Any]:
    original_split = stable.stratified_open_set_split
    stable.stratified_open_set_split = stratified_open_set_split_70_10_20
    try:
        report = stable.train_task(args)
    finally:
        stable.stratified_open_set_split = original_split
    report.pop("manifest_sha256", None)
    report["schema_version"] = (
        "strict_v4_fhmm_stable_70_10_20_cuda_task_v1"
    )
    report["model"]["name"] = (
        "FHMM-DS-CAEOS stable meta learner with 70/10/20 known split"
    )
    report["model"]["known_split_ratio"] = {
        "train": 0.7,
        "validation": 0.1,
        "test": 0.2,
        "unknown_family_all_in_test": True,
    }
    report["source"]["split_wrapper_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    report["claim_boundary"]["known_split_70_10_20"] = True
    report["claim_boundary"]["unknown_family_all_in_test"] = True
    report["claim_boundary"]["development_data_optimization_only"] = True
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(args.output_dir.resolve() / "metrics.json", report)
    return report


def main() -> None:
    args = stable.parse_arguments()
    if args.meta_heldout_loss_weight <= 0.0:
        raise ValueError("FHMM-DS requires positive meta heldout loss weight")
    if args.gradient_clip_norm <= 0.0:
        raise ValueError("gradient clip norm must be positive")
    report = train_task(args)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

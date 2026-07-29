from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from strict_v4_cicids2017_attack_family import (
    ATTACK_FAMILIES,
    atomic_json,
    canonical_hash,
    file_hash,
)


def create_fixture(
    *,
    output: Path,
    rows_per_family: int,
    sequence_length: int,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    families = ["Benign", *ATTACK_FAMILIES]
    rows = rows_per_family * len(families)
    packet_lengths = np.zeros((rows, sequence_length), dtype=np.int16)
    interarrival_us = np.zeros((rows, sequence_length), dtype=np.float32)
    mask = np.ones((rows, sequence_length), dtype=bool)
    labels = []
    flow_ids = []
    for family_index, family in enumerate(families):
        start = family_index * rows_per_family
        stop = start + rows_per_family
        base_length = 100 + family_index * 120
        lengths = rng.normal(
            base_length, 35.0, size=(rows_per_family, sequence_length)
        )
        direction = rng.choice(
            (-1, 1), size=(rows_per_family, sequence_length)
        )
        packet_lengths[start:stop] = np.clip(
            lengths * direction, -1500, 1500
        ).astype(np.int16)
        interarrival_us[start:stop] = rng.lognormal(
            mean=4.0 + 0.35 * family_index,
            sigma=0.5,
            size=(rows_per_family, sequence_length),
        ).astype(np.float32)
        labels.extend([family] * rows_per_family)
        flow_ids.extend(
            f"smoke-{family_index}-{row}" for row in range(rows_per_family)
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        np.savez_compressed(
            handle,
            packet_lengths=packet_lengths,
            interarrival_us=interarrival_us,
            mask=mask,
            flow_ids=np.asarray(flow_ids),
            capture_ids=np.asarray(["synthetic-smoke"] * rows),
            fine_labels=np.asarray(labels),
            families=np.asarray(labels),
        )
    report = {
        "schema_version": "strict_v4_packet_sequence_cuda_smoke_fixture_v1",
        "state": "complete_synthetic_fixture",
        "rows": rows,
        "rows_per_family": rows_per_family,
        "families": families,
        "sequence_length": sequence_length,
        "seed": seed,
        "output_path": str(output.resolve()),
        "output_sha256": file_hash(output),
        "claim_boundary": {
            "synthetic_data_only": True,
            "effect_result": False,
            "dataset_quality_evidence": False,
            "cuda_pipeline_smoke_only": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output.with_suffix(output.suffix + ".json"), report)
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows-per-family", type=int, default=512)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20260728)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    report = create_fixture(
        output=args.output.resolve(),
        rows_per_family=args.rows_per_family,
        sequence_length=args.sequence_length,
        seed=args.seed,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

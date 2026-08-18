from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import train_strict_v4_dual_metric_contrastive_task_cuda as training_core
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


def parse_split_seed(argv: list[str]) -> tuple[int, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--split-seed", type=int, required=True)
    split_args, remaining = parser.parse_known_args(argv)
    return int(split_args.split_seed), remaining


def train_same_split_member(
    args: argparse.Namespace,
    *,
    split_seed: int,
) -> dict[str, Any]:
    original_split = training_core.stratified_open_set_split

    def fixed_split(
        flow_ids: Any,
        families: Any,
        *,
        unknown_family: str,
        seed: int,
    ) -> dict[str, Any]:
        del seed
        return original_split(
            flow_ids,
            families,
            unknown_family=unknown_family,
            seed=split_seed,
        )

    training_core.stratified_open_set_split = fixed_split
    try:
        report = training_core.train_task(args)
    finally:
        training_core.stratified_open_set_split = original_split

    report["schema_version"] = "strict_v4_fhmm_same_split_member_cuda_task_v1"
    report["task"] = {
        "unknown_family": str(args.unknown_family),
        "split_seed": int(split_seed),
        "model_seed": int(args.seed),
    }
    report["model"]["name"] = (
        "FHMM-CAEOS same-split multi-initialization ensemble member"
    )
    report["source"]["base_training_kernel_sha256"] = file_hash(
        Path(training_core.__file__).resolve()
    )
    report["source"]["member_wrapper_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    report["claim_boundary"].update(
        {
            "split_seed_and_model_seed_separated": True,
            "base_training_kernel_modified": False,
            "member_is_not_a_standalone_confirmation": True,
        }
    )
    report.pop("manifest_sha256", None)
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(args.output_dir.resolve() / "metrics.json", report)
    return report


def main() -> None:
    split_seed, remaining = parse_split_seed(sys.argv[1:])
    original_argv = sys.argv
    sys.argv = [sys.argv[0], *remaining]
    try:
        args = training_core.parse_arguments()
    finally:
        sys.argv = original_argv
    if args.meta_heldout_loss_weight <= 0.0:
        raise ValueError(
            "FHMM same-split member requires positive meta heldout loss"
        )
    report = train_same_split_member(args, split_seed=split_seed)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

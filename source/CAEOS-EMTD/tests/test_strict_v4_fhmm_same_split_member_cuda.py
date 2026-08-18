from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import train_strict_v4_fhmm_same_split_member_cuda as member


def test_parse_split_seed_keeps_base_training_arguments() -> None:
    split_seed, remaining = member.parse_split_seed(
        [
            "--split-seed",
            "37",
            "--seed",
            "101",
            "--unknown-family",
            "Botnet",
        ]
    )
    assert split_seed == 37
    assert remaining == [
        "--seed",
        "101",
        "--unknown-family",
        "Botnet",
    ]


def test_training_wrapper_separates_split_and_model_seed(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    observed: dict[str, int] = {}

    def fake_split(
        flow_ids: Any,
        families: Any,
        *,
        unknown_family: str,
        seed: int,
    ) -> dict[str, Any]:
        del flow_ids, families, unknown_family
        observed["split_seed"] = seed
        return {"train": [], "validation": [], "test": []}

    def fake_train(args: argparse.Namespace) -> dict[str, Any]:
        member.training_core.stratified_open_set_split(
            None,
            None,
            unknown_family=args.unknown_family,
            seed=args.seed,
        )
        return {
            "schema_version": "base",
            "task": {"seed": args.seed},
            "model": {"name": "FHMM-CAEOS base"},
            "training": {"meta_heldout_loss_weight": 1.0},
            "source": {},
            "claim_boundary": {},
            "manifest_sha256": "base",
        }

    monkeypatch.setattr(
        member.training_core,
        "stratified_open_set_split",
        fake_split,
    )
    monkeypatch.setattr(member.training_core, "train_task", fake_train)
    args = argparse.Namespace(
        unknown_family="Botnet",
        seed=101,
        output_dir=tmp_path,
    )
    report = member.train_same_split_member(args, split_seed=37)

    assert observed["split_seed"] == 37
    assert report["task"] == {
        "unknown_family": "Botnet",
        "split_seed": 37,
        "model_seed": 101,
    }
    assert report["claim_boundary"]["base_training_kernel_modified"] is False
    persisted = json.loads(
        (tmp_path / "metrics.json").read_text(encoding="utf-8")
    )
    assert persisted["manifest_sha256"] == report["manifest_sha256"]


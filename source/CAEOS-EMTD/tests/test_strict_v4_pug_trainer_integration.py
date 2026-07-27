from __future__ import annotations

import sys

from caeos.pseudo_unknown_gated_continuous import PUG_SELECTION_NAME
from train_hybrid_open_set import parse_arguments


def test_trainer_parser_exposes_frozen_pug_selection(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "train_hybrid_open_set.py",
            "--csv",
            "unused.csv",
            "--config",
            "unused.json",
            "--unknown-classes",
            "attack",
            "--risk-selection",
            PUG_SELECTION_NAME,
            "--output-dir",
            "unused-output",
        ],
    )

    args = parse_arguments()

    assert args.risk_selection == PUG_SELECTION_NAME

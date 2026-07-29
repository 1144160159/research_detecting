from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from strict_v4_cicids2017_attack_family import (
    ATTACK_FAMILIES,
    FINE_TO_FAMILY,
    load_canonical,
    materialize_attack_family_cache,
)


def test_frozen_taxonomy_has_seven_attack_families() -> None:
    assert len(ATTACK_FAMILIES) == 7
    assert FINE_TO_FAMILY["Benign"] == "Benign"
    assert FINE_TO_FAMILY["Web Attack - XSS"] == "WebAttack"
    assert FINE_TO_FAMILY["PortScan"] == "Reconnaissance"


def test_materializer_balances_at_family_level(tmp_path: Path) -> None:
    labels = list(FINE_TO_FAMILY)
    rows = []
    for index, label in enumerate(labels):
        for repetition in range(4):
            rows.append(
                {
                    "Label": label,
                    "Feature": index * 10 + repetition,
                    "Flow_Group": f"{label}-{repetition}",
                }
            )
    source = tmp_path / "source.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "label_column": "Label",
                "group_column": "Flow_Group",
                "modalities": {"one": ["Feature"]},
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "family.csv"
    report = materialize_attack_family_cache(
        source_path=source,
        config_path=config,
        output_path=output,
        seed=7,
        maximum_per_family=3,
        chunksize=7,
    )
    frame = pd.read_csv(output)
    assert set(frame["Label"]) == {"Benign", *ATTACK_FAMILIES}
    assert frame.groupby("Label").size().max() == 3
    assert "Fine_Label" in frame.columns
    assert report["claim_boundary"]["fine_subtype_claim_authorized"] is False
    assert load_canonical(output.with_suffix(".csv.json"), "metadata")[
        "output_sha256"
    ] == report["output_sha256"]

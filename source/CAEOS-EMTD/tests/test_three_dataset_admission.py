from __future__ import annotations

import json
from pathlib import Path

from prepare_caeos_unified_multimodal_csv import path_label


def test_fivegad_catalog_and_label_index_use_the_same_relative_member() -> None:
    project_root = Path(__file__).resolve().parents[1]
    catalog = json.loads(
        (project_root / "configs" / "unified_multimodal_v5_split_class.datasets.json")
        .read_text(encoding="utf-8")
    )
    dataset = next(item for item in catalog["datasets"] if item["id"] == "5gad_2022")

    assert dataset["source_root"].endswith("/5GAD-2022")
    assert dataset["include_globs"] == [
        "repository/Normal-2UE/*.pcapng",
        "repository/Attacks/*/Attacks_*.pcapng",
    ]
    benign = path_label(dataset, "repository/Normal-2UE/normal_1.pcapng")
    attack = path_label(
        dataset,
        "repository/Attacks/CrashNRF/Attacks_CrashNRF.pcapng",
    )
    assert (benign.fine_label, benign.family_label, benign.binary_label) == (
        "Benign",
        "Benign",
        0,
    )
    assert (attack.fine_label, attack.family_label, attack.binary_label) == (
        "CrashNRF",
        "DoS",
        1,
    )

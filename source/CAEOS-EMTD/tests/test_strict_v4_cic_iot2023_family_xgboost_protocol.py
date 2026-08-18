from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from create_strict_v4_cic_iot2023_family_xgboost_protocol import (
    build_protocol,
)
from strict_v4_cic_iot2023_attack_family import FINE_TO_FAMILY


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_protocol_freezes_all_cic_iot2023_attack_families(
    tmp_path: Path,
) -> None:
    cache = tmp_path / "cache.csv"
    pd.DataFrame(
        {
            "Attack": sorted(FINE_TO_FAMILY),
            "CaptureGroup": [
                f"group-{index}" for index in range(len(FINE_TO_FAMILY))
            ],
        }
    ).to_csv(cache, index=False)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "label_column": "Attack",
                "group_column": "CaptureGroup",
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        project_root=PROJECT_ROOT,
        cache_csv=cache,
        config=config,
        expected_rows=len(FINE_TO_FAMILY),
        maximum_per_fine_class=1,
        development_seed=283,
        classification_level="family",
        result_root=tmp_path / "results",
        run_root=tmp_path / "runs",
        xgboost_root=tmp_path / "xgboost",
        maximum_parallel_tasks=8,
    )

    protocol = build_protocol(args)

    assert protocol["state"] == "frozen_before_development_effects"
    assert protocol["taxonomy"] == "cic_iot2023"
    assert protocol["classification_level"] == "family"
    assert protocol["expected_task_count"] == 8
    assert protocol["execution"]["backend"] == "xgboost_cuda"
    assert protocol["evaluation"]["safety_target"][
        "unknown_attack_alert_recall_minimum"
    ] == 0.95
    assert protocol["claim_boundary"][
        "paper_multimodal_claim_not_established_by_this_branch"
    ] is True

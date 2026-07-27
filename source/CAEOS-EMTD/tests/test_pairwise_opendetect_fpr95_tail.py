from __future__ import annotations

import numpy as np

from audit_strict_v4_pairwise_opendetect_fpr95_tail import (
    fpr95_details,
    plateau_stats,
    summarize_rows,
)


def test_minimum_plateau_explains_fpr95_one() -> None:
    known = np.concatenate([np.zeros(80), np.linspace(0.1, 0.9, 20)])
    unknown = np.concatenate([np.zeros(6), np.linspace(0.2, 1.0, 94)])
    risk = np.concatenate([known, unknown])
    target = np.concatenate(
        [np.zeros(len(known), dtype=bool), np.ones(len(unknown), dtype=bool)]
    )

    details = plateau_stats(risk, target)

    assert details["fpr95"] == 1.0
    assert details["unknown_at_minimum_fraction"] == 0.06
    assert details["known_at_minimum_fraction"] == 0.8
    assert details["minimum_plateau_explains_fpr95_one"] is True


def test_less_than_five_percent_unknown_at_floor_does_not_force_one() -> None:
    known = np.concatenate([np.zeros(80), np.linspace(0.1, 0.9, 20)])
    unknown = np.concatenate([np.zeros(4), np.linspace(0.2, 1.0, 96)])
    risk = np.concatenate([known, unknown])
    target = np.concatenate(
        [np.zeros(len(known), dtype=bool), np.ones(len(unknown), dtype=bool)]
    )

    details = plateau_stats(risk, target)

    assert details["fpr95"] < 1.0
    assert details["minimum_plateau_explains_fpr95_one"] is False


def test_fpr95_matches_first_roc_point_at_or_above_target() -> None:
    target = np.asarray([0, 0, 0, 1, 1, 1], dtype=np.int64)
    risk = np.asarray([0.1, 0.2, 0.8, 0.3, 0.7, 0.9], dtype=np.float64)

    details = fpr95_details(target, risk)

    assert details["fpr95"] == 1.0 / 3.0
    assert details["tpr"] == 1.0


def test_summary_orients_lower_fpr95_as_pairwise_win() -> None:
    rows = [
        {
            "pairwise_fpr95": 0.2,
            "opendetect_fpr95": 0.4,
            "pairwise_minus_opendetect_fpr95": -0.2,
            "outcome_vs_opendetect": "win",
            "selected_risk": "cauchy_modality_support_union",
            "pairwise_raw_plateau": {
                "minimum_is_exact_zero": True,
            },
            "pairwise_plateau": {
                "minimum_plateau_explains_fpr95_one": False,
                "minimum_is_exact_zero": True,
            },
        },
        {
            "pairwise_fpr95": 1.0,
            "opendetect_fpr95": 0.1,
            "pairwise_minus_opendetect_fpr95": 0.9,
            "outcome_vs_opendetect": "loss",
            "selected_risk": "pseudo_unknown_learned_blend",
            "pairwise_raw_plateau": {
                "minimum_is_exact_zero": True,
            },
            "pairwise_plateau": {
                "minimum_plateau_explains_fpr95_one": True,
                "minimum_is_exact_zero": True,
            },
        },
    ]

    summary = summarize_rows(rows)

    assert summary["scenario_count"] == 2
    assert summary["pairwise_win_count"] == 1
    assert summary["pairwise_loss_count"] == 1
    assert summary["minimum_plateau_explains_fpr95_one_count"] == 1
    assert summary["base_bonferroni_zero_floor_count"] == 1

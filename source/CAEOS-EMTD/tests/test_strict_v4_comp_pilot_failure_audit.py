from __future__ import annotations

import numpy as np

from audit_strict_v4_comp_pilot_failure import (
    average_rank_auc,
    plateau_features,
    screen_known_only_gates,
)


def test_average_rank_auc_handles_order_and_ties() -> None:
    labels = np.array([0, 0, 1, 1], dtype=bool)

    assert average_rank_auc(labels, np.array([0.0, 1.0, 2.0, 3.0])) == 1.0
    assert average_rank_auc(labels, np.array([3.0, 2.0, 1.0, 0.0])) == 0.0
    assert average_rank_auc(labels, np.ones(4)) == 0.5


def test_plateau_features_are_known_validation_only() -> None:
    features = plateau_features(
        np.array([0.0, 0.0, 0.4, 0.9]),
        np.array([0.1, 0.3, 0.4, 0.9]),
    )

    assert features["validation_reference_zero_fraction"] == 0.5
    assert features["validation_plateau_candidate_mean"] == 0.2
    assert np.isclose(
        features["validation_plateau_candidate_std"], 0.1
    )


def test_gate_screen_finds_scenario_consistent_safe_route() -> None:
    rows = []
    for scenario, value, deltas in (
        (
            "safe",
            0.8,
            {
                "unknown_aupr": 0.01,
                "unknown_auroc": 0.03,
                "unknown_fpr95": 0.18,
                "oscr": 0.02,
            },
        ),
        (
            "unsafe",
            0.2,
            {
                "unknown_aupr": -0.08,
                "unknown_auroc": 0.01,
                "unknown_fpr95": 0.08,
                "oscr": 0.01,
            },
        ),
    ):
        for seed in (1, 2, 3):
            rows.append(
                {
                    "scenario": scenario,
                    "seed": seed,
                    "validation_features": {
                        "validation_reference_zero_fraction": value,
                        "validation_plateau_candidate_mean": value,
                        "validation_plateau_candidate_std": value,
                        "validation_plateau_candidate_q90": value,
                        "validation_plateau_candidate_iqr": value,
                    },
                    "oriented_delta": deltas,
                }
            )

    screens = screen_known_only_gates(rows)
    feasible = [item for item in screens if item["development_feasible"]]

    assert feasible
    assert feasible[0]["admitted_scenarios"] == ["safe"]
    assert feasible[0]["scenario_consistent_on_three_seeds"] is True

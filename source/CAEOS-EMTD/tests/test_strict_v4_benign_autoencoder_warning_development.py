from __future__ import annotations

import numpy as np

from create_strict_v4_benign_autoencoder_warning_development_protocol import (
    ALERT_CANDIDATES,
)
from evaluate_strict_v4_benign_autoencoder_warning_development import (
    calibrated_prediction,
    evaluate_candidate,
    selection_key,
)


def test_alert_candidates_have_unique_names_and_bounded_union_budgets() -> None:
    names = [candidate["name"] for candidate in ALERT_CANDIDATES]
    assert len(names) == len(set(names))
    for candidate in ALERT_CANDIDATES:
        primary = candidate["primary_alert_budget"]
        rescue = candidate["autoencoder_rescue_budget"]
        assert 0.0 <= primary < 0.05
        assert 0.0 <= rescue < 0.05
        assert primary + rescue <= 0.044 + 1e-12


def test_zero_budget_produces_no_alerts_and_no_threshold() -> None:
    predicted, threshold = calibrated_prediction(
        np.asarray([0.1, 0.2, 0.9]),
        np.asarray([0, 0, 1]),
        benign_index=0,
        budget=0.0,
    )
    assert not predicted.any()
    assert threshold is None


def test_autoencoder_rescues_unknown_without_alerting_benign() -> None:
    arrays = {
        "benign_index": 0,
        "validation_labels": np.asarray([0, 0, 1, 1]),
        "test_labels": np.asarray([0, 1, -1]),
        "test_unknown": np.asarray([False, False, True]),
        "validation_type_prediction": np.asarray([1, 1, 1, 1]),
        "type_prediction": np.asarray([1, 1, 1]),
        "xgboost_validation_attack": np.asarray([0.01, 0.02, 0.8, 0.9]),
        "xgboost_test_attack": np.asarray([0.01, 0.95, 0.02]),
        "validation_uncertainty_tail": np.asarray([0.1, 0.2, 0.7, 0.8]),
        "test_uncertainty_tail": np.asarray([0.1, 0.2, 1.0]),
        "risk_tails": {
            "knn": {
                "validation_attack": np.asarray([0.1, 0.2, 0.7, 0.8]),
                "test_attack": np.asarray([0.1, 0.2, 1.0]),
            }
        },
    }
    result = evaluate_candidate(
        arrays=arrays,
        validation_autoencoder=np.asarray([0.01, 0.02, 0.2, 0.3]),
        test_autoencoder=np.asarray([0.01, 0.02, 1.0]),
        candidate={
            "name": "synthetic_union",
            "primary_alert_budget": 0.25,
            "autoencoder_rescue_budget": 0.25,
        },
        open_risk_name="knn",
        open_budget=0.5,
    )
    metrics = result["metrics"]
    assert metrics["alert_accuracy"] == 1.0
    assert metrics["attack_recall"] == 1.0
    assert metrics["benign_fpr"] == 0.0
    assert metrics["unknown_attack_alert_recall"] == 1.0
    assert metrics["unknown_label_recall"] == 1.0


def test_selection_prefers_fpr_feasible_candidate_before_unknown_recall() -> None:
    def record(*, unknown_recall: float, benign_fpr: float) -> dict:
        metrics = {
            "alert_accuracy": 0.97,
            "alert_precision": 0.99,
            "attack_recall": 0.97,
            "benign_fpr": benign_fpr,
            "known_attack_type_accuracy": 0.96,
            "unknown_attack_alert_recall": unknown_recall,
            "unknown_label_recall": 0.8,
        }
        engineering = {"passed": False}
        return {
            "overall": {
                "metrics": metrics,
                "engineering": engineering,
            },
            "per_seed": {
                "1": {
                    "metrics": metrics,
                    "engineering": engineering,
                }
            },
        }

    infeasible = record(unknown_recall=0.99, benign_fpr=0.051)
    feasible = record(unknown_recall=0.94, benign_fpr=0.049)
    assert selection_key(feasible) > selection_key(infeasible)

from __future__ import annotations

import numpy as np

from analyze_strict_v4_fine_probability_rescue import (
    benign_threshold,
    evaluate_task,
    probability_scores,
)


def test_probability_scores_are_finite() -> None:
    probability = np.asarray([[0.9, 0.1], [0.5, 0.5]])
    scores = probability_scores(probability)

    assert set(scores) == {
        "uncertainty",
        "normalized_entropy",
        "top2_closeness",
    }
    assert all(np.isfinite(value).all() for value in scores.values())
    assert scores["uncertainty"][1] > scores["uncertainty"][0]


def test_benign_threshold_respects_zero_budget() -> None:
    assert np.isinf(benign_threshold(np.asarray([0.1, 0.2]), 0.0))


def test_rescue_alerts_uncertain_unknown() -> None:
    result = evaluate_task(
        validation_probability=np.asarray(
            [[0.99, 0.01], [0.98, 0.02], [0.1, 0.9]]
        ),
        validation_labels=np.asarray([0, 0, 1]),
        test_probability=np.asarray(
            [[0.99, 0.01], [0.1, 0.9], [0.5, 0.5]]
        ),
        test_labels=np.asarray([0, 1, -1]),
        test_unknown=np.asarray([False, False, True]),
        primary_budget=0.25,
        rescue_name="uncertainty",
        rescue_budget=0.25,
    )

    assert result["metrics"]["unknown_attack_alert_recall"] == 1.0
    assert result["metrics"]["benign_fpr"] == 0.0

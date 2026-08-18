from __future__ import annotations

import numpy as np
import pytest

from strict_v4_open_set_metric_contract_v2 import (
    evaluate_open_set_metric_contract,
    exact_oscr_area,
    fpr_known_at_95_unknown_tpr,
)


def perfect_arrays() -> dict[str, np.ndarray]:
    return {
        "labels": np.asarray([0, 1, 0, 1, -1, -1]),
        "known_prediction": np.asarray([0, 1, 0, 1, 0, 1]),
        "is_unknown": np.asarray(
            [False, False, False, False, True, True]
        ),
        "unknown_risk": np.asarray([0.10, 0.20, 0.15, 0.30, 0.80, 0.90]),
        "rejected_as_unknown": np.asarray(
            [False, False, False, False, True, True]
        ),
    }


def test_perfect_contract_separates_three_metric_layers() -> None:
    arrays = perfect_arrays()
    report = evaluate_open_set_metric_contract(
        **arrays,
        class_names=["Benign", "Attack"],
    )
    assert report["closed_set_known"]["known_macro_f1"] == 1.0
    assert report["closed_set_known"]["known_balanced_accuracy"] == 1.0
    assert report["unknown_detection"]["unknown_auroc_out"] == 1.0
    assert report["unknown_detection"]["unknown_auroc"] == 1.0
    assert report["unknown_detection"]["unknown_aupr_out"] == 1.0
    assert report["unknown_detection"]["fpr_known_at_95_unknown_tpr"] == 0.0
    assert report["unknown_detection"]["unknown_f1_at_frozen_threshold"] == 1.0
    assert report["joint_open_set"]["oscr_exact_v2"] == 1.0
    assert report["calibration"]["available"] is False


def test_oscr_couples_correct_known_classification_and_unknown_rejection() -> None:
    arrays = perfect_arrays()
    wrong_prediction = 1 - arrays["known_prediction"]
    assert (
        exact_oscr_area(
            arrays["labels"],
            wrong_prediction,
            arrays["is_unknown"],
            arrays["unknown_risk"],
        )
        == 0.0
    )


def test_fpr95_uses_unknown_as_positive_class() -> None:
    unknown = np.asarray([False, False, True, True])
    risk = np.asarray([0.1, 0.9, 0.8, 1.0])
    assert fpr_known_at_95_unknown_tpr(unknown, risk) == 0.5


def test_known_only_probability_calibration_is_explicit() -> None:
    arrays = perfect_arrays()
    probability = np.asarray(
        [
            [0.9, 0.1],
            [0.1, 0.9],
            [0.8, 0.2],
            [0.2, 0.8],
            [0.5, 0.5],
            [0.5, 0.5],
        ]
    )
    report = evaluate_open_set_metric_contract(
        **arrays,
        known_class_probabilities=probability,
    )
    calibration = report["calibration"]
    assert calibration["available"] is True
    assert calibration["scope"] == "known_test_only"
    assert calibration["negative_log_likelihood"] > 0.0
    assert calibration["brier_score"] > 0.0


def test_rejects_single_population_evaluation() -> None:
    arrays = perfect_arrays()
    arrays["is_unknown"][:] = False
    with pytest.raises(ValueError, match="known and unknown"):
        evaluate_open_set_metric_contract(**arrays)


def test_numpy_metrics_match_sklearn_reference_when_available() -> None:
    metrics = pytest.importorskip("sklearn.metrics")
    arrays = {
        "labels": np.asarray([0, 0, 1, 1, 2, 2, -1, -1, -1]),
        "known_prediction": np.asarray([0, 1, 1, 1, 2, 0, 0, 1, 2]),
        "is_unknown": np.asarray(
            [False, False, False, False, False, False, True, True, True]
        ),
        "unknown_risk": np.asarray(
            [0.1, 0.4, 0.2, 0.5, 0.3, 0.5, 0.5, 0.8, 0.9]
        ),
        "rejected_as_unknown": np.asarray(
            [False, False, False, True, False, True, True, True, True]
        ),
    }
    report = evaluate_open_set_metric_contract(**arrays)
    unknown_target = arrays["is_unknown"].astype(np.int64)
    known = ~arrays["is_unknown"]
    assert report["unknown_detection"]["unknown_auroc_out"] == pytest.approx(
        metrics.roc_auc_score(unknown_target, arrays["unknown_risk"])
    )
    assert report["unknown_detection"]["unknown_aupr_out"] == pytest.approx(
        metrics.average_precision_score(
            unknown_target,
            arrays["unknown_risk"],
        )
    )
    assert report["closed_set_known"]["known_macro_f1"] == pytest.approx(
        metrics.f1_score(
            arrays["labels"][known],
            arrays["known_prediction"][known],
            average="macro",
        )
    )
    assert report["closed_set_known"][
        "known_balanced_accuracy"
    ] == pytest.approx(
        metrics.balanced_accuracy_score(
            arrays["labels"][known],
            arrays["known_prediction"][known],
        )
    )

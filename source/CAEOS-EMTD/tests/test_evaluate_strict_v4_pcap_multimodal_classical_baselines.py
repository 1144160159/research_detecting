from __future__ import annotations

import numpy as np

from evaluate_strict_v4_pcap_multimodal_classical_baselines import (
    baseline_records,
    evaluate_risk,
    known_only_threshold,
)


def test_known_only_threshold_uses_requested_acceptance_quantile() -> None:
    values = np.arange(20, dtype=np.float64)
    assert known_only_threshold(values, 0.95) == 19.0


def test_evaluate_risk_reports_perfect_unknown_ranking() -> None:
    result = evaluate_risk(
        validation_risk=np.asarray([0.1, 0.2, 0.3, 0.4]),
        test_risk=np.asarray([0.1, 0.2, 0.8, 0.9]),
        test_prediction=np.asarray([0, 1, 0, 1]),
        test_labels=np.asarray([0, 1, -1, -1]),
        is_unknown=np.asarray([False, False, True, True]),
    )

    assert result["known_accuracy"] == 1.0
    assert result["unknown_auroc"] == 1.0
    assert result["unknown_aupr"] == 1.0
    assert result["unknown_fpr95"] == 0.0
    assert result["unknown_rejection_rate"] == 1.0


def test_baseline_records_include_four_frozen_methods() -> None:
    train_embedding = np.asarray(
        [
            [-2.0, -1.0],
            [-1.8, -1.1],
            [-2.1, -0.9],
            [2.0, 1.0],
            [1.8, 1.1],
            [2.1, 0.9],
        ],
        dtype=np.float32,
    )
    train_logits = np.asarray(
        [
            [4.0, 0.1],
            [3.8, 0.2],
            [4.2, 0.0],
            [0.1, 4.0],
            [0.2, 3.8],
            [0.0, 4.2],
        ],
        dtype=np.float32,
    )
    train_belief = np.exp(train_logits)
    train_belief /= train_belief.sum(axis=1, keepdims=True)
    validation_embedding = train_embedding[:4]
    validation_logits = train_logits[:4]
    validation_belief = train_belief[:4]
    test_embedding = np.asarray(
        [[-2.0, -1.0], [2.0, 1.0], [0.0, 4.0], [0.0, -4.0]],
        dtype=np.float32,
    )
    test_logits = np.asarray(
        [[4.0, 0.1], [0.1, 4.0], [0.2, 0.2], [0.3, 0.3]],
        dtype=np.float32,
    )
    test_belief = np.exp(test_logits)
    test_belief /= test_belief.sum(axis=1, keepdims=True)
    arrays = {
        "baseline_train_embedding": train_embedding,
        "baseline_train_log_evidence": train_logits,
        "baseline_train_belief": train_belief,
        "baseline_train_label": np.asarray([0, 0, 0, 1, 1, 1]),
        "baseline_validation_embedding": validation_embedding,
        "baseline_validation_log_evidence": validation_logits,
        "baseline_validation_belief": validation_belief,
        "baseline_validation_label": np.asarray([0, 0, 0, 1]),
        "baseline_test_embedding": test_embedding,
        "baseline_test_log_evidence": test_logits,
        "baseline_test_belief": test_belief,
        "baseline_test_label": np.asarray([0, 1, -1, -1]),
        "baseline_test_is_unknown": np.asarray(
            [False, False, True, True]
        ),
    }

    result = baseline_records(arrays)

    assert set(result) == {"MSP", "Energy", "OpenMax", "Mahalanobis++"}
    assert all(
        0.0 <= record["unknown_auroc"] <= 1.0
        for record in result.values()
    )

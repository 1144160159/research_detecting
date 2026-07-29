import numpy as np

from train_strict_v4_xgboost_warning_task import operational_metrics


def test_xgboost_warning_metrics_keep_unknown_label_boundary() -> None:
    probability = np.array(
        [
            [0.99, 0.01, 0.00],
            [0.05, 0.90, 0.05],
            [0.10, 0.20, 0.70],
        ],
        dtype=np.float64,
    )
    result = operational_metrics(
        test_probability=probability,
        test_labels=np.array([0, 1, 2], dtype=np.int64),
        test_unknown=np.array([False, False, True]),
        benign_index=0,
        alert_threshold=0.5,
    )

    assert result["alert_accuracy"] == 1.0
    assert result["benign_fpr"] == 0.0
    assert result["known_attack_type_accuracy"] == 1.0
    assert result["unknown_attack_alert_recall"] == 1.0
    assert result["unknown_attack_recall"] == 0.0
    assert result["unknown_label_precision"] == 0.0

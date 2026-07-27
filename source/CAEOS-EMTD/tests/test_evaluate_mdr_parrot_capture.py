import numpy as np
import pytest

from evaluate_mdr_parrot_capture import batched_predictions, benign_metrics


def test_benign_metrics_separates_false_alert_reject_and_known_assignment():
    value = benign_metrics(
        prediction=np.asarray([0, 1, 1, 0]),
        risk=np.asarray([0.2, 0.2, 0.8, 0.8]),
        threshold=0.5,
        benign_index=0,
    )
    assert value["false_alert_rate"] == pytest.approx(0.5)
    assert value["known_attack_assignment_rate"] == pytest.approx(0.25)
    assert value["reject_rate"] == pytest.approx(0.5)
    assert value["operational_intervention_rate"] == pytest.approx(0.75)


def test_benign_metrics_rejects_nonpositive_threshold():
    with pytest.raises(ValueError, match="invalid"):
        benign_metrics(
            prediction=np.asarray([0]),
            risk=np.asarray([0.2]),
            threshold=0.0,
            benign_index=0,
        )


def test_benign_metrics_accepts_per_row_frozen_thresholds():
    value = benign_metrics(
        prediction=np.asarray([0, 1]),
        risk=np.asarray([0.2, 0.8]),
        threshold=np.asarray([0.5, 0.7]),
        benign_index=0,
    )
    assert value["reject_rate"] == pytest.approx(0.5)


def test_batched_predictions_preserves_row_order():
    def method(views):
        values = np.asarray(views[0]).ravel()
        return {
            "prediction": values.astype(int),
            "risk": values.astype(float) / 10.0,
        }

    output = batched_predictions(
        method, [np.arange(7).reshape(-1, 1)], batch_size=3
    )
    assert output["prediction"].tolist() == list(range(7))

from __future__ import annotations

import numpy as np

from caeos.conformal_safe_routing import (
    KnownValidationMaxRoutingCalibration,
)
from caeos.csr_runtime import CSRRuntime


class FakeRuntime:
    def __init__(self, probability, risk, conflict):
        self.probability = np.asarray(probability, dtype=np.float64)
        self.risk = np.asarray(risk, dtype=np.float64)
        self.evidence = {
            "final_probability": self.probability,
            "local_conflict": np.asarray(conflict, dtype=np.float64),
        }

    def predict(self, raw_views):
        return {
            "probability": self.probability,
            "prediction": self.probability.argmax(axis=1),
            "risk": self.risk,
        }


class DummyCSRRuntime(CSRRuntime):
    @staticmethod
    def _model_evidence(runtime, raw_views):
        return runtime.evidence

    def missing_mask(self, raw_views):
        return np.asarray(raw_views[0], dtype=bool)

    def _missing_aware_risk(self, raw_views, missing, fallback):
        return np.asarray(fallback, dtype=np.float64) + 0.1


def test_runtime_never_replaces_clean_classification() -> None:
    calibration = KnownValidationMaxRoutingCalibration.fit(
        {
            "final_probability": np.asarray([[0.9, 0.1], [0.8, 0.2]]),
            "local_conflict": np.asarray([[0.1], [0.2]]),
        },
        {
            "final_probability": np.asarray([[0.8, 0.2], [0.7, 0.3]]),
            "local_conflict": np.asarray([[0.1], [0.2]]),
        },
        np.asarray([0.1, 0.9]),
        np.asarray([0.1, 0.9]),
        np.asarray([0.1, 0.9]),
    )
    clean = FakeRuntime(
        [[0.9, 0.1], [0.8, 0.2]], [0.2, 0.4], [[0.5], [0.1]]
    )
    robust = FakeRuntime(
        [[0.1, 0.9], [0.2, 0.8]], [0.8, 0.1], [[0.5], [0.1]]
    )
    runtime = DummyCSRRuntime(
        clean_runtime=clean,
        robust_runtime=robust,
        health_calibration=calibration,
        missing_fraction_thresholds=np.asarray([0.0]),
        training_feature_scales=[np.asarray([1.0])],
        clean_threshold=0.5,
        augmentation_weight=0.5,
        training_seed=607,
        augmentation_seed=613,
    )
    result = runtime.predict([np.asarray([[False], [True]])])
    assert result["active"].tolist() == [True, True]
    np.testing.assert_array_equal(result["prediction"], [0, 0])
    np.testing.assert_array_equal(result["probability"], clean.probability)
    assert np.all(result["risk"] >= clean.risk)
    assert runtime.evidence()["algorithm"] == "csr_caeos_v1"

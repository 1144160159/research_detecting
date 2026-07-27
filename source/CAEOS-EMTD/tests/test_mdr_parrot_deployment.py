import numpy as np
import pandas as pd
import pytest

from caeos.mdr_deployment import MDRDeploymentBundle
from capture_mdr_parrot_deployment_bundle import source_benign_metrics


class Runtime:
    clean_threshold = 0.5

    def predict(self, views):
        values = np.asarray(views[0])[:, 0]
        risk = np.asarray([0.2, 0.8])[: len(values)]
        probability = np.column_stack(
            [np.full(len(values), 0.7), np.full(len(values), 0.3)]
        )
        return {
            "prediction": np.asarray([0, 1])[: len(values)],
            "probability": probability,
            "risk": risk,
            "threshold": np.full(len(values), 0.5),
        }

    def evidence(self):
        return {
            "schema_version": "strict_v4_mdr_caeos_runtime_v1",
            "augmentation_weight": 0.25,
        }


def bundle():
    return MDRDeploymentBundle(
        runtime=Runtime(),
        modality_names=("volume", "timing"),
        modalities={"volume": ("a", "b"), "timing": ("c",)},
        processor_states={
            "volume": {
                "median": [1.0, 2.0],
                "mean": [1.0, 2.0],
                "std": [2.0, 4.0],
            },
            "timing": {
                "median": [3.0],
                "mean": [3.0],
                "std": [2.0],
            },
        },
        class_names=("Benign", "Attack"),
        benign_index=0,
        source_config_sha256="a" * 64,
        source_split_fingerprint="b" * 64,
    )


def test_mdr_deployment_transforms_raw_features_and_predicts():
    value = bundle()
    frame = pd.DataFrame(
        {
            "a": [1.0, 3.0],
            "b": [np.nan, 6.0],
            "c": [3.0, 5.0],
        }
    )
    views, quality = value.transform_frame(frame)
    np.testing.assert_allclose(views[0], [[0.0, 0.0], [1.0, 1.0]])
    np.testing.assert_allclose(views[1], [[0.0], [1.0]])
    assert quality.shape == (2, 2)
    output = value.predict_frame(frame)
    assert output["prediction"].tolist() == [0, 1]
    assert output["rejected"].tolist() == [False, True]


def test_mdr_deployment_rejects_missing_feature():
    with pytest.raises(ValueError, match="missing columns"):
        bundle().transform_frame(pd.DataFrame({"a": [1.0]}))


def test_source_benign_metrics_separates_reject_and_known_assignment():
    metrics = source_benign_metrics(
        {
            "prediction": np.asarray([0, 1]),
            "risk": np.asarray([0.2, 0.8]),
            "threshold": np.asarray([0.5, 0.5]),
        },
        benign_index=0,
    )
    assert metrics["false_alert_rate"] == pytest.approx(0.5)
    assert metrics["known_attack_assignment_rate"] == pytest.approx(0.0)
    assert metrics["reject_rate"] == pytest.approx(0.5)

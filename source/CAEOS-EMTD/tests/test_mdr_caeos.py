from __future__ import annotations

import numpy as np

from caeos.mdr_fusion import KnownOnlyHealthCalibration, quantile_map
from caeos.structured_robust import (
    DEFAULT_FAMILY_SEVERITIES,
    StructuredRobustHybridClassifier,
    build_weighted_structured_training,
)


def test_structured_training_is_deterministic_and_label_aligned() -> None:
    rng = np.random.default_rng(5)
    labels = np.repeat(np.arange(3), 20)
    views = [rng.normal(size=(60, 4)), rng.normal(size=(60, 3))]
    first = build_weighted_structured_training(
        views,
        labels,
        augmentation_weight=0.25,
        sample_fraction=0.25,
        family_severities=DEFAULT_FAMILY_SEVERITIES,
        seed=331,
    )
    second = build_weighted_structured_training(
        views,
        labels,
        augmentation_weight=0.25,
        sample_fraction=0.25,
        family_severities=DEFAULT_FAMILY_SEVERITIES,
        seed=331,
    )
    for left, right in zip(first[0], second[0]):
        np.testing.assert_array_equal(left, right)
        assert len(left) == len(first[1]) == len(first[2])
    np.testing.assert_array_equal(first[1], second[1])
    np.testing.assert_array_equal(first[2], second[2])
    assert first[3]["families"] == list(DEFAULT_FAMILY_SEVERITIES)
    assert first[3]["unknown_or_test_labels_used"] is False
    assert first[3]["feature_shuffle_is_within_known_class"] is True


def test_quantile_map_preserves_order_and_target_scale() -> None:
    values = quantile_map(
        np.asarray([0.0, 1.0, 2.0, 3.0]),
        np.asarray([10.0, 20.0, 30.0, 40.0]),
        np.asarray([-1.0, 0.5, 2.5, 5.0]),
    )
    assert np.all(np.diff(values) >= 0.0)
    assert values[0] == 10.0
    assert values[-1] == 40.0


def test_health_gate_is_exact_on_inactive_samples_and_routes_missing() -> None:
    clean_validation = {
        "final_probability": np.asarray([[0.9, 0.1], [0.8, 0.2], [0.7, 0.3]]),
        "local_conflict": np.asarray([[0.01, 0.02], [0.02, 0.03], [0.03, 0.04]]),
    }
    robust_validation = {
        "final_probability": np.asarray([[0.88, 0.12], [0.79, 0.21], [0.69, 0.31]]),
        "local_conflict": clean_validation["local_conflict"],
    }
    calibration = KnownOnlyHealthCalibration.fit(
        clean_validation,
        robust_validation,
        np.asarray([0.1, 0.2, 0.3]),
        np.asarray([1.0, 2.0, 3.0]),
        np.asarray([4.0, 5.0, 6.0]),
        quantile=0.9,
    )
    clean_test = {
        "final_probability": np.asarray([[0.9, 0.1], [0.9, 0.1]]),
        "local_conflict": np.asarray([[0.0, 0.0], [0.0, 0.0]]),
    }
    robust_test = {
        "final_probability": np.asarray([[0.895, 0.105], [0.1, 0.9]]),
        "local_conflict": clean_test["local_conflict"],
    }
    output = calibration.apply(
        clean_test,
        robust_test,
        np.asarray([0.11, 0.12]),
        np.asarray([1.1, 1.2]),
        np.asarray([4.1, 4.2]),
        np.asarray([False, True]),
    )
    assert output["active"].tolist() == [False, True]
    assert output["prediction"].tolist() == [0, 1]
    assert output["risk"][0] == 0.11
    assert calibration.evidence()["unknown_or_test_labels_used"] is False


def test_structured_classifier_fits_and_predicts_with_finite_probabilities() -> None:
    rng = np.random.default_rng(17)
    train_labels = np.repeat(np.arange(3), 20)
    validation_labels = np.repeat(np.arange(3), 6)
    train_views = [
        rng.normal(size=(60, 4)) + train_labels[:, None],
        rng.normal(size=(60, 3)) + train_labels[:, None],
    ]
    validation_views = [
        rng.normal(size=(18, 4)) + validation_labels[:, None],
        rng.normal(size=(18, 3)) + validation_labels[:, None],
    ]
    model = StructuredRobustHybridClassifier(
        estimators=5,
        jobs=1,
        seed=331,
        structured_augmentation_weight=0.25,
        structured_sample_fraction=0.25,
        structured_augmentation_seed=331,
    )
    model.fit(
        train_views,
        train_labels,
        validation_views,
        validation_labels,
    )
    probability = model.predict_proba(validation_views)
    assert probability.shape == (18, 3)
    assert np.isfinite(probability).all()
    np.testing.assert_allclose(probability.sum(axis=1), 1.0)
    metadata = model.validation_scores["structured_training_augmentation"]
    assert metadata["enabled"] is True
    assert metadata["unknown_or_test_labels_used"] is False

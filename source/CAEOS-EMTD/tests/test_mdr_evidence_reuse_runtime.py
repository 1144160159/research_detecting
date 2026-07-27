from types import SimpleNamespace

import joblib
import numpy as np

from caeos.mdr_evidence_reuse_runtime import MDREvidenceReuseRuntime
from caeos.mdr_fusion import KnownOnlyHealthCalibration
from caeos.mdr_runtime import MDRRuntime
from caeos.pairwise_runtime import PairwiseRuntime


class ProbabilityModel:
    def predict_proba(self, values):
        values = np.asarray(values, dtype=np.float64)
        score = 1.0 / (1.0 + np.exp(-values.mean(axis=1)))
        return np.column_stack([score, 1.0 - score])


class EvidenceModel:
    def __init__(self, offset):
        self.offset = float(offset)
        self.calls = 0
        self.random_forest = ProbabilityModel()
        self.extra_trees = ProbabilityModel()

    @staticmethod
    def _global_values(views):
        return np.concatenate(views, axis=1)

    def predict_with_evidence(self, views):
        self.calls += 1
        values = self._global_values(views)
        score = 1.0 / (
            1.0 + np.exp(-(values.mean(axis=1) + self.offset))
        )
        probability = np.column_stack([score, 1.0 - score])
        local = np.column_stack(
            [
                np.abs(view.mean(axis=1) - values.mean(axis=1))
                for view in views
            ]
        )
        return {
            "final_probability": probability,
            "local_conflict": local,
            "global_conflict": local.max(axis=1),
        }


class ScoreModel:
    def __init__(self, offset=0.0):
        self.offset = float(offset)

    def score(self, values, prediction=None):
        values = np.asarray(values, dtype=np.float64)
        result = np.mean(np.abs(values), axis=1) + self.offset
        if prediction is not None:
            result = result + 0.01 * np.asarray(prediction)
        return result


class IdentityNormalizer:
    @staticmethod
    def transform(components):
        return {name: np.asarray(value) for name, value in components.items()}


def pairwise(offset):
    component_names = {
        "uncertainty",
        "inverse_belief",
        "inverse_margin",
        "conflict",
        "tree_disagreement",
        "distance",
        "knn_distance",
        "knn_view_0",
        "knn_view_1",
        "class_knn_distance",
        "lof_density",
    }
    reference = {
        name: np.linspace(-1.0, 10.0, 101) for name in component_names
    }
    return PairwiseRuntime(
        model=EvidenceModel(offset),
        foss_model=None,
        distance_model=ScoreModel(0.1),
        knn_model=ScoreModel(0.2),
        view_knn_models=[ScoreModel(0.3), ScoreModel(0.4)],
        class_knn_model=ScoreModel(0.5),
        lof_model=ScoreModel(0.6),
        normalizer=IdentityNormalizer(),
        tail_calibrator=SimpleNamespace(reference=reference),
        selected_risk="cauchy_modality_support_union",
        learned_weights={},
        validation_raw_learned=np.asarray([]),
        selected_alpha=0.0,
        foss_structural_view=False,
        foss_structural_view_mode="none",
        foss_structural_view_scope="full",
    )


def runtime():
    clean = pairwise(0.0)
    robust = pairwise(0.2)
    calibration = KnownOnlyHealthCalibration(
        conflict_threshold=0.2,
        disagreement_threshold=0.01,
        quantile=0.99,
        clean_risk_reference=np.linspace(0.0, 1.0, 20),
        robust_risk_reference=np.linspace(0.0, 1.0, 20),
        missing_risk_reference=np.linspace(0.0, 1.0, 20),
    )
    return MDRRuntime(
        clean_runtime=clean,
        robust_runtime=robust,
        health_calibration=calibration,
        missing_fraction_thresholds=np.asarray([0.8, 0.8]),
        training_feature_scales=[
            np.ones(2, dtype=np.float64),
            np.ones(3, dtype=np.float64),
        ],
        clean_threshold=0.8,
        augmentation_weight=0.25,
        training_seed=347,
        augmentation_seed=347,
    )


def assert_outputs_equal(left, right):
    assert set(left) == set(right)
    for key in left:
        np.testing.assert_allclose(
            np.asarray(left[key]),
            np.asarray(right[key]),
            rtol=0.0,
            atol=1e-12,
        )


def test_evidence_reuse_is_exact_and_reduces_model_passes(tmp_path):
    base = runtime()
    optimized = MDREvidenceReuseRuntime(base)
    rng = np.random.default_rng(41)
    views = [rng.normal(size=(12, 2)), rng.normal(size=(12, 3))]
    views[0][0] = 0.0

    expected = base.predict(views)
    assert base.clean_runtime.model.calls == 2
    assert base.robust_runtime.model.calls == 3

    base.clean_runtime.model.calls = 0
    base.robust_runtime.model.calls = 0
    actual = optimized.predict(views)
    assert base.clean_runtime.model.calls == 1
    assert base.robust_runtime.model.calls == 1
    assert_outputs_equal(expected, actual)

    path = tmp_path / "optimized.joblib"
    joblib.dump(optimized, path, compress=3)
    loaded = joblib.load(path)
    assert_outputs_equal(expected, loaded.predict(views))
    evidence = loaded.evidence()["deployment_optimization"]
    assert evidence["effect_semantics_changed"] is False


def test_evidence_reuse_remains_exact_under_all_frozen_corruptions():
    base = runtime()
    optimized = MDREvidenceReuseRuntime(base)
    rng = np.random.default_rng(43)
    views = [rng.normal(size=(15, 2)), rng.normal(size=(15, 3))]
    conditions = [
        ("modality_missing", 1.0),
        ("field_missing", 0.3),
        ("row_missing", 0.3),
        ("feature_shuffle", 0.3),
        ("gaussian_drift", 0.5),
    ]
    for index, (family, severity) in enumerate(conditions):
        corrupted = base.corrupt(
            views,
            family=family,
            modality=index % 2,
            severity=severity,
            seed=100 + index,
        )
        assert_outputs_equal(
            base.predict(corrupted), optimized.predict(corrupted)
        )

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from benchmark_pairwise_runtime_optimized import equivalence
from caeos.hybrid_open_set import EmpiricalTailCalibrator, KnownQuantileNormalizer
from caeos.hybrid import ConflictAwareHybridClassifier
from caeos.pairwise_runtime import PairwiseRuntime
from caeos.pairwise_runtime_optimized import (
    OptimizedPairwiseRuntime,
    demand_driven_open_set_components,
)


class ScoreModel:
    def __init__(self, value: float):
        self.value = value
        self.calls = 0

    def score(self, values, prediction=None):
        self.calls += 1
        return np.full(len(values), self.value, dtype=np.float64)


class ProbabilityModel:
    def __init__(self, probability: np.ndarray):
        self.probability = np.asarray(probability, dtype=np.float64)
        self.calls = 0

    def predict_proba(self, values):
        self.calls += 1
        return np.tile(self.probability, (len(values), 1))


def make_runtime(selected_risk: str, learned_weights=None) -> PairwiseRuntime:
    learned_weights = learned_weights or {}
    reference_components = {
        name: np.asarray([0.0, 0.5, 1.0])
        for name in (
            "uncertainty",
            "inverse_belief",
            "inverse_margin",
            "conflict",
            "tree_disagreement",
            "distance",
            "knn_distance",
            "knn_view_0",
            "class_knn_distance",
            "lof_density",
        )
    }
    tail = EmpiricalTailCalibrator()
    tail.fit(reference_components)
    normalizer = KnownQuantileNormalizer()
    normalizer.fit(reference_components)
    runtime = PairwiseRuntime(
        model=object(),
        foss_model=None,
        distance_model=ScoreModel(0.4),
        knn_model=ScoreModel(0.5),
        view_knn_models=[ScoreModel(0.6)],
        class_knn_model=ScoreModel(0.7),
        lof_model=ScoreModel(0.8),
        normalizer=normalizer,
        tail_calibrator=tail,
        selected_risk=selected_risk,
        learned_weights=learned_weights,
        validation_raw_learned=np.asarray([0.0, 0.5, 1.0]),
        selected_alpha=0.25,
        foss_structural_view=False,
        foss_structural_view_mode="tree",
        foss_structural_view_scope="full",
    )
    runtime._model_inputs = lambda raw_views: (
        [np.asarray(raw_views[0])],
        np.asarray(raw_views[0]),
        np.asarray(raw_views[0]),
    )
    return runtime


def fake_components(model, views, distance_model, values):
    count = len(values)
    components = {
        "uncertainty": np.full(count, 0.1),
        "inverse_belief": np.full(count, 0.2),
        "inverse_margin": np.full(count, 0.3),
        "conflict": np.full(count, 0.4),
        "tree_disagreement": np.full(count, 0.5),
        "distance": np.full(count, 0.6),
    }
    probability = np.tile(np.asarray([[0.7, 0.3]]), (count, 1))
    return components, probability


class OptimizedPairwiseRuntimeTests(unittest.TestCase):
    def test_supported_classifier_reuses_each_global_forest_once(self) -> None:
        model = ConflictAwareHybridClassifier()
        model.random_forest = ProbabilityModel(np.asarray([[0.8, 0.2]]))
        model.extra_trees = ProbabilityModel(np.asarray([[0.6, 0.4]]))
        model.global_rf_weight = 0.25
        model.view_weight = 0.2
        model.conflict_scale = 1.5
        model.temperature = 1.1
        model._view_evidence = lambda views: {
            "global_conflict": np.full(len(views[0]), 0.3),
            "view_fused_probability": np.tile(
                np.asarray([[0.55, 0.45]]), (len(views[0]), 1)
            ),
        }
        components, probability = demand_driven_open_set_components(
            model,
            [np.ones((3, 2))],
            ScoreModel(0.4),
            np.ones((3, 2)),
        )
        self.assertEqual(model.random_forest.calls, 1)
        self.assertEqual(model.extra_trees.calls, 1)
        self.assertEqual(probability.shape, (3, 2))
        self.assertEqual(components["tree_disagreement"].shape, (3,))

    @patch(
        "caeos.pairwise_runtime_optimized.hybrid_open_set_components",
        side_effect=fake_components,
    )
    def test_reference_branch_skips_unused_density_models(self, _mock) -> None:
        runtime = make_runtime("cauchy_modality_support_union")
        output = OptimizedPairwiseRuntime(runtime).predict([np.ones((4, 2))])
        self.assertEqual(output["risk"].shape, (4,))
        self.assertEqual(runtime.view_knn_models[0].calls, 1)
        self.assertEqual(runtime.knn_model.calls, 0)
        self.assertEqual(runtime.class_knn_model.calls, 0)
        self.assertEqual(runtime.lof_model.calls, 0)

    @patch(
        "caeos.pairwise_runtime_optimized.hybrid_open_set_components",
        side_effect=fake_components,
    )
    def test_learned_branch_only_computes_weighted_optional_components(
        self, _mock
    ) -> None:
        runtime = make_runtime(
            "pseudo_unknown_learned_blend",
            {"inverse_belief": 0.5, "knn_distance": 0.5},
        )
        OptimizedPairwiseRuntime(runtime).predict([np.ones((4, 2))])
        self.assertEqual(runtime.knn_model.calls, 1)
        self.assertEqual(runtime.class_knn_model.calls, 0)
        self.assertEqual(runtime.lof_model.calls, 0)

    def test_full_equivalence_gate_passes_at_zero_difference(self) -> None:
        class Runtime:
            def predict(self, views):
                return {
                    "prediction": np.asarray([0, 1]),
                    "probability": np.asarray([[0.8, 0.2], [0.1, 0.9]]),
                    "risk": np.asarray([0.2, 0.7]),
                }

        runtime = Runtime()
        result = equivalence(runtime, runtime, [np.ones((2, 1))])
        self.assertTrue(result["passes"])
        self.assertTrue(result["prediction_array_equal"])


if __name__ == "__main__":
    unittest.main()

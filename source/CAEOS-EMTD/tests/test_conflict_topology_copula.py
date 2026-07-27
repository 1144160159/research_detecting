import unittest

import numpy as np

from caeos.conflict_topology_copula import (
    FEATURE_NAMES,
    KnownOnlyCopulaRisk,
    blend_with_incumbent,
    conflict_topology_features,
)


def example(sample_count: int = 24):
    rng = np.random.RandomState(11)
    probability = rng.dirichlet(np.ones(4), size=(sample_count, 3))
    reliability = rng.uniform(0.2, 1.0, size=(sample_count, 3))
    conflict = rng.uniform(0.0, 0.6, size=(sample_count, 3, 3))
    conflict = 0.5 * (conflict + conflict.transpose(0, 2, 1))
    conflict[:, np.arange(3), np.arange(3)] = 0.0
    global_probability = rng.dirichlet(np.ones(4), size=sample_count)
    fused_probability = rng.dirichlet(np.ones(4), size=sample_count)
    return probability, reliability, conflict, global_probability, fused_probability


class ConflictTopologyCopulaTests(unittest.TestCase):
    def test_features_are_finite_and_view_permutation_invariant(self) -> None:
        probability, reliability, conflict, global_probability, fused_probability = example()
        first = conflict_topology_features(
            view_probability=probability,
            view_reliability=reliability,
            pairwise_conflict=conflict,
            global_probability=global_probability,
            view_fused_probability=fused_probability,
        )
        order = np.array([2, 0, 1])
        second = conflict_topology_features(
            view_probability=probability[:, order],
            view_reliability=reliability[:, order],
            pairwise_conflict=conflict[:, order][:, :, order],
            global_probability=global_probability,
            view_fused_probability=fused_probability,
        )
        self.assertEqual(first.shape, (24, len(FEATURE_NAMES)))
        self.assertTrue(np.isfinite(first).all())
        np.testing.assert_allclose(first, second, atol=1e-12, rtol=0.0)

    def test_laplacian_feature_responds_to_conflict_magnitude(self) -> None:
        probability, reliability, conflict, global_probability, fused_probability = example(2)
        conflict[0] = 0.0
        conflict[1] = np.array(
            [[0.0, 0.8, 0.7], [0.8, 0.0, 0.9], [0.7, 0.9, 0.0]]
        )
        features = conflict_topology_features(
            view_probability=probability,
            view_reliability=reliability,
            pairwise_conflict=conflict,
            global_probability=global_probability,
            view_fused_probability=fused_probability,
        )
        self.assertEqual(features[0, 2], 0.0)
        self.assertGreater(features[1, 2], features[0, 2])

    def test_known_only_copula_is_deterministic_and_bounded(self) -> None:
        probability, reliability, conflict, global_probability, fused_probability = example(60)
        features = conflict_topology_features(
            view_probability=probability,
            view_reliability=reliability,
            pairwise_conflict=conflict,
            global_probability=global_probability,
            view_fused_probability=fused_probability,
        )
        labels = np.repeat(np.arange(3), 20)
        first = KnownOnlyCopulaRisk().fit(features, labels)
        second = KnownOnlyCopulaRisk().fit(features, labels)
        first_risk = first.score(features)
        second_risk = second.score(features)
        np.testing.assert_array_equal(first.fit_indices, second.fit_indices)
        np.testing.assert_allclose(first_risk, second_risk, atol=0.0, rtol=0.0)
        self.assertTrue(np.all((0.0 <= first_risk) & (first_risk < 1.0)))
        self.assertFalse(first.evidence()["uses_unknown_or_test_labels_for_fit"])

    def test_blend_preserves_endpoints(self) -> None:
        incumbent = np.array([0.1, 0.7])
        topology = np.array([0.9, 0.3])
        np.testing.assert_array_equal(blend_with_incumbent(incumbent, topology, 0.0), incumbent)
        np.testing.assert_array_equal(blend_with_incumbent(incumbent, topology, 1.0), topology)


if __name__ == "__main__":
    unittest.main()

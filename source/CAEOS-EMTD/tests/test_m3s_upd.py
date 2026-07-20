import unittest

import numpy as np
import torch

from caeos.m3s_upd import (
    M3SClassifier,
    SpatialAlignment,
    adaptive_dbscan_eps,
    align_unlabeled_clusters,
    alignment_threshold,
    class_centroids,
    consistency_selection,
    standardize_embeddings,
    unknown_risk,
)


class M3SUPDTests(unittest.TestCase):
    def test_classifier_exposes_embedding_and_logits(self):
        model = M3SClassifier(12, 3, embedding_dim=7)
        output = model(torch.randn(8, 12))
        self.assertEqual(output["logits"].shape, (8, 3))
        self.assertEqual(output["embedding"].shape, (8, 7))

    def test_alignment_marks_far_cluster_unknown(self):
        labeled = np.asarray([[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0]])
        labels = np.asarray([0, 0, 1, 1])
        centroids = class_centroids(labeled, labels, 2)
        threshold = alignment_threshold(labeled, labels, centroids, 0.95)
        values = np.asarray([[0.02, 0.01], [0.03, 0.0], [20.0, 20.0], [20.1, 20.0]])
        result = align_unlabeled_clusters(values, centroids, threshold, min_samples=2)
        self.assertFalse(result.potential_unknown[:2].any())
        self.assertTrue(result.potential_unknown[2:].all())

    def test_consistency_requires_probability_alignment_agreement(self):
        probabilities = np.asarray(
            [[0.99, 0.01], [0.98, 0.02], [0.01, 0.99], [0.51, 0.49]]
        )
        alignment = SpatialAlignment(
            auxiliary_labels=np.asarray([0, 1, 1, 0]),
            potential_unknown=np.asarray([False, False, False, True]),
            sample_distance=np.asarray([0.1, 0.1, 0.1, 10.0]),
            cluster_labels=np.arange(4),
            eps=0.2,
        )
        result = consistency_selection(probabilities, alignment, 0.50, 0.25)
        self.assertIn(0, result.known_indices)
        self.assertNotIn(1, result.known_indices)
        self.assertIn(3, result.unknown_indices)

    def test_adaptive_eps_and_risk_are_finite(self):
        values = np.random.RandomState(7).normal(size=(30, 4))
        eps = adaptive_dbscan_eps(values, min_samples=5)
        risk = unknown_risk(
            np.tile(np.asarray([[0.7, 0.3]]), (30, 1)),
            np.linspace(0.0, 3.0, 30),
            1.0,
        )
        self.assertGreater(eps, 0.0)
        self.assertTrue(np.isfinite(risk).all())
        self.assertTrue((risk >= 0.0).all() and (risk <= 1.0).all())

    def test_embedding_standardization_uses_reference_only(self):
        reference = np.asarray([[0.0, 0.0], [2.0, 4.0]])
        values = np.asarray([[100.0, 100.0]])
        standardized_reference, standardized_values, state = standardize_embeddings(reference, values)
        np.testing.assert_allclose(state[0], [1.0, 2.0])
        np.testing.assert_allclose(standardized_reference.mean(axis=0), 0.0)
        self.assertTrue((standardized_values > 1.0).all())

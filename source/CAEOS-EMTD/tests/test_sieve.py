import unittest

import numpy as np
import torch

from caeos.sieve import (
    SieveClassifier,
    SieveMahalanobis,
    balanced_knn_scores,
    select_sieve_samples,
    sieve_contrastive_loss,
    swap_adjacent_features,
)


class SieveTests(unittest.TestCase):
    def test_classifier_exposes_official_detection_embedding(self):
        model = SieveClassifier([4, 3], 3)
        result = model((torch.randn(5, 4), torch.randn(5, 3)))
        self.assertEqual(result["logits"].shape, (5, 3))
        self.assertEqual(result["embedding"].shape, (5, 256))
        self.assertEqual(result["detection_embedding"].shape, (5, 480))

    def test_feature_swap_preserves_each_row_values(self):
        values = torch.arange(24, dtype=torch.float32).reshape(3, 8)
        swapped = swap_adjacent_features(values, 0.5)
        self.assertTrue(
            torch.equal(torch.sort(values, dim=1).values, torch.sort(swapped, dim=1).values)
        )

    def test_knn_excludes_self_and_selection_has_fallback(self):
        features = torch.eye(4)
        labels = torch.tensor([0, 0, 1, 1])
        scores = balanced_knn_scores(features, labels, 2, 1, exclude_self=True)
        self.assertEqual(tuple(scores.shape), (4, 2))
        selection = select_sieve_samples(
            features, torch.zeros(4, 2), labels, 2, neighbors=1, xi=2.0, zeta=1.1
        )
        self.assertTrue(torch.equal(selection.selected_indices, torch.arange(4)))

    def test_contrastive_loss_is_finite(self):
        first = torch.randn(8, 16)
        second = first + 0.01 * torch.randn(8, 16)
        loss = sieve_contrastive_loss(first, second, 0.07)
        self.assertTrue(torch.isfinite(loss))

    def test_mahalanobis_prefers_near_class_samples(self):
        rng = np.random.default_rng(7)
        train = np.vstack(
            [rng.normal(-2, 0.2, size=(20, 6)), rng.normal(2, 0.2, size=(20, 6))]
        )
        labels = np.repeat([0, 1], 20)
        detector = SieveMahalanobis()
        detector.fit(train, labels)
        risk = detector.score(np.array([[-2, -2, -2, -2, -2, -2], [0, 0, 0, 0, 0, 0]]))
        self.assertLess(risk[0], risk[1])


if __name__ == "__main__":
    unittest.main()

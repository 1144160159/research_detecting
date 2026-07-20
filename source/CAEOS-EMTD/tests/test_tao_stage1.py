import unittest

import numpy as np
import torch

from caeos.multiclass import ConcatMLPClassifier
from caeos.tao_stage1 import (
    PCAResidualScorer,
    hybrid_scores,
    mlp_blood_score,
    reference_zscore,
)


class TaoStage1AdapterTest(unittest.TestCase):
    def test_pca_residual_rewards_off_subspace_samples(self) -> None:
        anchor = np.column_stack([np.linspace(-2, 2, 30), np.zeros(30), np.zeros(30)])
        scorer = PCAResidualScorer(0.95)
        scorer.fit(anchor)
        risk = scorer.score(np.asarray([[0.0, 0.0, 0.0], [0.0, 4.0, 3.0]]))
        self.assertLess(risk[0], risk[1])

    def test_reference_normalization_never_uses_test_statistics(self) -> None:
        validation, test = reference_zscore(np.asarray([1.0, 2.0, 3.0]), np.asarray([100.0]))
        self.assertAlmostEqual(float(validation.mean()), 0.0)
        self.assertGreater(float(test[0]), 100.0)

    def test_hybrid_endpoints_match_normalized_components(self) -> None:
        validation = np.asarray([1.0, 2.0, 4.0])
        test = np.asarray([3.0, 8.0])
        val_pca, test_pca = hybrid_scores(validation, validation + 10, test, test + 10, alpha=1.0)
        expected_val, expected_test = reference_zscore(validation, test)
        np.testing.assert_allclose(val_pca, expected_val)
        np.testing.assert_allclose(test_pca, expected_test)

    def test_mlp_blood_is_finite_deterministic_and_batch_aligned(self) -> None:
        torch.manual_seed(7)
        model = ConcatMLPClassifier((3, 2), 3, hidden_dim=8, embedding_dim=4, dropout=0.0)
        views = (torch.randn(6, 3), torch.randn(6, 2))
        first = mlp_blood_score(model, views, estimators=3, seed=19)
        second = mlp_blood_score(model, views, estimators=3, seed=19)
        self.assertEqual(first.shape, (6,))
        self.assertTrue(np.isfinite(first).all())
        np.testing.assert_allclose(first, second)


if __name__ == "__main__":
    unittest.main()

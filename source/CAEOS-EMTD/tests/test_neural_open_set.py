import unittest

import numpy as np
import torch

from caeos.neural_open_set import (
    ARPLClassifier,
    OpenMaxCalibrator,
    RelativeMahalanobis,
    SharedCovarianceMahalanobis,
    ViMCalibrator,
    arpl_risk,
    energy_risk,
    msp_risk,
)
from caeos.multiclass import supervised_contrastive_loss


class NeuralOpenSetTests(unittest.TestCase):
    def test_msp_and_energy_assign_higher_risk_to_flat_logits(self):
        logits = np.asarray([[8.0, 0.0], [0.0, 0.0]])
        self.assertLess(msp_risk(logits)[0], msp_risk(logits)[1])
        self.assertLess(energy_risk(logits)[0], energy_risk(logits)[1])

    def test_mahalanobis_assigns_higher_risk_to_distant_point(self):
        values = np.asarray([[-1.1, -1.0], [-0.9, -1.0], [1.0, 1.1], [1.0, 0.9]])
        labels = np.asarray([0, 0, 1, 1])
        model = SharedCovarianceMahalanobis()
        model.fit(values, labels)
        score = model.score(np.asarray([[-1.0, -1.0], [8.0, 8.0]]))
        self.assertLess(score[0], score[1])

    def test_relative_mahalanobis_and_vim_are_finite(self):
        rng = np.random.RandomState(3)
        values = np.r_[rng.normal(-1, 0.2, (20, 4)), rng.normal(1, 0.2, (20, 4))]
        labels = np.r_[np.zeros(20, dtype=int), np.ones(20, dtype=int)]
        logits = np.c_[values[:, 0], -values[:, 0]]
        relative = RelativeMahalanobis()
        relative.fit(values, labels)
        self.assertTrue(np.isfinite(relative.score(values)).all())
        vim = ViMCalibrator(principal_dimension=2)
        vim.fit(values, logits, np.asarray([[1, 0, 0, 0], [-1, 0, 0, 0]]), np.zeros(2))
        self.assertTrue(np.isfinite(vim.score(values, logits)).all())

    def test_openmax_returns_finite_risk_and_known_predictions(self):
        logits = np.asarray(
            [[5.0, 0.0], [4.8, 0.1], [4.9, -0.1], [0.0, 5.0], [0.1, 4.8], [-0.1, 4.9]]
        )
        labels = np.asarray([0, 0, 0, 1, 1, 1])
        model = OpenMaxCalibrator(tail_size=3, alpha=2)
        model.fit(logits, labels)
        risk, prediction = model.predict(np.asarray([[5.0, 0.0], [0.0, 5.0], [2.5, 2.5]]))
        self.assertTrue(np.isfinite(risk).all())
        self.assertTrue(((risk >= 0.0) & (risk <= 1.0)).all())
        self.assertEqual(prediction.tolist()[:2], [0, 1])

    def test_arpl_forward_and_risk_shapes(self):
        model = ARPLClassifier([3, 2], num_classes=3, embedding_dim=4, hidden_dim=8)
        output = model([torch.randn(5, 3), torch.randn(5, 2)])
        loss = model.loss(output, torch.tensor([0, 1, 2, 0, 1]))
        self.assertEqual(tuple(output["logits"].shape), (5, 3))
        self.assertTrue(torch.isfinite(loss))
        self.assertEqual(arpl_risk(output["logits"].detach().numpy()).shape, (5,))

    def test_supervised_contrastive_loss_is_finite_with_singletons(self):
        embedding = torch.randn(4, 5)
        labels = torch.tensor([0, 1, 2, 3])
        self.assertTrue(torch.isfinite(supervised_contrastive_loss(embedding, labels)))


if __name__ == "__main__":
    unittest.main()

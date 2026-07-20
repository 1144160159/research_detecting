import unittest

import numpy as np
import torch

from caeos.open_detect import OpenDetectClassifier, open_detect_risk


class OpenDetectTest(unittest.TestCase):
    def test_forward_loss_and_risk_are_finite(self):
        torch.manual_seed(3)
        model = OpenDetectClassifier((4, 3), 3, hidden_dim=16, latent_dim=6)
        views = (torch.randn(10, 4), torch.randn(10, 3))
        labels = torch.arange(10) % 3
        output = model(views)
        loss = model.loss(output, labels)

        self.assertEqual(output["logits"].shape, (10, 3))
        self.assertEqual(output["embedding"].shape, (10, 6))
        self.assertEqual(output["reconstruction"].shape, (10, 7))
        self.assertTrue(torch.isfinite(loss))
        risk = open_detect_risk(output["logits"].detach().numpy())
        self.assertEqual(risk.shape, (10,))
        self.assertTrue(np.isfinite(risk).all())

    def test_eval_is_deterministic_and_prototypes_can_be_reset(self):
        torch.manual_seed(9)
        model = OpenDetectClassifier((5,), 2, hidden_dim=12, latent_dim=4)
        views = (torch.randn(8, 5),)
        model.eval()
        first = model(views)
        second = model(views)
        np.testing.assert_allclose(
            first["embedding"].detach().numpy(),
            second["embedding"].detach().numpy(),
        )

        embedding = np.vstack([np.ones((3, 4)), np.full((2, 4), 4.0)])
        labels = np.array([0, 0, 0, 1, 1])
        model.reset_prototypes(embedding, labels)
        np.testing.assert_allclose(model.prototypes[0].detach().numpy(), 1.0)
        np.testing.assert_allclose(model.prototypes[1].detach().numpy(), 4.0)

    def test_risk_matches_minimum_kl(self):
        logits = np.array([[-2.0, -5.0], [-7.0, -3.0]])
        np.testing.assert_allclose(open_detect_risk(logits), [2.0, 3.0])

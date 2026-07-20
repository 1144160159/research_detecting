import unittest

import numpy as np
import torch

from caeos.gradnorm_posthoc import gradnorm_confidence, gradnorm_risk


class GradNormPosthocTests(unittest.TestCase):
    def test_analytic_score_matches_official_autograd_construction(self):
        embedding = torch.tensor([[1.5, -0.5]], dtype=torch.float64)
        layer = torch.nn.Linear(2, 3, bias=True).double()
        with torch.no_grad():
            layer.weight.copy_(
                torch.tensor([[0.2, 0.4], [-0.3, 0.1], [0.5, -0.2]], dtype=torch.float64)
            )
            layer.bias.copy_(torch.tensor([0.1, -0.2, 0.3], dtype=torch.float64))
        logits = layer(embedding)
        loss = torch.sum(-torch.ones_like(logits) * torch.log_softmax(logits, dim=1))
        loss.backward()
        expected = float(layer.weight.grad.abs().sum())
        actual = gradnorm_confidence(
            embedding.detach().numpy(), logits.detach().numpy()
        )[0]
        self.assertAlmostEqual(actual, expected, places=10)

    def test_risk_is_negative_confidence_and_finite(self):
        embedding = np.array([[1.0, 2.0], [0.5, 0.25]])
        logits = np.array([[3.0, 0.0], [0.0, 0.0]])
        confidence = gradnorm_confidence(embedding, logits)
        risk = gradnorm_risk(embedding, logits)
        np.testing.assert_allclose(risk, -confidence)
        self.assertTrue(np.isfinite(risk).all())


if __name__ == "__main__":
    unittest.main()

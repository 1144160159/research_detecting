import unittest

import numpy as np
import torch
from torch import nn

from caeos.odin_posthoc import odin_batch, validate_parameters


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.classifier = nn.Linear(2, 2, bias=False)
        with torch.no_grad():
            self.classifier.weight.copy_(torch.tensor([[1.0, -1.0], [-1.0, 1.0]]))

    def forward(self, views, quality=None):
        values = torch.cat(views, dim=1)
        return {"logits": self.classifier(values), "embedding": values}


class ODINPosthocTests(unittest.TestCase):
    def test_zero_noise_matches_temperature_scaled_msp(self):
        model = TinyModel()
        views = [torch.tensor([[2.0], [0.0]]), torch.tensor([[0.0], [2.0]])]
        prediction, risk = odin_batch(
            model, views, torch.ones(2, 2), temperature=10.0, noise=0.0
        )
        with torch.no_grad():
            logits = model(views)["logits"] / 10.0
            expected = 1.0 - torch.softmax(logits, dim=1).max(dim=1).values
        np.testing.assert_array_equal(prediction, np.array([0, 1]))
        np.testing.assert_allclose(risk, expected.numpy(), rtol=1e-6, atol=1e-7)

    def test_perturbation_produces_finite_risk_without_changing_output_shape(self):
        prediction, risk = odin_batch(
            TinyModel(),
            [torch.tensor([[1.0], [-1.0]]), torch.tensor([[0.0], [0.0]])],
            torch.ones(2, 2),
            temperature=1000.0,
            noise=0.001,
        )
        self.assertEqual(prediction.shape, (2,))
        self.assertEqual(risk.shape, (2,))
        self.assertTrue(np.isfinite(risk).all())

    def test_invalid_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_parameters(0.0, 0.001)
        with self.assertRaises(ValueError):
            validate_parameters(1000.0, -0.001)


if __name__ == "__main__":
    unittest.main()

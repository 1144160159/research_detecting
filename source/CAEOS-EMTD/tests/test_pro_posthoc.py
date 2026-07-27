from __future__ import annotations

import unittest

import torch
from torch import nn

from caeos.pro_posthoc import OFFICIAL_COMMIT, evidence, pro_msp_batch


class ToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.classifier = nn.Linear(2, 2, bias=False)
        with torch.no_grad():
            self.classifier.weight.copy_(torch.tensor([[2.0, -1.0], [-1.0, 2.0]]))

    def forward(self, views, quality=None):
        values = torch.cat(list(views), dim=1)
        return {"logits": self.classifier(values), "embedding": values}


class PROPosthocTests(unittest.TestCase):
    def test_sign_descent_minimum_never_increases_confidence(self) -> None:
        model = ToyModel()
        views = [torch.tensor([[1.0], [0.2]]), torch.tensor([[0.0], [0.8]])]
        quality = torch.ones(2, 1)
        with torch.no_grad():
            original = torch.softmax(model(views)["logits"], dim=1).max(dim=1).values
            expected_prediction = model(views)["logits"].argmax(dim=1)
        prediction, risk, diagnostics = pro_msp_batch(
            model, views, quality, step_size=0.003, steps=1
        )
        torch.testing.assert_close(prediction, expected_prediction)
        self.assertTrue(torch.all(risk >= 1.0 - original - 1e-7))
        self.assertEqual(diagnostics["path_points"], 2)
        self.assertGreaterEqual(diagnostics["mean_confidence_drop"], 0.0)

    def test_official_defaults_are_frozen_without_ood_sweep(self) -> None:
        value = evidence()
        self.assertEqual(value["official_commit"], OFFICIAL_COMMIT)
        self.assertEqual(value["step_size"], 0.003)
        self.assertEqual(value["steps"], 1)
        self.assertIn("no_ood_sweep", value["hyperparameter_policy"])

    def test_invalid_parameters_fail_closed(self) -> None:
        model = ToyModel()
        views = [torch.zeros(2, 1), torch.zeros(2, 1)]
        quality = torch.ones(2, 1)
        with self.assertRaises(ValueError):
            pro_msp_batch(model, views, quality, step_size=0.0)
        with self.assertRaises(ValueError):
            pro_msp_batch(model, views, quality, steps=0)


if __name__ == "__main__":
    unittest.main()

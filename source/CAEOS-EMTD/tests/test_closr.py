from __future__ import annotations

import unittest

import numpy as np
import torch

from caeos.closr import (
    CLOSRClassifier,
    closr_loss,
    closr_risk,
    warmup_cosine_learning_rate,
)


class CLOSRTest(unittest.TestCase):
    def test_model_loss_centroids_and_risk(self) -> None:
        torch.manual_seed(7)
        model = CLOSRClassifier(
            [3, 2], num_classes=3, hidden_dim=16, embedding_dim=4, depth=2
        )
        views = [torch.randn(12, 3), torch.randn(12, 2)]
        labels = torch.arange(12) % 3
        output = model(views)

        self.assertEqual(output["embedding"].shape, (12, 3, 4))
        self.assertTrue(
            torch.allclose(
                output["embedding"].norm(dim=-1), torch.ones(12, 3), atol=1e-5
            )
        )
        loss = model.loss(output, labels)
        self.assertTrue(torch.isfinite(loss))
        loss.backward()

        model.fit_centroids(
            output["embedding"].detach().numpy(), labels.numpy()
        )
        fitted = model(views)
        self.assertEqual(fitted["logits"].shape, (12, 3))
        risk = closr_risk(fitted["logits"].detach().numpy())
        self.assertEqual(risk.shape, (12,))
        self.assertTrue(np.isfinite(risk).all())

    def test_functional_loss_rejects_wrong_shape(self) -> None:
        with self.assertRaises(ValueError):
            closr_loss(torch.randn(4, 8), torch.tensor([0, 1, 0, 1]))

    def test_warmup_cosine_schedule_reaches_peak_and_floor(self) -> None:
        values = [
            warmup_cosine_learning_rate(step, 100, peak=1e-5)
            for step in range(100)
        ]
        self.assertAlmostEqual(values[0], 1e-6)
        self.assertAlmostEqual(max(values), 1e-5)
        self.assertAlmostEqual(values[-1], 1e-6)


if __name__ == "__main__":
    unittest.main()


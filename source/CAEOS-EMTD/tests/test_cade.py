import unittest

import numpy as np
import torch

from caeos.cade import CADECalibrator, CADEClassifier, contrastive_pair_loss


class CADETest(unittest.TestCase):
    def test_forward_losses_and_gradients_are_finite(self):
        torch.manual_seed(3)
        model = CADEClassifier([3, 2], num_classes=3)
        labels = torch.tensor([0, 0, 1, 1, 2, 2, 0, 1])
        output = model([torch.randn(8, 3), torch.randn(8, 2)])
        ae_loss = model.autoencoder_loss(output, labels)
        classifier_loss = torch.nn.functional.cross_entropy(output["logits"], labels)
        (ae_loss + classifier_loss).backward()

        self.assertEqual(tuple(output["embedding"].shape), (8, 16))
        self.assertEqual(tuple(output["reconstruction"].shape), (8, 5))
        self.assertEqual(tuple(output["logits"].shape), (8, 3))
        self.assertTrue(torch.isfinite(ae_loss))
        self.assertTrue(all(
            parameter.grad is None or torch.isfinite(parameter.grad).all()
            for parameter in model.parameters()
        ))

    def test_pair_loss_handles_small_and_balanced_batches(self):
        embedding = torch.tensor(
            [[0.0, 0.0], [0.1, 0.0], [4.0, 4.0], [4.1, 4.0]]
        )
        labels = torch.tensor([0, 0, 1, 1])
        loss = contrastive_pair_loss(embedding, labels)
        singleton = contrastive_pair_loss(embedding[:1], labels[:1])
        self.assertTrue(torch.isfinite(loss))
        self.assertEqual(float(singleton), 0.0)

    def test_mad_calibrator_assigns_larger_risk_to_far_sample(self):
        rng = np.random.RandomState(5)
        values = np.r_[
            rng.normal(-1.0, 0.15, (80, 3)),
            rng.normal(1.0, 0.15, (80, 3)),
        ]
        labels = np.r_[np.zeros(80, dtype=int), np.ones(80, dtype=int)]
        calibrator = CADECalibrator()
        calibrator.fit(values, labels)
        risk = calibrator.score(np.asarray([[-1.0, -1.0, -1.0], [8.0, 8.0, 8.0]]))
        self.assertTrue(np.isfinite(risk).all())
        self.assertLess(risk[0], risk[1])


if __name__ == "__main__":
    unittest.main()

import unittest

import numpy as np
import torch

from caeos.ronetc import (
    RoNeTCClassifier,
    dempster_shafer_combine,
    evidence_to_opinion,
    ronetc_risk,
)


class RoNeTCTest(unittest.TestCase):
    def test_opinion_is_normalized_and_uncertainty_decreases_with_evidence(self):
        evidence = torch.tensor([[0.0, 0.0, 0.0], [8.0, 0.0, 0.0]])
        _, belief, uncertainty = evidence_to_opinion(evidence)
        torch.testing.assert_close(belief.sum(dim=-1, keepdim=True) + uncertainty, torch.ones(2, 1))
        self.assertLess(float(uncertainty[1]), float(uncertainty[0]))

    def test_dempster_shafer_combination_is_commutative_and_normalized(self):
        first = torch.tensor([[4.0, 1.0, 0.0]])
        second = torch.tensor([[1.0, 3.0, 0.0]])
        _, b1, u1 = evidence_to_opinion(first)
        _, b2, u2 = evidence_to_opinion(second)
        belief12, uncertainty12, conflict12 = dempster_shafer_combine(b1, u1, b2, u2)
        belief21, uncertainty21, conflict21 = dempster_shafer_combine(b2, u2, b1, u1)
        torch.testing.assert_close(belief12, belief21)
        torch.testing.assert_close(uncertainty12, uncertainty21)
        torch.testing.assert_close(conflict12, conflict21)
        torch.testing.assert_close(
            belief12.sum(dim=-1, keepdim=True) + uncertainty12,
            torch.ones(1, 1),
        )

    def test_model_forward_loss_and_risk_are_finite(self):
        torch.manual_seed(7)
        model = RoNeTCClassifier((4, 3, 2), 3, hidden_dim=16, embedding_dim=8)
        views = (torch.randn(12, 4), torch.randn(12, 3), torch.randn(12, 2))
        labels = torch.arange(12) % 3
        output = model(views)
        loss = model.loss(output, labels, epoch=2)
        self.assertEqual(output["logits"].shape, (12, 3))
        self.assertEqual(output["view_alpha"].shape, (12, 3, 3))
        self.assertEqual(output["sequential_conflict"].shape, (12, 2))
        self.assertTrue(torch.isfinite(loss))
        risk = ronetc_risk(output["joint_uncertainty"].detach().numpy())
        self.assertEqual(risk.shape, (12,))
        self.assertTrue(np.isfinite(risk).all())


if __name__ == "__main__":
    unittest.main()

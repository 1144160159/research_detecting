import unittest

import torch

from caeos.vos import (
    ClassConditionalGaussianQueue,
    VOSClassifier,
    lowest_likelihood_samples,
    weighted_logsumexp,
)


class VOSTests(unittest.TestCase):
    def test_lowest_likelihood_selection_uses_gaussian_tail(self) -> None:
        distribution = torch.distributions.MultivariateNormal(
            torch.zeros(2), torch.eye(2)
        )
        candidates = torch.tensor([[0.0, 0.0], [1.0, 0.0], [4.0, 0.0]])
        selected = lowest_likelihood_samples(distribution, candidates, 1)
        self.assertTrue(torch.equal(selected, candidates[2:3]))

    def test_queue_estimates_tied_covariance_and_synthesizes_per_class(self) -> None:
        torch.manual_seed(7)
        queues = ClassConditionalGaussianQueue(2, capacity=6)
        queues.update(torch.randn(6, 3), torch.zeros(6, dtype=torch.long))
        queues.update(torch.randn(6, 3) + 2.0, torch.ones(6, dtype=torch.long))
        means, covariance = queues.statistics(1e-4)
        outliers = queues.synthesize(sample_from=20, select=2, ridge=1e-4)
        self.assertEqual(means.shape, (2, 3))
        self.assertEqual(covariance.shape, (3, 3))
        self.assertEqual(outliers.shape, (4, 3))
        self.assertTrue(torch.isfinite(outliers).all())

    def test_classifier_and_weighted_energy_shapes(self) -> None:
        model = VOSClassifier([2, 3], 4, hidden_dim=8, embedding_dim=6)
        output = model([torch.randn(5, 2), torch.randn(5, 3)])
        self.assertEqual(output["logits"].shape, (5, 4))
        self.assertEqual(output["embedding"].shape, (5, 6))
        self.assertEqual(output["weighted_energy"].shape, (5,))
        self.assertEqual(model.discriminate_energy(output["weighted_energy"]).shape, (5, 2))
        energy = weighted_logsumexp(torch.zeros(2, 4), torch.ones(1, 4))
        self.assertTrue(torch.allclose(energy, torch.full((2,), torch.log(torch.tensor(4.0)))))


if __name__ == "__main__":
    unittest.main()

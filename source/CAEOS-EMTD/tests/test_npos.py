import unittest

import torch

from caeos.npos import (
    ClassFeatureQueues,
    NPOSClassifier,
    synthesize_nonparametric_outliers,
)


class NPOSTests(unittest.TestCase):
    def test_synthesis_is_finite_and_selects_requested_count(self) -> None:
        torch.manual_seed(7)
        features = torch.cat(
            [torch.randn(20, 4) * 0.05, torch.randn(4, 4) + 3.0]
        )
        outliers = synthesize_nonparametric_outliers(
            features,
            neighbors=5,
            boundary_count=6,
            noise_count=30,
            outlier_count=3,
            covariance_scale=0.1,
        )
        self.assertEqual(outliers.shape, (3, 4))
        self.assertTrue(torch.isfinite(outliers).all())

    def test_class_queues_are_bounded_and_require_every_class(self) -> None:
        queues = ClassFeatureQueues(2, capacity=3)
        queues.update(torch.arange(20, dtype=torch.float32).reshape(5, 4), torch.zeros(5, dtype=torch.long))
        self.assertEqual(queues.counts(), [3, 0])
        self.assertFalse(queues.ready(2))
        queues.update(torch.ones(2, 4), torch.ones(2, dtype=torch.long))
        self.assertTrue(queues.ready(2))

    def test_classifier_exposes_classification_and_id_heads(self) -> None:
        model = NPOSClassifier([2, 3], 4, hidden_dim=8, embedding_dim=6)
        output = model([torch.randn(5, 2), torch.randn(5, 3)])
        self.assertEqual(output["logits"].shape, (5, 4))
        self.assertEqual(output["embedding"].shape, (5, 6))
        self.assertEqual(output["id_logit"].shape, (5,))


if __name__ == "__main__":
    unittest.main()

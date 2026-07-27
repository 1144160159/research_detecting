import unittest

import numpy as np
import torch

from caeos.grood_posthoc import GROODCalibrator, grood_gradients


class GROODPosthocTests(unittest.TestCase):
    def test_analytic_ood_prototype_gradient_matches_autograd(self):
        embedding = np.array([[0.5, -0.25]], dtype=np.float64)
        prototypes = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float64)
        noise = np.array([0.25, 0.75], dtype=np.float64)
        actual, _ = grood_gradients(embedding, prototypes, noise)

        z = torch.tensor(embedding, dtype=torch.float64)
        known = torch.tensor(prototypes, dtype=torch.float64)
        q = torch.tensor(noise, dtype=torch.float64, requires_grad=True)
        scores = -torch.linalg.vector_norm(
            z[:, None, :] - torch.cat([known, q[None, :]], dim=0)[None, :, :],
            dim=2,
        )
        loss = torch.nn.functional.cross_entropy(
            scores, torch.tensor([0]), reduction="none"
        )
        expected = torch.autograd.grad(loss[0], q)[0].detach().numpy()
        np.testing.assert_allclose(actual[0], expected, atol=1e-12, rtol=1e-12)

    def test_fit_and_evaluate_are_deterministic_and_known_only(self):
        features = np.array(
            [
                [0.0, 0.0],
                [0.1, 0.0],
                [1.0, 1.0],
                [0.9, 1.0],
                [2.0, 0.0],
                [2.1, 0.1],
            ]
        )
        labels = np.array([0, 0, 1, 1, 2, 2])
        logits = np.array(
            [
                [4.0, 1.0, 0.0],
                [3.0, 1.0, 0.0],
                [0.0, 4.0, 1.0],
                [0.0, 3.0, 1.0],
                [0.0, 1.0, 4.0],
                [0.0, 1.0, 3.0],
            ]
        )
        first = GROODCalibrator(synthetic_count=4, synthetic_seed=7)
        second = GROODCalibrator(synthetic_count=4, synthetic_seed=7)
        first.fit(features, logits, labels)
        second.fit(features, logits, labels)
        np.testing.assert_array_equal(first.synthetic_indices, second.synthetic_indices)
        np.testing.assert_allclose(first.ood_prototype, second.ood_prototype)
        output = first.evaluate(np.array([[0.05, 0.0], [3.0, 3.0]]))
        self.assertEqual(output["risk"].shape, (2,))
        self.assertTrue(np.isfinite(output["risk"]).all())
        evidence = first.evidence()
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertTrue(evidence["adaptation"]["official_validation_ood_disabled"])

    def test_rejects_missing_known_class(self):
        calibrator = GROODCalibrator()
        with self.assertRaisesRegex(ValueError, "every known class"):
            calibrator.fit(
                np.array([[0.0, 0.0], [1.0, 1.0]]),
                np.array([[3.0, 1.0, 0.0], [0.0, 3.0, 1.0]]),
                np.array([0, 1]),
            )


if __name__ == "__main__":
    unittest.main()

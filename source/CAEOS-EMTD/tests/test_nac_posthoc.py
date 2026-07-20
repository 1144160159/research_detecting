import unittest

import numpy as np
import torch

from caeos.nac_posthoc import NACUEFixedCalibrator, official_thresholds


class NACPosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(43)
        self.train = rng.normal(size=(60, 7))
        self.weights = rng.normal(size=(4, 7))
        self.bias = rng.normal(size=4)
        self.train_logits = self.train @ self.weights.T + self.bias
        self.labels = np.repeat(np.arange(4), 15)
        self.features = rng.normal(size=(8, 7))
        self.logits = self.features @ self.weights.T + self.bias

    def test_analytic_uniform_kl_state_matches_autograd(self):
        calibrator = NACUEFixedCalibrator(sigmoid_alpha=3.0)
        actual = calibrator.activation_state(self.features, self.logits, self.weights)
        features = torch.tensor(self.features, dtype=torch.float64, requires_grad=True)
        weights = torch.tensor(self.weights, dtype=torch.float64)
        bias = torch.tensor(self.bias, dtype=torch.float64)
        logits = features @ weights.T + bias
        uniform = torch.ones_like(logits) / logits.shape[1]
        loss = torch.sum(-uniform * torch.log_softmax(logits, dim=1), dim=1).sum()
        gradient = torch.autograd.grad(loss, features)[0]
        expected = torch.sigmoid(3.0 * features.detach() * gradient).numpy()
        np.testing.assert_allclose(actual, expected, rtol=1e-11, atol=1e-12)

    def test_official_logspace_has_expected_intervals(self):
        thresholds = official_thresholds(50)
        self.assertEqual(thresholds.shape, (50,))
        self.assertAlmostEqual(thresholds[0], 0.0)
        self.assertAlmostEqual(thresholds[-1], 1.2)
        self.assertTrue(np.all(np.diff(thresholds) > 0.0))

    def test_fit_score_and_balanced_subset(self):
        calibrator = NACUEFixedCalibrator(valid_num=20, bucket_count=50, minimum_bin_count=2)
        calibrator.fit(self.train, self.train_logits, self.labels, self.weights)
        evidence = calibrator.evidence()
        self.assertEqual(evidence["coverage_subset_count"], 20)
        self.assertEqual(evidence["coverage_subset_per_class"], 5)
        output = calibrator.evaluate(self.features, self.logits)
        self.assertTrue(np.isfinite(output["risk"]).all())
        self.assertGreater(float(np.std(output["confidence"])), 0.0)

    def test_prediction_is_unmodified(self):
        calibrator = NACUEFixedCalibrator(valid_num=20)
        calibrator.fit(self.train, self.train_logits, self.labels, self.weights)
        output = calibrator.evaluate(self.features, self.logits)
        np.testing.assert_array_equal(output["prediction"], self.logits.argmax(axis=1))


if __name__ == "__main__":
    unittest.main()

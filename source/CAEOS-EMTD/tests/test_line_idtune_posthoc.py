import unittest

import numpy as np

from caeos.line_idtune_posthoc import LINeIDTuneCalibrator


class LINeIDTunePosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(23)
        self.train = rng.normal(loc=0.5, size=(30, 5))
        self.labels = np.repeat(np.arange(3), 10)
        self.validation = rng.normal(loc=0.5, size=(12, 5))
        self.validation_labels = np.arange(12) % 3
        self.weights = rng.normal(size=(3, 5))
        self.bias = rng.normal(size=3)
        self.validation_logits = self.validation @ self.weights.T + self.bias

    def _calibrator(self):
        calibrator = LINeIDTuneCalibrator(
            pruning_candidates=((10, 10), (90, 10)), clip_quantiles=(0.9, 0.99)
        )
        calibrator.fit(
            self.train, self.labels, self.validation, self.validation_labels,
            self.validation_logits, self.weights, self.bias,
        )
        return calibrator

    def test_taylor_contribution_matches_linear_head_identity(self):
        calibrator = self._calibrator()
        expected = np.vstack([
            (self.train[self.labels == class_index] * self.weights[class_index]).mean(axis=0)
            for class_index in range(3)
        ])
        np.testing.assert_allclose(calibrator.contribution, expected)

    def test_routing_matches_official_formula(self):
        calibrator = self._calibrator()
        output = calibrator.evaluate(self.validation, self.validation_logits)
        prediction = self.validation_logits.argmax(axis=1)
        clipped = np.minimum(self.validation, calibrator.parameters.clip_threshold)
        routed = clipped * calibrator.activation_mask[prediction]
        expected = np.einsum("nd,ncd->nc", routed, calibrator.masked_weights[prediction]) + self.bias
        np.testing.assert_array_equal(output["prediction"], prediction)
        np.testing.assert_allclose(output["routed_logits"], expected)

    def test_selection_is_known_only_and_deterministic(self):
        first = self._calibrator()
        second = self._calibrator()
        self.assertEqual(first.parameters, second.parameters)
        evidence = first.evidence()
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertEqual(evidence["adaptation"]["name"], "IDTune")


if __name__ == "__main__":
    unittest.main()

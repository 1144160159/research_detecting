import unittest

import numpy as np

from caeos.fdbd_posthoc import FDBDCalibrator


class FDBDPosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(29)
        self.train = rng.normal(size=(30, 5))
        self.features = rng.normal(size=(8, 5))
        self.weights = rng.normal(size=(4, 5))
        self.bias = rng.normal(size=4)
        self.logits = self.features @ self.weights.T + self.bias

    def test_formula_matches_official_code(self):
        calibrator = FDBDCalibrator()
        calibrator.fit(self.train, self.weights)
        output = calibrator.evaluate(self.features, self.logits)
        prediction = self.logits.argmax(axis=1)
        expected = []
        for feature, logits, predicted in zip(self.features, self.logits, prediction):
            denominator = np.linalg.norm(self.weights - self.weights[predicted], axis=1)
            denominator[predicted] = 1.0
            numerator = np.abs(logits - logits[predicted])
            expected.append(np.sum(numerator / denominator) / np.linalg.norm(feature - self.train.mean(axis=0)))
        np.testing.assert_allclose(output["confidence"], expected)
        np.testing.assert_allclose(output["risk"], -np.asarray(expected))

    def test_prediction_is_unmodified(self):
        calibrator = FDBDCalibrator()
        calibrator.fit(self.train, self.weights)
        output = calibrator.evaluate(self.features, self.logits)
        np.testing.assert_array_equal(output["prediction"], self.logits.argmax(axis=1))

    def test_duplicate_weights_use_numerical_adapter(self):
        weights = self.weights.copy()
        weights[1] = weights[0]
        calibrator = FDBDCalibrator()
        calibrator.fit(self.train, weights)
        self.assertEqual(calibrator.evidence()["zero_nonself_weight_distance_count"], 2)
        output = calibrator.evaluate(self.features, self.logits)
        self.assertTrue(np.isfinite(output["risk"]).all())


if __name__ == "__main__":
    unittest.main()

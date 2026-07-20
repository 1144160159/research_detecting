import unittest

import numpy as np

from caeos.optfs_posthoc import OptFSCalibrator


class OptFSPosthocTests(unittest.TestCase):
    def setUp(self):
        self.feature = np.array([
            [-2.0, -1.0, 0.5], [-1.0, 0.0, 1.0], [0.0, 1.0, 2.0],
            [1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0],
        ])
        self.weight = np.array([[1.0, 0.5, -0.25], [-0.5, 0.75, 1.0]])
        self.bias = np.array([0.2, -0.1])
        self.logits = self.feature @ self.weight.T + self.bias

    def test_formula_matches_direct_official_loops(self):
        calibrator = OptFSCalibrator(quantile_epsilon=0.1, bin_count=5, theta_norm=10.0)
        calibrator.fit(self.feature, self.logits, self.weight, self.bias)
        left = np.quantile(self.feature, 0.1)
        right = np.quantile(self.feature, 0.9)
        width = (right - left) / 5
        boundaries = left + width * np.arange(5)
        prediction = self.logits.argmax(axis=1)
        contribution = self.weight[prediction] * self.feature
        lc = np.array([
            np.mean(np.sum(((self.feature >= b) & (self.feature < b + width)) * contribution, axis=1))
            for b in boundaries
        ])
        theta = lc / np.linalg.norm(lc) * 10.0
        shaped = np.zeros_like(self.feature)
        for index, boundary in enumerate(boundaries):
            shaped += ((self.feature >= boundary) & (self.feature < boundary + width)) * self.feature * theta[index]
        np.testing.assert_allclose(calibrator.left_boundary, boundaries)
        np.testing.assert_allclose(calibrator.theta, theta)
        np.testing.assert_allclose(calibrator.transform(self.feature), shaped)

    def test_prediction_is_unshaped_and_risk_is_negative_vanilla_confidence(self):
        calibrator = OptFSCalibrator(quantile_epsilon=0.1, bin_count=5, theta_norm=10.0)
        calibrator.fit(self.feature, self.logits, self.weight, self.bias)
        output = calibrator.evaluate(self.feature, self.logits)
        np.testing.assert_array_equal(output["prediction"], self.logits.argmax(axis=1))
        expected = np.sum(self.weight[output["prediction"]] * output["shaped_feature"], axis=1)
        np.testing.assert_allclose(output["confidence"], expected)
        np.testing.assert_allclose(output["risk"], -expected)

    def test_fit_rejects_degenerate_feature_range(self):
        values = np.ones((4, 3))
        logits = values @ self.weight.T + self.bias
        with self.assertRaisesRegex(ValueError, "degenerate"):
            OptFSCalibrator().fit(values, logits, self.weight, self.bias)


if __name__ == "__main__":
    unittest.main()

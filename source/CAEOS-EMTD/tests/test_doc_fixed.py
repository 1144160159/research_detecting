import unittest

import numpy as np

from caeos.doc_fixed import DOCFixedCalibrator


class DOCFixedTests(unittest.TestCase):
    def test_gaussian_threshold_matches_paper_rule(self):
        calibrator = DOCFixedCalibrator(alpha=3.0, max_iter=20)
        embeddings = np.array([[2.0, 0.0], [1.5, 0.2], [0.0, 2.0], [0.2, 1.5]], dtype=np.float32)
        labels = np.array([0, 0, 1, 1])
        calibrator.fit(embeddings, labels, np.eye(2, dtype=np.float32), np.zeros(2, dtype=np.float32))
        output = calibrator.evaluate(embeddings)
        for class_index in range(2):
            positive = output.probabilities[labels == class_index, class_index]
            expected = max(0.5, 1.0 - 3.0 * np.sqrt(np.mean((positive - 1.0) ** 2)))
            self.assertAlmostEqual(calibrator.thresholds_[class_index], expected, delta=1e-6)

    def test_continuous_risk_preserves_native_rejection_boundary(self):
        calibrator = DOCFixedCalibrator()
        calibrator.weight_ = np.eye(2)
        calibrator.bias_ = np.zeros(2)
        calibrator.thresholds_ = np.array([0.8, 0.7])
        output = calibrator.evaluate(np.array([[3.0, -3.0], [0.0, 0.0], [-3.0, 2.0]]))
        np.testing.assert_array_equal(output.native_reject, output.risk > 0.0)

    def test_ovr_optimization_is_deterministic_and_nonincreasing(self):
        embeddings = np.array([[2.0, 0.0], [1.0, 0.1], [0.0, 2.0], [0.1, 1.0]], dtype=np.float32)
        labels = np.array([0, 0, 1, 1])
        fits = [DOCFixedCalibrator(max_iter=25).fit(embeddings, labels, np.eye(2), np.zeros(2)) for _ in range(2)]
        self.assertLessEqual(fits[0].final_loss_, fits[0].initial_loss_ + 1e-6)
        np.testing.assert_allclose(fits[0].weight_, fits[1].weight_, rtol=0.0, atol=1e-7)
        np.testing.assert_allclose(fits[0].thresholds_, fits[1].thresholds_, rtol=0.0, atol=1e-10)


if __name__ == "__main__":
    unittest.main()

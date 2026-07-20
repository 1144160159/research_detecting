import unittest

import numpy as np
from scipy.special import softmax

from caeos.sirc_posthoc import METHODS, SIRCMSPFixedCalibrator, sirc_risk


class SIRCPosthocTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(47)
        self.train = rng.normal(size=(80, 8))
        self.weight = rng.normal(size=(4, 8))
        self.bias = rng.normal(size=4)
        self.train_logits = self.train @ self.weight.T + self.bias
        self.test = rng.normal(size=(11, 8))
        self.test_logits = self.test @ self.weight.T + self.bias

    def test_formula_matches_official_logaddexp_form(self):
        primary = np.array([0.4, 0.7, 0.9])
        auxiliary = np.array([-2.0, 0.5, 3.0])
        actual = sirc_risk(primary, auxiliary, a=-0.2, b=1.7)
        expected = np.log(1.0 - primary) + np.logaddexp(0.0, -1.7 * (auxiliary + 0.2))
        np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-13)

    def test_known_only_parameter_rule(self):
        calibrator = SIRCMSPFixedCalibrator()
        calibrator.fit(self.train, self.train_logits, self.weight, self.bias)
        for params in calibrator.parameters.values():
            self.assertAlmostEqual(params.a, params.mean - 3.0 * params.std)
            self.assertAlmostEqual(params.b, 1.0 / params.std)

    def test_scores_are_finite_nondegenerate_and_predictions_unchanged(self):
        calibrator = SIRCMSPFixedCalibrator()
        calibrator.fit(self.train, self.train_logits, self.weight, self.bias)
        output = calibrator.evaluate(self.test, self.test_logits)
        np.testing.assert_array_equal(output["prediction"], self.test_logits.argmax(axis=1))
        np.testing.assert_allclose(output["msp"], softmax(self.test_logits, axis=1).max(axis=1))
        for method in METHODS:
            self.assertTrue(np.isfinite(output[method]).all())
            self.assertGreater(float(np.std(output[method])), 0.0)

    def test_evidence_freezes_official_commit_and_no_ood(self):
        calibrator = SIRCMSPFixedCalibrator()
        calibrator.fit(self.train, self.train_logits, self.weight, self.bias)
        evidence = calibrator.evidence()
        self.assertEqual(evidence["official_code_commit"], "0b492695d5bf34942cd8b333d10a998f763c3eff")
        self.assertFalse(evidence["unknown_or_test_labels_used"])


if __name__ == "__main__":
    unittest.main()

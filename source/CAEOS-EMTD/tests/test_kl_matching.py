import unittest

import numpy as np

from caeos.kl_matching import fit_kl_matching_templates, kl_matching_risk


class KLMatchingTests(unittest.TestCase):
    def test_templates_group_validation_softmax_by_prediction(self):
        logits = np.array([[5.0, 0.0], [4.0, 0.0], [0.0, 5.0]])
        templates = fit_kl_matching_templates(logits)
        self.assertEqual(templates.shape, (2, 2))
        self.assertGreater(templates[0, 0], templates[0, 1])
        self.assertGreater(templates[1, 1], templates[1, 0])

    def test_matching_samples_have_lower_risk_than_uniform_sample(self):
        validation = np.array([[6.0, 0.0], [5.0, 0.0], [0.0, 6.0], [0.0, 5.0]])
        templates = fit_kl_matching_templates(validation)
        risks = kl_matching_risk(np.array([[6.0, 0.0], [0.0, 0.0]]), templates)
        self.assertLess(risks[0], risks[1])

    def test_missing_predicted_class_uses_stable_one_hot_fallback(self):
        templates = fit_kl_matching_templates(np.array([[5.0, 0.0], [4.0, 0.0]]))
        np.testing.assert_allclose(templates[1], np.array([0.0, 1.0]))
        risk = kl_matching_risk(np.array([[0.0, 5.0]]), templates)
        self.assertTrue(np.isfinite(risk).all())


if __name__ == "__main__":
    unittest.main()

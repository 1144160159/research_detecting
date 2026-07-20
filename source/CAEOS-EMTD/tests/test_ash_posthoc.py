import unittest

import numpy as np

from caeos.ash_posthoc import ash_s_activations, ash_s_logits, ash_s_risk


class ASHPosthocTests(unittest.TestCase):
    def test_ash_s_keeps_top_features_and_preserves_official_scale(self):
        values = np.array([[1.0, 2.0, 3.0, 4.0]])
        shaped = ash_s_activations(values, percentile=50.0)
        self.assertEqual(np.count_nonzero(shaped), 2)
        self.assertEqual(np.flatnonzero(shaped[0]).tolist(), [2, 3])
        expected_scale = np.exp(10.0 / 7.0)
        np.testing.assert_allclose(shaped[0, 2:], values[0, 2:] * expected_scale)

    def test_gelu_negative_values_are_rectified_before_shaping(self):
        shaped = ash_s_activations(np.array([[-0.2, 0.0, 1.0, 2.0]]), 50.0)
        self.assertTrue((shaped >= 0.0).all())
        self.assertEqual(np.count_nonzero(shaped), 2)

    def test_logits_and_risk_are_finite(self):
        logits = ash_s_logits(
            np.array([[1.0, 2.0, 3.0, 4.0]]),
            np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]),
            np.zeros(2),
            50.0,
        )
        risk = ash_s_risk(logits)
        self.assertEqual(risk.shape, (1,))
        self.assertTrue(np.isfinite(risk).all())


if __name__ == "__main__":
    unittest.main()

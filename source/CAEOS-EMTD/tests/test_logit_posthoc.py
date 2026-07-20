import unittest

import numpy as np

from caeos.logit_posthoc import (
    generalized_entropy_risk,
    shannon_entropy_risk,
    softmax_probabilities,
)


class LogitPosthocTests(unittest.TestCase):
    def test_probabilities_are_stable_and_normalized(self) -> None:
        values = softmax_probabilities(np.array([[1000.0, 999.0], [-1000.0, -999.0]]))
        np.testing.assert_allclose(values.sum(axis=1), 1.0)
        self.assertTrue(np.isfinite(values).all())

    def test_entropy_risks_are_larger_for_uniform_logits(self) -> None:
        logits = np.array([[8.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        shannon = shannon_entropy_risk(logits)
        gen = generalized_entropy_risk(logits, gamma=0.1, top_m=100)
        self.assertGreater(shannon[1], shannon[0])
        self.assertGreater(gen[1], gen[0])

    def test_gen_matches_official_formula_with_class_clamped_top_m(self) -> None:
        logits = np.array([[2.0, 1.0, -1.0]])
        probability = softmax_probabilities(logits)
        expected = np.sum(probability ** 0.1 * (1.0 - probability) ** 0.1, axis=1)
        np.testing.assert_allclose(
            generalized_entropy_risk(logits, gamma=0.1, top_m=100), expected
        )


if __name__ == "__main__":
    unittest.main()

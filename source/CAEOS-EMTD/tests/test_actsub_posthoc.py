from __future__ import annotations

import unittest

import numpy as np

from caeos.actsub_posthoc import (
    OFFICIAL_COMMIT,
    actsub_score_batch,
    evidence,
    fit_actsub,
    scale_decisive,
)


class ActSubPosthocTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(11)
        self.weight = rng.normal(size=(3, 20))
        self.bias = rng.normal(size=3)
        self.train = rng.normal(size=(40, 20))

    def test_projectors_are_deterministic_and_partition_identity(self) -> None:
        first = fit_actsub(self.weight, self.bias, self.train)
        second = fit_actsub(self.weight, self.bias, self.train)
        self.assertEqual(first.balance_index, second.balance_index)
        np.testing.assert_allclose(
            first.decisive_transform + first.insignificant_transform,
            np.eye(20),
            atol=1e-12,
        )
        np.testing.assert_allclose(
            first.decisive_transform @ first.insignificant_transform,
            0.0,
            atol=1e-12,
        )

    def test_scale_matches_official_uniform_factor_formula(self) -> None:
        values = np.array([[1.0, 2.0, 3.0, 4.0]])
        shaped, diagnostics = scale_decisive(values, percentile=50.0)
        expected_factor = np.exp(10.0 / 7.0)
        np.testing.assert_allclose(shaped, values * expected_factor)
        self.assertEqual(diagnostics["retained_coordinates"], 2)

    def test_score_is_finite_and_uses_fixed_official_defaults(self) -> None:
        state = fit_actsub(self.weight, self.bias, self.train)
        score, diagnostics = actsub_score_batch(self.train[:5] + 0.01, state)
        self.assertEqual(score.shape, (5,))
        self.assertTrue(np.isfinite(score).all())
        self.assertTrue(diagnostics["all_scores_finite"])
        item = evidence()
        self.assertEqual(item["official_commit"], OFFICIAL_COMMIT)
        self.assertEqual(item["scale_percentile"], 95.0)
        self.assertEqual(item["lambda"], 2.0)
        self.assertIn("without_APS_OOD_sweep", item["hyperparameter_policy"])

    def test_invalid_or_singular_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            fit_actsub(self.weight, self.bias, self.train[:5], neighbors=10)
        with self.assertRaises(FloatingPointError):
            scale_decisive(np.array([[0.0, -1.0, -2.0, -3.0]]), percentile=75.0)


if __name__ == "__main__":
    unittest.main()

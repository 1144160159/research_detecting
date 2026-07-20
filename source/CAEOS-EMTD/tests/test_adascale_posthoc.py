import unittest

import numpy as np
import torch
from torch import nn

from caeos.adascale_posthoc import (
    AdaSCALECalibrator,
    adascale_factors,
    adascale_feature_batch,
    adaptive_percentiles,
    empirical_cdf,
    percent_to_count,
    q_prime_statistic,
)


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.classifier = nn.Linear(4, 2, bias=False)
        with torch.no_grad():
            self.classifier.weight.copy_(
                torch.tensor([[1.0, 2.0, 3.0, 4.0], [-1.0, -2.0, -3.0, -4.0]])
            )

    def forward(self, views, quality=None):
        feature = torch.cat(views, dim=1)
        return {"logits": self.classifier(feature), "embedding": feature}


class AdaSCALEPosthocTests(unittest.TestCase):
    def test_low_dimensional_percentages_retain_at_least_one_feature(self):
        self.assertEqual(percent_to_count(64, 1.0), 1)
        self.assertEqual(percent_to_count(64, 5.0), 3)
        self.assertEqual(percent_to_count(4, 1.0), 1)

    def test_q_prime_uses_k1_for_shift_and_k2_for_correction(self):
        feature = np.array([[10.0, 9.0, 1.0, 0.0]])
        perturbed = np.array([[12.0, 10.0, 100.0, 0.0]])
        value, k1, k2 = q_prime_statistic(
            feature, perturbed, k1_percent=25.0, k2_percent=50.0, lmbda=10.0
        )
        # Q = |12 - 10| at top-1; C_o = 12 + 10 at top-2.
        np.testing.assert_allclose(value, np.array([42.0]))
        self.assertEqual((k1, k2), (1, 2))

    def test_ecdf_and_adaptive_percentile_are_right_continuous(self):
        reference = np.array([1.0, 2.0, 2.0, 4.0])
        np.testing.assert_allclose(
            empirical_cdf(reference, np.array([0.0, 2.0, 3.0, 5.0])),
            np.array([0.0, 0.75, 0.75, 1.0]),
        )
        np.testing.assert_allclose(
            adaptive_percentiles(reference, np.array([0.0, 2.0, 5.0]), 60.0, 85.0),
            np.array([85.0, 66.25, 60.0]),
        )

    def test_factor_matches_mass_ratio_and_scales_raw_embedding(self):
        feature = np.array([[4.0, 3.0, 2.0, 1.0], [-1.0, -2.0, -3.0, -4.0]])
        factors, retained = adascale_factors(feature, np.array([50.0, 50.0]))
        np.testing.assert_allclose(factors[0], np.exp(10.0 / 7.0))
        np.testing.assert_allclose(factors[1], 1.0)
        np.testing.assert_array_equal(retained, np.array([2, 2]))

        calibrator = AdaSCALECalibrator(
            p_min=49.0, p_max=51.0, k1_percent=25.0, k2_percent=25.0
        )
        validation = np.array([[4.0, 3.0, -2.0, -1.0]])
        calibrator.fit(
            validation,
            validation.copy(),
            np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]),
            np.zeros(2),
        )
        output = calibrator.evaluate(validation, validation.copy())
        self.assertLess(output["logits"][0, 1], 0.0)
        self.assertTrue(np.isfinite(output["risk"]).all())

    def test_gradient_perturbation_changes_low_attribution_coordinates(self):
        model = TinyModel()
        views = [torch.tensor([[1.0, 1.0]]), torch.tensor([[1.0, 1.0]])]
        original, perturbed = adascale_feature_batch(
            model, views, torch.ones(1, 2), perturb_fraction=0.25, epsilon=0.5
        )
        np.testing.assert_allclose(original, np.ones((1, 4)))
        # The lowest absolute predicted-logit gradient is the first coordinate.
        np.testing.assert_allclose(perturbed, np.array([[1.5, 1.0, 1.0, 1.0]]))


if __name__ == "__main__":
    unittest.main()

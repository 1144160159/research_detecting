from __future__ import annotations

import unittest

import numpy as np

from analyze_strict_v4_fhmm_seed_instability import distribution


class FhmmSeedInstabilityTests(unittest.TestCase):
    def test_distribution_reports_fixed_quantiles(self) -> None:
        result = distribution(np.asarray([0.0, 0.5, 1.0]))
        self.assertEqual(3, result["count"])
        self.assertEqual(0.5, result["mean"])
        self.assertEqual(0.5, result["quantiles"]["0.50"])

    def test_distribution_rejects_nonfinite_values(self) -> None:
        with self.assertRaises(ValueError):
            distribution(np.asarray([0.0, np.nan]))


if __name__ == "__main__":
    unittest.main()

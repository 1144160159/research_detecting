from __future__ import annotations

import unittest

import numpy as np

from evaluate_strict_v4_class_conditional_tail_development import (
    conditional_empirical_cdf,
)


class ClassConditionalTailDevelopmentTest(unittest.TestCase):
    def test_local_tail_uses_class_scale(self) -> None:
        observed = conditional_empirical_cdf(
            np.array([0.0, 1.0, 100.0, 101.0]),
            np.array([0, 0, 1, 1]),
            np.array([0.5, 100.5]),
            np.array([0, 1]),
            minimum_local_reference=2,
            local_shrinkage=0.0,
        )
        np.testing.assert_allclose(observed, np.array([0.5, 0.5]))

    def test_small_class_falls_back_to_global_tail(self) -> None:
        observed = conditional_empirical_cdf(
            np.array([0.0, 1.0, 100.0]),
            np.array([0, 0, 1]),
            np.array([100.0]),
            np.array([1]),
            minimum_local_reference=2,
            local_shrinkage=0.0,
        )
        np.testing.assert_allclose(observed, np.array([1.0]))

    def test_shrinkage_blends_local_and_global(self) -> None:
        observed = conditional_empirical_cdf(
            np.array([0.0, 1.0, 100.0, 101.0]),
            np.array([0, 0, 1, 1]),
            np.array([100.5]),
            np.array([1]),
            minimum_local_reference=2,
            local_shrinkage=2.0,
        )
        np.testing.assert_allclose(observed, np.array([0.625]))


if __name__ == "__main__":
    unittest.main()

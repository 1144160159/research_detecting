from __future__ import annotations

import unittest

import numpy as np

from analyze_strict_v4_rank_calibrated_missing_fallback_development import (
    candidate_output,
    empirical_quantile_map,
)


class RankCalibratedMissingFallbackTests(unittest.TestCase):
    def test_quantile_map_preserves_identical_reference_scale(self) -> None:
        reference = np.asarray([0.0, 0.5, 1.0])
        mapped = empirical_quantile_map(
            np.asarray([0.0, 0.5, 1.0]), reference, reference
        )
        np.testing.assert_allclose(mapped, reference)

    def test_no_missing_samples_preserve_incumbent_exactly(self) -> None:
        archive = {
            "validation_risk": np.asarray([0.1, 0.5, 0.9]),
            "test_risk": np.asarray([0.2, 0.8]),
            "validation_missing_aware_cauchy_modality_support_union": (
                np.asarray([0.0, 0.5, 1.0])
            ),
            "test_missing_aware_cauchy_modality_support_union": (
                np.asarray([0.9, 0.1])
            ),
            "test_any_missing": np.asarray([False, False]),
            "test_missing_aware_prediction": np.asarray([1, 0]),
            "test_prediction": np.asarray([0, 1]),
        }
        output, count, exact = candidate_output(archive, "risk")
        self.assertEqual(count, 0)
        self.assertTrue(exact)
        np.testing.assert_array_equal(
            output["risk"], archive["test_risk"]
        )
        np.testing.assert_array_equal(
            output["prediction"], archive["test_prediction"]
        )

    def test_missing_sample_uses_fallback_prediction(self) -> None:
        archive = {
            "validation_risk": np.asarray([0.1, 0.5, 0.9]),
            "test_risk": np.asarray([0.2, 0.8]),
            "validation_missing_aware_cauchy_modality_support_union": (
                np.asarray([0.0, 0.5, 1.0])
            ),
            "test_missing_aware_cauchy_modality_support_union": (
                np.asarray([0.9, 0.1])
            ),
            "test_any_missing": np.asarray([True, False]),
            "test_missing_aware_prediction": np.asarray([1, 0]),
            "test_prediction": np.asarray([0, 1]),
        }
        output, count, exact = candidate_output(archive, "risk")
        self.assertEqual(count, 1)
        self.assertTrue(exact)
        self.assertEqual(output["prediction"].tolist(), [1, 1])


if __name__ == "__main__":
    unittest.main()

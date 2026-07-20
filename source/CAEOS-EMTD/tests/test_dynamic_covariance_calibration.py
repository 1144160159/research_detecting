import unittest

import numpy as np

from caeos.dynamic_covariance_calibration import (
    DynamicCovarianceCalibration,
    l2_normalize_rows,
)


class DynamicCovarianceCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.features = np.asarray(
            [
                [2.0, 0.0, 0.1],
                [1.8, 0.2, 0.0],
                [2.1, -0.1, 0.2],
                [0.0, 3.0, 0.1],
                [0.2, 2.8, 0.0],
                [-0.1, 3.1, 0.2],
            ],
            dtype=np.float64,
        )
        self.labels = np.asarray([0, 0, 0, 1, 1, 1], dtype=np.int64)

    def test_row_normalization_has_unit_norm(self) -> None:
        normalized = l2_normalize_rows(self.features)
        np.testing.assert_allclose(np.linalg.norm(normalized, axis=1), 1.0)

    def test_scores_are_finite_and_deterministic(self) -> None:
        model = DynamicCovarianceCalibration(residual_dimension=2)
        model.fit(self.features, self.labels)
        query = np.asarray([[1.0, 0.1, 0.0], [0.1, 1.0, 0.2]], dtype=np.float64)
        first = model.score(query)
        second = model.score(query)
        self.assertTrue(np.isfinite(first).all())
        np.testing.assert_allclose(first, second, rtol=0.0, atol=0.0)

    def test_score_is_invariant_to_positive_row_scaling(self) -> None:
        model = DynamicCovarianceCalibration(residual_dimension=2)
        model.fit(self.features, self.labels)
        query = np.asarray([[1.0, 0.1, 0.0], [0.1, 1.0, 0.2]], dtype=np.float64)
        np.testing.assert_allclose(model.score(query), model.score(query * [[4.0], [7.0]]))

    def test_evidence_records_fixed_adaptation_and_no_leakage(self) -> None:
        model = DynamicCovarianceCalibration(residual_dimension=50)
        model.fit(self.features, self.labels)
        evidence = model.evidence()
        self.assertEqual(evidence["effective_residual_dimension"], 2)
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertIn("fixed_WRN", evidence["tabular_adaptation"])

    def test_fit_requires_multiple_classes(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            DynamicCovarianceCalibration().fit(
                self.features[:3], np.zeros(3, dtype=np.int64)
            )


if __name__ == "__main__":
    unittest.main()

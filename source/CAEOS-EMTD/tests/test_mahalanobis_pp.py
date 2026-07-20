import unittest

import numpy as np

from caeos.mahalanobis_pp import MahalanobisPlusPlus, l2_normalize_rows


class MahalanobisPlusPlusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.features = np.asarray(
            [[2.0, 0.0], [1.8, 0.2], [0.0, 3.0], [0.2, 2.8]], dtype=np.float64
        )
        self.labels = np.asarray([0, 0, 1, 1], dtype=np.int64)

    def test_row_normalization_has_unit_norm_for_nonzero_rows(self) -> None:
        normalized = l2_normalize_rows(self.features)
        np.testing.assert_allclose(np.linalg.norm(normalized, axis=1), 1.0)

    def test_score_is_invariant_to_positive_row_scaling(self) -> None:
        model = MahalanobisPlusPlus()
        model.fit(self.features, self.labels)
        query = np.asarray([[1.0, 0.1], [0.1, 1.0]], dtype=np.float64)
        np.testing.assert_allclose(model.score(query), model.score(query * [[4.0], [7.0]]))

    def test_zero_vector_is_finite_and_evidence_has_no_leakage(self) -> None:
        model = MahalanobisPlusPlus()
        model.fit(self.features, self.labels)
        self.assertTrue(np.isfinite(model.score(np.zeros((1, 2)))).all())
        evidence = model.evidence()
        self.assertEqual(evidence["method"], "Mahalanobis++")
        self.assertFalse(evidence["unknown_or_test_labels_used"])

    def test_fit_requires_multiple_classes(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            MahalanobisPlusPlus().fit(self.features[:2], np.zeros(2, dtype=np.int64))


if __name__ == "__main__":
    unittest.main()

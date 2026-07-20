from __future__ import annotations

import unittest

import numpy as np

from train_hybrid_open_set import (
    apply_test_corruption,
    apply_training_label_noise,
    missing_aware_cauchy_risk,
    missing_aware_max_risk,
    missing_aware_view_probability,
    missing_view_mask,
)


class OpenSetCorruptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.train = [np.arange(60, dtype=float).reshape(20, 3)]
        self.test = [np.arange(30, dtype=float).reshape(10, 3)]

    def test_label_noise_is_exact_deterministic_and_changes_labels(self) -> None:
        labels = np.repeat(np.arange(3), 10)
        first, count = apply_training_label_noise(labels, 0.2, 7)
        second, second_count = apply_training_label_noise(labels, 0.2, 7)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(6, count)
        self.assertEqual(count, second_count)
        self.assertEqual(count, int((first != labels).sum()))

    def test_missing_and_shuffle_only_change_test_copy(self) -> None:
        original = self.test[0].copy()
        missing, metadata = apply_test_corruption(
            self.test, self.train, "field_missing", 0, 0.5, 11
        )
        self.assertGreater(metadata["affected_entries"], 0)
        np.testing.assert_array_equal(self.test[0], original)
        self.assertFalse(np.array_equal(missing[0], original))
        shuffled, _ = apply_test_corruption(
            self.test, self.train, "feature_shuffle", 0, 1.0, 11
        )
        np.testing.assert_array_equal(
            np.sort(shuffled[0], axis=0), np.sort(original, axis=0)
        )

    def test_gaussian_drift_is_scaled_finite_and_deterministic(self) -> None:
        first, metadata = apply_test_corruption(
            self.test, self.train, "gaussian_drift", 0, 0.5, 19
        )
        second, _ = apply_test_corruption(
            self.test, self.train, "gaussian_drift", 0, 0.5, 19
        )
        np.testing.assert_array_equal(first[0], second[0])
        self.assertTrue(np.isfinite(first[0]).all())
        self.assertEqual(self.test[0].size, metadata["affected_entries"])

    def test_invalid_boundaries_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            apply_training_label_noise(np.arange(4), 1.0, 7)
        with self.assertRaises(ValueError):
            apply_test_corruption(self.test, self.train, "field_missing", 1, 0.5, 7)
        with self.assertRaises(ValueError):
            apply_test_corruption(self.test, self.train, "none", 0, 0.1, 7)

    def test_missing_aware_fusion_excludes_flagged_view(self) -> None:
        validation = [np.ones((10, 2)), np.ones((10, 2))]
        query = [np.ones((3, 2)), np.zeros((3, 2))]
        missing, _ = missing_view_mask(validation, query)
        self.assertTrue(missing[:, 1].all())
        probability = np.asarray(
            [
                [[0.9, 0.1], [0.1, 0.9]],
                [[0.8, 0.2], [0.2, 0.8]],
                [[0.7, 0.3], [0.3, 0.7]],
            ]
        )
        reliability = np.ones((3, 2))
        fallback = np.full((3, 2), 0.5)
        fused = missing_aware_view_probability(
            probability, reliability, missing, fallback
        )
        np.testing.assert_allclose(fused, probability[:, 0])
        risks = np.asarray([[0.2, 0.99], [0.3, 0.99], [0.4, 0.99]])
        robust = missing_aware_cauchy_risk(risks, missing, np.ones(3))
        np.testing.assert_allclose(robust, risks[:, 0], atol=1e-6)
        maximum = missing_aware_max_risk(risks, missing, np.ones(3))
        np.testing.assert_allclose(maximum, risks[:, 0])


if __name__ == "__main__":
    unittest.main()

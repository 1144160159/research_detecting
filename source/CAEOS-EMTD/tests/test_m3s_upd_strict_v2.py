from __future__ import annotations

import unittest

import numpy as np

from train_m3s_upd_strict_v2 import initial_labeled_indices


class StrictV2M3SUPDTest(unittest.TestCase):
    def test_initial_labeled_indices_are_deterministic_and_stratified(self) -> None:
        labels = np.repeat(np.arange(3), 10)
        first = initial_labeled_indices(labels, 0.3, seed=7)
        second = initial_labeled_indices(labels, 0.3, seed=7)
        np.testing.assert_array_equal(first, second)
        self.assertEqual([3, 3, 3], np.bincount(labels[first]).tolist())

    def test_labeled_fraction_is_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "labeled-fraction"):
            initial_labeled_indices(np.asarray([0, 1]), 0.0, seed=7)


if __name__ == "__main__":
    unittest.main()

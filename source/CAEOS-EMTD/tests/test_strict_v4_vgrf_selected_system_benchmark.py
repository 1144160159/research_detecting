from __future__ import annotations

import unittest

import numpy as np

from benchmark_strict_v4_vgrf_selected_system import (
    batch_indices,
    method_order,
)


class VGRFSelectedSystemBenchmarkTests(unittest.TestCase):
    def test_batch_indices_wrap_without_changing_size(self) -> None:
        values = batch_indices(5, 8, 1)
        self.assertEqual(len(values), 8)
        self.assertTrue(np.array_equal(values, [3, 4, 0, 1, 2, 3, 4, 0]))

    def test_method_order_alternates(self) -> None:
        self.assertEqual(method_order(0), ("vgrf", "opendetect"))
        self.assertEqual(method_order(1), ("opendetect", "vgrf"))
        self.assertEqual(method_order(2), ("vgrf", "opendetect"))

    def test_invalid_batch_policy_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            batch_indices(0, 1, 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from hft_mgbs.batching import bounded_batches


class CountingIterator:
    def __init__(self, size: int):
        self.size = size
        self.index = 0
        self.pulls = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.size:
            raise StopIteration
        value = self.index
        self.index += 1
        self.pulls += 1
        return value


class BoundedBatchesTest(unittest.TestCase):
    def test_does_not_pull_beyond_limit(self):
        source = CountingIterator(10)

        batches = list(bounded_batches(source, batch_size=3, max_items=5))

        self.assertEqual(batches, [[0, 1, 2], [3, 4]])
        self.assertEqual(source.pulls, 5)

    def test_zero_limit_means_unbounded(self):
        source = CountingIterator(5)

        batches = list(bounded_batches(source, batch_size=2))

        self.assertEqual(batches, [[0, 1], [2, 3], [4]])
        self.assertEqual(source.pulls, 5)

    def test_rejects_invalid_limits(self):
        with self.assertRaises(ValueError):
            list(bounded_batches([], batch_size=0))
        with self.assertRaises(ValueError):
            list(bounded_batches([], batch_size=1, max_items=-1))


if __name__ == "__main__":
    unittest.main()

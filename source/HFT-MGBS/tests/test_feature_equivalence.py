import copy
import unittest

from hft_mgbs.feature_equivalence import (
    compare_feature_summaries,
    summarize_feature_vectors,
)


class FeatureEquivalenceTest(unittest.TestCase):
    def test_digest_is_order_independent(self):
        first = [float(index) for index in range(38)]
        second = [float(index * 2) for index in range(38)]

        left = summarize_feature_vectors([first, second])
        right = summarize_feature_vectors([second, first])
        comparison = compare_feature_summaries(left, right)

        self.assertTrue(comparison["accepted"])

    def test_changed_feature_is_rejected(self):
        feature = [float(index) for index in range(38)]
        changed = copy.deepcopy(feature)
        changed[20] += 1.0

        before = summarize_feature_vectors([feature])
        after = summarize_feature_vectors([changed])
        comparison = compare_feature_summaries(before, after)

        self.assertFalse(comparison["accepted"])
        self.assertFalse(
            comparison["checks"]["base_feature_multiset_equal"]
        )

    def test_non_frozen_feature_count_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize_feature_vectors([[0.0] * 37])

    def test_base_mode_allows_only_deep_scheduling_to_change(self):
        before_feature = [0.0] * 38
        after_feature = [0.0] * 38
        before_feature[34:38] = [1.0, 0.5, 0.0, 1.0]

        comparison = compare_feature_summaries(
            summarize_feature_vectors([before_feature]),
            summarize_feature_vectors([after_feature]),
            require="base",
        )

        self.assertTrue(comparison["accepted"])
        self.assertEqual(comparison["required_equivalence"], "base")
        self.assertFalse(
            comparison["checks"]["full_feature_multiset_equal"]
        )


if __name__ == "__main__":
    unittest.main()

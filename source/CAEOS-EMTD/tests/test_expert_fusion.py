import unittest

import numpy as np

from analyze_caeos_closr_fusion import (
    empirical_percentile,
    fixed_fusions,
    parse_allowlist,
)


class ExpertFusionTest(unittest.TestCase):
    def test_empirical_percentile_is_monotonic_and_bounded(self):
        reference = np.array([1.0, 2.0, 3.0])
        values = np.array([0.0, 1.5, 4.0])
        tail = empirical_percentile(reference, values)
        self.assertTrue(np.all(np.diff(tail) > 0))
        self.assertTrue(np.all((tail > 0.0) & (tail < 1.0)))

    def test_fixed_fusions_have_expected_values(self):
        first = np.array([0.2, 0.9])
        second = np.array([0.6, 0.4])
        fused = fixed_fusions(first, second)
        np.testing.assert_allclose(fused["rank_mean"], [0.4, 0.65])
        np.testing.assert_allclose(fused["rank_union"], [0.68, 0.94])
        np.testing.assert_allclose(fused["rank_max"], [0.6, 0.9])
        np.testing.assert_allclose(fused["rank_min"], [0.2, 0.4])
        self.assertTrue(np.all((fused["rank_cauchy"] >= 0.0) & (fused["rank_cauchy"] <= 1.0)))
        np.testing.assert_allclose(fused["rank_bonferroni"], [0.2, 0.8])

    def test_shape_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            fixed_fusions(np.zeros(2), np.zeros(3))

    def test_fixed_fusion_names_do_not_depend_on_expert_type(self):
        fused = fixed_fusions(np.array([0.1]), np.array([0.8]))
        self.assertEqual(
            set(fused),
            {
                "rank_mean",
                "rank_union",
                "rank_max",
                "rank_min",
                "rank_cauchy",
                "rank_bonferroni",
            },
        )

    def test_allowlist_parser_is_strict(self):
        self.assertIsNone(parse_allowlist(None))
        self.assertEqual(parse_allowlist("7,11", int), {7, 11})
        self.assertEqual(parse_allowlist("edge,nf"), {"edge", "nf"})
        for invalid in ("", "7,", "7,7", "x"):
            with self.subTest(invalid=invalid):
                cast = int if invalid == "x" else str
                with self.assertRaises(ValueError):
                    parse_allowlist(invalid, cast)


if __name__ == "__main__":
    unittest.main()

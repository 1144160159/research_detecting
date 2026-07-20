import unittest

from analyze_density_support_gate import choose_density_support, stable_parent


def aggregate(value):
    return {
        "robust_objective": value,
        "minimum_auroc": value,
        "mean_auroc": value,
    }


class DensitySupportGateTest(unittest.TestCase):
    def test_density_gate_only_changes_anchor_support_parent(self):
        aggregates = {
            "density_support_union": aggregate(0.9),
            "triple_support_union": aggregate(0.8),
            "anchor_support": aggregate(0.5),
        }
        selected, _, _ = choose_density_support(
            aggregates, "cauchy_evidence", 0.01
        )
        self.assertEqual(selected, "cauchy_evidence")

    def test_density_gate_requires_strict_validation_gain(self):
        aggregates = {
            "density_support_union": aggregate(0.52),
            "triple_support_union": aggregate(0.51),
            "anchor_support": aggregate(0.50),
        }
        selected, challenger, gain = choose_density_support(
            aggregates, "anchor_support", 0.02
        )
        self.assertEqual(selected, "anchor_support")
        self.assertEqual(challenger, "density_support_union")
        self.assertAlmostEqual(gain, 0.02)

    def test_stable_parent_preserves_joint_conflict_fallback(self):
        aggregates = {
            "support_union": aggregate(0.4),
            "anchor_support": aggregate(0.4),
            "cauchy_evidence": aggregate(0.5),
            "cauchy_all": aggregate(0.57),
        }
        self.assertEqual(stable_parent(aggregates, 0.055), "cauchy_all")


if __name__ == "__main__":
    unittest.main()

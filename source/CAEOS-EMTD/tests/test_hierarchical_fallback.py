from __future__ import annotations

import unittest

from train_hybrid_open_set import (
    select_density_reliability_fallback,
    select_hierarchical_fallback,
    select_modality_support_fallback,
    select_structural_partition,
    select_structural_support_weight,
)


def values(robust: float) -> dict[str, float]:
    return {
        "robust_objective": robust,
        "minimum_auroc": robust,
        "mean_auroc": robust,
    }


class HierarchicalFallbackTest(unittest.TestCase):
    def test_modality_support_requires_strict_gain_over_joint_parent(self):
        aggregates = {
            "support_union": values(0.6),
            "anchor_support": values(0.61),
            "cauchy_evidence": values(0.7),
            "cauchy_all": values(0.76),
            "modality_support_union": values(0.78),
        }
        selected, details = select_modality_support_fallback(
            aggregates,
            joint_minimum_gain=0.055,
            modality_minimum_gain=0.02,
        )
        self.assertEqual(selected, "cauchy_all")
        self.assertEqual(details["parent_selected_risk"], "cauchy_all")
        aggregates["modality_support_union"] = values(0.781)
        selected, details = select_modality_support_fallback(
            aggregates,
            joint_minimum_gain=0.055,
            modality_minimum_gain=0.02,
        )
        self.assertEqual(selected, "modality_support_union")
        self.assertAlmostEqual(details["modality_support_candidate_gain"], 0.021)

    def test_modality_support_can_override_anchor_parent(self):
        selected, details = select_modality_support_fallback(
            {
                "support_union": values(0.8),
                "anchor_support": values(0.81),
                "cauchy_evidence": values(0.7),
                "cauchy_all": values(0.72),
                "modality_support_union": values(0.84),
            },
            joint_minimum_gain=0.055,
            modality_minimum_gain=0.02,
        )
        self.assertEqual(selected, "modality_support_union")
        self.assertEqual(details["parent_selected_risk"], "anchor_support")

    def test_density_reliability_gate_requires_class_diversity(self):
        aggregates = {
            "support_union": values(0.8),
            "anchor_support": values(0.81),
            "cauchy_evidence": values(0.7),
            "cauchy_all": values(0.7),
            "density_support_union": values(0.82),
            "triple_support_union": values(0.85),
        }
        selected, details = select_density_reliability_fallback(
            aggregates, 0.055, 0.02, known_class_count=7,
            minimum_known_classes=8,
        )
        self.assertEqual(selected, "anchor_support")
        self.assertFalse(details["density_reliability_satisfied"])
        selected, details = select_density_reliability_fallback(
            aggregates, 0.055, 0.02, known_class_count=8,
            minimum_known_classes=8,
        )
        self.assertEqual(selected, "triple_support_union")
        self.assertAlmostEqual(details["density_support_candidate_gain"], 0.04)

    def test_density_reliability_gate_preserves_conflict_parent(self):
        aggregates = {
            "support_union": values(0.6),
            "anchor_support": values(0.61),
            "cauchy_evidence": values(0.7),
            "cauchy_all": values(0.76),
            "density_support_union": values(0.9),
            "triple_support_union": values(0.91),
        }
        selected, details = select_density_reliability_fallback(
            aggregates, 0.055, 0.02, known_class_count=12,
            minimum_known_classes=8,
        )
        self.assertEqual(selected, "cauchy_all")
        self.assertIsNone(details["density_support_candidate"])

    def test_support_branch_keeps_anchor(self):
        selected, details = select_hierarchical_fallback(
            {
                "support_union": values(0.8),
                "cauchy_evidence": values(0.7),
                "cauchy_baseline": values(0.9),
            },
            minimum_gain=0.055,
        )
        self.assertEqual(selected, "anchor_support")
        self.assertEqual(details["first_stage_selected_risk"], "support_union")

    def test_conflict_fallback_requires_strict_minimum_gain(self):
        aggregates = {
            "support_union": values(0.6),
            "cauchy_evidence": values(0.7),
            "cauchy_baseline": values(0.755),
        }
        selected, _ = select_hierarchical_fallback(aggregates, minimum_gain=0.055)
        self.assertEqual(selected, "cauchy_evidence")
        aggregates["cauchy_baseline"] = values(0.756)
        selected, details = select_hierarchical_fallback(
            aggregates, minimum_gain=0.055
        )
        self.assertEqual(selected, "cauchy_baseline")
        self.assertAlmostEqual(details["conflict_fallback_gain"], 0.056)

    def test_joint_fallback_uses_requested_challenger(self):
        selected, details = select_hierarchical_fallback(
            {
                "support_union": values(0.6),
                "cauchy_evidence": values(0.7),
                "cauchy_all": values(0.756),
            },
            minimum_gain=0.055,
            challenger="cauchy_all",
        )
        self.assertEqual(selected, "cauchy_all")
        self.assertEqual(details["conflict_fallback_candidate"], "cauchy_all")

    def test_structural_partition_requires_strict_gain_over_parent(self):
        aggregates = {
            "support_union": values(0.8),
            "anchor_support": values(0.81),
            "cauchy_evidence": values(0.7),
            "cauchy_all": values(0.9),
            "foss_partition": values(0.83),
        }
        selected, details = select_structural_partition(
            aggregates, joint_minimum_gain=0.055, structural_minimum_gain=0.02
        )
        self.assertEqual(selected, "anchor_support")
        self.assertEqual(details["parent_selected_risk"], "anchor_support")
        aggregates["foss_partition"] = values(0.831)
        selected, details = select_structural_partition(
            aggregates, joint_minimum_gain=0.055, structural_minimum_gain=0.02
        )
        self.assertEqual(selected, "foss_partition")
        self.assertAlmostEqual(details["structural_candidate_gain"], 0.021)

    def test_structural_partition_compares_against_joint_parent(self):
        selected, details = select_structural_partition(
            {
                "support_union": values(0.6),
                "anchor_support": values(0.61),
                "cauchy_evidence": values(0.7),
                "cauchy_all": values(0.76),
                "foss_partition": values(0.775),
            },
            joint_minimum_gain=0.055,
            structural_minimum_gain=0.02,
        )
        self.assertEqual(selected, "cauchy_all")
        self.assertEqual(details["parent_selected_risk"], "cauchy_all")

    def test_structural_support_weight_requires_gain_over_zero(self):
        aggregates = {
            "structural_support_w0": {
                "weight": 0.0,
                "joint_robust_objective": 0.80,
                "oscr_robust_objective": 0.80,
                "auroc_robust_objective": 0.80,
            },
            "structural_support_w0p25": {
                "weight": 0.25,
                "joint_robust_objective": 0.805,
                "oscr_robust_objective": 0.81,
                "auroc_robust_objective": 0.80,
            },
        }
        selected, _ = select_structural_support_weight(aggregates, 0.005)
        self.assertEqual(selected, "structural_support_w0")
        aggregates["structural_support_w0p25"]["joint_robust_objective"] = 0.806
        selected, details = select_structural_support_weight(aggregates, 0.005)
        self.assertEqual(selected, "structural_support_w0p25")
        self.assertAlmostEqual(details["structural_support_gain"], 0.006)


if __name__ == "__main__":
    unittest.main()

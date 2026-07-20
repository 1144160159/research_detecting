from __future__ import annotations

import unittest

from analyze_validation_adaptive_fusion_gate import build_rules, selected_parent


class ValidationAdaptiveFusionGateTest(unittest.TestCase):
    def test_grid_has_unique_frozen_rules(self) -> None:
        rules = build_rules()
        names = [rule["name"] for rule in rules]
        self.assertEqual(len(rules), 98)
        self.assertEqual(len(names), len(set(names)))

    def test_selected_joint_rule_uses_only_validation_diagnostics(self) -> None:
        rule = next(
            item
            for item in build_rules()
            if item["name"] == "entropy_if_corr_ge_0.8_and_mad_ge_0.11"
        )
        self.assertEqual(
            selected_parent(
                rule,
                {
                    "rank_correlation": 0.81,
                    "mean_absolute_rank_difference": 0.12,
                },
            ),
            "entropy",
        )
        self.assertEqual(
            selected_parent(
                rule,
                {
                    "rank_correlation": 0.79,
                    "mean_absolute_rank_difference": 0.12,
                },
            ),
            "rank_union",
        )


if __name__ == "__main__":
    unittest.main()

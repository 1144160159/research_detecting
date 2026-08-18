from __future__ import annotations

import unittest

from create_strict_v4_budgeted_rescue_screening_protocol import BUDGET_PAIRS
from evaluate_strict_v4_budgeted_rescue_screening import selection_key


class BudgetedRescueScreeningTest(unittest.TestCase):
    def test_budget_pairs_respect_total_false_positive_budget(self) -> None:
        self.assertTrue(BUDGET_PAIRS)
        for primary, rescue in BUDGET_PAIRS:
            self.assertAlmostEqual(primary + rescue, 0.04)
            self.assertGreater(primary, 0.0)
            self.assertGreater(rescue, 0.0)

    def test_selection_prioritizes_scenario_coverage(self) -> None:
        def result(count: int, recall: float) -> dict:
            return {
                "all_seed_engineering_passed": False,
                "scenario_pass_counts": {"engineering": count},
                "overall": {
                    "engineering": {"passed": False},
                    "metrics": {
                        "unknown_attack_alert_recall": recall,
                        "attack_recall": 0.99,
                        "alert_accuracy": 0.99,
                        "known_attack_type_accuracy": 0.99,
                        "benign_fpr": 0.01,
                        "unknown_label_recall": 0.90,
                    },
                },
            }

        self.assertGreater(
            selection_key(result(20, 0.90)),
            selection_key(result(19, 0.99)),
        )


if __name__ == "__main__":
    unittest.main()

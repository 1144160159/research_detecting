from __future__ import annotations

import unittest

from create_strict_v4_alert_budget_frontier_protocol import ALERT_BUDGETS


class AlertBudgetFrontierTest(unittest.TestCase):
    def test_frontier_is_dense_and_below_five_percent(self) -> None:
        self.assertEqual(len(ALERT_BUDGETS), 10)
        self.assertAlmostEqual(ALERT_BUDGETS[0], 0.04)
        self.assertAlmostEqual(ALERT_BUDGETS[-1], 0.049)
        self.assertTrue(all(0.0 < value < 0.05 for value in ALERT_BUDGETS))


if __name__ == "__main__":
    unittest.main()

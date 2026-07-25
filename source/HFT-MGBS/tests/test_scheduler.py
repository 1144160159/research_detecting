import unittest

from hft_mgbs.scheduler import AdaptiveBudgetScheduler, ExtractionCandidate


class SchedulerTests(unittest.TestCase):
    def test_effective_budget_never_exceeds_configured_hard_cap(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=0.8)
        scheduler.observe("flow", measured_cost_us=1.0, realized_utility=1.0, utilization=0.1)
        self.assertLessEqual(scheduler.effective_budget(100.0), 100.0)

    def test_budget_ratios_cannot_expand_above_hard_cap(self):
        with self.assertRaises(ValueError):
            AdaptiveBudgetScheduler(max_budget_ratio=1.01)

    def test_budget_is_never_exceeded(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=1.0, min_budget_ratio=1.0, max_budget_ratio=1.0)
        decisions = scheduler.plan(
            [ExtractionCandidate("high", 10.0), ExtractionCandidate("low", 1.0)],
            configured_budget_us=8.0,
        )
        self.assertLessEqual(sum(item.estimated_cost_us for item in decisions), 8.0)
        self.assertEqual([item.key for item in decisions], ["high", "low"])
        self.assertTrue(all(item.tier == "flow" for item in decisions))

    def test_feedback_reduces_effective_budget_under_pressure(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=0.8)
        scheduler.observe("flow", measured_cost_us=8.0, realized_utility=1.0, utilization=1.6)
        self.assertLess(scheduler.effective_budget(100.0), 100.0)

    def test_key_flow_is_reserved_before_higher_priority_ordinary_flow(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=1.0, min_budget_ratio=1.0, max_budget_ratio=1.0)
        plan = scheduler.plan_with_audit(
            [
                ExtractionCandidate("ordinary", 100.0),
                ExtractionCandidate("key", 1.0, is_key_flow=True),
            ],
            configured_budget_us=4.0,
        )
        self.assertEqual([item.key for item in plan.decisions], ["key"])
        self.assertEqual(plan.key_flow_coverage, 1.0)
        self.assertEqual(plan.budget_overrun_count, 0)

    def test_pressure_reduction_does_not_create_avoidable_key_flow_gap(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=0.8)
        scheduler.observe("flow", measured_cost_us=20.0, realized_utility=1.0, utilization=2.0)
        plan = scheduler.plan_with_audit(
            [ExtractionCandidate("key", 1.0, is_key_flow=True)],
            configured_budget_us=100.0,
            allow_deep=False,
        )
        self.assertEqual(plan.key_flow_coverage, 1.0)
        self.assertLessEqual(plan.effective_budget_us, 100.0)
        self.assertEqual(plan.budget_overrun_count, 0)

    def test_fallback_disables_deep_tier_and_is_auditable(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=1.0, min_budget_ratio=1.0, max_budget_ratio=1.0)
        plan = scheduler.plan_with_audit(
            [ExtractionCandidate("key", 10.0, is_key_flow=True)],
            configured_budget_us=100.0,
            allow_deep=False,
        )
        self.assertTrue(plan.fallback_active)
        self.assertTrue(all(item.tier == "flow" for item in plan.decisions))
        self.assertEqual(plan.key_flow_coverage, 1.0)

    def test_half_open_probe_reclaims_budget_without_exceeding_configured_cap(self):
        scheduler = AdaptiveBudgetScheduler(target_utilization=0.8)
        scheduler.observe("flow", measured_cost_us=4.0, realized_utility=1.0, utilization=2.0)
        self.assertEqual(scheduler.effective_budget(100.0), 40.0)
        plan = scheduler.plan_with_audit(
            [ExtractionCandidate("key", 1.0, is_key_flow=True)],
            configured_budget_us=100.0,
            allow_deep=True,
            recovery_probe=True,
        )
        self.assertEqual(plan.decisions[0].tier, "deep")
        self.assertLessEqual(plan.estimated_used_us, 100.0)
        self.assertLessEqual(plan.effective_budget_us, 100.0)
        self.assertEqual(plan.budget_overrun_count, 0)


if __name__ == "__main__":
    unittest.main()

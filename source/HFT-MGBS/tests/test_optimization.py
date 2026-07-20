import unittest

from hft_mgbs.optimization import CandidateMetrics, ConstraintProfile, ParetoOptimizer


def profile():
    return ConstraintProfile(
        target_load_mpps=1.0,
        max_packet_drop_count=0,
        max_p99_latency_us=200.0,
        max_p999_latency_us=400.0,
        max_cpu_utilization=0.85,
        max_gpu_utilization=0.85,
        max_memory_utilization=0.85,
        max_gpu_memory_utilization=0.85,
        max_budget_overrun_count=0,
        min_key_flow_coverage=0.99,
        max_fallback_recovery_s=2.0,
    )


def candidate(name, **overrides):
    values = dict(
        name=name,
        quality=0.92,
        gain_per_cost=1.0,
        throughput_mpps=1.2,
        packet_drop_count=0,
        p99_latency_us=150.0,
        p999_latency_us=300.0,
        cpu_utilization=0.60,
        gpu_utilization=0.50,
        memory_utilization=0.50,
        gpu_memory_utilization=0.40,
        budget_overrun_count=0,
        key_flow_coverage=0.995,
        fallback_recovery_s=1.0,
        complexity=0.40,
    )
    values.update(overrides)
    return CandidateMetrics(**values)


class ParetoOptimizationTests(unittest.TestCase):
    def test_high_accuracy_is_rejected_when_hard_constraints_fail(self):
        unsafe = candidate(
            "accuracy_only",
            quality=0.999,
            packet_drop_count=1,
            p99_latency_us=250.0,
            key_flow_coverage=0.95,
        )
        safe = candidate("balanced")
        selection = ParetoOptimizer(profile()).select([unsafe, safe])
        audit = next(item for item in selection.audits if item.candidate.name == "accuracy_only")
        self.assertFalse(audit.feasible)
        self.assertEqual(
            {item.constraint for item in audit.violations},
            {"packet_drop_count", "p99_latency_us", "key_flow_coverage"},
        )
        self.assertEqual(selection.champion.name, "balanced")

    def test_budget_resource_and_fallback_violations_are_hard_failures(self):
        unsafe = candidate(
            "unsafe",
            cpu_utilization=0.90,
            budget_overrun_count=2,
            fallback_recovery_s=3.0,
        )
        audit = ParetoOptimizer(profile()).audit(unsafe)
        self.assertEqual(
            {item.constraint for item in audit.violations},
            {"cpu_utilization", "budget_overrun_count", "fallback_recovery_s"},
        )

    def test_dominated_candidate_is_removed_from_front(self):
        strong = candidate("strong", quality=0.94, gain_per_cost=1.2, p99_latency_us=120.0)
        weak = candidate("weak", quality=0.90, gain_per_cost=0.8, p99_latency_us=180.0)
        selection = ParetoOptimizer(profile()).select([weak, strong])
        self.assertEqual([item.name for item in selection.pareto_front], ["strong"])

    def test_tradeoff_candidates_both_remain_on_front(self):
        quality = candidate("quality", quality=0.96, gain_per_cost=0.8, p99_latency_us=180.0)
        efficiency = candidate(
            "efficiency",
            quality=0.90,
            gain_per_cost=1.4,
            p99_latency_us=100.0,
            cpu_utilization=0.40,
            gpu_utilization=0.20,
        )
        selection = ParetoOptimizer(profile()).select([quality, efficiency])
        self.assertEqual({item.name for item in selection.pareto_front}, {"quality", "efficiency"})
        self.assertIsNotNone(selection.champion)

    def test_no_champion_when_every_candidate_is_infeasible(self):
        selection = ParetoOptimizer(profile()).select([candidate("slow", throughput_mpps=0.5)])
        self.assertEqual(selection.pareto_front, ())
        self.assertIsNone(selection.champion)


if __name__ == "__main__":
    unittest.main()

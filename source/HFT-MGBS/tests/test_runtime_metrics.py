import unittest

from hft_mgbs.runtime_metrics import RuntimeMetricsCollector, parse_nvidia_smi_sample, percentile
from hft_mgbs.scheduler import SchedulePlan


class RuntimeMetricsTests(unittest.TestCase):
    def test_percentile_interpolation(self):
        self.assertEqual(percentile([1.0, 2.0, 3.0], 0.5), 2.0)
        self.assertAlmostEqual(percentile([0.0, 100.0], 0.99), 99.0)

    def test_collector_aggregates_schedule_evidence(self):
        collector = RuntimeMetricsCollector()
        plan = SchedulePlan((), 10.0, 4.0, 0, 2, 2, 1.0, True)
        collector.record(100.0, 10, plan)
        summary = collector.summary()
        self.assertEqual(summary["packets_processed"], 10)
        self.assertEqual(summary["key_flow_coverage"], 1.0)
        self.assertEqual(summary["fallback_batches"], 1)
        self.assertEqual(summary["budget_overrun_count"], 0)
        self.assertEqual(summary["estimated_budget_overrun_count"], 0)
        self.assertEqual(summary["actual_budget_overrun_count"], 0)
        self.assertEqual(summary["actual_budget_overrun_batch_indices"], [])
        self.assertEqual(summary["actual_optional_cost_us"]["max"], 0.0)
        self.assertEqual(summary["tier_decision_counts"], {"base": 0, "deep": 0, "flow": 0})

    def test_parses_nvidia_smi_sample(self):
        sample = parse_nvidia_smi_sample("75, 2048, 8192")
        self.assertEqual(sample["gpu_utilization"], 0.75)
        self.assertEqual(sample["gpu_memory_utilization"], 0.25)


if __name__ == "__main__":
    unittest.main()

import unittest

from hft_mgbs.experiment import summarize_offline_runs


def run(throughput, p99, resource, coverage=1.0):
    return {
        "runtime": {
            "throughput_mpps": throughput,
            "batch_latency_us": {"p99": p99, "p999": p99 * 1.1},
            "process_cpu_utilization_total_capacity": resource,
            "memory_utilization": resource / 2,
            "budget_overrun_count": 0,
            "key_flow_coverage": coverage,
            "fallback_batches": 0,
        },
        "gpu": {
            "gpu_utilization_max": resource / 3,
            "gpu_memory_utilization_max": resource / 4,
        },
        "evidence_scope": {
            "processing_latency_verified": True,
            "application_budget_verified": True,
            "key_flow_coverage_verified": True,
            "gpu_resource_verified": True,
        },
    }


class ExperimentAggregationTests(unittest.TestCase):
    def test_uses_worst_repeat_and_never_marks_offline_as_final(self):
        named = [
            ("normal_batch512_budget5000_repeat1.json", run(1.2, 100, 0.4)),
            ("normal_batch512_budget5000_repeat2.json", run(1.0, 120, 0.5)),
            ("normal_batch512_budget5000_repeat3.json", run(1.1, 110, 0.45, 0.99)),
        ]
        summary = summarize_offline_runs(named)
        candidate = summary["candidates"][0]
        self.assertEqual(candidate["throughput_mpps_min"], 1.0)
        self.assertEqual(candidate["p99_latency_us_max"], 120)
        self.assertEqual(candidate["resource_pressure_max"], 0.5)
        self.assertEqual(candidate["key_flow_coverage_min"], 0.99)
        self.assertFalse(candidate["final_pareto_eligible"])
        self.assertIn("nic_packet_drop", candidate["missing_final_evidence"])

    def test_repeat_gate_excludes_incomplete_candidate_from_front(self):
        named = [
            ("fallback_batch512_budget5000_repeat1.json", run(2.0, 50, 0.2)),
            ("fallback_batch512_budget5000_repeat2.json", run(2.0, 50, 0.2)),
        ]
        summary = summarize_offline_runs(named)
        self.assertFalse(summary["candidates"][0]["repeat_gate_passed"])
        self.assertEqual(summary["preselection_front"], [])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from hft_mgbs.resource_sampling import (
    descendant_pids,
    parse_proc_stat,
    parse_proc_status,
    summarize_process_samples,
)
from hft_mgbs.resource_evidence import aggregate_resource_evidence


class ResourceSamplingTest(unittest.TestCase):
    def test_proc_parsers_handle_spaces_and_units(self):
        stat = (
            "42 (python worker) S 7 0 0 0 0 0 0 0 0 0 11 13 "
            "0 0 0 0 0 0"
        )
        parent, ticks = parse_proc_stat(stat)
        status = parse_proc_status(
            "VmRSS:\t123 kB\nThreads:\t4\nCpus_allowed_list:\t0-3\n"
        )

        self.assertEqual(parent, 7)
        self.assertEqual(ticks, 24)
        self.assertEqual(status["rss_bytes"], 123 * 1024)
        self.assertEqual(status["threads"], 4)
        self.assertEqual(status["cpu_set"], "0-3")

    def test_descendant_closure_is_exact(self):
        records = {
            10: {"parent_pid": 1},
            11: {"parent_pid": 10},
            12: {"parent_pid": 11},
            20: {"parent_pid": 1},
        }

        self.assertEqual(descendant_pids(records, 10), {10, 11, 12})

    def test_summary_uses_interval_max_and_total_capacity(self):
        samples = [
            {
                "monotonic_s": 10.0,
                "cpu_ticks": 100,
                "rss_bytes": 1000,
                "threads": 2,
                "service_pid": 11,
                "service_cpu_set": "0-3",
                "pids": [10, 11],
            },
            {
                "monotonic_s": 11.0,
                "cpu_ticks": 300,
                "rss_bytes": 2000,
                "threads": 3,
                "service_pid": 11,
                "service_cpu_set": "0-3",
                "pids": [10, 11],
            },
            {
                "monotonic_s": 12.0,
                "cpu_ticks": 350,
                "rss_bytes": 1500,
                "threads": 2,
                "service_pid": 11,
                "service_cpu_set": "0-3",
                "pids": [10, 11],
            },
        ]

        summary = summarize_process_samples(samples, 8, 100, 10000)

        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["cpu_cores_used_max"], 2.0)
        self.assertEqual(summary["host_cpu_fraction_max"], 0.25)
        self.assertEqual(summary["rss_bytes_max"], 2000)
        self.assertEqual(summary["host_memory_fraction_max"], 0.2)
        self.assertEqual(summary["threads_max"], 3)

    def test_repeat_audit_uses_worst_case(self):
        def run(cpu, gpu):
            return {
                "scope": "split_inference_node_resource_sampling",
                "accepted": True,
                "final_pareto_ingestion_allowed": False,
                "candidate_id": "A09",
                "runtime_candidate": "thread_cpu0_3",
                "algorithm_device": "cpu",
                "gpu_required": False,
                "manifest_sha256": "a" * 64,
                "resource_limits_sha256": "b" * 64,
                "process": {
                    "sample_count": 100,
                    "cpu_cores_used_max": cpu,
                    "host_cpu_fraction_max": cpu / 80,
                    "rss_bytes_max": 200,
                    "host_memory_fraction_max": 0.01,
                    "threads_max": 4,
                    "process_tree_pid_count_max": 2,
                },
                "gpu": {
                    "sample_count": 20,
                    "system_gpu_utilization_fraction_max": gpu,
                    "system_gpu_memory_fraction_max": 0.02,
                    "service_gpu_process_present": False,
                    "service_gpu_utilization_fraction_max": 0.0,
                    "service_gpu_memory_fraction_max": 0.0,
                    "service_gpu_memory_mib_max": 0.0,
                },
            }

        result = aggregate_resource_evidence(
            [run(1.0, 0.0), run(2.0, 0.1), run(1.5, 0.05)]
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(result["run_count"], 3)
        self.assertEqual(
            result["observed_worst_case"]["cpu_cores_used_max"], 2.0
        )
        self.assertEqual(
            result["observed_worst_case"][
                "system_gpu_utilization_fraction_max"
            ],
            0.1,
        )


if __name__ == "__main__":
    unittest.main()

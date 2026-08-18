import unittest

from scripts.summarize_xdp_load_exploration import _dominates


class XdpLoadExplorationTest(unittest.TestCase):
    def test_dominance_requires_no_worse_resource_and_latency(self):
        low = {
            "observed_mpps_min": 0.1,
            "kernel_to_feature_p99_us": 4000,
            "gpu_batch_p99_us": 80000,
            "maximum_rss_kib": 900000,
        }
        higher_but_slower = {
            "observed_mpps_min": 0.2,
            "kernel_to_feature_p99_us": 5000,
            "gpu_batch_p99_us": 85000,
            "maximum_rss_kib": 910000,
        }
        strictly_better = {
            "observed_mpps_min": 0.2,
            "kernel_to_feature_p99_us": 3000,
            "gpu_batch_p99_us": 70000,
            "maximum_rss_kib": 850000,
        }
        self.assertFalse(_dominates(higher_but_slower, low))
        self.assertTrue(_dominates(strictly_better, low))


if __name__ == "__main__":
    unittest.main()

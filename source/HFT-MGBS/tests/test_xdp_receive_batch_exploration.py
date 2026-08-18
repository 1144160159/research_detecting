import unittest

from scripts.summarize_xdp_receive_batch_exploration import _dominates


class XdpReceiveBatchExplorationTest(unittest.TestCase):
    def test_dominance_requires_all_costs_to_be_no_worse(self):
        baseline = {
            "kernel_to_feature_p99_us": 9000,
            "kernel_to_feature_p999_us": 20000,
            "gpu_batch_p99_us": 60000,
            "maximum_rss_kib": 900000,
        }
        lower_p99_but_more_memory = {
            "kernel_to_feature_p99_us": 8000,
            "kernel_to_feature_p999_us": 20000,
            "gpu_batch_p99_us": 60000,
            "maximum_rss_kib": 910000,
        }
        strictly_better = {
            "kernel_to_feature_p99_us": 8000,
            "kernel_to_feature_p999_us": 19000,
            "gpu_batch_p99_us": 59000,
            "maximum_rss_kib": 890000,
        }
        self.assertFalse(_dominates(lower_p99_but_more_memory, baseline))
        self.assertTrue(_dominates(strictly_better, baseline))


if __name__ == "__main__":
    unittest.main()

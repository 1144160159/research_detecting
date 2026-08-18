import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_xdp_fastpath_probe import summarize


class XdpFastpathProbeSummaryTest(unittest.TestCase):
    def test_zero_drop_matching_probe_passes_r0_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            (run / "frozen_thresholds.json").write_text(
                json.dumps(
                    {
                        "candidate_id": "R0",
                        "target_load_mpps": 0.5,
                        "max_raw_capture_p99_us": 100,
                        "max_raw_capture_p999_us": 500,
                    }
                ),
                encoding="utf-8",
            )
            (run / "probe_metrics.json").write_text(
                json.dumps(
                    {
                        "packets": 100,
                        "capture_packets_dropped": 0,
                        "process_cpu_cores_average": 1.0,
                        "queue_packets": [100],
                        "latency_sample_stride": 1,
                        "kernel_entry_to_borrowed_callback_latency": {
                            "p99_us": 80,
                            "p999_us": 120,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (run / "injector_metrics.json").write_text(
                json.dumps(
                    {
                        "offered_packets": 100,
                        "observed_mpps_min_1s": 0.51,
                    }
                ),
                encoding="utf-8",
            )
            result = summarize(run)
            self.assertTrue(result["r0_capture_only_qualified"])
            self.assertFalse(result["full_pipeline_qualified"])


if __name__ == "__main__":
    unittest.main()

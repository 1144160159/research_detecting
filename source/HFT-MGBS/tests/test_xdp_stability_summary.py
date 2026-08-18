from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_xdp_stability import summarize


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


class XdpStabilitySummaryTest(unittest.TestCase):
    def test_three_passing_runs_prefer_xdp_but_not_final_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = []
            metrics = {
                "packets_received": 100,
                "capture_packets_dropped": 0,
                "parse_reject_rate": 0.0,
                "key_flow_coverage": 1.0,
                "gpu_flows_scored": 10,
                "kernel_receive_to_feature_enqueue_latency": {
                    "p99_us": 100,
                    "p999_us": 200,
                },
                "flow_materialization_to_feature_enqueue_latency": {
                    "p99_us": 50
                },
                "gpu_batch_round_trip_latency": {
                    "p99_us": 1000,
                    "p999_us": 2000,
                },
            }
            for index in range(3):
                run = root / "run{}".format(index)
                run.mkdir()
                (run / "manifest.txt").write_text(
                    "capture_exit_status=0\ninjector_exit_status=0\n"
                    "live_composition_exit_status=0\n",
                    encoding="utf-8",
                )
                write_json(run / "metrics.json", metrics)
                write_json(
                    run / "injector_metrics.json",
                    {"offered_packets": 100},
                )
                write_json(
                    run / "live_evidence.diagnostic.json",
                    {"composition": {"diagnostic_accepted": True}},
                )
                runs.append(run)
            baseline = root / "af"
            baseline.mkdir()
            write_json(baseline / "metrics.json", metrics)
            native = root / "native"
            native.mkdir()
            (native / "capture_stderr.log").write_text(
                "Operation not supported", encoding="utf-8"
            )

            result = summarize(runs, baseline, native)

        self.assertTrue(result["all_runs_passed"])
        self.assertEqual(
            result["preferred_capture_driver"], "xdp-skb"
        )
        self.assertEqual(
            result["fallback_capture_driver"], "af-packet-ts"
        )
        self.assertFalse(result["final_selection_allowed"])


if __name__ == "__main__":
    unittest.main()

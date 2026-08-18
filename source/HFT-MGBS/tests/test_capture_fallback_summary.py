import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_capture_fallback import summarize


class CaptureFallbackSummaryTest(unittest.TestCase):
    def test_valid_runtime_fallback_is_diagnostic_only(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "manifest.txt").write_text(
                "\n".join(
                    [
                        "evidence_scope=physical_link_live_diagnostic",
                        "diagnostic_only=true",
                        "capture_driver=xdp-skb",
                        "capture_fallback_driver=af-packet-ts",
                        "diagnostic_xdp_fail_after_packets=50000",
                        "capture_exit_status=0",
                        "injector_exit_status=0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (run / "metrics.json").write_text(
                json.dumps(
                    {
                        "capture_driver": "xdp_skb_to_af_packet_ts",
                        "capture_driver_fallback_count": 1,
                        "capture_driver_fallback_recovery_ms": 2.5,
                        "capture_driver_fallback_reason": (
                            "primary_poll_failed: injected"
                        ),
                        "capture_driver_fallback_packets": 5000,
                        "packets_received": 55000,
                        "capture_packets_dropped": 0,
                    }
                ),
                encoding="utf-8",
            )
            (run / "injector_metrics.json").write_text(
                json.dumps({"offered_packets": 55010}), encoding="utf-8"
            )
            (run / "fallback_post_ip_link.json").write_text(
                json.dumps([{"promiscuity": 0}]), encoding="utf-8"
            )
            (run / "fallback_post_bpftool.txt").write_text(
                "xdp:\n\ntc:\n", encoding="utf-8"
            )
            (run / "fallback_post_ethtool_features.txt").write_text(
                "generic-receive-offload: on\n", encoding="utf-8"
            )
            result = summarize(run, 300.0)
            self.assertTrue(result["accepted"])
            self.assertTrue(
                result[
                    "capture_driver_runtime_fallback_evidence_complete"
                ]
            )
            self.assertFalse(result["production_fallback_evidence_complete"])
            self.assertFalse(result["final_pareto_ingestion_allowed"])


if __name__ == "__main__":
    unittest.main()

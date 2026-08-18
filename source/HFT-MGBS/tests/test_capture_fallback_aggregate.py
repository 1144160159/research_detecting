import json
import tempfile
import unittest
from pathlib import Path

from scripts.aggregate_capture_fallback import aggregate


class CaptureFallbackAggregateTest(unittest.TestCase):
    def test_three_runs_use_worst_recovery_and_do_not_reuse_zero_drop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, recovery in enumerate((100.0, 120.0, 110.0), start=1):
                path = root / f"run{index}.json"
                path.write_text(
                    json.dumps(
                        {
                            "accepted": True,
                            "capture_driver_runtime_fallback_evidence_complete": True,
                            "normal_path_zero_drop_evidence_reused": False,
                            "observed": {
                                "fallback_count": 1,
                                "fallback_recovery_ms": recovery,
                                "fallback_packets": 1000,
                                "fallback_transition_packet_gap": 100,
                                "post_promiscuity": 0,
                                "post_xdp_program_absent": True,
                                "post_gro_restored": True,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                paths.append(path)
            result = aggregate(paths)
            self.assertTrue(result["accepted"])
            self.assertEqual(
                result["observed_worst_case"]["fallback_recovery_ms_max"],
                120.0,
            )
            self.assertFalse(result["normal_path_zero_drop_evidence_reused"])
            self.assertFalse(result["production_fallback_evidence_complete"])


if __name__ == "__main__":
    unittest.main()

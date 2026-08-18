import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.summarize_xdp_joint_resources import summarize


class XdpJointResourceSummaryTest(unittest.TestCase):
    def make_pair(self, root: Path, index: int, resource_start_offset: float = 2.0):
        run = root / f"physical{index}"
        run.mkdir()
        (run / "manifest.txt").write_text(
            "\n".join(
                [
                    "capture_driver=xdp-skb",
                    "capture_exit_status=0",
                    "injector_exit_status=0",
                    "live_composition_exit_status=0",
                    "started_at=2026-07-30T08:00:00Z",
                    "ended_at=2026-07-30T08:00:20Z",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (run / "metrics.json").write_text(
            json.dumps({"capture_packets_dropped": 0}), encoding="utf-8"
        )
        (run / "live_evidence.diagnostic.json").write_text(
            json.dumps({"composition": {"diagnostic_accepted": True}}),
            encoding="utf-8",
        )
        (run / "physical_process_time.txt").write_text(
            "\tMaximum resident set size (kbytes): 1000\n", encoding="utf-8"
        )
        resource = root / f"resource{index}.json"
        generated_at = (
            datetime(2026, 7, 30, 8, 0, 0, tzinfo=timezone.utc)
            + timedelta(seconds=resource_start_offset + 15)
        ).isoformat()
        resource.write_text(
            json.dumps(
                {
                    "accepted": True,
                    "candidate_id": "A09",
                    "runtime_candidate": "thread_all",
                    "duration_s": 15.0,
                    "generated_at": generated_at,
                }
            ),
            encoding="utf-8",
        )
        return run, resource

    def test_three_concurrent_pairs_complete_diagnostic_resource_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pairs = [self.make_pair(root, index) for index in range(3)]
            resource_summary = root / "resource_summary.json"
            resource_summary.write_text(
                json.dumps(
                    {
                        "accepted": True,
                        "run_count": 3,
                        "identity": {"candidate_id": "A09"},
                        "observed_worst_case": {"cpu_cores_used_max": 1.1},
                    }
                ),
                encoding="utf-8",
            )
            result = summarize(
                [pair[0] for pair in pairs],
                [pair[1] for pair in pairs],
                resource_summary,
                12.0,
            )
            self.assertTrue(result["accepted"])
            self.assertTrue(result["diagnostic_resource_evidence_complete"])
            self.assertFalse(result["production_resource_evidence_complete"])
            self.assertFalse(result["final_pareto_ingestion_allowed"])


if __name__ == "__main__":
    unittest.main()

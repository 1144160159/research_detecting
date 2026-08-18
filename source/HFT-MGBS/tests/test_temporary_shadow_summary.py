import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.summarize_temporary_shadow_matrix import CANDIDATES, summarize


class TemporaryShadowSummaryTest(unittest.TestCase):
    def _write_campaign(self, root, overrides=None):
        overrides = overrides or {}
        values = {
            "shadow_b128_f1000": (4900.0, 80000.0, 4.0),
            "shadow_b64_f500": (3500.0, 70000.0, 2.5),
            "shadow_b32_f250": (3000.0, 75000.0, 3.0),
        }
        for candidate, parameters in CANDIDATES.items():
            internal, gpu, packet = values[candidate]
            internal = overrides.get(candidate, internal)
            for repeat in range(1, 4):
                run_dir = root / f"{candidate}_r{repeat}"
                run_dir.mkdir(parents=True)
                (run_dir / "scope.env").write_text(
                    "\n".join(
                        (
                            f"runtime_candidate={candidate}",
                            f"batch_size={parameters['batch_size']}",
                            (
                                "feature_flush_us="
                                f"{parameters['feature_flush_us']}"
                            ),
                            "max_duration_s=15",
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )
                metrics = {
                    "packets_received": 1000 + repeat,
                    "capture_drop_rate": 0.0,
                    "parse_reject_rate": 0.0001,
                    "key_flow_coverage": 1.0,
                    "gpu_flows_scored": 10,
                    "gpu_batches_failed": 0,
                    "gpu_queue_full": 0,
                    "fallback_flows": 0,
                    "budget_overrun_count": 0,
                    "flow_materialization_to_feature_enqueue_latency": {
                        "p99_us": internal
                    },
                    "gpu_batch_round_trip_latency": {"p99_us": gpu},
                    "packet_processing_latency": {"p99_us": packet},
                }
                (run_dir / "metrics.json").write_text(
                    json.dumps(metrics),
                    encoding="utf-8",
                )

    def test_selects_only_after_hard_gates_and_pareto(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_campaign(root)

            result = summarize(root)

        self.assertEqual(result["candidate_count"], 3)
        self.assertEqual(result["total_run_count"], 9)
        self.assertEqual(result["eligible_candidate_count"], 3)
        self.assertEqual(
            result["diagnostic_pareto_front"],
            ["shadow_b32_f250", "shadow_b64_f500"],
        )
        self.assertEqual(result["selected_candidate"], "shadow_b64_f500")
        self.assertEqual(
            result["candidates"][0]["duration_s_min"],
            15,
        )
        self.assertIn("minimize_max_normalized", result["selection_policy"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_worst_repeat_over_gate_rejects_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_campaign(
                root,
                overrides={"shadow_b128_f1000": 6000.0},
            )

            result = summarize(root)

        rejected = next(
            item
            for item in result["candidates"]
            if item["candidate_id"] == "shadow_b128_f1000"
        )
        self.assertFalse(rejected["eligible"])
        self.assertIn(
            "internal_feature_enqueue_p99_us",
            rejected["gate_errors"],
        )

    def test_can_confirm_one_frozen_candidate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_campaign(root)

            result = summarize(root, ["shadow_b128_f1000"])

        self.assertEqual(
            result["scope"],
            "temporary_management_interface_runtime_confirmation",
        )
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["total_run_count"], 3)
        self.assertEqual(result["selected_candidate"], "shadow_b128_f1000")


if __name__ == "__main__":
    unittest.main()

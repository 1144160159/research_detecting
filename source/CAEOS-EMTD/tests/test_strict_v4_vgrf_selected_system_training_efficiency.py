from __future__ import annotations

import unittest

from run_strict_v4_vgrf_selected_system_training_efficiency import (
    phase_metrics,
    sentinel_records,
)


class VGRFSelectedSystemTrainingEfficiencyTests(unittest.TestCase):
    def test_exact_fourteen_sentinel_pairs(self) -> None:
        sentinels = {
            f"suite_{index}": f"scenario_{index}"
            for index in range(7)
        }
        records = [
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
            }
            for suite, scenario in sentinels.items()
            for seed in (311, 313)
        ]
        protocol = {
            "training_calibration_efficiency": {
                "sentinel_scenarios": sentinels
            },
            "source_registry": records,
        }
        self.assertEqual(len(sentinel_records(protocol)), 14)

    def test_missing_sentinel_pair_fails_closed(self) -> None:
        sentinels = {
            f"suite_{index}": f"scenario_{index}"
            for index in range(7)
        }
        protocol = {
            "training_calibration_efficiency": {
                "sentinel_scenarios": sentinels
            },
            "source_registry": [
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": 311,
                }
                for suite, scenario in sentinels.items()
            ],
        }
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            sentinel_records(protocol)

    def test_vgrf_build_is_counted_as_calibration(self) -> None:
        manifest = {
            "phase_timings": {
                "feature_preparation_seconds": 2.0,
                "training_seconds": 3.0,
                "calibration_seconds": 4.0,
            },
            "peak_gpu_memory_mb": 0.0,
            "peak_host_rss_mb": 100.0,
        }
        result = phase_metrics(
            manifest,
            artifact_bytes=123,
            extra_calibration_seconds=5.0,
        )
        self.assertEqual(result["calibration_seconds"], 9.0)
        self.assertEqual(result["total_fit_seconds"], 14.0)
        self.assertEqual(
            result["serialized_deployment_artifact_bytes"], 123.0
        )

    def test_workflow_peak_rss_overrides_training_process_peak(self) -> None:
        manifest = {
            "phase_timings": {
                "feature_preparation_seconds": 2.0,
                "training_seconds": 3.0,
                "calibration_seconds": 4.0,
            },
            "peak_gpu_memory_mb": 0.0,
            "peak_host_rss_mb": 100.0,
        }
        result = phase_metrics(
            manifest,
            artifact_bytes=123,
            peak_host_rss_mb=150.0,
        )
        self.assertEqual(result["peak_host_rss_mb"], 150.0)


if __name__ == "__main__":
    unittest.main()

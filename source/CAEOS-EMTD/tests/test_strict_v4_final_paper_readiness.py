import unittest

from audit_strict_v4_final_paper_readiness import efficiency_superiority


def efficiency_fixture(ratio: float) -> dict:
    paired = {
        metric: {"bootstrap_95ci": [ratio, ratio]}
        for metric in (
            "latency_p50_ms",
            "latency_p95_ms",
            "latency_p99_ms",
            "samples_per_second",
        )
    }
    return {
        "inference": {
            "native_primary": {
                "by_batch_size": {
                    str(batch): {"paired": paired} for batch in (1, 64, 512)
                }
            }
        },
        "training": {
            "paired_candidate_over_comparator": {
                metric: {"bootstrap_95ci": [ratio, ratio]}
                for metric in (
                    "total_fit_seconds",
                    "deployment_artifact_bytes",
                    "peak_host_rss_mb",
                )
            }
        },
    }


class FinalPaperReadinessTests(unittest.TestCase):
    def test_efficiency_superiority_requires_directional_ci(self) -> None:
        fixture = efficiency_fixture(0.5)
        for batch in fixture["inference"]["native_primary"]["by_batch_size"].values():
            batch["paired"]["samples_per_second"]["bootstrap_95ci"] = [2.0, 2.0]
        self.assertTrue(efficiency_superiority(fixture)["passes"])

    def test_slow_candidate_fails_efficiency_superiority(self) -> None:
        self.assertFalse(efficiency_superiority(efficiency_fixture(2.0))["passes"])


if __name__ == "__main__":
    unittest.main()

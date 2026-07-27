from __future__ import annotations

import unittest

from analyze_strict_v4_missing_aware_fallback_development import (
    METRICS,
    degradation,
    report_metrics,
    summarize,
)


class MissingAwareFallbackDevelopmentTests(unittest.TestCase):
    def test_fpr95_degradation_is_oriented_as_increase(self) -> None:
        clean = {"unknown_fpr95": 0.2}
        corrupt = {"unknown_fpr95": 0.3}
        self.assertAlmostEqual(
            degradation(clean, corrupt, "unknown_fpr95"), 0.1
        )

    def test_report_requires_all_finite_metrics(self) -> None:
        report = {metric: 0.5 for metric in METRICS}
        self.assertEqual(report_metrics(report), report)
        report["oscr"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            report_metrics(report)

    def test_clean_fallback_and_improvement_admit_component(self) -> None:
        suites = {"suite": 1}
        families = [
            "modality_missing",
            "field_missing",
            "row_missing",
            "feature_shuffle",
            "gaussian_drift",
        ]
        protocol = {
            "corruption_families": families,
            "maximum_mean_degradation": {
                metric: 0.2 for metric in METRICS
            },
        }
        candidate = {
            family: {
                "suite": {metric: [0.05] for metric in METRICS}
            }
            for family in families
        }
        incumbent = {
            family: {
                "suite": {metric: [0.3] for metric in METRICS}
            }
            for family in families
        }
        result = summarize(
            protocol=protocol,
            suite_counts=suites,
            candidate=candidate,
            incumbent=incumbent,
            clean_differences={metric: [0.0] for metric in METRICS},
            observed_runs=510,
        )
        self.assertTrue(result["passes_development_admission"])
        self.assertEqual(
            result["decision"],
            "admit_missing_aware_fallback_to_new_seed_component_confirmation",
        )


if __name__ == "__main__":
    unittest.main()

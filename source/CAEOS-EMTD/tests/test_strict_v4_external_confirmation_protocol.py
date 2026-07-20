from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import create_protocol


def inputs() -> tuple[dict, dict, dict]:
    summary = {
        "schema_version": "strict_v4_full103_coverage_summary_v1",
        "coverage_manifest_sha256": "coverage",
        "baseline_manifest_sha256": "baselines",
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "method_count": 22,
            "independent_baseline_run_checks": 204,
            "split_fingerprints_identical": True,
        },
        "overall": [
            {"method": "caeos_pairwise", "mean_unknown_metric_rank": 1.0},
            {"method": "opendetect", "mean_unknown_metric_rank": 3.0},
            {"method": "mlp_knn", "mean_unknown_metric_rank": 2.5},
            {"method": "isolation_forest", "mean_unknown_metric_rank": 8.0},
        ],
    }
    coverage = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "manifest_sha256": "coverage",
    }
    router_protocol = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "manifest_sha256": "router-protocol",
        "confirmation_seeds": [137, 139, 149],
    }
    return summary, coverage, router_protocol


class StrictV4ExternalConfirmationProtocolTests(unittest.TestCase):
    def test_freezes_best_non_caeos_method(self) -> None:
        result = create_protocol(*inputs())
        self.assertEqual(result["selected_comparator"], "mlp_knn")
        self.assertEqual(
            result["selected_comparator_run_source"],
            "existing_mlp_confirmation_runs",
        )
        self.assertEqual(result["expected_comparator_runs"], 306)

    def test_tie_break_is_deterministic(self) -> None:
        summary, coverage, protocol = inputs()
        summary["overall"][1]["mean_unknown_metric_rank"] = 2.5
        result = create_protocol(summary, coverage, protocol)
        self.assertEqual(result["selected_comparator"], "mlp_knn")

    def test_incomplete_independent_baselines_fail_closed(self) -> None:
        summary, coverage, protocol = inputs()
        summary["validation"]["independent_baseline_run_checks"] = 203
        with self.assertRaisesRegex(ValueError, "incomplete"):
            create_protocol(summary, coverage, protocol)


if __name__ == "__main__":
    unittest.main()

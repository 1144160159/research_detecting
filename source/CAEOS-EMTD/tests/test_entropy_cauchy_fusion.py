from __future__ import annotations

import unittest

import numpy as np

from analyze_entropy_cauchy_fusion import (
    build_manifest,
    normalized_entropy_risk,
    reports_match,
)


class EntropyCauchyFusionTest(unittest.TestCase):
    def test_entropy_risk_replays_quantile_normalizer(self) -> None:
        validation = np.arange(100, dtype=np.float64)
        result = normalized_entropy_risk(validation, np.asarray([4.0, 49.5, 95.0]))
        low, high = np.quantile(validation, [0.05, 0.95])
        expected = np.clip((np.asarray([4.0, 49.5, 95.0]) - low) / (high - low), 0, 2)
        np.testing.assert_allclose(expected, result)

    def test_report_match_checks_every_primary_metric(self) -> None:
        report = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.4,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.5,
        }
        self.assertTrue(reports_match(report, report))
        changed = dict(report)
        changed["oscr"] += 0.01
        self.assertFalse(reports_match(report, changed))

    def test_manifest_freezes_non_entropy_fusion(self) -> None:
        screening = {
            "selected_candidate": "rank_union",
            "selection_rule": {"primary": "auroc"},
        }
        first = build_manifest(screening, {7, 11}, {67, 71}, "a" * 64)
        second = build_manifest(screening, {7, 11}, {67, 71}, "a" * 64)
        self.assertEqual(first, second)
        self.assertEqual("frozen_unconfirmed", first["status"])
        self.assertFalse(first["runtime_fusion_uses_unknown_or_test_labels"])


if __name__ == "__main__":
    unittest.main()

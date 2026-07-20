from __future__ import annotations

import unittest

from analyze_strict_v4_router_hypothesis_ceiling import analyze


def report(auroc: float, aupr: float, fpr95: float, oscr: float) -> dict:
    return {
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


class StrictV4RouterHypothesisCeilingTests(unittest.TestCase):
    def test_detects_incompatible_pairwise_and_union_frontier(self) -> None:
        raw = {
            "runs": [
                {
                    "suite": "suite",
                    "task": "attack_seed7",
                    "gate_report": report(0.8, 0.8, 0.4, 0.7),
                    "reports": {
                        "rank_union": report(0.9, 0.7, 0.2, 0.8),
                        "rank_mean": report(0.85, 0.75, 0.3, 0.75),
                    },
                }
            ]
        }
        router = {"routing": {"suite": {"method": "caeos_pairwise"}}}
        result = analyze(raw, router)
        self.assertEqual(result["enumerated_route_count"], 1)
        self.assertEqual(result["routes_dominating_metricwise_target"], 0)
        self.assertTrue(
            result["decision"]["fixed_suite_route_hypothesis_class_is_exhausted"]
        )

    def test_rejects_inconsistent_method_sets(self) -> None:
        base = report(0.8, 0.8, 0.4, 0.7)
        raw = {
            "runs": [
                {
                    "suite": "suite",
                    "task": "a_seed7",
                    "gate_report": base,
                    "reports": {"rank_union": base},
                },
                {
                    "suite": "suite",
                    "task": "b_seed7",
                    "gate_report": base,
                    "reports": {"rank_union": base, "rank_mean": base},
                },
            ]
        }
        router = {"routing": {"suite": {"method": "caeos_pairwise"}}}
        with self.assertRaisesRegex(ValueError, "method set differs"):
            analyze(raw, router)


if __name__ == "__main__":
    unittest.main()

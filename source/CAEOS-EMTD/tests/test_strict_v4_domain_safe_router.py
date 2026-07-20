from __future__ import annotations

import unittest

from select_strict_v4_domain_safe_router import FALLBACK, select_suite_method


def method(*gains: float) -> dict[str, object]:
    metrics = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
    return {
        "metrics": {
            name: {"oriented_mean_delta": gain}
            for name, gain in zip(metrics, gains)
        }
    }


class DomainSafeRouterTests(unittest.TestCase):
    def test_falls_back_when_every_candidate_regresses(self) -> None:
        name, gains = select_suite_method({
            "rank_union": method(0.1, -0.01, 0.2, 0.1),
            "rank_mean": method(-0.01, 0.1, 0.2, 0.1),
        })
        self.assertEqual(name, FALLBACK)
        self.assertEqual(set(gains.values()), {0.0})

    def test_maximizes_minimum_then_sum(self) -> None:
        name, _ = select_suite_method({
            "balanced": method(0.03, 0.03, 0.03, 0.03),
            "weak_tail": method(0.01, 0.20, 0.20, 0.20),
            "same_floor_more_sum": method(0.03, 0.04, 0.04, 0.04),
        })
        self.assertEqual(name, "same_floor_more_sum")


if __name__ == "__main__":
    unittest.main()

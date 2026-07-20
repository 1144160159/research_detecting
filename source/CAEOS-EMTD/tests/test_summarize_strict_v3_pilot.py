from __future__ import annotations

import unittest

from summarize_strict_v3_pilot import aggregate_table, build_summary


def metrics(auroc: float, aupr: float, fpr95: float, oscr: float):
    return {
        "known_macro_f1": 0.9,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


class SummarizeStrictV3PilotTest(unittest.TestCase):
    def blocks(self):
        return {
            "nf_unsw/a": {
                "caeos_current": metrics(0.7, 0.6, 0.5, 0.65),
                "caeos_rank_union": metrics(0.8, 0.7, 0.4, 0.66),
                "baseline": metrics(0.6, 0.5, 0.6, 0.55),
            },
            "cicids2017/b": {
                "caeos_current": metrics(0.72, 0.62, 0.48, 0.67),
                "caeos_rank_union": metrics(0.82, 0.72, 0.38, 0.68),
                "baseline": metrics(0.61, 0.51, 0.59, 0.56),
            },
        }

    def test_aggregate_ranks_lower_fpr95_in_correct_direction(self) -> None:
        table = aggregate_table(self.blocks())
        self.assertEqual("caeos_rank_union", table[0]["method"])
        candidate = next(row for row in table if row["method"] == "caeos_rank_union")
        self.assertEqual(1.0, candidate["metric_ranks"]["unknown_fpr95"])

    def test_generalization_gate_uses_oriented_deltas(self) -> None:
        summary = build_summary(self.blocks())
        gate = summary["rank_union_vs_current"]
        self.assertTrue(gate["development_generalization_gate"]["passes"])
        self.assertAlmostEqual(
            0.10, gate["oriented_mean_deltas"]["unknown_fpr95"]
        )


if __name__ == "__main__":
    unittest.main()

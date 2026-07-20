from __future__ import annotations

import unittest

from summarize_hcrp_osd_strict_v4_pilot import METHOD, build_summary, extend_table
from summarize_strict_v4_pilot import METRICS


def report(value: float) -> dict[str, float]:
    return {
        "known_macro_f1": value,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
    }


def row(method: str, value: float) -> dict[str, object]:
    return {
        "method": method,
        **report(value),
        "metric_ranks": {},
        "mean_unknown_metric_rank": 0.0,
    }


class HCRPOSDStrictV4PilotSummaryTests(unittest.TestCase):
    def test_extend_table_recomputes_ranks_with_hcrp(self) -> None:
        table = extend_table(
            [row("caeos", 0.8), row("baseline", 0.7)], report(0.9)
        )
        self.assertEqual(
            [entry["method"] for entry in table], [METHOD, "caeos", "baseline"]
        )
        self.assertEqual(table[0]["mean_unknown_metric_rank"], 1.0)

    def test_build_summary_expands_competitive_hcrp(self) -> None:
        existing = {
            "overall": [row("caeos", 0.8), row("baseline", 0.7)],
            "by_suite": {
                "cic_iot2023": [row("caeos", 0.8), row("baseline", 0.7)],
                "cic_ton_iot": [row("caeos", 0.8), row("baseline", 0.7)],
            },
        }
        blocks = {
            "cic_iot2023/a": {METHOD: report(0.9)},
            "cic_ton_iot/b": {METHOD: report(0.9)},
        }
        summary = build_summary(existing, blocks, {"passes": True})
        self.assertEqual(
            summary["budget_decision"]["state"], "expand_hcrp_multiseed"
        )
        self.assertEqual(
            summary["budget_decision"]["unknown_metric_wins_vs_caeos"],
            len(METRICS[1:]),
        )


if __name__ == "__main__":
    unittest.main()

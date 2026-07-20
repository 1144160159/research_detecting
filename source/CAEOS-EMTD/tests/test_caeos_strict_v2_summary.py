from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_caeos_strict_v2 import METRICS, build_summary


def write_metrics(root: Path, suite: str, scenario: str, value: float) -> None:
    run = root / suite / f"{scenario}_seed7"
    run.mkdir(parents=True, exist_ok=True)
    payload = {
        "seed": 7,
        "risk_selection": "gate",
        "selected_risk": "risk",
        "selected_report": {metric: value for metric in METRICS},
    }
    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")


class CaeosStrictV2SummaryTests(unittest.TestCase):
    def test_global_scenario_key_includes_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_metrics(root, "edge", "sql_injection", 0.2)
            write_metrics(root, "nf", "sql_injection", 0.8)
            summary = build_summary(
                root,
                (7,),
                {
                    "edge": {"sql_injection": "SQL Injection"},
                    "nf": {"sql_injection": "SQL Injection"},
                },
            )

        self.assertEqual(summary["state"], "complete")
        self.assertEqual(summary["global"]["scenario_count"], 2)
        self.assertAlmostEqual(
            summary["global"]["metrics"]["unknown_auroc"]["scenario_mean"],
            0.5,
        )
        self.assertEqual(
            set(summary["global"]["by_scenario"]),
            {"edge/sql_injection", "nf/sql_injection"},
        )


if __name__ == "__main__":
    unittest.main()

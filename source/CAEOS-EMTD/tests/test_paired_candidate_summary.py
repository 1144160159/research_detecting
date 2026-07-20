from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_paired_candidate import build_report


class PairedCandidateSummaryTest(unittest.TestCase):
    def test_pairs_selected_reports_and_orients_fpr95(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reference = root / "reference" / "hikari" / "probing_seed7"
            candidate = root / "candidate" / "hikari" / "probing_seed7"
            reference.mkdir(parents=True)
            candidate.mkdir(parents=True)
            base_report = {
                "known_macro_f1": 0.9,
                "unknown_auroc": 0.8,
                "unknown_aupr": 0.8,
                "unknown_fpr95": 0.4,
                "oscr": 0.8,
                "known_acceptance_rate": 0.9,
                "unknown_rejection_rate": 0.5,
            }
            new_report = {**base_report, "unknown_auroc": 0.85, "unknown_fpr95": 0.3}
            (reference / "metrics.json").write_text(
                json.dumps({"selected_risk": "old", "selected_report": base_report})
            )
            (candidate / "metrics.json").write_text(
                json.dumps({"selected_risk": "new", "selected_report": new_report})
            )
            report = build_report(root / "reference", root / "candidate")
            self.assertAlmostEqual(
                report["global"]["metrics"]["unknown_auroc"]["raw_mean_delta"],
                0.05,
            )
            self.assertAlmostEqual(
                report["global"]["metrics"]["unknown_fpr95"][
                    "oriented_mean_improvement"
                ],
                0.1,
            )


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from summarize_cade_matrix import METRICS, build_summary, load_runs


class CADESummaryTest(unittest.TestCase):
    def test_load_and_aggregate_both_threshold_protocols(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "hikari" / "probing_seed7_cade" / "metrics.json"
            path.parent.mkdir(parents=True)
            calibrated = {metric: 0.8 for metric in METRICS}
            official = {metric: 0.7 for metric in METRICS}
            path.write_text(
                json.dumps(
                    {
                        "reports": {"cade": calibrated},
                        "auxiliary_reports": {"cade_official_mad35": official},
                        "validation_thresholds": {"cade": 4.2},
                        "training_seconds": 12.5,
                        "trainable_parameters": 123,
                    }
                ),
                encoding="utf-8",
            )
            summary = build_summary(load_runs(root))

        self.assertEqual(summary["global"]["number_of_runs"], 1)
        self.assertEqual(
            summary["global"]["calibrated"]["unknown_auroc"]["mean"], 0.8
        )
        self.assertEqual(
            summary["global"]["official_mad35"]["unknown_auroc"]["mean"], 0.7
        )
        self.assertEqual(summary["trainable_parameters"], [123])


if __name__ == "__main__":
    unittest.main()

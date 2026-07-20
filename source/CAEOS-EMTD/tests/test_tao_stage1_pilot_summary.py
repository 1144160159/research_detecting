import json
import tempfile
import unittest
from pathlib import Path

from summarize_tao_stage1_adapter_pilot import RUNS, summarize


class TaoStage1PilotSummaryTest(unittest.TestCase):
    def write_run(self, root: Path, suite: str, run_name: str, adapter: float, baseline: float) -> None:
        path = root / suite / run_name
        path.mkdir(parents=True)
        report = lambda value: {
            "known_macro_f1": 0.8,
            "unknown_auroc": value,
            "unknown_aupr": value,
            "unknown_fpr95": 1.0 - value,
            "oscr": value,
        }
        payload = {
            "reports": {
                "tao_stage1_adapter": report(adapter),
                "energy": report(baseline),
            },
            "selection_evidence": {
                "postprocessors": {
                    "tao_stage1_adapter": {
                        "unknown_or_test_labels_used_for_fitting_or_selection": False
                    }
                }
            },
        }
        (path / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_expand_when_adapter_wins_at_least_one_primary_metric(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for suite, run_name in RUNS:
                self.write_run(root, suite, run_name, 0.8, 0.7)
            result = summarize(root)
        self.assertEqual(result["decision"], "expand")
        self.assertAlmostEqual(result["aggregate"]["mean_directed_delta_unknown_auroc"], 0.1)

    def test_retains_negative_result_when_adapter_loses_both_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for suite, run_name in RUNS:
                self.write_run(root, suite, run_name, 0.6, 0.7)
            result = summarize(root)
        self.assertEqual(result["decision"], "retain_negative")


if __name__ == "__main__":
    unittest.main()

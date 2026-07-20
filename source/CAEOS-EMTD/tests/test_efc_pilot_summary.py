from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_efc_strict_v2_pilot import summarize


class EfcPilotSummaryTest(unittest.TestCase):
    def write_metrics(
        self,
        path: Path,
        report: dict[str, float],
        kind: str,
        fingerprint: str = "a" * 64,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "split_metadata": {"split_fingerprint": {"combined": fingerprint}}
        }
        if kind == "efc":
            payload.update(
                {
                    "reports": {"efc_energy_margin": report},
                    "selection_evidence": {
                        "unknown_or_test_labels_used_for_training": False,
                        "unknown_or_test_labels_used_for_preprocessing": False,
                        "unknown_or_test_labels_used_for_thresholds": False,
                    },
                    "upstream": {"commit": "c" * 40},
                }
            )
            (path.parent / "scores.npz").touch()
            (path.parent / "provenance.json").write_text("{}", encoding="utf-8")
        elif kind == "gate":
            payload["selected_report"] = report
        else:
            payload["reports"] = {"ronetc": report}
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_expands_when_efc_passes_budget_gate(self) -> None:
        report = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.7,
            "unknown_aupr": 0.6,
            "unknown_fpr95": 0.4,
            "oscr": 0.65,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tasks = [
                {"suite": "edge_iiot", "scenario": "a", "seed": 7},
                {"suite": "nf_cse", "scenario": "b", "seed": 7},
                {"suite": "ustc_tfc2016", "scenario": "c", "seed": 7},
            ]
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "status": "frozen_before_real_results",
                        "upstream": {"commit": "c" * 40},
                        "pilot": tasks,
                    }
                ),
                encoding="utf-8",
            )
            for task in tasks:
                suite, scenario, seed = task["suite"], task["scenario"], task["seed"]
                self.write_metrics(
                    root / "efc" / suite / f"{scenario}_seed{seed}_efc" / "metrics.json",
                    report,
                    "efc",
                )
                self.write_metrics(
                    root / "gate" / suite / f"{scenario}_seed{seed}" / "metrics.json",
                    {**report, "unknown_auroc": 0.75},
                    "gate",
                )
                self.write_metrics(
                    root / "ronet" / suite / f"{scenario}_seed{seed}_ronetc" / "metrics.json",
                    {**report, "unknown_auroc": 0.69, "oscr": 0.66},
                    "ronetc",
                )
            summary = summarize(
                root / "efc", root / "gate", root / "ronet", manifest
            )
            self.assertEqual("expand_strict_v2_190", summary["decision"])
            self.assertEqual(6, summary["split_fingerprint_pair_checks"])


if __name__ == "__main__":
    unittest.main()

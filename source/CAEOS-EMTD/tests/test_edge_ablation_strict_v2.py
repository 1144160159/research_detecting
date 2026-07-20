from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_edge_ablation_strict_v2 import aggregate, discover_ablations, load_runs


FINAL = "cauchy_modality_support_union"
ABLATIONS = ("baseline", "cauchy_evidence")
POLICY = "confirmed_cauchy_modality_union_v1_edge"
BASE_REPORT = {
    "known_macro_f1": 0.8,
    "unknown_auroc": 0.6,
    "unknown_aupr": 0.5,
    "unknown_fpr95": 0.5,
    "oscr": 0.55,
}


class EdgeAblationStrictV2Test(unittest.TestCase):
    def test_discovers_every_report_except_final(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "edge_iiot" / "fingerprinting_seed7"
            directory.mkdir(parents=True)
            (directory / "metrics.json").write_text(
                json.dumps(
                    {"reports": {FINAL: {}, "entropy": {}, "baseline": {}}}
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                discover_ablations(root, FINAL),
                ("baseline", "entropy"),
            )

    def write_run(
        self,
        root: Path,
        scenario: str,
        seed: int,
        final_delta: float,
        missing_method: str | None = None,
    ) -> None:
        directory = root / "edge_iiot" / f"{scenario}_seed{seed}"
        directory.mkdir(parents=True)
        final_report = dict(BASE_REPORT)
        final_report["unknown_auroc"] += final_delta
        final_report["unknown_aupr"] += final_delta
        final_report["unknown_fpr95"] -= final_delta
        final_report["oscr"] += final_delta
        reports = {
            FINAL: final_report,
            "baseline": dict(BASE_REPORT),
            "cauchy_evidence": dict(BASE_REPORT),
        }
        if missing_method:
            reports.pop(missing_method)
        payload = {
            "risk_policy": POLICY,
            "selected_risk": FINAL,
            "selected_report": final_report,
            "reports": reports,
            "risk_selection_details": {
                "unknown_or_test_labels_used_for_selection": False,
            },
            "split_metadata": {
                "split_fingerprint": {"combined": f"{scenario}-{seed}"}
            },
        }
        (directory / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
        for name in ("scores.npz", "evidence_package.npz", "provenance.json"):
            (directory / name).touch()

    def build_matrix(self, root: Path) -> None:
        for scenario, delta in (("a", 0.10), ("b", 0.04)):
            for seed in (7, 11):
                self.write_run(root, scenario, seed, delta)

    def test_scenario_blocking_and_joint_holm_family(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.build_matrix(root)
            rows, validation = load_runs(
                root, {7, 11}, 2, FINAL, ABLATIONS, POLICY
            )
            self.assertEqual(4, validation["run_count"])
            result = aggregate(rows, FINAL, ABLATIONS, 500, 17)
            self.assertEqual(2, result["scenario_count"])
            self.assertEqual(8, result["holm_family"]["hypothesis_count"])
            item = result["comparisons"]["baseline"]["metrics"]["unknown_auroc"]
            self.assertAlmostEqual(0.07, item["oriented_mean_improvement"])
            fpr = result["comparisons"]["baseline"]["metrics"]["unknown_fpr95"]
            self.assertAlmostEqual(0.07, fpr["oriented_mean_improvement"])

    def test_missing_component_report_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_run(root, "a", 7, 0.1, missing_method="cauchy_evidence")
            with self.assertRaisesRegex(ValueError, "missing report 'cauchy_evidence'"):
                load_runs(root, {7}, 1, FINAL, ABLATIONS, POLICY)

    def test_incomplete_seed_coverage_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_run(root, "a", 7, 0.1)
            self.write_run(root, "b", 7, 0.1)
            self.write_run(root, "b", 11, 0.1)
            with self.assertRaisesRegex(ValueError, "seed coverage mismatch"):
                load_runs(root, {7, 11}, 2, FINAL, ABLATIONS, POLICY)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_paired_confirmation import aggregate, build_rows


METRIC_VALUES = {
    "known_macro_f1": 0.8,
    "unknown_auroc": 0.6,
    "unknown_aupr": 0.5,
    "unknown_fpr95": 0.4,
    "oscr": 0.55,
    "known_acceptance_rate": 0.95,
    "unknown_rejection_rate": 0.4,
}


class PairedConfirmationSummaryTest(unittest.TestCase):
    def write_run(
        self,
        root: Path,
        scenario: str,
        seed: int,
        policy: str,
        delta: float,
        fingerprint: str | None = None,
        leakage: bool = False,
    ) -> None:
        directory = root / "edge_iiot" / f"{scenario}_seed{seed}"
        directory.mkdir(parents=True)
        report = dict(METRIC_VALUES)
        report["unknown_auroc"] += delta
        report["unknown_aupr"] += delta
        report["unknown_fpr95"] -= delta
        report["oscr"] += delta
        payload = {
            "risk_policy": policy,
            "selected_risk": policy,
            "selected_report": report,
            "split_metadata": {
                "split_fingerprint": {
                    "combined": fingerprint or f"{scenario}-{seed}",
                }
            },
            "risk_selection_details": {
                "unknown_or_test_labels_used_for_selection": leakage,
            },
        }
        (directory / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
        for name in ("scores.npz", "evidence_package.npz", "provenance.json"):
            (directory / name).touch()

    def build_pair(self, base: Path) -> tuple[Path, Path]:
        reference = base / "reference"
        candidate = base / "candidate"
        for scenario, delta in (("a", 0.1), ("b", -0.02)):
            for seed in (29, 31):
                fingerprint = f"{scenario}-{seed}"
                self.write_run(
                    reference, scenario, seed, "reference_policy", 0.0, fingerprint
                )
                self.write_run(
                    candidate, scenario, seed, "candidate_policy", delta, fingerprint
                )
        return reference, candidate

    def test_build_rows_validates_pairing_and_scenario_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reference, candidate = self.build_pair(Path(temporary))
            rows, validation = build_rows(
                reference,
                candidate,
                {29, 31},
                expected_scenarios=2,
                candidate_risk_policy="candidate_policy",
                reference_risk_policy="reference_policy",
            )
            self.assertEqual(4, validation["paired_tasks"])
            summary = aggregate(rows, bootstrap_repetitions=500, bootstrap_seed=7)
            self.assertEqual(2, summary["scenario_count"])
            self.assertAlmostEqual(
                0.04,
                summary["metrics"]["unknown_auroc"]["oriented_mean_improvement"],
            )
            self.assertAlmostEqual(
                0.04,
                summary["metrics"]["unknown_fpr95"]["oriented_mean_improvement"],
            )
            self.assertTrue(summary["decision"]["mean_safety_gate"]["passes"])

    def test_split_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reference, candidate = self.build_pair(Path(temporary))
            path = candidate / "edge_iiot" / "a_seed29" / "metrics.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["split_metadata"]["split_fingerprint"]["combined"] = "wrong"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "split fingerprint mismatch"):
                build_rows(
                    reference,
                    candidate,
                    {29, 31},
                    expected_scenarios=2,
                    candidate_risk_policy="candidate_policy",
                    reference_risk_policy="reference_policy",
                )

    def test_missing_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reference, candidate = self.build_pair(Path(temporary))
            run = candidate / "edge_iiot" / "a_seed31"
            for path in run.iterdir():
                path.unlink()
            run.rmdir()
            with self.assertRaisesRegex(ValueError, "seed coverage mismatch"):
                build_rows(
                    reference,
                    candidate,
                    {29, 31},
                    expected_scenarios=2,
                    candidate_risk_policy="candidate_policy",
                    reference_risk_policy="reference_policy",
                )

    def test_leakage_guard_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reference, candidate = self.build_pair(Path(temporary))
            path = candidate / "edge_iiot" / "b_seed31" / "metrics.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["risk_selection_details"][
                "unknown_or_test_labels_used_for_selection"
            ] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "leakage guard"):
                build_rows(
                    reference,
                    candidate,
                    {29, 31},
                    expected_scenarios=2,
                    candidate_risk_policy="candidate_policy",
                    reference_risk_policy="reference_policy",
                )


if __name__ == "__main__":
    unittest.main()

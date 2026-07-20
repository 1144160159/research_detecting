from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from select_external_fusion_candidate import build_manifest, parse_seeds


def payload(expert: str, auroc: float, passes: bool = True) -> dict[str, object]:
    metric = {
        "gate_mean": 0.8,
        "candidate_mean": auroc,
        "oriented_mean_delta": auroc - 0.8,
        "wins_ties_losses": [2, 0, 0],
    }
    return {
        "selection_scope": {"seeds": [7], "suites": ["edge"]},
        "overall": {
            "number_of_runs": 2,
            "expert_name": expert,
            "methods": {
                "rank_cauchy": {
                    "mean_auroc": auroc,
                    "minimum_auroc": auroc - 0.1,
                    "mean_delta_vs_gate": auroc - 0.8,
                    "wins_ties_losses_vs_gate": [2, 0, 0],
                    "metrics": {
                        name: dict(metric)
                        for name in (
                            "known_macro_f1",
                            "unknown_auroc",
                            "unknown_aupr",
                            "unknown_fpr95",
                            "oscr",
                        )
                    },
                    "development_safety_gate": {"passes": passes},
                }
            },
        },
    }


class ExternalFusionSelectionTest(unittest.TestCase):
    def test_best_safe_candidate_is_frozen_without_seed_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "a.json"
            second = root / "b.json"
            safety = root / "b_full_metrics.json"
            first.write_text(json.dumps(payload("a", 0.82)), encoding="utf-8")
            second.write_text(json.dumps(payload("b", 0.85)), encoding="utf-8")
            safety.write_text(json.dumps(payload("b", 0.85)), encoding="utf-8")
            result = build_manifest([first, second], safety, (29, 31))
            self.assertEqual(result["selected_candidate"]["expert_name"], "b")
            self.assertEqual(
                result["selected_candidate"]["fusion_definition"],
                "equal-weight Cauchy p-value combination",
            )
            self.assertEqual(result["screened_candidate_count"], 2)
            self.assertEqual(result["seed_overlap"], [])

    def test_seed_overlap_and_unsafe_candidate_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "a.json"
            unsafe = Path(directory) / "a_full_metrics.json"
            path.write_text(json.dumps(payload("a", 0.85)), encoding="utf-8")
            unsafe.write_text(
                json.dumps(payload("a", 0.85, passes=False)), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "safety gate"):
                build_manifest([path], unsafe, (29, 31))
            unsafe.write_text(json.dumps(payload("a", 0.85)), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "overlap"):
                build_manifest([path], unsafe, (7, 29))

    def test_seed_parser_is_strict(self) -> None:
        self.assertEqual(parse_seeds("31,29"), (29, 31))
        for value in ("", "7,", "x", "7,7", "-1"):
            with self.assertRaises(ValueError):
                parse_seeds(value)


if __name__ == "__main__":
    unittest.main()

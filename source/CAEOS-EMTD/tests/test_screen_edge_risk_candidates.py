from __future__ import annotations

import unittest

from screen_edge_risk_candidates import (
    build_manifest,
    candidate_is_eligible,
    choose_candidate,
    pareto_frontier,
    screen,
)


def values(f1: float, auroc: float, aupr: float, fpr95: float, oscr: float):
    return {
        "known_macro_f1": f1,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


class ScreenEdgeRiskCandidatesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.means = {
            "final": values(0.9, 0.80, 0.70, 0.40, 0.75),
            "safe": values(0.9, 0.84, 0.70, 0.40, 0.75),
            "unsafe": values(0.9, 0.90, 0.60, 0.55, 0.60),
        }

    def test_candidate_gate_and_primary_selection(self) -> None:
        self.assertTrue(
            candidate_is_eligible(self.means["safe"], self.means["final"], 0.01)
        )
        self.assertFalse(
            candidate_is_eligible(self.means["unsafe"], self.means["final"], 0.01)
        )
        selected, eligible = choose_candidate(self.means, "final", 0.01)
        self.assertEqual("safe", selected)
        self.assertEqual(["final", "safe"], eligible)

    def test_screen_uses_scenarios_as_loso_units(self) -> None:
        blocks = {
            "edge/a": self.means,
            "edge/b": {
                "final": values(0.9, 0.82, 0.71, 0.39, 0.76),
                "safe": values(0.9, 0.85, 0.72, 0.38, 0.77),
                "unsafe": values(0.9, 0.91, 0.61, 0.54, 0.61),
            },
        }
        result = screen(blocks, "final", 0.01)
        self.assertEqual("safe", result["selected_candidate"])
        self.assertEqual({"safe": 2}, result["loso"]["selected_paths"])
        self.assertIn("safe", result["pareto_frontier"])

    def test_manifest_is_deterministic_and_records_label_boundary(self) -> None:
        validation = {
            "seeds": [7, 11],
            "scenario_count": 2,
            "method_count": 3,
            "source_metrics_combined_sha256": "a" * 64,
        }
        screening = {
            "selected_candidate": "safe",
            "selection_rule": {"primary": "test"},
        }
        first = build_manifest(validation, screening, {67, 71})
        second = build_manifest(validation, screening, {67, 71})
        self.assertEqual(first, second)
        self.assertTrue(
            first["development_candidate_screening_uses_test_unknown_labels"]
        )
        self.assertEqual("frozen_unconfirmed", first["status"])

    def test_pareto_frontier_removes_dominated_method(self) -> None:
        frontier = pareto_frontier(self.means)
        self.assertIn("safe", frontier)
        self.assertNotIn("final", frontier)
        self.assertIn("unsafe", frontier)


if __name__ == "__main__":
    unittest.main()

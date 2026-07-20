from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from summarize_anchor_gate import (
    aggregate,
    oracle_candidate_names,
    paired_p_value,
    parse_arguments,
)


class AnchorGateSummaryTest(unittest.TestCase):
    def test_parser_accepts_multiple_input_roots(self) -> None:
        with patch(
            "sys.argv",
            [
                "summarize_anchor_gate.py",
                "first",
                "second",
                "--output-json",
                "summary.json",
                "--output-md",
                "summary.md",
            ],
        ):
            arguments = parse_arguments()

        self.assertEqual(arguments.input_roots, ["first", "second"])

    def test_paired_p_value_uses_only_changed_pairs(self) -> None:
        baseline = np.zeros(18)
        candidate = np.asarray([1.0, 1.0, 1.0, *([0.0] * 15)])

        self.assertAlmostEqual(paired_p_value(candidate, baseline), 0.25)

    def test_aggregate_can_compare_joint_gate_to_hierarchical_parent(self) -> None:
        rows = [
            {
                "new_auroc": 0.8,
                "old_auroc": 0.6,
                "hierarchical_auroc": 0.75,
                "oracle_auroc": 0.85,
                "new_selection_correct": True,
                "new_selected": "cauchy_all",
            },
            {
                "new_auroc": 0.7,
                "old_auroc": 0.65,
                "hierarchical_auroc": 0.72,
                "oracle_auroc": 0.72,
                "new_selection_correct": False,
                "new_selected": "cauchy_evidence",
            },
        ]

        summary = aggregate(rows, "new", "hierarchical")

        self.assertAlmostEqual(summary["new_mean_auroc"], 0.75)
        self.assertAlmostEqual(summary["old_mean_auroc"], 0.735)
        self.assertAlmostEqual(summary["mean_delta"], 0.015)
        self.assertEqual((summary["wins"], summary["losses"]), (1, 1))

    def test_secondary_metric_improvement_orients_fpr95_downward(self) -> None:
        rows = [
            {
                "new_auroc": 0.8,
                "hierarchical_auroc": 0.7,
                "oracle_auroc": 0.8,
                "new_selection_correct": True,
                "new_selected": "cauchy_all",
                "new_unknown_aupr": 0.75,
                "hierarchical_unknown_aupr": 0.70,
                "new_unknown_fpr95": 0.20,
                "hierarchical_unknown_fpr95": 0.30,
            }
        ]

        summary = aggregate(rows, "new", "hierarchical")

        self.assertAlmostEqual(
            summary["secondary_metrics"]["unknown_aupr"][
                "oriented_improvement"
            ],
            0.05,
        )
        self.assertAlmostEqual(
            summary["secondary_metrics"]["unknown_fpr95"][
                "oriented_improvement"
            ],
            0.10,
        )

    def test_joint_gate_oracle_includes_joint_candidate(self):
        names = oracle_candidate_names(
            {
                "risk_selection": "nested_hierarchical_joint_gate",
                "reports": {
                    "anchor_support": {},
                    "cauchy_evidence": {},
                    "cauchy_all": {},
                },
            }
        )
        self.assertEqual(
            names, ("anchor_support", "cauchy_evidence", "cauchy_all")
        )

    def test_anchor_gate_oracle_remains_two_candidate(self):
        names = oracle_candidate_names(
            {
                "risk_selection": "nested_hierarchical_anchor_gate",
                "reports": {
                    "anchor_support": {},
                    "cauchy_evidence": {},
                    "cauchy_all": {},
                },
            }
        )
        self.assertEqual(names, ("anchor_support", "cauchy_evidence"))


if __name__ == "__main__":
    unittest.main()

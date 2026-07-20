from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from analyze_density_blend import load_trigger, select_safe_evaluation, task_seed


class DensityBlendAnalysisTests(unittest.TestCase):
    def write_metrics(self, payload: dict[str, object]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        metrics_path = Path(temporary.name) / "metrics.json"
        metrics_path.write_text(json.dumps(payload), encoding="utf-8")
        return metrics_path

    def test_load_trigger_reconstructs_raw_endpoint_from_frozen_blend(self) -> None:
        metrics_path = self.write_metrics(
            {
                "selected_risk": "density_reliability_blend",
                "risk_selection_details": {
                    "parent_selected_risk": "anchor_support",
                    "density_support_endpoint": "triple_support_union",
                    "density_gate_blend_weight": 0.05,
                },
            }
        )
        validation_parent = np.asarray([0.1, 0.2])
        validation_endpoint = np.asarray([0.9, 0.7])
        test_parent = np.asarray([0.3, 0.4])
        test_endpoint = np.asarray([0.8, 0.6])
        weight = 0.05
        validation_blend = (
            (1.0 - weight) * validation_parent + weight * validation_endpoint
        )
        test_blend = (1.0 - weight) * test_parent + weight * test_endpoint
        np.savez(
            metrics_path.parent / "scores.npz",
            validation_anchor_support=validation_parent,
            test_anchor_support=test_parent,
            test_labels=np.asarray([0, 1]),
            test_unknown=np.asarray([False, True]),
            test_prediction=np.asarray([0, 0]),
        )
        np.savez(
            metrics_path.parent / "evidence_package.npz",
            selected_risk_name=np.asarray("density_reliability_blend"),
            validation_selected_risk=validation_blend,
            test_selected_risk=test_blend,
        )

        trigger = load_trigger(metrics_path)

        self.assertIsNotNone(trigger)
        np.testing.assert_allclose(
            trigger["validation_candidate"], validation_endpoint
        )
        np.testing.assert_allclose(trigger["test_candidate"], test_endpoint)
        self.assertEqual(trigger["candidate"], "triple_support_union")
        self.assertEqual(
            trigger["candidate_source"],
            "reconstructed_from_frozen_blend_and_parent",
        )

    def test_load_trigger_rejects_non_density_endpoint(self) -> None:
        metrics_path = self.write_metrics(
            {
                "selected_risk": "support_union",
                "risk_selection_details": {
                    "parent_selected_risk": "anchor_support",
                    "density_support_endpoint": "support_union",
                },
            }
        )

        with self.assertRaisesRegex(
            ValueError, "not a raw density-support endpoint"
        ):
            load_trigger(metrics_path)

    def test_task_seed_rejects_unkeyed_paths(self) -> None:
        self.assertEqual(task_seed(Path("root/scenario_seed23/metrics.json")), 23)
        with self.assertRaisesRegex(ValueError, "cannot parse scenario seed"):
            task_seed(Path("root/scenario/metrics.json"))

    def test_safe_selection_rejects_high_auroc_with_unsafe_fpr95(self) -> None:
        def item(weight, auroc, aupr, oscr, fpr95):
            return {
                "weight": weight,
                "mean_unknown_auroc": auroc,
                "mean_unknown_aupr": aupr,
                "mean_oscr": oscr,
                "mean_unknown_fpr95": fpr95,
            }

        evaluations = [
            item(0.0, 0.70, 0.50, 0.60, 0.40),
            item(0.3, 0.75, 0.52, 0.62, 0.405),
            item(1.0, 0.80, 0.55, 0.64, 0.60),
        ]

        selected, eligible = select_safe_evaluation(
            evaluations, "unknown_auroc", 0.01, 0.0
        )

        self.assertEqual(selected["weight"], 0.3)
        self.assertEqual(eligible, [0.0, 0.3])


if __name__ == "__main__":
    unittest.main()

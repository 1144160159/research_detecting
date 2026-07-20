from __future__ import annotations

import unittest

from summarize_density_blend_confirmation import (
    holm_adjust,
    summarize,
    summarize_scenario_blocks,
    validate_selection_manifest,
)


def make_run(scenario: str, seed: int, oriented_delta: float) -> dict[str, object]:
    parent = {
        "unknown_auroc": 0.5,
        "unknown_aupr": 0.5,
        "unknown_fpr95": 0.5,
        "oscr": 0.5,
    }
    selected = {
        "unknown_auroc": 0.5 + oriented_delta,
        "unknown_aupr": 0.5 + oriented_delta,
        "unknown_fpr95": 0.5 - oriented_delta,
        "oscr": 0.5 + oriented_delta,
    }
    return {
        "scenario": scenario,
        "seed": seed,
        "triggered": True,
        "parent_report": parent,
        "selected_report": selected,
    }


class DensityBlendConfirmationSummaryTests(unittest.TestCase):
    def test_scenario_blocked_summary_uses_equal_inference_units(self) -> None:
        runs = [
            make_run("frequent", 7, 0.1),
            make_run("frequent", 11, 0.1),
            make_run("frequent", 23, 0.1),
            make_run("sparse", 7, -0.2),
        ]

        run_level = summarize(runs)
        blocked = summarize_scenario_blocks(runs)

        self.assertAlmostEqual(
            run_level["unknown_auroc"]["oriented"]["mean_delta"], 0.025
        )
        self.assertEqual(blocked["scenarios"], 2)
        self.assertEqual(blocked["inference_unit"], "scenario")
        self.assertAlmostEqual(
            blocked["unknown_auroc"]["oriented"]["mean_delta"], -0.05
        )
        self.assertIn(
            "holm_adjusted_p_value", blocked["unknown_auroc"]["oriented"]
        )

    def test_holm_adjust_is_monotone_in_sorted_p_value_order(self) -> None:
        adjusted = holm_adjust({"a": 0.01, "b": 0.02, "c": 0.2})

        self.assertAlmostEqual(adjusted["a"], 0.03)
        self.assertAlmostEqual(adjusted["b"], 0.04)
        self.assertAlmostEqual(adjusted["c"], 0.2)

    def test_confirmation_requires_disjoint_tasks_and_weight(self) -> None:
        manifest = {
            "purpose": "development_only_hyperparameter_selection",
            "eligible_for_confirmation_or_final_metrics": False,
            "selected_weight": 0.05,
            "development_tasks": ["edge/scenario_seed7"],
            "development_artifacts": {
                "edge/scenario_seed7": {"metrics.json": "development-hash"}
            },
        }
        runs = [
            {
                "task_id": "edge/scenario_seed11",
                "triggered": True,
                "blend_weight": 0.05,
                "artifact_sha256": {"metrics.json": "confirmation-hash"},
            }
        ]

        validation = validate_selection_manifest(manifest, runs)

        self.assertTrue(validation["validated_disjoint"])
        with self.assertRaisesRegex(ValueError, "task overlap"):
            validate_selection_manifest(
                manifest,
                [{**runs[0], "task_id": "edge/scenario_seed7"}],
            )
        with self.assertRaisesRegex(ValueError, "do not match"):
            validate_selection_manifest(
                manifest,
                [{**runs[0], "blend_weight": 0.1}],
            )


if __name__ == "__main__":
    unittest.main()

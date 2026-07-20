import unittest

import numpy as np

from caeos.pseudo_unknown_risk import (
    PseudoUnknownTask,
    boundary_pairwise_arrays,
    boundary_training_arrays,
    cross_fitted_shrinkage,
    empirical_tail_scores,
    quantile_local_rank_blend,
    robust_fold_gate,
)


def make_task(name: str, offset: float = 0.0) -> PseudoUnknownTask:
    features = np.asarray(
        [[0.05], [0.10], [0.15], [0.20], [0.80], [0.90]],
        dtype=np.float64,
    ) + offset
    target = np.asarray([False, False, False, False, True, True])
    return PseudoUnknownTask(
        name=name,
        features=features,
        target=target,
        reference_risk=np.asarray([0.10, 0.75, 0.20, 0.70, 0.60, 0.50]),
        labels=np.asarray([0, 0, 1, 1, -1, -1]),
        prediction=np.asarray([0, 0, 1, 1, 0, 1]),
    )


class PseudoUnknownRiskTests(unittest.TestCase):
    def test_boundary_pairwise_training_builds_symmetric_ranking_differences(self):
        values, targets, audit = boundary_pairwise_arrays(
            [make_task("attack")],
            hard_pseudo_fraction=0.5,
            interpolation=0.5,
            max_per_task=10,
        )
        self.assertEqual(targets.tolist(), [1, 1, 0, 0])
        np.testing.assert_allclose(values[:2], -values[2:])
        self.assertEqual(audit["ranking_pairs"], 2)
        self.assertEqual(audit["objective"], "pairwise_logistic_ranking")

    def test_boundary_training_uses_hard_rows_and_nearest_interpolation(self):
        values, targets, audit = boundary_training_arrays(
            [make_task("attack")],
            hard_pseudo_fraction=0.5,
            interpolation=0.5,
            max_per_task=10,
        )
        self.assertEqual(targets.tolist(), [0, 0, 1, 1])
        np.testing.assert_allclose(np.sort(values[:2, 0]), [0.10, 0.20])
        np.testing.assert_allclose(values[2:, 0], [0.90, 0.55])
        self.assertEqual(audit["tasks"][0]["synthetic_boundary_samples"], 1)
        self.assertLessEqual(
            audit["tasks"][0]["hard_pseudo_reference_risk_mean"],
            audit["tasks"][0]["all_pseudo_reference_risk_mean"],
        )

    def test_cross_fitted_boundary_training_records_leakage_boundary(self):
        result = cross_fitted_shrinkage(
            [make_task("a"), make_task("b", 0.01), make_task("c", 0.02)],
            alphas=(0.0, 0.5),
            boundary_training=True,
            seed=19,
        )
        self.assertTrue(result["training_distribution"]["enabled"])
        self.assertFalse(
            result["training_distribution"]["unknown_or_test_labels_used"]
        )
        self.assertIn("boundary interpolation", result["pseudo_unknown_source"])

    def test_cross_fitted_pairwise_training_records_ranking_objective(self):
        result = cross_fitted_shrinkage(
            [make_task("a"), make_task("b", 0.01), make_task("c", 0.02)],
            alphas=(0.0, 0.5),
            boundary_training=True,
            training_objective="pairwise",
            seed=23,
        )
        self.assertEqual(result["training_objective"], "pairwise")
        self.assertGreater(result["training_distribution"]["ranking_pairs"], 0)


    def test_local_rank_blend_preserves_reference_bin_order(self):
        reference = np.linspace(0.0, 1.0, 20, endpoint=False)
        learned = reference[::-1]
        validation, query = quantile_local_rank_blend(
            reference,
            reference,
            learned,
            learned,
            bins=5,
            beta=1.0,
        )
        np.testing.assert_allclose(validation, query)
        for left in range(4):
            self.assertLess(
                validation[reference < (left + 1) / 5].max(),
                validation[reference >= (left + 1) / 5].min(),
            )

    def test_robust_fold_gate_requires_mean_and_worst_fold_stability(self):
        learned = {
            "passes": True,
            "selected_summary": {"minimum_fold_metric_gain": -0.12},
        }
        self.assertTrue(
            robust_fold_gate(learned, minimum_fold_gain=-0.125)["passes"]
        )
        self.assertFalse(
            robust_fold_gate(learned, minimum_fold_gain=-0.10)["passes"]
        )
        learned["passes"] = False
        self.assertFalse(
            robust_fold_gate(learned, minimum_fold_gain=-0.125)["passes"]
        )

    def test_empirical_tail_uses_known_reference_only(self):
        scores = empirical_tail_scores(
            np.asarray([0.1, 0.2, 0.3]), np.asarray([0.05, 0.25, 0.9])
        )
        np.testing.assert_allclose(scores, [0.0, 0.5, 0.75])

    def test_cross_fitted_learning_excludes_evaluated_attack_class(self):
        result = cross_fitted_shrinkage(
            [
                make_task("attack_a"),
                make_task("attack_b", 0.01),
                make_task("attack_c", 0.02),
            ],
            alphas=(0.0, 0.5, 1.0),
            seed=17,
        )
        self.assertTrue(result["passes"])
        self.assertGreater(result["selected_alpha"], 0.0)
        self.assertEqual(len(result["final_weights"]), 1)
        for fold in result["folds"]:
            self.assertNotIn(fold["task"], fold["training_tasks"])
            self.assertEqual(len(fold["training_tasks"]), 2)
        gains = result["selected_summary"]["metric_mean_oriented_gains"]
        self.assertTrue(all(value > 0.0 for value in gains.values()))

    def test_cross_fitted_learning_falls_back_with_too_few_attack_classes(self):
        result = cross_fitted_shrinkage([make_task("a"), make_task("b")])
        self.assertFalse(result["passes"])
        self.assertEqual(result["selected_alpha"], 0.0)
        self.assertEqual(result["final_weights"], [])

    def test_task_rejects_true_unknown_only_input(self):
        with self.assertRaisesRegex(ValueError, "known and held-out"):
            PseudoUnknownTask(
                name="invalid",
                features=np.ones((3, 1)),
                target=np.ones(3, dtype=bool),
                reference_risk=np.ones(3),
                labels=-np.ones(3, dtype=np.int64),
                prediction=np.zeros(3, dtype=np.int64),
            )


if __name__ == "__main__":
    unittest.main()

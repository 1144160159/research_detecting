from __future__ import annotations

import unittest

import numpy as np

from caeos.pseudo_unknown_risk import PseudoUnknownTask
from caeos.tail_aware_ranking import (
    apply_tail_aware_head,
    cross_fitted_tail_aware_shrinkage,
    monotone_tail_basis,
    selected_tail_aware_fold_metrics,
    tail_aware_pairwise_arrays,
)


FEATURE_NAMES = ("uncertainty", "distance")


def task(name: str, offset: float) -> PseudoUnknownTask:
    known = np.asarray(
        [
            [0.05 + offset, 0.10],
            [0.10 + offset, 0.15],
            [0.20 + offset, 0.10],
            [0.25 + offset, 0.20],
        ]
    )
    pseudo = np.asarray(
        [
            [0.45 + offset, 0.55],
            [0.55 + offset, 0.45],
            [0.65 + offset, 0.60],
            [0.75 + offset, 0.70],
        ]
    )
    features = np.concatenate([known, pseudo], axis=0)
    target = np.asarray([False] * len(known) + [True] * len(pseudo))
    reference = np.asarray([0.10, 0.20, 0.60, 0.70, 0.30, 0.40, 0.50, 0.80])
    labels = np.asarray([0, 0, 1, 1, -1, -1, -1, -1])
    prediction = np.asarray([0, 0, 1, 1, 0, 0, 1, 1])
    return PseudoUnknownTask(name, features, target, reference, labels, prediction)


class TailAwareRankingTests(unittest.TestCase):
    def test_basis_and_nonnegative_head_are_monotone(self) -> None:
        low = np.asarray([[0.1, 0.2]])
        high = np.asarray([[0.3, 0.4]])
        low_basis, names = monotone_tail_basis(low, FEATURE_NAMES)
        high_basis, observed_names = monotone_tail_basis(high, FEATURE_NAMES)
        self.assertEqual(names, observed_names)
        self.assertTrue(np.all(high_basis >= low_basis))
        weights = np.arange(1, low_basis.shape[1] + 1, dtype=float)
        weights /= weights.sum()
        self.assertGreater(
            apply_tail_aware_head(high, FEATURE_NAMES, weights)[0],
            apply_tail_aware_head(low, FEATURE_NAMES, weights)[0],
        )

    def test_pairwise_arrays_are_balanced_and_tail_weighted(self) -> None:
        values, targets, weights, audit = tail_aware_pairwise_arrays(
            [task("a", 0.0)], FEATURE_NAMES, tail_gamma=2.0
        )
        self.assertEqual(values.shape[0], len(targets))
        self.assertEqual(len(targets), len(weights))
        self.assertEqual(int((targets == 0).sum()), int((targets == 1).sum()))
        self.assertGreater(float(weights.max()), float(weights.min()))
        self.assertFalse(audit["unknown_or_test_labels_used"])

    def test_cross_fitted_head_is_deterministic_and_passes_easy_tasks(self) -> None:
        tasks = [task("a", 0.00), task("b", 0.02), task("c", 0.04)]
        first = cross_fitted_tail_aware_shrinkage(
            tasks,
            FEATURE_NAMES,
            alphas=(0.5, 1.0),
            tail_gammas=(0.0, 2.0),
            seed=7,
        )
        second = cross_fitted_tail_aware_shrinkage(
            tasks,
            FEATURE_NAMES,
            alphas=(0.5, 1.0),
            tail_gammas=(0.0, 2.0),
            seed=7,
        )
        self.assertTrue(first["passes"])
        self.assertEqual(first["selected_alpha"], second["selected_alpha"])
        self.assertEqual(first["selected_tail_gamma"], second["selected_tail_gamma"])
        np.testing.assert_allclose(first["final_weights"], second["final_weights"])
        self.assertFalse(first["unknown_or_test_labels_used"])
        metrics = selected_tail_aware_fold_metrics(first, first["folds"][0])
        self.assertEqual(
            set(metrics), {"unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"}
        )

    def test_fewer_than_three_tasks_fails_closed(self) -> None:
        result = cross_fitted_tail_aware_shrinkage(
            [task("a", 0.0), task("b", 0.02)], FEATURE_NAMES
        )
        self.assertFalse(result["passes"])
        self.assertEqual(result["final_weights"], [])


if __name__ == "__main__":
    unittest.main()

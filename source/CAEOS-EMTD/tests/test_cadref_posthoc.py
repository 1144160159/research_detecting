from __future__ import annotations

import unittest

import numpy as np
from scipy.special import logsumexp

from caeos.cadref_posthoc import (
    OFFICIAL_COMMIT,
    cadref_score_batch,
    evidence,
    fit_cadref,
)


class CADRefPosthocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.weight = np.array([[1.0, 0.0], [-1.0, 0.0]])
        self.bias = np.zeros(2)
        self.train = np.array([[2.0, 1.0], [1.0, 1.0], [-2.0, 1.0], [-1.0, 1.0]])
        self.train_logits = self.train @ self.weight.T + self.bias

    def test_fit_groups_centroids_by_predicted_class(self) -> None:
        state = fit_cadref(self.weight, self.bias, self.train, self.train_logits)
        np.testing.assert_allclose(state.predicted_class_means[0], [1.5, 1.0])
        np.testing.assert_allclose(state.predicted_class_means[1], [-1.5, 1.0])
        np.testing.assert_array_equal(state.predicted_class_counts, [2, 2])

    def test_scores_match_official_equations(self) -> None:
        state = fit_cadref(self.weight, self.bias, self.train, self.train_logits)
        query = np.array([[1.8, 1.2]])
        logits = query @ self.weight.T + self.bias
        scores, diagnostics = cadref_score_batch(query, logits, state)
        expected_caref = -(0.3 + 0.2) / 3.0
        expected_cadref = -(0.3 / 3.0) / logsumexp(logits[0])
        np.testing.assert_allclose(scores["caref"], [expected_caref])
        np.testing.assert_allclose(scores["cadref_energy_fixed"], [expected_cadref])
        self.assertTrue(diagnostics["all_scores_finite"])

    def test_zero_mean_energy_and_mismatched_logits_fail_closed(self) -> None:
        zero_weight = np.zeros((2, 2))
        zero_bias = np.full(2, -np.log(2.0))
        zero_logits = self.train @ zero_weight.T + zero_bias
        with self.assertRaises(FloatingPointError):
            fit_cadref(zero_weight, zero_bias, self.train, zero_logits)
        bad_logits = self.train_logits.copy()
        bad_logits[0, 0] += 0.1
        with self.assertRaises(ValueError):
            fit_cadref(self.weight, self.bias, self.train, bad_logits)

    def test_evidence_pins_official_energy_variant(self) -> None:
        item = evidence()
        self.assertEqual(item["official_commit"], OFFICIAL_COMMIT)
        self.assertEqual(item["logit_method"], "Energy")
        self.assertIn("Eq.10", item["cadref_formula"])
        self.assertFalse(item["unknown_or_test_labels_used_for_fitting_or_selection"])


if __name__ == "__main__":
    unittest.main()

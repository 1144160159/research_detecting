from __future__ import annotations

import unittest

import numpy as np
from scipy.special import softmax

from caeos.fisher_rao_posthoc import evidence, fisher_rao_score_batch, fit_fisher_rao


class FisherRaoPosthocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.features = np.array(
            [[2.0, 0.1, 0.0], [1.6, 0.2, 0.2], [1.9, -0.1, -0.2],
             [-2.0, 0.0, 0.1], [-1.7, -0.2, -0.2], [-1.8, 0.2, 0.3]]
        )
        self.labels = np.array([0, 0, 0, 1, 1, 1])
        self.logits = np.column_stack((self.features[:, 0], -self.features[:, 0]))

    def test_standard_trace_matches_closed_form(self) -> None:
        state = fit_fisher_rao(self.features, self.logits, self.labels)
        query = np.array([[1.2, 0.3, -0.1]])
        logits = np.array([[1.2, -1.2]])
        scores, diagnostics = fisher_rao_score_batch(query, logits, state)
        p = softmax(logits, axis=1)[0]
        expected_risk = float(np.square(query).sum() * (1.0 - np.square(p).sum()))
        np.testing.assert_allclose(scores["fim_standard"], [-expected_risk])
        self.assertTrue(diagnostics["all_scores_finite"])

    def test_id_only_fit_is_deterministic_and_balanced(self) -> None:
        first = fit_fisher_rao(self.features, self.logits, self.labels)
        second = fit_fisher_rao(self.features, self.logits, self.labels)
        np.testing.assert_allclose(first.feature_basis, second.feature_basis)
        np.testing.assert_allclose(first.probability_basis, second.probability_basis)
        self.assertGreater(first.lambda_magnitude, 0.0)
        self.assertGreater(first.lambda_residual, 0.0)

    def test_degenerate_calibration_fails_closed(self) -> None:
        with self.assertRaises((ValueError, FloatingPointError)):
            fit_fisher_rao(np.ones((6, 3)), np.ones((6, 2)), self.labels)

    def test_evidence_pins_strict_adapter(self) -> None:
        item = evidence()
        self.assertIn("Eq.14-15", item["coefficient_policy"])
        self.assertEqual(item["fit_split"], "known_training_embeddings_logits_and_labels_only")
        self.assertFalse(item["unknown_or_test_labels_used_for_fitting_or_selection"])


if __name__ == "__main__":
    unittest.main()

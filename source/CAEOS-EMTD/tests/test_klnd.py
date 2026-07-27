from __future__ import annotations

import unittest

import numpy as np

from caeos.klnd import KLogitNeighborDistance, METHODS


class KLogitNeighborDistanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.train_logits = np.array(
            [
                [5.0, 0.2, -0.3],
                [4.5, 0.4, -0.1],
                [0.1, 5.0, 0.2],
                [0.3, 4.6, 0.1],
                [-0.2, 0.3, 5.1],
                [0.0, 0.4, 4.7],
            ]
        )
        self.train_labels = np.array([0, 0, 1, 1, 2, 2])
        self.validation_logits = np.array(
            [
                [4.8, 0.3, -0.2],
                [4.2, 0.5, 0.0],
                [0.2, 4.8, 0.3],
                [0.4, 4.3, 0.2],
                [-0.1, 0.2, 4.9],
                [0.1, 0.5, 4.4],
            ]
        )
        self.validation_labels = np.array([0, 0, 1, 1, 2, 2])

    def test_fit_uses_all_three_known_only_variants(self) -> None:
        calibrator = KLogitNeighborDistance().fit(
            self.train_logits,
            self.train_labels,
            self.validation_logits,
            self.validation_labels,
        )
        evidence = calibrator.evidence()
        self.assertEqual(set(evidence["thresholds"]), set(METHODS))
        self.assertEqual(evidence["neighbor_policy"], "all_other_known_classes")
        self.assertEqual(evidence["train_correct_counts"], [2, 2, 2])
        self.assertEqual(evidence["validation_correct_counts"], [2, 2, 2])

    def test_scores_match_paper_equations_and_orientation(self) -> None:
        calibrator = KLogitNeighborDistance().fit(
            self.train_logits,
            self.train_labels,
            self.validation_logits,
            self.validation_labels,
        )
        sample = np.array([[3.0, 1.0, 0.0]])
        output = calibrator.evaluate(sample)
        centers = calibrator.centers_
        assert centers is not None
        distances = np.linalg.norm(sample[0] - centers, axis=1)
        own = distances[0]
        others = distances[1:]
        self.assertAlmostEqual(output.risks["klnd1"][0], own)
        self.assertAlmostEqual(
            output.risks["klnd2"][0], -float(np.sum(others - own))
        )
        self.assertAlmostEqual(
            output.risks["klnd3"][0], own / float(np.sum(others))
        )

    def test_far_ambiguous_sample_has_higher_klnd1_and_klnd3_risk(self) -> None:
        calibrator = KLogitNeighborDistance().fit(
            self.train_logits,
            self.train_labels,
            self.validation_logits,
            self.validation_labels,
        )
        known = calibrator.evaluate(np.array([[4.7, 0.3, -0.1]]))
        ambiguous = calibrator.evaluate(np.array([[1.0, 0.9, 0.8]]))
        self.assertGreater(
            ambiguous.risks["klnd1"][0], known.risks["klnd1"][0]
        )
        self.assertGreater(
            ambiguous.risks["klnd3"][0], known.risks["klnd3"][0]
        )

    def test_missing_correct_validation_class_is_rejected(self) -> None:
        bad_validation = self.validation_logits.copy()
        bad_validation[4:, 0] = 10.0
        with self.assertRaisesRegex(
            ValueError, "no correctly classified validation samples"
        ):
            KLogitNeighborDistance().fit(
                self.train_logits,
                self.train_labels,
                bad_validation,
                self.validation_labels,
            )

    def test_inputs_must_be_finite(self) -> None:
        bad_train = self.train_logits.copy()
        bad_train[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            KLogitNeighborDistance().fit(
                bad_train,
                self.train_labels,
                self.validation_logits,
                self.validation_labels,
            )


if __name__ == "__main__":
    unittest.main()

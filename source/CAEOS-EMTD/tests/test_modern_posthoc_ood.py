import unittest

import numpy as np

from caeos.neural_open_set import DICECalibrator, ReActCalibrator, SHECalibrator


class ModernPosthocOODTests(unittest.TestCase):
    def setUp(self) -> None:
        self.embeddings = np.asarray(
            [[2.0, 0.0], [1.5, 0.1], [0.0, 2.0], [0.1, 1.5]],
            dtype=np.float64,
        )
        self.weight = np.asarray([[1.0, -0.5], [-0.5, 1.0]], dtype=np.float64)
        self.bias = np.asarray([0.1, -0.1], dtype=np.float64)
        self.logits = self.embeddings @ self.weight.T + self.bias
        self.labels = np.asarray([0, 0, 1, 1], dtype=np.int64)

    def test_react_clips_and_returns_ood_risk(self) -> None:
        calibrator = ReActCalibrator(percentile=50.0)
        calibrator.fit(self.embeddings, self.weight, self.bias)
        unclipped = calibrator.logits(np.asarray([[10.0, 0.0]]))
        clipped = calibrator.logits(np.asarray([[100.0, 0.0]]))
        np.testing.assert_allclose(unclipped, clipped)
        self.assertEqual(calibrator.score(self.embeddings).shape, (4,))
        self.assertFalse(calibrator.evidence()["unknown_or_test_labels_used"])

    def test_dice_uses_global_contribution_percentile(self) -> None:
        calibrator = DICECalibrator(percentile=50.0)
        calibrator.fit(self.embeddings, self.weight, self.bias)
        evidence = calibrator.evidence()
        self.assertAlmostEqual(evidence["retained_fraction"], 0.5)
        self.assertEqual(calibrator.logits(self.embeddings).shape, self.logits.shape)
        self.assertEqual(calibrator.score(self.embeddings).shape, (4,))

    def test_she_matches_official_correct_pattern_inner_product(self) -> None:
        calibrator = SHECalibrator()
        calibrator.fit(self.embeddings, self.logits, self.labels)
        risk = calibrator.score(self.embeddings, self.logits)
        expected_patterns = np.asarray([[1.75, 0.05], [0.05, 1.75]])
        expected = -np.einsum(
            "nd,nd->n", self.embeddings, expected_patterns[self.labels]
        )
        np.testing.assert_allclose(risk, expected)
        self.assertEqual(calibrator.evidence()["correct_train_count_by_class"], [2, 2])

    def test_she_rejects_missing_correct_class_pattern(self) -> None:
        bad_logits = self.logits.copy()
        bad_logits[2:, 0] = 10.0
        with self.assertRaisesRegex(ValueError, "no correctly classified"):
            SHECalibrator().fit(self.embeddings, bad_logits, self.labels)


if __name__ == "__main__":
    unittest.main()

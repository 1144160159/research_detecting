import unittest

import numpy as np

from caeos.excel_ood import ExCeLCalibrator


class ExCeLCalibratorTests(unittest.TestCase):
    def test_known_rank_signature_has_lower_ood_risk(self) -> None:
        logits = np.asarray(
            [
                [8.0, 4.0, 1.0],
                [7.0, 3.0, 0.0],
                [1.0, 8.0, 4.0],
                [0.0, 7.0, 3.0],
                [4.0, 1.0, 8.0],
                [3.0, 0.0, 7.0],
            ]
        )
        labels = np.asarray([0, 0, 1, 1, 2, 2])
        detector = ExCeLCalibrator().fit(logits, labels)
        aligned = np.asarray([[9.0, 5.0, 1.0]])
        reversed_tail = np.asarray([[9.0, 1.0, 5.0]])
        self.assertLess(detector.score(aligned)[0], detector.score(reversed_tail)[0])
        self.assertEqual(detector.evidence()["correct_training_samples_per_class"], [2, 2, 2])

    def test_missing_correct_class_is_rejected(self) -> None:
        logits = np.asarray([[4.0, 1.0], [3.0, 2.0]])
        labels = np.asarray([0, 1])
        with self.assertRaisesRegex(ValueError, "correctly classified"):
            ExCeLCalibrator().fit(logits, labels)

    def test_parameters_and_shapes_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "alpha"):
            ExCeLCalibrator(alpha=1.1)
        with self.assertRaisesRegex(ValueError, "two-dimensional"):
            ExCeLCalibrator().fit(np.ones(3), np.ones(3))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

import numpy as np

from caeos.wdiscood import WDiscOOD


class WDiscOODTests(unittest.TestCase):
    def test_known_train_fit_produces_finite_components(self) -> None:
        rng = np.random.default_rng(7)
        features = np.concatenate(
            [
                rng.normal([-2.0, 0.0, 0.0, 0.0], 0.15, size=(40, 4)),
                rng.normal([2.0, 0.0, 0.0, 0.0], 0.15, size=(40, 4)),
                rng.normal([0.0, 2.0, 0.0, 0.0], 0.15, size=(40, 4)),
            ]
        )
        labels = np.repeat(np.arange(3), 40)
        detector = WDiscOOD(alpha=1.0, ridge=1e-6)
        detector.fit(features, labels)
        components = detector.components(features[:8])
        self.assertEqual(set(components), {"wd_distance", "wdr_distance"})
        self.assertTrue(np.isfinite(detector.score(features[:8])).all())
        self.assertEqual(detector.evidence()["discriminant_dimension"], 2)
        self.assertFalse(detector.evidence()["unknown_or_test_labels_used"])

    def test_discriminative_and_residual_outliers_raise_risk(self) -> None:
        rng = np.random.default_rng(11)
        left = rng.normal([-2.0, 0.0, 0.0], 0.1, size=(80, 3))
        right = rng.normal([2.0, 0.0, 0.0], 0.1, size=(80, 3))
        features = np.concatenate([left, right])
        labels = np.repeat(np.arange(2), 80)
        detector = WDiscOOD(alpha=1.0)
        detector.fit(features, labels)
        known = float(np.median(detector.score(features)))
        discriminative = float(detector.score(np.asarray([[8.0, 0.0, 0.0]]))[0])
        residual = float(detector.score(np.asarray([[0.0, 0.0, 8.0]]))[0])
        self.assertGreater(discriminative, known)
        self.assertGreater(residual, known)

    def test_invalid_inputs_fail_closed(self) -> None:
        detector = WDiscOOD()
        with self.assertRaisesRegex(ValueError, "at least two known classes"):
            detector.fit(np.ones((4, 3)), np.zeros(4, dtype=np.int64))
        with self.assertRaisesRegex(RuntimeError, "not been fitted"):
            detector.score(np.ones((1, 3)))


if __name__ == "__main__":
    unittest.main()

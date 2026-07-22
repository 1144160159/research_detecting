from __future__ import annotations

import unittest

import numpy as np

from capture_opendetect_training_runtime import build_equivalence, parse_arguments


class OpenDetectTrainingCaptureTests(unittest.TestCase):
    def test_requires_forwarded_trainer_arguments(self) -> None:
        import sys

        original = sys.argv[:]
        try:
            sys.argv = [
                "capture_opendetect_training_runtime.py",
                "--trainer",
                "train_neural_open_set.py",
                "--capture-dir",
                "capture",
            ]
            with self.assertRaisesRegex(ValueError, "trainer arguments"):
                parse_arguments()
        finally:
            sys.argv = original

    def test_formal_equivalence_uses_stable_same_device_shadow(self) -> None:
        observed = {
            "prediction": np.asarray([0, 1]),
            "risk": np.asarray([1.0, 2.0]),
        }
        shadow = {
            "prediction": np.asarray([0, 1]),
            "risk": np.asarray([1.0, 2.0]),
        }
        source = {
            "prediction": np.asarray([0, 1]),
            "risk": np.asarray([1.0 + 1.5e-5, 2.0]),
        }
        result = build_equivalence(observed, shadow, source, "cuda")
        self.assertTrue(result["passes"])
        self.assertEqual(
            result["schema_version"],
            "strict_v4_opendetect_runtime_equivalence_v2",
        )
        self.assertEqual(result["risk_max_absolute_difference"], 0.0)
        self.assertFalse(
            result["source_score_diagnostic"]["is_formal_equivalence_reference"]
        )
        self.assertGreater(
            result["source_score_diagnostic"]["risk_max_absolute_difference"],
            1e-12,
        )

    def test_same_device_shadow_difference_fails_closed(self) -> None:
        observed = {
            "prediction": np.asarray([0]),
            "risk": np.asarray([1.0]),
        }
        shadow = {
            "prediction": np.asarray([0]),
            "risk": np.asarray([1.0 + 1e-6]),
        }
        result = build_equivalence(observed, shadow, observed, "cuda")
        self.assertFalse(result["passes"])


if __name__ == "__main__":
    unittest.main()

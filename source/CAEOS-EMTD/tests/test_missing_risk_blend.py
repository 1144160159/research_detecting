from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from screen_missing_risk_blend import screen


class MissingRiskBlendTests(unittest.TestCase):
    def test_endpoints_match_archived_risks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            labels = np.asarray([0, 1, -1, -1])
            unknown = labels == -1
            detector_path = root / "detector.npz"
            classifier_path = root / "classifier.npz"
            np.savez(
                detector_path,
                test_labels=labels,
                test_unknown=unknown,
                test_cauchy_modality_support_union=np.asarray([0.2, 0.8, 0.9, 0.7]),
                test_missing_aware_max_modality_knn=np.asarray([0.1, 0.2, 0.4, 0.3]),
            )
            np.savez(
                classifier_path,
                test_labels=labels,
                test_unknown=unknown,
                test_prediction=np.asarray([0, 1, 0, 0]),
            )
            detector = np.load(detector_path)
            classifier = np.load(classifier_path)
            rows = screen(detector, classifier, threshold=0.5, steps=3)
            self.assertEqual(rows[0]["current_risk_weight"], 0.0)
            self.assertEqual(rows[-1]["current_risk_weight"], 1.0)
            self.assertGreater(
                rows[0]["report"]["known_acceptance_rate"],
                rows[-1]["report"]["known_acceptance_rate"],
            )


if __name__ == "__main__":
    unittest.main()

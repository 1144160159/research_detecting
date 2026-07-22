from pathlib import Path
import tempfile
import unittest

import numpy as np

from summarize_strict_v4_postselection_corruption import degradation, risk_ece


class PostselectionCorruptionSummaryTests(unittest.TestCase):
    def test_risk_ece_is_zero_for_bin_calibrated_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.npz"
            np.savez(
                path,
                test_risk=np.asarray([0.0, 0.0, 1.0, 1.0]),
                test_unknown=np.asarray([False, False, True, True]),
            )
            self.assertEqual(risk_ece(path, "risk"), 0.0)

    def test_degradation_orients_fpr_and_ece_as_increases(self) -> None:
        clean = {"known_macro_f1": 0.9, "unknown_fpr95": 0.2, "ece": 0.1}
        corrupted = {"known_macro_f1": 0.8, "unknown_fpr95": 0.3, "ece": 0.15}
        self.assertAlmostEqual(
            degradation(clean, corrupted, "known_macro_f1"), 0.1
        )
        self.assertAlmostEqual(degradation(clean, corrupted, "unknown_fpr95"), 0.1)
        self.assertAlmostEqual(degradation(clean, corrupted, "ece"), 0.05)


if __name__ == "__main__":
    unittest.main()

import unittest

import numpy as np

from analyze_strict_v4_risk_coverage import fixed_operating_point, selective_metrics


class StrictV4RiskCoverageTests(unittest.TestCase):
    def test_aurc_rewards_ranking_errors_late(self) -> None:
        labels = np.array([0, 0, 0, 0])
        unknown = np.array([False, False, True, True])
        prediction = np.array([0, 0, 0, 0])
        good = selective_metrics(labels, unknown, prediction, np.array([0.1, 0.2, 0.8, 0.9]))
        bad = selective_metrics(labels, unknown, prediction, np.array([0.8, 0.9, 0.1, 0.2]))
        self.assertLess(good["aurc"], bad["aurc"])
        self.assertAlmostEqual(good["eaurc"], 0.0)

    def test_fixed_point_counts_unknown_rejection_and_known_acceptance(self) -> None:
        result = fixed_operating_point(
            np.array([0.1, 0.2, 0.3, 0.4]),
            np.array([0, 1, -1, -1]),
            np.array([False, False, True, True]),
            np.array([0, 0, 0, 0]),
            np.array([0.1, 0.2, 0.8, 0.9]),
            0.95,
        )
        self.assertEqual(result["known_acceptance_rate"], 1.0)
        self.assertEqual(result["unknown_rejection_rate"], 1.0)
        self.assertEqual(result["open_set_accuracy"], 0.75)
        self.assertEqual(result["coverage"], 0.5)


if __name__ == "__main__":
    unittest.main()

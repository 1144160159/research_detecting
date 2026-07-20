from __future__ import annotations

import unittest

from confirm_threshold_selection import confirm


class ThresholdConfirmationTest(unittest.TestCase):
    def selection(self) -> dict[str, object]:
        return {
            "purpose": "development_only_threshold_selection",
            "eligible_for_confirmation_or_final_metrics": False,
            "development_seeds": [7],
            "selected_target_known_acceptance": 0.975,
            "minimum_test_known_acceptance": 0.95,
            "risk": "fixed_risk",
        }

    def sensitivity(self) -> dict[str, object]:
        return {
            "seeds": [47, 53],
            "coverage_validated": True,
            "risk": "fixed_risk",
            "scenario_count": 2,
            "acceptances": {
                "0.975": {
                    "scenario_mean": {
                        "known_acceptance_rate": 0.96,
                        "unknown_rejection_rate": 0.4,
                        "unknown_f1": 0.5,
                    },
                    "by_scenario": [
                        {"metrics": {"known_acceptance_rate": 0.95}},
                        {"metrics": {"known_acceptance_rate": 0.97}},
                    ],
                }
            },
        }

    def test_confirms_disjoint_target(self) -> None:
        report = confirm(self.selection(), self.sensitivity(), (47, 53), 500, 7)
        self.assertTrue(report["confirmation_passes"])
        self.assertAlmostEqual(0.96, report["observed_test_known_acceptance"])

    def test_rejects_seed_overlap_and_risk_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "seed overlap"):
            confirm(self.selection(), self.sensitivity(), (7, 53), 500, 7)
        sensitivity = self.sensitivity()
        sensitivity["risk"] = "other"
        with self.assertRaisesRegex(ValueError, "risk mismatch"):
            confirm(self.selection(), sensitivity, (47, 53), 500, 7)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from select_threshold_from_development import select_target


class ThresholdDevelopmentSelectionTest(unittest.TestCase):
    def report(self) -> dict[str, object]:
        return {
            "seeds": [7],
            "coverage_validated": True,
            "risk": "fixed_risk",
            "acceptances": {
                "0.95": {
                    "target_known_acceptance": 0.95,
                    "scenario_mean": {"known_acceptance_rate": 0.94},
                },
                "0.975": {
                    "target_known_acceptance": 0.975,
                    "scenario_mean": {"known_acceptance_rate": 0.96},
                },
                "0.99": {
                    "target_known_acceptance": 0.99,
                    "scenario_mean": {"known_acceptance_rate": 0.98},
                },
            },
        }

    def test_selects_smallest_target_meeting_constraint(self) -> None:
        selected = select_target(self.report(), 0.95, (7,))
        self.assertEqual(0.975, selected["selected_target_known_acceptance"])
        self.assertFalse(selected["eligible_for_confirmation_or_final_metrics"])

    def test_rejects_seed_overlap_or_unmet_constraint(self) -> None:
        with self.assertRaisesRegex(ValueError, "seed mismatch"):
            select_target(self.report(), 0.95, (11,))
        with self.assertRaisesRegex(ValueError, "no threshold"):
            select_target(self.report(), 0.99, (7,))


if __name__ == "__main__":
    unittest.main()

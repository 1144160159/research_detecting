from __future__ import annotations

import unittest

from summarize_strict_v4_doh_extension import SCENARIOS, compare


class StrictV4DoHExtensionSummaryTests(unittest.TestCase):
    def test_scenario_registry_is_frozen(self) -> None:
        self.assertEqual(SCENARIOS, {"dns2tcp", "dnscat2", "iodine"})

    def test_compare_averages_seed_repeats_by_scenario(self) -> None:
        report = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.6,
        }
        candidate = dict(report, unknown_auroc=0.9)
        blocks = {
            f"scenario/seed{seed}": {
                "caeos_pairwise": report,
                "candidate": candidate,
            }
            for seed in (137, 139, 149)
        }
        result = compare(blocks, "candidate")
        self.assertEqual(result["scenario_count"], 1)
        self.assertTrue(result["seed_repeats_are_averaged_within_scenario"])
        self.assertAlmostEqual(
            result["metrics"]["unknown_auroc"]["oriented_mean_improvement"],
            0.1,
        )


if __name__ == "__main__":
    unittest.main()

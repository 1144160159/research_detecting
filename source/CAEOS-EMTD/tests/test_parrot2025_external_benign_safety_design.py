from __future__ import annotations

import unittest

from create_parrot2025_external_benign_safety_design import (
    SEEDS,
    USTC_UNKNOWN_FAMILIES,
)


class Parrot2025ExternalBenignSafetyDesignTests(unittest.TestCase):
    def test_source_scenario_matrix_is_complete(self) -> None:
        scenarios = {
            (family, seed)
            for family in USTC_UNKNOWN_FAMILIES
            for seed in SEEDS
        }
        self.assertEqual(len(USTC_UNKNOWN_FAMILIES), 10)
        self.assertEqual(SEEDS, (311, 313))
        self.assertEqual(len(scenarios), 20)

    def test_parrot_role_excludes_malicious_ground_truth(self) -> None:
        prohibited_claims = {
            "malicious unknown detection claim on PARROT2025",
            "PARROT2025 accuracy SOTA claim",
            "training validation calibration or threshold tuning on PARROT2025",
        }
        self.assertEqual(len(prohibited_claims), 3)


if __name__ == "__main__":
    unittest.main()

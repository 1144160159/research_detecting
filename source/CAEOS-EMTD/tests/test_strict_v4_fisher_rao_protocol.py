from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_fisher_rao_expansion_gate import create_gate
from run_strict_v4_fisher_rao_matrix import select_pilot_scenarios


class StrictV4FisherRaoProtocolTests(unittest.TestCase):
    def test_selection_is_deterministic_and_two_per_suite(self) -> None:
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "a" * 64,
            "scenario_registry": {
                f"suite_{index}": {"scenarios": [f"s{item}" for item in range(5)]}
                for index in range(7)
            },
        }
        first = select_pilot_scenarios(coverage)
        self.assertEqual(first, select_pilot_scenarios(coverage))
        self.assertEqual(sum(map(len, first.values())), 14)
        self.assertTrue(all(len(set(items)) == 2 for items in first.values()))

    def test_gate_is_frozen_before_results(self) -> None:
        protocol = {
            "schema_version": "strict_v4_mlp_fisher_rao_family_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["pilot_metrics_observed_at_freeze"], 0)
        self.assertEqual(len(gate["expansion_candidates"]), 3)
        with self.assertRaises(ValueError):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

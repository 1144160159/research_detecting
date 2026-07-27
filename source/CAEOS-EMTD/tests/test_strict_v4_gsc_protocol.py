from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_gsc_expansion_gate import create_gate
from run_strict_v4_gsc_matrix import select_pilot_scenarios


class StrictV4GSCProtocolTests(unittest.TestCase):
    def test_selection_is_deterministic_and_has_two_per_suite(self) -> None:
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "abc",
            "scenario_registry": {
                "a": {"scenarios": ["x", "y", "z"]},
                "b": {"scenarios": ["p", "q"]},
            },
        }
        selected = select_pilot_scenarios(coverage)
        self.assertEqual(selected, select_pilot_scenarios(coverage))
        self.assertEqual(len(set(selected["a"])), 2)
        self.assertEqual(len(set(selected["b"])), 2)

    def test_gate_is_strictly_pre_result_and_binds_formula_check(self) -> None:
        protocol = {
            "schema_version": "strict_v4_mlp_gsc_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        self.assertIn("formula_integrity", gate["all_required_checks"])
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

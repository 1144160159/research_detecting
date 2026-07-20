import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_odin_expansion_gate import create_gate
from run_strict_v4_odin_matrix import select_pilot_scenarios


class StrictV4ODINProtocolTests(unittest.TestCase):
    def test_pilot_selection_is_deterministic_and_two_per_suite(self):
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "abc",
            "scenario_registry": {
                "a": {"scenarios": ["x", "y", "z"]},
                "b": {"scenarios": ["p", "q"]},
            },
        }
        first = select_pilot_scenarios(coverage)
        self.assertEqual(first, select_pilot_scenarios(coverage))
        self.assertEqual(len(first["a"]), 2)
        self.assertEqual(len(set(first["b"])), 2)

    def test_gate_requires_zero_observed_results(self):
        protocol = {
            "schema_version": "strict_v4_mlp_odin_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
            "temperature": 1000.0,
            "noise": 0.001,
            "fit_data": "none",
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertTrue(gate["strict_run_before_preregistration"])
        self.assertFalse(gate["ood_parameter_tuning"])
        self.assertEqual(gate["fixed_parameters"]["temperature"], 1000.0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

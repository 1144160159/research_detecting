import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_sirc_expansion_gate import create_gate
from run_strict_v4_sirc_matrix import select_pilot_scenarios, validate_full_expansion


class StrictV4SIRCProtocolTests(unittest.TestCase):
    def test_selection_is_deterministic_two_per_suite(self):
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2", "manifest_sha256": "abc123",
            "scenario_registry": {
                "suite_a": {"scenarios": ["a", "b", "c"]},
                "suite_b": {"scenarios": ["d", "e", "f", "g"]},
            },
        }
        first = select_pilot_scenarios(coverage)
        self.assertEqual(first, select_pilot_scenarios(coverage))
        self.assertTrue(all(len(set(items)) == 2 for items in first.values()))

    def test_gate_binds_protocol_and_requires_zero_results(self):
        protocol = {
            "schema_version": "strict_v4_mlp_sirc_msp_fixed_protocol_v1", "mode": "pilot", "expected_runs": 14,
            "methods": ["sirc_msp_l1", "sirc_msp_residual"],
            "fit_data": "known_training_features_and_logits_only", "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)

    def test_full_expansion_uses_only_gate_passing_methods(self):
        gate = {
            "schema_version": "strict_v4_mlp_sirc_msp_fixed_expansion_gate_v1",
            "manifest_sha256": "gate-sha",
        }
        analysis = {
            "schema_version": "strict_v4_mlp_sirc_msp_fixed_pilot_analysis_v1",
            "expansion_gate_manifest_sha256": "gate-sha",
            "decision": {"expand_methods": ["sirc_msp_residual"]},
        }
        self.assertEqual(validate_full_expansion(gate, analysis), ["sirc_msp_residual"])


if __name__ == "__main__":
    unittest.main()

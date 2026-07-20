import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_fdbd_expansion_gate import create_gate
from run_strict_v4_fdbd_matrix import select_pilot_scenarios


class StrictV4FDBDProtocolTests(unittest.TestCase):
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
            "schema_version": "strict_v4_mlp_fdbd_protocol_v1", "mode": "pilot", "expected_runs": 14,
            "fit_data": "known_training_features_only", "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

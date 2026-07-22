import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_grood_expansion_gate import create_gate
from run_strict_v4_grood_matrix import select_pilot_scenarios


class StrictV4GROODProtocolTests(unittest.TestCase):
    def test_selection_is_deterministic(self):
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

    def test_gate_is_strictly_pre_result(self):
        protocol = {
            "schema_version": "strict_v4_mlp_grood_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

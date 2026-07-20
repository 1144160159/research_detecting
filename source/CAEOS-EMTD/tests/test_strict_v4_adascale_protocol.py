import unittest

from create_strict_v4_adascale_expansion_gate import create_gate
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_adascale_matrix import select_pilot_scenarios


class StrictV4AdaSCALEProtocolTests(unittest.TestCase):
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

    def test_gate_requires_zero_observed_results_and_fixed_parameters(self):
        protocol = {
            "schema_version": "strict_v4_mlp_adascale_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
            "p_min": 60.0,
            "p_max": 85.0,
            "k1_percent": 1.0,
            "k2_percent": 5.0,
            "lambda": 10.0,
            "perturb_fraction": 0.05,
            "epsilon": 0.5,
            "temperature": 1.0,
            "fit_data": "known_validation_ecdf_only",
            "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertTrue(gate["strict_run_before_preregistration"])
        self.assertFalse(gate["ood_parameter_tuning"])
        self.assertEqual(gate["primary_reference"], "mlp_scale")
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(protocol, 1)


if __name__ == "__main__":
    unittest.main()

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_logit_posthoc_expansion_gate import create_gate


class StrictV4LogitPosthocGateTests(unittest.TestCase):
    def test_gate_records_whether_results_already_existed(self) -> None:
        protocol = {
            "schema_version": "strict_v4_mlp_logit_posthoc_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        self.assertEqual(gate["expansion_candidate"], "gen")
        self.assertTrue(gate["strict_run_before_preregistration"])
        blind_gate = create_gate(protocol, 7)
        self.assertFalse(blind_gate["strict_run_before_preregistration"])
        self.assertFalse(blind_gate["pilot_metric_values_inspected_before_freeze"])


if __name__ == "__main__":
    unittest.main()

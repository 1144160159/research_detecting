import copy
import unittest

from create_strict_v4_doc_fixed_expansion_gate import create_gate
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_doc_fixed_matrix import select_pilot_scenarios


def coverage_fixture():
    result = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "manifest_sha256": "a" * 64,
        "scenario_registry": {
            "suite_%d" % suite: {"scenarios": ["scenario_%d" % index for index in range(5)]}
            for suite in range(7)
        },
    }
    return result


class StrictV4DOCFixedProtocolTests(unittest.TestCase):
    def test_selection_is_deterministic_two_per_suite(self):
        first = select_pilot_scenarios(coverage_fixture())
        second = select_pilot_scenarios(coverage_fixture())
        self.assertEqual(first, second)
        self.assertEqual(len(first), 7)
        self.assertTrue(all(len(set(items)) == 2 for items in first.values()))

    def test_gate_requires_zero_observed_results(self):
        protocol = {
            "schema_version": "strict_v4_mlp_doc_fixed_protocol_v1",
            "mode": "pilot", "expected_runs": 14,
            "fit_data": "known_training_embeddings_and_labels_only",
            "alpha": 3.0, "minimum_class_threshold": 0.5,
            "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        gate = create_gate(protocol, 0)
        self.assertEqual(gate["pilot_metrics_observed_at_freeze"], 0)
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        with self.assertRaises(ValueError):
            create_gate(copy.deepcopy(protocol), 1)

    def test_gate_fails_if_paper_parameters_change(self):
        protocol = {
            "schema_version": "strict_v4_mlp_doc_fixed_protocol_v1",
            "mode": "pilot", "expected_runs": 14,
            "fit_data": "known_training_embeddings_and_labels_only",
            "alpha": 2.0, "minimum_class_threshold": 0.5,
            "ood_parameter_sweep": False,
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        with self.assertRaises(ValueError):
            create_gate(protocol, 0)


if __name__ == "__main__":
    unittest.main()

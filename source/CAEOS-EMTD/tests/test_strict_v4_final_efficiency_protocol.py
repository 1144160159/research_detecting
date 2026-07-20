import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol import create_protocol


def inputs():
    coverage = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "datasets": 7,
        "scenario_inference_units": 102,
        "manifest_sha256": "a" * 64,
        "scenario_registry": {
            f"suite_{index}": {"count": 2, "scenarios": ["alpha", "beta"]}
            for index in range(7)
        },
    }
    audit = {
        "schema_version": "strict_v4_efficiency_evidence_audit_v1",
        "audit_implementation_sha256": "b" * 64,
        "direct_efficiency_comparison_allowed": False,
    }
    return coverage, audit


class StrictV4FinalEfficiencyProtocolTests(unittest.TestCase):
    def test_protocol_is_deterministic_and_hash_bound(self) -> None:
        first = create_protocol(*inputs())
        second = create_protocol(*inputs())
        self.assertEqual(first, second)
        self.assertEqual(first["manifest_sha256"], canonical_hash(first))
        self.assertEqual(
            len(first["training_calibration_benchmark"]["sentinel_scenarios"]), 7
        )
        self.assertFalse(first["pre_audit_direct_comparison_allowed"])

    def test_incomplete_registry_is_rejected(self) -> None:
        coverage, audit = inputs()
        coverage["scenario_registry"].pop("suite_0")
        with self.assertRaisesRegex(ValueError, "registry"):
            create_protocol(coverage, audit)


if __name__ == "__main__":
    unittest.main()

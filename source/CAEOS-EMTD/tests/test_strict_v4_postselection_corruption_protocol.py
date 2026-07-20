import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_postselection_corruption_protocol import create_protocol


def inputs():
    coverage = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "datasets": 7,
        "scenario_inference_units": 102,
        "scenario_registry": {
            f"suite_{index}": {"count": 2, "scenarios": ["alpha", "beta"]}
            for index in range(7)
        },
    }
    coverage["manifest_sha256"] = canonical_hash(coverage)
    decision = {
        "schema_version": "strict_v4_optimal_self_algorithm_decision_v1",
        "status": "frozen_optimal_self_algorithm",
        "selected_algorithm": "caeos_pairwise",
    }
    decision["manifest_sha256"] = canonical_hash(decision)
    kwargs = {
        "coverage_file_sha256": "1" * 64,
        "decision_file_sha256": "2" * 64,
        "pairwise_candidate_manifest_sha256": "6" * 64,
        "clean_pairwise_root_manifest_sha256": "3" * 64,
        "trainer_implementation_sha256": "4" * 64,
        "runner_implementation_sha256": "5" * 64,
        "corruption_metrics_observed_at_freeze": 0,
    }
    return [coverage, decision], kwargs


class StrictV4PostselectionCorruptionProtocolTests(unittest.TestCase):
    def test_protocol_is_deterministic_and_has_frozen_run_counts(self) -> None:
        values, kwargs = inputs()
        first = create_protocol(*values, **kwargs)
        second = create_protocol(*values, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["manifest_sha256"], canonical_hash(first))
        self.assertEqual(first["sentinel_severity_screen"]["expected_runs"], 273)
        self.assertEqual(first["full102_confirmation"]["expected_runs"], 510)
        self.assertEqual(first["total_expected_corruption_runs"], 783)

    def test_non_pairwise_decision_is_rejected(self) -> None:
        values, kwargs = inputs()
        values[1]["selected_algorithm"] = "caeos_domain_safe_router"
        values[1]["manifest_sha256"] = canonical_hash(values[1])
        with self.assertRaisesRegex(ValueError, "bound to caeos_pairwise"):
            create_protocol(*values, **kwargs)

    def test_existing_corruption_metric_blocks_freeze(self) -> None:
        values, kwargs = inputs()
        kwargs["corruption_metrics_observed_at_freeze"] = 1
        with self.assertRaisesRegex(ValueError, "before any corruption metrics"):
            create_protocol(*values, **kwargs)

    def test_incomplete_registry_is_rejected(self) -> None:
        values, kwargs = inputs()
        values[0]["scenario_registry"].pop("suite_0")
        values[0]["manifest_sha256"] = canonical_hash(values[0])
        with self.assertRaisesRegex(ValueError, "registry"):
            create_protocol(*values, **kwargs)


if __name__ == "__main__":
    unittest.main()

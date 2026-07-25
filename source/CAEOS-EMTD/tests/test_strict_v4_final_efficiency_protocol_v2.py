import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import create_protocol


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
    v1 = {
        "schema_version": "strict_v4_final_efficiency_protocol_v1",
        "purpose": "history",
    }
    v1["manifest_sha256"] = canonical_hash(v1)
    readiness = {
        "schema_version": "strict_v4_final_efficiency_execution_readiness_v1",
        "protocol_manifest_sha256": v1["manifest_sha256"],
        "v1_protocol_executable": False,
        "direct_efficiency_claim_allowed": False,
    }
    decision = {
        "schema_version": "strict_v4_optimal_self_algorithm_decision_v1",
        "status": "frozen_optimal_self_algorithm",
        "selected_algorithm": "caeos_pairwise",
    }
    decision["manifest_sha256"] = canonical_hash(decision)
    external = {
        "schema_version": "strict_v4_external_comparator_confirmation_v1",
        "selected_algorithm": "caeos_pairwise",
        "selected_comparator": "opendetect",
        "external_protocol_manifest_sha256": "e" * 64,
        "comparator_validation": {"passes": True, "paired_runs": 306},
    }
    kwargs = {
        "coverage_file_sha256": "1" * 64,
        "v1_protocol_file_sha256": "2" * 64,
        "readiness_file_sha256": "3" * 64,
        "decision_file_sha256": "4" * 64,
        "external_confirmation_file_sha256": "5" * 64,
        "candidate_implementation_sha256": "6" * 64,
        "comparator_implementation_sha256": "7" * 64,
        "candidate_runtime_sha256": "8" * 64,
        "candidate_capture_sha256": "9" * 64,
        "candidate_benchmark_sha256": "a" * 64,
        "comparator_runtime_sha256": "b" * 64,
        "comparator_capture_sha256": "c" * 64,
        "comparator_training_capture_sha256": "1" * 64,
        "comparator_benchmark_sha256": "d" * 64,
        "paired_runner_sha256": "e" * 64,
        "execution_plan_creator_sha256": "2" * 64,
        "execution_plan_executor_sha256": "3" * 64,
        "efficiency_summarizer_sha256": "4" * 64,
        "protocol_creator_sha256": "f" * 64,
        "efficiency_metrics_observed_at_freeze": 0,
    }
    return [coverage, v1, readiness, decision, external], kwargs


class StrictV4FinalEfficiencyProtocolV2Tests(unittest.TestCase):
    def test_protocol_is_deterministic_hash_bound_and_result_free(self) -> None:
        values, kwargs = inputs()
        first = create_protocol(*values, **kwargs)
        second = create_protocol(*values, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["manifest_sha256"], canonical_hash(first))
        self.assertEqual(first["methods"]["candidate"], "caeos_pairwise")
        self.assertEqual(
            len(first["training_calibration_benchmark"]["sentinel_scenarios"]), 7
        )
        self.assertEqual(first["efficiency_metrics_observed_at_freeze"], 0)
        self.assertEqual(first["inference_benchmark"]["seed"], 7)
        self.assertEqual(len(first["implementation_sha256"]), 14)
        self.assertTrue(
            first["instrumentation_equivalence_gate"][
                "stable_runtime_same_device_shadow_required_per_capture"
            ]
        )
        self.assertTrue(
            first["instrumentation_equivalence_gate"][
                "source_empirical_tail_risk_difference_is_diagnostic_only"
            ]
        )
        self.assertFalse(
            first["instrumentation_equivalence_gate"][
                "separate_stochastic_retraining_shadow_required"
            ]
        )
        self.assertEqual(
            first["deployment_device_modes"]["required_modes"],
            ["native_primary", "cpu_normalized_secondary"],
        )

    def test_incomplete_external_confirmation_is_rejected(self) -> None:
        values, kwargs = inputs()
        values[4]["comparator_validation"]["paired_runs"] = 305
        with self.assertRaisesRegex(ValueError, "incomplete"):
            create_protocol(*values, **kwargs)

    def test_existing_efficiency_metric_blocks_freeze(self) -> None:
        values, kwargs = inputs()
        kwargs["efficiency_metrics_observed_at_freeze"] = 1
        with self.assertRaisesRegex(ValueError, "before any efficiency metrics"):
            create_protocol(*values, **kwargs)

    def test_selected_algorithm_mismatch_is_rejected(self) -> None:
        values, kwargs = inputs()
        values[4]["selected_algorithm"] = "caeos_domain_safe_router"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            create_protocol(*values, **kwargs)


if __name__ == "__main__":
    unittest.main()

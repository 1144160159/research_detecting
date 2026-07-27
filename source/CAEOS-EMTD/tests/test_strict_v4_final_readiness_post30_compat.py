from __future__ import annotations

import unittest

from audit_strict_v4_final_paper_readiness_post30_compat import (
    create_audit,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures() -> dict:
    protocol = canonical(
        {
            "schema_version": (
                "strict_v4_final_readiness_post30_compat_protocol_v1"
            )
        }
    )
    accuracy = canonical(
        {
            "schema_version": "strict_v4_comprehensive_sota_audit_v12",
            "post30_baseline_coverage_complete": False,
            "strict_v4_confirmed_external_sota_allowed": False,
            "selected_algorithm": "caeos_pairwise",
            "comprehensive_formal_method_count": 30,
        }
    )
    compatibility = canonical(
        {
            "schema_version": (
                "strict_v4_post30_supersession_compatibility_audit_v1"
            ),
            "old_audit_manifest_sha256": accuracy["manifest_sha256"],
            "post30_baseline_coverage_compatible": True,
            "unaffected_families_pass": True,
            "superseded_family_audits": [
                {"family": "gsc", "passes": True},
                {"family": "pro_msp_fixed", "passes": True},
            ],
        }
    )
    efficiency = canonical(
        {
            "schema_version": "strict_v4_final_efficiency_summary_v2",
            "gates": {"formal_efficiency_claim_allowed": True},
            "training": {
                "paired_candidate_over_comparator": {
                    name: {"bootstrap_95ci": [0.8, 0.9]}
                    for name in (
                        "total_fit_seconds",
                        "deployment_artifact_bytes",
                        "peak_host_rss_mb",
                    )
                }
            },
        }
    )
    native = {
        f"optimized_over_comparator_{name}": {
            "bootstrap_95ci": [0.8, 0.9]
        }
        for name in (
            "latency_p50_ms",
            "latency_p95_ms",
            "latency_p99_ms",
        )
    }
    native["optimized_over_comparator_samples_per_second"] = {
        "bootstrap_95ci": [1.1, 1.2]
    }
    optimized = canonical(
        {
            "schema_version": (
                "strict_v4_optimized_efficiency_summary_v1"
            ),
            "gates": {
                "all_102_scenarios_x_2_modes_complete": True,
                "all_full_input_equivalence_checks_pass": True,
                "optimized_artifact_size_nonincrease_passes": True,
                "two_x_deployment_target_passes": True,
            },
            "aggregate": {"native_primary": {"1": native}},
        }
    )
    corruption = canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_summary_v1"
            ),
            "validation": {"passes": True},
            "confirmatory_gate": {"passes": True},
        }
    )
    comparative = canonical(
        {
            "schema_version": (
                "strict_v4_comparative_corruption_summary_v1"
            ),
            "validation": {"passes": True},
            "comparative_robustness_gate": {"passes": True},
        }
    )
    return {
        "protocol": protocol,
        "accuracy": accuracy,
        "compatibility": compatibility,
        "efficiency": efficiency,
        "optimized": optimized,
        "tensorized": None,
        "corruption": corruption,
        "comparative": comparative,
    }


class FinalReadinessPost30CompatibilityTests(unittest.TestCase):
    def test_explicit_compatibility_repairs_only_coverage_gate(
        self,
    ) -> None:
        values = fixtures()
        result = create_audit(**values)
        self.assertTrue(
            result["gates"]["post30_baseline_coverage_complete"]
        )
        self.assertFalse(
            result["gates"][
                "confirmed_external_accuracy_sota_7_datasets_102_scenarios"
            ]
        )
        self.assertFalse(
            result["multidimensional_comprehensive_sota_allowed"]
        )
        self.assertFalse(
            result["legacy_post30_coverage_value_preserved"]
        )

    def test_mismatched_legacy_audit_binding_fails_closed(self) -> None:
        values = fixtures()
        values["compatibility"]["old_audit_manifest_sha256"] = "0" * 64
        values["compatibility"]["manifest_sha256"] = canonical_hash(
            values["compatibility"]
        )
        with self.assertRaisesRegex(ValueError, "did not repair"):
            create_audit(**values)

    def test_effect_gate_is_not_relaxed_by_compatibility(self) -> None:
        values = fixtures()
        values["corruption"]["confirmatory_gate"]["passes"] = False
        values["corruption"]["manifest_sha256"] = canonical_hash(
            values["corruption"]
        )
        result = create_audit(**values)
        self.assertFalse(
            result["gates"]["candidate_graceful_degradation_gate"]
        )
        self.assertFalse(
            result["multidimensional_comprehensive_sota_allowed"]
        )


if __name__ == "__main__":
    unittest.main()

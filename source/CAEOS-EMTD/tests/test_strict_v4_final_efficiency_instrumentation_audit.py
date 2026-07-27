from __future__ import annotations

import unittest

from audit_strict_v4_final_efficiency_v2_instrumentation import build_audit


def pairwise(selected_risk: str) -> dict[str, object]:
    return {
        "schema_version": "strict_v4_pairwise_runtime_equivalence_v2",
        "passes": True,
        "prediction_array_equal": True,
        "risk_max_absolute_difference": 0.0,
        "component_max_absolute_difference": 0.0,
        "equivalence_mode": "source_components_plus_stable_runtime_shadow",
        "selected_risk": selected_risk,
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }


def opendetect() -> dict[str, object]:
    return {
        "schema_version": "strict_v4_opendetect_runtime_equivalence_v1",
        "passes": True,
        "prediction_array_equal": True,
        "risk_max_absolute_difference": 1.6e-5,
        "absolute_tolerance": 2e-5,
        "device": "cpu",
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }


def opendetect_shadow() -> dict[str, object]:
    return {
        "schema_version": "strict_v4_opendetect_runtime_equivalence_v1",
        "passes": True,
        "prediction_array_equal": True,
        "risk_max_absolute_difference": 0.0,
        "absolute_tolerance": 1e-12,
        "equivalence_mode": "runtime_vs_uninstrumented_same_device_shadow",
        "device": "cpu",
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }


class FinalEfficiencyInstrumentationAuditTests(unittest.TestCase):
    def test_incomplete_external_confirmation_keeps_execution_closed(self) -> None:
        audit = build_audit(
            pairwise("cauchy_modality_support_union"),
            pairwise("pseudo_unknown_learned_blend"),
            opendetect(),
            opendetect_shadow(),
            external_completed=141,
            external_expected=306,
            formal_efficiency_metrics=0,
            corruption_metrics=0,
            remote_runtime_tests_passed=15,
        )
        self.assertTrue(audit["verification"]["instrumentation_code_ready"])
        self.assertFalse(audit["gates"]["protocol_freeze_allowed"])
        self.assertFalse(audit["gates"]["formal_execution_allowed"])
        self.assertFalse(
            audit["opendetect_runtime"]["diagnostic_is_formal_evidence"]
        )
        self.assertTrue(
            audit["opendetect_runtime"]["formal_same_device_equivalence_observed"]
        )

    def test_complete_external_confirmation_only_unlocks_protocol_freeze(self) -> None:
        audit = build_audit(
            pairwise("cauchy_modality_support_union"),
            pairwise("pseudo_unknown_learned_blend"),
            opendetect(),
            opendetect_shadow(),
            external_completed=306,
            external_expected=306,
            formal_efficiency_metrics=0,
            corruption_metrics=0,
            remote_runtime_tests_passed=15,
        )
        self.assertTrue(audit["gates"]["protocol_freeze_allowed"])
        self.assertFalse(audit["gates"]["formal_execution_allowed"])

    def test_non_exact_pairwise_runtime_fails_instrumentation_gate(self) -> None:
        fallback = pairwise("cauchy_modality_support_union")
        fallback["component_max_absolute_difference"] = 1e-6
        audit = build_audit(
            fallback,
            pairwise("pseudo_unknown_learned_blend"),
            opendetect(),
            opendetect_shadow(),
            external_completed=0,
            external_expected=306,
            formal_efficiency_metrics=0,
            corruption_metrics=0,
            remote_runtime_tests_passed=15,
        )
        self.assertFalse(audit["verification"]["instrumentation_code_ready"])

    def test_missing_same_device_shadow_keeps_instrumentation_closed(self) -> None:
        audit = build_audit(
            pairwise("cauchy_modality_support_union"),
            pairwise("pseudo_unknown_learned_blend"),
            opendetect(),
            None,
            external_completed=0,
            external_expected=306,
            formal_efficiency_metrics=0,
            corruption_metrics=0,
            remote_runtime_tests_passed=20,
        )
        self.assertFalse(audit["verification"]["instrumentation_code_ready"])


if __name__ == "__main__":
    unittest.main()

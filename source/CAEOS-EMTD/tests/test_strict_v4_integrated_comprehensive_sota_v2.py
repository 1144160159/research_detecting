from __future__ import annotations

import unittest

from audit_strict_v4_integrated_comprehensive_sota_v2 import (
    SYSTEM_GATES,
    VGRF,
    create_audit,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def common(selected: str) -> dict:
    protocol = canonical(
        {
            "schema_version": (
                "strict_v4_integrated_comprehensive_sota_design_v2"
            )
        }
    )
    base = canonical(
        {
            "schema_version": "strict_v4_final_paper_readiness_audit_v4",
            "selected_algorithm": "caeos_pairwise",
            "gates": {
                "post30_baseline_coverage_complete": True,
                **{name: True for name in SYSTEM_GATES},
            },
        }
    )
    compatibility = canonical(
        {
            "schema_version": (
                "strict_v4_post30_supersession_compatibility_audit_v1"
            ),
            "post30_baseline_coverage_compatible": True,
        }
    )
    selection = canonical(
        {
            "schema_version": (
                "strict_v4_final_self_algorithm_selection_v1"
            ),
            "selected_algorithm": selected,
        }
    )
    external = canonical(
        {
            "schema_version": (
                "gpu_external_dataset_evaluation_summary_v1"
            ),
            "selected_algorithm": selected,
            "expanded_external_accuracy_confirmation_passes": True,
            "validation": {"passes": True},
        }
    )
    return {
        "protocol": protocol,
        "base": base,
        "compatibility": compatibility,
        "selection": selection,
        "external": external,
    }


def positive_reconfirmation() -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_selected_external_reconfirmation_summary_v1"
            ),
            "selected_algorithm": VGRF,
            "strict_seven_suite_accuracy_sota_allowed": True,
            "decision": {"passes": True},
            "validation": {"passes": True},
        }
    )


def vgrf_system() -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_confirmation_summary_v1"
            ),
            "selected_algorithm": VGRF,
            "validation": {"passes": True},
            "equivalence_block_count": 204,
            "comparative_corruption_pair_count": 1530,
            "gates": {name: True for name in SYSTEM_GATES},
        }
    )


class IntegratedComprehensiveSotaV2Tests(unittest.TestCase):
    def test_pairwise_uses_only_pairwise_base_system_evidence(self) -> None:
        values = common("caeos_pairwise")
        not_required = canonical(
            {
                "schema_version": (
                    "strict_v4_selected_external_"
                    "reconfirmation_not_required_v1"
                )
            }
        )
        result = create_audit(
            **values,
            reconfirmation=None,
            not_required=not_required,
            selected_system=None,
        )
        self.assertEqual(
            result["selected_system_evidence_source"],
            "pairwise_base_readiness",
        )
        self.assertTrue(
            result["gates"][
                "selected_algorithm_system_evidence_consistent"
            ]
        )
        self.assertFalse(
            result["gates"][
                "strict_seven_suite_accuracy_sota_reconfirmed"
            ]
        )

    def test_vgrf_cannot_inherit_pairwise_system_evidence(self) -> None:
        values = common(VGRF)
        with self.assertRaisesRegex(ValueError, "evidence is required"):
            create_audit(
                **values,
                reconfirmation=positive_reconfirmation(),
                not_required=None,
                selected_system=None,
            )

    def test_vgrf_complete_selected_system_evidence_can_pass(self) -> None:
        values = common(VGRF)
        result = create_audit(
            **values,
            reconfirmation=positive_reconfirmation(),
            not_required=None,
            selected_system=vgrf_system(),
        )
        self.assertTrue(
            result["multidimensional_comprehensive_sota_allowed"]
        )
        self.assertEqual(
            result["selected_system_evidence_source"],
            "vgrf_selected_system_confirmation",
        )

    def test_vgrf_failed_system_gate_remains_visible(self) -> None:
        values = common(VGRF)
        system = vgrf_system()
        system["gates"][
            "comparative_corruption_robustness_against_opendetect"
        ] = False
        system["manifest_sha256"] = canonical_hash(system)
        result = create_audit(
            **values,
            reconfirmation=positive_reconfirmation(),
            not_required=None,
            selected_system=system,
        )
        self.assertFalse(
            result["gates"][
                "comparative_corruption_robustness_against_opendetect"
            ]
        )
        self.assertFalse(
            result["multidimensional_comprehensive_sota_allowed"]
        )


if __name__ == "__main__":
    unittest.main()

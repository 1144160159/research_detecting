from __future__ import annotations

import unittest

from audit_strict_v4_integrated_comprehensive_sota_v3 import create_audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_integrated_comprehensive_sota_v3_design import (
    create_design,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def design() -> dict:
    v2 = canonical(
        {
            "schema_version": (
                "strict_v4_integrated_comprehensive_sota_design_v2"
            )
        }
    )
    suite = canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_"
                "suite_gate_protocol_v1"
            )
        }
    )
    return create_design(
        v2,
        suite,
        project_root="/project",
        v2_design_file_sha256="1" * 64,
        suite_protocol_file_sha256="2" * 64,
        auditor_sha256="3" * 64,
        v2_audit_count_at_freeze=0,
        suite_audit_count_at_freeze=0,
        v3_audit_count_at_freeze=0,
    )


def v2(passes: bool = True) -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_integrated_comprehensive_sota_audit_v2"
            ),
            "status": "complete",
            "selected_algorithm": "caeos_pairwise",
            "multidimensional_comprehensive_sota_allowed": passes,
        }
    )


def suite(passes: bool = True) -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_"
                "suite_gate_audit_v1"
            ),
            "status": "complete",
            "aggregate_family_gate_passes": passes,
            "all_175_suite_threshold_checks_pass": passes,
            "validation": {
                "suite_threshold_checks": 175,
                "passes": passes,
            },
            "passes": passes,
        }
    )


class IntegratedComprehensiveSotaV3Tests(unittest.TestCase):
    def test_all_predecessor_gates_can_confirm_v3(self) -> None:
        result = create_audit(
            design=design(), v2_audit=v2(), suite_audit=suite()
        )
        self.assertTrue(result["comprehensive_sota_confirmed"])
        self.assertEqual(result["required_follow_up"], [])

    def test_suite_failure_blocks_v3(self) -> None:
        result = create_audit(
            design=design(), v2_audit=v2(), suite_audit=suite(False)
        )
        self.assertFalse(result["comprehensive_sota_confirmed"])
        self.assertIn(
            "postselection_anchor_all_175_suite_threshold_checks",
            result["required_follow_up"],
        )

    def test_v2_failure_blocks_v3(self) -> None:
        result = create_audit(
            design=design(), v2_audit=v2(False), suite_audit=suite()
        )
        self.assertFalse(result["comprehensive_sota_confirmed"])
        self.assertIn(
            "integrated_v2_multidimensional_comprehensive_sota",
            result["required_follow_up"],
        )

    def test_design_rejects_freeze_after_any_audit(self) -> None:
        v2_design = canonical(
            {
                "schema_version": (
                    "strict_v4_integrated_comprehensive_sota_design_v2"
                )
            }
        )
        suite_protocol = canonical(
            {
                "schema_version": (
                    "strict_v4_postselection_corruption_"
                    "suite_gate_protocol_v1"
                )
            }
        )
        with self.assertRaisesRegex(ValueError, "before all audits"):
            create_design(
                v2_design,
                suite_protocol,
                project_root="/project",
                v2_design_file_sha256="1" * 64,
                suite_protocol_file_sha256="2" * 64,
                auditor_sha256="3" * 64,
                v2_audit_count_at_freeze=1,
                suite_audit_count_at_freeze=0,
                v3_audit_count_at_freeze=0,
            )


if __name__ == "__main__":
    unittest.main()

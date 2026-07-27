from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_vgrf_selected_system_preparation import (
    create_preparation,
)
from validate_strict_v4_vgrf_selected_system_summary import (
    VGRF,
    validate_summary,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(root: Path) -> dict:
    design = canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_confirmation_design_v1"
            ),
            "required_output": {
                "equivalence_block_count": 204,
                "comparative_corruption_pair_count": 1530,
                "required_system_gates": ["efficiency", "robustness"],
            },
        }
    )
    preparation = canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_preparation_protocol_v1"
            ),
            "design_manifest_sha256": design["manifest_sha256"],
        }
    )
    confirmation = canonical(
        {
            "schema_version": "strict_v4_vgrf_confirmation_summary_v1",
            "passes": True,
            "selected_algorithm": VGRF,
        }
    )
    selection = canonical(
        {
            "schema_version": (
                "strict_v4_final_self_algorithm_selection_v1"
            ),
            "selected_algorithm": VGRF,
            "vgrf_confirmation_passes": True,
            "confirmation_summary_manifest_sha256": confirmation[
                "manifest_sha256"
            ],
        }
    )
    summary = canonical(
        {
            "schema_version": (
                "strict_v4_vgrf_selected_system_confirmation_summary_v1"
            ),
            "selected_algorithm": VGRF,
            "design_manifest_sha256": design["manifest_sha256"],
            "preparation_protocol_manifest_sha256": preparation[
                "manifest_sha256"
            ],
            "final_selection_manifest_sha256": selection[
                "manifest_sha256"
            ],
            "vgrf_confirmation_summary_manifest_sha256": confirmation[
                "manifest_sha256"
            ],
            "equivalence_block_count": 204,
            "comparative_corruption_pair_count": 1530,
            "validation": {"passes": True},
            "metric_wise_or_suite_wise_splicing_used": False,
            "leakage_validation": {
                "unknown_or_test_labels_used_for_fitting_selection_threshold_or_corruption_generation": (
                    False
                ),
                "test_labels_used_for_final_metrics_only": True,
            },
            "gates": {"efficiency": True, "robustness": True},
        }
    )
    return {
        "design": design,
        "preparation": preparation,
        "selection": selection,
        "confirmation": confirmation,
        "summary": summary,
    }


class VGRFSelectedSystemPreparationTests(unittest.TestCase):
    def test_preparation_freezes_before_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            design = fixtures(root)["design"]
            value = create_preparation(
                project_root=root,
                design=design,
                design_file_sha256="a" * 64,
                implementation_sha256={"validator": "b" * 64},
                observed_outputs=0,
            )
        self.assertEqual(value["system_outputs_observed_at_freeze"], 0)

    def test_preparation_after_output_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            design = fixtures(root)["design"]
            with self.assertRaisesRegex(ValueError, "before system"):
                create_preparation(
                    project_root=root,
                    design=design,
                    design_file_sha256="a" * 64,
                    implementation_sha256={},
                    observed_outputs=1,
                )

    def test_positive_summary_is_admissible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            result = validate_summary(**values)
        self.assertTrue(result["all_system_gates_pass"])
        self.assertEqual(result["equivalence_block_count"], 204)
        self.assertEqual(result["comparative_corruption_pair_count"], 1530)

    def test_negative_effect_gate_is_valid_but_does_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["summary"]["gates"]["robustness"] = False
            values["summary"]["manifest_sha256"] = canonical_hash(
                values["summary"]
            )
            result = validate_summary(**values)
        self.assertFalse(result["all_system_gates_pass"])
        self.assertTrue(result["summary_is_structurally_admissible"])

    def test_wrong_design_binding_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["summary"]["design_manifest_sha256"] = "0" * 64
            values["summary"]["manifest_sha256"] = canonical_hash(
                values["summary"]
            )
            with self.assertRaisesRegex(ValueError, "binding mismatch"):
                validate_summary(**values)

    def test_leakage_declaration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = fixtures(Path(temporary))
            values["summary"]["leakage_validation"][
                "unknown_or_test_labels_used_for_fitting_selection_threshold_or_corruption_generation"
            ] = True
            values["summary"]["manifest_sha256"] = canonical_hash(
                values["summary"]
            )
            with self.assertRaisesRegex(ValueError, "leakage"):
                validate_summary(**values)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_vgrf_selected_system_design import create_design


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs(root: Path) -> dict:
    registry = {
        f"suite_{suite}": {
            "scenarios": [
                f"scenario_{suite}_{index}"
                for index in range(15 if suite < 4 else 14)
            ]
        }
        for suite in range(7)
    }
    coverage = canonical(
        {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "scenario_registry": registry,
        }
    )
    integrated = canonical(
        {
            "schema_version": (
                "strict_v4_integrated_comprehensive_sota_design_v2"
            ),
            "selected_system_evidence_contract": {
                "required_system_gates": ["gate_a", "gate_b"]
            },
        }
    )
    sentinel = {
        suite: value["scenarios"][0]
        for suite, value in registry.items()
    }
    efficiency = canonical(
        {
            "schema_version": "strict_v4_final_efficiency_protocol_v2",
            "inference_benchmark": {"batch_sizes": [1, 64, 512]},
            "training_calibration_benchmark": {
                "sentinel_scenarios": sentinel
            },
        }
    )
    corruption = canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_protocol_v1"
            ),
            "full102_confirmation": {
                "corruption_families": [
                    "modality_missing",
                    "field_missing",
                    "feature_shuffle",
                    "row_missing",
                    "gaussian_drift",
                ],
                "fixed_severity": {"field_missing": 0.3},
                "modality_selection_rule": "frozen_hash_modulo_3",
            },
            "execution_gate": {"corruption_seed": 211},
        }
    )
    pilot = canonical(
        {
            "schema_version": (
                "strict_v4_validation_gated_reliability_fusion_protocol_v1"
            )
        }
    )
    return {
        "project_root": root,
        "coverage": coverage,
        "integrated": integrated,
        "efficiency": efficiency,
        "corruption": corruption,
        "pilot": pilot,
        "input_file_sha256": {},
        "implementation_sha256": {},
        "observed_system_outputs": 0,
    }


class VGRFSelectedSystemDesignTests(unittest.TestCase):
    def test_exact_precommitted_workload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            value = create_design(**inputs(Path(temporary)))
        self.assertEqual(value["scenario_count"], 102)
        self.assertEqual(
            value["runtime_equivalence_and_efficiency"][
                "expected_blocks"
            ],
            204,
        )
        self.assertEqual(
            value["comparative_corruption"]["source_pair_count"], 306
        )
        self.assertEqual(
            value["comparative_corruption"][
                "expected_paired_condition_evaluations"
            ],
            1530,
        )
        self.assertEqual(
            value["seed_policy"]["comparative_robustness_seeds"],
            [311, 313, 317],
        )

    def test_outputs_before_design_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = inputs(Path(temporary))
            values["observed_system_outputs"] = 1
            with self.assertRaisesRegex(ValueError, "before outputs"):
                create_design(**values)

    def test_missing_scenario_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = inputs(Path(temporary))
            values["coverage"]["scenario_registry"]["suite_0"][
                "scenarios"
            ].pop()
            values["coverage"]["manifest_sha256"] = canonical_hash(
                values["coverage"]
            )
            with self.assertRaisesRegex(ValueError, "full 102"):
                create_design(**values)

    def test_corruption_family_count_is_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = inputs(Path(temporary))
            values["corruption"]["full102_confirmation"][
                "corruption_families"
            ].pop()
            values["corruption"]["manifest_sha256"] = canonical_hash(
                values["corruption"]
            )
            with self.assertRaisesRegex(ValueError, "five"):
                create_design(**values)


if __name__ == "__main__":
    unittest.main()

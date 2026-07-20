import argparse
import json
import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_postselection_corruption import (
    Task,
    build_tasks,
    command_for,
    selected_modality,
    validate_run,
)


def inputs():
    registry = {
        f"suite_{index}": {"count": 2, "scenarios": ["alpha", "beta"]}
        for index in range(7)
    }
    coverage = {"manifest_sha256": "a" * 64, "scenario_registry": registry}
    protocol = {
        "schema_version": "strict_v4_postselection_corruption_protocol_v1",
        "status": "frozen_post_selection_before_corruption_results",
        "coverage_manifest_sha256": "a" * 64,
        "corruption_definitions": {
            "families": {
                "modality_missing": [1.0],
                "field_missing": [0.1, 0.3, 0.5],
                "row_missing": [0.1, 0.3, 0.5],
                "feature_shuffle": [0.1, 0.3, 0.5],
                "gaussian_drift": [0.25, 0.5, 1.0],
            }
        },
        "sentinel_severity_screen": {
            "sentinel_scenarios": {suite: "alpha" for suite in registry}
        },
        "full102_confirmation": {
            "corruption_families": [
                "modality_missing",
                "field_missing",
                "row_missing",
                "feature_shuffle",
                "gaussian_drift",
            ],
            "fixed_severity": {
                "modality_missing": 1.0,
                "field_missing": 0.3,
                "row_missing": 0.3,
                "feature_shuffle": 0.3,
                "gaussian_drift": 0.5,
            },
        },
        "total_expected_corruption_runs": 343,
    }
    # This synthetic registry has 14 scenarios: 273 sentinel + 70 confirmation.
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol, coverage


class StrictV4PostselectionCorruptionRunnerTests(unittest.TestCase):
    def test_task_plan_is_deterministic_and_uses_sha_modalities(self) -> None:
        protocol, coverage = inputs()
        tasks = build_tasks(protocol, coverage)
        self.assertEqual(len(tasks), 343)
        full = next(task for task in tasks if task.tier == "full102")
        self.assertEqual(
            full.modality,
            selected_modality(
                coverage["manifest_sha256"],
                full.suite,
                full.scenario,
                full.corruption,
            ),
        )

    def test_command_contains_frozen_pairwise_and_corruption_arguments(self) -> None:
        task = Task("full102", "edge_iiot", "backdoor", "field_missing", 2, 0.3)
        candidate = {
            "maximum_alpha": 0.5,
            "minimum_fold_gain": -0.1,
            "hard_pseudo_fraction": 0.5,
            "interpolation": 0.5,
            "max_per_task": 512,
            "training_objective": "pairwise",
        }
        command = command_for(task, Path("out"), Path("cache"), candidate)
        self.assertIn("nested_boundary_pairwise_pseudo_unknown_blend", command)
        self.assertEqual(command[command.index("--test-corruption-modality") + 1], "2")
        self.assertEqual(command[command.index("--test-corruption-severity") + 1], "0.3")
        self.assertEqual(command[command.index("--workers") + 1], "1")

    def test_validation_rejects_split_mismatch(self) -> None:
        task = Task("full102", "edge_iiot", "backdoor", "field_missing", 0, 0.3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_root = root / "task"
            run = task_root / "edge_iiot" / "backdoor_seed7"
            clean = root / "clean" / "edge_iiot" / "backdoor_seed7"
            run.mkdir(parents=True)
            clean.mkdir(parents=True)
            payload = {
                "arguments": {
                    "test_corruption_kind": "field_missing",
                    "test_corruption_modality": 0,
                    "test_corruption_severity": 0.3,
                    "test_corruption_seed": 211,
                    "risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
                },
                "split_metadata": {"split_fingerprint": {"combined": "one"}},
                "risk_selection_details": {
                    "pseudo_unknown_learned_blend": {
                        "unknown_or_test_labels_used": False
                    }
                },
            }
            (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
            (run / "provenance.json").write_text("{}", encoding="utf-8")
            payload["split_metadata"]["split_fingerprint"]["combined"] = "two"
            (clean / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                validate_run(task, task_root, root / "clean")


if __name__ == "__main__":
    unittest.main()

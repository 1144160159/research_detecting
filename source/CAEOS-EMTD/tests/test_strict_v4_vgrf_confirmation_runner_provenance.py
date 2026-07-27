from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from run_strict_v4_vgrf_confirmation_matrix import (
    prepare_reference_execution,
)


class VGRFConfirmationRunnerProvenanceTests(unittest.TestCase):
    def test_reference_command_and_provenance_are_frozen_together(
        self,
    ) -> None:
        record = {
            "suite": "suite",
            "scenario": "scenario",
            "unknown_classes": "unknown",
            "training_seed": 313,
        }
        source = {
            "command": [
                "/old/python",
                "train_hybrid_open_set.py",
                "--seed",
                "7",
                "--output-dir",
                "/old/output",
                "--risk-policy-name",
                "old_policy",
                "--estimators",
                "80",
            ]
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            with (
                patch(
                    "run_strict_v4_vgrf_confirmation_matrix.sys.executable",
                    "/active/python",
                ),
                patch(
                    "run_strict_v4_vgrf_confirmation_matrix."
                    "build_run_provenance",
                    return_value={"frozen": True},
                ) as build,
            ):
                command, provenance = prepare_reference_execution(
                    record, source, output
                )
        self.assertEqual(command[0], "/active/python")
        self.assertEqual(command[command.index("--seed") + 1], "313")
        self.assertEqual(
            command[command.index("--risk-policy-name") + 1],
            "strict_v4_vgrf_confirmation_reference_v1",
        )
        self.assertEqual(provenance, {"frozen": True})
        experiment = build.call_args.args[0]
        self.assertEqual(experiment.seed, 313)
        self.assertEqual(experiment.scenario, "scenario")
        self.assertEqual(build.call_args.args[1], command)


if __name__ == "__main__":
    unittest.main()

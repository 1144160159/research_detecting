from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from run_nested_gate_matrix import (
    Experiment,
    ProvenanceMismatchError,
    attach_metrics_arguments,
    build_run_provenance,
    freeze_or_validate_provenance,
)


class MatrixProvenanceTest(unittest.TestCase):
    def test_runner_attaches_effective_gate_arguments_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metrics_path = Path(directory) / "metrics.json"
            metrics_path.write_text(
                json.dumps({"risk_selection": "density_gate_v2"}),
                encoding="utf-8",
            )
            command = [
                sys.executable,
                "train_hybrid_open_set.py",
                "--csv", "cache.csv",
                "--config", "config.json",
                "--split-strategy", "fingerprint_grouped",
                "--max-per-class", "1000",
                "--benign-class", "Normal",
                "--risk-selection", "density_gate_v2",
            ]
            attach_metrics_arguments(metrics_path, command)
            payload = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["arguments"]["max_per_class"], 1000)
            self.assertEqual(payload["arguments"]["csv"], "cache.csv")

            payload["arguments"]["csv"] = "different.csv"
            metrics_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ProvenanceMismatchError, "conflicting metrics arguments"
            ):
                attach_metrics_arguments(metrics_path, command)

    def test_provenance_captures_command_task_inputs_and_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "cache.csv"
            config_path = root / "config.json"
            csv_path.write_text("Label\nBenign\n", encoding="utf-8")
            config_path.write_text("{}", encoding="utf-8")
            declared_sha = "a" * 64
            Path(f"{csv_path}.json").write_text(
                json.dumps({"output_sha256": declared_sha}),
                encoding="utf-8",
            )
            experiment = Experiment(
                "edge_iiot",
                "fingerprinting",
                "Fingerprinting",
                7,
                str(root / "run"),
            )
            command = [
                sys.executable,
                "train_hybrid_open_set.py",
                "--csv",
                str(csv_path),
                "--config",
                str(config_path),
                "--unknown-classes",
                "Fingerprinting",
                "--seed",
                "7",
                "--output-dir",
                experiment.output_dir,
            ]

            provenance = build_run_provenance(experiment, command)

        self.assertEqual(provenance["command"], command)
        self.assertEqual(
            provenance["task"],
            {
                "suite": "edge_iiot",
                "scenario": "fingerprinting",
                "unknown_classes": "Fingerprinting",
                "seed": 7,
            },
        )
        self.assertEqual(
            provenance["inputs"]["csv"]["sidecar_sha"]["declared_sha256"],
            declared_sha,
        )
        self.assertEqual(len(provenance["code"]["sha256"]), 64)
        self.assertEqual(len(provenance["parameter_fingerprint"]), 64)

    def test_legacy_completed_artifact_without_provenance_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            metrics = output / "metrics.json"
            metrics.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ProvenanceMismatchError, "legacy run"):
                freeze_or_validate_provenance(
                    output,
                    {"schema_version": 1, "command": ["first"]},
                    (metrics,),
                )

    def test_changed_frozen_identity_is_rejected_instead_of_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            metrics = output / "metrics.json"
            original = {
                "schema_version": 1,
                "command": ["python", "train.py", "--seed", "7"],
            }
            changed = {
                "schema_version": 1,
                "command": ["python", "train.py", "--seed", "11"],
            }
            self.assertFalse(
                freeze_or_validate_provenance(output, original, (metrics,))
            )
            metrics.write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ProvenanceMismatchError, "incompatible"):
                freeze_or_validate_provenance(output, changed, (metrics,))

            self.assertTrue(
                freeze_or_validate_provenance(output, original, (metrics,))
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from create_gpu_external_preparation_protocol import create_protocol, verify_protocol


class GpuExternalPreparationProtocolTests(unittest.TestCase):
    def make_project(self, root: Path) -> tuple[Path, Path, Path]:
        project = root / "project"
        (project / "results/gpu_malicious_dataset_expansion_protocol_v1").mkdir(
            parents=True
        )
        (project / "results/gpu_dataset_admission_execution_protocol_v1").mkdir(
            parents=True
        )
        (project / "configs").mkdir()
        files = [
            project / "results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json",
            project / "results/gpu_dataset_admission_execution_protocol_v1/protocol.json",
            project / "configs/lsnm2024_external.json",
            project / "configs/cicids2017_strict.json",
        ]
        for path in files:
            path.write_text("{}", encoding="utf-8")
        preparer = project / "prepare.py"
        runner = project / "run.sh"
        preparer.write_text("pass", encoding="utf-8")
        runner.write_text("true", encoding="utf-8")
        return project, preparer, runner

    def test_freezes_caps_seeds_and_bindings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, preparer, runner = self.make_project(root)
            protocol = create_protocol(
                project_root=project,
                output_root=root / "prepared",
                preparer=preparer,
                runner=runner,
            )
            verify_protocol(protocol)
            self.assertEqual(protocol["seeds"], [223, 227, 229])
            self.assertEqual(
                protocol["datasets"]["LSNM2024"]["maximum_rows_per_label"], 4000
            )
            self.assertFalse(
                protocol["claim_boundary"]["unknown_or_test_metric_used_for_preparation"]
            )

    def test_refuses_existing_prepared_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, preparer, runner = self.make_project(root)
            output = root / "prepared/LSNM2024"
            output.mkdir(parents=True)
            (output / "manifest.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "before prepared manifests"):
                create_protocol(
                    project_root=project,
                    output_root=root / "prepared",
                    preparer=preparer,
                    runner=runner,
                )

    def test_waiter_fails_closed_on_admission_failure(self) -> None:
        script = (
            Path(__file__).parents[1]
            / "scripts/wait_and_run_gpu_external_dataset_preparation.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("audit_complete", script)
        self.assertIn("admission_passed", script)
        self.assertIn("blocked_by_admission_failure", script)


if __name__ == "__main__":
    unittest.main()

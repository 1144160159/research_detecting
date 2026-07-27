from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np

from audit_pairwise_deployment_bundle import audit_capture
from test_pairwise_deployment import make_bundle


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PairwiseDeploymentAuditTests(unittest.TestCase):
    def create_capture(self, directory: Path, schema_version: str = "v2") -> None:
        bundle = make_bundle()
        artifact = directory / "bundle.joblib"
        inputs = directory / "inputs.npz"
        outputs = directory / "outputs.npz"
        equivalence_path = directory / "equivalence.json"
        joblib.dump(bundle, artifact)
        views = [
            np.asarray([[0.0, 0.0], [4.0, 0.0]], dtype=np.float32),
            np.asarray([[0.0], [0.0]], dtype=np.float32),
        ]
        output = bundle.predict_views(views)
        np.savez_compressed(
            inputs, view_0=views[0], view_1=views[1]
        )
        np.savez_compressed(
            outputs,
            closed_set_index=output["closed_set_index"],
            probability=output["probability"],
            risk=output["risk"],
            rejected=output["rejected"],
        )
        equivalence = {
            "schema_version": "strict_v4_pairwise_deployment_equivalence_v2",
            "passes": True,
        }
        equivalence_path.write_text(
            json.dumps(equivalence) + "\n", encoding="utf-8"
        )
        manifest = {
            "schema_version": (
                f"strict_v4_pairwise_deployment_capture_{schema_version}"
            ),
            "deployment_artifact": artifact.name,
            "deployment_artifact_sha256": file_hash(artifact),
            "processed_benchmark_inputs": inputs.name,
            "processed_benchmark_inputs_sha256": file_hash(inputs),
            "processed_benchmark_inputs_contain_labels": False,
            "processed_benchmark_expected_outputs": outputs.name,
            "processed_benchmark_expected_outputs_sha256": file_hash(outputs),
            "processed_benchmark_expected_outputs_contain_ground_truth": False,
            "equivalence": equivalence_path.name,
            "equivalence_sha256": file_hash(equivalence_path),
            "source_equivalence": equivalence,
            "deployment_evidence": bundle.evidence(),
            "formal_model_metrics_admitted": 0,
            "storage_policy": "gpu_private_do_not_publish",
        }
        if schema_version == "v3":
            validation_inputs = directory / "validation_inputs.npz"
            validation_outputs = directory / "validation_outputs.npz"
            np.savez_compressed(
                validation_inputs, view_0=views[0], view_1=views[1]
            )
            np.savez_compressed(
                validation_outputs,
                closed_set_index=output["closed_set_index"],
                probability=output["probability"],
                risk=output["risk"],
                rejected=output["rejected"],
            )
            manifest.update(
                {
                    "processed_validation_inputs": validation_inputs.name,
                    "processed_validation_inputs_sha256": file_hash(
                        validation_inputs
                    ),
                    "processed_validation_inputs_contain_labels": False,
                    "processed_validation_expected_outputs": (
                        validation_outputs.name
                    ),
                    "processed_validation_expected_outputs_sha256": file_hash(
                        validation_outputs
                    ),
                    "processed_validation_expected_outputs_contain_labels": False,
                }
            )
        (directory / "capture_manifest.json").write_text(
            json.dumps(manifest) + "\n", encoding="utf-8"
        )

    def test_independent_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.create_capture(directory)
            result = audit_capture(directory)
        self.assertTrue(result["passes"])
        self.assertEqual(result["benchmark_row_count"], 2)
        self.assertEqual(result["formal_model_metrics_admitted"], 0)

    def test_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.create_capture(directory)
            with (directory / "inputs.npz").open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                audit_capture(directory)

    def test_v3_validation_replay_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.create_capture(directory, schema_version="v3")
            result = audit_capture(directory)
        self.assertTrue(result["validation_replay_passes"])
        self.assertEqual(result["validation_row_count"], 2)


if __name__ == "__main__":
    unittest.main()

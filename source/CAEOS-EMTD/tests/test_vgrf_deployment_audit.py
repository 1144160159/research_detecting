from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np

from audit_vgrf_deployment_bundle import audit_capture
from build_vgrf_deployment_bundle import file_hash
from test_vgrf_deployment import make_vgrf


class VGRFDeploymentAuditTests(unittest.TestCase):
    def create_capture(self, root: Path, schema_version: str = "v1") -> None:
        bundle = make_vgrf()
        artifact = root / "vgrf.joblib"
        inputs_path = root / "inputs.npz"
        outputs_path = root / "outputs.npz"
        equivalence_path = root / "equivalence.json"
        joblib.dump(bundle, artifact)
        views = [
            np.asarray([[-1.0], [1.0]], dtype=np.float32),
            np.asarray([[0.5], [-0.5]], dtype=np.float32),
        ]
        output = bundle.predict_views(views)
        np.savez_compressed(
            inputs_path, view_0=views[0], view_1=views[1]
        )
        np.savez_compressed(
            outputs_path,
            closed_set_index=output["closed_set_index"],
            probability=output["probability"],
            risk=output["risk"],
            rejected=output["rejected"],
        )
        equivalence = {
            "schema_version": "strict_v4_vgrf_deployment_equivalence_v1",
            "passes": True,
        }
        equivalence_path.write_text(
            json.dumps(equivalence) + "\n", encoding="utf-8"
        )
        manifest = {
            "schema_version": (
                f"strict_v4_vgrf_deployment_capture_{schema_version}"
            ),
            "deployment_artifact": artifact.name,
            "deployment_artifact_sha256": file_hash(artifact),
            "processed_benchmark_inputs": inputs_path.name,
            "processed_benchmark_inputs_sha256": file_hash(inputs_path),
            "processed_benchmark_expected_outputs": outputs_path.name,
            "processed_benchmark_expected_outputs_sha256": file_hash(
                outputs_path
            ),
            "equivalence": equivalence_path.name,
            "equivalence_sha256": file_hash(equivalence_path),
            "source_equivalence": equivalence,
            "deployment_evidence": bundle.evidence(),
            "validation_source": {
                "validation_labels_stored_in_deployment_artifact": False
            },
            "formal_model_metrics_admitted": 0,
            "formal_external_execution_admitted": False,
        }
        if schema_version == "v2":
            compatibility_path = root / "compatibility.json"
            compatibility = {
                "gate_decision_equal": True,
                "test_probability_array_equal": True,
                "test_risk_max_absolute_difference": 0.01,
            }
            compatibility_path.write_text(
                json.dumps(compatibility) + "\n", encoding="utf-8"
            )
            manifest.update(
                {
                    "source_runtime_compatibility": compatibility_path.name,
                    "source_runtime_compatibility_sha256": file_hash(
                        compatibility_path
                    ),
                }
            )
        (root / "capture_manifest.json").write_text(
            json.dumps(manifest) + "\n", encoding="utf-8"
        )

    def test_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_capture(root)
            result = audit_capture(root)
        self.assertTrue(result["passes"])
        self.assertEqual(result["benchmark_row_count"], 2)

    def test_artifact_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_capture(root)
            with (root / "vgrf.joblib").open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "hash-mismatched"):
                audit_capture(root)

    def test_v2_source_runtime_compatibility_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_capture(root, schema_version="v2")
            result = audit_capture(root)
        self.assertTrue(result["source_runtime_gate_decision_equal"])
        self.assertTrue(result["source_runtime_probability_equal"])
        self.assertEqual(
            result["source_runtime_risk_max_absolute_difference"], 0.01
        )


if __name__ == "__main__":
    unittest.main()

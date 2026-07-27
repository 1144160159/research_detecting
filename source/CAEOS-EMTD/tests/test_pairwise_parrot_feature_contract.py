from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import joblib

from audit_pairwise_parrot_feature_contract import audit_contract
from test_pairwise_deployment import make_bundle
from test_vgrf_deployment import make_vgrf


class PairwiseParrotFeatureContractTests(unittest.TestCase):
    def create_inputs(self, directory: Path) -> tuple[Path, Path, Path]:
        artifact = directory / "bundle.joblib"
        config_path = directory / "config.json"
        protocol_path = directory / "protocol.json"
        bundle = make_bundle()
        joblib.dump(bundle, artifact)
        config_path.write_text(
            json.dumps(
                {
                    "modalities": {
                        "flow": ["a", "b"],
                        "time": ["c"],
                    }
                }
            ),
            encoding="utf-8",
        )
        bundle.source_config_sha256 = hashlib.sha256(
            config_path.read_bytes()
        ).hexdigest()
        joblib.dump(bundle, artifact)
        protocol_path.write_text(
            json.dumps(
                {
                    "schema_version": (
                        "parrot2025_full_no_decryption_feature_protocol_v1"
                    ),
                    "status": "frozen_before_full_feature_extraction",
                    "manifest_sha256": "a" * 64,
                    "feature_columns": ["a", "b", "c"],
                    "feature_count": 3,
                    "input_contract": {
                        "capture_group_is_indivisible": True,
                        "deep_packet_inspection": False,
                        "payload_decryption": False,
                        "ssl_key_members_read": 0,
                    },
                    "safety_policy": {
                        "training_use": False,
                        "validation_use": False,
                        "calibration_use": False,
                        "threshold_selection_use": False,
                        "feature_selection_use": False,
                        "model_metrics_generated": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        return artifact, config_path, protocol_path

    def test_exact_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            inputs = self.create_inputs(Path(temporary))
            result = audit_contract(*inputs)
        self.assertTrue(result["passes"])
        self.assertEqual(result["feature_count"], 3)
        self.assertFalse(result["formal_external_execution_admitted"])

    def test_reordered_protocol_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, config_path, protocol_path = self.create_inputs(
                Path(temporary)
            )
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol["feature_columns"] = ["b", "a", "c"]
            protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from PARROT"):
                audit_contract(artifact, config_path, protocol_path)

    def test_vgrf_wrapper_uses_pairwise_feature_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            artifact, config_path, protocol_path = self.create_inputs(directory)
            vgrf = make_vgrf()
            vgrf.pairwise = joblib.load(artifact)
            joblib.dump(vgrf, artifact)
            result = audit_contract(
                artifact, config_path, protocol_path
            )
        self.assertTrue(result["passes"])
        self.assertEqual(
            result["deployment_algorithm"],
            "caeos_validation_gated_class_conditional_reliability_fusion",
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required")
class OpenDetectDeploymentBundleTests(unittest.TestCase):
    def test_capture_and_independent_audit_roundtrip(self) -> None:
        import numpy as np
        import torch

        from audit_opendetect_deployment_bundle import audit
        from caeos.open_detect import OpenDetectClassifier
        from capture_opendetect_deployment_bundle import capture
        from create_strict_v4_external_confirmation_protocol import (
            file_hash,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            pairwise = root / "pairwise"
            output = root / "capture"
            source.mkdir()
            pairwise.mkdir()
            config = root / "config.json"
            config.write_text("{}", encoding="utf-8")
            input_dims = [3, 2]
            class_names = ["a", "b"]
            model = OpenDetectClassifier(
                input_dims, 2, 8, 4, 0.0, 1.0, 0.005
            ).eval()
            rng = np.random.default_rng(7)
            arrays = [
                rng.normal(size=(9, width)).astype(np.float32)
                for width in input_dims
            ]
            device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            model = model.to(device)
            with torch.no_grad():
                logits = model(
                    [
                        torch.as_tensor(value, device=device)
                        for value in arrays
                    ],
                    None,
                )["logits"]
            prediction = logits.argmax(dim=1).cpu().numpy()
            risk = (
                -logits.max(dim=1).values.cpu().numpy()
            ).astype(np.float64)
            checkpoint = {
                "model_state": {
                    name: value.detach().cpu()
                    for name, value in model.state_dict().items()
                },
                "arguments": {
                    "model": "opendetect",
                    "hidden_dim": 8,
                    "embedding_dim": 4,
                    "dropout": 0.0,
                    "temperature": 1.0,
                    "open_detect_generative_weight": 0.005,
                    "config": str(config),
                },
                "class_names": class_names,
                "input_dims": input_dims,
            }
            torch.save(checkpoint, source / "model.pt")
            (source / "metrics.json").write_text(
                json.dumps(
                    {
                        "model": "opendetect",
                        "validation_thresholds": {
                            "opendetect": float(np.median(risk))
                        },
                        "split_sizes": {"test": len(risk)},
                        "selection_evidence": {
                            "unknown_or_test_labels_used_for_fitting_or_selection": False
                        },
                    }
                ),
                encoding="utf-8",
            )
            np.savez_compressed(
                source / "scores.npz",
                prediction_opendetect=prediction,
                test_opendetect=risk,
            )
            (source / "provenance.json").write_text(
                json.dumps(
                    {
                        "inputs": {
                            "config": {"path": str(config)}
                        }
                    }
                ),
                encoding="utf-8",
            )
            input_path = pairwise / "processed_benchmark_inputs.npz"
            np.savez_compressed(
                input_path,
                **{
                    f"view_{index}": value
                    for index, value in enumerate(arrays)
                },
            )
            (pairwise / "capture_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "strict_v4_pairwise_deployment_capture_v3"
                        ),
                        "source_equivalence": {"passes": True},
                        "processed_benchmark_inputs": input_path.name,
                        "processed_benchmark_inputs_sha256": file_hash(
                            input_path
                        ),
                    }
                ),
                encoding="utf-8",
            )
            manifest = capture(source, pairwise, output)
            result = audit(output)
        self.assertTrue(manifest["source_equivalence"]["passes"])
        self.assertTrue(result["passes"])
        self.assertTrue(result["exact_replay_passes"])


if __name__ == "__main__":
    unittest.main()

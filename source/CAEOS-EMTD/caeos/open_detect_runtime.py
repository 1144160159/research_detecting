from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import torch

from caeos.open_detect import OpenDetectClassifier, open_detect_risk


@dataclass
class OpenDetectRuntime:
    model: OpenDetectClassifier
    device_name: str

    @classmethod
    def from_checkpoint(
        cls, checkpoint: dict[str, Any], device_name: str = "cpu"
    ) -> "OpenDetectRuntime":
        arguments = checkpoint.get("arguments", {})
        if arguments.get("model") != "opendetect":
            raise ValueError("checkpoint is not an OpenDetect model")
        model = OpenDetectClassifier(
            list(checkpoint["input_dims"]),
            len(checkpoint["class_names"]),
            int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]),
            float(arguments["dropout"]),
            float(arguments["temperature"]),
            float(arguments["open_detect_generative_weight"]),
        )
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.to(torch.device(device_name)).eval()
        return cls(model=model, device_name=str(device_name))

    def synchronize(self) -> None:
        if torch.device(self.device_name).type == "cuda":
            torch.cuda.synchronize(torch.device(self.device_name))

    def predict(self, views: Sequence[np.ndarray]) -> dict[str, np.ndarray]:
        arrays = [np.asarray(view, dtype=np.float32) for view in views]
        if not arrays or len({len(view) for view in arrays}) != 1:
            raise ValueError("OpenDetect runtime requires aligned modality views")
        tensors = [torch.from_numpy(view).to(self.device_name) for view in arrays]
        with torch.inference_mode():
            output = self.model(tensors)
            logits = output["logits"].detach().cpu().numpy()
        prediction = logits.argmax(axis=1)
        risk = open_detect_risk(logits)
        return {
            "prediction": np.asarray(prediction, dtype=np.int64),
            "logits": np.asarray(logits, dtype=np.float64),
            "risk": np.asarray(risk, dtype=np.float64),
        }

    def evidence(self) -> dict[str, object]:
        return {
            "schema_version": "strict_v4_opendetect_runtime_v1",
            "device": self.device_name,
            "parameter_count": int(sum(p.numel() for p in self.model.parameters())),
            "contains_training_or_test_labels": False,
            "contains_test_ground_truth": False,
        }

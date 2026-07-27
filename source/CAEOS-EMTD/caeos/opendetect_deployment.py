from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import torch


@dataclass
class OpenDetectDeploymentBundle:
    model: Any
    class_names: tuple[str, ...]
    input_dims: tuple[int, ...]
    selected_threshold: float
    source_model_sha256: str
    source_config_sha256: str

    def __post_init__(self) -> None:
        self.class_names = tuple(str(value) for value in self.class_names)
        self.input_dims = tuple(int(value) for value in self.input_dims)
        self.selected_threshold = float(self.selected_threshold)
        if len(self.class_names) < 2:
            raise ValueError("OpenDetect bundle requires at least two classes")
        if not self.input_dims or any(value <= 0 for value in self.input_dims):
            raise ValueError("OpenDetect input dimensions are invalid")
        if not np.isfinite(self.selected_threshold):
            raise ValueError("OpenDetect threshold must be finite")
        for value in (
            self.source_model_sha256,
            self.source_config_sha256,
        ):
            if len(value) != 64:
                raise ValueError("OpenDetect source SHA-256 is invalid")
        self.model = self.model.cpu().eval()

    @torch.no_grad()
    def predict_views(
        self,
        views: Sequence[np.ndarray],
        device: str | torch.device | None = None,
    ) -> dict[str, np.ndarray]:
        if len(views) != len(self.input_dims):
            raise ValueError("OpenDetect view count mismatch")
        arrays = [np.asarray(view, dtype=np.float32) for view in views]
        row_counts = {len(view) for view in arrays}
        if len(row_counts) != 1:
            raise ValueError("OpenDetect views are not row aligned")
        for view, width in zip(arrays, self.input_dims):
            if view.ndim != 2 or view.shape[1] != width:
                raise ValueError("OpenDetect view width mismatch")
            if not np.isfinite(view).all():
                raise ValueError("OpenDetect input contains non-finite values")
        active = torch.device(
            device
            if device is not None
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = self.model.to(active).eval()
        tensors = [
            torch.as_tensor(view, dtype=torch.float32, device=active)
            for view in arrays
        ]
        output = self.model(tensors, None)
        logits = output["logits"]
        probability = torch.softmax(logits, dim=1)
        risk = -logits.max(dim=1).values
        prediction = logits.argmax(dim=1)
        probability_array = probability.detach().cpu().numpy()
        risk_array = risk.detach().cpu().numpy().astype(np.float64)
        prediction_array = prediction.detach().cpu().numpy().astype(np.int64)
        rejected = risk_array > self.selected_threshold
        return {
            "closed_set_index": prediction_array,
            "probability": probability_array,
            "risk": risk_array,
            "rejected": rejected,
        }

    def evidence(self) -> dict[str, object]:
        return {
            "schema_version": (
                "strict_v4_opendetect_deployment_bundle_v1"
            ),
            "class_count": len(self.class_names),
            "input_dims": list(self.input_dims),
            "feature_count": sum(self.input_dims),
            "selected_threshold": self.selected_threshold,
            "source_model_sha256": self.source_model_sha256,
            "source_config_sha256": self.source_config_sha256,
            "input_contract": "frozen_processed_multiview_float32",
            "risk_transform": "negative_max_class_conditional_kl_logit",
            "unknown_or_test_labels_used_for_model_or_threshold_fitting": False,
            "contains_validation_labels": False,
            "contains_test_labels": False,
            "storage_policy": "gpu_private_do_not_publish",
        }

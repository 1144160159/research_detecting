from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from caeos.class_conditional_reliability_fusion import (
    reliability_fused_candidate,
)
from caeos.pairwise_deployment import UNKNOWN_CLASS_NAME, PairwiseDeploymentBundle
from caeos.validation_gated_reliability_fusion import apply_validation_gate


@dataclass
class VGRFDeploymentBundle:
    """Deployable known-validation-gated reliability fusion state."""

    pairwise: PairwiseDeploymentBundle
    class_reliability: np.ndarray
    validation_gate: dict[str, Any]
    selected_threshold: float
    risk_blend: float
    source_protocol_manifest_sha256: str

    def __post_init__(self) -> None:
        self.class_reliability = np.asarray(
            self.class_reliability, dtype=np.float64
        )
        expected = (
            len(self.pairwise.modality_names),
            len(self.pairwise.class_names),
        )
        if self.class_reliability.shape != expected:
            raise ValueError(
                f"class reliability shape {self.class_reliability.shape} "
                f"does not match {expected}"
            )
        if not np.isfinite(self.class_reliability).all():
            raise ValueError("class reliability contains non-finite values")
        if np.any(
            (self.class_reliability <= 0.0)
            | (self.class_reliability > 1.0)
        ):
            raise ValueError("class reliability must be in (0, 1]")
        if self.validation_gate.get("enabled") not in (True, False):
            raise ValueError("validation gate requires a boolean enabled decision")
        self.selected_threshold = float(self.selected_threshold)
        if not np.isfinite(self.selected_threshold):
            raise ValueError("selected threshold must be finite")
        self.risk_blend = float(self.risk_blend)
        if not 0.0 <= self.risk_blend <= 1.0:
            raise ValueError("risk blend must be in [0, 1]")
        if len(self.source_protocol_manifest_sha256) != 64:
            raise ValueError("source protocol manifest SHA-256 is invalid")

    def _predict_selected(
        self, views: Sequence[np.ndarray]
    ) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        runtime = self.pairwise.runtime
        base = runtime.predict(views)
        model_views, _, _ = runtime._model_inputs(views)
        evidence = runtime.model.predict_with_evidence(model_views)
        required = (
            "view_probability",
            "global_probability",
            "view_fused_probability",
            "gate",
            "final_probability",
        )
        missing = [name for name in required if name not in evidence]
        if missing:
            raise ValueError(f"pairwise runtime evidence lacks fields: {missing}")
        base_probability = np.asarray(base["probability"], dtype=np.float64)
        incumbent_probability = np.asarray(
            evidence["final_probability"], dtype=np.float64
        )
        if not np.array_equal(base_probability, incumbent_probability):
            maximum = float(
                np.max(np.abs(base_probability - incumbent_probability))
            )
            raise ValueError(
                "pairwise probability differs from evidence final probability: "
                f"{maximum}"
            )
        candidate = reliability_fused_candidate(
            view_probability=evidence["view_probability"],
            class_reliability=self.class_reliability,
            global_probability=evidence["global_probability"],
            incumbent_view_fused_probability=evidence[
                "view_fused_probability"
            ],
            incumbent_gate=evidence["gate"],
            incumbent_final_probability=incumbent_probability,
            incumbent_risk=base["risk"],
            risk_blend=self.risk_blend,
        )
        probability, risk = apply_validation_gate(
            gate=self.validation_gate,
            incumbent_probability=incumbent_probability,
            candidate_probability=np.asarray(candidate["candidate_probability"]),
            incumbent_risk=np.asarray(base["risk"]),
            candidate_risk=np.asarray(candidate["candidate_risk"]),
        )
        probability = np.asarray(probability, dtype=np.float64)
        risk = np.asarray(risk, dtype=np.float64)
        if (
            probability.ndim != 2
            or probability.shape[1] != len(self.pairwise.class_names)
            or risk.shape != (len(probability),)
        ):
            raise ValueError("VGRF output shape is invalid")
        if not np.isfinite(probability).all() or not np.isfinite(risk).all():
            raise ValueError("VGRF output contains non-finite values")
        return probability, risk, candidate

    def predict_views(
        self,
        views: Sequence[np.ndarray],
        quality: np.ndarray | None = None,
    ) -> dict[str, np.ndarray]:
        probability, risk, _ = self._predict_selected(views)
        prediction = probability.argmax(axis=1).astype(np.int64)
        rejected = risk > self.selected_threshold
        open_set_index = np.where(rejected, -1, prediction).astype(np.int64)
        open_set_name = np.asarray(
            [
                (
                    UNKNOWN_CLASS_NAME
                    if reject
                    else self.pairwise.class_names[index]
                )
                for index, reject in zip(prediction, rejected)
            ],
            dtype=object,
        )
        result = {
            "closed_set_index": prediction,
            "open_set_index": open_set_index,
            "open_set_name": open_set_name,
            "probability": probability,
            "risk": risk,
            "rejected": rejected,
        }
        if quality is not None:
            quality_array = np.asarray(quality, dtype=np.float32)
            expected = (
                len(prediction),
                len(self.pairwise.modality_names),
            )
            if quality_array.shape != expected:
                raise ValueError(
                    f"quality shape {quality_array.shape} does not match {expected}"
                )
            result["modality_quality"] = quality_array
        return result

    def predict_frame(self, frame) -> dict[str, np.ndarray]:
        views, quality = self.pairwise.transform_frame(frame)
        return self.predict_views(views, quality)

    def evidence(self) -> dict[str, Any]:
        return {
            "schema_version": "strict_v4_vgrf_deployment_bundle_v1",
            "algorithm": (
                "caeos_validation_gated_class_conditional_reliability_fusion"
            ),
            "feature_schema_sha256": self.pairwise.feature_schema_sha256,
            "feature_count": len(self.pairwise.feature_columns),
            "modality_names": list(self.pairwise.modality_names),
            "class_count": len(self.pairwise.class_names),
            "validation_gate_enabled": bool(
                self.validation_gate["enabled"]
            ),
            "selected_threshold": self.selected_threshold,
            "risk_blend": self.risk_blend,
            "source_protocol_manifest_sha256": (
                self.source_protocol_manifest_sha256
            ),
            "contains_raw_input_rows": False,
            "contains_fitted_nonparametric_reference_vectors": True,
            "contains_fitted_class_conditional_state": True,
            "contains_known_validation_aggregate_statistics": True,
            "contains_validation_labels": False,
            "contains_test_labels": False,
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
            "storage_policy": "gpu_private_do_not_publish",
            "pairwise_evidence": self.pairwise.evidence(),
        }

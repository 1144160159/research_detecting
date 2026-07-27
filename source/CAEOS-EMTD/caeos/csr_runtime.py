from __future__ import annotations

from typing import Any, Dict, Sequence

import numpy as np

from caeos.conformal_safe_routing import (
    KnownValidationMaxRoutingCalibration,
)
from caeos.mdr_runtime import MDRRuntime


class CSRRuntime(MDRRuntime):
    """MDR-compatible dual runtime with risk-only safe routing."""

    health_calibration: KnownValidationMaxRoutingCalibration

    def predict(self, raw_views: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
        views = [np.asarray(view) for view in raw_views]
        clean = self.clean_runtime.predict(views)
        robust = self.robust_runtime.predict(views)
        clean_evidence = self._model_evidence(self.clean_runtime, views)
        robust_evidence = self._model_evidence(self.robust_runtime, views)
        missing = self.missing_mask(views)
        missing_risk = self._missing_aware_risk(
            views, missing, robust["risk"]
        )
        routed = self.health_calibration.apply(
            clean_evidence,
            robust_evidence,
            clean["risk"],
            robust["risk"],
            missing_risk,
            missing.any(axis=1),
        )
        return {
            **routed,
            "clean_probability": clean["probability"],
            "robust_probability": robust["probability"],
            "clean_risk": clean["risk"],
            "robust_risk": robust["risk"],
            "missing_risk": missing_risk,
            "view_missing": missing,
            "threshold": np.full(
                len(routed["probability"]),
                self.clean_threshold,
                dtype=np.float64,
            ),
        }

    def evidence(self) -> Dict[str, Any]:
        return {
            "schema_version": "strict_v4_csr_caeos_runtime_v1",
            "algorithm": "csr_caeos_v1",
            "augmentation_weight": float(self.augmentation_weight),
            "training_seed": int(self.training_seed),
            "augmentation_seed": int(self.augmentation_seed),
            "clean_threshold": float(self.clean_threshold),
            "modality_count": int(len(self.training_feature_scales)),
            "routing_calibration": self.health_calibration.evidence(),
            "prediction_probability_source": "clean_pairwise_exact",
            "risk_policy": "active_monotone_uplift_otherwise_clean_exact",
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection": (
                False
            ),
            "contains_test_ground_truth": False,
        }

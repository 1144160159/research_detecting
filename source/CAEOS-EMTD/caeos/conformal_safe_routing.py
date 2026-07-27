from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from caeos.mdr_fusion import (
    _maximum_local_conflict,
    js_divergence,
    quantile_map,
)


@dataclass(frozen=True)
class KnownValidationMaxRoutingCalibration:
    """Risk-only routing with a finite-sample maximum health boundary."""

    conflict_threshold: float
    disagreement_threshold: float
    clean_risk_reference: np.ndarray
    robust_risk_reference: np.ndarray
    missing_risk_reference: np.ndarray
    calibration_count: int

    @classmethod
    def fit(
        cls,
        clean_validation_evidence: Dict[str, np.ndarray],
        robust_validation_evidence: Dict[str, np.ndarray],
        clean_validation_risk: np.ndarray,
        robust_validation_risk: np.ndarray,
        missing_validation_risk: np.ndarray,
    ) -> "KnownValidationMaxRoutingCalibration":
        clean_probability = np.asarray(
            clean_validation_evidence["final_probability"], dtype=np.float64
        )
        robust_probability = np.asarray(
            robust_validation_evidence["final_probability"], dtype=np.float64
        )
        conflict = _maximum_local_conflict(clean_validation_evidence)
        disagreement = js_divergence(clean_probability, robust_probability)
        references = [
            np.asarray(clean_validation_risk, dtype=np.float64),
            np.asarray(robust_validation_risk, dtype=np.float64),
            np.asarray(missing_validation_risk, dtype=np.float64),
        ]
        lengths = {
            len(conflict),
            len(disagreement),
            *(len(reference) for reference in references),
        }
        if len(lengths) != 1 or not lengths or next(iter(lengths)) < 2:
            raise ValueError("aligned non-trivial calibration arrays required")
        if not all(np.isfinite(reference).all() for reference in references):
            raise ValueError("risk calibration arrays must be finite")
        count = len(conflict)
        return cls(
            conflict_threshold=float(conflict.max()),
            disagreement_threshold=float(disagreement.max()),
            clean_risk_reference=references[0],
            robust_risk_reference=references[1],
            missing_risk_reference=references[2],
            calibration_count=count,
        )

    def apply(
        self,
        clean_evidence: Dict[str, np.ndarray],
        robust_evidence: Dict[str, np.ndarray],
        clean_risk: np.ndarray,
        robust_risk: np.ndarray,
        missing_risk: np.ndarray,
        any_missing: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        clean_probability = np.asarray(
            clean_evidence["final_probability"], dtype=np.float64
        )
        robust_probability = np.asarray(
            robust_evidence["final_probability"], dtype=np.float64
        )
        conflict = _maximum_local_conflict(clean_evidence)
        disagreement = js_divergence(clean_probability, robust_probability)
        clean_risk = np.asarray(clean_risk, dtype=np.float64)
        any_missing = np.asarray(any_missing, dtype=bool)
        lengths = {
            len(clean_probability),
            len(robust_probability),
            len(conflict),
            len(disagreement),
            len(clean_risk),
            len(robust_risk),
            len(missing_risk),
            len(any_missing),
        }
        if len(lengths) != 1:
            raise ValueError("routing arrays are not aligned")
        conflict_active = (
            conflict > float(self.conflict_threshold) + 1e-12
        )
        disagreement_active = (
            disagreement > float(self.disagreement_threshold) + 1e-12
        )
        active = any_missing | conflict_active | disagreement_active
        robust_mapped = quantile_map(
            self.robust_risk_reference,
            self.clean_risk_reference,
            robust_risk,
        )
        missing_mapped = quantile_map(
            self.missing_risk_reference,
            self.clean_risk_reference,
            missing_risk,
        )
        routed = np.where(any_missing, missing_mapped, robust_mapped)
        uplifted = np.maximum(clean_risk, routed)
        risk = np.where(active, uplifted, clean_risk)
        prediction = clean_probability.argmax(axis=1).astype(np.int64)
        return {
            "prediction": prediction,
            "probability": clean_probability.copy(),
            "risk": risk,
            "active": active,
            "any_missing": any_missing,
            "conflict_active": conflict_active,
            "disagreement_active": disagreement_active,
            "conflict": conflict,
            "disagreement": disagreement,
            "clean_risk": clean_risk,
            "routed_risk": routed,
        }

    def evidence(self) -> Dict[str, object]:
        return {
            "schema_version": "csr_caeos_known_validation_max_calibration_v1",
            "routing_policy": "risk_only_monotone_uplift",
            "prediction_source": "clean_pairwise_exact",
            "probability_source": "clean_pairwise_exact",
            "conflict_threshold": float(self.conflict_threshold),
            "disagreement_threshold": float(
                self.disagreement_threshold
            ),
            "calibration_count": int(self.calibration_count),
            "next_exchangeable_false_activation_bound": float(
                1.0 / (self.calibration_count + 1)
            ),
            "unknown_or_test_labels_used": False,
        }

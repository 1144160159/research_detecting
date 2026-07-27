from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


def js_divergence(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.shape != right.shape or left.ndim != 2:
        raise ValueError("probability arrays must be matching two-dimensional arrays")
    left = left / np.clip(left.sum(axis=1, keepdims=True), 1e-12, None)
    right = right / np.clip(right.sum(axis=1, keepdims=True), 1e-12, None)
    middle = 0.5 * (left + right)
    return 0.5 * (
        np.sum(left * np.log(np.clip(left / middle, 1e-12, None)), axis=1)
        + np.sum(right * np.log(np.clip(right / middle, 1e-12, None)), axis=1)
    )


def quantile_map(
    source_reference: np.ndarray,
    target_reference: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    source = np.sort(np.asarray(source_reference, dtype=np.float64))
    target = np.sort(np.asarray(target_reference, dtype=np.float64))
    values = np.asarray(values, dtype=np.float64)
    if source.ndim != 1 or target.ndim != 1 or not len(source) or not len(target):
        raise ValueError("risk references must be non-empty one-dimensional arrays")
    if not (
        np.isfinite(source).all()
        and np.isfinite(target).all()
        and np.isfinite(values).all()
    ):
        raise ValueError("risk calibration arrays must be finite")
    source_grid = (np.arange(len(source), dtype=np.float64) + 0.5) / len(source)
    target_grid = (np.arange(len(target), dtype=np.float64) + 0.5) / len(target)
    quantiles = np.interp(values, source, source_grid, left=0.0, right=1.0)
    return np.interp(quantiles, target_grid, target, left=target[0], right=target[-1])


def _maximum_local_conflict(evidence: Dict[str, np.ndarray]) -> np.ndarray:
    local = np.asarray(evidence["local_conflict"], dtype=np.float64)
    if local.ndim != 2 or not np.isfinite(local).all():
        raise ValueError("local conflict must be a finite two-dimensional array")
    return local.max(axis=1)


@dataclass(frozen=True)
class KnownOnlyHealthCalibration:
    conflict_threshold: float
    disagreement_threshold: float
    quantile: float
    clean_risk_reference: np.ndarray
    robust_risk_reference: np.ndarray
    missing_risk_reference: np.ndarray

    @classmethod
    def fit(
        cls,
        clean_validation_evidence: Dict[str, np.ndarray],
        robust_validation_evidence: Dict[str, np.ndarray],
        clean_validation_risk: np.ndarray,
        robust_validation_risk: np.ndarray,
        missing_validation_risk: np.ndarray,
        *,
        quantile: float = 0.99,
    ) -> "KnownOnlyHealthCalibration":
        if not 0.5 < quantile < 1.0:
            raise ValueError("health quantile must be in (0.5, 1)")
        clean_probability = np.asarray(
            clean_validation_evidence["final_probability"], dtype=np.float64
        )
        robust_probability = np.asarray(
            robust_validation_evidence["final_probability"], dtype=np.float64
        )
        conflict = _maximum_local_conflict(clean_validation_evidence)
        disagreement = js_divergence(clean_probability, robust_probability)
        lengths = {
            len(conflict),
            len(disagreement),
            len(clean_validation_risk),
            len(robust_validation_risk),
            len(missing_validation_risk),
        }
        if len(lengths) != 1:
            raise ValueError("known-validation calibration arrays are not aligned")
        return cls(
            conflict_threshold=float(np.quantile(conflict, quantile)),
            disagreement_threshold=float(np.quantile(disagreement, quantile)),
            quantile=float(quantile),
            clean_risk_reference=np.asarray(
                clean_validation_risk, dtype=np.float64
            ),
            robust_risk_reference=np.asarray(
                robust_validation_risk, dtype=np.float64
            ),
            missing_risk_reference=np.asarray(
                missing_validation_risk, dtype=np.float64
            ),
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
        any_missing = np.asarray(any_missing, dtype=bool)
        if len(any_missing) != len(clean_probability):
            raise ValueError("missingness mask is not aligned")
        active = (
            any_missing
            | (conflict > self.conflict_threshold + 1e-12)
            | (disagreement > self.disagreement_threshold + 1e-12)
        )
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
        active_risk = np.where(any_missing, missing_mapped, robust_mapped)
        clean_risk = np.asarray(clean_risk, dtype=np.float64)
        risk = np.where(active, active_risk, clean_risk)
        clean_prediction = clean_probability.argmax(axis=1)
        robust_prediction = robust_probability.argmax(axis=1)
        prediction = np.where(active, robust_prediction, clean_prediction)
        return {
            "prediction": prediction.astype(np.int64),
            "risk": risk,
            "active": active,
            "any_missing": any_missing,
            "conflict": conflict,
            "disagreement": disagreement,
            "clean_prediction": clean_prediction.astype(np.int64),
            "robust_prediction": robust_prediction.astype(np.int64),
        }

    def evidence(self) -> Dict[str, object]:
        return {
            "schema_version": "mdr_caeos_known_only_health_calibration_v1",
            "health_quantile": self.quantile,
            "conflict_threshold": self.conflict_threshold,
            "disagreement_threshold": self.disagreement_threshold,
            "clean_reference_count": int(len(self.clean_risk_reference)),
            "robust_reference_count": int(len(self.robust_risk_reference)),
            "missing_reference_count": int(len(self.missing_risk_reference)),
            "unknown_or_test_labels_used": False,
        }

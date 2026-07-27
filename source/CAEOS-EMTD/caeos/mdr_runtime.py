from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

import numpy as np

from caeos.mdr_fusion import KnownOnlyHealthCalibration
from caeos.pairwise_runtime import (
    PairwiseRuntime,
    stable_empirical_tail_scores,
)
from train_hybrid_open_set import missing_aware_cauchy_risk


@dataclass
class MDRRuntime:
    """Deployable clean/robust runtime with known-only health calibration."""

    clean_runtime: PairwiseRuntime
    robust_runtime: PairwiseRuntime
    health_calibration: KnownOnlyHealthCalibration
    missing_fraction_thresholds: np.ndarray
    training_feature_scales: List[np.ndarray]
    clean_threshold: float
    augmentation_weight: float
    training_seed: int
    augmentation_seed: int

    def __post_init__(self) -> None:
        self.missing_fraction_thresholds = np.asarray(
            self.missing_fraction_thresholds, dtype=np.float64
        )
        self.training_feature_scales = [
            np.asarray(scale, dtype=np.float64)
            for scale in self.training_feature_scales
        ]
        if len(self.training_feature_scales) != len(
            self.missing_fraction_thresholds
        ):
            raise ValueError("MDR modality calibration sizes differ")
        if not 0.0 <= float(self.augmentation_weight) <= 1.0:
            raise ValueError("augmentation weight must be in [0, 1]")

    @staticmethod
    def _model_evidence(
        runtime: PairwiseRuntime, raw_views: Sequence[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        model_views, _, _ = runtime._model_inputs(raw_views)
        evidence = runtime.model.predict_with_evidence(model_views)
        return {
            "final_probability": np.asarray(
                evidence["final_probability"], dtype=np.float64
            ),
            "local_conflict": np.asarray(
                evidence["local_conflict"], dtype=np.float64
            ),
        }

    def missing_mask(self, raw_views: Sequence[np.ndarray]) -> np.ndarray:
        if len(raw_views) != len(self.missing_fraction_thresholds):
            raise ValueError("MDR runtime received the wrong number of modalities")
        masks = []
        for view, threshold in zip(
            raw_views, self.missing_fraction_thresholds
        ):
            values = np.asarray(view)
            zero_fraction = np.mean(np.isclose(values, 0.0), axis=1)
            masks.append(
                (zero_fraction > float(threshold) + 1e-12)
                | np.all(np.isclose(values, 0.0), axis=1)
            )
        return np.stack(masks, axis=1)

    def _missing_aware_risk(
        self,
        raw_views: Sequence[np.ndarray],
        missing: np.ndarray,
        fallback: np.ndarray,
    ) -> np.ndarray:
        components, _ = self.robust_runtime.component_values(raw_views)
        names = sorted(
            (
                name
                for name in components
                if name.startswith("knn_view_")
            ),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        if len(names) != missing.shape[1]:
            raise ValueError("MDR view-risk count differs from missingness mask")
        view_risks = np.stack(
            [
                stable_empirical_tail_scores(
                    self.robust_runtime.tail_calibrator.reference[name],
                    components[name],
                    self.robust_runtime._tail_cluster_starts[name],
                )
                for name in names
            ],
            axis=1,
        )
        return missing_aware_cauchy_risk(view_risks, missing, fallback)

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
        fused = self.health_calibration.apply(
            clean_evidence,
            robust_evidence,
            clean["risk"],
            robust["risk"],
            missing_risk,
            missing.any(axis=1),
        )
        probability = np.where(
            fused["active"][:, None],
            robust["probability"],
            clean["probability"],
        )
        return {
            **fused,
            "probability": probability,
            "clean_probability": clean["probability"],
            "robust_probability": robust["probability"],
            "clean_risk": clean["risk"],
            "robust_risk": robust["risk"],
            "missing_risk": missing_risk,
            "view_missing": missing,
            "threshold": np.full(
                len(probability), self.clean_threshold, dtype=np.float64
            ),
        }

    def corrupt(
        self,
        raw_views: Sequence[np.ndarray],
        *,
        family: str,
        modality: int,
        severity: float,
        seed: int,
    ) -> List[np.ndarray]:
        values = [np.asarray(view).copy() for view in raw_views]
        if family == "clean":
            return values
        if not 0 <= modality < len(values):
            raise ValueError("corruption modality index is out of range")
        rng = np.random.default_rng(int(seed))
        target = values[modality]
        if family == "modality_missing":
            if float(severity) != 1.0:
                raise ValueError("modality missing severity must equal 1")
            target.fill(0.0)
        elif family == "field_missing":
            target[rng.random(target.shape) < float(severity)] = 0.0
        elif family == "row_missing":
            target[rng.random(len(target)) < float(severity)] = 0.0
        elif family == "feature_shuffle":
            selected = np.flatnonzero(
                rng.random(len(target)) < float(severity)
            )
            if len(selected) > 1:
                target[selected] = target[rng.permutation(selected)]
        elif family == "gaussian_drift":
            target += (
                rng.normal(0.0, float(severity), size=target.shape)
                * self.training_feature_scales[modality]
            )
        else:
            raise ValueError(f"unsupported MDR corruption: {family}")
        if not np.isfinite(target).all():
            raise ValueError("MDR corruption produced non-finite values")
        return values

    def evidence(self) -> Dict[str, Any]:
        return {
            "schema_version": "strict_v4_mdr_caeos_runtime_v1",
            "algorithm": "mdr_caeos_v1",
            "augmentation_weight": float(self.augmentation_weight),
            "training_seed": int(self.training_seed),
            "augmentation_seed": int(self.augmentation_seed),
            "clean_threshold": float(self.clean_threshold),
            "modality_count": int(len(self.training_feature_scales)),
            "health_calibration": self.health_calibration.evidence(),
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
            "contains_test_ground_truth": False,
        }

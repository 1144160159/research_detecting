from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

from caeos.csr_exact_replay_runtime import CSRExactReplayRuntime
from caeos.csr_runtime import CSRRuntime


@dataclass
class KRCCSRRuntime:
    """Known-only reliability-certified CSR with exact Pairwise fallback."""

    base_runtime: CSRRuntime
    routing_enabled: bool
    calibration_known_macro_f1: float
    calibration_error_detection_auroc: Optional[float]
    macro_f1_minimum: float = 0.9
    error_auroc_minimum: float = 0.7

    @property
    def clean_threshold(self) -> float:
        return float(self.base_runtime.clean_threshold)

    def predict(self, raw_views: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
        result = dict(CSRExactReplayRuntime(self.base_runtime).predict(raw_views))
        clean_probability = np.asarray(result["clean_probability"])
        result["clean_prediction"] = clean_probability.argmax(axis=1).astype(
            np.int64
        )
        if not self.routing_enabled:
            count = len(result["clean_risk"])
            result["prediction"] = result["clean_prediction"].copy()
            result["probability"] = clean_probability.copy()
            result["risk"] = np.asarray(result["clean_risk"]).copy()
            result["active"] = np.zeros(count, dtype=bool)
            result["conflict_active"] = np.zeros(count, dtype=bool)
            result["disagreement_active"] = np.zeros(count, dtype=bool)
        return result

    def corrupt(
        self,
        raw_views: Sequence[np.ndarray],
        *,
        family: str,
        modality: int,
        severity: float,
        seed: int,
    ) -> list[np.ndarray]:
        return self.base_runtime.corrupt(
            raw_views,
            family=family,
            modality=modality,
            severity=severity,
            seed=seed,
        )

    def evidence(self) -> Dict[str, Any]:
        base = dict(self.base_runtime.evidence())
        base.update(
            {
                "schema_version": "strict_v4_krc_csr_runtime_v1",
                "algorithm": "krc_csr_caeos_v1",
                "runtime_revision": "known_only_reliability_certificate_v1",
                "routing_enabled": bool(self.routing_enabled),
                "known_only_certificate": {
                    "calibration_known_macro_f1": float(
                        self.calibration_known_macro_f1
                    ),
                    "calibration_error_detection_auroc": (
                        None
                        if self.calibration_error_detection_auroc is None
                        else float(self.calibration_error_detection_auroc)
                    ),
                    "calibration_known_macro_f1_minimum": float(
                        self.macro_f1_minimum
                    ),
                    "calibration_error_detection_auroc_minimum": float(
                        self.error_auroc_minimum
                    ),
                    "unknown_or_test_labels_used": False,
                },
                "disabled_behavior": (
                    "exact_pairwise_prediction_probability_risk"
                ),
                "contains_test_ground_truth": False,
            }
        )
        return base

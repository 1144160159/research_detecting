from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Sequence, Tuple

import numpy as np

from caeos.csr_exact_replay_runtime import CSRExactReplayRuntime
from caeos.csr_runtime import CSRRuntime


@dataclass
class RRCCSRRuntime:
    """Scenario-pooled reliability-certified CSR with exact fallback."""

    base_runtime: CSRRuntime
    routing_enabled: bool
    scenario_identity: str
    scenario_certificate_manifest_sha256: str
    training_seed: int
    certified_training_seeds: Tuple[int, ...]
    seed_error_detection_auroc: float
    seed_safety_active_rate_upper_95pct: float
    scenario_mean_error_detection_auroc: float
    scenario_minimum_error_detection_auroc: float
    all_seed_safety_checks_pass: bool
    scenario_mean_auroc_minimum: float = 0.7
    per_seed_auroc_minimum: float = 0.68
    safety_active_rate_upper_maximum: float = 0.01

    def __post_init__(self) -> None:
        seeds = tuple(sorted(int(seed) for seed in self.certified_training_seeds))
        if (
            not self.scenario_identity
            or len(self.scenario_certificate_manifest_sha256) != 64
            or int(self.training_seed) not in seeds
            or len(seeds) != 3
            or len(set(seeds)) != 3
        ):
            raise ValueError("valid three-seed scenario certificate required")
        expected = bool(
            float(self.scenario_mean_error_detection_auroc)
            >= float(self.scenario_mean_auroc_minimum)
            and float(self.scenario_minimum_error_detection_auroc)
            >= float(self.per_seed_auroc_minimum)
            and bool(self.all_seed_safety_checks_pass)
        )
        if bool(self.routing_enabled) != expected:
            raise ValueError("runtime routing disagrees with scenario certificate")
        if (
            float(self.seed_safety_active_rate_upper_95pct)
            > float(self.safety_active_rate_upper_maximum)
            and self.routing_enabled
        ):
            raise ValueError("enabled runtime violates per-seed safety bound")

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
                "schema_version": "strict_v4_rrc_csr_runtime_v1",
                "algorithm": "rrc_csr_caeos_v1",
                "runtime_revision": (
                    "scenario_pooled_relative_reliability_certificate_v1"
                ),
                "routing_enabled": bool(self.routing_enabled),
                "scenario_certificate": {
                    "scenario_identity": self.scenario_identity,
                    "manifest_sha256": (
                        self.scenario_certificate_manifest_sha256
                    ),
                    "training_seed": int(self.training_seed),
                    "certified_training_seeds": [
                        int(seed) for seed in self.certified_training_seeds
                    ],
                    "seed_error_detection_auroc": float(
                        self.seed_error_detection_auroc
                    ),
                    "seed_safety_active_rate_upper_95pct": float(
                        self.seed_safety_active_rate_upper_95pct
                    ),
                    "scenario_mean_error_detection_auroc": float(
                        self.scenario_mean_error_detection_auroc
                    ),
                    "scenario_minimum_error_detection_auroc": float(
                        self.scenario_minimum_error_detection_auroc
                    ),
                    "all_seed_safety_checks_pass": bool(
                        self.all_seed_safety_checks_pass
                    ),
                    "scenario_mean_auroc_minimum": float(
                        self.scenario_mean_auroc_minimum
                    ),
                    "per_seed_auroc_minimum": float(
                        self.per_seed_auroc_minimum
                    ),
                    "safety_active_rate_upper_maximum": float(
                        self.safety_active_rate_upper_maximum
                    ),
                    "absolute_known_macro_f1_threshold": None,
                    "unknown_or_test_labels_used": False,
                },
                "prediction_probability_source": "clean_pairwise_exact",
                "risk_policy": (
                    "active_monotone_uplift_otherwise_clean_exact"
                ),
                "disabled_behavior": (
                    "exact_pairwise_prediction_probability_risk"
                ),
                "contains_test_ground_truth": False,
            }
        )
        return base

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Sequence

import numpy as np

from caeos.csr_runtime import CSRRuntime


@dataclass
class CSRExactReplayRuntime:
    """Effect-invariant CSR wrapper with bit-exact clean probability reuse."""

    base_runtime: CSRRuntime

    @property
    def clean_threshold(self) -> float:
        return float(self.base_runtime.clean_threshold)

    def predict(self, raw_views: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
        result = dict(self.base_runtime.predict(raw_views))
        clean_probability = np.asarray(result["clean_probability"])
        result["probability"] = clean_probability.copy()
        result["prediction"] = clean_probability.argmax(axis=1).astype(np.int64)
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
        value = dict(self.base_runtime.evidence())
        value.update(
            {
                "schema_version": (
                    "strict_v4_csr_caeos_exact_replay_runtime_v2"
                ),
                "algorithm": "csr_caeos_v1",
                "runtime_revision": "exact_clean_probability_replay_v2",
                "prediction_probability_source": (
                    "single_clean_pairwise_forward_exact"
                ),
                "technical_repair": {
                    "changes_prediction": False,
                    "changes_probability_beyond_clean_reuse": False,
                    "changes_risk": False,
                    "changes_active_mask": False,
                    "changes_threshold": False,
                    "reads_effect_metrics": False,
                    "reads_test_labels": False,
                },
            }
        )
        return value

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from caeos.pairwise_runtime import SUPPORTED_RISKS
from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME


SUPPORTED_ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)


def infer_runtime_algorithm(runtime: Any) -> str:
    if not callable(getattr(runtime, "predict", None)):
        raise ValueError("selected-system runtime requires predict")
    evidence_method = getattr(runtime, "evidence", None)
    if not callable(evidence_method):
        raise ValueError("selected-system runtime requires evidence")
    evidence = evidence_method()
    if not isinstance(evidence, dict):
        raise ValueError("runtime evidence must be a dictionary")
    schema = evidence.get("schema_version")
    if schema == "strict_v4_pairwise_runtime_v2":
        selected_risk = evidence.get("selected_risk")
        if selected_risk not in SUPPORTED_RISKS:
            raise ValueError("unsupported Pairwise-family selected risk")
        return "caeos_pug" if selected_risk == PUG_RISK_NAME else "caeos_pairwise"
    if schema == "strict_v4_krc_csr_runtime_v1":
        if evidence.get("algorithm") != "krc_csr_caeos_v1":
            raise ValueError("KRC runtime algorithm evidence is inconsistent")
        return "krc_csr_caeos_v1"
    if schema == "strict_v4_rrc_csr_runtime_v1":
        if evidence.get("algorithm") != "rrc_csr_caeos_v1":
            raise ValueError("RRC runtime algorithm evidence is inconsistent")
        return "rrc_csr_caeos_v1"
    raise ValueError(f"unsupported selected-system runtime schema: {schema}")


def validate_prediction_output(output: Any) -> dict[str, np.ndarray]:
    if not isinstance(output, dict):
        raise ValueError("runtime prediction output must be a dictionary")
    required = {"prediction", "probability", "risk"}
    if not required.issubset(output):
        raise ValueError("runtime prediction output is incomplete")
    prediction = np.asarray(output["prediction"])
    probability = np.asarray(output["probability"], dtype=np.float64)
    risk = np.asarray(output["risk"], dtype=np.float64)
    if (
        prediction.ndim != 1
        or probability.ndim != 2
        or risk.ndim != 1
        or len(prediction) != len(probability)
        or len(prediction) != len(risk)
        or not len(prediction)
    ):
        raise ValueError("runtime prediction arrays are not aligned")
    if not np.issubdtype(prediction.dtype, np.integer):
        raise ValueError("runtime prediction must use integer labels")
    if (
        not np.isfinite(probability).all()
        or not np.isfinite(risk).all()
        or (probability < 0.0).any()
        or (probability > 1.0).any()
        or (risk < 0.0).any()
        or (risk > 1.0).any()
    ):
        raise ValueError("runtime probabilities and risks must be finite in [0, 1]")
    if not np.allclose(probability.sum(axis=1), 1.0, atol=1e-8, rtol=0.0):
        raise ValueError("runtime probabilities must sum to one")
    if not np.array_equal(prediction, probability.argmax(axis=1)):
        raise ValueError("runtime prediction disagrees with probability argmax")
    return {
        **output,
        "prediction": prediction.astype(np.int64, copy=False),
        "probability": probability,
        "risk": risk,
    }


@dataclass
class SelectedSystemRuntime:
    runtime: Any
    selected_algorithm: str
    known_validation_threshold: float

    def __post_init__(self) -> None:
        if self.selected_algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError("unsupported selected-system algorithm")
        inferred = infer_runtime_algorithm(self.runtime)
        if inferred != self.selected_algorithm:
            raise ValueError(
                "selected algorithm disagrees with runtime evidence"
            )
        threshold = float(self.known_validation_threshold)
        if not np.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
            raise ValueError("known-validation threshold must be in [0, 1]")
        self.known_validation_threshold = threshold
        evidence = self.runtime.evidence()
        if evidence.get("contains_test_ground_truth") is not False:
            raise ValueError("runtime must explicitly exclude test ground truth")
        if evidence.get("contains_training_or_test_labels") not in (
            None,
            False,
        ):
            raise ValueError("runtime evidence contains forbidden labels")

    def predict(
        self, raw_views: Sequence[np.ndarray]
    ) -> dict[str, np.ndarray]:
        return validate_prediction_output(self.runtime.predict(raw_views))

    def evidence(self) -> dict[str, Any]:
        source = self.runtime.evidence()
        return {
            "schema_version": "strict_v4_selected_system_runtime_v1",
            "selected_algorithm": self.selected_algorithm,
            "known_validation_threshold": self.known_validation_threshold,
            "threshold_source": "known_validation_only",
            "source_runtime_schema": source["schema_version"],
            "source_runtime_algorithm": infer_runtime_algorithm(self.runtime),
            "predict_contract": [
                "prediction",
                "probability",
                "risk",
            ],
            "unknown_or_test_labels_used_for_fit_selection_or_threshold": (
                False
            ),
            "contains_test_ground_truth": False,
        }

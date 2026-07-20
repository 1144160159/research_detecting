from __future__ import annotations

from typing import Any

import numpy as np

from caeos.logit_posthoc import softmax_probabilities


def gradnorm_confidence(embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
    features = np.asarray(embeddings, dtype=np.float64)
    values = np.asarray(logits, dtype=np.float64)
    if features.ndim != 2 or values.ndim != 2 or len(features) != len(values):
        raise ValueError("GradNorm embeddings and logits must be aligned matrices")
    if len(features) == 0 or features.shape[1] == 0 or values.shape[1] < 2:
        raise ValueError("GradNorm inputs must be non-empty")
    if not np.isfinite(features).all():
        raise ValueError("GradNorm embeddings must be finite")
    probability = softmax_probabilities(values)
    class_count = probability.shape[1]
    output_gradient_l1 = np.abs(class_count * probability - 1.0).sum(axis=1)
    feature_l1 = np.abs(features).sum(axis=1)
    confidence = feature_l1 * output_gradient_l1
    if not np.isfinite(confidence).all():
        raise FloatingPointError("GradNorm produced non-finite confidence")
    return confidence


def gradnorm_risk(embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
    return -gradnorm_confidence(embeddings, logits)


def evidence() -> dict[str, Any]:
    return {
        "method": "GradNorm",
        "benchmark": "OpenOOD v1.5",
        "official_code": (
            "https://github.com/Jingkang50/OpenOOD/blob/main/openood/"
            "postprocessors/gradnorm_postprocessor.py"
        ),
        "protocol_class": "official_last_layer_gradient_formula_frozen_mlp_adapter",
        "target": "all-ones vector over known classes",
        "confidence": "L1 norm of final linear-layer weight gradient",
        "analytic_equivalent": (
            "sum(abs(embedding)) * sum(abs(C * softmax(logits) - 1))"
        ),
        "risk_orientation": "negative confidence; higher means more OOD-like",
        "fit_split": "none",
        "unknown_or_test_labels_used": False,
    }

from __future__ import annotations

from typing import Any

import numpy as np


def softmax_probabilities(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] < 2:
        raise ValueError("logits must be a non-empty matrix with at least two classes")
    if not np.isfinite(values).all():
        raise ValueError("logits must be finite")
    shifted = values - values.max(axis=1, keepdims=True)
    exponentiated = np.exp(shifted)
    return exponentiated / exponentiated.sum(axis=1, keepdims=True)


def shannon_entropy_risk(logits: np.ndarray) -> np.ndarray:
    probability = softmax_probabilities(logits)
    terms = np.zeros_like(probability)
    positive = probability > 0.0
    terms[positive] = probability[positive] * np.log(probability[positive])
    return -terms.sum(axis=1)


def generalized_entropy_risk(
    logits: np.ndarray, gamma: float = 0.1, top_m: int = 100
) -> np.ndarray:
    if gamma <= 0.0:
        raise ValueError("GEN gamma must be positive")
    if top_m <= 0:
        raise ValueError("GEN top_m must be positive")
    probability = softmax_probabilities(logits)
    retained = min(int(top_m), probability.shape[1])
    top = np.sort(probability, axis=1)[:, -retained:]
    return np.sum(
        np.power(top, float(gamma)) * np.power(1.0 - top, float(gamma)), axis=1
    )


def evidence(gamma: float = 0.1, top_m: int = 100) -> dict[str, Any]:
    return {
        "gen": {
            "method": "GEN",
            "paper": "https://openaccess.thecvf.com/content/CVPR2023/html/Liu_GEN_Pushing_the_Limits_of_Softmax-Based_Out-of-Distribution_Detection_CVPR_2023_paper.html",
            "official_code": "https://github.com/XixiLiu95/GEN",
            "protocol_class": "official_formula_frozen_softmax_adapter",
            "gamma": float(gamma),
            "gamma_source": "official_default_0.1",
            "top_m": int(top_m),
            "effective_top_m": "min(top_m, number_of_known_classes)",
            "fit_split": "none",
            "unknown_or_test_labels_used": False,
        },
        "shannon_entropy": {
            "method": "Shannon entropy",
            "protocol_class": "standard_frozen_softmax_diagnostic",
            "fit_split": "none",
            "unknown_or_test_labels_used": False,
        },
    }

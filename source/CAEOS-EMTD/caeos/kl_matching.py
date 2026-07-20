from __future__ import annotations

from typing import Any

import numpy as np

from caeos.logit_posthoc import softmax_probabilities


def fit_kl_matching_templates(validation_logits: np.ndarray) -> np.ndarray:
    probability = softmax_probabilities(validation_logits)
    predicted = probability.argmax(axis=1)
    class_count = probability.shape[1]
    templates = []
    for class_index in range(class_count):
        selected = probability[predicted == class_index]
        if len(selected):
            templates.append(selected.mean(axis=0))
        else:
            fallback = np.zeros(class_count, dtype=np.float64)
            fallback[class_index] = 1.0
            templates.append(fallback)
    return np.asarray(templates, dtype=np.float64)


def kl_matching_risk(
    logits: np.ndarray, templates: np.ndarray, epsilon: float = 1e-12
) -> np.ndarray:
    if epsilon <= 0.0:
        raise ValueError("KLM epsilon must be positive")
    probability = softmax_probabilities(logits)
    reference = np.asarray(templates, dtype=np.float64)
    if reference.shape != (probability.shape[1], probability.shape[1]):
        raise ValueError("KLM templates must be a square class-by-class matrix")
    if not np.isfinite(reference).all() or np.any(reference < 0.0):
        raise ValueError("KLM templates must be finite and nonnegative")
    sums = reference.sum(axis=1, keepdims=True)
    if np.any(sums <= 0.0):
        raise ValueError("every KLM template must have positive mass")
    reference = reference / sums
    p = np.clip(probability, epsilon, 1.0)
    q = np.clip(reference, epsilon, 1.0)
    divergence = np.sum(
        p[:, None, :] * (np.log(p[:, None, :]) - np.log(q[None, :, :])),
        axis=2,
    )
    risk = divergence.min(axis=1)
    if not np.isfinite(risk).all():
        raise FloatingPointError("KLM produced non-finite risks")
    return risk


def evidence(epsilon: float = 1e-12) -> dict[str, Any]:
    return {
        "method": "KL Matching (KLM)",
        "benchmark": "OpenOOD v1.5",
        "official_code": (
            "https://github.com/Jingkang50/OpenOOD/blob/main/openood/"
            "postprocessors/kl_matching_postprocessor.py"
        ),
        "protocol_class": "official_formula_frozen_softmax_adapter",
        "template_split": "known_only_validation",
        "template_grouping": "validation softmax grouped by predicted class",
        "score": "minimum KL(test_softmax || predicted_class_mean_softmax)",
        "risk_orientation": "positive KL distance; higher means more OOD-like",
        "missing_predicted_class_fallback": "one-hot template as in official code",
        "numeric_epsilon": float(epsilon),
        "unknown_or_test_labels_used": False,
    }

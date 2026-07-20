from __future__ import annotations

import numpy as np
from scipy.special import logsumexp


OFFICIAL_PERCENTILE = 90.0
PAPER_URL = "https://arxiv.org/abs/2209.09858"
OFFICIAL_CODE_URL = "https://github.com/andrijazz/ash/blob/main/ash.py"


def _validate(activations: np.ndarray, percentile: float) -> np.ndarray:
    values = np.asarray(activations, dtype=np.float64)
    if values.ndim != 2 or not values.shape[0] or not values.shape[1]:
        raise ValueError("ASH activations must be a non-empty matrix")
    if not np.isfinite(values).all():
        raise ValueError("ASH activations must be finite")
    if not np.isfinite(percentile) or not 0.0 <= percentile < 100.0:
        raise ValueError("ASH percentile must be finite and in [0, 100)")
    return np.maximum(values, 0.0)


def ash_s_activations(
    activations: np.ndarray, percentile: float = OFFICIAL_PERCENTILE
) -> np.ndarray:
    """Apply the official ASH-S pruning and exponential sharpening formula."""

    values = _validate(activations, percentile)
    feature_count = values.shape[1]
    keep = max(1, feature_count - int(np.round(feature_count * percentile / 100.0)))
    indices = np.argpartition(values, feature_count - keep, axis=1)[:, -keep:]
    retained = np.take_along_axis(values, indices, axis=1)
    shaped = np.zeros_like(values)
    np.put_along_axis(shaped, indices, retained, axis=1)
    original_sum = values.sum(axis=1)
    retained_sum = shaped.sum(axis=1)
    ratio = np.zeros(len(values), dtype=np.float64)
    positive = retained_sum > 0.0
    ratio[positive] = original_sum[positive] / retained_sum[positive]
    if np.any(ratio > np.log(np.finfo(np.float64).max)):
        raise OverflowError("ASH exponential sharpening exceeds float64 range")
    return shaped * np.exp(ratio)[:, None]


def ash_s_logits(
    activations: np.ndarray,
    classifier_weight: np.ndarray,
    classifier_bias: np.ndarray,
    percentile: float = OFFICIAL_PERCENTILE,
) -> np.ndarray:
    shaped = ash_s_activations(activations, percentile)
    weight = np.asarray(classifier_weight, dtype=np.float64)
    bias = np.asarray(classifier_bias, dtype=np.float64).reshape(-1)
    if weight.ndim != 2 or weight.shape[1] != shaped.shape[1]:
        raise ValueError("ASH classifier weight has an incompatible shape")
    if bias.shape != (weight.shape[0],):
        raise ValueError("ASH classifier bias has an incompatible shape")
    return shaped @ weight.T + bias


def ash_s_risk(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("ASH temperature must be finite and positive")
    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError("ASH logits must be a finite matrix")
    return -float(temperature) * logsumexp(values / temperature, axis=1)


def evidence(percentile: float = OFFICIAL_PERCENTILE) -> dict[str, object]:
    _validate(np.ones((1, 1)), percentile)
    return {
        "method": "ASH-S",
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "protocol_class": "official_formula_frozen_penultimate_mlp_adapter",
        "percentile": float(percentile),
        "percentile_source": "paper_main_penultimate_setting_frozen_before_results",
        "formula": "keep_top_k_then_multiply_retained_by_exp(sum_before/sum_after)",
        "score": "negative_energy_larger_is_more_unknown",
        "fit_split": "none",
        "auxiliary_ood_used": False,
        "unknown_or_test_labels_used": False,
        "adaptation": {
            "placement": "frozen_mlp_penultimate_embedding",
            "gelu_negative_policy": "relu_clamp_before_official_nonnegative_formula",
            "minimum_kept_features": 1,
        },
    }

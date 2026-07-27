from __future__ import annotations

from typing import Any

import numpy as np
from scipy.special import logsumexp


PAPER_URL = (
    "https://openaccess.thecvf.com/content/ICCV2025/html/"
    "Gu_Gradient_Short-Circuit_Efficient_Out-of-Distribution_"
    "Detection_via_Feature_Intervention_ICCV_2025_paper.html"
)


def masked_coordinate_count(feature_dim: int, mask_ratio: float = 0.05) -> int:
    if feature_dim <= 0:
        raise ValueError("feature_dim must be positive")
    if not 0.0 < float(mask_ratio) <= 1.0:
        raise ValueError("mask_ratio must be in (0, 1]")
    return max(1, int(feature_dim * float(mask_ratio)))


def gradient_short_circuit_logits(
    embeddings: np.ndarray,
    logits: np.ndarray,
    classifier_weight: np.ndarray,
    mask_ratio: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply ICCV 2025 GSC zeroing with the paper's first-order logit update."""
    features = np.asarray(embeddings, dtype=np.float64)
    values = np.asarray(logits, dtype=np.float64)
    weight = np.asarray(classifier_weight, dtype=np.float64)
    if features.ndim != 2 or values.ndim != 2 or weight.ndim != 2:
        raise ValueError("GSC embeddings, logits, and classifier weight must be matrices")
    if len(features) == 0 or len(features) != len(values):
        raise ValueError("GSC embeddings and logits must be non-empty and aligned")
    if weight.shape != (values.shape[1], features.shape[1]):
        raise ValueError("GSC classifier weight shape does not match logits/features")
    if values.shape[1] < 2:
        raise ValueError("GSC requires at least two known classes")
    if not all(np.isfinite(item).all() for item in (features, values, weight)):
        raise ValueError("GSC inputs must be finite")

    predicted = values.argmax(axis=1)
    gradient = weight[predicted]
    count = masked_coordinate_count(features.shape[1], mask_ratio)
    selected = np.argsort(-np.abs(gradient), axis=1, kind="mergesort")[:, :count]
    delta = np.zeros_like(features)
    rows = np.arange(len(features))[:, None]
    delta[rows, selected] = -features[rows, selected]
    corrected = values + delta @ weight.T
    if not np.isfinite(corrected).all():
        raise FloatingPointError("GSC produced non-finite corrected logits")
    return corrected, selected


def gsc_risk(
    embeddings: np.ndarray,
    logits: np.ndarray,
    classifier_weight: np.ndarray,
    mask_ratio: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    corrected, selected = gradient_short_circuit_logits(
        embeddings, logits, classifier_weight, mask_ratio
    )
    return -logsumexp(corrected, axis=1), selected


def mask_diagnostics(selected: np.ndarray, predicted: np.ndarray) -> dict[str, Any]:
    indices = np.asarray(selected, dtype=np.int64)
    labels = np.asarray(predicted, dtype=np.int64)
    if indices.ndim != 2 or labels.ndim != 1 or len(indices) != len(labels):
        raise ValueError("GSC mask diagnostics require aligned masks and predictions")
    masks = [tuple(sorted(map(int, row))) for row in indices]
    class_masks: dict[int, set[tuple[int, ...]]] = {}
    for label, mask in zip(labels, masks):
        class_masks.setdefault(int(label), set()).add(mask)
    per_class_fixed = all(len(items) == 1 for items in class_masks.values())
    return {
        "sample_count": int(len(indices)),
        "masked_coordinates_per_sample": int(indices.shape[1]),
        "unique_mask_count": int(len(set(masks))),
        "predicted_class_count": int(len(class_masks)),
        "mask_is_fixed_within_predicted_class": bool(per_class_fixed),
        "linear_head_degeneracy_observed": bool(per_class_fixed),
    }


def evidence(mask_ratio: float = 0.05) -> dict[str, Any]:
    return {
        "method": "Gradient Short-Circuit",
        "paper": PAPER_URL,
        "venue": "ICCV 2025",
        "protocol_class": "paper_formula_penultimate_feature_linear_head_adapter",
        "split_layer": "penultimate_embedding_before_frozen_linear_classifier",
        "gradient": "predicted_class_logit_gradient_with_respect_to_embedding",
        "intervention": "zero_top_absolute_gradient_coordinates",
        "mask_ratio": float(mask_ratio),
        "masked_coordinate_rounding": "max(1, floor(feature_dim * mask_ratio))",
        "gradient_tie_policy": "stable_feature_index_order",
        "logit_update": "y_prime = y + Jacobian(y,F) @ (F_prime - F)",
        "score": "negative_logsumexp_of_first_order_corrected_logits",
        "linear_head_note": (
            "first_order_update_is_exact_and_mask_is_fixed_within_predicted_class"
        ),
        "fit_split": "none",
        "threshold_split": "known_only_validation",
        "unknown_or_test_labels_used": False,
    }

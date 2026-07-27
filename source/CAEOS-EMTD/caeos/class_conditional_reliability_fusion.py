from __future__ import annotations

import numpy as np

from caeos.hybrid import normalized_entropy, pairwise_js_conflict, temperature_scale


def fit_class_conditional_reliability(
    validation_view_probability: np.ndarray,
    validation_labels: np.ndarray,
    shrinkage: float = 20.0,
    minimum_reliability: float = 0.05,
) -> dict[str, np.ndarray]:
    """Estimate P(correct | view, predicted class) from known validation data."""
    probability = np.asarray(validation_view_probability, dtype=np.float64)
    labels = np.asarray(validation_labels, dtype=np.int64)
    if probability.ndim != 3 or len(probability) != len(labels):
        raise ValueError("validation probabilities must have shape [samples, views, classes]")
    if not np.isfinite(probability).all() or not np.isfinite(labels).all():
        raise ValueError("validation inputs must be finite")
    if shrinkage < 0.0 or not 0.0 < minimum_reliability <= 1.0:
        raise ValueError("invalid reliability regularization")
    samples, views, classes = probability.shape
    if samples == 0 or np.any(labels < 0) or np.any(labels >= classes):
        raise ValueError("validation labels are outside the probability class range")

    prediction = probability.argmax(axis=2)
    base = np.mean(prediction == labels[:, None], axis=0)
    reliability = np.empty((views, classes), dtype=np.float64)
    support = np.zeros((views, classes), dtype=np.int64)
    correct = np.zeros((views, classes), dtype=np.int64)
    for view in range(views):
        for class_index in range(classes):
            mask = prediction[:, view] == class_index
            support[view, class_index] = int(mask.sum())
            correct[view, class_index] = int(
                np.sum(mask & (labels == class_index))
            )
            reliability[view, class_index] = (
                correct[view, class_index] + shrinkage * base[view]
            ) / (support[view, class_index] + shrinkage)
    reliability = np.clip(reliability, minimum_reliability, 1.0)
    return {
        "reliability": reliability,
        "support": support,
        "correct": correct,
        "base_reliability": base,
    }


def fuse_with_class_conditional_reliability(
    view_probability: np.ndarray,
    class_reliability: np.ndarray,
) -> dict[str, np.ndarray]:
    probability = np.asarray(view_probability, dtype=np.float64)
    reliability = np.asarray(class_reliability, dtype=np.float64)
    if probability.ndim != 3 or reliability.shape != probability.shape[1:]:
        raise ValueError("class reliability must have shape [views, classes]")
    if not np.isfinite(probability).all() or not np.isfinite(reliability).all():
        raise ValueError("fusion inputs must be finite")
    probability = np.clip(probability, 1e-12, None)
    probability /= probability.sum(axis=2, keepdims=True)
    confidence = 1.0 - normalized_entropy(probability)
    expected_reliability = np.einsum("nvc,vc->nv", probability, reliability)
    weight = np.clip(
        expected_reliability * (0.25 + 0.75 * confidence), 1e-6, 1.0
    )
    fused = (weight[:, :, None] * probability).sum(axis=1)
    fused /= weight.sum(axis=1, keepdims=True)
    _, global_conflict = pairwise_js_conflict(probability, weight)
    sample_reliability = np.sum(weight * expected_reliability, axis=1) / np.sum(
        weight, axis=1
    )
    return {
        "fused_probability": fused,
        "expected_reliability": expected_reliability,
        "view_weight": weight,
        "global_conflict": global_conflict,
        "sample_reliability": np.clip(sample_reliability, 0.0, 1.0),
    }


def recover_temperature(
    pre_temperature_probability: np.ndarray,
    observed_probability: np.ndarray,
) -> tuple[float, float]:
    pre = np.asarray(pre_temperature_probability, dtype=np.float64)
    observed = np.asarray(observed_probability, dtype=np.float64)
    if pre.shape != observed.shape or pre.ndim != 2:
        raise ValueError("temperature recovery arrays must be aligned matrices")
    best = (float("inf"), 1.0)
    for temperature in np.linspace(0.5, 2.0, 61):
        error = float(np.max(np.abs(temperature_scale(pre, temperature) - observed)))
        candidate = (error, abs(float(temperature) - 1.0), float(temperature))
        incumbent = (best[0], abs(best[1] - 1.0), best[1])
        if candidate < incumbent:
            best = (error, float(temperature))
    return best[1], best[0]


def reliability_fused_candidate(
    *,
    view_probability: np.ndarray,
    class_reliability: np.ndarray,
    global_probability: np.ndarray,
    incumbent_view_fused_probability: np.ndarray,
    incumbent_gate: np.ndarray,
    incumbent_final_probability: np.ndarray,
    incumbent_risk: np.ndarray,
    risk_blend: float = 0.25,
) -> dict[str, np.ndarray | float]:
    if not 0.0 <= risk_blend <= 1.0:
        raise ValueError("risk_blend must be in [0, 1]")
    fusion = fuse_with_class_conditional_reliability(
        view_probability, class_reliability
    )
    gate = np.asarray(incumbent_gate, dtype=np.float64).reshape(-1)
    global_probability = np.asarray(global_probability, dtype=np.float64)
    old_fused = np.asarray(incumbent_view_fused_probability, dtype=np.float64)
    old_final = np.asarray(incumbent_final_probability, dtype=np.float64)
    risk = np.asarray(incumbent_risk, dtype=np.float64).reshape(-1)
    if not (
        len(gate)
        == len(global_probability)
        == len(old_fused)
        == len(old_final)
        == len(risk)
    ):
        raise ValueError("candidate inputs are not sample-aligned")
    old_pre = (1.0 - gate[:, None]) * global_probability + gate[:, None] * old_fused
    temperature, reconstruction_error = recover_temperature(old_pre, old_final)
    new_pre = (
        (1.0 - gate[:, None]) * global_probability
        + gate[:, None] * fusion["fused_probability"]
    )
    candidate_probability = temperature_scale(new_pre, temperature)
    evidence_risk = 1.0 - (
        candidate_probability.max(axis=1) * fusion["sample_reliability"]
    )
    candidate_risk = np.clip(
        (1.0 - risk_blend) * risk + risk_blend * evidence_risk, 0.0, 1.0
    )
    return {
        **fusion,
        "temperature": float(temperature),
        "temperature_reconstruction_max_abs_error": float(reconstruction_error),
        "candidate_probability": candidate_probability,
        "evidence_risk": evidence_risk,
        "candidate_risk": candidate_risk,
    }

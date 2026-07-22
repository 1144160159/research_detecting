from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.linalg import eigh
from scipy.special import softmax


PAPER_URL = "https://openreview.net/forum?id=GEtOzC4MIi"
ICLR_URL = "https://iclr.cc/virtual/2026/poster/10010515"


@dataclass(frozen=True)
class FisherRaoState:
    feature_basis: np.ndarray
    probability_basis: np.ndarray
    lambda_magnitude: float
    lambda_residual: float
    train_sample_count: int
    class_count: int


def _matrix(value: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or len(result) == 0 or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a non-empty finite matrix")
    return result


def _orthonormal_lda_basis(features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    classes = np.unique(labels)
    if len(classes) < 2:
        raise ValueError("Fisher-Rao LDA requires at least two known classes")
    dimension = features.shape[1]
    global_mean = features.mean(axis=0)
    within = np.zeros((dimension, dimension), dtype=np.float64)
    between = np.zeros_like(within)
    for label in classes:
        items = features[labels == label]
        if len(items) < 2:
            raise ValueError(f"Fisher-Rao LDA class {label} has fewer than two samples")
        centered = items - items.mean(axis=0)
        within += centered.T @ centered
        delta = items.mean(axis=0) - global_mean
        between += len(items) * np.outer(delta, delta)
    scale = max(float(np.trace(within)) / max(dimension, 1), 1.0)
    values, vectors = eigh(between, within + 1e-6 * scale * np.eye(dimension))
    order = np.argsort(values)[::-1]
    tolerance = max(float(np.max(np.abs(values))), 1.0) * 1e-10
    keep = order[values[order] > tolerance][: min(len(classes) - 1, dimension)]
    if len(keep) == 0:
        raise FloatingPointError("Fisher-Rao LDA found no discriminative direction")
    basis, _ = np.linalg.qr(vectors[:, keep], mode="reduced")
    return basis


def _pca_basis(probabilities: np.ndarray) -> np.ndarray:
    centered = probabilities - probabilities.mean(axis=0)
    _, singular, right = np.linalg.svd(centered, full_matrices=False)
    tolerance = max(float(singular[0]), 1.0) * max(centered.shape) * np.finfo(float).eps
    rank = min(int(np.count_nonzero(singular > tolerance)), probabilities.shape[1] - 1)
    if rank <= 0:
        raise FloatingPointError("Fisher-Rao PCA found no probability direction")
    return right[:rank].T


def _components(
    embeddings: np.ndarray,
    logits: np.ndarray,
    feature_basis: np.ndarray,
    probability_basis: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features = _matrix(embeddings, "embeddings")
    raw_logits = _matrix(logits, "logits")
    if len(features) != len(raw_logits):
        raise ValueError("Fisher-Rao embeddings and logits are misaligned")
    if features.shape[1] != feature_basis.shape[0]:
        raise ValueError("Fisher-Rao feature dimensions differ")
    if raw_logits.shape[1] != probability_basis.shape[0]:
        raise ValueError("Fisher-Rao probability dimensions differ")
    probabilities = softmax(raw_logits, axis=1)
    standard_uncertainty = 1.0 - np.square(probabilities).sum(axis=1)
    row_norm = np.square(probability_basis).sum(axis=1)
    projected_uncertainty = (
        probabilities @ row_norm
        - np.square(probabilities @ probability_basis).sum(axis=1)
    )
    projected = embeddings @ feature_basis
    magnitude = np.square(projected).sum(axis=1)
    residual = np.square(embeddings).sum(axis=1) - magnitude
    residual = np.maximum(residual, 0.0)
    return standard_uncertainty, projected_uncertainty, magnitude, residual


def fit_fisher_rao(
    train_embeddings: np.ndarray,
    train_logits: np.ndarray,
    train_labels: np.ndarray,
) -> FisherRaoState:
    features = _matrix(train_embeddings, "train_embeddings")
    logits = _matrix(train_logits, "train_logits")
    labels = np.asarray(train_labels)
    if labels.ndim != 1 or len(labels) != len(features) or len(logits) != len(features):
        raise ValueError("Fisher-Rao training arrays are misaligned")
    feature_basis = _orthonormal_lda_basis(features, labels)
    probability_basis = _pca_basis(softmax(logits, axis=1))
    _, uncertainty, magnitude, residual = _components(
        features, logits, feature_basis, probability_basis
    )
    variance_u = float(np.var(uncertainty))
    variance_m = float(np.var(magnitude))
    variance_y = float(np.var(residual))
    if min(variance_u, variance_m, variance_y) <= 1e-18:
        raise FloatingPointError("Fisher-Rao variance balancing encountered zero variance")
    return FisherRaoState(
        feature_basis=feature_basis,
        probability_basis=probability_basis,
        lambda_magnitude=float(np.sqrt(variance_u / variance_m)),
        lambda_residual=float(np.sqrt(variance_u / variance_y)),
        train_sample_count=int(len(features)),
        class_count=int(logits.shape[1]),
    )


def fisher_rao_score_batch(
    embeddings: np.ndarray,
    logits: np.ndarray,
    state: FisherRaoState,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    standard_u, tensor_u, magnitude, residual = _components(
        embeddings, logits, state.feature_basis, state.probability_basis
    )
    feature_norm = np.square(embeddings).sum(axis=1)
    risk = {
        "fim_standard": feature_norm * standard_u,
        "fim_tensor": tensor_u * magnitude,
        "fim_additive": (
            tensor_u
            - state.lambda_magnitude * magnitude
            + state.lambda_residual * residual
        ),
    }
    if not all(np.isfinite(value).all() for value in risk.values()):
        raise FloatingPointError("Fisher-Rao produced non-finite scores")
    scores = {name: -value for name, value in risk.items()}
    return scores, {
        "sample_count": int(len(feature_norm)),
        "all_scores_finite": True,
        "score_standard_deviation": {
            name: float(np.std(value)) for name, value in scores.items()
        },
        "minimum_standard_uncertainty": float(np.min(standard_u)),
        "minimum_tensor_uncertainty": float(np.min(tensor_u)),
        "minimum_residual": float(np.min(residual)),
    }


def evidence() -> dict[str, Any]:
    return {
        "family": "Fisher-Rao-FIM-Trace",
        "paper": PAPER_URL,
        "venue": ICLR_URL,
        "standard_formula": "Eq.7 ||f(x)||^2 * (1 - ||p(x)||^2)",
        "tensor_formula": "Eq.9 U(x) * M(x)",
        "additive_formula": "Eq.13 U(x) + lambda_M*M(x) + lambda_y*y(x)",
        "subspaces": "LDA feature basis and PCA softmax basis from known training data",
        "coefficient_policy": "Eq.14-15 ID-only analytic variance balancing",
        "coefficient_signs": "lambda_M negative; lambda_y positive per signal contribution",
        "fit_split": "known_training_embeddings_logits_and_labels_only",
        "threshold_split": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }

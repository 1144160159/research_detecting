from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import logsumexp


PAPER_URL = (
    "https://openaccess.thecvf.com/content/ICCV2025/html/"
    "Zongur_Activation_Subspaces_for_Out-of-Distribution_Detection_"
    "ICCV_2025_paper.html"
)
OFFICIAL_CODE_URL = "https://github.com/visinf/actsub"
OFFICIAL_COMMIT = "5b058e723c814fdfd36ab1b73b18227623faa410"


@dataclass(frozen=True)
class ActSubState:
    decisive_transform: np.ndarray
    insignificant_transform: np.ndarray
    normalized_insignificant_train: np.ndarray
    classifier_weight: np.ndarray
    classifier_bias: np.ndarray
    balance_index: int
    balance_gap: float
    train_sample_count: int


def _finite_matrix(value: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or len(result) == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def _normalized_rows(value: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(value, axis=1, keepdims=True)
    return value / np.maximum(norms, np.finfo(np.float64).eps)


def find_balance_index(
    classifier_weight: np.ndarray, train_embeddings: np.ndarray
) -> tuple[int, float, np.ndarray]:
    """Reproduce ActSub Eq. 4 using known-training embeddings only."""
    weight = _finite_matrix(classifier_weight, "classifier_weight")
    embeddings = _finite_matrix(train_embeddings, "train_embeddings")
    if weight.shape[1] != embeddings.shape[1]:
        raise ValueError("classifier and embedding dimensions differ")
    _, _, right = np.linalg.svd(weight, full_matrices=True)
    coordinates = embeddings @ right.T
    squared = coordinates * coordinates
    cumulative = np.cumsum(squared, axis=1)
    total = cumulative[:, -1]
    gaps = []
    for index in range(embeddings.shape[1]):
        decisive_squared = np.zeros(len(embeddings)) if index == 0 else cumulative[:, index - 1]
        insignificant_squared = np.maximum(total - decisive_squared, 0.0)
        decisive_norm = np.sqrt(np.maximum(decisive_squared, 0.0)).mean()
        insignificant_norm = np.sqrt(insignificant_squared).mean()
        gaps.append(abs(float(decisive_norm - insignificant_norm)))
    balance_index = int(np.argmin(np.asarray(gaps, dtype=np.float64)))
    return balance_index, float(gaps[balance_index]), right


def fit_actsub(
    classifier_weight: np.ndarray,
    classifier_bias: np.ndarray,
    train_embeddings: np.ndarray,
    *,
    neighbors: int = 10,
) -> ActSubState:
    weight = _finite_matrix(classifier_weight, "classifier_weight")
    embeddings = _finite_matrix(train_embeddings, "train_embeddings")
    bias = np.asarray(classifier_bias, dtype=np.float64)
    if bias.ndim != 1 or len(bias) != weight.shape[0] or not np.isfinite(bias).all():
        raise ValueError("classifier_bias must match the classifier rows")
    if neighbors <= 0 or len(embeddings) < neighbors:
        raise ValueError("ActSub requires at least neighbors known-training samples")
    index, gap, right = find_balance_index(weight, embeddings)
    decisive = right.T[:, :index] @ right[:index, :]
    insignificant = right.T[:, index:] @ right[index:, :]
    identity_error = float(
        np.max(np.abs(decisive + insignificant - np.eye(embeddings.shape[1])))
    )
    orthogonality_error = float(np.max(np.abs(decisive @ insignificant)))
    if identity_error > 1e-10 or orthogonality_error > 1e-10:
        raise FloatingPointError("ActSub SVD projectors failed integrity checks")
    insignificant_train = embeddings @ insignificant.T
    return ActSubState(
        decisive_transform=decisive,
        insignificant_transform=insignificant,
        normalized_insignificant_train=_normalized_rows(insignificant_train),
        classifier_weight=weight,
        classifier_bias=bias,
        balance_index=index,
        balance_gap=gap,
        train_sample_count=int(len(embeddings)),
    )


def scale_decisive(
    decisive_embeddings: np.ndarray, percentile: float = 95.0
) -> tuple[np.ndarray, dict[str, float | int]]:
    """Apply the official SCALE operation used by ActSub Eq. 9."""
    values = _finite_matrix(decisive_embeddings, "decisive_embeddings")
    if not 0.0 <= float(percentile) < 100.0:
        raise ValueError("percentile must be in [0, 100)")
    feature_count = values.shape[1]
    retained = feature_count - int(np.round(feature_count * float(percentile) / 100.0))
    if retained <= 0:
        raise ValueError("ActSub SCALE must retain at least one coordinate")
    order = np.argsort(-values, axis=1, kind="mergesort")[:, :retained]
    selected = np.take_along_axis(values, order, axis=1)
    full_sum = values.sum(axis=1)
    selected_sum = selected.sum(axis=1)
    tolerance = np.finfo(np.float64).eps * np.maximum(1.0, np.abs(full_sum))
    if np.any(np.abs(selected_sum) <= tolerance):
        raise FloatingPointError("ActSub SCALE selected-coordinate sum is numerically zero")
    exponent = full_sum / selected_sum
    with np.errstate(over="raise", invalid="raise"):
        try:
            factor = np.exp(exponent)
        except FloatingPointError as error:
            raise FloatingPointError("ActSub SCALE exponent overflow") from error
    shaped = values * factor[:, None]
    if not np.isfinite(shaped).all():
        raise FloatingPointError("ActSub SCALE produced non-finite activations")
    return shaped, {
        "retained_coordinates": int(retained),
        "minimum_absolute_selected_sum": float(np.min(np.abs(selected_sum))),
        "minimum_scale_factor": float(np.min(factor)),
        "maximum_scale_factor": float(np.max(factor)),
    }


def actsub_score_batch(
    embeddings: np.ndarray,
    state: ActSubState,
    *,
    percentile: float = 95.0,
    lmbd: float = 2.0,
    neighbors: int = 10,
) -> tuple[np.ndarray, dict[str, Any]]:
    values = _finite_matrix(embeddings, "embeddings")
    if values.shape[1] != state.classifier_weight.shape[1]:
        raise ValueError("ActSub query and classifier dimensions differ")
    if not np.isfinite(lmbd) or lmbd <= 0.0:
        raise ValueError("ActSub lambda must be finite and positive")
    if neighbors <= 0 or neighbors > state.train_sample_count:
        raise ValueError("invalid ActSub neighbor count")

    decisive = values @ state.decisive_transform.T
    shaped, scale_diagnostics = scale_decisive(decisive, percentile)
    logits = shaped @ state.classifier_weight.T + state.classifier_bias
    decisive_score = logsumexp(logits, axis=1)

    insignificant = _normalized_rows(values @ state.insignificant_transform.T)
    cosine = insignificant @ state.normalized_insignificant_train.T
    nearest = np.partition(cosine, cosine.shape[1] - neighbors, axis=1)[:, -neighbors:]
    mean_cosine = nearest.mean(axis=1)
    bounded_cosine = np.minimum(mean_cosine, np.nextafter(1.0, 0.0))
    insignificant_score = -np.log1p(-bounded_cosine)
    with np.errstate(over="raise", invalid="raise"):
        try:
            score = decisive_score * np.power(insignificant_score, float(lmbd))
        except FloatingPointError as error:
            raise FloatingPointError("ActSub score combination failed") from error
    if not np.isfinite(score).all():
        raise FloatingPointError("ActSub produced non-finite scores")
    diagnostics: dict[str, Any] = {
        **scale_diagnostics,
        "sample_count": int(len(values)),
        "all_scores_finite": True,
        "minimum_mean_cosine": float(np.min(mean_cosine)),
        "maximum_mean_cosine": float(np.max(mean_cosine)),
        "score_standard_deviation": float(np.std(score)),
    }
    return score, diagnostics


def evidence(
    *, percentile: float = 95.0, lmbd: float = 2.0, neighbors: int = 10
) -> dict[str, Any]:
    return {
        "method": "ActSub-SCALE-Fixed",
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "official_commit": OFFICIAL_COMMIT,
        "official_formula": "Eq. 10 decisive_energy_times_insignificant_score_power_lambda",
        "subspace": "full-SVD of frozen linear classifier weight",
        "balance_index": "Eq. 4 automatic norm-balance on known-training embeddings",
        "decisive_score": "Eq. 9 SCALE-shaped decisive projection energy",
        "insignificant_score": "negative_log_one_minus_mean_top10_cosine",
        "neighbors": int(neighbors),
        "scale_percentile": float(percentile),
        "lambda": float(lmbd),
        "hyperparameter_policy": "official_ResNet_defaults_without_APS_OOD_sweep",
        "fit_split": "known_training_embeddings_only",
        "threshold_split": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }

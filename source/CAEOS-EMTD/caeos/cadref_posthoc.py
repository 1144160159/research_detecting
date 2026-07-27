from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import logsumexp


PAPER_URL = (
    "https://openaccess.thecvf.com/content/CVPR2025/html/"
    "Ling_CADRef_Robust_Out-of-Distribution_Detection_via_Class-Aware_"
    "Decoupled_Relative_Feature_Leveraging_CVPR_2025_paper.html"
)
OFFICIAL_CODE_URL = "https://github.com/LingAndZero/CADRef"
OFFICIAL_COMMIT = "121f74b47ebd71644a1c5a6d856880021268c7fa"


@dataclass(frozen=True)
class CADRefState:
    predicted_class_means: np.ndarray
    predicted_class_support: np.ndarray
    predicted_class_counts: np.ndarray
    global_mean_energy: float
    classifier_weight: np.ndarray
    classifier_bias: np.ndarray
    train_sample_count: int


def _finite_matrix(value: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 2 or len(result) == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def fit_cadref(
    classifier_weight: np.ndarray,
    classifier_bias: np.ndarray,
    train_embeddings: np.ndarray,
    train_logits: np.ndarray,
) -> CADRefState:
    """Fit the official predicted-class statistics on known training data."""
    weight = _finite_matrix(classifier_weight, "classifier_weight")
    embeddings = _finite_matrix(train_embeddings, "train_embeddings")
    logits = _finite_matrix(train_logits, "train_logits")
    bias = np.asarray(classifier_bias, dtype=np.float64)
    if bias.ndim != 1 or len(bias) != weight.shape[0] or not np.isfinite(bias).all():
        raise ValueError("classifier_bias must match the classifier rows")
    if len(embeddings) != len(logits) or logits.shape[1] != weight.shape[0]:
        raise ValueError("CADRef training embeddings and logits are incompatible")
    if embeddings.shape[1] != weight.shape[1]:
        raise ValueError("CADRef classifier and embedding dimensions differ")
    reconstructed = embeddings @ weight.T + bias
    linear_difference = float(np.max(np.abs(reconstructed - logits)))
    linear_scale = max(1.0, float(np.max(np.abs(logits))))
    if linear_difference > 1e-5 * linear_scale:
        raise ValueError("CADRef logits do not match the frozen linear classifier")

    predictions = logits.argmax(axis=1)
    counts = np.bincount(predictions, minlength=weight.shape[0]).astype(np.int64)
    support = counts > 0
    means = np.zeros((weight.shape[0], embeddings.shape[1]), dtype=np.float64)
    for class_index in np.flatnonzero(support):
        means[class_index] = embeddings[predictions == class_index].mean(axis=0)
    energy = logsumexp(logits, axis=1)
    mean_energy = float(np.mean(energy))
    if not np.isfinite(mean_energy) or abs(mean_energy) <= 1e-12:
        raise FloatingPointError("CADRef mean known-training Energy is numerically zero")
    return CADRefState(
        predicted_class_means=means,
        predicted_class_support=support,
        predicted_class_counts=counts,
        global_mean_energy=mean_energy,
        classifier_weight=weight,
        classifier_bias=bias,
        train_sample_count=int(len(embeddings)),
    )


def cadref_score_batch(
    embeddings: np.ndarray,
    logits: np.ndarray,
    state: CADRefState,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    values = _finite_matrix(embeddings, "embeddings")
    raw_logits = _finite_matrix(logits, "logits")
    if len(values) != len(raw_logits):
        raise ValueError("CADRef query embeddings and logits are misaligned")
    if values.shape[1] != state.classifier_weight.shape[1]:
        raise ValueError("CADRef query and classifier dimensions differ")
    if raw_logits.shape[1] != state.classifier_weight.shape[0]:
        raise ValueError("CADRef query logits have the wrong class count")
    reconstructed = values @ state.classifier_weight.T + state.classifier_bias
    linear_difference = float(np.max(np.abs(reconstructed - raw_logits)))
    linear_scale = max(1.0, float(np.max(np.abs(raw_logits))))
    if linear_difference > 1e-5 * linear_scale:
        raise ValueError("CADRef query logits do not match the frozen classifier")

    predictions = raw_logits.argmax(axis=1)
    if not np.all(state.predicted_class_support[predictions]):
        missing = sorted(set(predictions[~state.predicted_class_support[predictions]].tolist()))
        raise ValueError(f"CADRef query uses unsupported predicted classes: {missing}")
    relative = values - state.predicted_class_means[predictions]
    feature_norm = np.abs(values).sum(axis=1)
    tolerance = np.finfo(np.float64).eps * np.maximum(
        1.0, np.abs(values).sum(axis=1)
    )
    if np.any(feature_norm <= tolerance):
        raise FloatingPointError("CADRef encountered a zero-L1 query feature")

    caref_error = np.abs(relative).sum(axis=1) / feature_norm
    signs = np.sign(state.classifier_weight[predictions])
    positive = np.maximum(relative * signs, 0.0)
    negative = np.maximum(relative * -signs, 0.0)
    positive_error = positive.sum(axis=1) / feature_norm
    negative_error = negative.sum(axis=1) / feature_norm
    energy = logsumexp(raw_logits, axis=1)
    if np.any(np.abs(energy) <= 1e-12):
        raise FloatingPointError("CADRef encountered numerically zero Energy")
    cadref_error = (
        positive_error / energy
        + negative_error / state.global_mean_energy
    )
    if not all(
        np.isfinite(item).all()
        for item in (caref_error, positive_error, negative_error, cadref_error)
    ):
        raise FloatingPointError("CADRef produced non-finite scores")
    scores = {
        "caref": -caref_error,
        "cadref_energy_fixed": -cadref_error,
    }
    diagnostics: dict[str, Any] = {
        "sample_count": int(len(values)),
        "all_scores_finite": True,
        "caref_score_standard_deviation": float(np.std(scores["caref"])),
        "cadref_score_standard_deviation": float(
            np.std(scores["cadref_energy_fixed"])
        ),
        "minimum_absolute_feature_l1": float(np.min(feature_norm)),
        "minimum_energy": float(np.min(energy)),
        "maximum_energy": float(np.max(energy)),
        "minimum_absolute_energy": float(np.min(np.abs(energy))),
        "queried_predicted_class_count": int(len(np.unique(predictions))),
        "zero_weight_coordinate_count": int(
            np.count_nonzero(state.classifier_weight == 0.0)
        ),
    }
    return scores, diagnostics


def evidence() -> dict[str, Any]:
    return {
        "family": "CARef-and-CADRef-Energy-Fixed",
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "official_commit": OFFICIAL_COMMIT,
        "class_center_formula": "Eq.5 mean embedding grouped by known-training predicted class",
        "caref_formula": "Eq.6 negative normalized L1 relative feature error",
        "cadref_formula": "Eq.10 negative(Ep/Energy(x)+En/mean_train_Energy)",
        "feature_decoupling": "official sign(weight_predicted_class) implementation",
        "logit_method": "Energy",
        "hyperparameter_policy": "official_default_Energy_without_OOD_sweep",
        "fit_split": "known_training_embeddings_and_logits_only",
        "threshold_split": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }

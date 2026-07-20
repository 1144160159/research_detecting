from __future__ import annotations

import numpy as np


PAPER_URL = "https://proceedings.mlr.press/v235/liu24ax.html"
OFFICIAL_CODE_URL = "https://github.com/litianliu/fDBD-OOD"
OFFICIAL_CODE_COMMIT = "961621e320bfeb9d7456356945fdcafb8a12868b"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("fDBD %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("fDBD %s must be finite" % name)
    return array


class FDBDCalibrator:
    """Official hyperparameter-free fDBD score for a frozen linear head."""

    def __init__(self, epsilon: float = 1e-12) -> None:
        self.epsilon = float(epsilon)
        if self.epsilon <= 0.0:
            raise ValueError("fDBD epsilon must be positive")
        self.training_mean: np.ndarray | None = None
        self.denominator_matrix: np.ndarray | None = None
        self.training_count: int | None = None
        self.zero_weight_distance_count: int | None = None

    def fit(self, training_features: np.ndarray, classifier_weights: np.ndarray) -> None:
        features = _matrix(training_features, "training features")
        weights = _matrix(classifier_weights, "classifier weights")
        if features.shape[1] != weights.shape[1] or weights.shape[0] < 2:
            raise ValueError("fDBD feature and classifier dimensions differ")
        differences = weights[None, :, :] - weights[:, None, :]
        denominators = np.linalg.norm(differences, axis=2)
        diagonal = np.eye(len(weights), dtype=bool)
        zero_nonself = (denominators <= self.epsilon) & ~diagonal
        denominators = np.maximum(denominators, self.epsilon)
        denominators[diagonal] = 1.0
        self.training_mean = features.mean(axis=0)
        self.denominator_matrix = denominators
        self.training_count = int(len(features))
        self.zero_weight_distance_count = int(zero_nonself.sum())

    def evaluate(self, features: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        values = _matrix(features, "inference features")
        scores = _matrix(logits, "inference logits")
        if self.training_mean is None or self.denominator_matrix is None:
            raise RuntimeError("fDBD calibrator has not been fitted")
        classes = len(self.denominator_matrix)
        if values.shape[1] != len(self.training_mean) or scores.shape != (len(values), classes):
            raise ValueError("fDBD inference shapes differ from fitted state")
        prediction = scores.argmax(axis=1).astype(np.int64, copy=False)
        predicted_logit = scores[np.arange(len(scores)), prediction]
        logit_gap = np.abs(scores - predicted_logit[:, None])
        boundary_sum = np.sum(logit_gap / self.denominator_matrix[prediction], axis=1)
        feature_deviation = np.linalg.norm(values - self.training_mean[None, :], axis=1)
        confidence = boundary_sum / np.maximum(feature_deviation, self.epsilon)
        return {
            "prediction": prediction,
            "risk": -confidence,
            "confidence": confidence,
            "boundary_distance_sum": boundary_sum,
            "feature_deviation": feature_deviation,
        }

    def evidence(self) -> dict[str, object]:
        if self.training_count is None or self.zero_weight_distance_count is None:
            raise RuntimeError("fDBD fit evidence is incomplete")
        return {
            "method": "fDBD",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "sum_c |logit_c-logit_pred|/||w_c-w_pred|| divided by ||z-training_mean||",
            "fit_split": "known_training_features_only",
            "training_embedding_count": self.training_count,
            "prediction_source": "unmodified_frozen_classifier",
            "risk_orientation": "negative_fdbd_confidence_larger_is_more_unknown",
            "hyperparameters": "none",
            "epsilon": self.epsilon,
            "zero_nonself_weight_distance_count": self.zero_weight_distance_count,
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "numerical_adapter": "epsilon only for zero norms; no effect when official denominators are nonzero",
        }

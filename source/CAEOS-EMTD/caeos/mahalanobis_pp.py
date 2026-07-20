from __future__ import annotations

import numpy as np
from sklearn.covariance import LedoitWolf


PAPER_URL = "https://arxiv.org/abs/2505.18032"


def l2_normalize_rows(values: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("Mahalanobis++ features must be a two-dimensional array")
    if not np.isfinite(values).all():
        raise ValueError("Mahalanobis++ features must be finite")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, float(epsilon))


class MahalanobisPlusPlus:
    """Shared-covariance Mahalanobis distance on L2-normalized features."""

    def __init__(self, epsilon: float = 1e-12):
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        self.epsilon = float(epsilon)
        self.classes: np.ndarray | None = None
        self.means: np.ndarray | None = None
        self.precision: np.ndarray | None = None
        self.training_count = 0

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        normalized = l2_normalize_rows(features, self.epsilon)
        labels = np.asarray(labels, dtype=np.int64)
        if labels.ndim != 1 or labels.shape[0] != normalized.shape[0]:
            raise ValueError("Mahalanobis++ labels must align with features")
        classes = np.unique(labels)
        if classes.size < 2:
            raise ValueError("Mahalanobis++ requires at least two known classes")
        means = np.stack([normalized[labels == value].mean(axis=0) for value in classes])
        residuals = np.concatenate(
            [normalized[labels == value] - means[index] for index, value in enumerate(classes)],
            axis=0,
        )
        self.classes = classes
        self.means = means
        self.precision = LedoitWolf(assume_centered=True).fit(residuals).precision_
        self.training_count = int(normalized.shape[0])

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.means is None or self.precision is None:
            raise RuntimeError("Mahalanobis++ has not been fitted")
        normalized = l2_normalize_rows(features, self.epsilon)
        delta = normalized[:, None, :] - self.means[None, :, :]
        squared = np.einsum("ncd,de,nce->nc", delta, self.precision, delta)
        return np.sqrt(np.maximum(squared.min(axis=1), 0.0))

    def evidence(self) -> dict[str, object]:
        if self.means is None or self.precision is None or self.classes is None:
            raise RuntimeError("Mahalanobis++ has not been fitted")
        return {
            "method": "Mahalanobis++",
            "paper": PAPER_URL,
            "feature_transform": "row_wise_l2_normalization_before_all_gaussian_estimates",
            "covariance": "ledoit_wolf_shared_class_residual_covariance",
            "fit_split": "known_only_train",
            "epsilon": self.epsilon,
            "training_count": self.training_count,
            "class_count": int(self.classes.size),
            "unknown_or_test_labels_used": False,
        }

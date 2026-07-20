from __future__ import annotations

from typing import Any

import numpy as np

from .logit_posthoc import shannon_entropy_risk


class PrototypeDistanceCalibrator:
    """Parameter-free nearest known-class centroid risk in frozen embeddings."""

    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> "PrototypeDistanceCalibrator":
        values = np.asarray(embeddings, dtype=np.float64)
        target = np.asarray(labels, dtype=np.int64)
        if values.ndim != 2 or target.ndim != 1 or len(values) != len(target):
            raise ValueError("prototype inputs have invalid shapes")
        classes = np.unique(target)
        if not np.array_equal(classes, np.arange(len(classes))):
            raise ValueError("prototype labels must be consecutive known-class indices")
        self.class_counts_ = np.asarray([(target == index).sum() for index in classes], dtype=np.int64)
        self.prototypes_ = np.stack([values[target == index].mean(axis=0) for index in classes])
        if not np.isfinite(self.prototypes_).all():
            raise ValueError("prototype centers are not finite")
        return self

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not hasattr(self, "prototypes_"):
            raise ValueError("prototype calibrator is not fitted")
        values = np.asarray(embeddings, dtype=np.float64)
        distances = np.sum((values[:, None, :] - self.prototypes_[None, :, :]) ** 2, axis=2)
        return distances.min(axis=1)

    def evidence(self) -> dict[str, Any]:
        if not hasattr(self, "prototypes_"):
            raise ValueError("prototype calibrator is not fitted")
        return {
            "method": "nearest known-class mean squared Euclidean distance",
            "fit_split": "known_training_embeddings_only",
            "class_count": int(len(self.prototypes_)),
            "embedding_dimension": int(self.prototypes_.shape[1]),
            "class_counts": self.class_counts_.tolist(),
            "hyperparameter_sweep": False,
            "unknown_or_test_labels_used": False,
        }


def evidence() -> dict[str, Any]:
    return {
        "shannon_entropy": {
            "method": "Shannon entropy of frozen softmax probabilities",
            "fit_split": "none",
            "hyperparameter_sweep": False,
            "unknown_or_test_labels_used": False,
        }
    }


__all__ = ["PrototypeDistanceCalibrator", "evidence", "shannon_entropy_risk"]

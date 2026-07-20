from __future__ import annotations

import numpy as np


PAPER_URL = "https://proceedings.iclr.cc/paper_files/paper/2024/file/04b84142b99dae8560b517401e6e5275-Paper-Conference.pdf"
OFFICIAL_CODE_URL = "https://gitlab.com/drti/neco"
OFFICIAL_CODE_COMMIT = "6a55640669f0aad3e23f45ce2f6a8e6400c929ba"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("NECO %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("NECO %s must be finite" % name)
    return array


class NECOID90Calibrator:
    """No-OOD-tuning NECO using the paper's 90% ID-variance rule."""

    def __init__(self, explained_variance: float = 0.90, epsilon: float = 1e-12) -> None:
        self.explained_variance = float(explained_variance)
        self.epsilon = float(epsilon)
        if not 0.0 < self.explained_variance <= 1.0:
            raise ValueError("NECO explained variance must be in (0, 1]")
        if self.epsilon <= 0.0:
            raise ValueError("NECO epsilon must be positive")
        self.mean: np.ndarray | None = None
        self.scale: np.ndarray | None = None
        self.components: np.ndarray | None = None
        self.selected_dimension: int | None = None
        self.training_count: int | None = None
        self.cumulative_explained_variance: float | None = None
        self.zero_scale_dimension_count: int | None = None

    def fit(self, training_features: np.ndarray) -> None:
        features = _matrix(training_features, "training features")
        mean = features.mean(axis=0)
        scale = features.std(axis=0)
        zero_scale = scale <= self.epsilon
        scale = scale.copy()
        scale[zero_scale] = 1.0
        standardized = (features - mean[None, :]) / scale[None, :]
        _, singular_values, components = np.linalg.svd(standardized, full_matrices=False)
        variance = singular_values ** 2
        total = float(variance.sum())
        if total <= self.epsilon:
            raise ValueError("NECO training features have no usable variance")
        cumulative = np.cumsum(variance) / total
        dimension = int(np.searchsorted(cumulative, self.explained_variance, side="left") + 1)
        self.mean = mean
        self.scale = scale
        self.components = components[:dimension]
        self.selected_dimension = dimension
        self.training_count = int(len(features))
        self.cumulative_explained_variance = float(cumulative[dimension - 1])
        self.zero_scale_dimension_count = int(zero_scale.sum())

    def evaluate(self, features: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        values = _matrix(features, "inference features")
        scores = _matrix(logits, "inference logits")
        if self.mean is None or self.scale is None or self.components is None:
            raise RuntimeError("NECO calibrator has not been fitted")
        if values.shape[1] != len(self.mean) or len(values) != len(scores):
            raise ValueError("NECO inference shapes differ from fitted state")
        standardized = (values - self.mean[None, :]) / self.scale[None, :]
        projected = standardized @ self.components.T
        projection_norm = np.linalg.norm(projected, axis=1)
        full_norm = np.linalg.norm(standardized, axis=1)
        confidence = projection_norm / np.maximum(full_norm, self.epsilon)
        return {
            "prediction": scores.argmax(axis=1).astype(np.int64, copy=False),
            "risk": -confidence,
            "confidence": confidence,
            "projection_norm": projection_norm,
            "full_norm": full_norm,
        }

    def evidence(self) -> dict[str, object]:
        if self.selected_dimension is None or self.training_count is None:
            raise RuntimeError("NECO fit evidence is incomplete")
        return {
            "method": "NECO-ID90",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "norm(first_d_PCA_projection(StandardScaler(z))) divided by norm(StandardScaler(z))",
            "fit_split": "known_training_features_only",
            "dimension_selection": "minimum first PCs explaining at least 90% known-training variance",
            "dimension_selection_source": "paper appendix general-case recommendation",
            "main_table_ood_tuned_dimension_reused": False,
            "training_embedding_count": self.training_count,
            "embedding_dimension": int(len(self.mean)),
            "selected_dimension": self.selected_dimension,
            "target_explained_variance": self.explained_variance,
            "selected_cumulative_explained_variance": self.cumulative_explained_variance,
            "prediction_source": "unmodified_frozen_classifier",
            "risk_orientation": "negative_neco_projection_ratio_larger_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "zero_scale_dimension_count": self.zero_scale_dimension_count,
            "architecture_adapter": "Algorithm-1 projection ratio only; no transformer max-logit multiplier",
            "numerical_adapter": "epsilon for zero norms and StandardScaler-compatible unit scale for constant dimensions",
        }

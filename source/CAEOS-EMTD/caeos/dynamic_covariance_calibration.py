from __future__ import annotations

import numpy as np


PAPER_URL = "https://proceedings.mlr.press/v267/guo25m.html"
OFFICIAL_CODE_URL = "https://github.com/workerbcd/ooddcc"


def l2_normalize_rows(values: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("DCC features must be a two-dimensional array")
    if not np.isfinite(values).all():
        raise ValueError("DCC features must be finite")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, float(epsilon))


class DynamicCovarianceCalibration:
    """Known-train Gaussian model with per-query dynamic covariance correction."""

    def __init__(
        self,
        residual_dimension: int = 50,
        ridge: float = 1e-6,
        eigenvalue_floor: float = 1e-8,
        epsilon: float = 1e-12,
    ):
        if residual_dimension <= 0:
            raise ValueError("residual_dimension must be positive")
        if ridge <= 0 or eigenvalue_floor <= 0 or epsilon <= 0:
            raise ValueError("DCC numerical safeguards must be positive")
        self.requested_residual_dimension = int(residual_dimension)
        self.ridge = float(ridge)
        self.eigenvalue_floor = float(eigenvalue_floor)
        self.epsilon = float(epsilon)
        self.classes: np.ndarray | None = None
        self.means: np.ndarray | None = None
        self.covariance: np.ndarray | None = None
        self.residual_basis: np.ndarray | None = None
        self.training_count = 0
        self.residual_dimension = 0

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        normalized = l2_normalize_rows(features, self.epsilon)
        labels = np.asarray(labels, dtype=np.int64)
        if labels.ndim != 1 or labels.shape[0] != normalized.shape[0]:
            raise ValueError("DCC labels must align with features")
        classes = np.unique(labels)
        if classes.size < 2:
            raise ValueError("DCC requires at least two known classes")
        means = np.stack([normalized[labels == value].mean(axis=0) for value in classes])
        residuals = np.concatenate(
            [normalized[labels == value] - means[index] for index, value in enumerate(classes)],
            axis=0,
        )
        covariance = residuals.T @ residuals / max(residuals.shape[0] - 1, 1)
        covariance = (covariance + covariance.T) * 0.5
        covariance += self.ridge * np.eye(covariance.shape[0], dtype=np.float64)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        residual_dimension = min(
            self.requested_residual_dimension, max(covariance.shape[0] - 1, 1)
        )
        self.classes = classes
        self.means = means
        self.covariance = covariance
        self.residual_basis = eigenvectors[:, :residual_dimension].T
        self.training_count = int(normalized.shape[0])
        self.residual_dimension = int(residual_dimension)

    def _dynamic_precision(self, feature: np.ndarray) -> np.ndarray:
        if self.covariance is None or self.residual_basis is None:
            raise RuntimeError("DCC has not been fitted")
        projected = self.residual_basis @ feature
        update = self.residual_basis.T @ projected
        dynamic = self.covariance - np.outer(update, update)
        dynamic = (dynamic + dynamic.T) * 0.5
        eigenvalues, eigenvectors = np.linalg.eigh(dynamic)
        scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
        floor = self.eigenvalue_floor * scale
        inverse = 1.0 / np.maximum(eigenvalues, floor)
        return (eigenvectors * inverse) @ eigenvectors.T

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.means is None:
            raise RuntimeError("DCC has not been fitted")
        normalized = l2_normalize_rows(features, self.epsilon)
        scores = np.empty(normalized.shape[0], dtype=np.float64)
        for index, feature in enumerate(normalized):
            precision = self._dynamic_precision(feature)
            delta = feature[None, :] - self.means
            squared = np.einsum("cd,de,ce->c", delta, precision, delta)
            scores[index] = np.sqrt(max(float(np.min(squared)), 0.0))
        return scores

    def evidence(self) -> dict[str, object]:
        if self.means is None or self.classes is None or self.covariance is None:
            raise RuntimeError("DCC has not been fitted")
        return {
            "method": "Dynamic Covariance Calibration",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "fit_split": "known_only_train",
            "feature_transform": "row_wise_l2_normalization",
            "dynamic_update": "known_train_covariance_minus_query_residual_projection_outer_product",
            "requested_residual_dimension": self.requested_residual_dimension,
            "effective_residual_dimension": self.residual_dimension,
            "tabular_adaptation": "fixed_WRN_style_residual_dimension_50_capped_at_d_minus_1",
            "numerical_safeguards": {
                "ridge": self.ridge,
                "symmetric_eigendecomposition": True,
                "relative_eigenvalue_floor": self.eigenvalue_floor,
            },
            "training_count": self.training_count,
            "class_count": int(self.classes.size),
            "unknown_or_test_labels_used": False,
        }

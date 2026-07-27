from __future__ import annotations

import numpy as np


PAPER_URL = (
    "https://openaccess.thecvf.com/content/ICCV2023/html/"
    "Chen_WDiscOOD_Out-of-Distribution_Detection_via_Whitened_Linear_"
    "Discriminant_Analysis_ICCV_2023_paper.html"
)
OFFICIAL_CODE_URL = "https://github.com/ivalab/WDiscOOD"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 2 or result.shape[0] == 0 or result.shape[1] < 2:
        raise ValueError(f"{name} must be a nonempty two-dimensional matrix")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


class WDiscOOD:
    """Whitened LDA distance in discriminative and residual subspaces."""

    def __init__(
        self,
        alpha: float = 1.0,
        ridge: float = 1e-6,
        discriminant_dimension: int | None = None,
    ):
        if not np.isfinite(alpha) or alpha < 0.0:
            raise ValueError("WDiscOOD alpha must be finite and nonnegative")
        if not np.isfinite(ridge) or ridge <= 0.0:
            raise ValueError("WDiscOOD ridge must be finite and positive")
        if discriminant_dimension is not None and discriminant_dimension <= 0:
            raise ValueError("WDiscOOD discriminant dimension must be positive")
        self.alpha = float(alpha)
        self.ridge = float(ridge)
        self.discriminant_dimension = discriminant_dimension
        self.classes: np.ndarray | None = None
        self.feature_mean: np.ndarray | None = None
        self.whitener: np.ndarray | None = None
        self.discriminants: np.ndarray | None = None
        self.wd_class_centers: np.ndarray | None = None
        self.wdr_center: np.ndarray | None = None
        self.training_count = 0
        self.whitening_eigenvalue_floor: float | None = None

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        values = _matrix(features, "WDiscOOD training features")
        labels = np.asarray(labels, dtype=np.int64)
        if labels.ndim != 1 or len(labels) != len(values):
            raise ValueError("WDiscOOD labels must align with training features")
        classes = np.unique(labels)
        if classes.size < 2:
            raise ValueError("WDiscOOD requires at least two known classes")

        feature_mean = values.mean(axis=0)
        centered = values - feature_mean
        class_centers = np.stack(
            [centered[labels == value].mean(axis=0) for value in classes]
        )
        residuals = np.concatenate(
            [
                centered[labels == value] - class_centers[index]
                for index, value in enumerate(classes)
            ],
            axis=0,
        )
        within = residuals.T @ residuals / float(len(residuals))
        scale = max(float(np.trace(within) / within.shape[0]), 1e-12)
        floor = self.ridge * scale
        eigenvalues, eigenvectors = np.linalg.eigh(within)
        inverse_sqrt = 1.0 / np.sqrt(np.maximum(eigenvalues, floor))
        whitener = (eigenvectors * inverse_sqrt) @ eigenvectors.T

        whitened = centered @ whitener
        whitened_class_centers = np.stack(
            [whitened[labels == value].mean(axis=0) for value in classes]
        )
        between = np.zeros((values.shape[1], values.shape[1]), dtype=np.float64)
        for index, value in enumerate(classes):
            count = int(np.sum(labels == value))
            center = whitened_class_centers[index]
            between += count * np.outer(center, center)
        between /= float(len(values))
        eigenvalues, eigenvectors = np.linalg.eigh(between)
        order = np.argsort(eigenvalues)[::-1]
        maximum = min(classes.size - 1, values.shape[1] - 1)
        dimension = (
            maximum
            if self.discriminant_dimension is None
            else min(int(self.discriminant_dimension), maximum)
        )
        discriminants = eigenvectors[:, order[:dimension]]

        wd = whitened @ discriminants
        projected = wd @ discriminants.T
        wdr = whitened - projected
        self.classes = classes
        self.feature_mean = feature_mean
        self.whitener = whitener
        self.discriminants = discriminants
        self.wd_class_centers = np.stack(
            [wd[labels == value].mean(axis=0) for value in classes]
        )
        self.wdr_center = wdr.mean(axis=0)
        self.training_count = int(len(values))
        self.whitening_eigenvalue_floor = float(floor)

    def components(self, features: np.ndarray) -> dict[str, np.ndarray]:
        if (
            self.feature_mean is None
            or self.whitener is None
            or self.discriminants is None
            or self.wd_class_centers is None
            or self.wdr_center is None
        ):
            raise RuntimeError("WDiscOOD has not been fitted")
        values = _matrix(features, "WDiscOOD query features")
        if values.shape[1] != self.feature_mean.shape[0]:
            raise ValueError("WDiscOOD query feature dimension differs from training")
        whitened = (values - self.feature_mean) @ self.whitener
        wd = whitened @ self.discriminants
        wd_delta = wd[:, None, :] - self.wd_class_centers[None, :, :]
        wd_distance = np.linalg.norm(wd_delta, axis=2).min(axis=1)
        wdr = whitened - (wd @ self.discriminants.T)
        wdr_distance = np.linalg.norm(wdr - self.wdr_center, axis=1)
        return {
            "wd_distance": wd_distance,
            "wdr_distance": wdr_distance,
        }

    def score(self, features: np.ndarray) -> np.ndarray:
        components = self.components(features)
        return components["wd_distance"] + self.alpha * components["wdr_distance"]

    def evidence(self) -> dict[str, object]:
        if self.discriminants is None or self.classes is None:
            raise RuntimeError("WDiscOOD has not been fitted")
        return {
            "method": "WDiscOOD",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "feature_space": "frozen_prelogit_embedding",
            "whitening": "known_train_pooled_within_class_covariance",
            "discriminative_score": "nearest_known_class_center_euclidean_distance",
            "residual_score": "distance_to_known_train_residual_center",
            "alpha": self.alpha,
            "alpha_selection": "fixed_a_priori",
            "ridge": self.ridge,
            "discriminant_dimension": int(self.discriminants.shape[1]),
            "training_count": self.training_count,
            "known_class_count": int(len(self.classes)),
            "whitening_eigenvalue_floor": self.whitening_eigenvalue_floor,
            "unknown_or_test_labels_used": False,
        }

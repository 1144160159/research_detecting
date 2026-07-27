from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.special import ndtri
from sklearn.covariance import LedoitWolf


EPSILON = 1e-12
FEATURE_NAMES = (
    "reliability_weighted_view_js",
    "maximum_view_to_consensus_js",
    "pairwise_conflict_laplacian_radius",
    "conflict_reliability_coupling",
    "global_to_view_fused_js",
)


def _probability(values: np.ndarray, name: str) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim < 2 or not np.isfinite(values).all() or np.any(values < 0.0):
        raise ValueError(f"{name} must be a finite nonnegative probability array")
    normalizer = values.sum(axis=-1, keepdims=True)
    if np.any(normalizer <= 0.0):
        raise ValueError(f"{name} contains an empty probability vector")
    return values / normalizer


def _kl_divergence(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left = np.clip(left, EPSILON, 1.0)
    right = np.clip(right, EPSILON, 1.0)
    return np.sum(left * (np.log(left) - np.log(right)), axis=-1)


def _paired_js(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    midpoint = 0.5 * (left + right)
    class_count = left.shape[-1]
    scale = np.log(max(2, class_count))
    return 0.5 * (_kl_divergence(left, midpoint) + _kl_divergence(right, midpoint)) / scale


def conflict_topology_features(
    *,
    view_probability: np.ndarray,
    view_reliability: np.ndarray,
    pairwise_conflict: np.ndarray,
    global_probability: np.ndarray,
    view_fused_probability: np.ndarray,
) -> np.ndarray:
    """Extract permutation-invariant conflict-topology features per sample."""
    view_probability = _probability(view_probability, "view_probability")
    global_probability = _probability(global_probability, "global_probability")
    view_fused_probability = _probability(
        view_fused_probability, "view_fused_probability"
    )
    if view_probability.ndim != 3:
        raise ValueError("view_probability must have shape [samples, views, classes]")
    sample_count, view_count, class_count = view_probability.shape
    if view_count < 2 or class_count < 2:
        raise ValueError("conflict topology requires at least two views and classes")
    if global_probability.shape != (sample_count, class_count):
        raise ValueError("global_probability shape is incompatible")
    if view_fused_probability.shape != (sample_count, class_count):
        raise ValueError("view_fused_probability shape is incompatible")

    reliability = np.asarray(view_reliability, dtype=np.float64)
    conflict = np.asarray(pairwise_conflict, dtype=np.float64)
    if reliability.shape != (sample_count, view_count):
        raise ValueError("view_reliability shape is incompatible")
    if conflict.shape != (sample_count, view_count, view_count):
        raise ValueError("pairwise_conflict shape is incompatible")
    if not np.isfinite(reliability).all() or not np.isfinite(conflict).all():
        raise ValueError("reliability and conflict must be finite")
    if np.any(reliability < 0.0) or np.any(conflict < 0.0):
        raise ValueError("reliability and conflict must be nonnegative")

    reliability = np.clip(reliability, 0.0, 1.0)
    weights = reliability / np.maximum(reliability.sum(axis=1, keepdims=True), EPSILON)
    empty = reliability.sum(axis=1) <= EPSILON
    weights[empty] = 1.0 / view_count
    consensus = np.sum(weights[:, :, None] * view_probability, axis=1)
    per_view_js = _paired_js(view_probability, consensus[:, None, :])
    weighted_js = np.sum(weights * per_view_js, axis=1)
    maximum_js = per_view_js.max(axis=1)

    adjacency = np.clip(0.5 * (conflict + conflict.transpose(0, 2, 1)), 0.0, 1.0)
    diagonal = np.arange(view_count)
    adjacency[:, diagonal, diagonal] = 0.0
    degree = adjacency.sum(axis=2)
    laplacian = -adjacency
    laplacian[:, diagonal, diagonal] = degree
    spectral_radius = np.linalg.eigvalsh(laplacian)[:, -1] / view_count
    coupling = np.sum(degree * (1.0 - reliability), axis=1) / (
        view_count * max(1, view_count - 1)
    )
    global_view_js = _paired_js(global_probability, view_fused_probability)

    features = np.column_stack(
        [weighted_js, maximum_js, spectral_radius, coupling, global_view_js]
    )
    if features.shape != (sample_count, len(FEATURE_NAMES)):
        raise AssertionError("unexpected conflict-topology feature shape")
    if not np.isfinite(features).all() or np.any(features < -EPSILON):
        raise FloatingPointError("conflict-topology features are invalid")
    return np.maximum(features, 0.0)


@dataclass
class KnownOnlyCopulaRisk:
    calibration_fraction: float = 0.4
    split_seed: int = 229

    def __post_init__(self) -> None:
        if not 0.2 <= float(self.calibration_fraction) <= 0.5:
            raise ValueError("calibration_fraction must be in [0.2, 0.5]")
        self.feature_reference: list[np.ndarray] | None = None
        self.location: np.ndarray | None = None
        self.precision: np.ndarray | None = None
        self.tail_reference: np.ndarray | None = None
        self.fit_indices: np.ndarray | None = None
        self.calibration_indices: np.ndarray | None = None

    def _split(self, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        labels = np.asarray(labels)
        if labels.ndim != 1:
            raise ValueError("known validation labels must be one-dimensional")
        rng = np.random.RandomState(self.split_seed)
        fit_parts: list[np.ndarray] = []
        calibration_parts: list[np.ndarray] = []
        for label in np.unique(labels):
            indices = np.flatnonzero(labels == label)
            if len(indices) < 4:
                raise ValueError("each known validation class requires at least four samples")
            indices = indices[rng.permutation(len(indices))]
            calibration_count = max(1, int(np.floor(len(indices) * self.calibration_fraction)))
            calibration_count = min(calibration_count, len(indices) - 2)
            calibration_parts.append(indices[:calibration_count])
            fit_parts.append(indices[calibration_count:])
        return np.sort(np.concatenate(fit_parts)), np.sort(np.concatenate(calibration_parts))

    @staticmethod
    def _validate_features(features: np.ndarray) -> np.ndarray:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim != 2 or features.shape[1] != len(FEATURE_NAMES):
            raise ValueError("unexpected conflict-topology feature matrix")
        if not np.isfinite(features).all():
            raise ValueError("conflict-topology features must be finite")
        return features

    def _normal_scores(self, features: np.ndarray) -> np.ndarray:
        if self.feature_reference is None:
            raise RuntimeError("copula risk is not fitted")
        columns = []
        for values, reference in zip(features.T, self.feature_reference):
            rank = np.searchsorted(reference, values, side="right")
            probability = (rank + 0.5) / (len(reference) + 1.0)
            probability = np.clip(probability, 1e-6, 1.0 - 1e-6)
            columns.append(ndtri(probability))
        return np.column_stack(columns)

    def _distance(self, features: np.ndarray) -> np.ndarray:
        if self.location is None or self.precision is None:
            raise RuntimeError("copula risk is not fitted")
        centered = self._normal_scores(features) - self.location
        return np.einsum("ni,ij,nj->n", centered, self.precision, centered)

    def fit(self, features: np.ndarray, known_labels: Sequence[int]) -> "KnownOnlyCopulaRisk":
        features = self._validate_features(features)
        labels = np.asarray(known_labels)
        if len(labels) != len(features):
            raise ValueError("known validation labels are not aligned")
        fit_indices, calibration_indices = self._split(labels)
        fit_features = features[fit_indices]
        self.feature_reference = [np.sort(values) for values in fit_features.T]
        transformed = self._normal_scores(fit_features)
        covariance = LedoitWolf().fit(transformed)
        self.location = np.asarray(covariance.location_, dtype=np.float64)
        self.precision = np.asarray(covariance.precision_, dtype=np.float64)
        self.fit_indices = fit_indices
        self.calibration_indices = calibration_indices
        self.tail_reference = np.sort(self._distance(features[calibration_indices]))
        return self

    def score(self, features: np.ndarray) -> np.ndarray:
        features = self._validate_features(features)
        if self.tail_reference is None:
            raise RuntimeError("copula risk is not fitted")
        distance = self._distance(features)
        rank = np.searchsorted(self.tail_reference, distance, side="right")
        return rank.astype(np.float64) / (len(self.tail_reference) + 1.0)

    def evidence(self) -> dict[str, object]:
        if self.tail_reference is None or self.fit_indices is None or self.calibration_indices is None:
            raise RuntimeError("copula risk is not fitted")
        return {
            "schema_version": "known_only_conflict_topology_copula_v1",
            "feature_names": list(FEATURE_NAMES),
            "calibration_fraction": float(self.calibration_fraction),
            "split_seed": int(self.split_seed),
            "fit_count": int(len(self.fit_indices)),
            "calibration_count": int(len(self.calibration_indices)),
            "uses_unknown_or_test_labels_for_fit": False,
        }


def blend_with_incumbent(
    incumbent_risk: np.ndarray, topology_risk: np.ndarray, alpha: float = 0.25
) -> np.ndarray:
    incumbent = np.asarray(incumbent_risk, dtype=np.float64)
    topology = np.asarray(topology_risk, dtype=np.float64)
    if incumbent.shape != topology.shape or incumbent.ndim != 1:
        raise ValueError("incumbent and topology risk must be aligned vectors")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    if not np.isfinite(incumbent).all() or not np.isfinite(topology).all():
        raise ValueError("risk values must be finite")
    return (1.0 - alpha) * incumbent + alpha * topology

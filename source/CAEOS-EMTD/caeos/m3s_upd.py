from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors


class M3SClassifier(nn.Module):
    """Small tabular classifier used by the paper-formula M3S-UPD adapter."""

    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        hidden_dims: Sequence[int] = (128, 64),
        embedding_dim: int = 32,
        dropout: float = 0.15,
    ):
        super().__init__()
        layers: List[nn.Module] = []
        previous = int(input_dim)
        for width in hidden_dims:
            layers.extend(
                [
                    nn.Linear(previous, int(width)),
                    nn.LayerNorm(int(width)),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                ]
            )
            previous = int(width)
        self.encoder = nn.Sequential(*layers)
        self.embedding = nn.Linear(previous, int(embedding_dim))
        self.classifier = nn.Linear(int(embedding_dim), int(num_classes))

    def forward(self, values: torch.Tensor) -> Dict[str, torch.Tensor]:
        hidden = self.encoder(values)
        embedding = self.embedding(hidden)
        return {
            "logits": self.classifier(F.relu(embedding)),
            "embedding": embedding,
        }


def standardize_embeddings(
    reference: np.ndarray, values: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    reference = np.asarray(reference, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    mean = reference.mean(axis=0)
    std = reference.std(axis=0)
    std[std < 1e-8] = 1.0
    return (reference - mean) / std, (values - mean) / std, np.stack([mean, std])


def adaptive_dbscan_eps(
    embeddings: np.ndarray,
    min_samples: int = 5,
    quantile: float = 0.90,
) -> float:
    embeddings = np.asarray(embeddings, dtype=np.float64)
    if len(embeddings) < 2:
        return 1e-6
    neighbors = min(max(2, int(min_samples)), len(embeddings))
    estimator = NearestNeighbors(n_neighbors=neighbors).fit(embeddings)
    distances, _ = estimator.kneighbors(embeddings)
    kth_distance = distances[:, -1]
    eps = float(np.quantile(kth_distance, quantile))
    if not np.isfinite(eps) or eps <= 0.0:
        positive = kth_distance[kth_distance > 0.0]
        eps = float(np.median(positive)) if len(positive) else 1e-6
    return max(float(np.nextafter(eps, np.inf)), 1e-6)


def cluster_embeddings(
    embeddings: np.ndarray,
    min_samples: int = 5,
    eps_quantile: float = 0.90,
) -> Tuple[np.ndarray, float]:
    embeddings = np.asarray(embeddings, dtype=np.float64)
    if len(embeddings) < max(2, min_samples):
        return np.arange(len(embeddings), dtype=np.int64), 1e-6
    eps = adaptive_dbscan_eps(embeddings, min_samples, eps_quantile)
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(embeddings)
    if np.any(labels == -1):
        next_label = int(labels.max()) + 1
        for index in np.where(labels == -1)[0]:
            labels[index] = next_label
            next_label += 1
    return labels.astype(np.int64), eps


def class_centroids(
    embeddings: np.ndarray, labels: np.ndarray, num_classes: int
) -> np.ndarray:
    embeddings = np.asarray(embeddings, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    centroids = []
    for label in range(num_classes):
        selected = embeddings[labels == label]
        if not len(selected):
            raise ValueError("class %d has no labeled embeddings" % label)
        centroids.append(selected.mean(axis=0))
    return np.stack(centroids)


def alignment_threshold(
    labeled_embeddings: np.ndarray,
    labeled_labels: np.ndarray,
    centroids: np.ndarray,
    quantile: float = 0.95,
) -> float:
    own = centroids[np.asarray(labeled_labels, dtype=np.int64)]
    distances = np.linalg.norm(np.asarray(labeled_embeddings) - own, axis=1)
    threshold = float(np.quantile(distances, quantile))
    return max(threshold, 1e-6)


@dataclass(frozen=True)
class SpatialAlignment:
    auxiliary_labels: np.ndarray
    potential_unknown: np.ndarray
    sample_distance: np.ndarray
    cluster_labels: np.ndarray
    eps: float


def align_unlabeled_clusters(
    unlabeled_embeddings: np.ndarray,
    centroids: np.ndarray,
    distance_threshold: float,
    min_samples: int = 5,
    eps_quantile: float = 0.90,
) -> SpatialAlignment:
    unlabeled_embeddings = np.asarray(unlabeled_embeddings, dtype=np.float64)
    clusters, eps = cluster_embeddings(
        unlabeled_embeddings, min_samples=min_samples, eps_quantile=eps_quantile
    )
    auxiliary = np.empty(len(unlabeled_embeddings), dtype=np.int64)
    potential_unknown = np.zeros(len(unlabeled_embeddings), dtype=bool)
    sample_distance = np.empty(len(unlabeled_embeddings), dtype=np.float64)
    for cluster in np.unique(clusters):
        indices = np.where(clusters == cluster)[0]
        cluster_center = unlabeled_embeddings[indices].mean(axis=0)
        distances = np.linalg.norm(centroids - cluster_center, axis=1)
        nearest = int(np.argmin(distances))
        minimum = float(distances[nearest])
        auxiliary[indices] = nearest
        potential_unknown[indices] = minimum >= distance_threshold
        sample_distance[indices] = minimum
    return SpatialAlignment(
        auxiliary_labels=auxiliary,
        potential_unknown=potential_unknown,
        sample_distance=sample_distance,
        cluster_labels=clusters,
        eps=eps,
    )


@dataclass(frozen=True)
class ConsistencySelection:
    known_indices: np.ndarray
    unknown_indices: np.ndarray
    deferred_indices: np.ndarray
    confidence_low: float
    confidence_high: float


def consistency_selection(
    probabilities: np.ndarray,
    alignment: SpatialAlignment,
    top_fraction: float = 0.10,
    bottom_fraction: float = 0.10,
) -> ConsistencySelection:
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if len(probabilities) == 0:
        empty = np.empty(0, dtype=np.int64)
        return ConsistencySelection(empty, empty, empty, float("nan"), float("nan"))
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    low = float(np.quantile(confidence, bottom_fraction))
    high = float(np.quantile(confidence, 1.0 - top_fraction))
    known = (
        (confidence >= high)
        & (~alignment.potential_unknown)
        & (prediction == alignment.auxiliary_labels)
    )
    unknown = (confidence <= low) & alignment.potential_unknown
    deferred = ~(known | unknown)
    return ConsistencySelection(
        known_indices=np.where(known)[0],
        unknown_indices=np.where(unknown)[0],
        deferred_indices=np.where(deferred)[0],
        confidence_low=low,
        confidence_high=high,
    )


def unknown_risk(
    probabilities: np.ndarray,
    sample_distance: np.ndarray,
    distance_threshold: float,
) -> np.ndarray:
    confidence_risk = 1.0 - np.asarray(probabilities).max(axis=1)
    distance_risk = np.asarray(sample_distance) / max(distance_threshold, 1e-6)
    distance_risk = distance_risk / (1.0 + distance_risk)
    return 0.5 * (confidence_risk + distance_risk)


def iter_minibatches(
    indices: np.ndarray,
    batch_size: int,
    rng: np.random.RandomState,
) -> Iterable[np.ndarray]:
    shuffled = np.asarray(indices, dtype=np.int64).copy()
    rng.shuffle(shuffled)
    for start in range(0, len(shuffled), batch_size):
        yield shuffled[start : start + batch_size]

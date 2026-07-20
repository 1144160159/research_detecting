from __future__ import annotations

import numpy as np
import torch
from sklearn.neighbors import NearestNeighbors
from torch import nn
import torch.nn.functional as F


class ResidualBlock1D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size=3, stride=stride, padding=1
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.shortcut = (
            nn.Identity()
            if stride == 1 and in_channels == out_channels
            else nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm1d(out_channels),
            )
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(values)
        values = F.relu(self.bn1(self.conv1(values)))
        values = self.bn2(self.conv2(values))
        return F.relu(values + residual)


class AEGISClassifier(nn.Module):
    """AEGIS-Net DeepResNet adapted to concatenated tabular feature sequences."""

    def __init__(self, input_dims: tuple[int, ...], num_classes: int) -> None:
        super().__init__()
        self.input_dim = sum(input_dims)
        self.conv1 = nn.Conv1d(1, 64, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm1d(64)
        self.blocks = nn.Sequential(
            ResidualBlock1D(64, 128),
            ResidualBlock1D(128, 256, stride=2),
            ResidualBlock1D(256, 512, stride=2),
            ResidualBlock1D(512, 1024, stride=2),
        )
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.classifier = nn.Linear(1024, num_classes)

    def forward_values(self, values: torch.Tensor) -> dict[str, torch.Tensor]:
        if values.ndim != 2 or values.shape[1] != self.input_dim:
            raise ValueError("AEGIS input has unexpected shape")
        hidden = F.relu(self.bn1(self.conv1(values.unsqueeze(1))))
        hidden = self.blocks(hidden)
        embedding = self.pool(hidden).flatten(1)
        return {
            "logits": self.classifier(embedding),
            "embedding": embedding,
            "detection_embedding": F.normalize(embedding[:, -128:], dim=1),
        }

    def forward(self, views: tuple[torch.Tensor, ...]) -> torch.Tensor:
        return self.forward_values(torch.cat(views, dim=1))["logits"]


def supervised_contrastive_loss(
    embedding: torch.Tensor, labels: torch.Tensor, temperature: float
) -> torch.Tensor:
    normalized = F.normalize(embedding, dim=1)
    similarity = normalized @ normalized.T / temperature
    self_mask = torch.eye(len(labels), dtype=torch.bool, device=labels.device)
    positive = labels[:, None].eq(labels[None, :]) & ~self_mask
    similarity = similarity - similarity.max(dim=1, keepdim=True).values.detach()
    exp_similarity = torch.exp(similarity).masked_fill(self_mask, 0.0)
    log_probability = similarity - torch.log(
        exp_similarity.sum(dim=1, keepdim=True).clamp_min(1e-12)
    )
    positive_count = positive.sum(dim=1)
    valid = positive_count > 0
    if not bool(valid.any()):
        return embedding.sum() * 0.0
    mean_positive = (log_probability * positive).sum(dim=1) / positive_count.clamp_min(1)
    return -mean_positive[valid].mean()


def _cosine_similarity(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    first_norm = np.linalg.norm(first, axis=1, keepdims=True)
    second_norm = np.linalg.norm(second, axis=1, keepdims=True)
    return (first @ second.T) / (first_norm @ second_norm.T + 1e-8)


def _class_prototypes(
    embedding: np.ndarray,
    labels: np.ndarray,
    class_index: int,
    prototypes: int,
    maximum_samples: int,
    rng: np.random.Generator,
) -> np.ndarray:
    values = embedding[labels == class_index]
    if len(values) == 0:
        raise ValueError("AEGIS class has no known-training samples")
    if len(values) > maximum_samples:
        values = values[rng.choice(len(values), maximum_samples, replace=False)]
    if len(values) <= prototypes:
        return values
    similarity = _cosine_similarity(values, values)
    cutoff = np.quantile(similarity, 0.6, method="higher")
    density = (similarity > cutoff).sum(axis=1) - (np.diag(similarity) > cutoff)
    maximum_density = density.max()
    eta = np.where(
        density == maximum_density,
        similarity.min(axis=1),
        np.fmax(
            np.diag(similarity),
            np.max(similarity * (density[:, None] > density[None, :]), axis=1),
        ),
    )
    indices = np.argpartition(eta, prototypes)[:prototypes]
    return values[indices]


def produce_pseudo_labels(
    embedding: np.ndarray,
    labels: np.ndarray,
    num_classes: int,
    prototypes: int = 14,
    maximum_samples: int = 1280,
    seed: int = 7,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    prototype_sets = [
        _class_prototypes(
            embedding,
            labels,
            class_index,
            prototypes,
            maximum_samples,
            rng,
        )
        for class_index in range(num_classes)
    ]
    scores = np.stack(
        [_cosine_similarity(embedding, values).mean(axis=1) for values in prototype_sets],
        axis=1,
    )
    return scores.argmax(axis=1).astype(np.int64)


class AEGISKNN:
    def __init__(self, neighbors: int = 50) -> None:
        self.neighbors = neighbors
        self.model: NearestNeighbors | None = None
        self.fitted_neighbors = 0

    def fit(self, embedding: np.ndarray) -> "AEGISKNN":
        values = np.asarray(embedding, dtype=np.float32)
        if values.ndim != 2 or len(values) < 2:
            raise ValueError("AEGIS KNN requires at least two training embeddings")
        self.fitted_neighbors = min(self.neighbors, len(values))
        self.model = NearestNeighbors(
            n_neighbors=self.fitted_neighbors, metric="euclidean", n_jobs=-1
        ).fit(values)
        return self

    def score(self, embedding: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("AEGIS KNN is not fitted")
        distances, _ = self.model.kneighbors(
            np.asarray(embedding, dtype=np.float32), return_distance=True
        )
        return distances[:, -1].astype(np.float64)

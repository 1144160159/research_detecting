from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock1D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size=3, stride=stride, padding=1
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.shortcut = (
            nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm1d(out_channels),
            )
            if stride != 1 or in_channels != out_channels
            else nn.Identity()
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(values)
        values = F.relu(self.bn1(self.conv1(values)), inplace=True)
        values = self.bn2(self.conv2(values))
        return F.relu(values + residual, inplace=True)


class SieveClassifier(nn.Module):
    """Official Sieve 1D DeepResNet adapted to CAEOS multi-view tensors."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        initial_channels: int = 32,
    ):
        super().__init__()
        self.input_dims = tuple(int(value) for value in input_dims)
        self.conv1 = nn.Conv1d(
            1, initial_channels, kernel_size=7, stride=2, padding=3
        )
        self.bn1 = nn.BatchNorm1d(initial_channels)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(initial_channels, initial_channels, 2)
        self.layer2 = self._make_layer(
            initial_channels, initial_channels * 2, 2, stride=2
        )
        self.layer3 = self._make_layer(
            initial_channels * 2, initial_channels * 4, 2, stride=2
        )
        self.layer4 = self._make_layer(
            initial_channels * 4, initial_channels * 8, 2, stride=2
        )
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.classifier = nn.Linear(initial_channels * 8, num_classes)
        self.projection = nn.Sequential(
            nn.Linear(initial_channels * 8, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 128),
        )
        self._initialize_weights()

    @staticmethod
    def _make_layer(
        in_channels: int, out_channels: int, blocks: int, stride: int = 1
    ) -> nn.Sequential:
        layers = [ResidualBlock1D(in_channels, out_channels, stride)]
        layers.extend(
            ResidualBlock1D(out_channels, out_channels) for _ in range(1, blocks)
        )
        return nn.Sequential(*layers)

    def _initialize_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv1d):
                nn.init.kaiming_normal_(
                    module.weight, mode="fan_out", nonlinearity="relu"
                )
            elif isinstance(module, nn.BatchNorm1d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)

    @staticmethod
    def concatenate_views(views: Sequence[torch.Tensor]) -> torch.Tensor:
        return torch.cat(tuple(views), dim=1)

    def encode_values(
        self, values: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if values.ndim == 2:
            values = values.unsqueeze(1)
        values = self.maxpool(F.relu(self.bn1(self.conv1(values)), inplace=True))
        pooled = []
        for layer in (self.layer1, self.layer2, self.layer3, self.layer4):
            values = layer(values)
            pooled.append(F.adaptive_avg_pool1d(values, 1).squeeze(-1))
        embedding = self.avgpool(values).squeeze(-1)
        detection_embedding = F.normalize(torch.cat(pooled, dim=1), dim=1)
        return embedding, detection_embedding

    def forward_values(self, values: torch.Tensor) -> dict[str, torch.Tensor]:
        embedding, detection_embedding = self.encode_values(values)
        return {
            "logits": self.classifier(embedding),
            "embedding": embedding,
            "detection_embedding": detection_embedding,
        }

    def forward(
        self, views: Sequence[torch.Tensor], quality: torch.Tensor | None = None
    ) -> dict[str, torch.Tensor]:
        del quality
        return self.forward_values(self.concatenate_views(views))


def swap_adjacent_features(values: torch.Tensor, ratio: float) -> torch.Tensor:
    """Apply Sieve's feature swapping with non-overlapping adjacent pairs."""

    swaps = int(values.shape[1] * ratio)
    if swaps <= 0 or values.shape[1] < 2:
        return values.clone()
    pair_count = values.shape[1] // 2
    swaps = min(swaps, pair_count)
    random_order = torch.rand(
        values.shape[0], pair_count, device=values.device
    ).argsort(dim=1)[:, :swaps]
    starts = 2 * random_order
    order = torch.arange(values.shape[1], device=values.device).expand(
        values.shape[0], -1
    ).clone()
    order.scatter_(1, starts, starts + 1)
    order.scatter_(1, starts + 1, starts)
    return torch.gather(values, 1, order)


def sieve_contrastive_loss(
    first: torch.Tensor, second: torch.Tensor, temperature: float
) -> torch.Tensor:
    first = F.normalize(first, dim=1)
    second = F.normalize(second, dim=1)
    positive = torch.sum(first * second, dim=1) / temperature
    cross = torch.mm(first, second.T) / temperature
    within_first = torch.mm(first, first.T) / temperature
    within_second = torch.mm(second, second.T) / temperature
    diagonal = torch.eye(first.shape[0], device=first.device, dtype=torch.bool)
    cross = cross.masked_fill(diagonal, float("-inf"))
    within_first = within_first.masked_fill(diagonal, float("-inf"))
    within_second = within_second.masked_fill(diagonal, float("-inf"))
    target = torch.zeros(first.shape[0], device=first.device, dtype=torch.long)
    first_logits = torch.cat(
        [positive[:, None], cross, within_first], dim=1
    )
    second_logits = torch.cat(
        [positive[:, None], cross.T, within_second], dim=1
    )
    return 0.5 * (
        F.cross_entropy(first_logits, target)
        + F.cross_entropy(second_logits, target)
    )


def balanced_knn_scores(
    features: torch.Tensor,
    labels: torch.Tensor,
    num_classes: int,
    neighbors: int,
    chunk_size: int = 1024,
    exclude_self: bool = True,
) -> torch.Tensor:
    features = F.normalize(features, dim=1)
    labels = labels.to(features.device)
    population = torch.bincount(labels, minlength=num_classes).to(features.dtype)
    prior = population.clamp_min(1e-10) / population.sum().clamp_min(1.0)
    k = min(neighbors, features.shape[0] - int(exclude_self))
    if k < 1:
        return F.one_hot(labels, num_classes=num_classes).to(features.dtype)
    parts = []
    for start in range(0, features.shape[0], chunk_size):
        stop = min(start + chunk_size, features.shape[0])
        similarity = torch.mm(features[start:stop], features.T)
        if exclude_self:
            rows = torch.arange(stop - start, device=features.device)
            columns = torch.arange(start, stop, device=features.device)
            similarity[rows, columns] = float("-inf")
        indices = similarity.topk(k=k, dim=1).indices
        neighbor_labels = labels[indices]
        scores = torch.zeros(
            stop - start, num_classes, device=features.device, dtype=features.dtype
        )
        scores.scatter_add_(
            1, neighbor_labels, torch.ones_like(neighbor_labels, dtype=features.dtype)
        )
        scores = scores / float(k)
        scores = scores / prior
        parts.append(scores / scores.sum(dim=1, keepdim=True).clamp_min(1e-12))
    return torch.cat(parts, dim=0)


@dataclass(frozen=True)
class SieveSelection:
    selected_indices: torch.Tensor
    clean_indices: torch.Tensor
    expanded_indices: torch.Tensor
    modified_labels: torch.Tensor
    mean_confidence: float


def select_sieve_samples(
    features: torch.Tensor,
    logits: torch.Tensor,
    labels: torch.Tensor,
    num_classes: int,
    neighbors: int = 100,
    xi: float = 1.0,
    zeta: float = 0.93,
) -> SieveSelection:
    probabilities = torch.softmax(logits, dim=1)
    confidence, prediction = probabilities.max(dim=1)
    modified = labels.clone()
    confident = confidence > zeta
    modified[confident] = prediction[confident]
    scores = balanced_knn_scores(
        features, modified, num_classes, neighbors, exclude_self=True
    )
    assigned = scores.gather(1, modified[:, None]).squeeze(1)
    consistency = assigned / scores.max(dim=1).values.clamp_min(1e-12)
    clean = torch.where(consistency >= xi)[0]
    expanded = torch.where((consistency < xi) & (confidence >= zeta))[0]
    modified[expanded] = prediction[expanded]
    selected = torch.unique(torch.cat([clean, expanded]), sorted=True)
    if selected.numel() == 0:
        selected = torch.where(confidence >= zeta)[0]
    if selected.numel() == 0:
        selected = torch.arange(features.shape[0], device=features.device)
    return SieveSelection(
        selected_indices=selected,
        clean_indices=clean,
        expanded_indices=expanded,
        modified_labels=modified,
        mean_confidence=float(confidence.mean().detach().cpu()),
    )


class SieveMahalanobis:
    """Class-conditional pseudoinverse Mahalanobis used by Sieve."""

    def __init__(self):
        self.global_mean: np.ndarray | None = None
        self.global_std: np.ndarray | None = None
        self.classes: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        features = np.asarray(features, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        self.global_mean = features.mean(axis=0)
        self.global_std = features.std(axis=0)
        self.global_std[self.global_std < 1e-10] = 1.0
        standardized = (features - self.global_mean) / self.global_std
        self.classes = []
        for label in sorted(np.unique(labels)):
            values = standardized[labels == label]
            mean = values.mean(axis=0)
            centered = values - mean
            if len(values) < 2 or not np.any(centered):
                self.classes.append(
                    (mean, np.zeros((0, values.shape[1])), np.zeros(0))
                )
                continue
            _, singular, right = np.linalg.svd(centered, full_matrices=False)
            tolerance = np.finfo(np.float64).eps * max(centered.shape) * singular[0]
            keep = singular > tolerance
            components = right[keep]
            inverse_variance = len(values) / np.square(singular[keep])
            self.classes.append((mean, components, inverse_variance))

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.global_mean is None or self.global_std is None or not self.classes:
            raise RuntimeError("SieveMahalanobis has not been fitted")
        values = (np.asarray(features, dtype=np.float64) - self.global_mean) / self.global_std
        distances = []
        for mean, components, inverse_variance in self.classes:
            centered = values - mean
            if components.shape[0] == 0:
                distances.append(np.zeros(len(values)))
            else:
                projected = centered @ components.T
                distances.append(np.sum(np.square(projected) * inverse_variance, axis=1))
        return np.min(np.stack(distances, axis=1), axis=1)

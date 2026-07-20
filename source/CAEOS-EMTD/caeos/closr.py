from __future__ import annotations

import math
from typing import Dict, Sequence

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F


def _class_contrastive_loss(
    distance: Tensor,
    labels: Tensor,
    target_class: int,
    margin: float,
    squared: bool,
    alpha: float,
    eps: float = 1e-6,
) -> Tensor:
    """Class-head loss used by the official CLOSR implementation."""
    equal = labels[:, None].eq(labels[None, :])
    target_rows = labels[:, None].eq(int(target_class))
    similar = equal & target_rows
    dissimilar = (~equal) & target_rows

    similar_distance = distance.masked_select(similar)
    similar_distance = similar_distance[similar_distance > eps]
    if squared:
        similar_distance = similar_distance.square()
    similar_loss = (
        similar_distance.mean()
        if similar_distance.numel()
        else distance.sum() * 0.0
    )

    dissimilar_distance = distance.masked_select(dissimilar)
    dissimilar_loss = F.relu(float(margin) - dissimilar_distance)
    dissimilar_loss = dissimilar_loss[dissimilar_loss > eps]
    if squared:
        dissimilar_loss = dissimilar_loss.square()
    dissimilar_loss = (
        dissimilar_loss.mean()
        if dissimilar_loss.numel()
        else distance.sum() * 0.0
    )
    return float(alpha) * similar_loss + (1.0 - float(alpha)) * dissimilar_loss


def closr_loss(
    embeddings: Tensor,
    labels: Tensor,
    margin: float = 1.0,
    squared: bool = True,
    alpha: float = 0.5,
) -> Tensor:
    """CLOSR loss over class-specific unit-sphere embeddings."""
    if embeddings.ndim != 3:
        raise ValueError("CLOSR embeddings must have shape [batch, classes, dim]")
    normalized = F.normalize(embeddings, dim=-1)
    by_class = normalized.transpose(0, 1)
    similarity = torch.bmm(by_class, by_class.transpose(1, 2))
    distance = (1.0 - similarity) / 2.0
    losses = [
        _class_contrastive_loss(
            distance[index], labels, index, margin, squared, alpha
        )
        for index in range(embeddings.shape[1])
    ]
    return torch.stack(losses).mean()


class CLOSRClassifier(nn.Module):
    """Tabular adaptation of the official class-specific CLOSR MLP."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 1024,
        embedding_dim: int = 64,
        depth: int = 3,
        dropout: float = 0.1,
        margin: float = 1.0,
        squared: bool = True,
        alpha: float = 0.5,
    ) -> None:
        super().__init__()
        if depth < 1:
            raise ValueError("CLOSR depth must be positive")
        layers = []
        width = int(sum(input_dims))
        for _ in range(int(depth)):
            layers.extend(
                [
                    nn.Linear(width, int(hidden_dim)),
                    nn.ReLU(),
                    nn.Dropout(float(dropout)),
                ]
            )
            width = int(hidden_dim)
        self.encoder = nn.Sequential(*layers)
        self.projection = nn.Linear(
            int(hidden_dim), int(num_classes) * int(embedding_dim)
        )
        self.num_classes = int(num_classes)
        self.embedding_dim = int(embedding_dim)
        self.margin = float(margin)
        self.squared = bool(squared)
        self.alpha = float(alpha)
        self.register_buffer(
            "centroids", torch.zeros(self.num_classes, self.embedding_dim)
        )
        self.register_buffer("centroids_ready", torch.tensor(False))

    def forward(self, views: Sequence[Tensor], quality: Tensor = None) -> Dict[str, Tensor]:
        features = self.encoder(torch.cat(list(views), dim=-1))
        embedding = self.projection(features).reshape(
            len(features), self.num_classes, self.embedding_dim
        )
        embedding = F.normalize(embedding, dim=-1)
        if bool(self.centroids_ready.item()):
            logits = (embedding * self.centroids.unsqueeze(0)).sum(dim=-1)
        else:
            logits = torch.zeros(
                len(features), self.num_classes, device=features.device, dtype=features.dtype
            )
        return {"logits": logits, "embedding": embedding}

    def loss(self, output: Dict[str, Tensor], labels: Tensor) -> Tensor:
        return closr_loss(
            output["embedding"],
            labels,
            margin=self.margin,
            squared=self.squared,
            alpha=self.alpha,
        )

    @torch.no_grad()
    def fit_centroids(self, embeddings: np.ndarray, labels: np.ndarray) -> None:
        values = torch.as_tensor(
            embeddings, dtype=self.centroids.dtype, device=self.centroids.device
        )
        targets = torch.as_tensor(labels, dtype=torch.long, device=self.centroids.device)
        if values.ndim != 3 or values.shape[1:] != self.centroids.shape:
            raise ValueError("embedding shape does not match CLOSR class heads")
        centroids = []
        for class_index in range(self.num_classes):
            selected = values[targets == class_index, class_index]
            if not len(selected):
                raise ValueError(f"class {class_index} has no centroid samples")
            centroids.append(F.normalize(selected, dim=-1).mean(dim=0))
        self.centroids.copy_(F.normalize(torch.stack(centroids), dim=-1))
        self.centroids_ready.fill_(True)


def closr_risk(similarities: np.ndarray) -> np.ndarray:
    """Official CLOSR knownness converted to a risk where larger means unknown."""
    values = torch.as_tensor(similarities, dtype=torch.float64)
    probability = torch.softmax(values, dim=-1)
    knownness = (values.square() * probability).sum(dim=-1)
    return -knownness.numpy()


def warmup_cosine_learning_rate(
    step: int,
    total_steps: int,
    peak: float,
    floor: float = 1e-6,
    warmup_fraction: float = 0.1,
) -> float:
    """Official-style linear warmup followed by cosine decay."""
    total_steps = max(1, int(total_steps))
    warmup = max(1, int(total_steps * float(warmup_fraction)))
    step = min(max(0, int(step)), total_steps - 1)
    if step < warmup:
        fraction = step / max(1, warmup - 1)
        return float(floor + fraction * (peak - floor))
    progress = (step - warmup) / max(1, total_steps - warmup - 1)
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return float(floor + cosine * (peak - floor))


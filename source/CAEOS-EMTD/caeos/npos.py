from __future__ import annotations

from typing import Sequence

import torch
from torch import Tensor, nn

from .model import ViewEncoder


def normalize_rows(values: Tensor, epsilon: float = 1e-12) -> Tensor:
    if values.ndim != 2:
        raise ValueError("NPOS features must be a matrix")
    return values / values.norm(dim=1, keepdim=True).clamp_min(epsilon)


def synthesize_nonparametric_outliers(
    features: Tensor,
    *,
    neighbors: int,
    boundary_count: int,
    noise_count: int,
    outlier_count: int,
    covariance_scale: float,
) -> Tensor:
    """Generate NPOS boundary outliers without a parametric ID assumption."""

    if features.ndim != 2 or len(features) < 2:
        raise ValueError("NPOS synthesis requires at least two feature rows")
    if min(neighbors, boundary_count, noise_count, outlier_count) <= 0:
        raise ValueError("NPOS synthesis counts must be positive")
    if covariance_scale <= 0.0:
        raise ValueError("NPOS covariance scale must be positive")

    normalized = normalize_rows(features)
    pairwise = torch.cdist(normalized, normalized)
    pairwise.fill_diagonal_(float("inf"))
    effective_k = min(int(neighbors), len(features) - 1)
    kth_distance = pairwise.kthvalue(effective_k, dim=1).values
    boundary_size = min(int(boundary_count), len(features))
    boundary_indices = torch.topk(kth_distance, boundary_size).indices
    boundary = features[boundary_indices]

    anchor_indices = torch.randint(
        len(boundary), (int(noise_count),), device=features.device
    )
    candidates = boundary[anchor_indices] + float(covariance_scale) * torch.randn(
        int(noise_count), features.shape[1], device=features.device, dtype=features.dtype
    )
    candidate_distance = torch.cdist(normalize_rows(candidates), normalized)
    candidate_kth = candidate_distance.kthvalue(
        min(int(neighbors), len(features)), dim=1
    ).values
    selected = torch.topk(
        candidate_kth, min(int(outlier_count), len(candidates))
    ).indices
    return candidates[selected]


class ClassFeatureQueues:
    def __init__(self, class_count: int, capacity: int):
        if class_count <= 0 or capacity <= 1:
            raise ValueError("NPOS queue dimensions are invalid")
        self.class_count = int(class_count)
        self.capacity = int(capacity)
        self.values: list[Tensor | None] = [None] * self.class_count

    def update(self, features: Tensor, labels: Tensor) -> None:
        detached = features.detach()
        for class_index in labels.unique().tolist():
            index = int(class_index)
            if not 0 <= index < self.class_count:
                raise ValueError("NPOS queue label is outside the known class range")
            selected = detached[labels == index]
            existing = self.values[index]
            combined = selected if existing is None else torch.cat([existing, selected])
            self.values[index] = combined[-self.capacity :]

    def ready(self, minimum: int) -> bool:
        return all(value is not None and len(value) >= minimum for value in self.values)

    def counts(self) -> list[int]:
        return [0 if value is None else int(len(value)) for value in self.values]

    def synthesize(
        self,
        *,
        minimum: int,
        neighbors: int,
        boundary_count: int,
        noise_count: int,
        outlier_count: int,
        covariance_scale: float,
    ) -> Tensor:
        if not self.ready(minimum):
            raise RuntimeError("NPOS feature queues are not ready")
        generated = [
            synthesize_nonparametric_outliers(
                value,
                neighbors=neighbors,
                boundary_count=boundary_count,
                noise_count=noise_count,
                outlier_count=outlier_count,
                covariance_scale=covariance_scale,
            )
            for value in self.values
            if value is not None
        ]
        return torch.cat(generated)


class NPOSClassifier(nn.Module):
    """Shared tabular backbone with the official NPOS auxiliary ID head."""

    def __init__(
        self,
        input_dims: Sequence[int],
        class_count: int,
        hidden_dim: int = 256,
        embedding_dim: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = ViewEncoder(
            sum(input_dims), hidden_dim, embedding_dim, dropout
        )
        self.classifier = nn.Linear(embedding_dim, class_count)
        self.id_head = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(inplace=True),
            nn.Linear(embedding_dim, 1),
        )

    def forward(
        self, views: Sequence[Tensor], quality: Tensor | None = None
    ) -> dict[str, Tensor]:
        embedding = self.encoder(torch.cat(list(views), dim=-1))
        return {
            "logits": self.classifier(embedding),
            "embedding": embedding,
            "id_logit": self.id_head(embedding).squeeze(1),
        }

    def id_logits(self, embeddings: Tensor) -> Tensor:
        return self.id_head(embeddings).squeeze(1)

from __future__ import annotations

from typing import Sequence

import torch
from torch import Tensor, nn

from .model import ViewEncoder


def weighted_logsumexp(
    logits: Tensor, class_weights: Tensor, epsilon: float = 1e-12
) -> Tensor:
    """Official VOS weighted energy with a finite zero-weight safeguard."""

    if logits.ndim != 2:
        raise ValueError("VOS logits must be a matrix")
    weights = torch.relu(class_weights).reshape(1, -1)
    if weights.shape[1] != logits.shape[1]:
        raise ValueError("VOS energy weight count must match the class count")
    maximum = logits.max(dim=1, keepdim=True).values
    weighted = (weights * torch.exp(logits - maximum)).sum(dim=1)
    return maximum.squeeze(1) + torch.log(weighted.clamp_min(epsilon))


def lowest_likelihood_samples(
    distribution: torch.distributions.MultivariateNormal,
    candidates: Tensor,
    select: int,
) -> Tensor:
    if candidates.ndim != 2 or select <= 0 or select > len(candidates):
        raise ValueError("invalid VOS low-likelihood selection request")
    log_density = distribution.log_prob(candidates)
    indices = torch.topk(-log_density, int(select)).indices
    return candidates[indices]


class ClassConditionalGaussianQueue:
    """Per-class feature queues with the tied covariance used by VOS."""

    def __init__(self, class_count: int, capacity: int):
        if class_count <= 0 or capacity <= 1:
            raise ValueError("VOS queue dimensions are invalid")
        self.class_count = int(class_count)
        self.capacity = int(capacity)
        self.values: list[Tensor | None] = [None] * self.class_count

    def update(self, features: Tensor, labels: Tensor) -> None:
        detached = features.detach().float()
        for class_index in labels.unique().tolist():
            index = int(class_index)
            if not 0 <= index < self.class_count:
                raise ValueError("VOS queue label is outside the known class range")
            selected = detached[labels == index]
            existing = self.values[index]
            combined = selected if existing is None else torch.cat([existing, selected])
            self.values[index] = combined[-self.capacity :]

    def ready(self, minimum: int | None = None) -> bool:
        required = self.capacity if minimum is None else int(minimum)
        if required <= 1 or required > self.capacity:
            raise ValueError("VOS queue readiness threshold is invalid")
        return all(value is not None and len(value) >= required for value in self.values)

    def counts(self) -> list[int]:
        return [0 if value is None else int(len(value)) for value in self.values]

    def statistics(self, ridge: float) -> tuple[Tensor, Tensor]:
        if ridge <= 0.0:
            raise ValueError("VOS covariance ridge must be positive")
        if not self.ready():
            raise RuntimeError("VOS feature queues are not full")
        queued = [value for value in self.values if value is not None]
        means = torch.stack([value.mean(dim=0) for value in queued])
        centered = torch.cat(
            [value - mean for value, mean in zip(queued, means)], dim=0
        )
        covariance = centered.T @ centered / float(len(centered))
        covariance = covariance + float(ridge) * torch.eye(
            covariance.shape[0], device=covariance.device, dtype=covariance.dtype
        )
        if not torch.isfinite(covariance).all():
            raise RuntimeError("VOS covariance is non-finite")
        _, info = torch.linalg.cholesky_ex(covariance)
        if int(info.max().item()) != 0:
            raise RuntimeError("VOS covariance is not positive definite")
        return means, covariance

    @torch.no_grad()
    def synthesize(self, *, sample_from: int, select: int, ridge: float) -> Tensor:
        if sample_from <= 0 or select <= 0 or select > sample_from:
            raise ValueError("VOS synthesis counts are invalid")
        means, covariance = self.statistics(ridge)
        samples = []
        for mean in means:
            distribution = torch.distributions.MultivariateNormal(
                mean, covariance_matrix=covariance
            )
            candidates = distribution.rsample((int(sample_from),))
            samples.append(lowest_likelihood_samples(distribution, candidates, select))
        return torch.cat(samples, dim=0)


class VOSClassifier(nn.Module):
    """Shared tabular backbone with the VOS weighted-energy branch."""

    def __init__(
        self,
        input_dims: Sequence[int],
        class_count: int,
        hidden_dim: int = 256,
        embedding_dim: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = ViewEncoder(sum(input_dims), hidden_dim, embedding_dim, dropout)
        self.classifier = nn.Linear(embedding_dim, class_count)
        self.energy_weights = nn.Parameter(torch.empty(1, class_count))
        nn.init.uniform_(self.energy_weights)
        self.energy_discriminator = nn.Linear(1, 2)

    def classify_embedding(self, embedding: Tensor) -> Tensor:
        return self.classifier(embedding)

    def energy(self, logits: Tensor) -> Tensor:
        return weighted_logsumexp(logits, self.energy_weights)

    def discriminate_energy(self, energy: Tensor) -> Tensor:
        return self.energy_discriminator(energy.reshape(-1, 1))

    def forward(
        self, views: Sequence[Tensor], quality: Tensor | None = None
    ) -> dict[str, Tensor]:
        embedding = self.encoder(torch.cat(list(views), dim=-1))
        logits = self.classify_embedding(embedding)
        return {
            "logits": logits,
            "embedding": embedding,
            "weighted_energy": self.energy(logits),
        }

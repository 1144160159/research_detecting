from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F


def contrastive_pair_loss(
    embedding: Tensor,
    labels: Tensor,
    margin: float = 10.0,
    similar_ratio: float = 0.25,
) -> Tensor:
    """CADE pair loss with half of the batch acting as anchors.

    The official sampler builds a batch from ``B/2`` anchors and ``B/2``
    partners. ``similar_ratio=0.25`` therefore makes half of the pairs
    similar and half dissimilar. Partners are selected inside the current
    class-balanced batch to avoid a second host-side sampling pipeline.
    """
    if embedding.ndim != 2 or labels.ndim != 1:
        raise ValueError("CADE embedding and labels must be two- and one-dimensional")
    if len(embedding) != len(labels):
        raise ValueError("CADE embedding and labels must contain the same samples")
    pair_count = len(embedding) // 2
    if pair_count < 1:
        return embedding.sum() * 0.0

    anchors = torch.arange(pair_count, device=embedding.device)
    similar_count = min(pair_count, max(0, int(len(embedding) * similar_ratio)))
    require_similar = torch.arange(pair_count, device=embedding.device) < similar_count
    equal = labels[anchors, None].eq(labels[None, :])
    valid = torch.where(require_similar[:, None], equal, ~equal)

    # Prefer a different sample for positive pairs, but retain self as a
    # fallback for a singleton class in a small final batch.
    valid[torch.arange(pair_count, device=embedding.device), anchors] = False
    empty = ~valid.any(dim=1)
    if empty.any():
        fallback = torch.where(require_similar[:, None], equal, ~equal)
        valid[empty] = fallback[empty]
    random_priority = torch.rand(
        valid.shape, device=embedding.device, dtype=embedding.dtype
    ).masked_fill(~valid, -1.0)
    partners = random_priority.argmax(dim=1)

    distance = torch.linalg.vector_norm(
        embedding[anchors] - embedding[partners], dim=1
    )
    pair_loss = torch.where(
        require_similar,
        distance,
        F.relu(float(margin) - distance),
    )
    return pair_loss.mean()


class CADEClassifier(nn.Module):
    """PyTorch adaptation of CADE's contrastive AE and target MLP."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dims: Sequence[int] = (64, 32, 16),
        classifier_hidden: int = 30,
        classifier_dropout: float = 0.2,
        contrast_weight: float = 0.1,
        margin: float = 10.0,
        similar_ratio: float = 0.25,
    ) -> None:
        super().__init__()
        input_dim = int(sum(input_dims))
        hidden_dims = tuple(int(value) for value in hidden_dims)
        if not hidden_dims or min(hidden_dims) < 1:
            raise ValueError("CADE hidden dimensions must be positive")

        encoder_layers: list[nn.Module] = []
        width = input_dim
        for index, hidden in enumerate(hidden_dims):
            encoder_layers.append(nn.Linear(width, hidden))
            if index < len(hidden_dims) - 1:
                encoder_layers.append(nn.ReLU())
            width = hidden
        self.encoder = nn.Sequential(*encoder_layers)

        decoder_layers: list[nn.Module] = []
        decoder_widths = tuple(reversed(hidden_dims[:-1])) + (input_dim,)
        for index, hidden in enumerate(decoder_widths):
            decoder_layers.append(nn.Linear(width, hidden))
            if index < len(decoder_widths) - 1:
                decoder_layers.append(nn.ReLU())
            width = hidden
        self.decoder = nn.Sequential(*decoder_layers)

        self.classifier = nn.Sequential(
            nn.Linear(input_dim, int(classifier_hidden)),
            nn.ReLU(),
            nn.Dropout(float(classifier_dropout)),
            nn.Linear(int(classifier_hidden), int(num_classes)),
        )
        self.contrast_weight = float(contrast_weight)
        self.margin = float(margin)
        self.similar_ratio = float(similar_ratio)

    def forward(
        self, views: Sequence[Tensor], quality: Tensor = None
    ) -> Dict[str, Tensor]:
        features = torch.cat(list(views), dim=-1)
        embedding = self.encoder(features)
        return {
            "logits": self.classifier(features),
            "embedding": embedding,
            "reconstruction": self.decoder(embedding),
            "features": features,
        }

    def autoencoder_loss(self, output: Dict[str, Tensor], labels: Tensor) -> Tensor:
        reconstruction = F.mse_loss(output["reconstruction"], output["features"])
        contrastive = contrastive_pair_loss(
            output["embedding"], labels, self.margin, self.similar_ratio
        )
        return reconstruction + self.contrast_weight * contrastive

    def autoencoder_parameters(self):
        yield from self.encoder.parameters()
        yield from self.decoder.parameters()


class CADECalibrator:
    """Class-centroid MAD risk from the original CADE detector."""

    def __init__(self, epsilon: float = 1e-6) -> None:
        self.epsilon = float(epsilon)
        self.centroids: np.ndarray | None = None
        self.distance_medians: np.ndarray | None = None
        self.distance_mads: np.ndarray | None = None

    def fit(self, embedding: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(embedding, dtype=np.float64)
        targets = np.asarray(labels, dtype=np.int64)
        classes = np.arange(int(targets.max()) + 1)
        centroids = []
        medians = []
        mads = []
        for class_index in classes:
            selected = values[targets == class_index]
            if not len(selected):
                raise ValueError(f"class {class_index} has no CADE fitting samples")
            centroid = selected.mean(axis=0)
            distance = np.linalg.norm(selected - centroid, axis=1)
            median = float(np.median(distance))
            mad = float(1.4826 * np.median(np.abs(distance - median)))
            centroids.append(centroid)
            medians.append(median)
            mads.append(max(mad, self.epsilon))
        self.centroids = np.stack(centroids)
        self.distance_medians = np.asarray(medians)
        self.distance_mads = np.asarray(mads)

    def score(self, embedding: np.ndarray) -> np.ndarray:
        if (
            self.centroids is None
            or self.distance_medians is None
            or self.distance_mads is None
        ):
            raise RuntimeError("CADE calibrator has not been fitted")
        values = np.asarray(embedding, dtype=np.float64)
        distance = np.linalg.norm(
            values[:, None, :] - self.centroids[None, :, :], axis=2
        )
        anomaly = np.abs(distance - self.distance_medians[None, :])
        anomaly /= self.distance_mads[None, :]
        return anomaly.min(axis=1)

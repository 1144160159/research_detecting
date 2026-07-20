from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F


class OpenDetectClassifier(nn.Module):
    """Tabular adaptation of Open-Detect's Gaussian-prototype VAE.

    The original method uses a ResNet VAE over 32x32 flow images. This
    adaptation retains its Gaussian prototypes, reconstruction constraint,
    class-conditional KL constraint and discriminative prototype loss while
    replacing only the image encoder/decoder with MLPs for the shared CAEOS
    side-channel feature protocol.
    """

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 256,
        latent_dim: int = 128,
        dropout: float = 0.1,
        temperature: float = 1.0,
        generative_weight: float = 0.005,
    ) -> None:
        super().__init__()
        input_dim = int(sum(input_dims))
        if input_dim < 1 or num_classes < 2:
            raise ValueError("Open-Detect requires positive inputs and at least two classes")
        if hidden_dim < 2 or latent_dim < 2:
            raise ValueError("Open-Detect hidden and latent dimensions must exceed one")
        if temperature <= 0:
            raise ValueError("Open-Detect temperature must be positive")
        if not 0.0 <= generative_weight <= 1.0:
            raise ValueError("Open-Detect generative weight must be in [0, 1]")

        bottleneck = max(latent_dim, hidden_dim // 2)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(float(dropout)),
            nn.Linear(hidden_dim, bottleneck),
            nn.ReLU(),
        )
        self.mean = nn.Linear(bottleneck, latent_dim)
        self.log_variance = nn.Linear(bottleneck, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, bottleneck),
            nn.ReLU(),
            nn.Linear(bottleneck, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )
        self.prototypes = nn.Parameter(torch.empty(num_classes, latent_dim))
        nn.init.kaiming_normal_(self.prototypes)
        self.num_classes = int(num_classes)
        self.temperature = float(temperature)
        self.generative_weight = float(generative_weight)

    @staticmethod
    def squared_distance(values: Tensor, prototypes: Tensor) -> Tensor:
        return (
            values.square().sum(dim=1, keepdim=True)
            + prototypes.square().sum(dim=1).unsqueeze(0)
            - 2.0 * values @ prototypes.t()
        ).clamp_min(0.0)

    def _encode(self, features: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        hidden = self.encoder(features)
        mean = self.mean(hidden)
        log_variance = self.log_variance(hidden).clamp(-10.0, 10.0)
        if self.training:
            embedding = mean + torch.exp(0.5 * log_variance) * torch.randn_like(mean)
        else:
            embedding = mean
        return embedding, mean, log_variance

    def forward(
        self, views: Sequence[Tensor], quality: Tensor = None
    ) -> Dict[str, Tensor]:
        features = torch.cat(list(views), dim=-1)
        embedding, mean, log_variance = self._encode(features)
        distance = self.squared_distance(embedding, self.prototypes)
        variance_term = (
            log_variance.exp() - log_variance - 1.0
        ).sum(dim=1, keepdim=True)
        class_kl = 0.5 * (
            self.squared_distance(mean, self.prototypes) + variance_term
        )
        logits = -class_kl / self.temperature
        return {
            "logits": logits,
            "embedding": mean,
            "sampled_embedding": embedding,
            "class_kl": class_kl,
            "distance": distance,
            "reconstruction": self.decoder(embedding),
            "features": features,
        }

    def loss(self, output: Dict[str, Tensor], labels: Tensor) -> Tensor:
        selected_kl = output["class_kl"].gather(1, labels[:, None]).mean()
        reconstruction = F.mse_loss(output["reconstruction"], output["features"])
        discriminative = F.cross_entropy(output["logits"], labels)
        generative = reconstruction + selected_kl
        return (
            self.generative_weight * generative
            + (1.0 - self.generative_weight) * discriminative
        )

    @torch.no_grad()
    def reset_prototypes(self, embedding: np.ndarray, labels: np.ndarray) -> None:
        values = torch.as_tensor(
            embedding, dtype=self.prototypes.dtype, device=self.prototypes.device
        )
        targets = torch.as_tensor(labels, dtype=torch.long, device=values.device)
        updated = []
        for class_index in range(self.num_classes):
            selected = values[targets == class_index]
            if not len(selected):
                raise ValueError(f"class {class_index} has no prototype samples")
            updated.append(selected.mean(dim=0))
        self.prototypes.copy_(torch.stack(updated))


def open_detect_risk(logits: np.ndarray) -> np.ndarray:
    """Minimum class-conditional KL, oriented so larger means more unknown."""

    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("Open-Detect logits must be a two-dimensional array")
    return -values.max(axis=1)

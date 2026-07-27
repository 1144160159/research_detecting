from __future__ import annotations

from typing import Dict, Optional, Sequence

import torch
import torch.nn.functional as F
from torch import Tensor, nn

from .model import ViewEncoder


class MEDAFTabularExpert(nn.Module):
    def __init__(
        self,
        embedding_dim: int,
        num_classes: int,
        dropout: float,
    ) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.classifier = nn.Linear(embedding_dim, num_classes, bias=False)

    def forward(
        self, shared: Tensor, labels: Optional[Tensor] = None
    ) -> Dict[str, Tensor]:
        embedding = self.encoder(shared)
        logits = self.classifier(embedding)
        result = {"embedding": embedding, "logits": logits}
        if labels is not None:
            class_weight = self.classifier.weight.index_select(0, labels)
            result["class_activation"] = embedding * class_weight
        return result


class MEDAFTabularClassifier(nn.Module):
    """Strict-v4 tabular adapter for MEDAF's three-expert gated classifier."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        gate_temperature: float = 100.0,
        num_experts: int = 3,
    ) -> None:
        super().__init__()
        if int(num_experts) != 3:
            raise ValueError("MEDAF source contract requires exactly three experts")
        if float(gate_temperature) <= 0.0:
            raise ValueError("gate temperature must be positive")
        input_dim = int(sum(input_dims))
        self.shared_encoder = ViewEncoder(
            input_dim, hidden_dim, embedding_dim, dropout
        )
        self.experts = nn.ModuleList(
            MEDAFTabularExpert(embedding_dim, num_classes, dropout)
            for _ in range(num_experts)
        )
        # The official gate has its own copied feature extractor.
        self.gate_encoder = ViewEncoder(
            input_dim, hidden_dim, embedding_dim, dropout
        )
        self.gate_head = nn.Sequential(
            nn.Linear(embedding_dim, max(4, embedding_dim // 4)),
            nn.Linear(max(4, embedding_dim // 4), num_experts),
        )
        self.gate_temperature = float(gate_temperature)
        self.num_classes = int(num_classes)
        self.num_experts = int(num_experts)

    def forward(
        self,
        views: Sequence[Tensor],
        quality: Optional[Tensor] = None,
        labels: Optional[Tensor] = None,
    ) -> Dict[str, Tensor]:
        del quality
        values = torch.cat(tuple(views), dim=-1)
        shared = self.shared_encoder(values)
        expert_values = [expert(shared, labels) for expert in self.experts]
        expert_logits = torch.stack(
            [value["logits"] for value in expert_values], dim=1
        )
        gate_embedding = self.gate_encoder(values)
        gate_weights = F.softmax(
            self.gate_head(gate_embedding) / self.gate_temperature,
            dim=1,
        )
        gated_logits = (
            expert_logits.detach() * gate_weights.unsqueeze(-1)
        ).sum(dim=1)
        result = {
            "logits": gated_logits,
            "gated_logits": gated_logits,
            "expert_logits": expert_logits,
            "gate_weights": gate_weights,
            "embedding": shared,
            "expert_embeddings": torch.stack(
                [value["embedding"] for value in expert_values], dim=1
            ),
        }
        if labels is not None:
            result["class_activation_maps"] = torch.stack(
                [value["class_activation"] for value in expert_values],
                dim=1,
            )
        return result


def official_attention_diversity(class_activation_maps: Tensor) -> Tensor:
    """Match MEDAF's centered positive CAM pairwise cosine sum."""

    if class_activation_maps.ndim != 3:
        raise ValueError(
            "class activation maps must have [batch, experts, positions]"
        )
    if class_activation_maps.shape[1] != 3:
        raise ValueError("MEDAF diversity requires exactly three experts")
    maps = F.normalize(class_activation_maps, p=2, dim=-1)
    maps = F.relu(maps - maps.mean(dim=-1, keepdim=True))
    loss = maps.new_tensor(0.0)
    for left in range(3):
        for right in range(left + 1, 3):
            loss = loss + F.cosine_similarity(
                maps[:, left, :],
                maps[:, right, :],
                dim=-1,
                eps=1e-6,
            ).mean()
    return loss


def medaf_training_loss(
    output: Dict[str, Tensor],
    labels: Tensor,
    expert_weight: float = 0.7,
    gate_weight: float = 1.0,
    diversity_weight: float = 0.01,
) -> Dict[str, Tensor]:
    expert_losses = torch.stack(
        [
            F.cross_entropy(output["expert_logits"][:, index, :], labels)
            for index in range(output["expert_logits"].shape[1])
        ]
    )
    gate_loss = F.cross_entropy(output["gated_logits"], labels)
    diversity = official_attention_diversity(
        output["class_activation_maps"]
    )
    total = (
        float(expert_weight) * expert_losses.sum()
        + float(gate_weight) * gate_loss
        + float(diversity_weight) * diversity
    )
    return {
        "total": total,
        "expert_cross_entropy": expert_losses,
        "gate_cross_entropy": gate_loss,
        "attention_diversity": diversity,
    }


def medaf_probabilities(
    output: Dict[str, Tensor], logit_temperature: float = 100.0
) -> Tensor:
    if float(logit_temperature) <= 0.0:
        raise ValueError("logit temperature must be positive")
    return F.softmax(
        output["gated_logits"] / float(logit_temperature), dim=-1
    )


def medaf_risk(
    output: Dict[str, Tensor], logit_temperature: float = 100.0
) -> Tensor:
    probability = medaf_probabilities(output, logit_temperature)
    return 1.0 - probability.max(dim=-1).values

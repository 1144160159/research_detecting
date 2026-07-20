from __future__ import annotations

from typing import Dict, Sequence, Tuple

import numpy as np
import torch
from torch import Tensor, nn
import torch.nn.functional as F

from .losses import evidential_classification_loss
from .model import ViewEncoder


def evidence_to_opinion(evidence: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
    """Map non-negative evidence to RoNeTC's Dirichlet opinion."""
    if evidence.ndim < 2:
        raise ValueError("evidence must include batch and class dimensions")
    classes = evidence.shape[-1]
    alpha = evidence + 1.0
    strength = alpha.sum(dim=-1, keepdim=True)
    belief = evidence / strength
    uncertainty = evidence.new_tensor(float(classes)) / strength
    return alpha, belief, uncertainty


def dempster_shafer_combine(
    first_belief: Tensor,
    first_uncertainty: Tensor,
    second_belief: Tensor,
    second_uncertainty: Tensor,
    eps: float = 1e-8,
) -> Tuple[Tensor, Tensor, Tensor]:
    """Combine two multinomial opinions using RoNeTC equations (5)-(7)."""
    if first_belief.shape != second_belief.shape:
        raise ValueError("belief tensors must have identical shapes")
    if first_uncertainty.shape != first_belief.shape[:-1] + (1,):
        raise ValueError("first uncertainty must have a singleton class dimension")
    if second_uncertainty.shape != second_belief.shape[:-1] + (1,):
        raise ValueError("second uncertainty must have a singleton class dimension")

    committed_product = first_belief.sum(dim=-1, keepdim=True) * second_belief.sum(
        dim=-1, keepdim=True
    )
    agreement = (first_belief * second_belief).sum(dim=-1, keepdim=True)
    conflict = (committed_product - agreement).clamp(0.0, 1.0)
    normalizer = (1.0 - conflict).clamp_min(eps)
    belief = (
        first_belief * second_belief
        + first_belief * second_uncertainty
        + second_belief * first_uncertainty
    ) / normalizer
    uncertainty = first_uncertainty * second_uncertainty / normalizer

    # Floating-point drift is possible after sequential fusion.
    total = (belief.sum(dim=-1, keepdim=True) + uncertainty).clamp_min(eps)
    return belief / total, uncertainty / total, conflict.squeeze(-1)


class RoNeTCClassifier(nn.Module):
    """RoNeTC opinion mechanism adapted to shared tabular side-channel views.

    The paper's CNN/Transformer byte extractor is replaced by one MLP encoder per
    configured feature view. Its evidence generation, Dirichlet opinions, joint
    loss, Dempster-Shafer fusion, and uncertainty score are retained.
    """

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        annealing_epochs: int = 10,
    ):
        super().__init__()
        if len(input_dims) < 2:
            raise ValueError("RoNeTC requires at least two views")
        if num_classes < 2:
            raise ValueError("RoNeTC requires at least two known classes")
        self.num_classes = int(num_classes)
        self.annealing_epochs = int(annealing_epochs)
        self.encoders = nn.ModuleList(
            ViewEncoder(dim, hidden_dim, embedding_dim, dropout) for dim in input_dims
        )
        self.evidence_heads = nn.ModuleList(
            nn.Linear(embedding_dim, num_classes) for _ in input_dims
        )

    def forward(
        self, views: Sequence[Tensor], quality: Tensor | None = None
    ) -> Dict[str, Tensor]:
        if len(views) != len(self.encoders):
            raise ValueError("number of views does not match the model")
        embeddings = [encoder(view) for encoder, view in zip(self.encoders, views)]
        view_evidence = torch.stack(
            [
                F.softplus(head(embedding))
                for head, embedding in zip(self.evidence_heads, embeddings)
            ],
            dim=1,
        )
        view_alpha, view_belief, view_uncertainty = evidence_to_opinion(view_evidence)

        joint_belief = view_belief[:, 0]
        joint_uncertainty = view_uncertainty[:, 0]
        conflicts = []
        for index in range(1, view_belief.shape[1]):
            joint_belief, joint_uncertainty, conflict = dempster_shafer_combine(
                joint_belief,
                joint_uncertainty,
                view_belief[:, index],
                view_uncertainty[:, index],
            )
            conflicts.append(conflict)

        joint_strength = self.num_classes / joint_uncertainty.clamp_min(1e-8)
        joint_evidence = joint_belief * joint_strength
        joint_alpha = joint_evidence + 1.0
        probability = joint_alpha / joint_alpha.sum(dim=-1, keepdim=True)
        embedding = torch.stack(embeddings, dim=1).mean(dim=1)
        sequential_conflict = torch.stack(conflicts, dim=1)
        return {
            "logits": torch.log(probability.clamp_min(1e-8)),
            "embedding": embedding,
            "view_evidence": view_evidence,
            "view_alpha": view_alpha,
            "view_belief": view_belief,
            "view_uncertainty": view_uncertainty.squeeze(-1),
            "joint_evidence": joint_evidence,
            "joint_alpha": joint_alpha,
            "joint_belief": joint_belief,
            "joint_uncertainty": joint_uncertainty.squeeze(-1),
            "sequential_conflict": sequential_conflict,
        }

    def loss(self, output: Dict[str, Tensor], targets: Tensor, epoch: int) -> Tensor:
        view_losses = [
            evidential_classification_loss(
                output["view_alpha"][:, index],
                targets,
                epoch,
                self.annealing_epochs,
            )
            for index in range(output["view_alpha"].shape[1])
        ]
        joint_loss = evidential_classification_loss(
            output["joint_alpha"], targets, epoch, self.annealing_epochs
        )
        return torch.stack(view_losses).sum() + joint_loss


def ronetc_risk(joint_uncertainty: np.ndarray) -> np.ndarray:
    """Use RoNeTC's joint opinion uncertainty as the unknown risk."""
    values = np.asarray(joint_uncertainty, dtype=np.float64).reshape(-1)
    if not np.isfinite(values).all():
        raise ValueError("RoNeTC uncertainty contains non-finite values")
    return values

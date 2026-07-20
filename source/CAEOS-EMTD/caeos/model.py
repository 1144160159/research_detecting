from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import torch
from torch import Tensor, nn
import torch.nn.functional as F


def evidence_to_opinion(evidence: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
    """Convert non-negative class evidence to Dirichlet belief and uncertainty."""
    num_classes = evidence.shape[-1]
    alpha = evidence + 1.0
    strength = alpha.sum(dim=-1, keepdim=True)
    belief = evidence / strength
    uncertainty = evidence.new_tensor(float(num_classes)) / strength
    return alpha, belief, uncertainty


def pairwise_conflict(
    beliefs: Tensor, reliabilities: Tensor
) -> Tuple[Tensor, Tensor, Tensor, Tensor]:
    """Compute raw/effective pairwise conflict for B x M x K opinions."""
    if beliefs.ndim != 3:
        raise ValueError("beliefs must have shape [batch, modalities, classes]")
    if reliabilities.shape != beliefs.shape[:2]:
        raise ValueError("reliabilities must have shape [batch, modalities]")

    committed_mass = beliefs.sum(dim=-1)
    agreement = torch.bmm(beliefs, beliefs.transpose(1, 2))
    committed_product = committed_mass.unsqueeze(2) * committed_mass.unsqueeze(1)
    disagreement_mass = (committed_product - agreement).clamp_min(0.0)
    raw = torch.where(
        committed_product > 1e-8,
        disagreement_mass / committed_product.clamp_min(1e-8),
        torch.zeros_like(disagreement_mass),
    ).clamp(0.0, 1.0)

    num_modalities = beliefs.shape[1]
    eye = torch.eye(num_modalities, device=beliefs.device, dtype=beliefs.dtype)
    off_diag = 1.0 - eye.unsqueeze(0)
    raw = raw * off_diag

    pair_reliability = reliabilities.unsqueeze(2) * reliabilities.unsqueeze(1)
    effective = raw * pair_reliability * off_diag
    global_conflict = effective.sum(dim=(1, 2)) / (
        (pair_reliability * off_diag).sum(dim=(1, 2)) + 1e-8
    )

    other_reliability = (
        reliabilities.sum(dim=1, keepdim=True) - reliabilities
    ).clamp_min(1e-8)
    per_modality = effective.sum(dim=2) / other_reliability
    return raw, effective, global_conflict, per_modality


class ViewEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, embedding_dim: int, dropout: float):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.GELU(),
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.network(x)


class ConflictAwareEvidentialNet(nn.Module):
    """Multi-view classifier with evidential opinions and conflict-aware fusion."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        conflict_scale: float = 2.0,
        fusion_mode: str = "conflict",
    ):
        super().__init__()
        if len(input_dims) < 2:
            raise ValueError("at least two modalities are required")
        self.input_dims = list(input_dims)
        self.num_modalities = len(input_dims)
        self.num_classes = num_classes
        self.embedding_dim = embedding_dim
        self.conflict_scale = conflict_scale
        if fusion_mode not in {"sum", "reliability", "conflict"}:
            raise ValueError("fusion_mode must be sum, reliability, or conflict")
        self.fusion_mode = fusion_mode

        self.encoders = nn.ModuleList(
            ViewEncoder(dim, hidden_dim, embedding_dim, dropout) for dim in input_dims
        )
        self.evidence_heads = nn.ModuleList(
            nn.Linear(embedding_dim, num_classes) for _ in input_dims
        )
        self.reliability_heads = nn.ModuleList(
            nn.Sequential(
                nn.Linear(embedding_dim + 2, embedding_dim // 2),
                nn.GELU(),
                nn.Linear(embedding_dim // 2, 1),
            )
            for _ in input_dims
        )
        self.projections = nn.ModuleList(
            nn.Linear(embedding_dim, embedding_dim) for _ in input_dims
        )
        self.class_centers = nn.Parameter(torch.randn(num_classes, embedding_dim) * 0.05)
        self.malicious_head = nn.Linear(embedding_dim, 1)

    def forward(
        self, views: Sequence[Tensor], quality: Optional[Tensor] = None
    ) -> Dict[str, Tensor]:
        if len(views) != self.num_modalities:
            raise ValueError("number of input views does not match model configuration")
        batch_size = views[0].shape[0]
        if quality is None:
            quality = views[0].new_ones((batch_size, self.num_modalities))
        if quality.shape != (batch_size, self.num_modalities):
            raise ValueError("quality must have shape [batch, modalities]")

        embeddings: List[Tensor] = []
        evidences: List[Tensor] = []
        beliefs: List[Tensor] = []
        uncertainties: List[Tensor] = []
        reliability_logits: List[Tensor] = []
        reliabilities: List[Tensor] = []

        for index, (view, encoder, evidence_head, reliability_head) in enumerate(
            zip(views, self.encoders, self.evidence_heads, self.reliability_heads)
        ):
            embedding = encoder(view)
            evidence = F.softplus(evidence_head(embedding))
            _, belief, uncertainty = evidence_to_opinion(evidence)
            reliability_input = torch.cat(
                [embedding, uncertainty.detach(), quality[:, index : index + 1]], dim=-1
            )
            reliability_logit = reliability_head(reliability_input).squeeze(-1)
            reliability = torch.sigmoid(reliability_logit)
            embeddings.append(embedding)
            evidences.append(evidence)
            beliefs.append(belief)
            uncertainties.append(uncertainty.squeeze(-1))
            reliability_logits.append(reliability_logit)
            reliabilities.append(reliability)

        evidence_tensor = torch.stack(evidences, dim=1)
        belief_tensor = torch.stack(beliefs, dim=1)
        uncertainty_tensor = torch.stack(uncertainties, dim=1)
        reliability_tensor = torch.stack(reliabilities, dim=1)

        raw_conflict, effective_conflict, global_conflict, modality_conflict = (
            pairwise_conflict(belief_tensor, reliability_tensor)
        )
        if self.fusion_mode == "sum":
            discounts = torch.ones_like(reliability_tensor)
        elif self.fusion_mode == "reliability":
            discounts = reliability_tensor
        else:
            discounts = reliability_tensor * torch.exp(
                -self.conflict_scale * modality_conflict
            )

        fused_evidence = (discounts.unsqueeze(-1) * evidence_tensor).sum(dim=1)
        fused_alpha, fused_belief, fused_uncertainty = evidence_to_opinion(fused_evidence)
        fused_probability = fused_alpha / fused_alpha.sum(dim=-1, keepdim=True)

        projected = torch.stack(
            [projection(embedding) for projection, embedding in zip(self.projections, embeddings)],
            dim=1,
        )
        normalized_discount = discounts / (discounts.sum(dim=1, keepdim=True) + 1e-8)
        fused_embedding = (normalized_discount.unsqueeze(-1) * projected).sum(dim=1)
        malicious_logit = self.malicious_head(fused_embedding).squeeze(-1)

        return {
            "embeddings": torch.stack(embeddings, dim=1),
            "evidence": evidence_tensor,
            "belief": belief_tensor,
            "uncertainty": uncertainty_tensor,
            "reliability_logit": torch.stack(reliability_logits, dim=1),
            "reliability": reliability_tensor,
            "raw_conflict": raw_conflict,
            "effective_conflict": effective_conflict,
            "global_conflict": global_conflict,
            "modality_conflict": modality_conflict,
            "discount": discounts,
            "fused_evidence": fused_evidence,
            "fused_alpha": fused_alpha,
            "fused_belief": fused_belief,
            "fused_probability": fused_probability,
            "fused_uncertainty": fused_uncertainty.squeeze(-1),
            "fused_embedding": fused_embedding,
            "malicious_logit": malicious_logit,
            "class_centers": self.class_centers,
        }

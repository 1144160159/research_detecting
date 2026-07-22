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


class TlsHandshakeEncoder(nn.Module):
    """Gated encoder for the mixed continuous/discrete TLS handshake vector."""

    def __init__(self, input_dim: int, hidden_dim: int, embedding_dim: int, dropout: float):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 2 * hidden_dim),
            nn.GLU(dim=-1),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.GELU(),
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.network(x)


class PacketSequenceTCNEncoder(nn.Module):
    """Temporal convolution encoder for an ordered packet-side-channel vector."""

    def __init__(self, input_dim: int, hidden_dim: int, embedding_dim: int, dropout: float):
        super().__init__()
        if input_dim < 3:
            raise ValueError("packet sequence encoder requires at least three positions")
        channels = max(8, min(int(hidden_dim), 64))
        self.temporal = nn.Sequential(
            nn.Conv1d(1, channels, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Conv1d(channels, channels, kernel_size=3, padding=2, dilation=2),
            nn.GELU(),
        )
        self.projection = nn.Sequential(
            nn.Linear(2 * channels, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.GELU(),
        )

    def forward(self, x: Tensor) -> Tensor:
        temporal = self.temporal(x.unsqueeze(1))
        pooled = torch.cat(
            [temporal.mean(dim=-1), temporal.amax(dim=-1)], dim=-1
        )
        return self.projection(pooled)


class ConservativeResidualEncoder(nn.Module):
    """Add a bounded specialist correction to a full-capacity MLP backbone."""

    def __init__(
        self,
        base: nn.Module,
        specialist: nn.Module,
        embedding_dim: int,
        residual_scale: float = 0.25,
    ):
        super().__init__()
        if not 0.0 < residual_scale <= 1.0:
            raise ValueError("residual scale must be in (0, 1]")
        self.base = base
        self.specialist = specialist
        self.residual_projection = nn.Linear(embedding_dim, embedding_dim)
        nn.init.zeros_(self.residual_projection.weight)
        nn.init.zeros_(self.residual_projection.bias)
        self.residual_scale = float(residual_scale)

    def forward(self, x: Tensor) -> Tensor:
        base = self.base(x)
        residual = torch.tanh(self.residual_projection(self.specialist(x)))
        return base + self.residual_scale * residual


class NullEvidenceAdapter(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.num_classes = int(num_classes)

    def forward(self, x: Tensor) -> Tensor:
        return x.new_zeros((len(x), self.num_classes))


class SpecialistEvidenceAdapter(nn.Module):
    """Predict a zero-initialized bounded correction to fused class evidence."""

    def __init__(self, encoder: nn.Module, embedding_dim: int, num_classes: int):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Linear(embedding_dim, num_classes)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x: Tensor) -> Tensor:
        return self.head(self.encoder(x))


class ConflictConditionedEvidenceGate(nn.Module):
    """Apply a zero-initialized bounded log attenuation to fused evidence."""

    def __init__(
        self,
        num_modalities: int,
        hidden_dim: int,
        max_log_attenuation: float = 1.0,
    ):
        super().__init__()
        if max_log_attenuation <= 0.0:
            raise ValueError("max log attenuation must be positive")
        gate_hidden = max(4, hidden_dim // 4)
        self.network = nn.Sequential(
            nn.Linear(1 + 3 * num_modalities, gate_hidden),
            nn.GELU(),
            nn.Linear(gate_hidden, 1),
        )
        nn.init.zeros_(self.network[-1].weight)
        nn.init.zeros_(self.network[-1].bias)
        self.max_log_attenuation = float(max_log_attenuation)

    def forward(self, features: Tensor) -> Tensor:
        return self.max_log_attenuation * torch.tanh(
            self.network(features).squeeze(-1)
        )


def build_view_encoder(
    kind: str,
    input_dim: int,
    hidden_dim: int,
    embedding_dim: int,
    dropout: float,
) -> nn.Module:
    if kind == "mlp":
        return ViewEncoder(input_dim, hidden_dim, embedding_dim, dropout)
    if kind == "tls_gated":
        return TlsHandshakeEncoder(input_dim, hidden_dim, embedding_dim, dropout)
    if kind == "sequence_tcn":
        return PacketSequenceTCNEncoder(input_dim, hidden_dim, embedding_dim, dropout)
    if kind == "tls_residual_025":
        return ConservativeResidualEncoder(
            ViewEncoder(input_dim, hidden_dim, embedding_dim, dropout),
            TlsHandshakeEncoder(input_dim, hidden_dim, embedding_dim, dropout),
            embedding_dim,
        )
    if kind == "sequence_residual_025":
        return ConservativeResidualEncoder(
            ViewEncoder(input_dim, hidden_dim, embedding_dim, dropout),
            PacketSequenceTCNEncoder(input_dim, hidden_dim, embedding_dim, dropout),
            embedding_dim,
        )
    raise ValueError(f"unknown view encoder kind: {kind}")


def build_evidence_adapter(
    kind: str,
    input_dim: int,
    hidden_dim: int,
    embedding_dim: int,
    num_classes: int,
    dropout: float,
) -> nn.Module:
    if kind == "none":
        return NullEvidenceAdapter(num_classes)
    if kind == "tls_gated":
        encoder = TlsHandshakeEncoder(input_dim, hidden_dim, embedding_dim, dropout)
    elif kind == "sequence_tcn":
        encoder = PacketSequenceTCNEncoder(input_dim, hidden_dim, embedding_dim, dropout)
    else:
        raise ValueError(f"unknown evidence adapter kind: {kind}")
    return SpecialistEvidenceAdapter(encoder, embedding_dim, num_classes)


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
        encoder_kinds: Optional[Sequence[str]] = None,
        evidence_adapter_kinds: Optional[Sequence[str]] = None,
        evidence_adapter_scale: float = 0.25,
        counterfactual_conflict_gate: bool = False,
        counterfactual_gate_max_log_attenuation: float = 1.0,
    ):
        super().__init__()
        if len(input_dims) < 2:
            raise ValueError("at least two modalities are required")
        self.input_dims = list(input_dims)
        self.num_modalities = len(input_dims)
        self.num_classes = num_classes
        self.embedding_dim = embedding_dim
        self.conflict_scale = conflict_scale
        if encoder_kinds is None:
            encoder_kinds = ["mlp"] * len(input_dims)
        if len(encoder_kinds) != len(input_dims):
            raise ValueError("encoder kinds must match the modality count")
        self.encoder_kinds = [str(kind) for kind in encoder_kinds]
        if evidence_adapter_kinds is None:
            evidence_adapter_kinds = ["none"] * len(input_dims)
        if len(evidence_adapter_kinds) != len(input_dims):
            raise ValueError("evidence adapter kinds must match the modality count")
        if not 0.0 < evidence_adapter_scale <= 1.0:
            raise ValueError("evidence adapter scale must be in (0, 1]")
        self.evidence_adapter_kinds = [str(kind) for kind in evidence_adapter_kinds]
        self.evidence_adapter_scale = float(evidence_adapter_scale)
        if fusion_mode not in {"sum", "reliability", "conflict"}:
            raise ValueError("fusion_mode must be sum, reliability, or conflict")
        self.fusion_mode = fusion_mode

        self.encoders = nn.ModuleList(
            build_view_encoder(kind, dim, hidden_dim, embedding_dim, dropout)
            for kind, dim in zip(self.encoder_kinds, input_dims)
        )
        self.evidence_adapters = nn.ModuleList(
            build_evidence_adapter(
                kind,
                dim,
                hidden_dim,
                embedding_dim,
                num_classes,
                dropout,
            )
            for kind, dim in zip(self.evidence_adapter_kinds, input_dims)
        )
        self.counterfactual_conflict_gate = (
            ConflictConditionedEvidenceGate(
                self.num_modalities,
                hidden_dim,
                counterfactual_gate_max_log_attenuation,
            )
            if counterfactual_conflict_gate
            else None
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
        adapter_delta = sum(
            (adapter(view) for adapter, view in zip(self.evidence_adapters, views)),
            fused_evidence.new_zeros(fused_evidence.shape),
        )
        fused_evidence = (
            fused_evidence
            + self.evidence_adapter_scale * torch.tanh(adapter_delta)
        ).clamp_min(0.0)
        if self.counterfactual_conflict_gate is None:
            gate_log_attenuation = fused_evidence.new_zeros(batch_size)
        else:
            gate_features = torch.cat(
                [
                    global_conflict.unsqueeze(-1),
                    modality_conflict,
                    uncertainty_tensor,
                    reliability_tensor,
                ],
                dim=-1,
            )
            gate_log_attenuation = self.counterfactual_conflict_gate(gate_features)
            fused_evidence = fused_evidence * torch.exp(
                -gate_log_attenuation.unsqueeze(-1)
            )
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
            "evidence_adapter_delta": adapter_delta,
            "counterfactual_gate_log_attenuation": gate_log_attenuation,
            "fused_alpha": fused_alpha,
            "fused_belief": fused_belief,
            "fused_probability": fused_probability,
            "fused_uncertainty": fused_uncertainty.squeeze(-1),
            "fused_embedding": fused_embedding,
            "malicious_logit": malicious_logit,
            "class_centers": self.class_centers,
        }

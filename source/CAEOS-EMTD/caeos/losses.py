from typing import Dict, Optional

import torch
from torch import Tensor
import torch.nn.functional as F


def dirichlet_kl_to_uniform(alpha: Tensor) -> Tensor:
    num_classes = alpha.shape[-1]
    strength = alpha.sum(dim=-1, keepdim=True)
    log_normalizer = (
        torch.lgamma(strength)
        - torch.lgamma(alpha).sum(dim=-1, keepdim=True)
        - torch.lgamma(alpha.new_tensor(float(num_classes)))
    )
    digamma_term = ((alpha - 1.0) * (torch.digamma(alpha) - torch.digamma(strength))).sum(
        dim=-1, keepdim=True
    )
    return (log_normalizer + digamma_term).squeeze(-1)


def evidential_classification_loss(
    alpha: Tensor,
    targets: Tensor,
    epoch: int,
    annealing_epochs: int = 10,
    sample_weight: Optional[Tensor] = None,
) -> Tensor:
    one_hot = F.one_hot(targets, num_classes=alpha.shape[-1]).to(alpha.dtype)
    strength = alpha.sum(dim=-1, keepdim=True)
    expected_ce = (
        one_hot * (torch.digamma(strength) - torch.digamma(alpha))
    ).sum(dim=-1)
    alpha_without_true_evidence = one_hot + (1.0 - one_hot) * alpha
    annealing = min(1.0, float(epoch + 1) / max(1, annealing_epochs))
    loss = expected_ce + annealing * dirichlet_kl_to_uniform(alpha_without_true_evidence)
    if sample_weight is not None:
        loss = loss * sample_weight
        return loss.sum() / sample_weight.sum().clamp_min(1.0)
    return loss.mean()


def center_loss(embeddings: Tensor, targets: Tensor, centers: Tensor) -> Tensor:
    return (embeddings - centers[targets]).pow(2).sum(dim=-1).mean()


def supervised_contrastive_loss(
    embeddings: Tensor,
    targets: Tensor,
    temperature: float = 0.1,
) -> Tensor:
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    if len(embeddings) < 2:
        return embeddings.sum() * 0.0
    normalized = F.normalize(embeddings, dim=-1)
    logits = normalized @ normalized.transpose(0, 1)
    logits = logits / temperature
    diagonal = torch.eye(
        len(embeddings),
        dtype=torch.bool,
        device=embeddings.device,
    )
    candidate_mask = ~diagonal
    positive_mask = (
        targets.view(-1, 1) == targets.view(1, -1)
    ) & candidate_mask
    positive_count = positive_mask.sum(dim=1)
    valid = positive_count > 0
    if not torch.any(valid):
        return embeddings.sum() * 0.0
    row_max = logits.masked_fill(diagonal, -torch.inf).max(
        dim=1, keepdim=True
    ).values.detach()
    shifted = logits - row_max
    log_denominator = torch.log(
        (torch.exp(shifted) * candidate_mask).sum(
            dim=1, keepdim=True
        ).clamp_min(1e-12)
    )
    log_probability = shifted - log_denominator
    mean_positive_log_probability = (
        (log_probability * positive_mask).sum(dim=1)
        / positive_count.clamp_min(1)
    )
    return -mean_positive_log_probability[valid].mean()


def compute_training_loss(
    output: Dict[str, Tensor],
    targets: Tensor,
    reliability_targets: Tensor,
    benign_index: int,
    epoch: int,
    annealing_epochs: int,
    fused_weight: float = 1.0,
    center_weight: float = 0.02,
    reliability_weight: float = 0.2,
    malicious_weight: float = 0.2,
) -> Dict[str, Tensor]:
    modality_losses = []
    for modality_index in range(output["evidence"].shape[1]):
        alpha = output["evidence"][:, modality_index] + 1.0
        modality_losses.append(
            evidential_classification_loss(
                alpha,
                targets,
                epoch,
                annealing_epochs,
                reliability_targets[:, modality_index],
            )
        )
    modality_loss = torch.stack(modality_losses).mean()
    fused_loss = evidential_classification_loss(
        output["fused_alpha"], targets, epoch, annealing_epochs
    )
    prototype_loss = center_loss(
        output["fused_embedding"], targets, output["class_centers"]
    ) if "class_centers" in output else output["fused_embedding"].new_tensor(0.0)
    reliability_loss = F.binary_cross_entropy_with_logits(
        output["reliability_logit"], reliability_targets
    )
    malicious_target = (targets != benign_index).to(output["malicious_logit"].dtype)
    malicious_loss = F.binary_cross_entropy_with_logits(
        output["malicious_logit"], malicious_target
    )
    total = (
        modality_loss
        + fused_weight * fused_loss
        + center_weight * prototype_loss
        + reliability_weight * reliability_loss
        + malicious_weight * malicious_loss
    )
    return {
        "total": total,
        "modality": modality_loss.detach(),
        "fused": fused_loss.detach(),
        "center": prototype_loss.detach(),
        "reliability": reliability_loss.detach(),
        "malicious": malicious_loss.detach(),
    }

from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score
from torch import Tensor, nn

from .losses import compute_training_loss


def move_batch(batch: Dict[str, object], device: torch.device) -> Tuple[List[Tensor], Tensor, Tensor, Tensor]:
    views = [view.to(device, non_blocking=True) for view in batch["views"]]
    quality = batch["quality"].to(device, non_blocking=True)
    labels = batch["label"].to(device, non_blocking=True)
    is_unknown = batch["is_unknown"].to(device, non_blocking=True)
    return views, quality, labels, is_unknown


def corrupt_modalities(
    views: Sequence[Tensor],
    quality: Tensor,
    probability: float,
    noise_std: float,
) -> Tuple[List[Tensor], Tensor, Tensor]:
    batch_size = views[0].shape[0]
    num_modalities = len(views)
    mask = torch.rand((batch_size, num_modalities), device=views[0].device) < probability
    reliability_target = (~mask).to(views[0].dtype)
    corrupted_views: List[Tensor] = []
    for modality_index, view in enumerate(views):
        replace = mask[:, modality_index].view(-1, *([1] * (view.ndim - 1)))
        noise = torch.randn_like(view) * noise_std
        corrupted_views.append(torch.where(replace, noise, view))
    corrupted_quality = quality * (1.0 - 0.75 * mask.to(quality.dtype))
    return corrupted_views, corrupted_quality, reliability_target


def label_mismatched_sources(labels: Tensor) -> Tuple[Tensor, Tensor]:
    """Choose a deterministic different-class source for every eligible sample."""
    if labels.ndim != 1:
        raise ValueError("labels must be one-dimensional")
    count = len(labels)
    if count == 0:
        return labels.new_empty((0,), dtype=torch.long), labels.new_empty(
            (0,), dtype=torch.bool
        )
    indices = torch.arange(count, device=labels.device)
    different = labels[:, None] != labels[None, :]
    valid = different.any(dim=1)
    offsets = (indices[None, :] - indices[:, None]).remainder(count)
    offsets = torch.where(
        different,
        offsets,
        torch.full_like(offsets, count + 1),
    )
    sources = offsets.argmin(dim=1)
    sources = torch.where(valid, sources, indices)
    return sources, valid


def make_counterfactual_views(
    views: Sequence[Tensor],
    labels: Tensor,
    modality_indices: Sequence[int],
) -> Tuple[List[Tensor], Tensor]:
    sources, valid = label_mismatched_sources(labels)
    selected = {int(index) for index in modality_indices}
    if not selected or min(selected) < 0 or max(selected) >= len(views):
        raise ValueError("counterfactual modality indices are invalid")
    counterfactual = [
        view[sources] if index in selected else view
        for index, view in enumerate(views)
    ]
    return counterfactual, valid


def train_model(
    model: nn.Module,
    train_loader: Iterable[Dict[str, object]],
    validation_loader: Iterable[Dict[str, object]],
    device: torch.device,
    benign_index: int,
    epochs: int,
    learning_rate: float,
    weight_decay: float,
    annealing_epochs: int,
    corruption_probability: float,
    corruption_noise: float,
    use_amp: bool,
    teacher_model: Optional[nn.Module] = None,
    consistency_weight: float = 0.0,
    counterfactual_weight: float = 0.0,
    counterfactual_margin: float = 0.05,
    counterfactual_modality_indices: Sequence[int] = (0, 3),
    counterfactual_nonattenuation_weight: float = 0.1,
    prefer_last_epoch_on_known_f1_tie: bool = False,
) -> List[Dict[str, float]]:
    if consistency_weight < 0.0:
        raise ValueError("consistency weight must be nonnegative")
    if teacher_model is None and consistency_weight != 0.0:
        raise ValueError("positive consistency weight requires a teacher model")
    if counterfactual_weight < 0.0 or counterfactual_nonattenuation_weight < 0.0:
        raise ValueError("counterfactual weights must be nonnegative")
    if counterfactual_margin < 0.0:
        raise ValueError("counterfactual margin must be nonnegative")
    if teacher_model is None and counterfactual_weight != 0.0:
        raise ValueError("positive counterfactual weight requires a teacher model")
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp and device.type == "cuda")
    best_f1 = -1.0
    best_state = None
    history: List[Dict[str, float]] = []

    for epoch in range(epochs):
        model.train()
        if teacher_model is not None:
            teacher_model.eval()
        running_total = 0.0
        running_consistency = 0.0
        running_counterfactual = 0.0
        running_batches = 0
        for batch in train_loader:
            views, quality, labels, _ = move_batch(batch, device)
            clean_views = views
            clean_quality = quality
            views, quality, reliability_target = corrupt_modalities(
                views,
                quality,
                corruption_probability,
                corruption_noise,
            )
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=use_amp and device.type == "cuda"):
                output = model(views, quality)
                losses = compute_training_loss(
                    output,
                    labels,
                    reliability_target,
                    benign_index,
                    epoch,
                    annealing_epochs,
                )
                if teacher_model is not None:
                    with torch.no_grad():
                        teacher_output = teacher_model(clean_views, clean_quality)
                        teacher_probability = teacher_output["fused_probability"]
                    student_probability = output["fused_probability"].clamp_min(1e-8)
                    consistency = F.kl_div(
                        student_probability.log(),
                        teacher_probability,
                        reduction="batchmean",
                    )
                    losses["consistency"] = consistency
                    losses["total"] = losses["total"] + consistency_weight * consistency
                    if counterfactual_weight > 0.0:
                        counterfactual_views, valid = make_counterfactual_views(
                            clean_views,
                            labels,
                            counterfactual_modality_indices,
                        )
                        counterfactual_output = model(
                            counterfactual_views, clean_quality
                        )
                        if bool(valid.any()):
                            target = (
                                teacher_output["fused_uncertainty"]
                                + counterfactual_margin
                            ).clamp_max(1.0)
                            margin_loss = F.relu(
                                target[valid]
                                - counterfactual_output["fused_uncertainty"][valid]
                            ).mean()
                            nonattenuation = F.relu(
                                -counterfactual_output[
                                    "counterfactual_gate_log_attenuation"
                                ][valid]
                            ).mean()
                            counterfactual_loss = (
                                margin_loss
                                + counterfactual_nonattenuation_weight * nonattenuation
                            )
                        else:
                            counterfactual_loss = losses["total"].new_zeros(())
                        losses["counterfactual"] = counterfactual_loss
                        losses["total"] = (
                            losses["total"]
                            + counterfactual_weight * counterfactual_loss
                        )
            scaler.scale(losses["total"]).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
            running_total += float(losses["total"].detach().cpu())
            running_consistency += float(
                losses.get("consistency", losses["total"].new_zeros(())).detach().cpu()
            )
            running_counterfactual += float(
                losses.get(
                    "counterfactual", losses["total"].new_zeros(())
                ).detach().cpu()
            )
            running_batches += 1

        validation_f1 = evaluate_known_f1(model, validation_loader, device)
        epoch_record = {
            "epoch": float(epoch + 1),
            "train_loss": running_total / max(1, running_batches),
            "validation_macro_f1": validation_f1,
            "consistency_loss": running_consistency / max(1, running_batches),
            "counterfactual_loss": running_counterfactual / max(1, running_batches),
        }
        history.append(epoch_record)
        print(
            "epoch=%d train_loss=%.5f validation_macro_f1=%.5f"
            % (epoch + 1, epoch_record["train_loss"], validation_f1),
            flush=True,
        )
        if validation_f1 > best_f1 or (
            prefer_last_epoch_on_known_f1_tie
            and abs(validation_f1 - best_f1) <= 1e-12
        ):
            best_f1 = validation_f1
            best_state = copy.deepcopy(model.state_dict())

    if best_state is not None:
        model.load_state_dict(best_state)
    return history


@torch.no_grad()
def evaluate_counterfactual_gate(
    model: nn.Module,
    loader: Iterable[Dict[str, object]],
    device: torch.device,
    modality_indices: Sequence[int],
    margin: float,
) -> Dict[str, float]:
    model.eval()
    views_all: Optional[List[List[Tensor]]] = None
    quality_all: List[Tensor] = []
    labels_all: List[Tensor] = []
    unknown_all: List[Tensor] = []
    for batch in loader:
        views, quality, labels, is_unknown = move_batch(batch, device)
        if views_all is None:
            views_all = [[] for _ in views]
        for collected, view in zip(views_all, views):
            collected.append(view)
        quality_all.append(quality)
        labels_all.append(labels)
        unknown_all.append(is_unknown)
    if views_all is None:
        raise ValueError("counterfactual diagnostic loader is empty")
    if bool(torch.cat(unknown_all).any()):
        raise ValueError("counterfactual diagnostics require known-only data")
    views = [torch.cat(parts) for parts in views_all]
    quality = torch.cat(quality_all)
    labels = torch.cat(labels_all)
    counterfactual_views, valid = make_counterfactual_views(
        views, labels, modality_indices
    )
    if not bool(valid.any()):
        raise ValueError("counterfactual diagnostics require at least two classes")
    clean = model(views, quality)
    counterfactual = model(counterfactual_views, quality)
    uncertainty_gain = (
        counterfactual["fused_uncertainty"] - clean["fused_uncertainty"]
    )[valid]
    attenuation_gain = (
        counterfactual["counterfactual_gate_log_attenuation"]
        - clean["counterfactual_gate_log_attenuation"]
    )[valid]
    return {
        "valid_samples": int(valid.sum().item()),
        "mean_clean_uncertainty": float(clean["fused_uncertainty"][valid].mean().cpu()),
        "mean_counterfactual_uncertainty": float(
            counterfactual["fused_uncertainty"][valid].mean().cpu()
        ),
        "mean_counterfactual_uncertainty_gain": float(uncertainty_gain.mean().cpu()),
        "margin_satisfaction_fraction": float(
            (uncertainty_gain >= margin).to(torch.float32).mean().cpu()
        ),
        "mean_clean_log_attenuation": float(
            clean["counterfactual_gate_log_attenuation"][valid].mean().cpu()
        ),
        "mean_counterfactual_log_attenuation": float(
            counterfactual["counterfactual_gate_log_attenuation"][valid].mean().cpu()
        ),
        "mean_counterfactual_log_attenuation_gain": float(
            attenuation_gain.mean().cpu()
        ),
        "unknown_or_test_labels_used": False,
    }


@torch.no_grad()
def evaluate_known_f1(
    model: nn.Module,
    loader: Iterable[Dict[str, object]],
    device: torch.device,
) -> float:
    model.eval()
    labels_all = []
    predictions_all = []
    for batch in loader:
        views, quality, labels, _ = move_batch(batch, device)
        output = model(views, quality)
        predictions = output["fused_belief"].argmax(dim=-1)
        labels_all.append(labels.cpu().numpy())
        predictions_all.append(predictions.cpu().numpy())
    labels_np = np.concatenate(labels_all)
    predictions_np = np.concatenate(predictions_all)
    return float(f1_score(labels_np, predictions_np, average="macro"))


@torch.no_grad()
def collect_outputs(
    model: nn.Module,
    loader: Iterable[Dict[str, object]],
    device: torch.device,
) -> Tuple[Dict[str, Tensor], Tensor, Tensor]:
    model.eval()
    collected: Dict[str, List[Tensor]] = {
        "fused_evidence": [],
        "fused_alpha": [],
        "fused_belief": [],
        "fused_probability": [],
        "fused_uncertainty": [],
        "fused_embedding": [],
        "raw_conflict": [],
        "effective_conflict": [],
        "global_conflict": [],
        "malicious_logit": [],
        "reliability": [],
        "discount": [],
    }
    labels_all: List[Tensor] = []
    unknown_all: List[Tensor] = []
    for batch in loader:
        views, quality, labels, is_unknown = move_batch(batch, device)
        output = model(views, quality)
        for key in collected:
            collected[key].append(output[key].detach().cpu())
        labels_all.append(labels.cpu())
        unknown_all.append(is_unknown.cpu())
    return (
        {key: torch.cat(values, dim=0) for key, values in collected.items()},
        torch.cat(labels_all, dim=0),
        torch.cat(unknown_all, dim=0),
    )

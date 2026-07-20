from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
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
) -> List[Dict[str, float]]:
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp and device.type == "cuda")
    best_f1 = -1.0
    best_state = None
    history: List[Dict[str, float]] = []

    for epoch in range(epochs):
        model.train()
        running_total = 0.0
        running_batches = 0
        for batch in train_loader:
            views, quality, labels, _ = move_batch(batch, device)
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
            scaler.scale(losses["total"]).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
            running_total += float(losses["total"].detach().cpu())
            running_batches += 1

        validation_f1 = evaluate_known_f1(model, validation_loader, device)
        epoch_record = {
            "epoch": float(epoch + 1),
            "train_loss": running_total / max(1, running_batches),
            "validation_macro_f1": validation_f1,
        }
        history.append(epoch_record)
        print(
            "epoch=%d train_loss=%.5f validation_macro_f1=%.5f"
            % (epoch + 1, epoch_record["train_loss"], validation_f1),
            flush=True,
        )
        if validation_f1 > best_f1:
            best_f1 = validation_f1
            best_state = copy.deepcopy(model.state_dict())

    if best_state is not None:
        model.load_state_dict(best_state)
    return history


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

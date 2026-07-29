from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)
from train_strict_v4_packet_sequence_fusion_task_cuda import (
    BENIGN_FAMILY,
    GPUSampler,
    benign_prototype_distance,
    class_weights,
    prototype_distance,
    query_gpu,
    robust_scale_statistics,
    sequence_channels,
    sigmoid,
    softmax,
    stratified_open_set_split,
    tail_percentile,
)


def build_model(
    torch: Any,
    number_of_classes: int,
    sequence_length: int,
    statistic_dimension: int,
    cosine_scale: float,
) -> Any:
    nn = torch.nn

    class ResidualBlock(nn.Module):
        def __init__(self, channels: int, dilation: int) -> None:
            super().__init__()
            self.network = nn.Sequential(
                nn.Conv1d(
                    channels,
                    channels,
                    kernel_size=5,
                    padding=2 * dilation,
                    dilation=dilation,
                    bias=False,
                ),
                nn.BatchNorm1d(channels),
                nn.GELU(),
                nn.Conv1d(channels, channels, kernel_size=1, bias=False),
                nn.BatchNorm1d(channels),
            )
            self.activation = nn.GELU()

        def forward(self, values: Any) -> Any:
            return self.activation(values + self.network(values))

    class CosineClassifier(nn.Module):
        def __init__(self, input_dimension: int) -> None:
            super().__init__()
            self.weight = nn.Parameter(
                torch.empty(number_of_classes, input_dimension)
            )
            nn.init.xavier_uniform_(self.weight)

        def cosine(self, values: Any) -> Any:
            weights = torch.nn.functional.normalize(self.weight, dim=1)
            return values @ weights.T

        def forward(self, values: Any) -> Any:
            return cosine_scale * self.cosine(values)

    class DualMetricContrastiveNet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            channels = 128
            self.stem = nn.Sequential(
                nn.Conv1d(4, channels, kernel_size=5, padding=2, bias=False),
                nn.BatchNorm1d(channels),
                nn.GELU(),
            )
            self.position = nn.Parameter(
                torch.zeros(1, channels, sequence_length)
            )
            self.blocks = nn.Sequential(
                ResidualBlock(channels, 1),
                ResidualBlock(channels, 2),
                ResidualBlock(channels, 4),
                ResidualBlock(channels, 1),
            )
            self.statistic_encoder = nn.Sequential(
                nn.Linear(statistic_dimension, 128),
                nn.LayerNorm(128),
                nn.GELU(),
                nn.Dropout(0.15),
                nn.Linear(128, 64),
                nn.GELU(),
            )
            self.shared_embedding = nn.Sequential(
                nn.Linear(channels * 2 + 64, 192),
                nn.GELU(),
                nn.Dropout(0.15),
                nn.Linear(192, 128),
                nn.GELU(),
            )
            self.type_projection = nn.Sequential(
                nn.Linear(128, 128),
                nn.GELU(),
                nn.Linear(128, 96),
            )
            self.attack_projection = nn.Sequential(
                nn.Linear(128, 96),
                nn.GELU(),
                nn.Linear(96, 64),
            )
            self.family_head = CosineClassifier(96)
            self.attack_head = nn.Linear(64, 1)
            self.knownness_head = nn.Linear(96, 1)

        def forward(
            self, values: Any, statistics: Any
        ) -> tuple[Any, Any, Any, Any, Any]:
            mask = values[:, 3:4, :]
            encoded = self.blocks(self.stem(values) + self.position) * mask
            denominator = mask.sum(dim=2).clamp_min(1.0)
            mean_pool = encoded.sum(dim=2) / denominator
            minimum = torch.finfo(encoded.dtype).min
            max_pool = encoded.masked_fill(mask == 0, minimum).amax(dim=2)
            max_pool = torch.where(
                torch.isfinite(max_pool), max_pool, torch.zeros_like(max_pool)
            )
            fused = torch.cat(
                (
                    mean_pool,
                    max_pool,
                    self.statistic_encoder(statistics),
                ),
                dim=1,
            )
            shared = self.shared_embedding(fused)
            type_embedding = torch.nn.functional.normalize(
                self.type_projection(shared), dim=1
            )
            attack_embedding = torch.nn.functional.normalize(
                self.attack_projection(shared), dim=1
            )
            return (
                type_embedding,
                attack_embedding,
                self.family_head(type_embedding),
                self.attack_head(attack_embedding).squeeze(1),
                self.knownness_head(type_embedding).squeeze(1),
            )

        def family_cosine(self, type_embedding: Any) -> Any:
            return self.family_head.cosine(type_embedding)

    return DualMetricContrastiveNet()


def supervised_contrastive_loss(
    torch: Any,
    embeddings: Any,
    labels: Any,
    temperature: float,
) -> Any:
    if embeddings.shape[0] < 2:
        return embeddings.sum() * 0.0
    values = torch.nn.functional.normalize(embeddings.float(), dim=1)
    similarity = values @ values.T / temperature
    identity = torch.eye(
        labels.numel(), dtype=torch.bool, device=labels.device
    )
    positive = labels[:, None].eq(labels[None, :]) & ~identity
    valid = positive.sum(dim=1) > 0
    if not bool(valid.any()):
        return values.sum() * 0.0
    similarity = similarity - similarity.max(dim=1, keepdim=True).values.detach()
    exp_similarity = torch.exp(similarity).masked_fill(identity, 0.0)
    log_probability = similarity - torch.log(
        exp_similarity.sum(dim=1, keepdim=True).clamp_min(1e-12)
    )
    mean_positive = (
        (log_probability * positive).sum(dim=1)
        / positive.sum(dim=1).clamp_min(1)
    )
    return -mean_positive[valid].mean()


def pseudo_family_for_step(
    attack_class_indices: list[int],
    epoch: int,
    batch_number: int,
) -> int:
    if not attack_class_indices:
        raise ValueError("at least one attack class is required")
    return attack_class_indices[
        (epoch + batch_number) % len(attack_class_indices)
    ]


def leave_one_family_margin_loss(
    torch: Any,
    cosine: Any,
    labels: Any,
    pseudo_family: int,
    known_margin: float,
    pseudo_unknown_margin: float,
) -> Any:
    class_count = cosine.shape[1]
    own_similarity = cosine.gather(1, labels[:, None]).squeeze(1)
    known_mask = labels != pseudo_family
    known_term = torch.relu(known_margin - own_similarity[known_mask])
    pseudo_mask = labels == pseudo_family
    if bool(pseudo_mask.any()) and class_count > 1:
        allowed = torch.ones(
            class_count, dtype=torch.bool, device=cosine.device
        )
        allowed[pseudo_family] = False
        closest_other = cosine[pseudo_mask][:, allowed].max(dim=1).values
        pseudo_term = torch.relu(
            closest_other - pseudo_unknown_margin
        )
    else:
        pseudo_term = cosine.sum().reshape(1) * 0.0
    parts = []
    if known_term.numel():
        parts.append(known_term.mean())
    if pseudo_term.numel():
        parts.append(pseudo_term.mean())
    return torch.stack(parts).mean() if parts else cosine.sum() * 0.0


def attack_probability_variants(
    family_probability: np.ndarray,
    attack_probability: np.ndarray,
    benign_index: int,
) -> dict[str, np.ndarray]:
    family_attack = 1.0 - np.asarray(
        family_probability[:, benign_index], dtype=np.float64
    )
    attack_head = np.asarray(attack_probability, dtype=np.float64)
    return {
        "attack_head": attack_head,
        "family": family_attack,
        "maximum": np.maximum(attack_head, family_attack),
        "noisy_or": 1.0 - (1.0 - attack_head) * (1.0 - family_attack),
    }


def batched_inference(
    *,
    torch: Any,
    model: Any,
    features: Any,
    statistics: Any,
    batch_size: int,
) -> tuple[np.ndarray, ...]:
    outputs: list[list[np.ndarray]] = [[], [], [], [], [], []]
    model.eval()
    with torch.no_grad():
        for start in range(0, features.shape[0], batch_size):
            values = model(
                features[start : start + batch_size],
                statistics[start : start + batch_size],
            )
            cosine = model.family_cosine(values[0])
            for collection, value in zip(outputs[:5], values):
                collection.append(value.float().cpu().numpy())
            outputs[5].append(cosine.float().cpu().numpy())
    return tuple(np.concatenate(values, axis=0) for values in outputs)


def apply_statistic_modality_dropout(
    torch: Any,
    statistics: Any,
    probability: float,
) -> Any:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("statistic modality dropout probability must be in [0, 1]")
    if probability == 0.0:
        return statistics
    if probability == 1.0:
        return torch.zeros_like(statistics)
    keep = (
        torch.rand(
            (statistics.shape[0], 1),
            device=statistics.device,
            dtype=statistics.dtype,
        )
        >= probability
    ).to(statistics.dtype)
    return statistics * keep / (1.0 - probability)


def evaluation_statistics_for_dropout(
    torch: Any,
    statistics: Any,
    probability: float,
) -> Any:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("statistic modality dropout probability must be in [0, 1]")
    if probability == 1.0:
        return torch.zeros_like(statistics)
    return statistics


def family_heldout_meta_loss(
    *,
    torch: Any,
    model: Any,
    attack_logits: Any,
    batch_labels: Any,
    benign_index: int,
    heldout_family: int,
    episode_features: Any,
    episode_statistics: Any,
    episode_attack_targets: Any,
    inner_learning_rate: float,
) -> tuple[Any, Any]:
    if inner_learning_rate <= 0.0:
        raise ValueError("meta inner learning rate must be positive")
    inner_mask = batch_labels != heldout_family
    if not bool(inner_mask.any()):
        raise ValueError("meta inner batch is empty after family holdout")
    inner_targets = (batch_labels[inner_mask] != benign_index).float()
    inner_loss = torch.nn.functional.binary_cross_entropy_with_logits(
        attack_logits[inner_mask],
        inner_targets,
    )
    named_parameters = dict(model.named_parameters())
    gradients = torch.autograd.grad(
        inner_loss,
        tuple(named_parameters.values()),
        create_graph=True,
        retain_graph=True,
        allow_unused=True,
    )
    fast_parameters = {
        name: (
            parameter - inner_learning_rate * gradient
            if gradient is not None
            else parameter
        )
        for (name, parameter), gradient in zip(
            named_parameters.items(), gradients
        )
    }
    episode_outputs = torch.func.functional_call(
        model,
        fast_parameters,
        (episode_features, episode_statistics),
    )
    outer_loss = torch.nn.functional.binary_cross_entropy_with_logits(
        episode_outputs[3],
        episode_attack_targets.float(),
    )
    return inner_loss, outer_loss


def train_task(args: argparse.Namespace) -> dict[str, Any]:
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_index)
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA is not available")
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda:0")
    torch.cuda.set_device(args.gpu_index)
    torch.empty(1, device=device)
    torch.cuda.reset_peak_memory_stats(args.gpu_index)
    sentinel = torch.randn((512, 512), device=device)
    sentinel_checksum = float((sentinel @ sentinel.T).sum().item())
    if not math.isfinite(sentinel_checksum):
        raise RuntimeError("CUDA sentinel computation was not finite")
    with np.load(args.sequence_dataset.resolve(), allow_pickle=False) as source:
        packet_lengths = np.asarray(source["packet_lengths"], dtype=np.int16)
        interarrival_us = np.asarray(source["interarrival_us"], dtype=np.float32)
        mask = np.asarray(source["mask"], dtype=bool)
        flow_ids = np.asarray(source["flow_ids"]).astype(str)
        families = np.asarray(source["families"]).astype(str)
        statistics = np.asarray(source["flow_statistics"], dtype=np.float32)
        statistic_names = np.asarray(source["flow_statistic_names"]).astype(str)
    if not (
        packet_lengths.shape == interarrival_us.shape == mask.shape
        and packet_lengths.shape[0] == flow_ids.size == families.size
        and statistics.ndim == 2
        and statistics.shape[0] == flow_ids.size
        and statistic_names.size == statistics.shape[1]
    ):
        raise ValueError("packet/statistic dataset array shapes are inconsistent")
    splits = stratified_open_set_split(
        flow_ids,
        families,
        unknown_family=args.unknown_family,
        seed=args.seed,
    )
    known_class_names = sorted(
        family
        for family in np.unique(families).tolist()
        if family != args.unknown_family
    )
    benign_index = known_class_names.index(BENIGN_FAMILY)
    class_to_index = {
        family: index for index, family in enumerate(known_class_names)
    }
    encoded_labels = np.asarray(
        [class_to_index.get(family, -1) for family in families],
        dtype=np.int64,
    )
    channels = sequence_channels(packet_lengths, interarrival_us, mask)
    scaled_statistics, scaling_report = robust_scale_statistics(
        statistics, splits["train"]
    )
    feature_tensor = torch.from_numpy(channels).to(device)
    statistic_tensor = torch.from_numpy(scaled_statistics).to(device)
    evaluation_statistic_tensor = evaluation_statistics_for_dropout(
        torch,
        statistic_tensor,
        args.statistic_modality_dropout_probability,
    )
    label_tensor = torch.from_numpy(encoded_labels).to(device)
    train_indices = torch.from_numpy(splits["train"]).to(device)
    validation_indices = torch.from_numpy(splits["validation"]).to(device)
    model = build_model(
        torch,
        len(known_class_names),
        packet_lengths.shape[1],
        statistics.shape[1],
        args.cosine_scale,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs
    )
    weight_tensor = torch.from_numpy(
        class_weights(
            encoded_labels[splits["train"]], len(known_class_names)
        )
    ).to(device)
    family_loss = torch.nn.CrossEntropyLoss(weight=weight_tensor)
    attack_loss = torch.nn.BCEWithLogitsLoss()
    knownness_loss = torch.nn.BCEWithLogitsLoss()
    attack_class_indices = [
        index
        for index in range(len(known_class_names))
        if index != benign_index
    ]
    meta_enabled = args.meta_heldout_loss_weight > 0.0
    architecture_name = (
        "family_heldout_meta_packet_statistic_v1"
        if meta_enabled
        else "dual_metric_contrastive_packet_statistic_v1"
    )
    algorithm_name = (
        "FHMM-CAEOS family-held-out malicious-boundary meta learner"
        if meta_enabled
        else "DMC-CAEOS dual-metric contrastive fusion"
    )
    training_indices_by_class = {
        class_index: torch.from_numpy(
            splits["train"][
                encoded_labels[splits["train"]] == class_index
            ]
        ).to(device)
        for class_index in range(len(known_class_names))
    }
    if meta_enabled:
        if args.meta_episode_rows_per_class <= 0:
            raise ValueError("meta episode rows per class must be positive")
        if args.meta_inner_learning_rate <= 0.0:
            raise ValueError("meta inner learning rate must be positive")
        if any(
            training_indices_by_class[index].numel() == 0
            for index in [benign_index, *attack_class_indices]
        ):
            raise ValueError("meta training requires every known class")
    scaler = torch.cuda.amp.GradScaler()
    initial_gpu = query_gpu()
    sampler = GPUSampler(args.gpu_sample_interval_seconds)
    sampler.start()
    started = time.perf_counter()
    best_validation = math.inf
    best_epoch = -1
    best_state = None
    stale_epochs = 0
    history = []
    try:
        for epoch in range(args.epochs):
            model.train()
            permutation = train_indices[
                torch.randperm(train_indices.numel(), device=device)
            ]
            training_losses = []
            training_meta_outer_losses = []
            for batch_number, start in enumerate(
                range(0, permutation.numel(), args.batch_size)
            ):
                indices = permutation[start : start + args.batch_size]
                batch_values = feature_tensor[indices]
                batch_statistics = apply_statistic_modality_dropout(
                    torch,
                    statistic_tensor[indices],
                    args.statistic_modality_dropout_probability,
                )
                batch_labels = label_tensor[indices]
                batch_attack = (batch_labels != benign_index).long()
                pseudo_family = pseudo_family_for_step(
                    attack_class_indices, epoch, batch_number
                )
                optimizer.zero_grad(set_to_none=True)
                with torch.cuda.amp.autocast():
                    (
                        type_embedding,
                        attack_embedding,
                        family_logits,
                        attack_logits,
                        knownness_logits,
                    ) = model(batch_values, batch_statistics)
                    attack_training_mask = (
                        batch_labels != pseudo_family
                        if meta_enabled
                        else torch.ones_like(batch_labels, dtype=torch.bool)
                    )
                    total_loss = (
                        family_loss(family_logits, batch_labels)
                        + args.attack_loss_weight
                        * attack_loss(
                            attack_logits[attack_training_mask],
                            batch_attack[attack_training_mask].float(),
                        )
                        + args.knownness_loss_weight
                        * knownness_loss(
                            knownness_logits,
                            torch.ones_like(knownness_logits),
                        )
                    )
                    type_contrast = supervised_contrastive_loss(
                        torch,
                        type_embedding,
                        batch_labels,
                        args.contrastive_temperature,
                    )
                    attack_contrast = supervised_contrastive_loss(
                        torch,
                        attack_embedding[attack_training_mask],
                        batch_attack[attack_training_mask],
                        args.contrastive_temperature,
                    )
                    margin = leave_one_family_margin_loss(
                        torch,
                        model.family_cosine(type_embedding),
                        batch_labels,
                        pseudo_family,
                        args.known_similarity_margin,
                        args.pseudo_unknown_similarity_margin,
                    )
                    total_loss = (
                        total_loss
                        + args.family_contrastive_loss_weight * type_contrast
                        + args.attack_contrastive_loss_weight * attack_contrast
                        + args.episodic_margin_loss_weight * margin
                    )
                    rotated = torch.roll(
                        torch.arange(batch_labels.numel(), device=device), 1
                    )
                    different_attack_families = (
                        (batch_labels != benign_index)
                        & (batch_labels[rotated] != benign_index)
                        & (batch_labels != batch_labels[rotated])
                    )
                    if bool(different_attack_families.any()):
                        left = type_embedding[different_attack_families]
                        right = type_embedding[
                            rotated[different_attack_families]
                        ]
                        mixed = torch.nn.functional.normalize(
                            args.pseudo_mix_lambda * left
                            + (1.0 - args.pseudo_mix_lambda) * right,
                            dim=1,
                        )
                        mixed_logits = model.knownness_head(mixed).squeeze(1)
                        total_loss = (
                            total_loss
                            + args.pseudo_mix_loss_weight
                            * knownness_loss(
                                mixed_logits, torch.zeros_like(mixed_logits)
                            )
                        )
                    if meta_enabled:
                        heldout_pool = training_indices_by_class[
                            pseudo_family
                        ]
                        benign_pool = training_indices_by_class[benign_index]
                        heldout_episode = heldout_pool[
                            torch.randint(
                                heldout_pool.numel(),
                                (args.meta_episode_rows_per_class,),
                                device=device,
                            )
                        ]
                        benign_episode = benign_pool[
                            torch.randint(
                                benign_pool.numel(),
                                (args.meta_episode_rows_per_class,),
                                device=device,
                            )
                        ]
                        episode_indices = torch.cat(
                            (heldout_episode, benign_episode)
                        )
                        episode_indices = episode_indices[
                            torch.randperm(
                                episode_indices.numel(), device=device
                            )
                        ]
                        episode_statistics = (
                            apply_statistic_modality_dropout(
                                torch,
                                statistic_tensor[episode_indices],
                                args.statistic_modality_dropout_probability,
                            )
                        )
                        _, meta_outer = family_heldout_meta_loss(
                            torch=torch,
                            model=model,
                            attack_logits=attack_logits,
                            batch_labels=batch_labels,
                            benign_index=benign_index,
                            heldout_family=pseudo_family,
                            episode_features=feature_tensor[episode_indices],
                            episode_statistics=episode_statistics,
                            episode_attack_targets=(
                                label_tensor[episode_indices] != benign_index
                            ),
                            inner_learning_rate=args.meta_inner_learning_rate,
                        )
                        total_loss = (
                            total_loss
                            + args.meta_heldout_loss_weight * meta_outer
                        )
                        training_meta_outer_losses.append(
                            float(meta_outer.detach().cpu())
                        )
                scaler.scale(total_loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                scaler.step(optimizer)
                scaler.update()
                training_losses.append(float(total_loss.detach().cpu()))
            scheduler.step()
            model.eval()
            with torch.no_grad(), torch.cuda.amp.autocast():
                validation_values = model(
                    feature_tensor[validation_indices],
                    evaluation_statistic_tensor[validation_indices],
                )
                validation_labels = label_tensor[validation_indices]
                validation_target = (
                    validation_labels != benign_index
                ).float()
                validation_loss = (
                    family_loss(validation_values[2], validation_labels)
                    + args.attack_loss_weight
                    * attack_loss(validation_values[3], validation_target)
                    + args.knownness_loss_weight
                    * knownness_loss(
                        validation_values[4],
                        torch.ones_like(validation_values[4]),
                    )
                )
            validation_value = float(validation_loss.float().cpu())
            history.append(
                {
                    "epoch": epoch,
                    "training_loss": float(np.mean(training_losses)),
                    "meta_outer_loss": (
                        float(np.mean(training_meta_outer_losses))
                        if training_meta_outer_losses
                        else None
                    ),
                    "validation_loss": validation_value,
                    "learning_rate": float(scheduler.get_last_lr()[0]),
                }
            )
            if validation_value < best_validation - args.minimum_improvement:
                best_validation = validation_value
                best_epoch = epoch
                best_state = {
                    key: value.detach().cpu().clone()
                    for key, value in model.state_dict().items()
                }
                stale_epochs = 0
            else:
                stale_epochs += 1
            if stale_epochs >= args.early_stopping_patience:
                break
        if best_state is None:
            raise RuntimeError("training did not produce a checkpoint")
        model.load_state_dict(best_state)
        train_arrays = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[train_indices],
            statistics=evaluation_statistic_tensor[train_indices],
            batch_size=args.inference_batch_size,
        )
        validation_arrays = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[validation_indices],
            statistics=evaluation_statistic_tensor[validation_indices],
            batch_size=args.inference_batch_size,
        )
        test_indices = torch.from_numpy(splits["test"]).to(device)
        test_arrays = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[test_indices],
            statistics=evaluation_statistic_tensor[test_indices],
            batch_size=args.inference_batch_size,
        )
        torch.cuda.synchronize()
    finally:
        sampler.stop()
    elapsed_seconds = time.perf_counter() - started
    (
        train_type_embedding,
        train_attack_embedding,
        _,
        _,
        _,
        _,
    ) = train_arrays
    (
        validation_type_embedding,
        validation_attack_embedding,
        validation_family,
        validation_attack,
        validation_knownness,
        validation_cosine,
    ) = validation_arrays
    (
        test_type_embedding,
        test_attack_embedding,
        test_family,
        test_attack,
        test_knownness,
        test_cosine,
    ) = test_arrays
    train_labels_np = encoded_labels[splits["train"]]
    validation_labels_np = encoded_labels[splits["validation"]]
    test_labels = encoded_labels[splits["test"]]
    test_unknown = families[splits["test"]] == args.unknown_family
    validation_probability = softmax(validation_family)
    test_probability = softmax(test_family)
    validation_attack_variants = attack_probability_variants(
        validation_probability,
        sigmoid(validation_attack),
        benign_index,
    )
    test_attack_variants = attack_probability_variants(
        test_probability,
        sigmoid(test_attack),
        benign_index,
    )
    validation_prototype, prototype_report = prototype_distance(
        train_type_embedding,
        train_labels_np,
        validation_type_embedding,
        len(known_class_names),
    )
    test_prototype, _ = prototype_distance(
        train_type_embedding,
        train_labels_np,
        test_type_embedding,
        len(known_class_names),
    )
    validation_benign_distance, benign_prototype_report = (
        benign_prototype_distance(
            train_attack_embedding,
            train_labels_np,
            validation_attack_embedding,
            benign_index,
        )
    )
    test_benign_distance, _ = benign_prototype_distance(
        train_attack_embedding,
        train_labels_np,
        test_attack_embedding,
        benign_index,
    )
    validation_raw = {
        "family_uncertainty": 1.0 - validation_probability.max(axis=1),
        "knownness_head": 1.0 - sigmoid(validation_knownness),
        "cosine_distance": 1.0 - validation_cosine.max(axis=1),
        "prototype_distance": validation_prototype,
        "benign_distance": validation_benign_distance,
    }
    test_raw = {
        "family_uncertainty": 1.0 - test_probability.max(axis=1),
        "knownness_head": 1.0 - sigmoid(test_knownness),
        "cosine_distance": 1.0 - test_cosine.max(axis=1),
        "prototype_distance": test_prototype,
        "benign_distance": test_benign_distance,
    }
    validation_tail = {
        name: tail_percentile(values, values)
        for name, values in validation_raw.items()
    }
    test_tail = {
        name: tail_percentile(validation_raw[name], values)
        for name, values in test_raw.items()
    }
    validation_knownness_tail = np.maximum(
        validation_tail["knownness_head"],
        validation_tail["cosine_distance"],
    )
    test_knownness_tail = np.maximum(
        test_tail["knownness_head"],
        test_tail["cosine_distance"],
    )
    validation_open_values = [
        validation_tail["family_uncertainty"],
        validation_knownness_tail,
        validation_tail["prototype_distance"],
        validation_tail["benign_distance"],
    ]
    test_open_values = [
        test_tail["family_uncertainty"],
        test_knownness_tail,
        test_tail["prototype_distance"],
        test_tail["benign_distance"],
    ]
    validation_open_max = np.maximum.reduce(validation_open_values)
    test_open_max = np.maximum.reduce(test_open_values)
    validation_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in validation_open_values], axis=0
    )
    test_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in test_open_values], axis=0
    )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.pt"
    torch.save(
        {
            "state_dict": best_state,
            "known_class_names": known_class_names,
            "sequence_length": packet_lengths.shape[1],
            "flow_statistic_names": statistic_names.tolist(),
            "flow_statistic_scaling": scaling_report,
            "architecture": architecture_name,
            "statistics_zeroed_during_evaluation": (
                args.statistic_modality_dropout_probability == 1.0
            ),
        },
        model_path,
    )
    scores_path = output_dir / "scores.npz"
    score_arrays: dict[str, Any] = {
        "validation_attack_probability": validation_attack_variants[
            "attack_head"
        ],
        "validation_open_max": validation_open_max,
        "validation_open_noisy_or": validation_open_noisy_or,
        "validation_family_uncertainty_tail": validation_tail[
            "family_uncertainty"
        ],
        "validation_knownness_uncertainty_tail": validation_knownness_tail,
        "validation_prototype_distance_tail": validation_tail[
            "prototype_distance"
        ],
        "validation_benign_distance_tail": validation_tail["benign_distance"],
        "validation_type_prediction": validation_probability.argmax(axis=1),
        "validation_labels": validation_labels_np,
        "test_attack_probability": test_attack_variants["attack_head"],
        "test_open_max": test_open_max,
        "test_open_noisy_or": test_open_noisy_or,
        "test_family_uncertainty_tail": test_tail["family_uncertainty"],
        "test_knownness_uncertainty_tail": test_knownness_tail,
        "test_prototype_distance_tail": test_tail["prototype_distance"],
        "test_benign_distance_tail": test_tail["benign_distance"],
        "test_type_prediction": test_probability.argmax(axis=1),
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "known_class_names": np.asarray(known_class_names),
    }
    for variant, values in validation_attack_variants.items():
        score_arrays[f"validation_{variant}_attack_probability"] = values
    for variant, values in test_attack_variants.items():
        score_arrays[f"test_{variant}_attack_probability"] = values
    np.savez_compressed(scores_path, **score_arrays)
    own_pid = os.getpid()
    peak_utilization = max(
        (sample["utilization_percent"] for sample in sampler.samples),
        default=0.0,
    )
    peak_memory = max(
        (sample["memory_used_mib"] for sample in sampler.samples), default=0.0
    )
    own_pid_observed = any(
        any(
            int(process["pid"]) == own_pid
            for process in sample["compute_processes"]
        )
        for sample in sampler.samples
    )
    compute_process_observed = any(
        sample["compute_processes"] for sample in sampler.samples
    )
    torch_peak_allocated_mib = (
        float(torch.cuda.max_memory_allocated(device)) / (1024.0 * 1024.0)
    )
    torch_peak_reserved_mib = (
        float(torch.cuda.max_memory_reserved(device)) / (1024.0 * 1024.0)
    )
    gpu_passes = (
        torch.cuda.is_available()
        and initial_gpu["uuid"] == args.required_gpu_uuid
        and compute_process_observed
        and torch_peak_allocated_mib > 1.0
        and torch_peak_reserved_mib > 1.0
        and peak_utilization > 0.0
        and peak_memory > 1.0
        and not sampler.errors
    )
    gpu_evidence: dict[str, Any] = {
        "schema_version": (
            "strict_v4_family_heldout_meta_cuda_task_evidence_v1"
            if meta_enabled
            else "strict_v4_dual_metric_contrastive_cuda_task_evidence_v1"
        ),
        "state": "complete",
        "requested_device": "cuda:0",
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "gpu_identity": {
            key: initial_gpu[key] for key in ("index", "name", "uuid")
        },
        "own_pid": own_pid,
        "own_pid_observed_by_nvidia_smi": own_pid_observed,
        "nvidia_smi_pid_namespace_matches_container": own_pid_observed,
        "nvidia_smi_pid_namespace_match_required": False,
        "compute_process_observed_by_nvidia_smi": compute_process_observed,
        "torch_cuda_sentinel": {
            "device": str(sentinel.device),
            "finite_checksum": sentinel_checksum,
        },
        "torch_peak_memory_allocated_mib": torch_peak_allocated_mib,
        "torch_peak_memory_reserved_mib": torch_peak_reserved_mib,
        "sample_count": len(sampler.samples),
        "samples": sampler.samples,
        "sample_errors": sampler.errors,
        "peak_gpu_utilization_percent": peak_utilization,
        "peak_gpu_memory_mib": peak_memory,
        "passes": gpu_passes,
    }
    gpu_evidence["manifest_sha256"] = canonical_hash(gpu_evidence)
    atomic_json(output_dir / "gpu_execution.json", gpu_evidence)
    split_count_report = {
        split: dict(sorted(Counter(families[indices].tolist()).items()))
        for split, indices in splits.items()
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_family_heldout_meta_cuda_task_v1"
            if meta_enabled
            else "strict_v4_dual_metric_contrastive_cuda_task_v1"
        ),
        "state": "complete",
        "task": {
            "unknown_family": args.unknown_family,
            "seed": args.seed,
        },
        "known_class_names": known_class_names,
        "benign_index": benign_index,
        "split_counts": split_count_report,
        "model": {
            "name": algorithm_name,
            "architecture": architecture_name,
            "sequence_channels": [
                "signed_packet_length",
                "absolute_packet_length",
                "log_interarrival_time",
                "valid_packet_mask",
            ],
            "sequence_length": int(packet_lengths.shape[1]),
            "flow_statistic_dimension": int(statistic_names.size),
            "flow_statistic_names": statistic_names.tolist(),
            "flow_statistic_scaling": scaling_report,
            "active_modalities": (
                ["packet_sequence"]
                if args.statistic_modality_dropout_probability == 1.0
                else ["packet_sequence", "flow_statistics"]
            ),
            "parameter_count": int(
                sum(parameter.numel() for parameter in model.parameters())
            ),
            "best_epoch": best_epoch,
            "best_validation_loss": best_validation,
            "epochs_completed": len(history),
            "type_prototype": prototype_report,
            "attack_benign_prototype": benign_prototype_report,
            "attack_probability_variants": sorted(
                validation_attack_variants
            ),
            "knownness_evidence": (
                "maximum_of_knownness_head_and_cosine_prototype_tail"
            ),
        },
        "training": {
            "elapsed_seconds": elapsed_seconds,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "attack_loss_weight": args.attack_loss_weight,
            "knownness_loss_weight": args.knownness_loss_weight,
            "family_contrastive_loss_weight": (
                args.family_contrastive_loss_weight
            ),
            "attack_contrastive_loss_weight": (
                args.attack_contrastive_loss_weight
            ),
            "pseudo_mix_loss_weight": args.pseudo_mix_loss_weight,
            "episodic_margin_loss_weight": args.episodic_margin_loss_weight,
            "statistic_modality_dropout_probability": (
                args.statistic_modality_dropout_probability
            ),
            "statistics_zeroed_during_evaluation": (
                args.statistic_modality_dropout_probability == 1.0
            ),
            "meta_heldout_loss_weight": args.meta_heldout_loss_weight,
            "meta_inner_learning_rate": args.meta_inner_learning_rate,
            "meta_episode_rows_per_class": args.meta_episode_rows_per_class,
            "meta_attack_families": [
                known_class_names[index] for index in attack_class_indices
            ],
            "contrastive_temperature": args.contrastive_temperature,
            "cosine_scale": args.cosine_scale,
            "known_similarity_margin": args.known_similarity_margin,
            "pseudo_unknown_similarity_margin": (
                args.pseudo_unknown_similarity_margin
            ),
            "history": history,
        },
        "gpu_execution": {
            "file": "gpu_execution.json",
            "file_sha256": file_hash(output_dir / "gpu_execution.json"),
            "manifest_sha256": gpu_evidence["manifest_sha256"],
            "passes": gpu_passes,
        },
        "artifacts": {
            "model": {"file": model_path.name, "sha256": file_hash(model_path)},
            "scores": {
                "file": scores_path.name,
                "sha256": file_hash(scores_path),
            },
        },
        "source": {
            "sequence_dataset": str(args.sequence_dataset.resolve()),
            "sequence_dataset_sha256": file_hash(
                args.sequence_dataset.resolve()
            ),
        },
        "claim_boundary": {
            "development_seed_only": True,
            "unknown_family_excluded_from_train_and_validation": True,
            "unknown_or_test_labels_used_for_fitting_or_early_stopping": False,
            "true_unknown_used_for_final_configuration_selection": False,
            "formal_model_training_uses_cuda": True,
            "packet_sequence_and_flow_statistics_fused": (
                args.statistic_modality_dropout_probability < 1.0
            ),
            "flow_statistic_scaling_fit_on_training_split_only": True,
            "pseudo_unknowns_derived_from_known_training_families_only": True,
            "episodic_leave_one_family_uses_known_training_labels_only": True,
            "differentiable_family_heldout_meta_objective_enabled": (
                meta_enabled
            ),
            "meta_outer_episode_uses_heldout_known_family_and_benign_only": (
                meta_enabled
            ),
            "nvidia_smi_reports_host_namespace_pids_not_container_pids": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_dir / "metrics.json", report)
    if not gpu_passes:
        raise RuntimeError("DMC-CAEOS CUDA execution evidence did not pass")
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--unknown-family", required=True)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--required-gpu-uuid", required=True)
    parser.add_argument("--gpu-index", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=160)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--inference-batch-size", type=int, default=4096)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--weight-decay", type=float, default=0.0001)
    parser.add_argument("--attack-loss-weight", type=float, default=1.0)
    parser.add_argument("--knownness-loss-weight", type=float, default=0.2)
    parser.add_argument(
        "--family-contrastive-loss-weight", type=float, default=0.10
    )
    parser.add_argument(
        "--attack-contrastive-loss-weight", type=float, default=0.30
    )
    parser.add_argument("--pseudo-mix-loss-weight", type=float, default=0.25)
    parser.add_argument(
        "--episodic-margin-loss-weight", type=float, default=0.15
    )
    parser.add_argument(
        "--statistic-modality-dropout-probability",
        type=float,
        default=0.5,
    )
    parser.add_argument("--meta-heldout-loss-weight", type=float, default=0.0)
    parser.add_argument("--meta-inner-learning-rate", type=float, default=0.05)
    parser.add_argument("--meta-episode-rows-per-class", type=int, default=64)
    parser.add_argument("--contrastive-temperature", type=float, default=0.12)
    parser.add_argument("--pseudo-mix-lambda", type=float, default=0.5)
    parser.add_argument("--cosine-scale", type=float, default=16.0)
    parser.add_argument("--known-similarity-margin", type=float, default=0.35)
    parser.add_argument(
        "--pseudo-unknown-similarity-margin", type=float, default=0.15
    )
    parser.add_argument("--early-stopping-patience", type=int, default=24)
    parser.add_argument("--minimum-improvement", type=float, default=0.0001)
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.2)
    return parser.parse_args()


def main() -> None:
    report = train_task(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

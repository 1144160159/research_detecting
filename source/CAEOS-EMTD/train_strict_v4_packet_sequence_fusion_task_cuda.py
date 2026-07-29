from __future__ import annotations

import argparse
import copy
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
from verify_xgboost_cuda_backend import GPUSampler, query_gpu


BENIGN_FAMILY = "Benign"


def hash_rank(flow_id: str, seed: int) -> int:
    import hashlib

    digest = hashlib.sha256(f"{seed}\0{flow_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def stratified_open_set_split(
    flow_ids: np.ndarray,
    families: np.ndarray,
    *,
    unknown_family: str,
    seed: int,
) -> dict[str, np.ndarray]:
    train: list[int] = []
    validation: list[int] = []
    test: list[int] = []
    unique_families = sorted(str(value) for value in np.unique(families))
    if unknown_family not in unique_families or unknown_family == BENIGN_FAMILY:
        raise ValueError(f"invalid unknown attack family: {unknown_family}")
    for family in unique_families:
        indices = np.flatnonzero(families == family).tolist()
        indices.sort(key=lambda index: hash_rank(str(flow_ids[index]), seed))
        if family == unknown_family:
            test.extend(indices)
            continue
        count = len(indices)
        if count < 5:
            raise ValueError(f"known family {family} has fewer than five flows")
        train_count = max(1, int(math.floor(count * 0.6)))
        validation_count = max(1, int(math.floor(count * 0.2)))
        if train_count + validation_count >= count:
            validation_count = max(1, count - train_count - 1)
        train.extend(indices[:train_count])
        validation.extend(indices[train_count : train_count + validation_count])
        test.extend(indices[train_count + validation_count :])
    return {
        "train": np.asarray(sorted(train), dtype=np.int64),
        "validation": np.asarray(sorted(validation), dtype=np.int64),
        "test": np.asarray(sorted(test), dtype=np.int64),
    }


def sequence_channels(
    packet_lengths: np.ndarray,
    interarrival_us: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    signed = np.clip(packet_lengths.astype(np.float32) / 1500.0, -4.0, 4.0)
    absolute = np.clip(np.abs(packet_lengths).astype(np.float32) / 1500.0, 0.0, 4.0)
    timing = np.log1p(np.maximum(interarrival_us, 0.0)).astype(np.float32)
    timing /= np.float32(np.log1p(1_000_000_000.0))
    valid = mask.astype(np.float32)
    return np.stack((signed, absolute, timing, valid), axis=1)


def robust_scale_statistics(
    values: np.ndarray,
    train_indices: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    values = np.asarray(values, dtype=np.float32)
    if values.ndim != 2 or values.shape[1] == 0:
        raise ValueError("flow statistics must be a nonempty matrix")
    training = values[np.asarray(train_indices, dtype=np.int64)]
    medians = np.zeros(values.shape[1], dtype=np.float32)
    scales = np.ones(values.shape[1], dtype=np.float32)
    inactive = []
    for index in range(values.shape[1]):
        finite = training[:, index][np.isfinite(training[:, index])]
        if finite.size == 0:
            inactive.append(index)
            continue
        median = float(np.median(finite))
        scale = float(np.percentile(finite, 75) - np.percentile(finite, 25))
        medians[index] = median
        scales[index] = max(scale, 1e-6)
    finite_values = np.where(np.isfinite(values), values, medians[None, :])
    scaled = np.clip(
        (finite_values - medians[None, :]) / scales[None, :],
        -10.0,
        10.0,
    ).astype(np.float32)
    return scaled, {
        "fit_rows": int(training.shape[0]),
        "dimension": int(values.shape[1]),
        "median": medians.tolist(),
        "iqr_scale": scales.tolist(),
        "inactive_all_nonfinite_indices": inactive,
        "clip_interval": [-10.0, 10.0],
        "fit_on_training_split_only": True,
    }


def class_weights(labels: np.ndarray, number_of_classes: int) -> np.ndarray:
    counts = np.bincount(labels, minlength=number_of_classes).astype(np.float64)
    if np.any(counts <= 0):
        raise ValueError(f"training split misses known classes: {counts.tolist()}")
    weights = np.sqrt(counts.sum() / (number_of_classes * counts))
    return (weights / weights.mean()).astype(np.float32)


def tail_percentile(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    reference = np.sort(np.asarray(reference, dtype=np.float64))
    if reference.size == 0:
        raise ValueError("tail percentile reference is empty")
    ranks = np.searchsorted(reference, values, side="right")
    return np.asarray((ranks + 0.5) / (reference.size + 1.0), dtype=np.float64)


def build_model(
    torch: Any,
    number_of_classes: int,
    sequence_length: int,
    statistic_dimension: int = 0,
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

    class PacketSequenceFusion(nn.Module):
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
            self.statistic_encoder = (
                nn.Sequential(
                    nn.Linear(statistic_dimension, 128),
                    nn.LayerNorm(128),
                    nn.GELU(),
                    nn.Dropout(0.15),
                    nn.Linear(128, 64),
                    nn.GELU(),
                )
                if statistic_dimension > 0
                else None
            )
            self.embedding = nn.Sequential(
                nn.Linear(
                    channels * 2 + (64 if statistic_dimension > 0 else 0),
                    192,
                ),
                nn.GELU(),
                nn.Dropout(0.15),
                nn.Linear(192, 128),
            )
            self.family_head = nn.Linear(128, number_of_classes)
            self.attack_head = nn.Linear(128, 1)
            self.knownness_head = nn.Linear(128, 1)

        def forward(
            self, values: Any, statistics: Any | None = None
        ) -> tuple[Any, Any, Any, Any]:
            mask = values[:, 3:4, :]
            encoded = self.stem(values) + self.position
            encoded = self.blocks(encoded) * mask
            denominator = mask.sum(dim=2).clamp_min(1.0)
            mean_pool = encoded.sum(dim=2) / denominator
            minimum = torch.finfo(encoded.dtype).min
            max_pool = encoded.masked_fill(mask == 0, minimum).amax(dim=2)
            max_pool = torch.where(
                torch.isfinite(max_pool), max_pool, torch.zeros_like(max_pool)
            )
            fused = torch.cat((mean_pool, max_pool), dim=1)
            if self.statistic_encoder is not None:
                if statistics is None:
                    raise ValueError("flow statistics are required by this model")
                fused = torch.cat(
                    (fused, self.statistic_encoder(statistics)), dim=1
                )
            embedding = self.embedding(fused)
            normalized = torch.nn.functional.normalize(embedding, dim=1)
            return (
                normalized,
                self.family_head(normalized),
                self.attack_head(normalized).squeeze(1),
                self.knownness_head(normalized).squeeze(1),
            )

    return PacketSequenceFusion()


def batched_inference(
    *,
    torch: Any,
    model: Any,
    features: Any,
    statistics: Any | None,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    embeddings = []
    family_logits = []
    attack_logits = []
    knownness_logits = []
    model.eval()
    with torch.no_grad():
        for start in range(0, features.shape[0], batch_size):
            batch = features[start : start + batch_size]
            batch_statistics = (
                None
                if statistics is None
                else statistics[start : start + batch_size]
            )
            with torch.cuda.amp.autocast():
                embedding, family, attack, knownness = model(
                    batch, batch_statistics
                )
            embeddings.append(embedding.float().cpu().numpy())
            family_logits.append(family.float().cpu().numpy())
            attack_logits.append(attack.float().cpu().numpy())
            knownness_logits.append(knownness.float().cpu().numpy())
    return (
        np.concatenate(embeddings),
        np.concatenate(family_logits),
        np.concatenate(attack_logits),
        np.concatenate(knownness_logits),
    )


def sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values.astype(np.float64), -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def softmax(values: np.ndarray) -> np.ndarray:
    shifted = values.astype(np.float64) - values.max(axis=1, keepdims=True)
    exponent = np.exp(shifted)
    return exponent / exponent.sum(axis=1, keepdims=True)


def prototype_distance(
    train_embeddings: np.ndarray,
    train_labels: np.ndarray,
    values: np.ndarray,
    number_of_classes: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    prototypes = np.stack(
        [
            train_embeddings[train_labels == label].mean(axis=0)
            for label in range(number_of_classes)
        ]
    )
    within = np.concatenate(
        [
            np.sum(
                np.square(
                    train_embeddings[train_labels == label] - prototypes[label]
                ),
                axis=1,
            )
            for label in range(number_of_classes)
        ]
    )
    scale = float(max(np.median(within), 1e-6))
    distances = np.sum(
        np.square(values[:, None, :] - prototypes[None, :, :]), axis=2
    )
    return distances.min(axis=1) / scale, {
        "prototype_shape": list(prototypes.shape),
        "within_class_median_squared_distance": scale,
    }


def benign_prototype_distance(
    train_embeddings: np.ndarray,
    train_labels: np.ndarray,
    values: np.ndarray,
    benign_index: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    benign = train_embeddings[train_labels == benign_index]
    if benign.size == 0:
        raise ValueError("training split lacks benign embeddings")
    prototype = benign.mean(axis=0)
    within = np.sum(np.square(benign - prototype), axis=1)
    scale = float(max(np.median(within), 1e-6))
    distances = np.sum(np.square(values - prototype), axis=1) / scale
    return distances, {
        "benign_training_rows": int(benign.shape[0]),
        "within_benign_median_squared_distance": scale,
    }


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
        statistics = (
            np.asarray(source["flow_statistics"], dtype=np.float32)
            if "flow_statistics" in source.files
            else None
        )
        statistic_names = (
            np.asarray(source["flow_statistic_names"]).astype(str)
            if "flow_statistic_names" in source.files
            else np.asarray([], dtype=str)
        )
    if not (
        packet_lengths.shape == interarrival_us.shape == mask.shape
        and packet_lengths.shape[0] == flow_ids.size == families.size
    ):
        raise ValueError("packet sequence dataset array shapes are inconsistent")
    if args.require_flow_statistics and statistics is None:
        raise ValueError("packet sequence dataset lacks required flow statistics")
    if statistics is not None and (
        statistics.ndim != 2
        or statistics.shape[0] != flow_ids.size
        or statistic_names.size != statistics.shape[1]
    ):
        raise ValueError("flow statistic dataset array shapes are inconsistent")
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
        [class_to_index.get(family, -1) for family in families], dtype=np.int64
    )
    channels = sequence_channels(packet_lengths, interarrival_us, mask)
    feature_tensor = torch.from_numpy(channels).to(device)
    scaling_report = None
    statistic_tensor = None
    if statistics is not None:
        scaled_statistics, scaling_report = robust_scale_statistics(
            statistics, splits["train"]
        )
        statistic_tensor = torch.from_numpy(scaled_statistics).to(device)
    label_tensor = torch.from_numpy(encoded_labels).to(device)
    train_indices = torch.from_numpy(splits["train"]).to(device)
    validation_indices = torch.from_numpy(splits["validation"]).to(device)
    model = build_model(
        torch,
        len(known_class_names),
        packet_lengths.shape[1],
        0 if statistics is None else statistics.shape[1],
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
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
            for start in range(0, permutation.numel(), args.batch_size):
                indices = permutation[start : start + args.batch_size]
                batch_values = feature_tensor[indices]
                batch_statistics = (
                    None
                    if statistic_tensor is None
                    else statistic_tensor[indices]
                )
                batch_labels = label_tensor[indices]
                batch_attack = (batch_labels != benign_index).float()
                optimizer.zero_grad(set_to_none=True)
                with torch.cuda.amp.autocast():
                    embedding, family_logits, attack_logits, knownness_logits = model(
                        batch_values, batch_statistics
                    )
                    base_loss = (
                        family_loss(family_logits, batch_labels)
                        + args.attack_loss_weight
                        * attack_loss(attack_logits, batch_attack)
                        + args.knownness_loss_weight
                        * knownness_loss(
                            knownness_logits,
                            torch.ones_like(knownness_logits),
                        )
                    )
                    rotated = torch.roll(
                        torch.arange(batch_labels.numel(), device=device), 1
                    )
                    different = batch_labels != batch_labels[rotated]
                    if different.any():
                        mixed = 0.5 * (
                            embedding[different]
                            + embedding[rotated[different]]
                        )
                        mixed_logits = model.knownness_head(mixed).squeeze(1)
                        base_loss = (
                            base_loss
                            + args.boundary_mix_loss_weight
                            * knownness_loss(
                                mixed_logits, torch.zeros_like(mixed_logits)
                            )
                        )
                scaler.scale(base_loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                scaler.step(optimizer)
                scaler.update()
                training_losses.append(float(base_loss.detach().cpu()))
            scheduler.step()
            model.eval()
            with torch.no_grad(), torch.cuda.amp.autocast():
                _, validation_family, validation_attack, validation_knownness = model(
                    feature_tensor[validation_indices],
                    (
                        None
                        if statistic_tensor is None
                        else statistic_tensor[validation_indices]
                    ),
                )
                validation_labels = label_tensor[validation_indices]
                validation_target = (
                    validation_labels != benign_index
                ).float()
                validation_loss = (
                    family_loss(validation_family, validation_labels)
                    + args.attack_loss_weight
                    * attack_loss(validation_attack, validation_target)
                    + args.knownness_loss_weight
                    * knownness_loss(
                        validation_knownness,
                        torch.ones_like(validation_knownness),
                    )
                )
            validation_value = float(validation_loss.float().cpu())
            history.append(
                {
                    "epoch": epoch,
                    "training_loss": float(np.mean(training_losses)),
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
        train_embeddings, _, _, _ = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[train_indices],
            statistics=(
                None
                if statistic_tensor is None
                else statistic_tensor[train_indices]
            ),
            batch_size=args.inference_batch_size,
        )
        validation_arrays = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[validation_indices],
            statistics=(
                None
                if statistic_tensor is None
                else statistic_tensor[validation_indices]
            ),
            batch_size=args.inference_batch_size,
        )
        test_indices = torch.from_numpy(splits["test"]).to(device)
        test_arrays = batched_inference(
            torch=torch,
            model=model,
            features=feature_tensor[test_indices],
            statistics=(
                None
                if statistic_tensor is None
                else statistic_tensor[test_indices]
            ),
            batch_size=args.inference_batch_size,
        )
        torch.cuda.synchronize()
    finally:
        sampler.stop()
    elapsed_seconds = time.perf_counter() - started
    validation_embedding, validation_family, validation_attack, validation_knownness = (
        validation_arrays
    )
    test_embedding, test_family, test_attack, test_knownness = test_arrays
    validation_labels_np = encoded_labels[splits["validation"]]
    test_labels = encoded_labels[splits["test"]]
    test_unknown = families[splits["test"]] == args.unknown_family
    validation_probability = softmax(validation_family)
    test_probability = softmax(test_family)
    validation_prototype, prototype_report = prototype_distance(
        train_embeddings,
        encoded_labels[splits["train"]],
        validation_embedding,
        len(known_class_names),
    )
    test_prototype, _ = prototype_distance(
        train_embeddings,
        encoded_labels[splits["train"]],
        test_embedding,
        len(known_class_names),
    )
    validation_benign_distance, benign_prototype_report = benign_prototype_distance(
        train_embeddings,
        encoded_labels[splits["train"]],
        validation_embedding,
        benign_index,
    )
    test_benign_distance, _ = benign_prototype_distance(
        train_embeddings,
        encoded_labels[splits["train"]],
        test_embedding,
        benign_index,
    )
    validation_components = {
        "family_uncertainty": 1.0 - validation_probability.max(axis=1),
        "knownness_uncertainty": 1.0 - sigmoid(validation_knownness),
        "prototype_distance": validation_prototype,
        "benign_distance": validation_benign_distance,
    }
    test_components = {
        "family_uncertainty": 1.0 - test_probability.max(axis=1),
        "knownness_uncertainty": 1.0 - sigmoid(test_knownness),
        "prototype_distance": test_prototype,
        "benign_distance": test_benign_distance,
    }
    validation_tail = {
        name: tail_percentile(values, values)
        for name, values in validation_components.items()
    }
    test_tail = {
        name: tail_percentile(validation_components[name], values)
        for name, values in test_components.items()
    }
    validation_open_max = np.maximum.reduce(list(validation_tail.values()))
    test_open_max = np.maximum.reduce(list(test_tail.values()))
    validation_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in validation_tail.values()], axis=0
    )
    test_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in test_tail.values()], axis=0
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
            "architecture": "packet_sequence_statistic_fusion_multitask_v2",
        },
        model_path,
    )
    scores_path = output_dir / "scores.npz"
    np.savez_compressed(
        scores_path,
        validation_attack_probability=sigmoid(validation_attack),
        validation_open_max=validation_open_max,
        validation_open_noisy_or=validation_open_noisy_or,
        validation_family_uncertainty_tail=validation_tail["family_uncertainty"],
        validation_knownness_uncertainty_tail=validation_tail[
            "knownness_uncertainty"
        ],
        validation_prototype_distance_tail=validation_tail[
            "prototype_distance"
        ],
        validation_benign_distance_tail=validation_tail["benign_distance"],
        validation_type_prediction=validation_probability.argmax(axis=1),
        validation_labels=validation_labels_np,
        test_attack_probability=sigmoid(test_attack),
        test_open_max=test_open_max,
        test_open_noisy_or=test_open_noisy_or,
        test_family_uncertainty_tail=test_tail["family_uncertainty"],
        test_knownness_uncertainty_tail=test_tail["knownness_uncertainty"],
        test_prototype_distance_tail=test_tail["prototype_distance"],
        test_benign_distance_tail=test_tail["benign_distance"],
        test_type_prediction=test_probability.argmax(axis=1),
        test_labels=test_labels,
        test_unknown=test_unknown,
        known_class_names=np.asarray(known_class_names),
    )
    own_pid = os.getpid()
    peak_utilization = max(
        (sample["utilization_percent"] for sample in sampler.samples), default=0.0
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
        "schema_version": "strict_v4_packet_sequence_cuda_task_evidence_v1",
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
    split_counts = {
        split: dict(
            sorted(Counter(families[indices].tolist()).items())
        )
        for split, indices in splits.items()
    }
    report: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_cuda_task_v1",
        "state": "complete",
        "task": {
            "unknown_family": args.unknown_family,
            "seed": args.seed,
        },
        "known_class_names": known_class_names,
        "benign_index": benign_index,
        "split_counts": split_counts,
        "model": {
            "name": "PSF-CAEOS-F packet-sequence and flow-statistic fusion",
            "architecture": (
                "residual_dilated_cnn_statistic_mlp_multitask_boundary_mix_v2"
            ),
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
            "parameter_count": int(
                sum(parameter.numel() for parameter in model.parameters())
            ),
            "best_epoch": best_epoch,
            "best_validation_loss": best_validation,
            "epochs_completed": len(history),
            "prototype": prototype_report,
            "benign_prototype": benign_prototype_report,
        },
        "training": {
            "elapsed_seconds": elapsed_seconds,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "attack_loss_weight": args.attack_loss_weight,
            "knownness_loss_weight": args.knownness_loss_weight,
            "boundary_mix_loss_weight": args.boundary_mix_loss_weight,
            "history": history,
        },
        "gpu_execution": {
            "file": "gpu_execution.json",
            "file_sha256": file_hash(output_dir / "gpu_execution.json"),
            "manifest_sha256": gpu_evidence["manifest_sha256"],
            "passes": gpu_passes,
        },
        "artifacts": {
            "model": {"file": "model.pt", "sha256": file_hash(model_path)},
            "scores": {"file": "scores.npz", "sha256": file_hash(scores_path)},
        },
        "source": {
            "sequence_dataset": str(args.sequence_dataset.resolve()),
            "sequence_dataset_sha256": file_hash(args.sequence_dataset.resolve()),
        },
        "claim_boundary": {
            "development_seed_only": True,
            "unknown_family_excluded_from_train_and_validation": True,
            "unknown_or_test_labels_used_for_fitting_or_early_stopping": False,
            "true_unknown_used_for_final_configuration_selection": False,
            "formal_model_training_uses_cuda": True,
            "packet_sequence_model_only": statistics is None,
            "packet_sequence_and_flow_statistics_fused": statistics is not None,
            "flow_statistic_scaling_fit_on_training_split_only": (
                statistics is not None
            ),
            "nvidia_smi_reports_host_namespace_pids_not_container_pids": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_dir / "metrics.json", report)
    if not gpu_passes:
        raise RuntimeError("packet-sequence CUDA execution evidence did not pass")
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
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--inference-batch-size", type=int, default=4096)
    parser.add_argument("--learning-rate", type=float, default=0.002)
    parser.add_argument("--weight-decay", type=float, default=0.0001)
    parser.add_argument("--attack-loss-weight", type=float, default=1.0)
    parser.add_argument("--knownness-loss-weight", type=float, default=0.2)
    parser.add_argument("--boundary-mix-loss-weight", type=float, default=0.4)
    parser.add_argument("--early-stopping-patience", type=int, default=20)
    parser.add_argument("--minimum-improvement", type=float, default=0.0001)
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.2)
    parser.add_argument("--require-flow-statistics", action="store_true")
    return parser.parse_args()


def main() -> None:
    report = train_task(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

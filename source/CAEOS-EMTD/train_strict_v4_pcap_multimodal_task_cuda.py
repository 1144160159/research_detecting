from __future__ import annotations

import argparse
import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from torch import Tensor

from caeos.losses import compute_training_loss, supervised_contrastive_loss
from caeos.metrics import evaluate_open_set
from caeos.model import ConflictAwareEvidentialNet
from caeos.open_set import OpenSetCalibrator, learn_simplex_risk_weights
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)
from strict_v4_pcap_multimodal_protocol import (
    encode_known_labels,
    family_mapping,
    select_pseudo_unknown_fine_labels,
    split_capture_groups,
)


MODALITY_NAMES = (
    "payload_semantics",
    "packet_behavior",
    "packet_interaction_graph",
)

CALIBRATOR_WEIGHTS = {
    "base": None,
    "hierarchical_fine": {
        "uncertainty": 0.20,
        "conflict": 0.25,
        "distance": 0.15,
        "fine_distance": 0.25,
        "energy": 0.15,
    },
    "hierarchical_fine_max": {
        "uncertainty": 0.20,
        "conflict": 0.20,
        "distance": 0.20,
        "fine_distance": 0.20,
        "energy": 0.20,
    },
    "nested_pseudo_risk": {
        "uncertainty": 0.20,
        "conflict": 0.25,
        "distance": 0.15,
        "fine_distance": 0.25,
        "energy": 0.15,
    },
}

CALIBRATOR_AGGREGATION = {
    "base": "weighted_mean",
    "hierarchical_fine": "weighted_mean",
    "hierarchical_fine_max": "maximum",
    "nested_pseudo_risk": "weighted_mean",
}

FINE_PROTOTYPE_PROFILES = {
    "hierarchical_fine",
    "hierarchical_fine_max",
    "nested_pseudo_risk",
}

FAMILY_CROSSFIT_ALERT_PROFILES = {
    "family_crossfit_dual_alert",
    "family_crossfit_meta_select_dual_alert",
    "family_crossfit_meta_select_classscore_dual_alert",
    "family_crossfit_meta_select_classscore_component_dual_alert",
}


def validate_family_crossfit_settings(
    alert_profile: str,
    false_positive_budget: float,
    checkpoint_interval: int,
) -> None:
    if alert_profile not in FAMILY_CROSSFIT_ALERT_PROFILES:
        return
    if (
        not 0.0 < false_positive_budget < 0.5
        or checkpoint_interval <= 0
    ):
        raise ValueError("family-crossfit alert settings are invalid")


def initialize_cuda_device(device_index: int = 0) -> torch.device:
    torch.cuda.init()
    torch.cuda.set_device(device_index)
    device = torch.device("cuda", device_index)
    torch.cuda.reset_peak_memory_stats(device)
    return device


def tensors_for_indices(
    cache: dict[str, np.ndarray],
    labels: np.ndarray,
    indices: np.ndarray,
    device: torch.device,
) -> tuple[list[Tensor], Tensor, Tensor]:
    payload = cache["payload"][indices].astype(np.int64, copy=False)
    views = [
        torch.from_numpy(payload).to(
            device=device, dtype=torch.long
        ),
        torch.from_numpy(cache["sequence"][indices]).to(
            device=device, dtype=torch.float32
        ),
        torch.from_numpy(cache["graph"][indices]).to(
            device=device, dtype=torch.float32
        ),
    ]
    quality = torch.from_numpy(cache["quality"][indices]).to(
        device=device, dtype=torch.float32
    )
    target = torch.from_numpy(labels[indices]).to(
        device=device, dtype=torch.long
    )
    return views, quality, target


def tensors_for_cache(
    cache: dict[str, np.ndarray],
    device: torch.device,
) -> tuple[list[Tensor], Tensor]:
    count = len(cache["family"])
    indices = np.arange(count, dtype=np.int64)
    dummy_labels = np.zeros(count, dtype=np.int64)
    views, quality, _ = tensors_for_indices(
        cache, dummy_labels, indices, device
    )
    return views, quality


def engineering_behavior_features(
    cache: dict[str, np.ndarray],
    indices: np.ndarray,
    output: dict[str, Tensor],
) -> np.ndarray:
    sequence = cache["sequence"][indices].astype(np.float32, copy=False)
    if sequence.shape[1] % 6 != 0:
        raise ValueError("packet behavior sequence width is not divisible by 6")
    packet_count = sequence.shape[1] // 6
    sequence_view = sequence.reshape(-1, packet_count, 6)
    graph = cache["graph"][indices].astype(np.float32, copy=False)
    graph_node_width = packet_count * 5
    if graph.shape[1] < graph_node_width:
        raise ValueError("packet graph does not contain frozen node features")
    graph_nodes = graph[:, :graph_node_width]
    node_view = graph_nodes.reshape(-1, packet_count, 5)
    mask = node_view[:, :, 4] > 0.5
    denominator = np.maximum(mask.sum(axis=1, keepdims=True), 1)

    summaries = [
        mask.mean(axis=1, keepdims=True),
        sequence_view[:, :, 1].sum(axis=1, keepdims=True),
    ]
    for column in (0, 1, 4, 5):
        values = (
            np.abs(sequence_view[:, :, column])
            if column == 0
            else sequence_view[:, :, column]
        )
        masked = np.where(mask, values, 0.0)
        mean = masked.sum(axis=1, keepdims=True) / denominator
        variance = (
            np.where(mask, (values - mean) ** 2, 0.0).sum(
                axis=1, keepdims=True
            )
            / denominator
        )
        summaries.extend(
            [
                mean,
                np.sqrt(variance),
                np.where(mask, values, -np.inf)
                .max(axis=1, keepdims=True)
                .clip(min=0.0),
            ]
        )
    direction = sequence_view[:, :, 2]
    summaries.append(
        np.abs(
            np.where(mask, direction, 0.0).sum(
                axis=1, keepdims=True
            )
            / denominator
        )
    )
    adjacent_mask = mask[:, 1:] & mask[:, :-1]
    direction_switch = (
        adjacent_mask
        & (direction[:, 1:] != direction[:, :-1])
    )
    summaries.append(
        direction_switch.sum(axis=1, keepdims=True)
        / np.maximum(adjacent_mask.sum(axis=1, keepdims=True), 1)
    )
    summary = np.concatenate(summaries, axis=1).astype(np.float32)
    model_features = np.concatenate(
        [
            output["fused_embedding"].numpy(),
            output["fused_probability"].numpy(),
            output["fused_uncertainty"].numpy()[:, None],
            output["global_conflict"].numpy()[:, None],
            output["reliability"].numpy(),
            output["discount"].numpy(),
            output["fused_evidence"].numpy(),
            output["malicious_logit"].numpy()[:, None],
        ],
        axis=1,
    ).astype(np.float32)
    features = np.concatenate(
        [
            sequence,
            graph_nodes,
            cache["quality"][indices].astype(np.float32, copy=False),
            summary,
            model_features,
        ],
        axis=1,
    )
    if not np.isfinite(features).all():
        raise ValueError("engineering behavior features contain non-finite values")
    return features


def family_invariant_alert_features(
    cache: dict[str, np.ndarray],
    indices: np.ndarray,
    output: dict[str, Tensor],
) -> np.ndarray:
    payload = cache["payload"][indices].astype(np.uint16, copy=False)
    payload_valid = payload < 256
    payload_denominator = np.maximum(
        payload_valid.sum(axis=1, keepdims=True),
        1,
    )
    payload_values = np.where(payload_valid, payload, 0).astype(np.float32)
    payload_mean = (
        payload_values.sum(axis=1, keepdims=True)
        / payload_denominator
        / 255.0
    )
    payload_variance = (
        np.where(
            payload_valid,
            (payload_values / 255.0 - payload_mean) ** 2,
            0.0,
        ).sum(axis=1, keepdims=True)
        / payload_denominator
    )
    payload_probabilities = []
    for lower in range(0, 256, 16):
        selected = (
            payload_valid
            & (payload >= lower)
            & (payload < lower + 16)
        )
        payload_probabilities.append(
            selected.sum(axis=1, keepdims=True) / payload_denominator
        )
    payload_distribution = np.concatenate(
        payload_probabilities,
        axis=1,
    )
    payload_entropy = (
        -np.where(
            payload_distribution > 0.0,
            payload_distribution
            * np.log(payload_distribution.clip(min=1e-12)),
            0.0,
        ).sum(axis=1, keepdims=True)
        / math.log(16.0)
    )
    payload_summary = np.concatenate(
        [
            payload_valid.mean(axis=1, keepdims=True),
            (
                payload_valid & (payload != 0)
            ).sum(axis=1, keepdims=True)
            / payload_denominator,
            (
                payload_valid & (payload >= 32) & (payload <= 126)
            ).sum(axis=1, keepdims=True)
            / payload_denominator,
            (
                payload_valid & (payload >= 128)
            ).sum(axis=1, keepdims=True)
            / payload_denominator,
            payload_mean,
            np.sqrt(payload_variance),
            payload_entropy,
        ],
        axis=1,
    )

    sequence = cache["sequence"][indices].astype(np.float32, copy=False)
    if sequence.shape[1] % 6 != 0:
        raise ValueError("packet behavior sequence width is not divisible by 6")
    packet_count = sequence.shape[1] // 6
    sequence_view = sequence.reshape(-1, packet_count, 6)
    graph = cache["graph"][indices].astype(np.float32, copy=False)
    graph_node_width = packet_count * 5
    graph_edge_width = packet_count * packet_count
    if graph.shape[1] != graph_node_width + graph_edge_width:
        raise ValueError("packet graph width differs from frozen contract")
    node_view = graph[:, :graph_node_width].reshape(
        -1, packet_count, 5
    )
    node_mask = node_view[:, :, 4] > 0.5
    node_denominator = np.maximum(
        node_mask.sum(axis=1, keepdims=True),
        1,
    )
    sequence_summary_parts = [
        node_mask.mean(axis=1, keepdims=True),
        sequence_view[:, :, 1].sum(axis=1, keepdims=True),
    ]
    for column in (0, 1, 4, 5):
        values = (
            np.abs(sequence_view[:, :, column])
            if column == 0
            else sequence_view[:, :, column]
        )
        masked = np.where(node_mask, values, 0.0)
        mean = masked.sum(axis=1, keepdims=True) / node_denominator
        variance = (
            np.where(node_mask, (values - mean) ** 2, 0.0).sum(
                axis=1,
                keepdims=True,
            )
            / node_denominator
        )
        sequence_summary_parts.extend(
            [
                mean,
                np.sqrt(variance),
                np.where(node_mask, values, -np.inf)
                .max(axis=1, keepdims=True)
                .clip(min=0.0),
            ]
        )
    direction = sequence_view[:, :, 2]
    sequence_summary_parts.append(
        np.abs(
            np.where(node_mask, direction, 0.0).sum(
                axis=1,
                keepdims=True,
            )
            / node_denominator
        )
    )
    adjacent_mask = node_mask[:, 1:] & node_mask[:, :-1]
    sequence_summary_parts.append(
        (
            adjacent_mask
            & (direction[:, 1:] != direction[:, :-1])
        ).sum(axis=1, keepdims=True)
        / np.maximum(
            adjacent_mask.sum(axis=1, keepdims=True),
            1,
        )
    )
    sequence_summary = np.concatenate(
        sequence_summary_parts,
        axis=1,
    )

    adjacency = graph[:, graph_node_width:].reshape(
        -1,
        packet_count,
        packet_count,
    )
    active_edges = adjacency > 0.0
    edge_denominator = np.maximum(
        active_edges.sum(axis=(1, 2), keepdims=True),
        1,
    ).reshape(-1, 1)
    edge_sum = adjacency.sum(axis=(1, 2), keepdims=True).reshape(-1, 1)
    edge_mean = edge_sum / edge_denominator
    edge_variance = (
        np.where(
            active_edges,
            (adjacency - edge_mean[:, None, :]) ** 2,
            0.0,
        )
        .sum(axis=(1, 2), keepdims=True)
        .reshape(-1, 1)
        / edge_denominator
    )
    graph_summary = np.concatenate(
        [
            active_edges.mean(axis=(1, 2), keepdims=True).reshape(-1, 1),
            edge_mean,
            np.sqrt(edge_variance),
            adjacency.max(axis=(1, 2), keepdims=True).reshape(-1, 1),
            np.abs(adjacency - adjacency.transpose(0, 2, 1))
            .mean(axis=(1, 2), keepdims=True)
            .reshape(-1, 1),
        ],
        axis=1,
    )
    reliability = output["reliability"].numpy()
    discount = output["discount"].numpy()
    evidence_total = output["fused_evidence"].numpy().sum(
        axis=1,
        keepdims=True,
    )
    evidence_summary = np.concatenate(
        [
            output["fused_uncertainty"].numpy()[:, None],
            output["global_conflict"].numpy()[:, None],
            reliability.mean(axis=1, keepdims=True),
            reliability.std(axis=1, keepdims=True),
            discount.mean(axis=1, keepdims=True),
            discount.std(axis=1, keepdims=True),
            evidence_total,
            output["malicious_logit"].numpy()[:, None],
        ],
        axis=1,
    )
    features = np.concatenate(
        [
            payload_summary,
            sequence_summary,
            graph_summary,
            cache["quality"][indices].astype(np.float32, copy=False),
            evidence_summary,
        ],
        axis=1,
    ).astype(np.float32)
    if not np.isfinite(features).all():
        raise ValueError(
            "family-invariant alert features contain non-finite values"
        )
    return features


def subset_views(views: list[Tensor], indices: Tensor) -> list[Tensor]:
    return [view[indices] for view in views]


def class_balanced_epoch_indices(
    labels: Tensor, generator: torch.Generator
) -> Tensor:
    counts = torch.bincount(labels)
    maximum = int(counts.max().item())
    sampled = []
    for class_index in range(len(counts)):
        selected = torch.where(labels == class_index)[0]
        draw = torch.randint(
            len(selected),
            (maximum,),
            generator=generator,
            device=labels.device,
        )
        sampled.append(selected[draw])
    merged = torch.cat(sampled)
    return merged[
        torch.randperm(
            len(merged), generator=generator, device=labels.device
        )
    ]


def compact_output(output: dict[str, Tensor]) -> dict[str, Tensor]:
    required = (
        "fused_probability",
        "fused_belief",
        "fused_uncertainty",
        "global_conflict",
        "raw_conflict",
        "reliability",
        "discount",
        "fused_embedding",
        "fused_evidence",
        "malicious_logit",
    )
    return {
        name: output[name].detach().to(device="cpu", dtype=torch.float32)
        for name in required
    }


def classical_baseline_score_arrays(
    *,
    train_output: dict[str, Tensor],
    train_labels: Tensor,
    validation_output: dict[str, Tensor],
    validation_labels: Tensor,
    test_output: dict[str, Tensor],
    test_labels: Tensor,
    is_unknown: np.ndarray,
) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    splits = (
        ("train", train_output, train_labels),
        ("validation", validation_output, validation_labels),
        ("test", test_output, test_labels),
    )
    for split, output, labels in splits:
        evidence = output["fused_evidence"].detach().cpu()
        arrays[f"baseline_{split}_embedding"] = (
            output["fused_embedding"].detach().cpu().numpy()
        )
        arrays[f"baseline_{split}_log_evidence"] = (
            torch.log(evidence + 1e-6).numpy()
        )
        arrays[f"baseline_{split}_belief"] = (
            output["fused_belief"].detach().cpu().numpy()
        )
        arrays[f"baseline_{split}_label"] = (
            labels.detach().cpu().numpy().astype(np.int64, copy=False)
        )
    arrays["baseline_test_is_unknown"] = np.asarray(
        is_unknown, dtype=bool
    )
    return arrays


def risk_diagnostic_score_arrays(
    *,
    calibrator: OpenSetCalibrator,
    train_output: dict[str, Tensor],
    validation_output: dict[str, Tensor],
    test_output: dict[str, Tensor],
) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    splits = (
        ("train", train_output),
        ("validation", validation_output),
        ("test", test_output),
    )
    for split, output in splits:
        risk, maliciousness, normalized_components = calibrator.score(output)
        arrays[f"self_{split}_risk"] = risk.detach().cpu().numpy()
        arrays[f"self_{split}_maliciousness"] = (
            maliciousness.detach().cpu().numpy()
        )
        for name, values in normalized_components.items():
            arrays[f"self_{split}_{name}"] = (
                values.detach().cpu().numpy()
            )
        for name in (
            "fused_uncertainty",
            "global_conflict",
            "raw_conflict",
            "malicious_logit",
            "reliability",
            "discount",
        ):
            arrays[f"diagnostic_{split}_{name}"] = (
                output[name].detach().cpu().numpy()
            )
    return arrays


def external_surrogate_unknown_loss(
    output: dict[str, Tensor],
    evidence_weight: float,
    malicious_weight: float,
) -> dict[str, Tensor]:
    if evidence_weight < 0.0 or malicious_weight < 0.0:
        raise ValueError("external surrogate loss weights must be non-negative")
    probability = output["fused_probability"].clamp_min(1e-8)
    class_count = probability.shape[-1]
    uniform_kl = (
        probability
        * (probability.log() + math.log(float(class_count)))
    ).sum(dim=-1).mean()
    evidence_penalty = torch.log1p(
        output["fused_evidence"].sum(dim=-1)
    ).mean()
    malicious_loss = torch.nn.functional.binary_cross_entropy_with_logits(
        output["malicious_logit"],
        torch.ones_like(output["malicious_logit"]),
    )
    return {
        "total": (
            uniform_kl
            + evidence_weight * evidence_penalty
            + malicious_weight * malicious_loss
        ),
        "uniform_kl": uniform_kl,
        "evidence_penalty": evidence_penalty,
        "malicious_loss": malicious_loss,
    }


def cross_family_modality_counterfactuals(
    views: list[Tensor],
    quality: Tensor,
    labels: Tensor,
    modality_index: int,
) -> tuple[list[Tensor], Tensor, dict[str, Tensor | int]]:
    if len(views) < 2:
        raise ValueError("counterfactual mixing requires at least two modalities")
    if not 0 <= modality_index < len(views):
        raise ValueError("counterfactual modality index is out of range")
    if quality.ndim != 2 or quality.shape[1] != len(views):
        raise ValueError("counterfactual quality shape differs from modalities")
    if labels.ndim != 1 or len(labels) != len(quality):
        raise ValueError("counterfactual labels differ from sample count")
    if any(len(view) != len(labels) for view in views):
        raise ValueError("counterfactual view sample counts differ")

    attack_classes = sorted(
        int(value)
        for value in torch.unique(labels[labels != 0]).detach().cpu().tolist()
    )
    if len(attack_classes) < 2:
        raise ValueError(
            "counterfactual mixing requires two known attack families"
        )

    source_parts: list[Tensor] = []
    donor_parts: list[Tensor] = []
    for position, class_index in enumerate(attack_classes):
        source = torch.where(labels == class_index)[0]
        donors = torch.where((labels != 0) & (labels != class_index))[0]
        if len(source) == 0 or len(donors) == 0:
            raise ValueError("counterfactual family pairing is empty")
        offset = (modality_index + position) % len(donors)
        donor_position = (
            torch.arange(len(source), device=labels.device) + offset
        ) % len(donors)
        source_parts.append(source)
        donor_parts.append(donors[donor_position])

    source_indices = torch.cat(source_parts)
    donor_indices = torch.cat(donor_parts)
    source_labels = labels[source_indices]
    donor_labels = labels[donor_indices]
    if not bool((source_labels != donor_labels).all()):
        raise RuntimeError("counterfactual donor belongs to the source family")

    mixed_views = [view[source_indices].clone() for view in views]
    mixed_views[modality_index] = views[modality_index][donor_indices]
    mixed_quality = quality[source_indices].clone()
    mixed_quality[:, modality_index] = quality[
        donor_indices, modality_index
    ]
    evidence: dict[str, Tensor | int] = {
        "modality_index": modality_index,
        "source_indices": source_indices,
        "donor_indices": donor_indices,
        "source_labels": source_labels,
        "donor_labels": donor_labels,
    }
    return mixed_views, mixed_quality, evidence


@torch.no_grad()
def counterfactual_validation_metrics(
    model: ConflictAwareEvidentialNet,
    validation_views: list[Tensor],
    validation_quality: Tensor,
    validation_labels: Tensor,
    batch_size: int,
) -> dict[str, float]:
    uncertainty = []
    malicious_probability = []
    uniformity = []
    sample_count = 0
    for modality_index in range(len(validation_views)):
        mixed_views, mixed_quality, _ = (
            cross_family_modality_counterfactuals(
                validation_views,
                validation_quality,
                validation_labels,
                modality_index,
            )
        )
        output = infer(model, mixed_views, mixed_quality, batch_size)
        probability = output["fused_probability"].clamp_min(1e-8)
        class_count = probability.shape[-1]
        kl = (
            probability
            * (probability.log() + math.log(float(class_count)))
        ).sum(dim=-1)
        uncertainty.append(float(output["fused_uncertainty"].mean()))
        malicious_probability.append(
            float(torch.sigmoid(output["malicious_logit"]).mean())
        )
        uniformity.append(
            float(
                (
                    1.0
                    - kl / max(math.log(float(class_count)), 1e-8)
                )
                .clamp(0.0, 1.0)
                .mean()
            )
        )
        sample_count += len(mixed_quality)
    return {
        "counterfactual_sample_count": float(sample_count),
        "counterfactual_uncertainty": float(np.mean(uncertainty)),
        "counterfactual_malicious_probability": float(
            np.mean(malicious_probability)
        ),
        "counterfactual_uniformity": float(np.mean(uniformity)),
    }


@torch.no_grad()
def infer(
    model: ConflictAwareEvidentialNet,
    views: list[Tensor],
    quality: Tensor,
    batch_size: int,
) -> dict[str, Tensor]:
    model.eval()
    chunks: dict[str, list[Tensor]] = {}
    for start in range(0, len(quality), batch_size):
        selection = slice(start, start + batch_size)
        output = compact_output(
            model(
                [view[selection] for view in views],
                quality[selection],
            )
        )
        for name, values in output.items():
            chunks.setdefault(name, []).append(values)
    return {
        name: torch.cat(parts, dim=0) for name, parts in chunks.items()
    }


def train_model(
    model: ConflictAwareEvidentialNet,
    train_views: list[Tensor],
    train_quality: Tensor,
    train_labels: Tensor,
    train_fine_labels: Tensor,
    validation_views: list[Tensor],
    validation_quality: Tensor,
    validation_labels: Tensor,
    seed: int,
    epochs: int,
    patience: int,
    batch_size: int,
    learning_rate: float,
    fine_contrastive_weight: float,
    fine_contrastive_temperature: float,
    counterfactual_mix_weight: float = 0.0,
    counterfactual_evidence_weight: float = 0.05,
    counterfactual_malicious_weight: float = 0.5,
    external_surrogate_views: list[Tensor] | None = None,
    external_surrogate_quality: Tensor | None = None,
    external_surrogate_weight: float = 0.0,
    external_surrogate_evidence_weight: float = 0.05,
    external_surrogate_malicious_weight: float = 0.5,
) -> tuple[dict[str, Tensor], list[dict[str, float]], int]:
    surrogate_enabled = external_surrogate_views is not None
    if surrogate_enabled != (external_surrogate_quality is not None):
        raise ValueError(
            "external surrogate views and quality must be provided together"
        )
    if surrogate_enabled and external_surrogate_weight <= 0.0:
        raise ValueError("external surrogate weight must be positive")
    if not surrogate_enabled and external_surrogate_weight != 0.0:
        raise ValueError("external surrogate weight requires surrogate data")
    if (
        external_surrogate_evidence_weight < 0.0
        or external_surrogate_malicious_weight < 0.0
    ):
        raise ValueError("external surrogate component weights are invalid")
    if (
        counterfactual_mix_weight < 0.0
        or counterfactual_evidence_weight < 0.0
        or counterfactual_malicious_weight < 0.0
    ):
        raise ValueError("counterfactual loss weights are invalid")
    if counterfactual_mix_weight > 0.0:
        attack_classes = torch.unique(train_labels[train_labels != 0])
        if len(attack_classes) < 2:
            raise ValueError(
                "counterfactual exposure requires two known attack families"
            )
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=1e-4
    )
    generator = torch.Generator(device=train_labels.device)
    generator.manual_seed(seed)
    best_state: dict[str, Tensor] | None = None
    best_epoch = -1
    best_score = -math.inf
    stale = 0
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        model.train()
        order = class_balanced_epoch_indices(train_labels, generator)
        total_loss = 0.0
        total_fine_contrastive_loss = 0.0
        total_surrogate_loss = 0.0
        total_surrogate_uniform_kl = 0.0
        total_surrogate_evidence_penalty = 0.0
        total_surrogate_malicious_loss = 0.0
        total_counterfactual_loss = 0.0
        total_counterfactual_uniform_kl = 0.0
        total_counterfactual_evidence_penalty = 0.0
        total_counterfactual_malicious_loss = 0.0
        steps = 0
        for batch_number, start in enumerate(
            range(0, len(order), batch_size)
        ):
            indices = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            output = model(
                subset_views(train_views, indices),
                train_quality[indices],
            )
            losses = compute_training_loss(
                output,
                train_labels[indices],
                train_quality[indices],
                benign_index=0,
                epoch=epoch,
                annealing_epochs=min(10, epochs),
                center_weight=0.01,
                reliability_weight=0.15,
                malicious_weight=0.3,
            )
            fine_contrastive = supervised_contrastive_loss(
                output["fused_embedding"],
                train_fine_labels[indices],
                temperature=fine_contrastive_temperature,
            )
            losses["total"] = (
                losses["total"]
                + fine_contrastive_weight * fine_contrastive
            )
            batch_attack_classes = torch.unique(
                train_labels[indices][train_labels[indices] != 0]
            )
            if (
                counterfactual_mix_weight > 0.0
                and len(batch_attack_classes) >= 2
            ):
                mixed_views, mixed_quality, _ = (
                    cross_family_modality_counterfactuals(
                        subset_views(train_views, indices),
                        train_quality[indices],
                        train_labels[indices],
                        (epoch + batch_number) % len(train_views),
                    )
                )
                counterfactual_output = model(
                    mixed_views,
                    mixed_quality,
                )
                counterfactual_losses = external_surrogate_unknown_loss(
                    counterfactual_output,
                    evidence_weight=counterfactual_evidence_weight,
                    malicious_weight=counterfactual_malicious_weight,
                )
                losses["total"] = (
                    losses["total"]
                    + counterfactual_mix_weight
                    * counterfactual_losses["total"]
                )
                total_counterfactual_loss += float(
                    counterfactual_losses["total"].detach()
                )
                total_counterfactual_uniform_kl += float(
                    counterfactual_losses["uniform_kl"].detach()
                )
                total_counterfactual_evidence_penalty += float(
                    counterfactual_losses["evidence_penalty"].detach()
                )
                total_counterfactual_malicious_loss += float(
                    counterfactual_losses["malicious_loss"].detach()
                )
            if (
                external_surrogate_views is not None
                and external_surrogate_quality is not None
            ):
                surrogate_indices = torch.randint(
                    len(external_surrogate_quality),
                    (len(indices),),
                    generator=generator,
                    device=train_labels.device,
                )
                surrogate_output = model(
                    subset_views(
                        external_surrogate_views,
                        surrogate_indices,
                    ),
                    external_surrogate_quality[surrogate_indices],
                )
                surrogate_losses = external_surrogate_unknown_loss(
                    surrogate_output,
                    evidence_weight=(
                        external_surrogate_evidence_weight
                    ),
                    malicious_weight=(
                        external_surrogate_malicious_weight
                    ),
                )
                losses["total"] = (
                    losses["total"]
                    + external_surrogate_weight
                    * surrogate_losses["total"]
                )
                total_surrogate_loss += float(
                    surrogate_losses["total"].detach()
                )
                total_surrogate_uniform_kl += float(
                    surrogate_losses["uniform_kl"].detach()
                )
                total_surrogate_evidence_penalty += float(
                    surrogate_losses["evidence_penalty"].detach()
                )
                total_surrogate_malicious_loss += float(
                    surrogate_losses["malicious_loss"].detach()
                )
            losses["total"].backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            total_loss += float(losses["total"].detach())
            total_fine_contrastive_loss += float(
                fine_contrastive.detach()
            )
            steps += 1
        validation_output = infer(
            model,
            validation_views,
            validation_quality,
            batch_size,
        )
        prediction = (
            validation_output["fused_probability"].argmax(dim=-1).numpy()
        )
        truth = validation_labels.detach().cpu().numpy()
        macro_f1 = float(f1_score(truth, prediction, average="macro"))
        balanced = float(balanced_accuracy_score(truth, prediction))
        counterfactual_validation: dict[str, float] = {}
        if counterfactual_mix_weight > 0.0:
            counterfactual_validation = counterfactual_validation_metrics(
                model,
                validation_views,
                validation_quality,
                validation_labels,
                batch_size,
            )
            score = (
                0.4 * macro_f1
                + 0.4 * balanced
                + 0.1
                * counterfactual_validation[
                    "counterfactual_uncertainty"
                ]
                + 0.1
                * counterfactual_validation[
                    "counterfactual_malicious_probability"
                ]
            )
        else:
            score = 0.5 * (macro_f1 + balanced)
        history.append(
            {
                "epoch": float(epoch),
                "loss": total_loss / max(1, steps),
                "fine_contrastive_loss": (
                    total_fine_contrastive_loss / max(1, steps)
                ),
                "external_surrogate_loss": (
                    total_surrogate_loss / max(1, steps)
                ),
                "external_surrogate_uniform_kl": (
                    total_surrogate_uniform_kl / max(1, steps)
                ),
                "external_surrogate_evidence_penalty": (
                    total_surrogate_evidence_penalty / max(1, steps)
                ),
                "external_surrogate_malicious_loss": (
                    total_surrogate_malicious_loss / max(1, steps)
                ),
                "counterfactual_loss": (
                    total_counterfactual_loss / max(1, steps)
                ),
                "counterfactual_uniform_kl": (
                    total_counterfactual_uniform_kl / max(1, steps)
                ),
                "counterfactual_evidence_penalty": (
                    total_counterfactual_evidence_penalty / max(1, steps)
                ),
                "counterfactual_malicious_loss": (
                    total_counterfactual_malicious_loss / max(1, steps)
                ),
                "validation_macro_f1": macro_f1,
                "validation_balanced_accuracy": balanced,
                "validation_checkpoint_score": score,
                **counterfactual_validation,
            }
        )
        if score > best_score + 1e-5:
            best_score = score
            best_epoch = epoch
            best_state = {
                name: value.detach().cpu().clone()
                for name, value in model.state_dict().items()
            }
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break
    if best_state is None:
        raise RuntimeError("training did not produce a checkpoint")
    model.load_state_dict(best_state)
    return best_state, history, best_epoch


def quantile_higher(values: np.ndarray, quantile: float) -> float:
    try:
        return float(np.quantile(values, quantile, method="higher"))
    except TypeError:  # numpy < 1.22
        return float(np.quantile(values, quantile, interpolation="higher"))


@torch.no_grad()
def cosine_knn_distance(
    query_embeddings: Tensor,
    reference_embeddings: Tensor,
    k: int = 5,
    batch_size: int = 2048,
    device: torch.device | None = None,
) -> Tensor:
    if k <= 0 or batch_size <= 0:
        raise ValueError("k and batch size must be positive")
    if len(reference_embeddings) < k:
        raise ValueError("reference embeddings contain fewer than k samples")
    if device is None:
        device = query_embeddings.device
    reference = torch.nn.functional.normalize(
        reference_embeddings.to(device=device, dtype=torch.float32),
        dim=-1,
    )
    distances = []
    for start in range(0, len(query_embeddings), batch_size):
        query = torch.nn.functional.normalize(
            query_embeddings[start : start + batch_size].to(
                device=device,
                dtype=torch.float32,
            ),
            dim=-1,
        )
        similarity = query @ reference.transpose(0, 1)
        nearest = torch.topk(similarity, k=k, dim=1).values.mean(dim=1)
        distances.append((1.0 - nearest).to(device="cpu"))
    return torch.cat(distances)


def fit_binary_alert_head(
    train_embeddings: Tensor,
    train_labels: Tensor,
    seed: int,
    hidden_dim: int = 64,
    steps: int = 400,
    batch_size: int = 1024,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
    device: torch.device | None = None,
) -> tuple[torch.nn.Module, dict[str, float]]:
    if hidden_dim <= 0 or steps <= 0 or batch_size < 2:
        raise ValueError("binary alert head dimensions and counts must be positive")
    if learning_rate <= 0.0 or weight_decay < 0.0:
        raise ValueError("binary alert head optimizer settings are invalid")
    if device is None:
        device = train_embeddings.device
    embeddings = train_embeddings.to(device=device, dtype=torch.float32)
    binary_labels = (train_labels.to(device=device) != 0).to(torch.float32)
    benign_indices = torch.nonzero(
        binary_labels == 0,
        as_tuple=False,
    ).flatten()
    attack_indices = torch.nonzero(
        binary_labels == 1,
        as_tuple=False,
    ).flatten()
    if len(benign_indices) == 0 or len(attack_indices) == 0:
        raise ValueError("binary alert head requires benign and attack samples")

    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    head = torch.nn.Sequential(
        torch.nn.Linear(embeddings.shape[1], hidden_dim),
        torch.nn.GELU(),
        torch.nn.Linear(hidden_dim, 1),
    ).to(device)
    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)
    benign_batch = batch_size // 2
    attack_batch = batch_size - benign_batch
    final_loss = math.nan
    head.train()
    for _ in range(steps):
        selected_benign = benign_indices[
            torch.randint(
                len(benign_indices),
                (benign_batch,),
                generator=generator,
                device=device,
            )
        ]
        selected_attack = attack_indices[
            torch.randint(
                len(attack_indices),
                (attack_batch,),
                generator=generator,
                device=device,
            )
        ]
        selected = torch.cat((selected_benign, selected_attack))
        selected = selected[
            torch.randperm(
                len(selected),
                generator=generator,
                device=device,
            )
        ]
        optimizer.zero_grad(set_to_none=True)
        logits = head(embeddings[selected]).squeeze(-1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(
            logits,
            binary_labels[selected],
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(head.parameters(), 5.0)
        optimizer.step()
        final_loss = float(loss.detach())

    head.eval()
    with torch.no_grad():
        train_prediction = (
            torch.sigmoid(head(embeddings).squeeze(-1)) >= 0.5
        )
    evidence = {
        "binary_head_final_training_loss": final_loss,
        "binary_head_training_accuracy_at_0_5": float(
            (train_prediction == binary_labels.bool()).float().mean()
        ),
        "binary_head_training_benign_samples": float(len(benign_indices)),
        "binary_head_training_attack_samples": float(len(attack_indices)),
    }
    return head, evidence


@torch.no_grad()
def binary_alert_probability(
    head: torch.nn.Module,
    embeddings: Tensor,
    batch_size: int = 2048,
    device: torch.device | None = None,
) -> np.ndarray:
    if batch_size <= 0:
        raise ValueError("binary alert inference batch size must be positive")
    if device is None:
        device = embeddings.device
    head.eval()
    probabilities = []
    for start in range(0, len(embeddings), batch_size):
        batch = embeddings[start : start + batch_size].to(
            device=device,
            dtype=torch.float32,
        )
        probabilities.append(
            torch.sigmoid(head(batch).squeeze(-1)).to(device="cpu")
        )
    return torch.cat(probabilities).numpy()


def known_class_attack_probability(
    output: dict[str, Tensor],
) -> np.ndarray:
    probability = output["fused_probability"]
    if probability.ndim != 2 or probability.shape[1] < 2:
        raise ValueError(
            "known class attack probability requires benign plus attack classes"
        )
    score = 1.0 - probability[:, 0].detach().cpu().numpy()
    if not np.isfinite(score).all():
        raise ValueError("known class attack probability is not finite")
    return np.asarray(score, dtype=np.float64)


def probability_logit(probability: np.ndarray) -> np.ndarray:
    clipped = np.clip(
        np.asarray(probability, dtype=np.float64),
        1e-6,
        1.0 - 1e-6,
    )
    return np.log(clipped) - np.log1p(-clipped)


def fit_family_crossfit_alert(
    train_features: np.ndarray,
    train_labels: Tensor,
    validation_features: np.ndarray,
    validation_labels: Tensor,
    validation_capture_groups: np.ndarray,
    test_features: np.ndarray,
    *,
    seed: int,
    hidden_dim: int,
    steps: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    false_positive_budget: float,
    checkpoint_interval: int,
    device: torch.device,
    model_path: Path | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    if (
        hidden_dim <= 0
        or steps <= 0
        or batch_size < 4
        or checkpoint_interval <= 0
        or learning_rate <= 0.0
        or weight_decay < 0.0
    ):
        raise ValueError("family-crossfit head settings are invalid")
    if not 0.0 < false_positive_budget < 0.5:
        raise ValueError("family-crossfit false-positive budget is invalid")
    if train_features.ndim != 2 or validation_features.ndim != 2:
        raise ValueError("family-crossfit features must be matrices")
    if test_features.ndim != 2:
        raise ValueError("family-crossfit test features must be a matrix")
    if not (
        train_features.shape[1]
        == validation_features.shape[1]
        == test_features.shape[1]
    ):
        raise ValueError("family-crossfit feature widths differ")

    train_label_array = train_labels.detach().cpu().numpy().astype(np.int64)
    validation_label_array = (
        validation_labels.detach().cpu().numpy().astype(np.int64)
    )
    omitted_classes = sorted(
        class_index
        for class_index in set(train_label_array.tolist())
        if class_index != 0
    )
    if len(omitted_classes) < 2:
        raise ValueError(
            "family-crossfit requires at least two known attack families"
        )
    if set(omitted_classes) != set(
        validation_label_array[validation_label_array != 0].tolist()
    ):
        raise ValueError(
            "family-crossfit train and validation attack families differ"
        )

    train_tensor = torch.from_numpy(
        np.asarray(train_features, dtype=np.float32)
    ).to(device)
    validation_tensor = torch.from_numpy(
        np.asarray(validation_features, dtype=np.float32)
    ).to(device)
    test_tensor = torch.from_numpy(
        np.asarray(test_features, dtype=np.float32)
    ).to(device)
    train_label_tensor = torch.from_numpy(train_label_array).to(device)
    validation_margins = []
    test_margins = []
    head_records: list[dict[str, Any]] = []
    checkpoint_payload: list[dict[str, Any]] = []

    for head_offset, omitted_class in enumerate(omitted_classes):
        eligible = train_label_tensor != omitted_class
        eligible_classes = sorted(
            int(value)
            for value in torch.unique(
                train_label_tensor[eligible]
            ).detach().cpu().tolist()
        )
        if 0 not in eligible_classes or len(eligible_classes) < 2:
            raise ValueError(
                "family-crossfit episode lacks benign or attack training data"
            )
        eligible_indices = torch.nonzero(
            eligible, as_tuple=False
        ).flatten()
        feature_mean = train_tensor[eligible_indices].mean(dim=0)
        feature_scale = train_tensor[eligible_indices].std(
            dim=0, unbiased=False
        ).clamp_min(1e-4)
        normalized_train = (train_tensor - feature_mean) / feature_scale
        normalized_validation = (
            validation_tensor - feature_mean
        ) / feature_scale
        normalized_test = (test_tensor - feature_mean) / feature_scale

        episode_seed = seed + 1009 * (head_offset + 1)
        torch.manual_seed(episode_seed)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(episode_seed)
        head = torch.nn.Sequential(
            torch.nn.Linear(train_tensor.shape[1], hidden_dim),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, max(hidden_dim // 2, 8)),
            torch.nn.GELU(),
            torch.nn.Linear(max(hidden_dim // 2, 8), 1),
        ).to(device)
        optimizer = torch.optim.AdamW(
            head.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )
        generator = torch.Generator(device=device)
        generator.manual_seed(episode_seed)
        class_indices = {
            class_index: torch.nonzero(
                train_label_tensor == class_index,
                as_tuple=False,
            ).flatten()
            for class_index in eligible_classes
        }
        samples_per_class = max(
            2,
            batch_size // len(eligible_classes),
        )
        best_key: tuple[float, float, int] | None = None
        best_state: dict[str, Tensor] | None = None
        best_step = 0
        best_threshold = math.nan
        best_meta_recall = math.nan
        best_meta_mean_probability = math.nan
        final_loss = math.nan

        head.train()
        for step in range(1, steps + 1):
            selected_parts = []
            for class_index in eligible_classes:
                candidates = class_indices[class_index]
                selected_parts.append(
                    candidates[
                        torch.randint(
                            len(candidates),
                            (samples_per_class,),
                            generator=generator,
                            device=device,
                        )
                    ]
                )
            selected = torch.cat(selected_parts)
            selected = selected[
                torch.randperm(
                    len(selected),
                    generator=generator,
                    device=device,
                )
            ]
            target = (train_label_tensor[selected] != 0).to(
                torch.float32
            )
            optimizer.zero_grad(set_to_none=True)
            logits = head(normalized_train[selected]).squeeze(-1)
            loss = torch.nn.functional.binary_cross_entropy_with_logits(
                logits,
                target,
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(head.parameters(), 5.0)
            optimizer.step()
            final_loss = float(loss.detach())

            if (
                step % checkpoint_interval != 0
                and step != steps
            ):
                continue
            head.eval()
            with torch.no_grad():
                validation_probability = torch.sigmoid(
                    head(normalized_validation).squeeze(-1)
                ).detach().cpu().numpy()
            threshold, _ = calibrate_group_conservative_score_threshold(
                validation_probability,
                validation_label_array,
                validation_capture_groups,
                false_positive_budget,
            )
            pseudo_unknown = validation_label_array == omitted_class
            meta_recall = float(
                np.mean(
                    validation_probability[pseudo_unknown] > threshold
                )
            )
            meta_mean_probability = float(
                validation_probability[pseudo_unknown].mean()
            )
            candidate_key = (
                meta_recall,
                meta_mean_probability,
                -step,
            )
            if best_key is None or candidate_key > best_key:
                best_key = candidate_key
                best_state = {
                    name: value.detach().cpu().clone()
                    for name, value in head.state_dict().items()
                }
                best_step = step
                best_threshold = threshold
                best_meta_recall = meta_recall
                best_meta_mean_probability = meta_mean_probability
            head.train()

        if best_state is None:
            raise RuntimeError("family-crossfit checkpoint selection failed")
        head.load_state_dict(best_state)
        head.eval()
        with torch.no_grad():
            validation_probability = torch.sigmoid(
                head(normalized_validation).squeeze(-1)
            ).detach().cpu().numpy()
            test_probability = torch.sigmoid(
                head(normalized_test).squeeze(-1)
            ).detach().cpu().numpy()
        threshold_logit = float(
            probability_logit(np.asarray([best_threshold]))[0]
        )
        validation_margins.append(
            probability_logit(validation_probability) - threshold_logit
        )
        test_margins.append(
            probability_logit(test_probability) - threshold_logit
        )
        head_records.append(
            {
                "omitted_class_index": omitted_class,
                "eligible_class_indices": eligible_classes,
                "training_samples": int(eligible.sum().item()),
                "selected_step": best_step,
                "final_training_loss": final_loss,
                "benign_threshold": best_threshold,
                "pseudo_unknown_validation_recall": best_meta_recall,
                "pseudo_unknown_validation_mean_probability": (
                    best_meta_mean_probability
                ),
            }
        )
        checkpoint_payload.append(
            {
                "omitted_class_index": omitted_class,
                "state_dict": best_state,
                "feature_mean": feature_mean.detach().cpu(),
                "feature_scale": feature_scale.detach().cpu(),
                "benign_threshold": best_threshold,
                "selected_step": best_step,
            }
        )

    validation_margin_matrix = np.stack(validation_margins, axis=1)
    test_margin_matrix = np.stack(test_margins, axis=1)
    validation_score = validation_margin_matrix.mean(axis=1)
    test_score = test_margin_matrix.mean(axis=1)
    aggregate_threshold, benign_group_count = (
        calibrate_group_conservative_score_threshold(
            validation_score,
            validation_label_array,
            validation_capture_groups,
            false_positive_budget,
        )
    )
    oof_meta_recalls = {}
    for head_index, omitted_class in enumerate(omitted_classes):
        selected = validation_label_array == omitted_class
        oof_meta_recalls[str(omitted_class)] = float(
            np.mean(validation_margin_matrix[selected, head_index] > 0.0)
        )

    if model_path is not None:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "schema_version": "family_crossfit_alert_v1",
                "feature_count": int(train_features.shape[1]),
                "hidden_dim": hidden_dim,
                "heads": checkpoint_payload,
                "aggregate": "mean_per_head_benign_normalized_logit_margin",
                "aggregate_threshold": aggregate_threshold,
            },
            model_path,
        )
    evidence: dict[str, Any] = {
        "family_crossfit_feature_count": int(train_features.shape[1]),
        "family_crossfit_head_count": len(omitted_classes),
        "family_crossfit_omitted_class_indices": omitted_classes,
        "family_crossfit_heads": head_records,
        "family_crossfit_oof_meta_recalls": oof_meta_recalls,
        "family_crossfit_oof_meta_recall_mean": float(
            np.mean(list(oof_meta_recalls.values()))
        ),
        "family_crossfit_oof_meta_recall_worst": float(
            np.min(list(oof_meta_recalls.values()))
        ),
        "family_crossfit_aggregate": (
            "mean_per_head_benign_normalized_logit_margin"
        ),
        "family_crossfit_aggregate_threshold": aggregate_threshold,
        "family_crossfit_false_positive_budget": false_positive_budget,
        "family_crossfit_validation_benign_group_count": benign_group_count,
        "family_crossfit_true_unknown_used_for_training": False,
        "family_crossfit_true_unknown_used_for_model_selection": False,
        "family_crossfit_true_unknown_used_for_threshold": False,
        "family_crossfit_model_path": (
            str(model_path) if model_path is not None else None
        ),
        "family_crossfit_model_sha256": (
            file_hash(model_path)
            if model_path is not None
            else None
        ),
    }
    return test_score - aggregate_threshold, evidence


def select_family_crossfit_candidate(
    candidates: dict[str, tuple[np.ndarray, dict[str, Any]]],
) -> tuple[str, np.ndarray, dict[str, Any]]:
    if set(candidates) != {"high_capacity", "family_invariant"}:
        raise ValueError("family-crossfit meta candidates differ")
    priority = {"high_capacity": 0, "family_invariant": 1}
    for profile, (_, evidence) in candidates.items():
        for boundary in (
            "family_crossfit_true_unknown_used_for_training",
            "family_crossfit_true_unknown_used_for_model_selection",
            "family_crossfit_true_unknown_used_for_threshold",
        ):
            if evidence.get(boundary) is not False:
                raise ValueError(
                    f"{profile} lacks true-unknown isolation: {boundary}"
                )
    selected_profile = max(
        candidates,
        key=lambda profile: (
            float(
                candidates[profile][1][
                    "family_crossfit_oof_meta_recall_worst"
                ]
            ),
            float(
                candidates[profile][1][
                    "family_crossfit_oof_meta_recall_mean"
                ]
            ),
            priority[profile],
        ),
    )
    margin, evidence = candidates[selected_profile]
    candidate_audit = {
        profile: {
            "feature_count": int(
                candidate_evidence["family_crossfit_feature_count"]
            ),
            "oof_meta_recall_worst": float(
                candidate_evidence[
                    "family_crossfit_oof_meta_recall_worst"
                ]
            ),
            "oof_meta_recall_mean": float(
                candidate_evidence[
                    "family_crossfit_oof_meta_recall_mean"
                ]
            ),
            "model_sha256": candidate_evidence[
                "family_crossfit_model_sha256"
            ],
        }
        for profile, (_, candidate_evidence) in candidates.items()
    }
    selected_evidence = {
        **evidence,
        "family_crossfit_selected_feature_profile": selected_profile,
        "family_crossfit_meta_selection_key": (
            "known_only_oof_worst_recall_then_mean_recall_then_lower_capacity"
        ),
        "family_crossfit_meta_candidates": candidate_audit,
        "family_crossfit_meta_true_unknown_scores_used": False,
    }
    return selected_profile, margin, selected_evidence


def fit_xgboost_behavior_alert(
    train_features: np.ndarray,
    train_labels: Tensor,
    validation_features: np.ndarray,
    validation_labels: Tensor,
    seed: int,
    estimators: int,
    max_depth: int,
    learning_rate: float,
    early_stopping_rounds: int,
    jobs: int,
    model_path: Path,
    xgboost_root: Path | None = None,
) -> tuple[Any, dict[str, Any]]:
    if (
        estimators <= 0
        or max_depth <= 0
        or learning_rate <= 0.0
        or early_stopping_rounds <= 0
        or jobs <= 0
    ):
        raise ValueError("XGBoost behavior alert settings are invalid")
    if xgboost_root is not None:
        resolved_root = xgboost_root.resolve()
        if str(resolved_root) not in sys.path:
            sys.path.insert(0, str(resolved_root))
    try:
        import xgboost
        from xgboost import XGBClassifier
    except ImportError as exc:  # pragma: no cover - GPU dependency gate
        raise RuntimeError("xgboost is required for behavior alert") from exc
    package_root = Path(xgboost.__file__).resolve().parent
    library_path = package_root / "lib" / "libxgboost.so"
    if not library_path.is_file():
        raise RuntimeError("xgboost shared library is missing")
    binary_train = (
        train_labels.detach().cpu().numpy() != 0
    ).astype(np.int64)
    binary_validation = (
        validation_labels.detach().cpu().numpy() != 0
    ).astype(np.int64)
    counts = np.bincount(binary_train, minlength=2)
    if np.any(counts == 0):
        raise ValueError(
            "XGBoost behavior alert requires benign and attack training data"
        )
    train_weights = len(binary_train) / (2.0 * counts[binary_train])
    validation_counts = np.bincount(binary_validation, minlength=2)
    validation_weights = len(binary_validation) / (
        2.0 * np.maximum(validation_counts[binary_validation], 1)
    )
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_weight=2.0,
        reg_lambda=1.0,
        tree_method="hist",
        device="cuda",
        early_stopping_rounds=early_stopping_rounds,
        n_jobs=jobs,
        random_state=seed,
    )
    model.fit(
        train_features,
        binary_train,
        sample_weight=train_weights,
        eval_set=[(validation_features, binary_validation)],
        sample_weight_eval_set=[validation_weights],
        verbose=False,
    )
    configuration = model.get_booster().save_config()
    if '"device":"cuda' not in configuration.replace(" ", ""):
        raise RuntimeError("XGBoost behavior alert did not bind CUDA")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(model_path)
    train_prediction = (
        model.predict_proba(train_features)[:, 1] >= 0.5
    )
    evidence = {
        "xgboost_behavior_feature_count": int(train_features.shape[1]),
        "xgboost_behavior_training_samples": int(len(binary_train)),
        "xgboost_behavior_training_benign_samples": int(counts[0]),
        "xgboost_behavior_training_attack_samples": int(counts[1]),
        "xgboost_behavior_training_accuracy_at_0_5": float(
            (train_prediction == binary_train.astype(bool)).mean()
        ),
        "xgboost_behavior_estimators_requested": estimators,
        "xgboost_behavior_best_iteration": int(model.best_iteration),
        "xgboost_behavior_max_depth": max_depth,
        "xgboost_behavior_learning_rate": learning_rate,
        "xgboost_behavior_early_stopping_rounds": early_stopping_rounds,
        "xgboost_behavior_jobs": jobs,
        "xgboost_behavior_device": "cuda",
        "xgboost_version": xgboost.__version__,
        "xgboost_package_root": str(package_root),
        "xgboost_library_sha256": file_hash(library_path),
        "xgboost_behavior_model_path": str(model_path),
        "xgboost_behavior_model_sha256": file_hash(model_path),
        "xgboost_behavior_configuration_sha256": canonical_hash(
            {"configuration": configuration}
        ),
    }
    return model, evidence


def calibrate_group_conservative_score_threshold(
    validation_score: np.ndarray,
    validation_labels: np.ndarray,
    validation_capture_groups: np.ndarray,
    false_positive_budget: float,
) -> tuple[float, int]:
    if not 0.0 < false_positive_budget < 0.5:
        raise ValueError("false-positive budget must be in (0, 0.5)")
    benign = validation_labels == 0
    if not np.any(benign):
        raise ValueError("benign validation samples are required")
    benign_groups = sorted(set(validation_capture_groups[benign].tolist()))
    if len(benign_groups) < 2:
        raise ValueError(
            "at least two benign validation capture groups are required"
        )
    quantile = 1.0 - false_positive_budget
    thresholds = [
        quantile_higher(
            validation_score[
                benign & (validation_capture_groups == capture_group)
            ],
            quantile,
        )
        for capture_group in benign_groups
    ]
    return max(thresholds), len(benign_groups)


def select_known_only_risk_component(
    validation_candidates: dict[str, np.ndarray],
    test_candidates: dict[str, np.ndarray],
    validation_labels: np.ndarray,
    validation_capture_groups: np.ndarray,
    false_positive_budget: float,
) -> tuple[str, np.ndarray, dict[str, Any]]:
    expected = {
        "risk",
        "uncertainty",
        "conflict",
        "distance",
        "energy",
    }
    if set(validation_candidates) != expected:
        raise ValueError("known-only risk validation candidates differ")
    if set(test_candidates) != expected:
        raise ValueError("known-only risk test candidates differ")
    labels = np.asarray(validation_labels, dtype=np.int64)
    attack_classes = sorted(set(labels[labels != 0].tolist()))
    if len(attack_classes) < 2:
        raise ValueError(
            "known-only risk selection requires at least two attack classes"
        )
    priority = {
        "risk": 4,
        "distance": 3,
        "conflict": 2,
        "uncertainty": 1,
        "energy": 0,
    }
    candidates: dict[str, dict[str, Any]] = {}
    for name in sorted(expected):
        validation_score = np.asarray(
            validation_candidates[name],
            dtype=np.float64,
        )
        test_score = np.asarray(test_candidates[name], dtype=np.float64)
        if len(validation_score) != len(labels):
            raise ValueError(
                f"risk component {name} validation sample count differs"
            )
        if not (
            np.isfinite(validation_score).all()
            and np.isfinite(test_score).all()
        ):
            raise ValueError(f"risk component {name} is not finite")
        threshold, benign_group_count = (
            calibrate_group_conservative_score_threshold(
                validation_score,
                labels,
                validation_capture_groups,
                false_positive_budget,
            )
        )
        recalls = {
            str(class_index): float(
                np.mean(
                    validation_score[labels == class_index] > threshold
                )
            )
            for class_index in attack_classes
        }
        candidates[name] = {
            "threshold": float(threshold),
            "known_attack_validation_recalls": recalls,
            "known_attack_validation_recall_worst": float(
                min(recalls.values())
            ),
            "known_attack_validation_recall_mean": float(
                np.mean(list(recalls.values()))
            ),
            "validation_benign_group_count": benign_group_count,
        }
    selected = max(
        candidates,
        key=lambda name: (
            candidates[name][
                "known_attack_validation_recall_worst"
            ],
            candidates[name][
                "known_attack_validation_recall_mean"
            ],
            priority[name],
        ),
    )
    selected_threshold = candidates[selected]["threshold"]
    margin = test_candidates[selected] - selected_threshold
    evidence = {
        "known_only_risk_component_selected": selected,
        "known_only_risk_component_threshold": selected_threshold,
        "known_only_risk_component_candidates": candidates,
        "known_only_risk_component_selection_key": (
            "known_attack_validation_worst_recall_then_mean_recall_"
            "then_fixed_priority"
        ),
        "known_only_risk_component_false_positive_budget": (
            false_positive_budget
        ),
        "known_only_risk_component_true_unknown_used_for_candidates": False,
        "known_only_risk_component_true_unknown_used_for_threshold": False,
        "known_only_risk_component_true_unknown_used_for_selection": False,
    }
    return selected, np.asarray(margin, dtype=np.float64), evidence


def calibrate_group_conservative_alert_thresholds(
    validation_risk: np.ndarray,
    validation_maliciousness: np.ndarray,
    validation_labels: np.ndarray,
    validation_capture_groups: np.ndarray,
    branch_false_positive_budget: float = 0.02,
) -> tuple[float, float, int]:
    if not 0.0 < branch_false_positive_budget < 0.5:
        raise ValueError("branch false-positive budget must be in (0, 0.5)")
    benign = validation_labels == 0
    if not np.any(benign):
        raise ValueError("benign validation samples are required")
    quantile = 1.0 - branch_false_positive_budget
    benign_groups = sorted(set(validation_capture_groups[benign].tolist()))
    if len(benign_groups) < 2:
        raise ValueError(
            "at least two benign validation capture groups are required"
        )
    risk_thresholds = []
    malicious_thresholds = []
    for capture_group in benign_groups:
        selected = benign & (validation_capture_groups == capture_group)
        risk_thresholds.append(
            quantile_higher(validation_risk[selected], quantile)
        )
        malicious_thresholds.append(
            quantile_higher(validation_maliciousness[selected], quantile)
        )
    return (
        max(risk_thresholds),
        max(malicious_thresholds),
        len(benign_groups),
    )


def operational_metrics(
    calibrator: OpenSetCalibrator,
    validation_output: dict[str, Tensor],
    validation_labels: Tensor,
    validation_capture_groups: np.ndarray,
    test_output: dict[str, Tensor],
    test_labels: Tensor,
    is_unknown: Tensor,
    train_output: dict[str, Tensor] | None = None,
    train_labels: Tensor | None = None,
    external_attack_output: dict[str, Tensor] | None = None,
    train_engineering_features: np.ndarray | None = None,
    validation_engineering_features: np.ndarray | None = None,
    test_engineering_features: np.ndarray | None = None,
    train_family_invariant_features: np.ndarray | None = None,
    validation_family_invariant_features: np.ndarray | None = None,
    test_family_invariant_features: np.ndarray | None = None,
    alert_profile: str = "dual_risk_malicious",
    benign_knn_k: int = 5,
    benign_knn_false_positive_budget: float = 0.04,
    binary_head_seed: int = 0,
    binary_head_hidden_dim: int = 64,
    binary_head_steps: int = 400,
    binary_head_batch_size: int = 1024,
    binary_head_learning_rate: float = 1e-3,
    binary_head_weight_decay: float = 1e-4,
    binary_head_false_positive_budget: float = 0.04,
    auxiliary_alert_branch_false_positive_budget: float = 0.015,
    family_crossfit_false_positive_budget: float = 0.005,
    family_crossfit_checkpoint_interval: int = 25,
    family_crossfit_model_path: Path | None = None,
    xgboost_behavior_estimators: int = 800,
    xgboost_behavior_max_depth: int = 8,
    xgboost_behavior_learning_rate: float = 0.05,
    xgboost_behavior_early_stopping_rounds: int = 40,
    xgboost_behavior_jobs: int = 20,
    xgboost_behavior_false_positive_budget: float = 0.04,
    xgboost_behavior_model_path: Path | None = None,
    xgboost_root: Path | None = None,
    distance_device: torch.device | None = None,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    prediction = calibrator.predict(test_output)
    risk = prediction["risk"].numpy()
    maliciousness = prediction["maliciousness"].numpy()
    known_prediction = prediction["known_prediction"].numpy()
    unknown_prediction = prediction["is_unknown"].numpy().astype(bool)
    truth = test_labels.numpy()
    unknown = is_unknown.numpy().astype(bool)
    known = ~unknown
    benign = known & (truth == 0)
    known_attack = known & (truth != 0)
    actual_attack = ~benign
    alert_evidence: dict[str, Any]
    score_arrays: dict[str, np.ndarray] = {}
    if alert_profile == "dual_risk_malicious":
        validation_risk, validation_maliciousness, _ = calibrator.score(
            validation_output
        )
        (
            alert_risk_threshold,
            alert_malicious_threshold,
            alert_validation_benign_group_count,
        ) = calibrate_group_conservative_alert_thresholds(
            validation_risk.numpy(),
            validation_maliciousness.numpy(),
            validation_labels.numpy(),
            validation_capture_groups,
        )
        risk_scale = max(alert_risk_threshold, 1e-8)
        malicious_scale = max(alert_malicious_threshold, 1e-8)
        alert_score = np.maximum(
            risk / risk_scale,
            maliciousness / malicious_scale,
        )
        alert = alert_score >= 1.0
        alert_evidence = {
            "alert_profile": alert_profile,
            "alert_risk_threshold": alert_risk_threshold,
            "alert_malicious_threshold": alert_malicious_threshold,
            "alert_branch_false_positive_budget": 0.02,
            "alert_joint_false_positive_budget_upper_bound": 0.04,
            "alert_validation_benign_group_count": (
                alert_validation_benign_group_count
            ),
        }
    elif alert_profile == "benign_knn":
        if train_output is None or train_labels is None:
            raise ValueError(
                "benign_knn alert requires training output and labels"
            )
        benign_reference = train_output["fused_embedding"][
            train_labels.cpu() == 0
        ]
        validation_distance = cosine_knn_distance(
            validation_output["fused_embedding"],
            benign_reference,
            k=benign_knn_k,
            device=distance_device,
        ).numpy()
        test_distance = cosine_knn_distance(
            test_output["fused_embedding"],
            benign_reference,
            k=benign_knn_k,
            device=distance_device,
        ).numpy()
        (
            benign_knn_threshold,
            alert_validation_benign_group_count,
        ) = calibrate_group_conservative_score_threshold(
            validation_distance,
            validation_labels.numpy(),
            validation_capture_groups,
            benign_knn_false_positive_budget,
        )
        alert_score = test_distance / max(benign_knn_threshold, 1e-8)
        alert = test_distance > benign_knn_threshold
        score_arrays["benign_knn_distance"] = test_distance
        alert_evidence = {
            "alert_profile": alert_profile,
            "alert_benign_knn_threshold": benign_knn_threshold,
            "alert_benign_knn_k": benign_knn_k,
            "alert_benign_reference_samples": int(len(benign_reference)),
            "alert_branch_false_positive_budget": (
                benign_knn_false_positive_budget
            ),
            "alert_joint_false_positive_budget_upper_bound": (
                benign_knn_false_positive_budget
            ),
            "alert_validation_benign_group_count": (
                alert_validation_benign_group_count
            ),
        }
    elif alert_profile in {
        "binary_head",
        "binary_dual_alert",
        "family_crossfit_dual_alert",
        "family_crossfit_meta_select_dual_alert",
        "family_crossfit_meta_select_classscore_dual_alert",
        "family_crossfit_meta_select_classscore_component_dual_alert",
    }:
        if train_output is None or train_labels is None:
            raise ValueError(
                "binary_head alert requires training output and labels"
            )
        external_attack_samples = 0
        classscore_profile = alert_profile in {
            "family_crossfit_meta_select_classscore_dual_alert",
            "family_crossfit_meta_select_classscore_component_dual_alert",
        }
        component_select_profile = (
            alert_profile
            == "family_crossfit_meta_select_classscore_component_dual_alert"
        )
        if classscore_profile:
            validation_probability = known_class_attack_probability(
                validation_output
            )
            test_probability = known_class_attack_probability(test_output)
            binary_head_evidence = {
                "classification_attack_score": "1_minus_benign_probability",
                "classification_attack_score_training_required": False,
                "classification_attack_score_true_unknown_used_for_threshold": (
                    False
                ),
            }
        else:
            binary_train_embeddings = train_output["fused_embedding"]
            binary_train_labels = train_labels
            if external_attack_output is not None:
                external_attack_embeddings = external_attack_output[
                    "fused_embedding"
                ]
                external_attack_samples = len(external_attack_embeddings)
                binary_train_embeddings = torch.cat(
                    (
                        binary_train_embeddings,
                        external_attack_embeddings,
                    ),
                    dim=0,
                )
                binary_train_labels = torch.cat(
                    (
                        binary_train_labels,
                        torch.ones(
                            external_attack_samples,
                            dtype=binary_train_labels.dtype,
                            device=binary_train_labels.device,
                        ),
                    ),
                    dim=0,
                )
            head, binary_head_evidence = fit_binary_alert_head(
                binary_train_embeddings,
                binary_train_labels,
                seed=binary_head_seed,
                hidden_dim=binary_head_hidden_dim,
                steps=binary_head_steps,
                batch_size=binary_head_batch_size,
                learning_rate=binary_head_learning_rate,
                weight_decay=binary_head_weight_decay,
                device=distance_device,
            )
            validation_probability = binary_alert_probability(
                head,
                validation_output["fused_embedding"],
                device=distance_device,
            )
            test_probability = binary_alert_probability(
                head,
                test_output["fused_embedding"],
                device=distance_device,
            )
        (
            binary_head_threshold,
            alert_validation_benign_group_count,
        ) = calibrate_group_conservative_score_threshold(
            validation_probability,
            validation_labels.numpy(),
            validation_capture_groups,
            binary_head_false_positive_budget,
        )
        alert_score = test_probability / max(binary_head_threshold, 1e-8)
        alert = test_probability > binary_head_threshold
        score_arrays["binary_alert_probability"] = test_probability
        auxiliary_evidence: dict[str, Any] = {}
        if alert_profile in {
            "binary_dual_alert",
            "family_crossfit_dual_alert",
            "family_crossfit_meta_select_dual_alert",
            "family_crossfit_meta_select_classscore_dual_alert",
            "family_crossfit_meta_select_classscore_component_dual_alert",
        }:
            (
                validation_risk,
                validation_maliciousness,
                validation_components,
            ) = calibrator.score(validation_output)
            component_evidence: dict[str, Any] = {}
            if component_select_profile:
                component_names = (
                    "uncertainty",
                    "conflict",
                    "distance",
                    "energy",
                )
                missing = sorted(
                    set(component_names) - set(validation_components)
                )
                if missing:
                    raise ValueError(
                        "risk component selector is missing: "
                        + ", ".join(missing)
                    )
                test_components = prediction["components"]
                (
                    _,
                    component_margin,
                    component_evidence,
                ) = select_known_only_risk_component(
                    {
                        "risk": validation_risk.numpy(),
                        **{
                            name: validation_components[name].numpy()
                            for name in component_names
                        },
                    },
                    {
                        "risk": risk,
                        **{
                            name: test_components[name].numpy()
                            for name in component_names
                        },
                    },
                    validation_labels.numpy(),
                    validation_capture_groups,
                    auxiliary_alert_branch_false_positive_budget,
                )
                auxiliary_risk_threshold = component_evidence[
                    "known_only_risk_component_threshold"
                ]
                auxiliary_group_count = component_evidence[
                    "known_only_risk_component_candidates"
                ][
                    component_evidence[
                        "known_only_risk_component_selected"
                    ]
                ]["validation_benign_group_count"]
                auxiliary_risk_alert = component_margin > 0.0
                auxiliary_risk_score = np.exp(
                    np.clip(component_margin, -20.0, 20.0)
                )
                score_arrays[
                    "known_only_risk_component_alert_margin"
                ] = component_margin
            else:
                (
                    auxiliary_risk_threshold,
                    _,
                    auxiliary_group_count,
                ) = calibrate_group_conservative_alert_thresholds(
                    validation_risk.numpy(),
                    validation_maliciousness.numpy(),
                    validation_labels.numpy(),
                    validation_capture_groups,
                    branch_false_positive_budget=(
                        auxiliary_alert_branch_false_positive_budget
                    ),
                )
                auxiliary_risk_alert = risk > auxiliary_risk_threshold
                auxiliary_risk_score = (
                    risk / max(auxiliary_risk_threshold, 1e-8)
                )
            (
                auxiliary_malicious_threshold,
                malicious_group_count,
            ) = calibrate_group_conservative_score_threshold(
                validation_maliciousness.numpy(),
                validation_labels.numpy(),
                validation_capture_groups,
                auxiliary_alert_branch_false_positive_budget,
            )
            if malicious_group_count != auxiliary_group_count:
                raise ValueError(
                    "auxiliary alert benign group counts differ"
                )
            auxiliary_malicious_alert = (
                maliciousness > auxiliary_malicious_threshold
            )
            alert = (
                alert | auxiliary_risk_alert | auxiliary_malicious_alert
            )
            alert_score = np.maximum.reduce(
                (
                    alert_score,
                    auxiliary_risk_score,
                    maliciousness
                    / max(auxiliary_malicious_threshold, 1e-8),
                )
            )
            auxiliary_evidence = {
                "alert_auxiliary_risk_threshold": (
                    auxiliary_risk_threshold
                ),
                "alert_auxiliary_malicious_threshold": (
                    auxiliary_malicious_threshold
                ),
                "alert_auxiliary_branch_false_positive_budget": (
                    auxiliary_alert_branch_false_positive_budget
                ),
                "alert_auxiliary_validation_benign_group_count": (
                    auxiliary_group_count
                ),
                **component_evidence,
            }
        family_crossfit_evidence: dict[str, Any] = {}
        if alert_profile in {
            "family_crossfit_dual_alert",
            "family_crossfit_meta_select_dual_alert",
            "family_crossfit_meta_select_classscore_dual_alert",
            "family_crossfit_meta_select_classscore_component_dual_alert",
        }:
            if (
                train_engineering_features is None
                or validation_engineering_features is None
                or test_engineering_features is None
                or family_crossfit_model_path is None
            ):
                raise ValueError(
                    "family-crossfit alert requires frozen feature matrices"
                )
            high_capacity_model_path = family_crossfit_model_path
            if alert_profile == "family_crossfit_dual_alert":
                crossfit_margin, family_crossfit_evidence = (
                    fit_family_crossfit_alert(
                        train_engineering_features,
                        train_labels,
                        validation_engineering_features,
                        validation_labels,
                        validation_capture_groups,
                        test_engineering_features,
                        seed=binary_head_seed + 300007,
                        hidden_dim=binary_head_hidden_dim,
                        steps=binary_head_steps,
                        batch_size=binary_head_batch_size,
                        learning_rate=binary_head_learning_rate,
                        weight_decay=binary_head_weight_decay,
                        false_positive_budget=(
                            family_crossfit_false_positive_budget
                        ),
                        checkpoint_interval=(
                            family_crossfit_checkpoint_interval
                        ),
                        device=(
                            distance_device
                            if distance_device is not None
                            else train_output["fused_embedding"].device
                        ),
                        model_path=high_capacity_model_path,
                    )
                )
            else:
                if (
                    train_family_invariant_features is None
                    or validation_family_invariant_features is None
                    or test_family_invariant_features is None
                ):
                    raise ValueError(
                        "family-crossfit meta selection requires both feature profiles"
                    )
                high_capacity_model_path = (
                    family_crossfit_model_path.with_name(
                        "family_crossfit_high_capacity_alert.pt"
                    )
                )
                invariant_model_path = (
                    family_crossfit_model_path.with_name(
                        "family_crossfit_family_invariant_alert.pt"
                    )
                )
                high_capacity_margin, high_capacity_evidence = (
                    fit_family_crossfit_alert(
                        train_engineering_features,
                        train_labels,
                        validation_engineering_features,
                        validation_labels,
                        validation_capture_groups,
                        test_engineering_features,
                        seed=binary_head_seed + 300007,
                        hidden_dim=binary_head_hidden_dim,
                        steps=binary_head_steps,
                        batch_size=binary_head_batch_size,
                        learning_rate=binary_head_learning_rate,
                        weight_decay=binary_head_weight_decay,
                        false_positive_budget=(
                            family_crossfit_false_positive_budget
                        ),
                        checkpoint_interval=(
                            family_crossfit_checkpoint_interval
                        ),
                        device=(
                            distance_device
                            if distance_device is not None
                            else train_output["fused_embedding"].device
                        ),
                        model_path=high_capacity_model_path,
                    )
                )
                invariant_margin, invariant_evidence = (
                    fit_family_crossfit_alert(
                        train_family_invariant_features,
                        train_labels,
                        validation_family_invariant_features,
                        validation_labels,
                        validation_capture_groups,
                        test_family_invariant_features,
                        seed=binary_head_seed + 400009,
                        hidden_dim=binary_head_hidden_dim,
                        steps=binary_head_steps,
                        batch_size=binary_head_batch_size,
                        learning_rate=binary_head_learning_rate,
                        weight_decay=binary_head_weight_decay,
                        false_positive_budget=(
                            family_crossfit_false_positive_budget
                        ),
                        checkpoint_interval=(
                            family_crossfit_checkpoint_interval
                        ),
                        device=(
                            distance_device
                            if distance_device is not None
                            else train_output["fused_embedding"].device
                        ),
                        model_path=invariant_model_path,
                    )
                )
                (
                    _,
                    crossfit_margin,
                    family_crossfit_evidence,
                ) = select_family_crossfit_candidate(
                    {
                        "high_capacity": (
                            high_capacity_margin,
                            high_capacity_evidence,
                        ),
                        "family_invariant": (
                            invariant_margin,
                            invariant_evidence,
                        ),
                    }
                )
            crossfit_score = np.exp(
                np.clip(crossfit_margin, -20.0, 20.0)
            )
            alert = alert | (crossfit_margin > 0.0)
            alert_score = np.maximum(alert_score, crossfit_score)
            score_arrays["family_crossfit_alert_margin"] = crossfit_margin
        alert_evidence = {
            "alert_profile": alert_profile,
            "alert_primary_score_profile": (
                "known_class_attack_probability"
                if classscore_profile
                else "binary_embedding_head"
            ),
            "alert_binary_head_threshold": binary_head_threshold,
            "alert_binary_head_hidden_dim": binary_head_hidden_dim,
            "alert_binary_head_steps": binary_head_steps,
            "alert_binary_head_batch_size": binary_head_batch_size,
            "alert_binary_head_learning_rate": binary_head_learning_rate,
            "alert_binary_head_weight_decay": binary_head_weight_decay,
            "alert_branch_false_positive_budget": (
                binary_head_false_positive_budget
            ),
            "alert_joint_false_positive_budget_upper_bound": (
                binary_head_false_positive_budget
                + (
                    2.0 * auxiliary_alert_branch_false_positive_budget
                    if alert_profile
                    in {
                        "binary_dual_alert",
                        "family_crossfit_dual_alert",
                        "family_crossfit_meta_select_dual_alert",
                        "family_crossfit_meta_select_classscore_dual_alert",
                        "family_crossfit_meta_select_classscore_component_dual_alert",
                    }
                    else 0.0
                )
                + (
                    family_crossfit_false_positive_budget
                    if alert_profile
                    in {
                        "family_crossfit_dual_alert",
                        "family_crossfit_meta_select_dual_alert",
                        "family_crossfit_meta_select_classscore_dual_alert",
                        "family_crossfit_meta_select_classscore_component_dual_alert",
                    }
                    else 0.0
                )
            ),
            "alert_validation_benign_group_count": (
                alert_validation_benign_group_count
            ),
            "binary_head_external_surrogate_attack_samples": (
                external_attack_samples
            ),
            **binary_head_evidence,
            **auxiliary_evidence,
            **family_crossfit_evidence,
        }
    elif alert_profile == "xgboost_behavior_head":
        if (
            train_engineering_features is None
            or validation_engineering_features is None
            or test_engineering_features is None
            or train_labels is None
            or xgboost_behavior_model_path is None
        ):
            raise ValueError(
                "XGBoost behavior alert requires frozen feature matrices"
            )
        model, xgboost_evidence = fit_xgboost_behavior_alert(
            train_engineering_features,
            train_labels,
            validation_engineering_features,
            validation_labels,
            seed=binary_head_seed,
            estimators=xgboost_behavior_estimators,
            max_depth=xgboost_behavior_max_depth,
            learning_rate=xgboost_behavior_learning_rate,
            early_stopping_rounds=(
                xgboost_behavior_early_stopping_rounds
            ),
            jobs=xgboost_behavior_jobs,
            model_path=xgboost_behavior_model_path,
            xgboost_root=xgboost_root,
        )
        validation_probability = np.asarray(
            model.predict_proba(validation_engineering_features)[:, 1],
            dtype=np.float64,
        )
        test_probability = np.asarray(
            model.predict_proba(test_engineering_features)[:, 1],
            dtype=np.float64,
        )
        (
            xgboost_threshold,
            alert_validation_benign_group_count,
        ) = calibrate_group_conservative_score_threshold(
            validation_probability,
            validation_labels.numpy(),
            validation_capture_groups,
            xgboost_behavior_false_positive_budget,
        )
        alert_score = test_probability / max(xgboost_threshold, 1e-8)
        alert = test_probability > xgboost_threshold
        score_arrays["xgboost_behavior_alert_probability"] = (
            test_probability
        )
        alert_evidence = {
            "alert_profile": alert_profile,
            "alert_xgboost_behavior_threshold": xgboost_threshold,
            "alert_branch_false_positive_budget": (
                xgboost_behavior_false_positive_budget
            ),
            "alert_joint_false_positive_budget_upper_bound": (
                xgboost_behavior_false_positive_budget
            ),
            "alert_validation_benign_group_count": (
                alert_validation_benign_group_count
            ),
            **xgboost_evidence,
        }
    else:
        raise ValueError(f"unknown alert profile: {alert_profile}")
    metrics = {
        "alert_accuracy": float(
            accuracy_score(actual_attack.astype(np.int64), alert)
        ),
        "alert_precision": float(
            precision_score(
                actual_attack.astype(np.int64),
                alert,
                zero_division=0,
            )
        ),
        "attack_recall": float(
            recall_score(
                actual_attack.astype(np.int64),
                alert,
                zero_division=0,
            )
        ),
        "benign_fpr": float(alert[benign].mean()),
        "known_attack_type_accuracy": float(
            (known_prediction[known_attack] == truth[known_attack]).mean()
        ),
        "unknown_attack_alert_recall": float(alert[unknown].mean()),
        "unknown_label_recall": float(unknown_prediction[unknown].mean()),
        "known_acceptance_rate": float(
            (~unknown_prediction[known]).mean()
        ),
        **alert_evidence,
        "risk_threshold": float(calibrator.risk_threshold),
    }
    arrays = {
        "risk": risk,
        "maliciousness": maliciousness,
        "alert_score": alert_score,
        "alert": alert,
        "known_prediction": known_prediction,
        "is_unknown": unknown,
        "unknown_prediction": unknown_prediction,
        "label": truth,
        **score_arrays,
    }
    return metrics, arrays


def gpu_identity() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=uuid,name,driver_version",
        "--format=csv,noheader",
    ]
    completed = subprocess.run(
        command, check=True, capture_output=True, text=True
    )
    fields = [field.strip() for field in completed.stdout.splitlines()[0].split(",")]
    return {
        "uuid": fields[0],
        "name": fields[1],
        "driver_version": fields[2],
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
    }


def load_cache(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        required = (
            "payload",
            "sequence",
            "graph",
            "quality",
            "fine_label",
            "family",
            "capture_group",
        )
        missing = [name for name in required if name not in archive]
        if missing:
            raise ValueError(f"multimodal cache misses arrays: {missing}")
        return {name: archive[name] for name in required}


def append_training_only_external_benign_cache(
    primary: dict[str, np.ndarray],
    external: dict[str, np.ndarray],
    required_capture_group_prefix: str = "CICIoT2022::",
) -> tuple[dict[str, np.ndarray], np.ndarray, dict[str, Any]]:
    array_names = (
        "payload",
        "sequence",
        "graph",
        "quality",
        "fine_label",
        "family",
        "capture_group",
    )
    primary_count = len(primary["family"])
    external_count = len(external["family"])
    if external_count == 0:
        raise ValueError("external benign cache is empty")
    for name in array_names:
        if len(primary[name]) != primary_count:
            raise ValueError(f"primary cache array length differs: {name}")
        if len(external[name]) != external_count:
            raise ValueError(f"external cache array length differs: {name}")
        if name in {"payload", "sequence", "graph", "quality"}:
            if primary[name].shape[1:] != external[name].shape[1:]:
                raise ValueError(f"external cache shape differs: {name}")
    external_families = external["family"].astype(str)
    external_fine_labels = external["fine_label"].astype(str)
    external_groups = external["capture_group"].astype(str)
    if set(external_families.tolist()) != {"Benign"}:
        raise ValueError("external training cache must contain only Benign")
    if set(external_fine_labels.tolist()) != {"Benign_Final"}:
        raise ValueError(
            "external training cache must use the frozen Benign_Final label"
        )
    if not all(
        group.startswith(required_capture_group_prefix)
        for group in external_groups
    ):
        raise ValueError("external capture group namespace is not frozen")
    primary_groups = set(primary["capture_group"].astype(str).tolist())
    overlap = sorted(primary_groups & set(external_groups.tolist()))
    if overlap:
        raise ValueError(f"external capture groups overlap primary: {overlap}")

    combined = {
        name: np.concatenate([primary[name], external[name]], axis=0)
        for name in array_names
    }
    external_indices = np.arange(
        primary_count,
        primary_count + external_count,
        dtype=np.int64,
    )
    evidence = {
        "enabled": True,
        "role": "training_only_external_benign",
        "sample_count": external_count,
        "capture_group_count": len(set(external_groups.tolist())),
        "capture_group_prefix": required_capture_group_prefix,
        "family_values": sorted(set(external_families.tolist())),
        "fine_label_values": sorted(set(external_fine_labels.tolist())),
        "primary_validation_or_test_modified": False,
        "capture_group_overlap": overlap,
    }
    return combined, external_indices, evidence


def validate_training_only_external_surrogate_cache(
    primary: dict[str, np.ndarray],
    external: dict[str, np.ndarray],
    required_capture_group_prefix: str = "UNSW-NB15::",
) -> dict[str, Any]:
    array_names = (
        "payload",
        "sequence",
        "graph",
        "quality",
        "fine_label",
        "family",
        "capture_group",
    )
    primary_count = len(primary["family"])
    external_count = len(external["family"])
    if external_count == 0:
        raise ValueError("external surrogate cache is empty")
    for name in array_names:
        if len(primary[name]) != primary_count:
            raise ValueError(f"primary cache array length differs: {name}")
        if len(external[name]) != external_count:
            raise ValueError(f"external surrogate array length differs: {name}")
        if name in {"payload", "sequence", "graph", "quality"}:
            if primary[name].shape[1:] != external[name].shape[1:]:
                raise ValueError(
                    f"external surrogate cache shape differs: {name}"
                )
    external_families = external["family"].astype(str)
    external_fine_labels = external["fine_label"].astype(str)
    external_groups = external["capture_group"].astype(str)
    if set(external_families.tolist()) != {"ExternalSurrogateUnknown"}:
        raise ValueError(
            "external surrogate family contract differs"
        )
    direct_overlap = sorted(
        label
        for label in set(external_fine_labels.tolist())
        if label.casefold() in {"ddos", "dos", "mirai"}
    )
    if direct_overlap:
        raise ValueError(
            "external surrogate labels overlap target held-out families: "
            + ", ".join(direct_overlap)
        )
    if not all(
        group.startswith(required_capture_group_prefix)
        for group in external_groups
    ):
        raise ValueError(
            "external surrogate capture group namespace is not frozen"
        )
    primary_groups = set(primary["capture_group"].astype(str).tolist())
    overlap = sorted(primary_groups & set(external_groups.tolist()))
    if overlap:
        raise ValueError(
            f"external surrogate capture groups overlap primary: {overlap}"
        )
    return {
        "enabled": True,
        "role": "training_only_external_surrogate_unknown",
        "sample_count": external_count,
        "capture_group_count": len(set(external_groups.tolist())),
        "capture_group_prefix": required_capture_group_prefix,
        "family_values": sorted(set(external_families.tolist())),
        "fine_label_values": sorted(set(external_fine_labels.tolist())),
        "primary_validation_or_test_modified": False,
        "known_class_prototypes_modified": False,
        "threshold_fit_modified": False,
        "capture_group_overlap": overlap,
    }


def bind_external_surrogate_manifest(
    cache_path: Path,
    sample_count: int,
) -> dict[str, Any]:
    manifest_path = cache_path.with_suffix(
        cache_path.suffix + ".manifest.json"
    )
    if not manifest_path.is_file():
        raise ValueError(
            f"external surrogate manifest is missing: {manifest_path}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest_hash = canonical_hash(
        {
            name: value
            for name, value in manifest.items()
            if name != "manifest_sha256"
        }
    )
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        raise ValueError("external surrogate manifest hash is invalid")
    if manifest.get("cache_sha256") != file_hash(cache_path):
        raise ValueError("external surrogate cache hash differs from manifest")
    if manifest.get("samples") != sample_count:
        raise ValueError(
            "external surrogate sample count differs from manifest"
        )
    if manifest.get("source_role") != (
        "training_only_external_surrogate_unknown"
    ):
        raise ValueError("external surrogate source role differs")
    claim_boundary = manifest.get("claim_boundary", {})
    if claim_boundary.get(
        "target_ciciot2023_test_unknown_labels_accessed"
    ) is not False:
        raise ValueError(
            "external surrogate manifest does not prove target-label isolation"
        )
    return {
        "path": str(cache_path),
        "sha256": file_hash(cache_path),
        "manifest_path": str(manifest_path),
        "manifest_file_sha256": file_hash(manifest_path),
        "manifest_sha256": manifest["manifest_sha256"],
        "source_dataset": manifest.get("source_dataset"),
        "source_role": manifest["source_role"],
        "allowed_categories": manifest.get("allowed_categories", []),
        "samples_by_category": manifest.get("samples_by_category", {}),
        "source_file_count": len(manifest.get("source_files", [])),
        "target_test_unknown_labels_accessed": False,
    }


def reset_random_state(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def configure_reproducible_cuda(seed: int) -> dict[str, Any]:
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    reset_random_state(seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    return {
        "torch_deterministic_algorithms": (
            torch.are_deterministic_algorithms_enabled()
        ),
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "cuda_matmul_allow_tf32": (
            torch.backends.cuda.matmul.allow_tf32
        ),
        "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
        "cublas_workspace_config": os.environ[
            "CUBLAS_WORKSPACE_CONFIG"
        ],
    }


def fine_targets_for_indices(
    fine_labels: np.ndarray,
    indices: np.ndarray,
    device: torch.device,
) -> tuple[list[str], dict[str, int], Tensor]:
    names = sorted(set(fine_labels[indices].tolist()))
    mapping = {
        fine_label: index for index, fine_label in enumerate(names)
    }
    targets = torch.tensor(
        [mapping[fine_label] for fine_label in fine_labels[indices]],
        dtype=torch.long,
        device=device,
    )
    return names, mapping, targets


def build_model(
    cache: dict[str, np.ndarray],
    num_classes: int,
    hidden_dim: int,
    embedding_dim: int,
    device: torch.device,
    counterfactual_conflict_gate: bool = False,
) -> ConflictAwareEvidentialNet:
    return ConflictAwareEvidentialNet(
        input_dims=[
            int(cache["payload"].shape[1]),
            int(cache["sequence"].shape[1]),
            int(cache["graph"].shape[1]),
        ],
        num_classes=num_classes,
        hidden_dim=hidden_dim,
        embedding_dim=embedding_dim,
        dropout=0.1,
        conflict_scale=2.0,
        fusion_mode="conflict",
        encoder_kinds=["byte_cnn", "sequence_tcn", "packet_graph"],
        counterfactual_conflict_gate=counterfactual_conflict_gate,
    ).to(device)


def fit_nested_pseudo_risk_weights(
    cache: dict[str, np.ndarray],
    fine_labels: np.ndarray,
    families: np.ndarray,
    encoded_labels: np.ndarray,
    split: dict[str, Any],
    class_count: int,
    unknown_family: str,
    seed: int,
    epochs: int,
    patience: int,
    batch_size: int,
    hidden_dim: int,
    embedding_dim: int,
    learning_rate: float,
    risk_weight_steps: int,
    risk_weight_batch_size: int,
    risk_weight_margin: float,
    risk_weight_regularization: float,
    device: torch.device,
) -> tuple[dict[str, float], dict[str, Any]]:
    selected = select_pseudo_unknown_fine_labels(
        fine_labels,
        families,
        split["train_mask"],
        unknown_family,
        seed,
    )
    selected_fine_labels = set(selected.values())
    selector_train_indices = np.where(
        split["train_mask"]
        & ~np.isin(fine_labels, list(selected_fine_labels))
    )[0]
    selector_known_validation_indices = np.where(
        split["validation_mask"]
        & ~np.isin(fine_labels, list(selected_fine_labels))
    )[0]
    selector_pseudo_indices = np.where(
        split["validation_mask"]
        & np.isin(fine_labels, list(selected_fine_labels))
    )[0]
    if min(
        len(selector_train_indices),
        len(selector_known_validation_indices),
        len(selector_pseudo_indices),
    ) == 0:
        raise ValueError("nested pseudo-unknown split contains an empty role")
    selector_seed = seed + 100003
    reset_random_state(selector_seed)
    selector_train_views, selector_train_quality, selector_train_labels = (
        tensors_for_indices(
            cache,
            encoded_labels,
            selector_train_indices,
            device,
        )
    )
    (
        selector_fine_names,
        selector_fine_mapping,
        selector_train_fine_labels,
    ) = fine_targets_for_indices(
        fine_labels,
        selector_train_indices,
        device,
    )
    selector_validation_views, selector_validation_quality, (
        selector_validation_labels
    ) = tensors_for_indices(
        cache,
        encoded_labels,
        selector_known_validation_indices,
        device,
    )
    selector_pseudo_views, selector_pseudo_quality, _ = (
        tensors_for_indices(
            cache,
            encoded_labels,
            selector_pseudo_indices,
            device,
        )
    )
    selector_model = build_model(
        cache,
        class_count,
        hidden_dim,
        embedding_dim,
        device,
    )
    (
        selector_best_state,
        selector_history,
        selector_best_epoch,
    ) = train_model(
        selector_model,
        selector_train_views,
        selector_train_quality,
        selector_train_labels,
        selector_train_fine_labels,
        selector_validation_views,
        selector_validation_quality,
        selector_validation_labels,
        selector_seed,
        epochs,
        patience,
        batch_size,
        learning_rate,
        0.0,
        0.1,
    )
    selector_train_output = infer(
        selector_model,
        selector_train_views,
        selector_train_quality,
        batch_size,
    )
    selector_validation_output = infer(
        selector_model,
        selector_validation_views,
        selector_validation_quality,
        batch_size,
    )
    selector_pseudo_output = infer(
        selector_model,
        selector_pseudo_views,
        selector_pseudo_quality,
        batch_size,
    )
    selector_calibrator = OpenSetCalibrator(
        class_count,
        benign_index=0,
        weights=CALIBRATOR_WEIGHTS["nested_pseudo_risk"],
        known_acceptance=0.96,
    )
    selector_calibrator.fit_prototypes(
        selector_train_output["fused_embedding"],
        selector_train_labels.cpu(),
    )
    selector_calibrator.fit_fine_prototypes(
        selector_train_output["fused_embedding"],
        selector_train_fine_labels.cpu(),
    )
    selector_calibrator.fit_known_validation(
        selector_validation_output
    )
    _, _, known_components = selector_calibrator.score(
        selector_validation_output
    )
    _, _, pseudo_components = selector_calibrator.score(
        selector_pseudo_output
    )
    pseudo_group_mapping = {
        fine_label: index
        for index, fine_label in enumerate(sorted(selected_fine_labels))
    }
    pseudo_groups = torch.tensor(
        [
            pseudo_group_mapping[fine_label]
            for fine_label in fine_labels[selector_pseudo_indices]
        ],
        dtype=torch.long,
    )
    learned_weights, learning_evidence = learn_simplex_risk_weights(
        known_components,
        pseudo_components,
        pseudo_groups,
        selector_calibrator.weights,
        seed=selector_seed + 1,
        steps=risk_weight_steps,
        batch_size=risk_weight_batch_size,
        margin=risk_weight_margin,
        regularization=risk_weight_regularization,
    )
    evidence: dict[str, Any] = {
        "enabled": True,
        "selector_seed": selector_seed,
        "selected_pseudo_unknown_fine_labels": selected,
        "selected_pseudo_unknown_group_mapping": pseudo_group_mapping,
        "selector_sample_counts": {
            "train": int(len(selector_train_indices)),
            "known_validation": int(
                len(selector_known_validation_indices)
            ),
            "pseudo_unknown_validation": int(
                len(selector_pseudo_indices)
            ),
        },
        "selector_fine_label_mapping": selector_fine_mapping,
        "selector_fine_prototype_count": len(selector_fine_names),
        "selector_epochs_completed": len(selector_history),
        "selector_best_epoch": selector_best_epoch,
        "selector_history": selector_history,
        "weight_learning": learning_evidence,
        "real_unknown_labels_or_samples_used": False,
    }
    del (
        selector_best_state,
        selector_model,
        selector_train_views,
        selector_train_quality,
        selector_train_labels,
        selector_train_fine_labels,
        selector_validation_views,
        selector_validation_quality,
        selector_validation_labels,
        selector_pseudo_views,
        selector_pseudo_quality,
    )
    torch.cuda.empty_cache()
    reset_random_state(seed)
    return learned_weights, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--external-benign-cache", type=Path)
    parser.add_argument("--external-surrogate-unknown-cache", type=Path)
    parser.add_argument("--xgboost-root", type=Path)
    parser.add_argument("--reuse-task-dir", type=Path)
    parser.add_argument(
        "--unknown-family",
        choices=("DDoS", "DoS", "Mirai"),
        required=True,
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=96)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument(
        "--calibrator-profile",
        choices=tuple(CALIBRATOR_WEIGHTS),
        default="base",
    )
    parser.add_argument("--fine-contrastive-weight", type=float, default=0.0)
    parser.add_argument(
        "--fine-contrastive-temperature",
        type=float,
        default=0.1,
    )
    parser.add_argument(
        "--counterfactual-mix-weight",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--counterfactual-evidence-weight",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--counterfactual-malicious-weight",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--external-surrogate-weight",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--external-surrogate-evidence-weight",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--external-surrogate-malicious-weight",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--external-surrogate-binary-head-augmentation",
        action="store_true",
    )
    parser.add_argument("--risk-weight-steps", type=int, default=400)
    parser.add_argument("--risk-weight-batch-size", type=int, default=512)
    parser.add_argument("--risk-weight-margin", type=float, default=0.1)
    parser.add_argument(
        "--risk-weight-regularization",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--alert-profile",
        choices=(
            "dual_risk_malicious",
            "benign_knn",
            "binary_head",
            "binary_dual_alert",
            "family_crossfit_dual_alert",
            "family_crossfit_meta_select_dual_alert",
            "family_crossfit_meta_select_classscore_dual_alert",
            "family_crossfit_meta_select_classscore_component_dual_alert",
            "xgboost_behavior_head",
        ),
        default="dual_risk_malicious",
    )
    parser.add_argument("--benign-knn-k", type=int, default=5)
    parser.add_argument(
        "--benign-knn-false-positive-budget",
        type=float,
        default=0.04,
    )
    parser.add_argument("--binary-head-hidden-dim", type=int, default=64)
    parser.add_argument("--binary-head-steps", type=int, default=400)
    parser.add_argument("--binary-head-batch-size", type=int, default=1024)
    parser.add_argument(
        "--binary-head-learning-rate",
        type=float,
        default=1e-3,
    )
    parser.add_argument(
        "--binary-head-weight-decay",
        type=float,
        default=1e-4,
    )
    parser.add_argument(
        "--binary-head-false-positive-budget",
        type=float,
        default=0.04,
    )
    parser.add_argument(
        "--auxiliary-alert-branch-false-positive-budget",
        type=float,
        default=0.015,
    )
    parser.add_argument(
        "--family-crossfit-false-positive-budget",
        type=float,
        default=0.005,
    )
    parser.add_argument(
        "--family-crossfit-checkpoint-interval",
        type=int,
        default=25,
    )
    parser.add_argument(
        "--xgboost-behavior-estimators",
        type=int,
        default=800,
    )
    parser.add_argument(
        "--xgboost-behavior-max-depth",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--xgboost-behavior-learning-rate",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--xgboost-behavior-early-stopping-rounds",
        type=int,
        default=40,
    )
    parser.add_argument(
        "--xgboost-behavior-jobs",
        type=int,
        default=20,
    )
    parser.add_argument(
        "--xgboost-behavior-false-positive-budget",
        type=float,
        default=0.04,
    )
    args = parser.parse_args()
    if args.fine_contrastive_weight < 0.0:
        raise ValueError("fine contrastive weight must be non-negative")
    if args.fine_contrastive_temperature <= 0.0:
        raise ValueError("fine contrastive temperature must be positive")
    if (
        args.counterfactual_mix_weight < 0.0
        or args.counterfactual_evidence_weight < 0.0
        or args.counterfactual_malicious_weight < 0.0
    ):
        raise ValueError("counterfactual loss weights are invalid")
    if (
        args.reuse_task_dir is not None
        and args.counterfactual_mix_weight > 0.0
    ):
        raise ValueError(
            "counterfactual representation training cannot reuse a frozen task"
        )
    if args.external_surrogate_unknown_cache is None:
        if (
            args.external_surrogate_weight != 0.0
            or args.external_surrogate_binary_head_augmentation
        ):
            raise ValueError(
                "external surrogate training requires a surrogate cache"
            )
    elif (
        args.external_surrogate_weight <= 0.0
        and not args.external_surrogate_binary_head_augmentation
    ):
        raise ValueError(
            "external surrogate cache requires OE or alert augmentation"
        )
    if args.external_surrogate_weight < 0.0:
        raise ValueError("external surrogate weight must be non-negative")
    if (
        args.external_surrogate_evidence_weight < 0.0
        or args.external_surrogate_malicious_weight < 0.0
    ):
        raise ValueError("external surrogate component weights are invalid")
    if (
        args.reuse_task_dir is not None
        and args.external_surrogate_weight > 0.0
    ):
        raise ValueError(
            "external surrogate OE cannot reuse a frozen task"
        )
    if (
        args.external_surrogate_binary_head_augmentation
        and args.alert_profile not in {"binary_head", "binary_dual_alert"}
    ):
        raise ValueError(
            "external surrogate alert augmentation requires binary alert"
        )
    if args.risk_weight_steps <= 0 or args.risk_weight_batch_size <= 0:
        raise ValueError("risk weight learning counts must be positive")
    if (
        args.external_benign_cache is not None
        and args.calibrator_profile != "base"
    ):
        raise ValueError(
            "external benign development is frozen with the base calibrator"
        )
    if (
        args.alert_profile in {
            "benign_knn",
            "binary_head",
            "binary_dual_alert",
            "family_crossfit_dual_alert",
            "family_crossfit_meta_select_dual_alert",
            "family_crossfit_meta_select_classscore_dual_alert",
            "family_crossfit_meta_select_classscore_component_dual_alert",
        }
        and args.external_benign_cache is None
    ):
        raise ValueError(
            f"{args.alert_profile} alert requires external benign training"
        )
    if args.reuse_task_dir is not None:
        reuse_task_dir = args.reuse_task_dir.resolve()
        required_reuse_files = (
            reuse_task_dir / "model.pt",
            reuse_task_dir / "calibrator.json",
            reuse_task_dir / "metrics.json",
        )
        missing_reuse_files = [
            str(path) for path in required_reuse_files if not path.is_file()
        ]
        if missing_reuse_files:
            raise ValueError(
                f"frozen task misses files: {missing_reuse_files}"
            )
    if (
        args.binary_head_hidden_dim <= 0
        or args.binary_head_steps <= 0
        or args.binary_head_batch_size < 2
    ):
        raise ValueError("binary alert head dimensions and counts are invalid")
    validate_family_crossfit_settings(
        args.alert_profile,
        args.family_crossfit_false_positive_budget,
        args.family_crossfit_checkpoint_interval,
    )
    if (
        args.xgboost_behavior_estimators <= 0
        or args.xgboost_behavior_max_depth <= 0
        or args.xgboost_behavior_learning_rate <= 0.0
        or args.xgboost_behavior_early_stopping_rounds <= 0
        or args.xgboost_behavior_jobs <= 0
        or not 0.0
        < args.xgboost_behavior_false_positive_budget
        < 0.5
    ):
        raise ValueError("XGBoost behavior alert settings are invalid")
    if args.alert_profile == "xgboost_behavior_head":
        if args.xgboost_root is None:
            raise ValueError("XGBoost behavior alert requires --xgboost-root")
        xgboost_init = (
            args.xgboost_root.resolve() / "xgboost" / "__init__.py"
        )
        if not xgboost_init.is_file():
            raise ValueError(
                f"XGBoost package root is invalid: {args.xgboost_root}"
            )

    if not torch.cuda.is_available():
        raise RuntimeError("formal task requires CUDA")
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise ValueError(f"refusing to overwrite task output: {output_dir}")
    output_dir.mkdir(parents=True)
    reproducibility = configure_reproducible_cuda(args.seed)
    device = initialize_cuda_device()
    started = time.time()

    cache_path = args.cache.resolve()
    primary_cache = load_cache(cache_path)
    primary_fine_labels = primary_cache["fine_label"].astype(str)
    primary_families = primary_cache["family"].astype(str)
    primary_capture_groups = primary_cache["capture_group"].astype(str)
    split = split_capture_groups(
        primary_fine_labels,
        primary_families,
        primary_capture_groups,
        args.unknown_family,
        args.seed,
    )
    cache = primary_cache
    external_indices = np.empty(0, dtype=np.int64)
    external_benign_evidence: dict[str, Any] = {"enabled": False}
    external_benign_path: Path | None = None
    if args.external_benign_cache is not None:
        external_benign_path = args.external_benign_cache.resolve()
        external_cache = load_cache(external_benign_path)
        cache, external_indices, external_benign_evidence = (
            append_training_only_external_benign_cache(
                primary_cache,
                external_cache,
            )
        )
        external_benign_evidence["path"] = str(external_benign_path)
        external_benign_evidence["sha256"] = file_hash(
            external_benign_path
        )
    external_surrogate_cache: dict[str, np.ndarray] | None = None
    external_surrogate_evidence: dict[str, Any] = {"enabled": False}
    external_surrogate_path: Path | None = None
    if args.external_surrogate_unknown_cache is not None:
        external_surrogate_path = (
            args.external_surrogate_unknown_cache.resolve()
        )
        external_surrogate_cache = load_cache(external_surrogate_path)
        external_surrogate_evidence = (
            validate_training_only_external_surrogate_cache(
                cache,
                external_surrogate_cache,
            )
        )
        external_surrogate_evidence.update(
            bind_external_surrogate_manifest(
                external_surrogate_path,
                len(external_surrogate_cache["family"]),
            )
        )
    fine_labels = cache["fine_label"].astype(str)
    families = cache["family"].astype(str)
    capture_groups = cache["capture_group"].astype(str)
    class_names, mapping = family_mapping(args.unknown_family)
    encoded_labels = encode_known_labels(
        families, mapping, args.unknown_family
    )
    indices = {
        "train": np.concatenate(
            [
                np.where(split["train_mask"])[0],
                external_indices,
            ]
        ),
        "validation": np.where(split["validation_mask"])[0],
        "known_test": np.where(split["known_test_mask"])[0],
        "unknown_test": np.where(split["unknown_test_mask"])[0],
    }
    test_indices = np.concatenate(
        [indices["known_test"], indices["unknown_test"]]
    )
    test_labels_np = encoded_labels[test_indices]
    is_unknown_np = test_labels_np < 0

    train_views, train_quality, train_labels = tensors_for_indices(
        cache, encoded_labels, indices["train"], device
    )
    (
        train_fine_names,
        train_fine_mapping,
        train_fine_labels,
    ) = fine_targets_for_indices(
        fine_labels,
        indices["train"],
        device,
    )
    validation_views, validation_quality, validation_labels = (
        tensors_for_indices(
            cache, encoded_labels, indices["validation"], device
        )
    )
    test_views, test_quality, _ = tensors_for_indices(
        cache,
        np.where(encoded_labels < 0, 0, encoded_labels),
        test_indices,
        device,
    )
    test_labels = torch.from_numpy(test_labels_np).to(torch.long)
    is_unknown = torch.from_numpy(is_unknown_np)
    external_surrogate_views: list[Tensor] | None = None
    external_surrogate_quality: Tensor | None = None
    if external_surrogate_cache is not None:
        (
            external_surrogate_views,
            external_surrogate_quality,
        ) = tensors_for_cache(external_surrogate_cache, device)

    risk_learning_evidence: dict[str, Any] = {"enabled": False}
    final_risk_weights = CALIBRATOR_WEIGHTS[args.calibrator_profile]
    if (
        args.calibrator_profile == "nested_pseudo_risk"
        and args.reuse_task_dir is None
    ):
        final_risk_weights, risk_learning_evidence = (
            fit_nested_pseudo_risk_weights(
                cache,
                fine_labels,
                families,
                encoded_labels,
                split,
                len(class_names),
                args.unknown_family,
                args.seed,
                args.epochs,
                args.patience,
                args.batch_size,
                args.hidden_dim,
                args.embedding_dim,
                args.learning_rate,
                args.risk_weight_steps,
                args.risk_weight_batch_size,
                args.risk_weight_margin,
                args.risk_weight_regularization,
                device,
            )
        )
    model = build_model(
        cache,
        len(class_names),
        args.hidden_dim,
        args.embedding_dim,
        device,
        counterfactual_conflict_gate=(
            args.counterfactual_mix_weight > 0.0
        ),
    )
    frozen_task_evidence: dict[str, Any] = {"enabled": False}
    frozen_base_metrics: dict[str, Any] | None = None
    if args.reuse_task_dir is not None:
        reuse_task_dir = args.reuse_task_dir.resolve()
        checkpoint_path = reuse_task_dir / "model.pt"
        calibrator_path = reuse_task_dir / "calibrator.json"
        base_metrics_path = reuse_task_dir / "metrics.json"
        checkpoint = torch.load(checkpoint_path, map_location=device)
        if checkpoint["class_names"] != class_names:
            raise ValueError("frozen task class names differ from current split")
        expected_model = {
            "hidden_dim": args.hidden_dim,
            "embedding_dim": args.embedding_dim,
            "input_dims": [
                int(cache["payload"].shape[1]),
                int(cache["sequence"].shape[1]),
                int(cache["graph"].shape[1]),
            ],
        }
        if checkpoint["model"] != expected_model:
            raise ValueError("frozen task model configuration differs")
        best_state = checkpoint["state_dict"]
        model.load_state_dict(best_state)
        frozen_base_metrics = json.loads(
            base_metrics_path.read_text(encoding="utf-8")
        )
        if frozen_base_metrics["unknown_family"] != args.unknown_family:
            raise ValueError("frozen task unknown family differs")
        if frozen_base_metrics["seed"] != args.seed:
            raise ValueError("frozen task seed differs")
        history = []
        best_epoch = int(
            frozen_base_metrics["training"]["best_epoch"]
        )
        frozen_task_evidence = {
            "enabled": True,
            "task_dir": str(reuse_task_dir),
            "model_sha256": file_hash(checkpoint_path),
            "calibrator_sha256": file_hash(calibrator_path),
            "metrics_sha256": file_hash(base_metrics_path),
            "base_metrics_manifest_sha256": (
                frozen_base_metrics["manifest_sha256"]
            ),
            "model_training_epochs_executed": 0,
        }
    else:
        best_state, history, best_epoch = train_model(
            model,
            train_views,
            train_quality,
            train_labels,
            train_fine_labels,
            validation_views,
            validation_quality,
            validation_labels,
            args.seed,
            args.epochs,
            args.patience,
            args.batch_size,
            args.learning_rate,
            args.fine_contrastive_weight,
            args.fine_contrastive_temperature,
            counterfactual_mix_weight=args.counterfactual_mix_weight,
            counterfactual_evidence_weight=(
                args.counterfactual_evidence_weight
            ),
            counterfactual_malicious_weight=(
                args.counterfactual_malicious_weight
            ),
            external_surrogate_views=(
                external_surrogate_views
                if args.external_surrogate_weight > 0.0
                else None
            ),
            external_surrogate_quality=(
                external_surrogate_quality
                if args.external_surrogate_weight > 0.0
                else None
            ),
            external_surrogate_weight=args.external_surrogate_weight,
            external_surrogate_evidence_weight=(
                args.external_surrogate_evidence_weight
            ),
            external_surrogate_malicious_weight=(
                args.external_surrogate_malicious_weight
            ),
        )

    train_output = infer(
        model, train_views, train_quality, args.batch_size
    )
    validation_output = infer(
        model,
        validation_views,
        validation_quality,
        args.batch_size,
    )
    test_output = infer(model, test_views, test_quality, args.batch_size)
    counterfactual_validation_evidence: dict[str, float] = {}
    if args.counterfactual_mix_weight > 0.0:
        counterfactual_validation_evidence = (
            counterfactual_validation_metrics(
                model,
                validation_views,
                validation_quality,
                validation_labels,
                args.batch_size,
            )
        )
    external_surrogate_output: dict[str, Tensor] | None = None
    if (
        external_surrogate_views is not None
        and external_surrogate_quality is not None
    ):
        external_surrogate_output = infer(
            model,
            external_surrogate_views,
            external_surrogate_quality,
            args.batch_size,
        )
        external_surrogate_evidence["model_output_summary"] = {
            "mean_max_known_probability": float(
                external_surrogate_output["fused_probability"]
                .max(dim=-1)
                .values.mean()
            ),
            "mean_uncertainty": float(
                external_surrogate_output["fused_uncertainty"].mean()
            ),
            "mean_conflict": float(
                external_surrogate_output["global_conflict"].mean()
            ),
            "mean_total_evidence": float(
                external_surrogate_output["fused_evidence"]
                .sum(dim=-1)
                .mean()
            ),
            "mean_malicious_probability": float(
                torch.sigmoid(
                    external_surrogate_output["malicious_logit"]
                ).mean()
            ),
        }
    if args.reuse_task_dir is not None:
        calibrator = OpenSetCalibrator.from_state_dict(
            json.loads(
                (
                    args.reuse_task_dir.resolve() / "calibrator.json"
                ).read_text(encoding="utf-8")
            )
        )
    else:
        calibrator = OpenSetCalibrator(
            len(class_names),
            benign_index=0,
            weights=final_risk_weights,
            known_acceptance=0.96,
            aggregation=CALIBRATOR_AGGREGATION[args.calibrator_profile],
        )
        calibrator.fit_prototypes(
            train_output["fused_embedding"],
            train_labels.cpu(),
        )
        if args.calibrator_profile in FINE_PROTOTYPE_PROFILES:
            calibrator.fit_fine_prototypes(
                train_output["fused_embedding"],
                train_fine_labels.cpu(),
            )
        calibrator.fit_known_validation(validation_output)
    open_set_metrics = evaluate_open_set(
        test_output, test_labels, is_unknown, calibrator
    )
    known_test = ~is_unknown_np
    known_prediction = (
        test_output["fused_probability"].argmax(dim=-1).numpy()
    )
    open_set_metrics["known_balanced_accuracy"] = float(
        balanced_accuracy_score(
            test_labels_np[known_test],
            known_prediction[known_test],
        )
    )
    if frozen_base_metrics is not None:
        identity_differences = {
            key: abs(
                float(open_set_metrics[key])
                - float(frozen_base_metrics["three_layer_metrics"][key])
            )
            for key in frozen_base_metrics["three_layer_metrics"]
        }
        maximum_identity_difference = max(identity_differences.values())
        if maximum_identity_difference > 1e-7:
            raise RuntimeError(
                "frozen checkpoint identity check failed: "
                f"{maximum_identity_difference}"
            )
        frozen_task_evidence["three_layer_metric_max_abs_difference"] = (
            maximum_identity_difference
        )
        frozen_task_evidence["three_layer_metric_identity_tolerance"] = 1e-7
        frozen_task_evidence["three_layer_metric_identity_pass"] = True
    train_engineering_features: np.ndarray | None = None
    validation_engineering_features: np.ndarray | None = None
    test_engineering_features: np.ndarray | None = None
    train_family_invariant_features: np.ndarray | None = None
    validation_family_invariant_features: np.ndarray | None = None
    test_family_invariant_features: np.ndarray | None = None
    if args.alert_profile == "xgboost_behavior_head":
        feature_builder = engineering_behavior_features
    elif args.alert_profile == "family_crossfit_dual_alert":
        feature_builder = family_invariant_alert_features
    elif args.alert_profile in {
        "family_crossfit_meta_select_dual_alert",
        "family_crossfit_meta_select_classscore_dual_alert",
        "family_crossfit_meta_select_classscore_component_dual_alert",
    }:
        feature_builder = engineering_behavior_features
        train_family_invariant_features = (
            family_invariant_alert_features(
                cache,
                indices["train"],
                train_output,
            )
        )
        validation_family_invariant_features = (
            family_invariant_alert_features(
                cache,
                indices["validation"],
                validation_output,
            )
        )
        test_family_invariant_features = (
            family_invariant_alert_features(
                cache,
                test_indices,
                test_output,
            )
        )
    else:
        feature_builder = None
    if feature_builder is not None:
        train_engineering_features = feature_builder(
            cache,
            indices["train"],
            train_output,
        )
        validation_engineering_features = feature_builder(
            cache,
            indices["validation"],
            validation_output,
        )
        test_engineering_features = feature_builder(
            cache,
            test_indices,
            test_output,
        )
    operational, score_arrays = operational_metrics(
        calibrator,
        validation_output,
        validation_labels.cpu(),
        capture_groups[indices["validation"]],
        test_output,
        test_labels,
        is_unknown,
        train_output=train_output,
        train_labels=train_labels,
        external_attack_output=(
            external_surrogate_output
            if args.external_surrogate_binary_head_augmentation
            else None
        ),
        train_engineering_features=train_engineering_features,
        validation_engineering_features=(
            validation_engineering_features
        ),
        test_engineering_features=test_engineering_features,
        train_family_invariant_features=(
            train_family_invariant_features
        ),
        validation_family_invariant_features=(
            validation_family_invariant_features
        ),
        test_family_invariant_features=(
            test_family_invariant_features
        ),
        alert_profile=args.alert_profile,
        benign_knn_k=args.benign_knn_k,
        benign_knn_false_positive_budget=(
            args.benign_knn_false_positive_budget
        ),
        binary_head_seed=args.seed + 200003,
        binary_head_hidden_dim=args.binary_head_hidden_dim,
        binary_head_steps=args.binary_head_steps,
        binary_head_batch_size=args.binary_head_batch_size,
        binary_head_learning_rate=args.binary_head_learning_rate,
        binary_head_weight_decay=args.binary_head_weight_decay,
        binary_head_false_positive_budget=(
            args.binary_head_false_positive_budget
        ),
        auxiliary_alert_branch_false_positive_budget=(
            args.auxiliary_alert_branch_false_positive_budget
        ),
        family_crossfit_false_positive_budget=(
            args.family_crossfit_false_positive_budget
        ),
        family_crossfit_checkpoint_interval=(
            args.family_crossfit_checkpoint_interval
        ),
        family_crossfit_model_path=(
            output_dir / "family_crossfit_alert.pt"
            if args.alert_profile
            in {
                "family_crossfit_dual_alert",
                "family_crossfit_meta_select_dual_alert",
                "family_crossfit_meta_select_classscore_dual_alert",
                "family_crossfit_meta_select_classscore_component_dual_alert",
            }
            else None
        ),
        xgboost_behavior_estimators=(
            args.xgboost_behavior_estimators
        ),
        xgboost_behavior_max_depth=args.xgboost_behavior_max_depth,
        xgboost_behavior_learning_rate=(
            args.xgboost_behavior_learning_rate
        ),
        xgboost_behavior_early_stopping_rounds=(
            args.xgboost_behavior_early_stopping_rounds
        ),
        xgboost_behavior_jobs=args.xgboost_behavior_jobs,
        xgboost_behavior_false_positive_budget=(
            args.xgboost_behavior_false_positive_budget
        ),
        xgboost_behavior_model_path=(
            output_dir / "xgboost_behavior_alert.ubj"
            if args.alert_profile == "xgboost_behavior_head"
            else None
        ),
        xgboost_root=(
            args.xgboost_root.resolve()
            if args.xgboost_root is not None
            else None
        ),
        distance_device=device,
    )
    score_arrays.update(
        classical_baseline_score_arrays(
            train_output=train_output,
            train_labels=train_labels,
            validation_output=validation_output,
            validation_labels=validation_labels,
            test_output=test_output,
            test_labels=test_labels,
            is_unknown=is_unknown,
        )
    )
    score_arrays.update(
        risk_diagnostic_score_arrays(
            calibrator=calibrator,
            train_output=train_output,
            validation_output=validation_output,
            test_output=test_output,
        )
    )
    elapsed = time.time() - started
    gpu = gpu_identity()
    gpu.update(
        {
            "cuda_required": True,
            "cuda_used": True,
            "peak_allocated_bytes": int(
                torch.cuda.max_memory_allocated(device)
            ),
            "peak_reserved_bytes": int(
                torch.cuda.max_memory_reserved(device)
            ),
        }
    )
    split_evidence = {
        "strategy": "source_pcap_capture_grouped_family_held_out",
        "unknown_family": args.unknown_family,
        "known_class_names": class_names,
        "known_family_mapping": mapping,
        "sample_counts": {
            name: int(len(values)) for name, values in indices.items()
        },
        "capture_assignment": split["assignment"],
        "unknown_capture_groups": split["unknown_groups"],
        "overlap": split["overlap"],
        "training_only_external_benign": external_benign_evidence,
        "training_only_external_surrogate_unknown": (
            external_surrogate_evidence
        ),
        "unknown_labels_used_for_training_or_threshold": False,
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_cuda_task_metrics_v1"
        ),
        "state": "completed",
        "algorithm": {
            "name": "CAEOS-EMTD PCAP heterogeneous evidential fusion",
            "modalities": list(MODALITY_NAMES),
            "fusion": "reliability_discounted_conflict_aware_dirichlet",
            "risk": (
                "known_normalized_maximum_uncertainty_conflict_hierarchical_prototype_distance_energy"
                if args.calibrator_profile == "hierarchical_fine_max"
                else "known_only_nested_pseudo_unknown_learned_hierarchical_risk"
                if args.calibrator_profile == "nested_pseudo_risk"
                else "fixed uncertainty_conflict_hierarchical_prototype_distance_energy"
                if args.calibrator_profile == "hierarchical_fine"
                else "fixed uncertainty_conflict_prototype_distance_energy"
            ),
            "calibrator_profile": args.calibrator_profile,
            "risk_aggregation": calibrator.aggregation,
            "risk_weights": calibrator.weights,
            "external_surrogate_outlier_exposure": (
                args.external_surrogate_weight > 0.0
            ),
        },
        "cache": {
            "path": str(cache_path),
            "sha256": file_hash(cache_path),
            "external_training_benign": external_benign_evidence,
            "external_training_surrogate_unknown": (
                external_surrogate_evidence
            ),
        },
        "unknown_family": args.unknown_family,
        "seed": args.seed,
        "split": split_evidence,
        "training": {
            "epochs_requested": args.epochs,
            "epochs_completed": len(history),
            "best_epoch": best_epoch,
            "batch_size": args.batch_size,
            "hidden_dim": args.hidden_dim,
            "embedding_dim": args.embedding_dim,
            "learning_rate": args.learning_rate,
            "reproducible_cuda_runtime": reproducibility,
            "calibrator_profile": args.calibrator_profile,
            "fine_prototype_count": (
                len(train_fine_names)
                if args.calibrator_profile in FINE_PROTOTYPE_PROFILES
                else 0
            ),
            "fine_label_mapping": (
                train_fine_mapping
                if args.calibrator_profile in FINE_PROTOTYPE_PROFILES
                else {}
            ),
            "fine_contrastive_weight": args.fine_contrastive_weight,
            "fine_contrastive_temperature": (
                args.fine_contrastive_temperature
            ),
            "counterfactual_mix_weight": (
                args.counterfactual_mix_weight
            ),
            "counterfactual_evidence_weight": (
                args.counterfactual_evidence_weight
            ),
            "counterfactual_malicious_weight": (
                args.counterfactual_malicious_weight
            ),
            "counterfactual_conflict_gate_enabled": (
                args.counterfactual_mix_weight > 0.0
            ),
            "counterfactual_checkpoint_selection": (
                "0.4_macro_f1_plus_0.4_balanced_accuracy_plus_"
                "0.1_counterfactual_uncertainty_plus_"
                "0.1_counterfactual_malicious_probability"
                if args.counterfactual_mix_weight > 0.0
                else "0.5_macro_f1_plus_0.5_balanced_accuracy"
            ),
            "counterfactual_validation": (
                counterfactual_validation_evidence
            ),
            "history": history,
            "frozen_base_task": frozen_task_evidence,
            "nested_pseudo_risk_learning": risk_learning_evidence,
            "external_training_benign": external_benign_evidence,
            "external_training_surrogate_unknown": (
                external_surrogate_evidence
            ),
            "external_surrogate_weight": (
                args.external_surrogate_weight
            ),
            "external_surrogate_evidence_weight": (
                args.external_surrogate_evidence_weight
            ),
            "external_surrogate_malicious_weight": (
                args.external_surrogate_malicious_weight
            ),
            "external_surrogate_binary_head_attack_augmentation": (
                args.external_surrogate_binary_head_augmentation
            ),
            "alert_profile": args.alert_profile,
            "benign_knn_k": args.benign_knn_k,
            "benign_knn_false_positive_budget": (
                args.benign_knn_false_positive_budget
            ),
            "binary_head_seed_offset": 200003,
            "binary_head_hidden_dim": args.binary_head_hidden_dim,
            "binary_head_steps": args.binary_head_steps,
            "binary_head_batch_size": args.binary_head_batch_size,
            "binary_head_learning_rate": args.binary_head_learning_rate,
            "binary_head_weight_decay": args.binary_head_weight_decay,
            "binary_head_false_positive_budget": (
                args.binary_head_false_positive_budget
            ),
            "auxiliary_alert_branch_false_positive_budget": (
                args.auxiliary_alert_branch_false_positive_budget
            ),
            "xgboost_behavior_estimators": (
                args.xgboost_behavior_estimators
            ),
            "xgboost_behavior_max_depth": (
                args.xgboost_behavior_max_depth
            ),
            "xgboost_behavior_learning_rate": (
                args.xgboost_behavior_learning_rate
            ),
            "xgboost_behavior_early_stopping_rounds": (
                args.xgboost_behavior_early_stopping_rounds
            ),
            "xgboost_behavior_jobs": args.xgboost_behavior_jobs,
            "xgboost_behavior_false_positive_budget": (
                args.xgboost_behavior_false_positive_budget
            ),
            "xgboost_root": (
                str(args.xgboost_root.resolve())
                if args.xgboost_root is not None
                else None
            ),
        },
        "three_layer_metrics": {
            key: open_set_metrics[key]
            for key in (
                "known_macro_f1",
                "known_accuracy",
                "known_balanced_accuracy",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "unknown_f1",
                "oscr",
                "ece",
                "brier_score",
                "known_acceptance_rate",
                "unknown_rejection_rate",
            )
        },
        "risk_diagnostics": {
            key: value
            for key, value in open_set_metrics.items()
            if key.endswith("_auroc")
            or key.startswith("mean_known_")
            or key.startswith("mean_unknown_")
        },
        "operational_95_5": operational,
        "gpu_execution": gpu,
        "elapsed_seconds": elapsed,
        "claim_boundary": {
            "development_task": True,
            "unknown_family_excluded_from_train_and_validation": True,
            "thresholds_known_validation_only": True,
            "nested_pseudo_unknowns_from_known_fine_labels_only": (
                args.calibrator_profile == "nested_pseudo_risk"
            ),
            "real_unknown_used_for_risk_weight_learning": False,
            "counterfactuals_from_known_attack_families_only": (
                args.counterfactual_mix_weight > 0.0
            ),
            "counterfactual_true_unknown_used_for_training": False,
            "counterfactual_true_unknown_used_for_checkpoint_selection": (
                False
            ),
            "source_pcap_capture_groups_disjoint": True,
            "external_benign_training_only": (
                external_benign_path is not None
            ),
            "external_surrogate_unknown_training_only": (
                external_surrogate_path is not None
            ),
            "external_surrogate_not_in_known_prototypes": True,
            "external_surrogate_not_in_threshold_fit": True,
            "primary_validation_and_test_unchanged": True,
            "frozen_model_and_calibrator_reused": (
                args.reuse_task_dir is not None
            ),
            "engineering_alert_thresholds_known_benign_validation_only": True,
            "confirmation_claim_not_permitted": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_dir / "metrics.json", report)
    atomic_json(
        output_dir / "calibrator.json", calibrator.state_dict()
    )
    torch.save(
        {
            "state_dict": best_state,
            "class_names": class_names,
            "model": {
                "hidden_dim": args.hidden_dim,
                "embedding_dim": args.embedding_dim,
                "input_dims": [
                    int(cache["payload"].shape[1]),
                    int(cache["sequence"].shape[1]),
                    int(cache["graph"].shape[1]),
                ],
            },
        },
        output_dir / "model.pt",
    )
    np.savez_compressed(output_dir / "scores.npz", **score_arrays)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

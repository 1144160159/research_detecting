from __future__ import annotations

from typing import Any

import numpy as np
import torch
import torch.nn.functional as F


def validate_parameters(temperature: float, noise: float) -> None:
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("ODIN temperature must be finite and positive")
    if not np.isfinite(noise) or noise < 0.0:
        raise ValueError("ODIN noise must be finite and non-negative")


def odin_batch(
    model: torch.nn.Module,
    views: list[torch.Tensor],
    quality: torch.Tensor,
    temperature: float = 1000.0,
    noise: float = 0.001,
) -> tuple[np.ndarray, np.ndarray]:
    """Return original predictions and ODIN OOD risk for one batch.

    The tabular preprocessing has already standardized each feature, so the
    perturbation is applied directly in standardized input coordinates.
    """

    validate_parameters(temperature, noise)
    model.eval()
    inputs = [value.detach().clone().requires_grad_(True) for value in views]
    logits = model(inputs, quality)["logits"]
    prediction = logits.detach().argmax(dim=1)
    loss = F.cross_entropy(logits / temperature, prediction)
    gradients = torch.autograd.grad(loss, inputs, only_inputs=True)
    perturbed = [
        value.detach() - noise * gradient.detach().sign()
        for value, gradient in zip(inputs, gradients)
    ]
    with torch.no_grad():
        perturbed_logits = model(perturbed, quality)["logits"] / temperature
        confidence = torch.softmax(perturbed_logits, dim=1).max(dim=1).values
    return prediction.cpu().numpy(), (1.0 - confidence).cpu().numpy()


def collect_odin(
    model: torch.nn.Module,
    loader: Any,
    device: torch.device,
    temperature: float = 1000.0,
    noise: float = 0.001,
) -> dict[str, np.ndarray]:
    output: dict[str, list[np.ndarray]] = {
        "labels": [],
        "unknown": [],
        "prediction": [],
        "risk": [],
    }
    for batch in loader:
        views = [value.to(device, non_blocking=True) for value in batch["views"]]
        quality = batch["quality"].to(device, non_blocking=True)
        prediction, risk = odin_batch(
            model, views, quality, temperature=temperature, noise=noise
        )
        output["labels"].append(batch["label"].numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        output["prediction"].append(prediction)
        output["risk"].append(risk)
    return {name: np.concatenate(parts, axis=0) for name, parts in output.items()}


def evidence(temperature: float, noise: float) -> dict[str, object]:
    validate_parameters(temperature, noise)
    return {
        "method": "ODIN",
        "paper": "https://arxiv.org/abs/1706.02690",
        "reference_implementation": (
            "https://github.com/Jingkang50/OpenOOD/blob/main/openood/"
            "postprocessors/odin_postprocessor.py"
        ),
        "protocol_class": "official_formula_frozen_tabular_mlp_adapter",
        "temperature": float(temperature),
        "noise": float(noise),
        "parameter_source": "preregistered canonical values without OOD tuning",
        "input_gradient": "cross_entropy_of_temperature_scaled_pseudo_label",
        "perturbation": "negative_noise_times_gradient_sign",
        "input_coordinates": "already_standardized_tabular_features",
        "classification_prediction": "unperturbed_frozen_mlp",
        "unknown_or_test_labels_used": False,
    }

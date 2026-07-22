from __future__ import annotations

from typing import Dict, Iterable

import torch
from torch import Tensor

from .model import evidence_to_opinion


DEFAULT_TEMPERATURE_GRID = tuple(float(value) for value in torch.linspace(0.5, 3.0, 51))


def apply_evidence_temperature(
    output: Dict[str, Tensor], temperature: float
) -> Dict[str, Tensor]:
    """Temperature-scale fused evidence while preserving class ordering."""
    if not torch.isfinite(torch.tensor(temperature)) or temperature <= 0.0:
        raise ValueError("evidence temperature must be finite and positive")
    evidence = output["fused_evidence"].clamp_min(1e-8).pow(1.0 / temperature)
    alpha, belief, uncertainty = evidence_to_opinion(evidence)
    calibrated = dict(output)
    calibrated.update(
        {
            "fused_evidence": evidence,
            "fused_alpha": alpha,
            "fused_belief": belief,
            "fused_probability": alpha / alpha.sum(dim=-1, keepdim=True),
            "fused_uncertainty": uncertainty.squeeze(-1),
        }
    )
    return calibrated


def fit_known_evidence_temperature(
    output: Dict[str, Tensor],
    labels: Tensor,
    grid: Iterable[float] = DEFAULT_TEMPERATURE_GRID,
) -> tuple[float, float]:
    """Select temperature by known-validation NLL with a deterministic tie break."""
    labels = labels.to(torch.long)
    candidates = []
    for raw_temperature in grid:
        temperature = float(raw_temperature)
        probability = apply_evidence_temperature(output, temperature)[
            "fused_probability"
        ]
        selected = probability[torch.arange(len(labels)), labels].clamp_min(1e-12)
        nll = float((-selected.log().mean()).item())
        candidates.append((nll, abs(temperature - 1.0), temperature))
    if not candidates:
        raise ValueError("evidence temperature grid must be non-empty")
    nll, _, temperature = min(candidates)
    return temperature, nll

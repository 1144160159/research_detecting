from __future__ import annotations

from typing import Sequence

import numpy as np
import torch
from torch import Tensor, nn


PAPER_URL = (
    "https://openaccess.thecvf.com/content/CVPR2025/html/Chen_Leveraging_"
    "Perturbation_Robustness_to_Enhance_Out-of-Distribution_Detection_"
    "CVPR_2025_paper.html"
)
OFFICIAL_CODE_URL = (
    "https://github.com/wenxichen2746/Perturbation-Rectified-OOD-Detection"
)
OFFICIAL_COMMIT = "bb22cc2b1c4c928e4bc38e2d7c7db4f8900df295"


def pro_msp_batch(
    model: nn.Module,
    views: Sequence[Tensor],
    quality: Tensor,
    *,
    step_size: float = 0.003,
    steps: int = 1,
    temperature: float = 1.0,
) -> tuple[Tensor, Tensor, dict[str, object]]:
    """Official PROv2-MSP minimization adapted to standardized tabular views."""
    if not views or any(view.ndim != 2 for view in views):
        raise ValueError("PRO requires non-empty two-dimensional views")
    if len({len(view) for view in views}) != 1 or len(quality) != len(views[0]):
        raise ValueError("PRO views and quality must share the batch dimension")
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("PRO step size must be finite and positive")
    if steps < 1:
        raise ValueError("PRO gradient-descent steps must be positive")
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("PRO temperature must be finite and positive")

    model.eval()
    perturbed = [view.detach().clone() for view in views]
    confidence_path: list[Tensor] = []
    prediction: Tensor | None = None
    for _ in range(steps):
        differentiable = [view.detach().requires_grad_(True) for view in perturbed]
        logits = model(differentiable, quality)["logits"] / temperature
        confidence, current_prediction = torch.softmax(logits, dim=1).max(dim=1)
        if prediction is None:
            prediction = current_prediction.detach()
        confidence_path.append(confidence.detach())
        gradients = torch.autograd.grad(
            confidence.sum(), differentiable, create_graph=False, retain_graph=False
        )
        perturbed = [
            view.detach() - step_size * gradient.detach().sign()
            for view, gradient in zip(differentiable, gradients)
        ]

    with torch.no_grad():
        final_logits = model(perturbed, quality)["logits"] / temperature
        final_confidence = torch.softmax(final_logits, dim=1).max(dim=1).values
    confidence_path.append(final_confidence)
    path = torch.stack(confidence_path, dim=0)
    minimum_confidence = path.min(dim=0).values
    risk = 1.0 - minimum_confidence
    assert prediction is not None
    diagnostics = {
        "path_points": int(path.shape[0]),
        "steps": int(steps),
        "step_size": float(step_size),
        "temperature": float(temperature),
        "minimum_includes_unperturbed_score": True,
        "prediction_source": "unperturbed_frozen_classifier",
        "mean_confidence_drop": float(
            (path[0] - minimum_confidence).mean().detach().cpu()
        ),
        "maximum_confidence_drop": float(
            (path[0] - minimum_confidence).max().detach().cpu()
        ),
    }
    return prediction, risk.detach(), diagnostics


def evidence() -> dict[str, object]:
    return {
        "method": "PRO-MSP-Fixed",
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "official_commit": OFFICIAL_COMMIT,
        "official_class": "PROv2_MSP_Postprocessor",
        "score": "minimum MSP over original and sign-gradient descent path",
        "step_size": 0.003,
        "steps": 1,
        "temperature": 1.0,
        "hyperparameter_policy": "official_config_defaults_no_ood_sweep",
        "input_space": "known-training-standardized tabular coordinates",
        "projection_policy": "none_matching_official_PROv2_MSP_code",
    }

from __future__ import annotations

import numpy as np
import pytest
import torch

import train_strict_v4_pcap_multimodal_task_cuda as task


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is required")
def test_counterfactual_conflict_gate_cuda_backward_is_finite() -> None:
    device = torch.device("cuda:0")
    cache = {
        "payload": np.empty((1, 512), dtype=np.uint16),
        "sequence": np.empty((1, 96), dtype=np.float32),
        "graph": np.empty((1, 336), dtype=np.float32),
    }
    model = task.build_model(
        cache,
        num_classes=3,
        hidden_dim=32,
        embedding_dim=16,
        device=device,
        counterfactual_conflict_gate=True,
    )
    views = [
        torch.randint(0, 257, (6, 512), device=device),
        torch.randn((6, 96), device=device),
        torch.randn((6, 336), device=device),
    ]
    quality = torch.ones((6, 3), device=device)
    labels = torch.tensor([0, 1, 1, 2, 2, 0], device=device)
    mixed_views, mixed_quality, _ = (
        task.cross_family_modality_counterfactuals(
            views,
            quality,
            labels,
            modality_index=1,
        )
    )

    output = model(mixed_views, mixed_quality)
    loss = task.external_surrogate_unknown_loss(
        output,
        evidence_weight=0.05,
        malicious_weight=0.5,
    )["total"]
    loss.backward()

    gradients = [
        parameter.grad
        for parameter in model.counterfactual_conflict_gate.parameters()
        if parameter.grad is not None
    ]
    assert output["fused_evidence"].is_cuda
    assert torch.isfinite(loss)
    assert gradients
    assert all(torch.isfinite(gradient).all() for gradient in gradients)
    assert sum(float(gradient.abs().sum()) for gradient in gradients) > 0.0

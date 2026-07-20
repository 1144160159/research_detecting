from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
import torch
from sklearn.decomposition import PCA
from torch import Tensor


@dataclass
class PCAResidualScorer:
    variance_ratio: float = 0.95

    def __post_init__(self) -> None:
        if not 0.0 < self.variance_ratio <= 1.0:
            raise ValueError("variance_ratio must be in (0, 1]")
        self.model: Optional[PCA] = None

    def fit(self, embeddings: np.ndarray) -> None:
        values = np.asarray(embeddings, dtype=np.float64)
        if values.ndim != 2 or len(values) < 2:
            raise ValueError("PCA anchor embeddings must be a non-empty matrix")
        self.model = PCA(n_components=self.variance_ratio, svd_solver="full")
        self.model.fit(values)

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("PCA residual scorer has not been fitted")
        values = np.asarray(embeddings, dtype=np.float64)
        reconstructed = self.model.inverse_transform(self.model.transform(values))
        return np.linalg.norm(values - reconstructed, axis=1)


def reference_zscore(reference: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    reference = np.asarray(reference, dtype=np.float64).reshape(-1)
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    if not len(reference) or not np.isfinite(reference).all() or not np.isfinite(values).all():
        raise ValueError("TAO Stage-1 scores must be finite and reference must be non-empty")
    mean = float(reference.mean())
    scale = max(float(reference.std()), 1e-8)
    return (reference - mean) / scale, (values - mean) / scale


def hybrid_scores(
    validation_pca: np.ndarray,
    validation_blood: np.ndarray,
    test_pca: np.ndarray,
    test_blood: np.ndarray,
    *,
    alpha: float = 0.6,
) -> tuple[np.ndarray, np.ndarray]:
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    validation_pca_z, test_pca_z = reference_zscore(validation_pca, test_pca)
    validation_blood_z, test_blood_z = reference_zscore(validation_blood, test_blood)
    return (
        alpha * validation_pca_z + (1.0 - alpha) * validation_blood_z,
        alpha * test_pca_z + (1.0 - alpha) * test_blood_z,
    )


def mlp_blood_score(
    model: torch.nn.Module,
    views: Sequence[Tensor],
    *,
    estimators: int = 50,
    seed: int = 0,
) -> np.ndarray:
    """Hutchinson estimate of inter-layer Jacobian smoothness for the shared MLP."""
    if estimators < 1:
        raise ValueError("estimators must be positive")
    network = getattr(getattr(model, "encoder", None), "network", None)
    if not isinstance(network, torch.nn.Sequential) or len(network) != 7:
        raise TypeError("TAO Stage-1 adapter requires the shared two-layer MLP encoder")

    model.eval()
    combined = torch.cat(tuple(views), dim=-1)
    first = network[:3](combined)
    second = network[3:](first)
    estimates = []
    cuda_devices = [combined.device.index or 0] if combined.is_cuda else []
    with torch.random.fork_rng(devices=cuda_devices):
        torch.manual_seed(int(seed))
        if combined.is_cuda:
            torch.cuda.manual_seed_all(int(seed))
        for _ in range(estimators):
            output_probe = torch.randn_like(second)
            gradient = torch.autograd.grad(
                (second * output_probe).sum(), first, retain_graph=True
            )[0]
            input_probe = torch.randn_like(gradient)
            estimates.append(torch.square((gradient * input_probe).sum(dim=1)))
    return torch.stack(estimates, dim=1).mean(dim=1).detach().cpu().numpy()

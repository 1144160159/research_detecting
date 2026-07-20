from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F


@dataclass
class DOCFixedOutput:
    probabilities: np.ndarray
    prediction: np.ndarray
    risk: np.ndarray
    native_reject: np.ndarray


class DOCFixedCalibrator:
    """Frozen-encoder DOC head with the paper's one-vs-rest Gaussian rule."""

    def __init__(self, alpha: float = 3.0, max_iter: int = 100) -> None:
        if alpha <= 0.0 or max_iter <= 0:
            raise ValueError("alpha and max_iter must be positive")
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)

    def fit(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        initial_weight: np.ndarray,
        initial_bias: np.ndarray,
    ) -> "DOCFixedCalibrator":
        x = torch.as_tensor(np.asarray(embeddings), dtype=torch.float32, device="cpu")
        y = torch.as_tensor(np.asarray(labels), dtype=torch.long, device="cpu")
        weight = torch.nn.Parameter(torch.as_tensor(np.asarray(initial_weight), dtype=torch.float32).clone())
        bias = torch.nn.Parameter(torch.as_tensor(np.asarray(initial_bias), dtype=torch.float32).clone())
        if x.ndim != 2 or weight.ndim != 2 or bias.ndim != 1:
            raise ValueError("DOC inputs have invalid dimensions")
        if x.shape[0] != y.shape[0] or x.shape[1] != weight.shape[1] or weight.shape[0] != bias.shape[0]:
            raise ValueError("DOC inputs have incompatible shapes")
        class_count = int(weight.shape[0])
        if set(np.unique(labels).tolist()) != set(range(class_count)):
            raise ValueError("DOC training labels must cover every known class")
        targets = F.one_hot(y, num_classes=class_count).to(dtype=torch.float32)

        def loss_value() -> torch.Tensor:
            return F.binary_cross_entropy_with_logits(x @ weight.t() + bias, targets)

        with torch.no_grad():
            initial_loss = float(loss_value().item())
        optimizer = torch.optim.LBFGS(
            [weight, bias], lr=1.0, max_iter=self.max_iter,
            tolerance_grad=1e-7, tolerance_change=1e-9, line_search_fn="strong_wolfe",
        )
        closure_calls = 0

        def closure() -> torch.Tensor:
            nonlocal closure_calls
            closure_calls += 1
            optimizer.zero_grad(set_to_none=True)
            loss = loss_value()
            loss.backward()
            return loss

        optimizer.step(closure)
        with torch.no_grad():
            final_loss = float(loss_value().item())
            probabilities = torch.sigmoid(x @ weight.t() + bias).cpu().numpy()
        if not np.isfinite(final_loss) or final_loss > initial_loss + 1e-6:
            raise ValueError("DOC optimization did not produce a finite non-increasing loss")

        sigma = np.empty(class_count, dtype=np.float64)
        counts = np.empty(class_count, dtype=np.int64)
        for class_index in range(class_count):
            positive = probabilities[np.asarray(labels) == class_index, class_index]
            if positive.size == 0:
                raise ValueError("DOC class has no positive training samples")
            counts[class_index] = positive.size
            sigma[class_index] = float(np.sqrt(np.mean(np.square(positive - 1.0))))
        thresholds = np.maximum(0.5, 1.0 - self.alpha * sigma)
        if not np.isfinite(thresholds).all():
            raise ValueError("DOC thresholds are not finite")
        self.weight_ = weight.detach().cpu().numpy().astype(np.float64)
        self.bias_ = bias.detach().cpu().numpy().astype(np.float64)
        self.sigma_ = sigma
        self.thresholds_ = thresholds
        self.class_counts_ = counts
        self.initial_loss_ = initial_loss
        self.final_loss_ = final_loss
        self.closure_calls_ = closure_calls
        return self

    def evaluate(self, embeddings: np.ndarray) -> DOCFixedOutput:
        if not hasattr(self, "thresholds_"):
            raise ValueError("DOC calibrator is not fitted")
        logits = np.asarray(embeddings, dtype=np.float64) @ self.weight_.T + self.bias_
        probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -60.0, 60.0)))
        prediction = np.argmax(probabilities, axis=1).astype(np.int64)
        margins = probabilities - self.thresholds_[None, :]
        max_margin = np.max(margins, axis=1)
        return DOCFixedOutput(
            probabilities=probabilities,
            prediction=prediction,
            risk=-max_margin,
            native_reject=max_margin < 0.0,
        )

    def evidence(self) -> dict[str, Any]:
        if not hasattr(self, "thresholds_"):
            raise ValueError("DOC calibrator is not fitted")
        return {
            "alpha": self.alpha,
            "optimizer": "full_batch_lbfgs_strong_wolfe",
            "max_iter": self.max_iter,
            "closure_calls": self.closure_calls_,
            "initial_bce": self.initial_loss_,
            "final_bce": self.final_loss_,
            "class_counts": self.class_counts_.tolist(),
            "sigma": self.sigma_.tolist(),
            "thresholds": self.thresholds_.tolist(),
            "threshold_min": float(self.thresholds_.min()),
            "threshold_max": float(self.thresholds_.max()),
            "fit_uses_known_training_only": True,
        }

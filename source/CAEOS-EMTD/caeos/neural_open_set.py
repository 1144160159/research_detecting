from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Sequence

import numpy as np
import torch
from scipy.stats import weibull_min
from scipy.special import logsumexp
from sklearn.covariance import LedoitWolf
from torch import Tensor, nn

from .model import ViewEncoder


def msp_risk(logits: np.ndarray) -> np.ndarray:
    probability = torch.softmax(torch.as_tensor(logits), dim=1).numpy()
    return 1.0 - probability.max(axis=1)


def energy_risk(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    values = torch.as_tensor(logits, dtype=torch.float64)
    return (-float(temperature) * torch.logsumexp(values / temperature, dim=1)).numpy()


class ReActCalibrator:
    """ReAct activation clipping fitted on known-only embeddings."""

    def __init__(self, percentile: float = 90.0, temperature: float = 1.0):
        if not 0.0 <= percentile <= 100.0:
            raise ValueError("ReAct percentile must be in [0, 100]")
        if temperature <= 0.0:
            raise ValueError("ReAct temperature must be positive")
        self.percentile = float(percentile)
        self.temperature = float(temperature)
        self.activation_cap: float | None = None
        self.classifier_weight: np.ndarray | None = None
        self.classifier_bias: np.ndarray | None = None
        self.train_count: int | None = None

    def fit(
        self,
        train_embeddings: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray,
    ) -> None:
        embeddings = np.asarray(train_embeddings, dtype=np.float64)
        weight = np.asarray(classifier_weight, dtype=np.float64)
        bias = np.asarray(classifier_bias, dtype=np.float64).reshape(-1)
        if embeddings.ndim != 2 or not len(embeddings):
            raise ValueError("ReAct train embeddings must be a non-empty matrix")
        if weight.ndim != 2 or weight.shape[1] != embeddings.shape[1]:
            raise ValueError("ReAct classifier weight and embedding dimensions differ")
        if len(bias) != weight.shape[0]:
            raise ValueError("ReAct classifier bias and weight class counts differ")
        self.activation_cap = float(np.percentile(embeddings.reshape(-1), self.percentile))
        self.classifier_weight = weight.copy()
        self.classifier_bias = bias.copy()
        self.train_count = int(len(embeddings))

    def logits(self, embeddings: np.ndarray) -> np.ndarray:
        if (
            self.activation_cap is None
            or self.classifier_weight is None
            or self.classifier_bias is None
        ):
            raise RuntimeError("ReAct calibrator has not been fitted")
        embeddings = np.asarray(embeddings, dtype=np.float64)
        if embeddings.ndim != 2 or embeddings.shape[1] != self.classifier_weight.shape[1]:
            raise ValueError("ReAct embeddings have an incompatible shape")
        clipped = np.minimum(embeddings, self.activation_cap)
        return clipped @ self.classifier_weight.T + self.classifier_bias

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        return energy_risk(self.logits(embeddings), self.temperature)

    def evidence(self) -> dict[str, object]:
        if self.activation_cap is None or self.train_count is None:
            raise RuntimeError("ReAct calibrator has not been fitted")
        return {
            "method": "ReAct",
            "paper": "https://proceedings.neurips.cc/paper/2021/hash/01894d6f048493d2cacde3c579c315a3-Abstract.html",
            "official_code": "https://github.com/deeplearning-wisc/react",
            "protocol_class": "official_formula_shared_mlp_adapter",
            "fit_split": "known_only_train",
            "percentile": self.percentile,
            "percentile_source": "official_default_90",
            "temperature": self.temperature,
            "activation_cap": self.activation_cap,
            "train_embedding_count": self.train_count,
            "unknown_or_test_labels_used": False,
        }


class DICECalibrator:
    """DICE contribution sparsification fitted on known-only embeddings."""

    def __init__(self, percentile: float = 90.0, temperature: float = 1.0):
        if not 0.0 <= percentile <= 100.0:
            raise ValueError("DICE percentile must be in [0, 100]")
        if temperature <= 0.0:
            raise ValueError("DICE temperature must be positive")
        self.percentile = float(percentile)
        self.temperature = float(temperature)
        self.sparse_weight: np.ndarray | None = None
        self.classifier_bias: np.ndarray | None = None
        self.contribution_threshold: float | None = None
        self.retained_fraction: float | None = None
        self.train_count: int | None = None

    def fit(
        self,
        train_embeddings: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray,
    ) -> None:
        embeddings = np.asarray(train_embeddings, dtype=np.float64)
        weight = np.asarray(classifier_weight, dtype=np.float64)
        bias = np.asarray(classifier_bias, dtype=np.float64).reshape(-1)
        if embeddings.ndim != 2 or not len(embeddings):
            raise ValueError("DICE train embeddings must be a non-empty matrix")
        if weight.ndim != 2 or weight.shape[1] != embeddings.shape[1]:
            raise ValueError("DICE classifier weight and embedding dimensions differ")
        if len(bias) != weight.shape[0]:
            raise ValueError("DICE classifier bias and weight class counts differ")
        contribution = weight * embeddings.mean(axis=0)[None, :]
        self.contribution_threshold = float(
            np.percentile(contribution.reshape(-1), self.percentile)
        )
        mask = contribution > self.contribution_threshold
        self.sparse_weight = weight * mask
        self.classifier_bias = bias.copy()
        self.retained_fraction = float(mask.mean())
        self.train_count = int(len(embeddings))

    def logits(self, embeddings: np.ndarray) -> np.ndarray:
        if self.sparse_weight is None or self.classifier_bias is None:
            raise RuntimeError("DICE calibrator has not been fitted")
        embeddings = np.asarray(embeddings, dtype=np.float64)
        if embeddings.ndim != 2 or embeddings.shape[1] != self.sparse_weight.shape[1]:
            raise ValueError("DICE embeddings have an incompatible shape")
        return embeddings @ self.sparse_weight.T + self.classifier_bias

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        return energy_risk(self.logits(embeddings), self.temperature)

    def evidence(self) -> dict[str, object]:
        if (
            self.contribution_threshold is None
            or self.retained_fraction is None
            or self.train_count is None
        ):
            raise RuntimeError("DICE calibrator has not been fitted")
        return {
            "method": "DICE",
            "paper": "https://arxiv.org/abs/2111.09805",
            "official_code": "https://github.com/deeplearning-wisc/dice",
            "protocol_class": "official_formula_shared_mlp_adapter",
            "fit_split": "known_only_train",
            "percentile": self.percentile,
            "percentile_source": "official_default_90",
            "temperature": self.temperature,
            "contribution_threshold": self.contribution_threshold,
            "retained_fraction": self.retained_fraction,
            "train_embedding_count": self.train_count,
            "unknown_or_test_labels_used": False,
        }


class SHECalibrator:
    """Simplified Hopfield Energy using one correct-train pattern per class."""

    def __init__(self):
        self.patterns: np.ndarray | None = None
        self.correct_train_count: int | None = None
        self.class_counts: list[int] | None = None

    def fit(
        self,
        train_embeddings: np.ndarray,
        train_logits: np.ndarray,
        train_labels: np.ndarray,
    ) -> None:
        embeddings = np.asarray(train_embeddings, dtype=np.float64)
        logits = np.asarray(train_logits, dtype=np.float64)
        labels = np.asarray(train_labels, dtype=np.int64).reshape(-1)
        if embeddings.ndim != 2 or logits.ndim != 2 or not len(embeddings):
            raise ValueError("SHE fitting inputs must be non-empty matrices")
        if len(embeddings) != len(logits) or len(labels) != len(embeddings):
            raise ValueError("SHE fitting inputs have different row counts")
        if labels.min() < 0 or labels.max() >= logits.shape[1]:
            raise ValueError("SHE labels exceed the classifier class range")
        predictions = logits.argmax(axis=1)
        correct = predictions == labels
        patterns = []
        counts = []
        for class_index in range(logits.shape[1]):
            selected = embeddings[correct & (predictions == class_index)]
            if not len(selected):
                raise ValueError(
                    f"SHE has no correctly classified train pattern for class {class_index}"
                )
            patterns.append(selected.mean(axis=0))
            counts.append(int(len(selected)))
        self.patterns = np.stack(patterns)
        self.correct_train_count = int(correct.sum())
        self.class_counts = counts

    def score(self, embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
        if self.patterns is None:
            raise RuntimeError("SHE calibrator has not been fitted")
        embeddings = np.asarray(embeddings, dtype=np.float64)
        logits = np.asarray(logits, dtype=np.float64)
        if embeddings.ndim != 2 or logits.ndim != 2 or len(embeddings) != len(logits):
            raise ValueError("SHE scoring inputs have incompatible shapes")
        if embeddings.shape[1] != self.patterns.shape[1] or logits.shape[1] != len(self.patterns):
            raise ValueError("SHE scoring dimensions differ from stored patterns")
        prediction = logits.argmax(axis=1)
        knownness = np.einsum("nd,nd->n", embeddings, self.patterns[prediction])
        return -knownness

    def evidence(self) -> dict[str, object]:
        if self.patterns is None or self.correct_train_count is None or self.class_counts is None:
            raise RuntimeError("SHE calibrator has not been fitted")
        return {
            "method": "SHE",
            "paper": "https://openreview.net/forum?id=KkazG4lgKL",
            "official_code": "https://github.com/zjs975584714/SHE_ood_detection",
            "protocol_class": "official_formula_shared_mlp_adapter",
            "fit_split": "correctly_classified_known_only_train",
            "stored_pattern": "per_class_mean_penultimate_embedding",
            "metric": "inner_product",
            "correct_train_count": self.correct_train_count,
            "correct_train_count_by_class": self.class_counts,
            "unknown_or_test_labels_used": False,
        }


class NCICalibrator:
    """Neural-collapse-inspired OOD score from the official NCI postprocessor.

    The official implementation returns an ID confidence.  This adapter returns
    its negative so that larger values consistently mean higher OOD risk in the
    CAEOS evaluation stack.
    """

    def __init__(self, alpha: float = 0.0001, epsilon: float = 1e-12):
        if alpha < 0.0:
            raise ValueError("NCI alpha must be non-negative")
        if epsilon <= 0.0:
            raise ValueError("NCI epsilon must be positive")
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.train_mean: np.ndarray | None = None
        self.classifier_weight: np.ndarray | None = None
        self.train_count: int | None = None

    def fit(self, train_embeddings: np.ndarray, classifier_weight: np.ndarray) -> None:
        embeddings = np.asarray(train_embeddings, dtype=np.float64)
        weight = np.asarray(classifier_weight, dtype=np.float64)
        if embeddings.ndim != 2 or not len(embeddings):
            raise ValueError("NCI train embeddings must be a non-empty matrix")
        if weight.ndim != 2 or weight.shape[1] != embeddings.shape[1]:
            raise ValueError("NCI classifier weight and embedding dimensions differ")
        self.train_mean = embeddings.mean(axis=0)
        self.classifier_weight = weight.copy()
        self.train_count = int(len(embeddings))

    def knownness(self, embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
        if self.train_mean is None or self.classifier_weight is None:
            raise RuntimeError("NCI calibrator has not been fitted")
        embeddings = np.asarray(embeddings, dtype=np.float64)
        logits = np.asarray(logits, dtype=np.float64)
        if embeddings.ndim != 2 or logits.ndim != 2:
            raise ValueError("NCI embeddings and logits must be matrices")
        if len(embeddings) != len(logits):
            raise ValueError("NCI embeddings and logits have different row counts")
        if logits.shape[1] != self.classifier_weight.shape[0]:
            raise ValueError("NCI logits and classifier weight have different class counts")

        prediction = logits.argmax(axis=1)
        centered = embeddings - self.train_mean
        alignment = np.einsum(
            "nd,nd->n", self.classifier_weight[prediction], centered
        ) / np.maximum(np.linalg.norm(centered, axis=1), self.epsilon)
        feature_norm = np.linalg.norm(embeddings, ord=1, axis=1)
        return alignment + self.alpha * feature_norm

    def score(self, embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
        return -self.knownness(embeddings, logits)

    def evidence(self) -> dict[str, object]:
        if self.train_mean is None or self.classifier_weight is None:
            raise RuntimeError("NCI calibrator has not been fitted")
        return {
            "method": "NCI",
            "paper": "https://arxiv.org/abs/2311.01479",
            "official_code": "https://github.com/litianliu/NCI-OOD",
            "fit_split": "known_only_train",
            "alpha": self.alpha,
            "official_default_alpha": 0.0001,
            "alpha_source": (
                "fixed_official_default_without_auxiliary_ood_sweep"
                if self.alpha == 0.0001
                else "fixed_cli_value_without_auxiliary_ood_sweep"
            ),
            "train_embedding_count": self.train_count,
            "feature_dimension": int(self.train_mean.shape[0]),
            "unknown_or_test_labels_used": False,
        }


class CEACalibrator:
    """Capture Extreme Activations (CEA) with known-only validation fitting."""

    def __init__(
        self,
        percentile: float = 99.9,
        addition_coefficient: float = 10.0,
        threshold_caution_coefficient: float = 1.1,
        denominator_offset: float = 0.1,
    ):
        if not 0.0 <= percentile <= 100.0:
            raise ValueError("CEA percentile must be in [0, 100]")
        if addition_coefficient < 0.0:
            raise ValueError("CEA addition coefficient must be non-negative")
        if threshold_caution_coefficient <= 0.0:
            raise ValueError("CEA threshold caution coefficient must be positive")
        if denominator_offset <= 0.0:
            raise ValueError("CEA denominator offset must be positive")
        self.percentile = float(percentile)
        self.addition_coefficient = float(addition_coefficient)
        self.threshold_caution_coefficient = float(
            threshold_caution_coefficient
        )
        self.denominator_offset = float(denominator_offset)
        self.threshold: float | None = None
        self.coefficient: float | None = None
        self.validation_count: int | None = None

    def extreme_activation(self, embeddings: np.ndarray) -> np.ndarray:
        if self.threshold is None:
            raise RuntimeError("CEA calibrator has not been fitted")
        embeddings = np.asarray(embeddings, dtype=np.float64)
        if embeddings.ndim != 2:
            raise ValueError("CEA embeddings must be a matrix")
        excess = np.maximum(embeddings - self.threshold, 0.0)
        return np.linalg.norm(excess, axis=1)

    def fit(
        self, validation_embeddings: np.ndarray, validation_base_risk: np.ndarray
    ) -> None:
        embeddings = np.asarray(validation_embeddings, dtype=np.float64)
        base_risk = np.asarray(validation_base_risk, dtype=np.float64).reshape(-1)
        if embeddings.ndim != 2 or not len(embeddings):
            raise ValueError("CEA validation embeddings must be a non-empty matrix")
        if len(embeddings) != len(base_risk):
            raise ValueError("CEA validation embeddings and risks have different row counts")
        if not np.isfinite(embeddings).all() or not np.isfinite(base_risk).all():
            raise ValueError("CEA fitting inputs must be finite")

        self.threshold = self.threshold_caution_coefficient * float(
            np.percentile(embeddings.reshape(-1), self.percentile)
        )
        added_risk = self.extreme_activation(embeddings)
        self.coefficient = self.addition_coefficient * abs(float(base_risk.mean())) / (
            abs(float(added_risk.mean())) + self.denominator_offset
        )
        self.validation_count = int(len(embeddings))

    def score(self, embeddings: np.ndarray, base_risk: np.ndarray) -> np.ndarray:
        if self.coefficient is None:
            raise RuntimeError("CEA calibrator has not been fitted")
        base_risk = np.asarray(base_risk, dtype=np.float64).reshape(-1)
        added_risk = self.extreme_activation(embeddings)
        if len(added_risk) != len(base_risk):
            raise ValueError("CEA embeddings and base risks have different row counts")
        return base_risk + self.coefficient * added_risk

    def evidence(self) -> dict[str, object]:
        if self.threshold is None or self.coefficient is None:
            raise RuntimeError("CEA calibrator has not been fitted")
        return {
            "method": "CEA",
            "paper": "https://proceedings.mlr.press/v244/azizmalayeri24a.html",
            "official_code": "https://github.com/mazizmalayeri/CEA",
            "fit_split": "known_only_validation",
            "percentile": self.percentile,
            "addition_coefficient": self.addition_coefficient,
            "threshold_caution_coefficient": self.threshold_caution_coefficient,
            "denominator_offset": self.denominator_offset,
            "hyperparameter_source": (
                "fixed_official_defaults"
                if (
                    self.percentile == 99.9
                    and self.addition_coefficient == 10.0
                    and self.threshold_caution_coefficient == 1.1
                    and self.denominator_offset == 0.1
                )
                else "fixed_cli_values"
            ),
            "fitted_threshold": self.threshold,
            "fitted_score_coefficient": self.coefficient,
            "validation_embedding_count": self.validation_count,
            "unknown_or_test_labels_used": False,
        }


class SharedCovarianceMahalanobis:
    """Minimum class distance under a shrinkage shared covariance estimate."""

    def __init__(self):
        self.means: np.ndarray | None = None
        self.precision: np.ndarray | None = None

    def fit(self, values: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        classes = np.arange(int(labels.max()) + 1)
        self.means = np.stack([values[labels == index].mean(axis=0) for index in classes])
        residuals = np.concatenate(
            [values[labels == index] - self.means[index] for index in classes], axis=0
        )
        self.precision = LedoitWolf(assume_centered=True).fit(residuals).precision_

    def score(self, values: np.ndarray) -> np.ndarray:
        if self.means is None or self.precision is None:
            raise RuntimeError("Mahalanobis model has not been fitted")
        delta = np.asarray(values, dtype=np.float64)[:, None, :] - self.means[None, :, :]
        squared = np.einsum("ncd,de,nce->nc", delta, self.precision, delta)
        return np.sqrt(np.maximum(squared.min(axis=1), 0.0))


class RelativeMahalanobis:
    """Class-conditional distance after subtracting global background distance."""

    def __init__(self):
        self.class_model = SharedCovarianceMahalanobis()
        self.global_mean: np.ndarray | None = None
        self.global_precision: np.ndarray | None = None

    def fit(self, values: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        self.class_model.fit(values, labels)
        self.global_mean = values.mean(axis=0)
        centered = values - self.global_mean
        self.global_precision = LedoitWolf(assume_centered=True).fit(centered).precision_

    def score(self, values: np.ndarray) -> np.ndarray:
        if self.global_mean is None or self.global_precision is None:
            raise RuntimeError("relative Mahalanobis model has not been fitted")
        values = np.asarray(values, dtype=np.float64)
        class_distance = np.square(self.class_model.score(values))
        delta = values - self.global_mean
        global_distance = np.einsum("nd,de,ne->n", delta, self.global_precision, delta)
        return class_distance - global_distance


class ViMCalibrator:
    """Virtual-logit matching using the low-variance embedding residual space."""

    def __init__(self, principal_dimension: int | None = None):
        self.principal_dimension = principal_dimension
        self.origin: np.ndarray | None = None
        self.null_basis: np.ndarray | None = None
        self.alpha: float | None = None

    def fit(
        self,
        embeddings: np.ndarray,
        logits: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray,
    ) -> None:
        embeddings = np.asarray(embeddings, dtype=np.float64)
        logits = np.asarray(logits, dtype=np.float64)
        weight = np.asarray(classifier_weight, dtype=np.float64)
        bias = np.asarray(classifier_bias, dtype=np.float64)
        dimension = embeddings.shape[1]
        principal = self.principal_dimension
        if principal is None:
            principal = max(1, dimension // 2)
        principal = min(max(1, int(principal)), dimension - 1)
        self.origin = -np.linalg.pinv(weight) @ bias
        centered = embeddings - self.origin
        covariance = np.cov(centered, rowvar=False)
        _, eigenvectors = np.linalg.eigh(covariance)
        self.null_basis = eigenvectors[:, : dimension - principal]
        residual = np.linalg.norm(centered @ self.null_basis, axis=1)
        known_logit = logits.max(axis=1).mean()
        self.alpha = float(max(abs(known_logit), 1e-8) / max(residual.mean(), 1e-8))

    def score(self, embeddings: np.ndarray, logits: np.ndarray) -> np.ndarray:
        if self.origin is None or self.null_basis is None or self.alpha is None:
            raise RuntimeError("ViM calibrator has not been fitted")
        centered = np.asarray(embeddings, dtype=np.float64) - self.origin
        residual = np.linalg.norm(centered @ self.null_basis, axis=1)
        energy = logsumexp(np.asarray(logits, dtype=np.float64), axis=1)
        return self.alpha * residual - energy


@dataclass
class WeibullTail:
    shape: float
    scale: float

    def cdf(self, value: np.ndarray) -> np.ndarray:
        return weibull_min.cdf(value, self.shape, loc=0.0, scale=self.scale)


class OpenMaxCalibrator:
    """OpenMax recalibration using correct-class MAVs and Weibull tail fitting."""

    def __init__(self, tail_size: int = 20, alpha: int = 10):
        self.tail_size = int(tail_size)
        self.alpha = int(alpha)
        self.means: np.ndarray | None = None
        self.tails: list[WeibullTail] = []

    def fit(self, logits: np.ndarray, labels: np.ndarray) -> None:
        logits = np.asarray(logits, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        prediction = logits.argmax(axis=1)
        classes = np.arange(logits.shape[1])
        means = []
        tails = []
        for class_index in classes:
            selected = logits[(labels == class_index) & (prediction == class_index)]
            if len(selected) == 0:
                selected = logits[labels == class_index]
            if len(selected) == 0:
                raise ValueError(f"class {class_index} has no OpenMax fitting samples")
            mean = selected.mean(axis=0)
            distance = np.linalg.norm(selected - mean, axis=1)
            tail = np.sort(distance)[-min(self.tail_size, len(distance)) :]
            tail = np.maximum(tail, 1e-8)
            try:
                shape, _, scale = weibull_min.fit(tail, floc=0.0)
            except (ValueError, FloatingPointError):
                shape, scale = 1.0, float(tail.mean())
            if not np.isfinite(shape) or shape <= 0:
                shape = 1.0
            if not np.isfinite(scale) or scale <= 0:
                scale = float(max(tail.mean(), 1e-8))
            means.append(mean)
            tails.append(WeibullTail(float(shape), float(scale)))
        self.means = np.stack(means)
        self.tails = tails

    def predict(self, logits: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if self.means is None or not self.tails:
            raise RuntimeError("OpenMax calibrator has not been fitted")
        logits = np.asarray(logits, dtype=np.float64)
        class_count = logits.shape[1]
        alpha = min(self.alpha, class_count)
        order = np.argsort(logits, axis=1)[:, ::-1]
        rank_weight = np.zeros_like(logits)
        for rank in range(alpha):
            rank_weight[np.arange(len(logits)), order[:, rank]] = (alpha - rank) / alpha

        revised = logits.copy()
        unknown_activation = np.zeros(len(logits), dtype=np.float64)
        for class_index in range(class_count):
            distance = np.linalg.norm(logits - self.means[class_index], axis=1)
            outlier_probability = self.tails[class_index].cdf(distance)
            removed = logits[:, class_index] * rank_weight[:, class_index] * outlier_probability
            revised[:, class_index] -= removed
            unknown_activation += removed

        activation = np.concatenate([revised, unknown_activation[:, None]], axis=1)
        activation -= activation.max(axis=1, keepdims=True)
        probability = np.exp(activation)
        probability /= probability.sum(axis=1, keepdims=True)
        return probability[:, -1], probability[:, :-1].argmax(axis=1)


class ARPLClassifier(nn.Module):
    """Tabular adaptation of the official ARPL reciprocal-point objective."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        temperature: float = 1.0,
        radius_weight: float = 0.1,
    ):
        super().__init__()
        self.encoder = ViewEncoder(sum(input_dims), hidden_dim, embedding_dim, dropout)
        self.points = nn.Parameter(0.1 * torch.randn(num_classes, embedding_dim))
        self.radius = nn.Parameter(torch.zeros(1))
        self.temperature = float(temperature)
        self.radius_weight = float(radius_weight)
        self.margin_loss = nn.MarginRankingLoss(margin=1.0)

    def forward(self, views: Sequence[Tensor], quality: Tensor = None) -> Dict[str, Tensor]:
        embedding = self.encoder(torch.cat(list(views), dim=-1))
        squared_l2 = torch.square(embedding[:, None, :] - self.points[None, :, :]).mean(dim=2)
        dot = embedding @ self.points.t()
        logits = squared_l2 - dot
        return {"logits": logits, "embedding": embedding}

    def loss(self, output: Dict[str, Tensor], labels: Tensor) -> Tensor:
        logits = output["logits"]
        embedding = output["embedding"]
        classification = nn.functional.cross_entropy(logits / self.temperature, labels)
        class_points = self.points[labels]
        known_distance = torch.square(embedding - class_points).mean(dim=1)
        target = torch.ones_like(known_distance)
        radius = self.radius.expand_as(known_distance)
        radius_loss = self.margin_loss(radius, known_distance, target)
        return classification + self.radius_weight * radius_loss


class ResidualConv1DBlock(nn.Module):
    def __init__(self, channels: int, dropout: float):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv1d(channels, channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(channels),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Conv1d(channels, channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(channels),
        )

    def forward(self, values: Tensor) -> Tensor:
        return nn.functional.gelu(values + self.network(values))


class HybridConvolutionEncoder(nn.Module):
    """Paper-structure adapter for HCRP-OSD's 1D/2D hybrid backbone."""

    def __init__(
        self,
        input_dim: int,
        embedding_dim: int,
        channels: int = 32,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_dim = int(input_dim)
        self.side = int(math.ceil(math.sqrt(self.input_dim)))
        self.padded_dim = self.side * self.side
        self.one_dimensional = nn.Sequential(
            nn.Conv1d(1, channels, kernel_size=5, padding=2, bias=False),
            nn.BatchNorm1d(channels),
            nn.GELU(),
            ResidualConv1DBlock(channels, dropout),
            ResidualConv1DBlock(channels, dropout),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
        )
        self.two_dimensional = nn.Sequential(
            nn.Conv2d(1, channels // 2, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(channels // 2),
            nn.GELU(),
            nn.Conv2d(
                channels // 2, channels, kernel_size=3, padding=1, bias=False
            ),
            nn.BatchNorm2d(channels),
            nn.GELU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )
        self.projection = nn.Sequential(
            nn.Linear(2 * channels, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )

    def forward(self, values: Tensor) -> Tensor:
        if values.ndim != 2 or values.shape[1] != self.input_dim:
            raise ValueError("HCRP hybrid encoder received an incompatible input")
        one_dimensional = self.one_dimensional(values.unsqueeze(1))
        if self.padded_dim != self.input_dim:
            values = nn.functional.pad(values, (0, self.padded_dim - self.input_dim))
        image = values.reshape(len(values), 1, self.side, self.side)
        two_dimensional = self.two_dimensional(image)
        return self.projection(torch.cat([one_dimensional, two_dimensional], dim=1))


class HCRPOSDClassifier(ARPLClassifier):
    """HCRP-OSD paper-structure adapter with the shared ARPL objective."""

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 32,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        temperature: float = 1.0,
        radius_weight: float = 0.1,
    ):
        super().__init__(
            input_dims,
            num_classes,
            hidden_dim,
            embedding_dim,
            dropout,
            temperature,
            radius_weight,
        )
        self.encoder = HybridConvolutionEncoder(
            sum(input_dims), embedding_dim, max(8, hidden_dim), dropout
        )


def arpl_risk(logits: np.ndarray) -> np.ndarray:
    """Official ARPL evaluation treats maximum reciprocal logit as knownness."""
    return -np.asarray(logits, dtype=np.float64).max(axis=1)


def max_logit_risk(logits: np.ndarray) -> np.ndarray:
    return -np.asarray(logits, dtype=np.float64).max(axis=1)

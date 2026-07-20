from __future__ import annotations

import math
from typing import Dict, Sequence

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F

from .model import ViewEncoder


PALM_PAPER = "https://arxiv.org/abs/2402.02653"
PALM_OFFICIAL_CODE = "https://github.com/jeff024/PALM"


def balanced_sinkhorn_assignments(
    features: Tensor,
    prototypes: Tensor,
    epsilon: float = 0.05,
    iterations: int = 3,
) -> Tensor:
    """Return PALM's balanced sample-to-prototype soft assignments.

    The returned matrix has shape ``[samples, prototypes]``. Its rows sum to
    one and its columns approach ``samples / prototypes`` within the requested
    finite iteration budget, matching the official equipartition updates.
    """

    if features.ndim != 2 or prototypes.ndim != 2:
        raise ValueError("PALM features and prototypes must be matrices")
    if not len(features) or not len(prototypes):
        raise ValueError("PALM assignments require non-empty inputs")
    if features.shape[1] != prototypes.shape[1]:
        raise ValueError("PALM feature and prototype dimensions differ")
    if epsilon <= 0.0:
        raise ValueError("PALM assignment epsilon must be positive")
    if iterations < 1:
        raise ValueError("PALM Sinkhorn iterations must be positive")

    features = F.normalize(features, dim=1)
    prototypes = F.normalize(prototypes, dim=1)
    logits = features @ prototypes.detach().t() / float(epsilon)
    # The max subtraction is algebraically neutral after normalization and
    # avoids the overflow recovery branch in the original implementation.
    assignment = torch.exp((logits - logits.max()).t())
    assignment = assignment / assignment.sum().clamp_min(1e-12)
    sample_count = assignment.shape[1]
    prototype_count = assignment.shape[0]
    for _ in range(int(iterations)):
        assignment = assignment / assignment.sum(dim=1, keepdim=True).clamp_min(1e-12)
        assignment = assignment / float(prototype_count)
        assignment = assignment / assignment.sum(dim=0, keepdim=True).clamp_min(1e-12)
        assignment = assignment / float(sample_count)
    return (assignment * float(sample_count)).t()


class PALMObjective(nn.Module):
    """PALM MLE and prototype-contrastive objective with EMA prototypes.

    Prototypes are non-gradient state, as in the official implementation.
    Their current-step differentiable EMA expression is retained solely for
    the prototype-contrastive term before the detached state is committed.
    """

    def __init__(
        self,
        num_classes: int,
        embedding_dim: int,
        prototypes_per_class: int = 6,
        assignment_top_k: int = 5,
        prototype_momentum: float = 0.999,
        temperature: float = 0.1,
        assignment_epsilon: float = 0.05,
        sinkhorn_iterations: int = 3,
        prototype_contrast_weight: float = 1.0,
        prototype_contrast_temperature: float = 0.5,
    ) -> None:
        super().__init__()
        if num_classes < 2:
            raise ValueError("PALM requires at least two known classes")
        if embedding_dim < 2:
            raise ValueError("PALM embedding dimension must exceed one")
        if prototypes_per_class < 2:
            raise ValueError("PALM requires multiple prototypes per class")
        if assignment_top_k < 0 or assignment_top_k > prototypes_per_class:
            raise ValueError(
                "PALM assignment top-k must be zero or no larger than the class cache"
            )
        if not 0.0 <= prototype_momentum < 1.0:
            raise ValueError("PALM prototype momentum must be in [0, 1)")
        if temperature <= 0.0 or assignment_epsilon <= 0.0:
            raise ValueError("PALM temperatures must be positive")
        if sinkhorn_iterations < 1:
            raise ValueError("PALM Sinkhorn iterations must be positive")
        if prototype_contrast_weight < 0.0:
            raise ValueError("PALM prototype contrast weight must be non-negative")
        if prototype_contrast_temperature <= 0.0:
            raise ValueError("PALM prototype contrast temperature must be positive")

        self.num_classes = int(num_classes)
        self.embedding_dim = int(embedding_dim)
        self.prototypes_per_class = int(prototypes_per_class)
        self.assignment_top_k = int(assignment_top_k)
        self.prototype_momentum = float(prototype_momentum)
        self.temperature = float(temperature)
        self.assignment_epsilon = float(assignment_epsilon)
        self.sinkhorn_iterations = int(sinkhorn_iterations)
        self.prototype_contrast_weight = float(prototype_contrast_weight)
        self.prototype_contrast_temperature = float(
            prototype_contrast_temperature
        )

        prototype_count = self.num_classes * self.prototypes_per_class
        initial = F.normalize(torch.rand(prototype_count, embedding_dim), dim=1)
        self.register_buffer("prototypes", initial)
        self.register_buffer("update_count", torch.zeros((), dtype=torch.long))
        self.last_components: dict[str, float] = {}

    @property
    def prototype_labels(self) -> Tensor:
        return torch.arange(
            self.num_classes, device=self.prototypes.device
        ).repeat_interleave(self.prototypes_per_class)

    @staticmethod
    def _flatten_views(features: Tensor, labels: Tensor) -> tuple[Tensor, Tensor]:
        if features.ndim == 2:
            features = features[:, None, :]
        if features.ndim != 3 or labels.ndim != 1:
            raise ValueError("PALM expects [batch, views, dim] features and vector labels")
        if features.shape[0] != len(labels):
            raise ValueError("PALM features and labels contain different sample counts")
        # This is the same view-major order used by the official torch.unbind +
        # cat implementation.
        flattened = torch.cat(torch.unbind(features, dim=1), dim=0)
        repeated_labels = labels.contiguous().repeat(features.shape[1])
        return F.normalize(flattened, dim=1), repeated_labels

    def soft_assignments(self, features: Tensor) -> Tensor:
        return balanced_sinkhorn_assignments(
            features,
            self.prototypes,
            self.assignment_epsilon,
            self.sinkhorn_iterations,
        )

    def class_assignment_mask(
        self, assignments: Tensor, labels: Tensor
    ) -> Tensor:
        if assignments.ndim != 2 or labels.ndim != 1:
            raise ValueError("PALM assignments must be a matrix with vector labels")
        if len(assignments) != len(labels):
            raise ValueError("PALM assignments and labels have different row counts")
        if assignments.shape[1] != len(self.prototypes):
            raise ValueError("PALM assignment width differs from the prototype count")
        if labels.numel() and (
            int(labels.min()) < 0 or int(labels.max()) >= self.num_classes
        ):
            raise ValueError("PALM labels fall outside the known class range")

        same_class = labels[:, None].eq(self.prototype_labels[None, :])
        if 0 < self.assignment_top_k < self.prototypes_per_class:
            ranked = assignments.masked_fill(~same_class, float("-inf"))
            indices = ranked.topk(self.assignment_top_k, dim=1).indices
            return torch.zeros_like(same_class).scatter(1, indices, True)
        return same_class

    def class_assignment_weights(
        self,
        assignments: Tensor,
        labels: Tensor,
        selected_mask: Tensor | None = None,
    ) -> Tensor:
        if selected_mask is None:
            selected_mask = self.class_assignment_mask(assignments, labels)
        elif selected_mask.shape != assignments.shape:
            raise ValueError("PALM selected prototype mask has an invalid shape")
        weights = assignments * selected_mask.to(assignments.dtype)
        return weights / weights.sum(dim=1, keepdim=True).clamp_min(1e-12)

    def _updated_prototypes(self, features: Tensor, weights: Tensor) -> Tensor:
        # Official PALM first normalizes per sample and then per prototype.
        update_weights = weights / weights.sum(dim=0, keepdim=True).clamp_min(1e-12)
        update_features = update_weights.t() @ features
        updated = (
            self.prototype_momentum * self.prototypes.detach()
            + (1.0 - self.prototype_momentum) * update_features
        )
        return F.normalize(updated, dim=1)

    def _mle_loss(
        self,
        features: Tensor,
        labels: Tensor,
        prototypes: Tensor,
        selected_mask: Tensor,
    ) -> Tensor:
        assignments = balanced_sinkhorn_assignments(
            features,
            prototypes,
            self.assignment_epsilon,
            self.sinkhorn_iterations,
        )
        # Official PALM freezes the pre-update top-k indices and only refreshes
        # their Sinkhorn weights after the EMA prototype update.
        positive_weights = self.class_assignment_weights(
            assignments, labels, selected_mask
        )
        logits = features @ prototypes.detach().t() / self.temperature
        positive = (positive_weights * logits).sum(dim=1)
        normalizer = torch.logsumexp(logits, dim=1)
        return (normalizer - positive).mean()

    def _prototype_contrastive_loss(self, prototypes: Tensor) -> Tensor:
        prototypes = F.normalize(prototypes, dim=1)
        labels = self.prototype_labels
        similarities = prototypes @ prototypes.t()
        similarities = similarities / self.prototype_contrast_temperature
        similarities = similarities - similarities.max(
            dim=1, keepdim=True
        ).values.detach()
        diagonal = torch.eye(
            len(prototypes), device=prototypes.device, dtype=torch.bool
        )
        positive = labels[:, None].eq(labels[None, :]) & ~diagonal
        positive_weights = positive.to(similarities.dtype)
        positive_weights = positive_weights / positive_weights.sum(
            dim=1, keepdim=True
        ).clamp_min(1.0)
        positive_logit = (positive_weights * similarities).sum(dim=1)
        normalizer = torch.logsumexp(
            similarities.masked_fill(diagonal, float("-inf")), dim=1
        )
        return (normalizer - positive_logit).mean()

    def loss_components(
        self,
        embedding_views: Tensor,
        labels: Tensor,
        update: bool | None = None,
    ) -> Dict[str, Tensor]:
        if update is None:
            update = self.training
        features, repeated_labels = self._flatten_views(embedding_views, labels)
        if features.shape[1] != self.embedding_dim:
            raise ValueError("PALM feature dimension differs from its prototype bank")

        assignments = self.soft_assignments(features)
        selected_mask = self.class_assignment_mask(
            assignments, repeated_labels
        )
        update_weights = self.class_assignment_weights(
            assignments, repeated_labels, selected_mask
        )
        current_prototypes = self._updated_prototypes(features, update_weights)
        if update:
            with torch.no_grad():
                self.prototypes.copy_(current_prototypes.detach())
                self.update_count.add_(1)
        else:
            current_prototypes = self.prototypes.detach()

        mle = self._mle_loss(
            features,
            repeated_labels,
            current_prototypes,
            selected_mask,
        )
        prototype_contrast = self._prototype_contrastive_loss(current_prototypes)
        total = mle + self.prototype_contrast_weight * prototype_contrast
        return {
            "total": total,
            "mle": mle,
            "prototype_contrast": prototype_contrast,
        }

    def forward(
        self,
        embedding_views: Tensor,
        labels: Tensor,
        update: bool | None = None,
    ) -> Tensor:
        components = self.loss_components(embedding_views, labels, update)
        self.last_components = {
            name: float(value.detach().cpu()) for name, value in components.items()
        }
        return components["total"]

    def evidence(self) -> dict[str, object]:
        return {
            "method": "PALM",
            "paper": PALM_PAPER,
            "official_code": PALM_OFFICIAL_CODE,
            "fit_split": "known_only_train",
            "distribution": "class_conditional_mixture_of_von_mises_fisher_directions",
            "prototype_state": "unit_normalized_non_gradient_ema",
            "prototypes_per_class": self.prototypes_per_class,
            "assignment": (
                "balanced_sinkhorn_then_label_masked_top_k_frozen_across_ema"
            ),
            "assignment_top_k": self.assignment_top_k,
            "prototype_momentum": self.prototype_momentum,
            "temperature": self.temperature,
            "assignment_epsilon": self.assignment_epsilon,
            "sinkhorn_iterations": self.sinkhorn_iterations,
            "prototype_contrast_weight": self.prototype_contrast_weight,
            "prototype_contrast_temperature": self.prototype_contrast_temperature,
            "hyperparameter_source": "fixed_official_defaults",
            "unknown_or_test_labels_used": False,
        }


class PALMClassifier(nn.Module):
    """Known-only tabular adaptation of PALM's representation learner.

    The image ResNet is replaced by the shared CAEOS concatenated-view MLP.
    PALM's projection head, unit-sphere embeddings, mixture prototypes,
    balanced assignment, EMA update, MLE and prototype-contrastive objectives
    are retained. Two image crops are replaced by stochastic encoder passes
    over the same standardized tabular row during training.
    """

    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
        training_views: int = 2,
        prototypes_per_class: int = 6,
        assignment_top_k: int = 5,
        prototype_momentum: float = 0.999,
        temperature: float = 0.1,
        assignment_epsilon: float = 0.05,
        sinkhorn_iterations: int = 3,
        prototype_contrast_weight: float = 1.0,
    ) -> None:
        super().__init__()
        if not input_dims or min(int(value) for value in input_dims) < 1:
            raise ValueError("PALM input dimensions must be positive")
        if training_views < 1:
            raise ValueError("PALM training view count must be positive")
        self.input_dims = tuple(int(value) for value in input_dims)
        self.num_classes = int(num_classes)
        self.training_views = int(training_views)
        self.encoder = ViewEncoder(
            sum(self.input_dims), hidden_dim, embedding_dim, dropout
        )
        self.projection = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim),
        )
        self.objective = PALMObjective(
            num_classes=num_classes,
            embedding_dim=embedding_dim,
            prototypes_per_class=prototypes_per_class,
            assignment_top_k=assignment_top_k,
            prototype_momentum=prototype_momentum,
            temperature=temperature,
            assignment_epsilon=assignment_epsilon,
            sinkhorn_iterations=sinkhorn_iterations,
            prototype_contrast_weight=prototype_contrast_weight,
        )

    def _encode(self, features: Tensor) -> Tensor:
        return F.normalize(self.projection(self.encoder(features)), dim=1)

    def class_logits(self, embedding: Tensor) -> Tensor:
        similarity = embedding @ self.objective.prototypes.t()
        similarity = similarity.reshape(
            len(embedding), self.num_classes, self.objective.prototypes_per_class
        )
        return torch.logsumexp(
            similarity / self.objective.temperature, dim=2
        ) - math.log(self.objective.prototypes_per_class)

    def forward(
        self, views: Sequence[Tensor], quality: Tensor | None = None
    ) -> Dict[str, Tensor]:
        del quality
        if len(views) != len(self.input_dims):
            raise ValueError("PALM received a different number of CAEOS input views")
        features = torch.cat(tuple(views), dim=1)
        first = self._encode(features)
        embedding_views = [first]
        if self.training:
            embedding_views.extend(
                self._encode(features) for _ in range(1, self.training_views)
            )
        return {
            "logits": self.class_logits(first),
            "embedding": first,
            "palm_views": torch.stack(embedding_views, dim=1),
        }

    def loss(self, output: Dict[str, Tensor], labels: Tensor) -> Tensor:
        return self.objective(output["palm_views"], labels)

    def evidence(self) -> dict[str, object]:
        evidence = self.objective.evidence()
        evidence.update(
            {
                "training_views": self.training_views,
                "adaptations": [
                    "image_resnet_replaced_by_shared_concat_view_tabular_mlp",
                    "image_crops_replaced_by_stochastic_encoder_passes",
                    "class_prediction_uses_vmf_mixture_log_likelihood",
                ],
            }
        )
        return evidence


class PALMSSDMahalanobis:
    """PALM repository's known-only SSD+ evaluation score.

    By default ``official_centering=True`` retains the public PALM evaluator's
    exact post-standardization centering. The alternate setting centers at the
    standardized training mean and is exposed only as an audited correction,
    not as the strict baseline default.
    """

    def __init__(self, epsilon: float = 1e-10, official_centering: bool = True):
        if epsilon <= 0.0:
            raise ValueError("PALM SSD+ epsilon must be positive")
        self.epsilon = float(epsilon)
        self.official_centering = bool(official_centering)
        self.normalized_mean: np.ndarray | None = None
        self.normalized_std: np.ndarray | None = None
        self.score_center: np.ndarray | None = None
        self.precision: np.ndarray | None = None
        self.train_count: int | None = None

    @staticmethod
    def _normalize(values: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(values, axis=1, keepdims=True)
        return values / (norm + 1e-10)

    def fit(self, train_embeddings: np.ndarray) -> None:
        values = np.asarray(train_embeddings, dtype=np.float64)
        if values.ndim != 2 or not len(values):
            raise ValueError("PALM SSD+ train embeddings must be a non-empty matrix")
        if not np.isfinite(values).all():
            raise ValueError("PALM SSD+ train embeddings must be finite")
        normalized = self._normalize(values)
        self.normalized_mean = normalized.mean(axis=0)
        self.normalized_std = normalized.std(axis=0)
        standardized = (normalized - self.normalized_mean) / (
            self.normalized_std + self.epsilon
        )
        covariance = np.atleast_2d(np.cov(standardized.T, bias=True))
        self.precision = np.linalg.pinv(covariance)
        self.score_center = (
            self.normalized_mean.copy()
            if self.official_centering
            else standardized.mean(axis=0)
        )
        self.train_count = int(len(values))

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if (
            self.normalized_mean is None
            or self.normalized_std is None
            or self.score_center is None
            or self.precision is None
        ):
            raise RuntimeError("PALM SSD+ calibrator has not been fitted")
        values = np.asarray(embeddings, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != len(self.normalized_mean):
            raise ValueError("PALM SSD+ embedding shape differs from the fitted data")
        normalized = self._normalize(values)
        standardized = (normalized - self.normalized_mean) / (
            self.normalized_std + self.epsilon
        )
        delta = standardized - self.score_center
        risk = np.einsum("nd,de,ne->n", delta, self.precision, delta)
        return np.maximum(risk, 0.0)

    def evidence(self) -> dict[str, object]:
        if self.precision is None:
            raise RuntimeError("PALM SSD+ calibrator has not been fitted")
        return {
            "method": "PALM_SSD_plus",
            "paper": PALM_PAPER,
            "official_code": PALM_OFFICIAL_CODE,
            "fit_split": "known_only_train",
            "score_orientation": "higher_is_more_unknown",
            "normalization": "l2_then_training_mean_std",
            "covariance": "population_covariance_pseudoinverse",
            "official_centering": self.official_centering,
            "train_embedding_count": self.train_count,
            "unknown_or_test_labels_used": False,
        }

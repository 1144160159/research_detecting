from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.neighbors import NearestNeighbors


PAPER_URL = "https://openreview.net/forum?id=2V7itvvMVJ"
OFFICIAL_CODE_URL = (
    "https://github.com/mostafaelaraby/Gradient-Aware-OOD-Detection"
)
OFFICIAL_CODE_COMMIT = "8a5ecdfdad178b6793132bec5d23cfad224fba11"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("GROOD %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("GROOD %s must be finite" % name)
    return array


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - values.max(axis=1, keepdims=True)
    numerator = np.exp(shifted)
    return numerator / numerator.sum(axis=1, keepdims=True)


def grood_gradients(
    embeddings: np.ndarray,
    class_prototypes: np.ndarray,
    ood_prototype: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    features = _matrix(embeddings, "embeddings")
    prototypes = _matrix(class_prototypes, "class prototypes")
    noise = np.asarray(ood_prototype, dtype=np.float64).reshape(-1)
    if prototypes.shape[1] != features.shape[1] or noise.shape != (features.shape[1],):
        raise ValueError("GROOD prototype dimensions must match embeddings")
    if not np.isfinite(noise).all():
        raise ValueError("GROOD OOD prototype must be finite")

    all_prototypes = np.vstack([prototypes, noise[None, :]])
    distances = np.linalg.norm(
        features[:, None, :] - all_prototypes[None, :, :], axis=2
    )
    ncc_scores = -distances
    probability_ood = _softmax(ncc_scores)[:, -1]
    vectors = features - noise[None, :]
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    unit_vectors = vectors / np.maximum(norms, 1e-12)
    gradients = probability_ood[:, None] * unit_vectors
    ncc_prediction = ncc_scores[:, :-1].argmax(axis=1).astype(np.int64, copy=False)
    return gradients, ncc_prediction


class GROODCalibrator:
    """Known-only tabular adaptation of official gradient-space GROOD."""

    def __init__(
        self,
        synthetic_count: int = 100,
        mixup_lambda: float = 0.5,
        synthetic_seed: int = 0,
    ) -> None:
        self.synthetic_count = int(synthetic_count)
        self.mixup_lambda = float(mixup_lambda)
        self.synthetic_seed = int(synthetic_seed)
        if self.synthetic_count <= 0:
            raise ValueError("GROOD synthetic count must be positive")
        if not 0.0 < self.mixup_lambda < 1.0:
            raise ValueError("GROOD mixup lambda must be in (0, 1)")
        self.class_prototypes: np.ndarray | None = None
        self.ood_prototype: np.ndarray | None = None
        self.index: NearestNeighbors | None = None
        self.training_count: int | None = None
        self.correct_training_count: int | None = None
        self.synthetic_indices: np.ndarray | None = None

    def fit(
        self,
        training_embeddings: np.ndarray,
        training_logits: np.ndarray,
        training_labels: np.ndarray,
    ) -> None:
        features = _matrix(training_embeddings, "training embeddings")
        logits = _matrix(training_logits, "training logits")
        labels = np.asarray(training_labels, dtype=np.int64).reshape(-1)
        if len(logits) != len(features) or len(labels) != len(features):
            raise ValueError("GROOD training arrays must be aligned")
        class_count = logits.shape[1]
        if class_count < 2 or labels.min() < 0 or labels.max() >= class_count:
            raise ValueError("GROOD training labels are outside the known classes")

        prototypes = []
        for class_index in range(class_count):
            selected = features[labels == class_index]
            if not len(selected):
                raise ValueError("GROOD requires every known class in training")
            prototypes.append(selected.mean(axis=0))
        self.class_prototypes = np.stack(prototypes)

        predictions = logits.argmax(axis=1)
        correct = predictions == labels
        if not correct.any():
            raise ValueError("GROOD has no correctly classified training samples")
        correct_indices = np.flatnonzero(correct)
        count = min(self.synthetic_count, len(correct_indices))
        rng = np.random.RandomState(self.synthetic_seed)
        chosen = np.sort(rng.choice(correct_indices, size=count, replace=False))
        second_class = np.argsort(logits[chosen], axis=1)[:, -2]
        synthetic = (
            self.mixup_lambda * features[chosen]
            + (1.0 - self.mixup_lambda) * self.class_prototypes[second_class]
        )
        self.ood_prototype = synthetic.mean(axis=0)

        gradients, _ = grood_gradients(
            features[correct], self.class_prototypes, self.ood_prototype
        )
        self.index = NearestNeighbors(n_neighbors=1, algorithm="brute", metric="euclidean")
        self.index.fit(gradients)
        self.training_count = int(len(features))
        self.correct_training_count = int(correct.sum())
        self.synthetic_indices = chosen.astype(np.int64, copy=False)

    def _require_fit(self) -> tuple[np.ndarray, np.ndarray, NearestNeighbors]:
        if self.class_prototypes is None or self.ood_prototype is None or self.index is None:
            raise RuntimeError("GROOD calibrator has not been fitted")
        return self.class_prototypes, self.ood_prototype, self.index

    def evaluate(self, embeddings: np.ndarray) -> dict[str, np.ndarray]:
        prototypes, noise, index = self._require_fit()
        gradients, prediction = grood_gradients(embeddings, prototypes, noise)
        distances = index.kneighbors(gradients, return_distance=True)[0][:, 0]
        if not np.isfinite(distances).all():
            raise FloatingPointError("GROOD produced non-finite distances")
        return {
            "prediction": prediction,
            "risk": distances,
            "gradient_norm": np.linalg.norm(gradients, axis=1),
            "nearest_gradient_distance": distances,
        }

    def evidence(self) -> dict[str, Any]:
        prototypes, noise, _ = self._require_fit()
        if (
            self.training_count is None
            or self.correct_training_count is None
            or self.synthetic_indices is None
        ):
            raise RuntimeError("GROOD fit evidence is incomplete")
        return {
            "method": "GROOD",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "protocol_class": "known_only_tabular_penultimate_feature_adapter",
            "class_prototype_fit_split": "known_training_only",
            "gradient_index_fit_split": "correctly_classified_known_training_only",
            "training_count": self.training_count,
            "correct_training_count": self.correct_training_count,
            "synthetic_ood_source": "known_training_embedding_and_second_logit_class_prototype",
            "synthetic_count_requested": self.synthetic_count,
            "synthetic_count_used": int(len(self.synthetic_indices)),
            "synthetic_seed": self.synthetic_seed,
            "mixup_lambda": self.mixup_lambda,
            "class_count": int(len(prototypes)),
            "embedding_dimension": int(prototypes.shape[1]),
            "ood_prototype_norm": float(np.linalg.norm(noise)),
            "score": "euclidean_1nn_distance_in_ood_prototype_gradient_space",
            "prediction": "nearest_known_class_prototype",
            "risk_orientation": "larger_gradient_distance_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "adaptation": {
                "image_intermediate_mixup_replaced_by_penultimate_tabular_mixup": True,
                "reason": "frozen tabular MLP exposes a stable penultimate embedding",
                "official_validation_ood_disabled": True,
            },
        }

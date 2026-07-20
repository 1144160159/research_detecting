from __future__ import annotations

import numpy as np


PAPER_URL = "https://proceedings.iclr.cc/paper_files/paper/2024/hash/2b1a955952bc98518a331ad6d8cc524d-Abstract-Conference.html"
OFFICIAL_CODE_URL = "https://github.com/BierOne/ood_coverage"
OFFICIAL_CODE_COMMIT = "16933b0b17fe451cdcd60f77d95d8746e57da4cc"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("NAC %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("NAC %s must be finite" % name)
    return array


def _labels(values: np.ndarray, count: int) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64)
    if array.ndim != 1 or len(array) != count:
        raise ValueError("NAC labels must match the training matrix")
    return array


def official_thresholds(bucket_count: int) -> np.ndarray:
    half = int(bucket_count / 2)
    if bucket_count < 4 or half < 2:
        raise ValueError("NAC bucket count is too small")
    x = np.linspace(1.0, np.sqrt(1e3), num=half)
    x_left = np.emath.logn(1e3, x).real
    x_right = (1.0 - x_left)[::-1]
    thresholds = np.concatenate([x_left[:-1], x_right])
    thresholds[-1] += 1e-2
    return np.append(thresholds, 1.2).astype(np.float64)


class NACUEFixedCalibrator:
    """NAC-UE with the official CIFAR-10 avgpool defaults frozen a priori."""

    def __init__(
        self,
        valid_num: int = 1000,
        bucket_count: int = 50,
        minimum_bin_count: int = 50,
        sigmoid_alpha: float = 100.0,
        subset_seed: int = 1,
    ) -> None:
        self.valid_num = int(valid_num)
        self.bucket_count = int(bucket_count)
        self.minimum_bin_count = int(minimum_bin_count)
        self.sigmoid_alpha = float(sigmoid_alpha)
        self.subset_seed = int(subset_seed)
        if self.valid_num <= 0 or self.minimum_bin_count <= 0 or self.sigmoid_alpha <= 0.0:
            raise ValueError("NAC fixed hyperparameters must be positive")
        self.thresholds = official_thresholds(self.bucket_count)
        self.coverage: np.ndarray | None = None
        self.weights: np.ndarray | None = None
        self.class_count: int | None = None
        self.training_count: int | None = None
        self.subset_count: int | None = None
        self.subset_per_class: int | None = None
        self.coverage_nonzero_fraction: float | None = None
        self.coverage_mean: float | None = None

    def activation_state(
        self, features: np.ndarray, logits: np.ndarray, classifier_weights: np.ndarray | None = None
    ) -> np.ndarray:
        values = _matrix(features, "features")
        scores = _matrix(logits, "logits")
        weights = self.weights if classifier_weights is None else _matrix(classifier_weights, "classifier weights")
        if weights is None:
            raise RuntimeError("NAC calibrator has not been fitted")
        if len(values) != len(scores) or values.shape[1] != weights.shape[1] or scores.shape[1] != weights.shape[0]:
            raise ValueError("NAC feature, logit and classifier dimensions differ")
        shifted = scores - scores.max(axis=1, keepdims=True)
        probabilities = np.exp(shifted)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        uniform = 1.0 / scores.shape[1]
        kl_gradient = (probabilities - uniform) @ weights
        argument = np.clip(self.sigmoid_alpha * values * kl_gradient, -700.0, 700.0)
        return 1.0 / (1.0 + np.exp(-argument))

    def _balanced_subset(self, labels: np.ndarray) -> np.ndarray:
        classes = np.unique(labels)
        if not len(classes) or not np.array_equal(classes, np.arange(len(classes))):
            raise ValueError("NAC training labels must be contiguous from zero")
        class_indices = [np.flatnonzero(labels == class_index) for class_index in classes]
        minimum = min(len(indices) for indices in class_indices)
        per_class = min(int(self.valid_num / len(classes)), minimum)
        if per_class <= 0:
            raise ValueError("NAC balanced training subset is empty")
        selected = []
        for indices in class_indices:
            indices = indices.copy()
            np.random.RandomState(self.subset_seed).shuffle(indices)
            selected.extend(indices[:per_class].tolist())
        self.subset_per_class = int(per_class)
        return np.asarray(selected, dtype=np.int64)

    def _bin_indices(self, states: np.ndarray) -> np.ndarray:
        indices = np.searchsorted(self.thresholds, states, side="right") - 1
        return np.clip(indices, 0, self.bucket_count - 2)

    def fit(
        self,
        training_features: np.ndarray,
        training_logits: np.ndarray,
        training_labels: np.ndarray,
        classifier_weights: np.ndarray,
    ) -> None:
        features = _matrix(training_features, "training features")
        logits = _matrix(training_logits, "training logits")
        labels = _labels(training_labels, len(features))
        weights = _matrix(classifier_weights, "classifier weights")
        if len(logits) != len(features) or features.shape[1] != weights.shape[1] or logits.shape[1] != weights.shape[0]:
            raise ValueError("NAC training dimensions differ")
        self.weights = weights.copy()
        self.class_count = int(weights.shape[0])
        subset = self._balanced_subset(labels)
        states = self.activation_state(features[subset], logits[subset])
        bins = self._bin_indices(states)
        counts = np.zeros((self.bucket_count - 1, features.shape[1]), dtype=np.float64)
        for neuron in range(features.shape[1]):
            counts[:, neuron] = np.bincount(bins[:, neuron], minlength=self.bucket_count - 1)
        self.coverage = np.minimum(counts / self.minimum_bin_count, 1.0)
        self.training_count = int(len(features))
        self.subset_count = int(len(subset))
        self.coverage_nonzero_fraction = float(np.mean(self.coverage > 0.0))
        self.coverage_mean = float(self.coverage.mean())

    def evaluate(self, features: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        values = _matrix(features, "inference features")
        scores = _matrix(logits, "inference logits")
        if self.coverage is None or self.weights is None:
            raise RuntimeError("NAC calibrator has not been fitted")
        states = self.activation_state(values, scores)
        bins = self._bin_indices(states)
        neuron_indices = np.arange(values.shape[1])[None, :]
        confidence = self.coverage[bins, neuron_indices].mean(axis=1)
        return {
            "prediction": scores.argmax(axis=1).astype(np.int64, copy=False),
            "risk": -confidence,
            "confidence": confidence,
            "activation_state": states,
        }

    def evidence(self) -> dict[str, object]:
        if self.coverage is None or self.subset_count is None or self.training_count is None:
            raise RuntimeError("NAC fit evidence is incomplete")
        return {
            "method": "NAC-UE-Fixed",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "mean known-training bin coverage of sigmoid(neuron_output * uniform-KL gradient)",
            "layer_adapter": "frozen MLP final embedding corresponds to official pre-classifier avgpool layer",
            "gradient_adapter": "analytic W^T(softmax-uniform), verified against autograd",
            "fit_split": "class-balanced known_training_features_only",
            "training_embedding_count": self.training_count,
            "coverage_subset_count": self.subset_count,
            "coverage_subset_per_class": self.subset_per_class,
            "class_count": self.class_count,
            "embedding_dimension": int(self.coverage.shape[1]),
            "fixed_official_source": "official CIFAR-10 ResNet avgpool defaults",
            "valid_num": self.valid_num,
            "bucket_count_M": self.bucket_count,
            "minimum_bin_count_O": self.minimum_bin_count,
            "sigmoid_alpha": self.sigmoid_alpha,
            "subset_seed": self.subset_seed,
            "state_method": "sigmoid(o*g_kl)",
            "test_method": "avg",
            "official_ood_validation_sweep_reused": False,
            "coverage_nonzero_fraction": self.coverage_nonzero_fraction,
            "coverage_mean": self.coverage_mean,
            "prediction_source": "unmodified_frozen_classifier",
            "risk_orientation": "negative_nac_coverage_larger_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
        }

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

import numpy as np
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    roc_auc_score,
)

from .hybrid import _normalize_probability, normalized_entropy
from .metrics import fpr_at_95_tpr, open_set_classification_rate


def jensen_shannon_divergence(
    left: np.ndarray, right: np.ndarray
) -> np.ndarray:
    left = _normalize_probability(left)
    right = _normalize_probability(right)
    mixture = 0.5 * (left + right)
    return 0.5 * (
        (left * np.log(left / mixture)).sum(axis=1)
        + (right * np.log(right / mixture)).sum(axis=1)
    ) / np.log(2.0)


class ClassConditionalDiagonalDistance:
    def __init__(self, variance_floor: float = 0.1):
        self.variance_floor = float(variance_floor)
        self.means: np.ndarray | None = None
        self.variances: np.ndarray | None = None

    def fit(self, values: np.ndarray, labels: np.ndarray) -> None:
        labels = np.asarray(labels, dtype=np.int64)
        classes = np.arange(int(labels.max()) + 1)
        means = []
        variances = []
        for class_index in classes:
            selected = np.asarray(values)[labels == class_index]
            if len(selected) == 0:
                raise ValueError(f"class {class_index} has no samples")
            means.append(selected.mean(axis=0))
            variances.append(selected.var(axis=0) + self.variance_floor)
        self.means = np.asarray(means, dtype=np.float64)
        self.variances = np.asarray(variances, dtype=np.float64)

    def score(self, values: np.ndarray) -> np.ndarray:
        if self.means is None or self.variances is None:
            raise RuntimeError("distance model has not been fitted")
        values = np.asarray(values, dtype=np.float64)
        scores = []
        for mean, variance in zip(self.means, self.variances):
            squared = np.square(values - mean) / variance
            scores.append(np.sqrt(squared.mean(axis=1)))
        return np.stack(scores, axis=1).min(axis=1)


class KnownKnnDistance:
    """Measure local support by distance to the k-th nearest known sample."""

    def __init__(self, neighbors: int = 10):
        self.neighbors = int(neighbors)
        self.model: NearestNeighbors | None = None

    def fit(self, values: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        if len(values) == 0:
            raise ValueError("KNN support requires at least one known sample")
        count = min(self.neighbors, len(values))
        self.model = NearestNeighbors(n_neighbors=count, metric="euclidean")
        self.model.fit(values)

    def score(self, values: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("KNN support model has not been fitted")
        distances, _ = self.model.kneighbors(np.asarray(values, dtype=np.float64))
        return distances[:, -1]


class PredictedClassKnnDistance:
    """Measure support inside the known class claimed by the classifier."""

    def __init__(self, neighbors: int = 10):
        self.neighbors = int(neighbors)
        self.models: dict[int, NearestNeighbors] = {}

    def fit(self, values: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        self.models = {}
        for class_index in np.unique(labels):
            selected = values[labels == class_index]
            count = min(self.neighbors, len(selected))
            model = NearestNeighbors(n_neighbors=count, metric="euclidean")
            model.fit(selected)
            self.models[int(class_index)] = model

    def score(
        self, values: np.ndarray, predicted_labels: np.ndarray
    ) -> np.ndarray:
        if not self.models:
            raise RuntimeError("class-conditional KNN model has not been fitted")
        values = np.asarray(values, dtype=np.float64)
        predicted_labels = np.asarray(predicted_labels, dtype=np.int64)
        result = np.empty(len(values), dtype=np.float64)
        for class_index in np.unique(predicted_labels):
            if int(class_index) not in self.models:
                raise ValueError(f"unknown predicted class {class_index}")
            selected = predicted_labels == class_index
            distances, _ = self.models[int(class_index)].kneighbors(values[selected])
            result[selected] = distances[:, -1]
        return result


class KnownLocalOutlierFactor:
    """Estimate class-independent local density deviation in novelty mode."""

    def __init__(self, neighbors: int = 20, jobs: int = -1):
        self.neighbors = int(neighbors)
        self.jobs = int(jobs)
        self.model: LocalOutlierFactor | None = None

    def fit(self, values: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        if len(values) < 2:
            raise ValueError("LOF support requires at least two known samples")
        count = min(self.neighbors, len(values) - 1)
        self.model = LocalOutlierFactor(
            n_neighbors=count,
            novelty=True,
            contamination="auto",
            n_jobs=self.jobs,
        )
        self.model.fit(values)

    def score(self, values: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LOF support model has not been fitted")
        return -self.model.score_samples(np.asarray(values, dtype=np.float64))


class ForestLeafRarity:
    """Score samples by the training support of reached ensemble leaves."""

    def __init__(self):
        self.estimators: list[object] = []
        self.leaf_counts: list[dict[int, int]] = []
        self.training_size = 0

    def fit(self, forests: list[object], values: np.ndarray) -> None:
        values = np.asarray(values)
        self.estimators = [
            estimator for forest in forests for estimator in forest.estimators_
        ]
        self.training_size = len(values)
        self.leaf_counts = []
        for estimator in self.estimators:
            leaves, counts = np.unique(estimator.apply(values), return_counts=True)
            self.leaf_counts.append(
                {int(leaf): int(count) for leaf, count in zip(leaves, counts)}
            )

    def score(self, values: np.ndarray) -> np.ndarray:
        if not self.estimators:
            raise RuntimeError("leaf rarity model has not been fitted")
        values = np.asarray(values)
        rarity = np.zeros(len(values), dtype=np.float64)
        for estimator, counts in zip(self.estimators, self.leaf_counts):
            leaves = estimator.apply(values)
            support = np.asarray([counts.get(int(leaf), 0) for leaf in leaves])
            rarity += np.log((self.training_size + len(counts)) / (support + 1.0))
        return rarity / len(self.estimators)


class KnownQuantileNormalizer:
    def __init__(self):
        self.bounds: Dict[str, tuple[float, float]] = {}

    def fit(self, components: Mapping[str, np.ndarray]) -> None:
        self.bounds = {}
        for name, values in components.items():
            low, high = np.quantile(np.asarray(values), [0.05, 0.95])
            if high - low < 1e-8:
                high = low + 1e-8
            self.bounds[name] = (float(low), float(high))

    def transform(self, components: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self.bounds:
            raise RuntimeError("normalizer has not been fitted")
        result = {}
        for name, values in components.items():
            low, high = self.bounds[name]
            result[name] = np.clip((np.asarray(values) - low) / (high - low), 0.0, 2.0)
        return result


class EmpiricalTailCalibrator:
    """Map diagnostics to known-only upper-tail anomaly scores."""

    def __init__(self):
        self.reference: Dict[str, np.ndarray] = {}

    def fit(self, components: Mapping[str, np.ndarray]) -> None:
        self.reference = {
            name: np.sort(np.asarray(values, dtype=np.float64))
            for name, values in components.items()
        }

    def transform(self, components: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self.reference:
            raise RuntimeError("tail calibrator has not been fitted")
        result = {}
        for name, values in components.items():
            reference = self.reference[name]
            insertion = np.searchsorted(reference, np.asarray(values), side="left")
            upper_count = len(reference) - insertion
            p_value = (upper_count + 1.0) / (len(reference) + 1.0)
            result[name] = 1.0 - p_value
        return result


class ClassConditionalEmpiricalTailCalibrator:
    """Empirical upper tails conditioned on the classifier's claimed class."""

    def __init__(self):
        self.reference: Dict[str, dict[int, np.ndarray]] = {}
        self.global_reference: Dict[str, np.ndarray] = {}

    def fit(
        self,
        components: Mapping[str, np.ndarray],
        predicted_labels: np.ndarray,
    ) -> None:
        predicted_labels = np.asarray(predicted_labels, dtype=np.int64)
        self.reference = {}
        self.global_reference = {}
        for name, values in components.items():
            values = np.asarray(values, dtype=np.float64)
            self.global_reference[name] = np.sort(values)
            self.reference[name] = {
                int(class_index): np.sort(values[predicted_labels == class_index])
                for class_index in np.unique(predicted_labels)
            }

    def transform(
        self,
        components: Mapping[str, np.ndarray],
        predicted_labels: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        if not self.reference:
            raise RuntimeError("class-conditional tail calibrator has not been fitted")
        predicted_labels = np.asarray(predicted_labels, dtype=np.int64)
        result = {}
        for name, values in components.items():
            values = np.asarray(values, dtype=np.float64)
            scores = np.empty(len(values), dtype=np.float64)
            for class_index in np.unique(predicted_labels):
                selected = predicted_labels == class_index
                reference = self.reference[name].get(
                    int(class_index), self.global_reference[name]
                )
                insertion = np.searchsorted(
                    reference, values[selected], side="left"
                )
                upper_count = len(reference) - insertion
                p_value = (upper_count + 1.0) / (len(reference) + 1.0)
                scores[selected] = 1.0 - p_value
            result[name] = scores
        return result


class EmpiricalTwoSidedCalibrator:
    """Map diagnostics to known-only two-sided empirical anomaly scores."""

    def __init__(self):
        self.reference: Dict[str, np.ndarray] = {}

    def fit(self, components: Mapping[str, np.ndarray]) -> None:
        self.reference = {
            name: np.sort(np.asarray(values, dtype=np.float64))
            for name, values in components.items()
        }

    def transform(self, components: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self.reference:
            raise RuntimeError("two-sided calibrator has not been fitted")
        result = {}
        for name, values in components.items():
            reference = self.reference[name]
            values = np.asarray(values)
            lower_count = np.searchsorted(reference, values, side="right")
            upper_count = len(reference) - np.searchsorted(
                reference, values, side="left"
            )
            lower_p = (lower_count + 1.0) / (len(reference) + 1.0)
            upper_p = (upper_count + 1.0) / (len(reference) + 1.0)
            two_sided_p = np.minimum(1.0, 2.0 * np.minimum(lower_p, upper_p))
            result[name] = 1.0 - two_sided_p
        return result


def cauchy_combined_risk(
    tail_risk: Mapping[str, np.ndarray], names: tuple[str, ...]
) -> np.ndarray:
    p_values = np.stack(
        [np.clip(1.0 - np.asarray(tail_risk[name]), 1e-6, 1.0 - 1e-6) for name in names],
        axis=1,
    )
    statistic = np.tan((0.5 - p_values) * np.pi).mean(axis=1)
    combined_p = 0.5 - np.arctan(statistic) / np.pi
    return np.clip(1.0 - combined_p, 0.0, 1.0)


def bonferroni_union_risk(
    tail_risk: Mapping[str, np.ndarray], names: tuple[str, ...]
) -> np.ndarray:
    """Combine calibrated anomaly p-values while controlling a union test."""
    p_values = np.stack(
        [np.clip(1.0 - np.asarray(tail_risk[name]), 1e-12, 1.0) for name in names],
        axis=1,
    )
    adjusted_p = np.minimum(1.0, len(names) * p_values.min(axis=1))
    return 1.0 - adjusted_p


def hybrid_open_set_components(
    model,
    views,
    distance_model: ClassConditionalDiagonalDistance,
    distance_values: np.ndarray | None = None,
) -> tuple[Dict[str, np.ndarray], np.ndarray]:
    global_values = model._global_values(views)
    support_values = (
        global_values
        if distance_values is None
        else np.asarray(distance_values, dtype=np.float64)
    )
    evidence = model.predict_with_evidence(views)
    probability = evidence["final_probability"]
    sorted_probability = np.sort(probability, axis=1)
    rf_probability = model.random_forest.predict_proba(global_values)
    et_probability = model.extra_trees.predict_proba(global_values)
    components = {
        "uncertainty": normalized_entropy(probability),
        "inverse_belief": 1.0 - probability.max(axis=1),
        "inverse_margin": 1.0 - (sorted_probability[:, -1] - sorted_probability[:, -2]),
        "conflict": np.asarray(evidence["global_conflict"], dtype=np.float64),
        "tree_disagreement": jensen_shannon_divergence(rf_probability, et_probability),
        "distance": distance_model.score(support_values),
    }
    return components, probability


RISK_WEIGHTS = {
    "msp": {"inverse_belief": 1.0},
    "entropy": {"uncertainty": 1.0},
    "distance": {"distance": 1.0},
    "conflict": {"conflict": 1.0},
    "tree_disagreement": {"tree_disagreement": 1.0},
    "knn_distance": {"knn_distance": 1.0},
    "class_knn_distance": {"class_knn_distance": 1.0},
    "lof_density": {"lof_density": 1.0},
    "support_distance": {"distance": 0.5, "knn_distance": 0.5},
    "baseline": {"uncertainty": 0.5, "distance": 0.5},
    "conflict_augmented": {"uncertainty": 0.4, "distance": 0.4, "conflict": 0.2},
    "disagreement_augmented": {
        "uncertainty": 0.35,
        "distance": 0.35,
        "conflict": 0.15,
        "tree_disagreement": 0.15,
    },
}


def weighted_risk(
    components: Mapping[str, np.ndarray], weights: Mapping[str, float]
) -> np.ndarray:
    total = float(sum(weights.values()))
    if total <= 0:
        raise ValueError("risk weights must sum to a positive value")
    return sum(float(weight) * np.asarray(components[name]) for name, weight in weights.items()) / total


def evaluate_hybrid_open_set(
    labels: np.ndarray,
    is_unknown: np.ndarray,
    known_prediction: np.ndarray,
    risk: np.ndarray,
    threshold: float,
) -> Dict[str, float]:
    labels = np.asarray(labels)
    is_unknown = np.asarray(is_unknown, dtype=bool)
    known = ~is_unknown
    target = is_unknown.astype(np.int64)
    rejected = risk >= threshold
    return {
        "known_accuracy": float((known_prediction[known] == labels[known]).mean()),
        "known_macro_f1": float(
            f1_score(labels[known], known_prediction[known], average="macro", zero_division=0)
        ),
        "unknown_auroc": float(roc_auc_score(target, risk)),
        "unknown_aupr": float(average_precision_score(target, risk)),
        "unknown_fpr95": fpr_at_95_tpr(target, risk),
        "unknown_f1": float(f1_score(target, rejected.astype(np.int64), zero_division=0)),
        "oscr": open_set_classification_rate(labels, known_prediction, is_unknown, risk),
        "known_acceptance_rate": float((~rejected[known]).mean()),
        "unknown_rejection_rate": float(rejected[is_unknown].mean()),
        "mean_known_risk": float(risk[known].mean()),
        "mean_unknown_risk": float(risk[is_unknown].mean()),
    }


@dataclass
class HybridOpenSetResult:
    validation_thresholds: Dict[str, float]
    reports: Dict[str, Dict[str, float]]
    component_auroc: Dict[str, float]

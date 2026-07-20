from __future__ import annotations

from typing import Any

import numpy as np


class ExCeLCalibrator:
    """Class-rank signature score from the TMLR 2025 ExCeL detector."""

    def __init__(self, reward: float = 10.0, high_probability: float = 5.0, alpha: float = 0.8):
        if reward <= 0.0 or high_probability <= 0.0:
            raise ValueError("reward and high_probability must be positive")
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be in [0, 1]")
        self.reward = float(reward)
        self.high_probability = float(high_probability)
        self.alpha = float(alpha)
        self.smoothed_probability: np.ndarray | None = None
        self.correct_counts: np.ndarray | None = None

    @staticmethod
    def _logits(values: np.ndarray) -> np.ndarray:
        result = np.asarray(values, dtype=np.float64)
        if result.ndim != 2 or result.shape[1] < 2:
            raise ValueError("logits must be a two-dimensional array with at least two classes")
        if not np.isfinite(result).all():
            raise ValueError("logits contain non-finite values")
        return result

    def fit(self, logits: np.ndarray, labels: np.ndarray) -> "ExCeLCalibrator":
        values = self._logits(logits)
        targets = np.asarray(labels, dtype=np.int64)
        if targets.shape != (len(values),):
            raise ValueError("labels do not match logits")
        classes = values.shape[1]
        if targets.size == 0 or targets.min() < 0 or targets.max() >= classes:
            raise ValueError("labels are empty or outside the logit class range")

        rankings = np.argsort(-values, axis=1, kind="stable")
        correct = rankings[:, 0] == targets
        counts = np.zeros((classes, classes, classes), dtype=np.float64)
        correct_counts = np.zeros(classes, dtype=np.int64)
        ranks = np.arange(classes)
        for index in np.flatnonzero(correct):
            target = int(targets[index])
            counts[target, rankings[index], ranks] += 1.0
            correct_counts[target] += 1
        if np.any(correct_counts == 0):
            missing = np.flatnonzero(correct_counts == 0).tolist()
            raise ValueError(f"no correctly classified training samples for classes {missing}")

        probability = counts / correct_counts[:, None, None]
        random_probability = 1.0 / (classes - 1)
        high_threshold = self.high_probability * random_probability
        smoothed = np.empty_like(probability)
        smoothed[probability >= high_threshold] = self.reward * random_probability
        middle = (probability >= random_probability) & (probability < high_threshold)
        smoothed[middle] = random_probability
        low = (probability > 0.0) & (probability < random_probability)
        smoothed[low] = -random_probability
        smoothed[probability == 0.0] = -self.reward * random_probability
        self.smoothed_probability = smoothed
        self.correct_counts = correct_counts
        return self

    def id_score(self, logits: np.ndarray) -> np.ndarray:
        if self.smoothed_probability is None:
            raise RuntimeError("ExCeLCalibrator must be fitted before scoring")
        values = self._logits(logits)
        if values.shape[1] != self.smoothed_probability.shape[0]:
            raise ValueError("logit class count differs from fitted ExCeL matrices")
        rankings = np.argsort(-values, axis=1, kind="stable")
        predicted = rankings[:, 0]
        ranks = np.arange(values.shape[1])
        rank_score = self.smoothed_probability[predicted[:, None], rankings, ranks].sum(axis=1)
        max_logit = values.max(axis=1)
        return self.alpha * rank_score + (1.0 - self.alpha) * max_logit

    def score(self, logits: np.ndarray) -> np.ndarray:
        return -self.id_score(logits)

    def evidence(self) -> dict[str, Any]:
        if self.correct_counts is None:
            raise RuntimeError("ExCeLCalibrator has not been fitted")
        return {
            "method": "excel",
            "reward_a": self.reward,
            "high_probability_b": self.high_probability,
            "alpha": self.alpha,
            "correct_training_samples_per_class": self.correct_counts.tolist(),
            "fit_data": "correctly_classified_known_training_logits_only",
            "score_orientation": "higher_is_more_ood",
        }

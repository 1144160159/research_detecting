from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


METHODS = ("klnd1", "klnd2", "klnd3")


@dataclass(frozen=True)
class KLNDOutput:
    prediction: np.ndarray
    risks: dict[str, np.ndarray]
    native_reject: dict[str, np.ndarray]


class KLogitNeighborDistance:
    """Paper-faithful k-LND scores fitted on known train/validation logits."""

    def __init__(self, percentile: float = 0.9) -> None:
        if not 0.5 < percentile < 1.0:
            raise ValueError("percentile must be in (0.5, 1)")
        self.percentile = float(percentile)
        self.centers_: np.ndarray | None = None
        self.thresholds_: dict[str, np.ndarray] | None = None
        self.train_correct_counts_: list[int] | None = None
        self.validation_correct_counts_: list[int] | None = None

    @staticmethod
    def _validate(
        logits: np.ndarray,
        labels: np.ndarray,
        *,
        class_count: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(logits, dtype=np.float64)
        targets = np.asarray(labels, dtype=np.int64)
        if values.ndim != 2 or targets.ndim != 1 or len(values) != len(targets):
            raise ValueError("logits and labels have incompatible shapes")
        if len(values) == 0 or not np.isfinite(values).all():
            raise ValueError("logits must be nonempty and finite")
        expected = values.shape[1] if class_count is None else class_count
        if values.shape[1] != expected or expected < 2:
            raise ValueError("logit width must equal a class count of at least two")
        if targets.min(initial=0) < 0 or targets.max(initial=-1) >= expected:
            raise ValueError("labels are outside the logit class range")
        return values, targets

    @staticmethod
    def _risks(logits: np.ndarray, centers: np.ndarray) -> dict[str, np.ndarray]:
        prediction = logits.argmax(axis=1)
        distances = np.linalg.norm(logits[:, None, :] - centers[None, :, :], axis=2)
        own = distances[np.arange(len(logits)), prediction]
        other_mask = np.ones_like(distances, dtype=bool)
        other_mask[np.arange(len(logits)), prediction] = False
        other = distances[other_mask].reshape(len(logits), centers.shape[0] - 1)
        d2 = np.sum(other - own[:, None], axis=1)
        denominator = np.maximum(other.sum(axis=1), np.finfo(np.float64).tiny)
        return {
            "klnd1": own,
            "klnd2": -d2,
            "klnd3": own / denominator,
        }

    @staticmethod
    def _higher_quantile(values: np.ndarray, percentile: float) -> float:
        try:
            return float(np.quantile(values, percentile, method="higher"))
        except TypeError:
            return float(
                np.quantile(values, percentile, interpolation="higher")
            )

    def fit(
        self,
        train_logits: np.ndarray,
        train_labels: np.ndarray,
        validation_logits: np.ndarray,
        validation_labels: np.ndarray,
    ) -> "KLogitNeighborDistance":
        train_values, train_targets = self._validate(train_logits, train_labels)
        class_count = train_values.shape[1]
        validation_values, validation_targets = self._validate(
            validation_logits, validation_labels, class_count=class_count
        )
        if set(np.unique(train_targets)) != set(range(class_count)):
            raise ValueError("training labels must cover every known class")
        train_prediction = train_values.argmax(axis=1)
        validation_prediction = validation_values.argmax(axis=1)
        centers = []
        train_counts = []
        validation_counts = []
        for class_index in range(class_count):
            train_mask = (train_targets == class_index) & (
                train_prediction == class_index
            )
            validation_mask = (validation_targets == class_index) & (
                validation_prediction == class_index
            )
            train_count = int(train_mask.sum())
            validation_count = int(validation_mask.sum())
            if train_count == 0:
                raise ValueError(
                    "class %d has no correctly classified training samples"
                    % class_index
                )
            if validation_count == 0:
                raise ValueError(
                    "class %d has no correctly classified validation samples"
                    % class_index
                )
            centers.append(train_values[train_mask].mean(axis=0))
            train_counts.append(train_count)
            validation_counts.append(validation_count)
        centers_array = np.asarray(centers, dtype=np.float64)
        validation_risks = self._risks(validation_values, centers_array)
        thresholds: dict[str, np.ndarray] = {}
        correct = validation_prediction == validation_targets
        for method in METHODS:
            per_class = []
            for class_index in range(class_count):
                mask = correct & (validation_targets == class_index)
                per_class.append(
                    self._higher_quantile(
                        validation_risks[method][mask],
                        self.percentile,
                    )
                )
            thresholds[method] = np.asarray(per_class, dtype=np.float64)
        self.centers_ = centers_array
        self.thresholds_ = thresholds
        self.train_correct_counts_ = train_counts
        self.validation_correct_counts_ = validation_counts
        return self

    def evaluate(self, logits: np.ndarray) -> KLNDOutput:
        if self.centers_ is None or self.thresholds_ is None:
            raise ValueError("k-LND calibrator is not fitted")
        values, _ = self._validate(
            logits,
            np.zeros(len(logits), dtype=np.int64),
            class_count=self.centers_.shape[0],
        )
        prediction = values.argmax(axis=1)
        risks = self._risks(values, self.centers_)
        native_reject = {
            method: risk > self.thresholds_[method][prediction]
            for method, risk in risks.items()
        }
        return KLNDOutput(
            prediction=prediction,
            risks=risks,
            native_reject=native_reject,
        )

    def evidence(self) -> dict[str, Any]:
        if (
            self.centers_ is None
            or self.thresholds_ is None
            or self.train_correct_counts_ is None
            or self.validation_correct_counts_ is None
        ):
            raise ValueError("k-LND calibrator is not fitted")
        return {
            "percentile": self.percentile,
            "class_count": int(self.centers_.shape[0]),
            "neighbor_policy": "all_other_known_classes",
            "train_correct_counts": self.train_correct_counts_,
            "validation_correct_counts": self.validation_correct_counts_,
            "thresholds": {
                method: values.tolist()
                for method, values in self.thresholds_.items()
            },
            "risk_orientation": {
                "klnd1": "D1; higher is more unknown",
                "klnd2": "-D2; higher is more unknown",
                "klnd3": "D3; higher is more unknown",
            },
        }

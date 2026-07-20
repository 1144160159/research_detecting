from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


PAPER_URL = "https://openaccess.thecvf.com/content/CVPR2023/papers/Ahn_LINe_Out-of-Distribution_Detection_by_Leveraging_Important_Neurons_CVPR_2023_paper.pdf"
SUPPLEMENT_URL = "https://openaccess.thecvf.com/content/CVPR2023/supplemental/Ahn_LINe_Out-of-Distribution_Detection_CVPR_2023_supplemental.pdf"
OFFICIAL_CODE_URL = "https://github.com/YongHyun-Ahn/LINe-Out-of-Distribution-Detection-by-Leveraging-Important-Neurons"
OFFICIAL_CODE_COMMIT = "465ddf584d62c8e8bbf18c014aa48f1d3c1e7532"


def _matrix(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("LINe %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("LINe %s must be finite" % name)
    return array


def _logsumexp(logits: np.ndarray) -> np.ndarray:
    maximum = logits.max(axis=1)
    return maximum + np.log(np.exp(logits - maximum[:, None]).sum(axis=1))


def _nll(logits: np.ndarray, labels: np.ndarray) -> float:
    return float(np.mean(_logsumexp(logits) - logits[np.arange(len(labels)), labels]))


@dataclass(frozen=True)
class LINeParameters:
    weight_percentile: float
    activation_percentile: float
    clip_quantile: float
    clip_threshold: float


class LINeIDTuneCalibrator:
    """LINe equations with an ID-only, scale-portable parameter policy."""

    def __init__(
        self,
        pruning_candidates: Iterable[tuple[float, float]] = ((10.0, 10.0), (90.0, 90.0), (90.0, 10.0)),
        clip_quantiles: Iterable[float] = (0.90, 0.95, 0.99),
    ) -> None:
        self.pruning_candidates = tuple((float(pw), float(pa)) for pw, pa in pruning_candidates)
        self.clip_quantiles = tuple(float(value) for value in clip_quantiles)
        if not self.pruning_candidates:
            raise ValueError("LINe requires at least one pruning candidate")
        if any(not 0.0 <= value < 100.0 for pair in self.pruning_candidates for value in pair):
            raise ValueError("LINe pruning percentiles must be in [0, 100)")
        if not self.clip_quantiles or any(not 0.0 < value <= 1.0 for value in self.clip_quantiles):
            raise ValueError("LINe clip quantiles must be in (0, 1]")
        self.weights: np.ndarray | None = None
        self.bias: np.ndarray | None = None
        self.contribution: np.ndarray | None = None
        self.parameters: LINeParameters | None = None
        self.activation_mask: np.ndarray | None = None
        self.masked_weights: np.ndarray | None = None
        self.selection_table: list[dict[str, float]] | None = None
        self.class_counts: list[int] | None = None

    @staticmethod
    def _labels(values: np.ndarray, rows: int, classes: int, name: str) -> np.ndarray:
        labels = np.asarray(values, dtype=np.int64)
        if labels.ndim != 1 or len(labels) != rows:
            raise ValueError("LINe %s must match feature rows" % name)
        if np.any(labels < 0) or np.any(labels >= classes):
            raise ValueError("LINe %s contains an invalid class" % name)
        return labels

    @staticmethod
    def _masks(
        contribution: np.ndarray,
        weights: np.ndarray,
        weight_percentile: float,
        activation_percentile: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        classes, dimensions = contribution.shape
        activation_mask = np.zeros((classes, dimensions), dtype=bool)
        masked_weights = np.zeros((classes, classes, dimensions), dtype=np.float64)
        for routed_class in range(classes):
            matrix = np.abs(contribution[routed_class])[None, :] * weights
            weight_threshold = np.percentile(matrix, weight_percentile)
            masked_weights[routed_class] = weights * (matrix > weight_threshold)
            activation_threshold = np.percentile(contribution[routed_class], activation_percentile)
            activation_mask[routed_class] = contribution[routed_class] > activation_threshold
        return activation_mask, masked_weights

    @staticmethod
    def _routed_logits(
        features: np.ndarray,
        raw_logits: np.ndarray,
        bias: np.ndarray,
        activation_mask: np.ndarray,
        masked_weights: np.ndarray,
        clip_threshold: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        prediction = raw_logits.argmax(axis=1).astype(np.int64, copy=False)
        clipped = np.minimum(features, clip_threshold)
        routed_features = clipped * activation_mask[prediction]
        selected_weights = masked_weights[prediction]
        logits = np.einsum("nd,ncd->nc", routed_features, selected_weights) + bias[None, :]
        return prediction, logits

    def fit(
        self,
        training_features: np.ndarray,
        training_labels: np.ndarray,
        validation_features: np.ndarray,
        validation_labels: np.ndarray,
        validation_logits: np.ndarray,
        classifier_weights: np.ndarray,
        classifier_bias: np.ndarray,
    ) -> None:
        train = _matrix(training_features, "training features")
        validation = _matrix(validation_features, "validation features")
        weights = _matrix(classifier_weights, "classifier weights")
        if train.shape[1] != validation.shape[1] or train.shape[1] != weights.shape[1]:
            raise ValueError("LINe feature and classifier dimensions differ")
        classes = weights.shape[0]
        labels = self._labels(training_labels, len(train), classes, "training labels")
        val_labels = self._labels(validation_labels, len(validation), classes, "validation labels")
        logits = _matrix(validation_logits, "validation logits")
        if logits.shape != (len(validation), classes):
            raise ValueError("LINe validation logits have an unexpected shape")
        bias = np.asarray(classifier_bias, dtype=np.float64)
        if bias.shape != (classes,) or not np.isfinite(bias).all():
            raise ValueError("LINe classifier bias has an unexpected shape")

        contribution = np.zeros_like(weights)
        class_counts = []
        for class_index in range(classes):
            class_features = train[labels == class_index]
            if not len(class_features):
                raise ValueError("LINe training data is missing class %d" % class_index)
            contribution[class_index] = (class_features * weights[class_index]).mean(axis=0)
            class_counts.append(int(len(class_features)))

        rows = []
        candidates = []
        for weight_percentile, activation_percentile in self.pruning_candidates:
            activation_mask, masked_weights = self._masks(
                contribution, weights, weight_percentile, activation_percentile
            )
            for clip_quantile in self.clip_quantiles:
                clip_threshold = float(np.quantile(train, clip_quantile))
                prediction, routed_logits = self._routed_logits(
                    validation, logits, bias, activation_mask, masked_weights, clip_threshold
                )
                row = {
                    "weight_percentile": weight_percentile,
                    "activation_percentile": activation_percentile,
                    "clip_quantile": clip_quantile,
                    "clip_threshold": clip_threshold,
                    "known_validation_nll": _nll(routed_logits, val_labels),
                    "known_validation_accuracy": float(np.mean(prediction == val_labels)),
                }
                rows.append(row)
                candidates.append((row, activation_mask, masked_weights))
        selected, activation_mask, masked_weights = min(
            candidates,
            key=lambda item: (
                item[0]["known_validation_nll"],
                -item[0]["known_validation_accuracy"],
                item[0]["weight_percentile"],
                item[0]["activation_percentile"],
                item[0]["clip_quantile"],
            ),
        )
        self.weights = weights
        self.bias = bias
        self.contribution = contribution
        self.parameters = LINeParameters(
            selected["weight_percentile"], selected["activation_percentile"],
            selected["clip_quantile"], selected["clip_threshold"],
        )
        self.activation_mask = activation_mask
        self.masked_weights = masked_weights
        self.selection_table = rows
        self.class_counts = class_counts

    def evaluate(self, features: np.ndarray, raw_logits: np.ndarray) -> dict[str, np.ndarray]:
        values = _matrix(features, "inference features")
        logits = _matrix(raw_logits, "inference logits")
        if self.parameters is None or self.bias is None or self.activation_mask is None or self.masked_weights is None:
            raise RuntimeError("LINe calibrator has not been fitted")
        if logits.shape != (len(values), len(self.bias)):
            raise ValueError("LINe inference logits have an unexpected shape")
        prediction, routed_logits = self._routed_logits(
            values, logits, self.bias, self.activation_mask, self.masked_weights,
            self.parameters.clip_threshold,
        )
        confidence = _logsumexp(routed_logits)
        return {
            "prediction": prediction,
            "risk": -confidence,
            "confidence": confidence,
            "routed_logits": routed_logits,
        }

    def evidence(self) -> dict[str, object]:
        if self.parameters is None or self.selection_table is None or self.class_counts is None:
            raise RuntimeError("LINe fit evidence is incomplete")
        return {
            "method": "LINe-IDTune",
            "paper": PAPER_URL,
            "supplement": SUPPLEMENT_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "classwise first-order Taylor contribution, activation pruning, weight pruning, upper activation clipping, Energy confidence",
            "taylor_specialization": "embedding times true-class final-linear weight; exact for a frozen linear head",
            "fit_split": "known_training_and_known_validation_only",
            "class_training_counts": self.class_counts,
            "pruning_candidates": [list(pair) for pair in self.pruning_candidates],
            "clip_quantiles": list(self.clip_quantiles),
            "selection_objective": "minimum known-validation NLL; deterministic accuracy and parameter tie-breakers",
            "selected": self.parameters.__dict__,
            "selection_table": self.selection_table,
            "prediction_source": "unmodified_frozen_classifier",
            "risk_orientation": "negative_routed_logsumexp_larger_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "adaptation": {
                "name": "IDTune",
                "reason": "official LINe uses dataset-specific sparsity and raw clip thresholds; OOD-test ablations cannot be reused as a no-leak universal default",
                "scale_portability": "replace raw activation threshold by a known-training embedding quantile",
                "claim_boundary": "paper-formula-consistent ID-only adapter, not an official fixed-default reproduction",
            },
        }

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import softmax

from .neural_open_set import ViMCalibrator


METHODS = ("sirc_msp_l1", "sirc_msp_residual")


@dataclass(frozen=True)
class SIRCParameters:
    mean: float
    std: float
    a: float
    b: float


def sirc_risk(
    primary_confidence: np.ndarray,
    auxiliary_confidence: np.ndarray,
    a: float,
    b: float,
    epsilon: float = 1e-12,
) -> np.ndarray:
    """Official SIRC confidence formula, oriented as larger-is-more-OOD risk."""
    primary = np.asarray(primary_confidence, dtype=np.float64).reshape(-1)
    auxiliary = np.asarray(auxiliary_confidence, dtype=np.float64).reshape(-1)
    if primary.shape != auxiliary.shape:
        raise ValueError("SIRC primary and auxiliary scores have different shapes")
    if epsilon <= 0.0:
        raise ValueError("SIRC epsilon must be positive")
    softmax_term = np.log(np.maximum(1.0 - primary, epsilon))
    auxiliary_term = np.logaddexp(0.0, -float(b) * (auxiliary - float(a)))
    return softmax_term + auxiliary_term


class SIRCMSPFixedCalibrator:
    """SIRC with MSP primary score and two official known-only auxiliaries."""

    def __init__(self, standard_deviation_multiplier: float = 3.0, epsilon: float = 1e-12):
        if standard_deviation_multiplier <= 0.0:
            raise ValueError("SIRC standard deviation multiplier must be positive")
        if epsilon <= 0.0:
            raise ValueError("SIRC epsilon must be positive")
        self.standard_deviation_multiplier = float(standard_deviation_multiplier)
        self.epsilon = float(epsilon)
        self.vim = ViMCalibrator()
        self.parameters: dict[str, SIRCParameters] = {}
        self.train_count: int | None = None

    def _auxiliary_scores(self, embeddings: np.ndarray) -> dict[str, np.ndarray]:
        values = np.asarray(embeddings, dtype=np.float64)
        if values.ndim != 2:
            raise ValueError("SIRC embeddings must be a matrix")
        if self.vim.origin is None or self.vim.null_basis is None or self.vim.alpha is None:
            raise RuntimeError("SIRC calibrator has not been fitted")
        centered = values - self.vim.origin
        residual = self.vim.alpha * np.linalg.norm(centered @ self.vim.null_basis, axis=1)
        return {
            "sirc_msp_l1": np.linalg.norm(values, ord=1, axis=1),
            "sirc_msp_residual": -residual,
        }

    def fit(
        self,
        train_embeddings: np.ndarray,
        train_logits: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray,
    ) -> None:
        embeddings = np.asarray(train_embeddings, dtype=np.float64)
        logits = np.asarray(train_logits, dtype=np.float64)
        if embeddings.ndim != 2 or logits.ndim != 2 or not len(embeddings):
            raise ValueError("SIRC fitting inputs must be non-empty matrices")
        if len(embeddings) != len(logits):
            raise ValueError("SIRC fitting inputs have different row counts")
        self.vim.fit(embeddings, logits, classifier_weight, classifier_bias)
        for method, score in self._auxiliary_scores(embeddings).items():
            mean = float(np.mean(score))
            std = float(np.std(score))
            if not np.isfinite(mean) or not np.isfinite(std) or std <= self.epsilon:
                raise ValueError("SIRC auxiliary score is degenerate for %s" % method)
            self.parameters[method] = SIRCParameters(
                mean=mean,
                std=std,
                a=mean - self.standard_deviation_multiplier * std,
                b=1.0 / std,
            )
        self.train_count = int(len(embeddings))

    def evaluate(self, embeddings: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        if set(self.parameters) != set(METHODS):
            raise RuntimeError("SIRC calibrator has not been fitted")
        values = np.asarray(logits, dtype=np.float64)
        if values.ndim != 2:
            raise ValueError("SIRC logits must be a matrix")
        probability = softmax(values, axis=1)
        msp = probability.max(axis=1)
        auxiliaries = self._auxiliary_scores(embeddings)
        result = {"prediction": values.argmax(axis=1), "msp": msp}
        for method in METHODS:
            params = self.parameters[method]
            result[method] = sirc_risk(msp, auxiliaries[method], params.a, params.b, self.epsilon)
            result[method + "_auxiliary"] = auxiliaries[method]
        return result

    def evidence(self) -> dict[str, object]:
        if self.train_count is None or set(self.parameters) != set(METHODS):
            raise RuntimeError("SIRC calibrator has not been fitted")
        return {
            "method": "SIRC-MSP-Fixed",
            "paper": "https://openaccess.thecvf.com/content/ACCV2022/html/Xia_Augmenting_Softmax_Information_for_Selective_Classification_with_Out-of-Distribution_Data_ACCV_2022_paper.html",
            "official_code": "https://github.com/Guoxoug/SIRC",
            "official_code_commit": "0b492695d5bf34942cd8b333d10a998f763c3eff",
            "fit_split": "known_only_train",
            "primary_confidence": "maximum_softmax_probability",
            "auxiliary_confidences": {
                "sirc_msp_l1": "penultimate_embedding_l1_norm",
                "sirc_msp_residual": "negative_scaled_vim_residual",
            },
            "parameter_rule": "a=known_train_mean-3*known_train_std,b=1/known_train_std",
            "standard_deviation_multiplier": self.standard_deviation_multiplier,
            "parameters": {
                name: vars(params) for name, params in sorted(self.parameters.items())
            },
            "train_embedding_count": self.train_count,
            "vim_principal_dimension": self.vim.principal_dimension,
            "unknown_or_test_labels_used": False,
        }

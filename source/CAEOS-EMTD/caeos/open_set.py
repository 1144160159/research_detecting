from __future__ import annotations

from typing import Dict, Mapping, Optional, Tuple

import numpy as np
import torch
from sklearn.covariance import LedoitWolf
from torch import Tensor


DEFAULT_WEIGHTS = {
    "uncertainty": 0.25,
    "conflict": 0.30,
    "distance": 0.30,
    "energy": 0.15,
}


class OpenSetCalibrator:
    """Known-only calibration for prototype and compound unknown-risk scoring."""

    def __init__(
        self,
        num_classes: int,
        benign_index: int,
        weights: Optional[Mapping[str, float]] = None,
        known_acceptance: float = 0.95,
        malicious_threshold: float = 0.5,
    ):
        self.num_classes = num_classes
        self.benign_index = benign_index
        self.weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
        total_weight = sum(self.weights.values())
        if total_weight <= 0:
            raise ValueError("risk weights must sum to a positive value")
        self.weights = {name: value / total_weight for name, value in self.weights.items()}
        self.known_acceptance = known_acceptance
        self.malicious_threshold = malicious_threshold
        self.prototypes: Optional[Tensor] = None
        self.quantiles: Dict[str, Tuple[float, float]] = {}
        self.risk_threshold: Optional[float] = None

    @staticmethod
    def _energy(output: Dict[str, Tensor]) -> Tensor:
        logits = torch.log(output["fused_evidence"] + 1e-6)
        return -torch.logsumexp(logits, dim=-1)

    def _prototype_distance(self, embeddings: Tensor) -> Tensor:
        if self.prototypes is None:
            raise RuntimeError("calibrator has not been fitted")
        prototypes = self.prototypes.to(embeddings.device)
        return torch.cdist(embeddings, prototypes).min(dim=1).values

    def _normal_distance(self, embeddings: Tensor) -> Tensor:
        if self.prototypes is None:
            raise RuntimeError("calibrator has not been fitted")
        prototype = self.prototypes[self.benign_index].to(embeddings.device)
        return torch.linalg.vector_norm(embeddings - prototype, dim=-1)

    @staticmethod
    def _fit_quantile(values: np.ndarray) -> Tuple[float, float]:
        low, high = np.quantile(values, [0.05, 0.95])
        if high - low < 1e-8:
            high = low + 1e-8
        return float(low), float(high)

    def _normalize(self, name: str, values: Tensor) -> Tensor:
        low, high = self.quantiles[name]
        return ((values - low) / (high - low)).clamp(0.0, 2.0)

    def fit_prototypes(self, embeddings: Tensor, labels: Tensor) -> None:
        prototypes = []
        for class_index in range(self.num_classes):
            selected = embeddings[labels == class_index]
            if selected.numel() == 0:
                raise ValueError("class %d has no prototype samples" % class_index)
            prototypes.append(selected.mean(dim=0))
        self.prototypes = torch.stack(prototypes).detach().cpu()

    def raw_components(self, output: Dict[str, Tensor]) -> Dict[str, Tensor]:
        return {
            "uncertainty": output["fused_uncertainty"],
            "conflict": output["global_conflict"],
            "distance": self._prototype_distance(output["fused_embedding"]),
            "energy": self._energy(output),
            "inverse_belief": 1.0 - output["fused_belief"].max(dim=-1).values,
            "normal_distance": self._normal_distance(output["fused_embedding"]),
        }

    def fit_known_validation(self, validation_output: Dict[str, Tensor]) -> None:
        components = self.raw_components(validation_output)
        for name in ("uncertainty", "conflict", "distance", "energy", "normal_distance"):
            values = components[name].detach().cpu().numpy()
            self.quantiles[name] = self._fit_quantile(values)
        risk, _, _ = self.score(validation_output)
        self.risk_threshold = float(
            np.quantile(risk.detach().cpu().numpy(), self.known_acceptance)
        )

    def score(
        self, output: Dict[str, Tensor]
    ) -> Tuple[Tensor, Tensor, Dict[str, Tensor]]:
        if self.prototypes is None or not self.quantiles:
            raise RuntimeError("calibrator has not been fitted")
        raw = self.raw_components(output)
        normalized = {
            name: self._normalize(name, raw[name])
            for name in ("uncertainty", "conflict", "distance", "energy")
        }
        risk = sum(self.weights[name] * normalized[name] for name in self.weights)
        normal_distance = self._normalize("normal_distance", raw["normal_distance"])
        malicious_probability = torch.sigmoid(output["malicious_logit"])
        maliciousness = 0.5 * malicious_probability + 0.5 * normal_distance.clamp(0.0, 1.0)
        return risk, maliciousness, normalized

    def predict(self, output: Dict[str, Tensor]) -> Dict[str, Tensor]:
        if self.risk_threshold is None:
            raise RuntimeError("risk threshold has not been fitted")
        risk, maliciousness, components = self.score(output)
        known_prediction = output["fused_belief"].argmax(dim=-1)
        is_unknown = risk >= self.risk_threshold
        decision = known_prediction.clone()
        decision[is_unknown & (maliciousness >= self.malicious_threshold)] = -1
        decision[is_unknown & (maliciousness < self.malicious_threshold)] = -2
        return {
            "decision": decision,
            "known_prediction": known_prediction,
            "is_unknown": is_unknown,
            "risk": risk,
            "maliciousness": maliciousness,
            "components": components,
        }

    def state_dict(self) -> Dict[str, object]:
        if self.prototypes is None or self.risk_threshold is None:
            raise RuntimeError("cannot serialize an unfitted calibrator")
        return {
            "num_classes": self.num_classes,
            "benign_index": self.benign_index,
            "weights": self.weights,
            "known_acceptance": self.known_acceptance,
            "malicious_threshold": self.malicious_threshold,
            "prototypes": self.prototypes.tolist(),
            "quantiles": {key: list(value) for key, value in self.quantiles.items()},
            "risk_threshold": self.risk_threshold,
        }

    @classmethod
    def from_state_dict(cls, state: Mapping[str, object]) -> "OpenSetCalibrator":
        calibrator = cls(
            int(state["num_classes"]),
            int(state["benign_index"]),
            state["weights"],
            float(state["known_acceptance"]),
            float(state["malicious_threshold"]),
        )
        calibrator.prototypes = torch.tensor(state["prototypes"], dtype=torch.float32)
        calibrator.quantiles = {
            key: (float(value[0]), float(value[1]))
            for key, value in state["quantiles"].items()
        }
        calibrator.risk_threshold = float(state["risk_threshold"])
        return calibrator


class DiagnosticConformalCalibrator(OpenSetCalibrator):
    """Class-conditional known-only calibration in a multivariate diagnostic space."""

    FEATURE_NAMES = (
        "uncertainty",
        "conflict",
        "distance",
        "normal_distance",
        "inverse_belief",
    )

    def __init__(
        self,
        num_classes: int,
        benign_index: int,
        known_acceptance: float = 0.95,
        malicious_threshold: float = 0.5,
        min_class_samples: int = 20,
    ):
        super().__init__(
            num_classes,
            benign_index,
            known_acceptance=known_acceptance,
            malicious_threshold=malicious_threshold,
        )
        self.min_class_samples = min_class_samples
        self.feature_median: Optional[Tensor] = None
        self.feature_scale: Optional[Tensor] = None
        self.reference_models: Dict[int, Tuple[Tensor, Tensor]] = {}
        self.calibration_scores: Dict[int, Tensor] = {}
        self.risk_threshold = known_acceptance

    def _feature_matrix(self, output: Dict[str, Tensor]) -> Tensor:
        raw = self.raw_components(output)
        return torch.stack([raw[name] for name in self.FEATURE_NAMES], dim=-1)

    def _standardize(self, features: Tensor) -> Tensor:
        if self.feature_median is None or self.feature_scale is None:
            raise RuntimeError("diagnostic reference has not been fitted")
        median = self.feature_median.to(features.device)
        scale = self.feature_scale.to(features.device)
        return (features - median) / scale

    @staticmethod
    def _fit_reference_model(values: np.ndarray) -> Tuple[Tensor, Tensor]:
        if len(values) < 2:
            location = values.mean(axis=0) if len(values) else np.zeros(values.shape[1])
            precision = np.eye(values.shape[1], dtype=np.float64)
        else:
            estimator = LedoitWolf().fit(values)
            location = estimator.location_
            precision = estimator.precision_
        return (
            torch.tensor(location, dtype=torch.float32),
            torch.tensor(precision, dtype=torch.float32),
        )

    def fit_reference(self, train_output: Dict[str, Tensor], train_labels: Tensor) -> None:
        features = self._feature_matrix(train_output).detach().cpu()
        labels = train_labels.detach().cpu().to(torch.long)
        lower = torch.quantile(features, 0.25, dim=0)
        upper = torch.quantile(features, 0.75, dim=0)
        self.feature_median = torch.median(features, dim=0).values
        self.feature_scale = (upper - lower).clamp_min(1e-6)
        standardized = self._standardize(features).numpy().astype(np.float64)
        self.reference_models = {
            -1: self._fit_reference_model(standardized)
        }
        for class_index in range(self.num_classes):
            selected = standardized[labels.numpy() == class_index]
            if len(selected) >= self.min_class_samples:
                self.reference_models[class_index] = self._fit_reference_model(selected)

    def _nonconformity(self, output: Dict[str, Tensor]) -> Tuple[Tensor, Tensor]:
        if not self.reference_models:
            raise RuntimeError("diagnostic reference has not been fitted")
        features = self._standardize(self._feature_matrix(output))
        predicted_class = output["fused_belief"].argmax(dim=-1)
        scores = features.new_empty(features.shape[0])
        for class_index in predicted_class.unique().tolist():
            selected = predicted_class == class_index
            location, precision = self.reference_models.get(
                int(class_index), self.reference_models[-1]
            )
            delta = features[selected] - location.to(features.device)
            scores[selected] = torch.einsum(
                "bi,ij,bj->b",
                delta,
                precision.to(features.device),
                delta,
            )
        return scores.clamp_min(0.0), predicted_class

    def fit_known_validation(self, validation_output: Dict[str, Tensor]) -> None:
        scores, predicted_class = self._nonconformity(validation_output)
        scores = scores.detach().cpu()
        predicted_class = predicted_class.detach().cpu()
        self.calibration_scores = {-1: torch.sort(scores).values}
        for class_index in range(self.num_classes):
            selected = scores[predicted_class == class_index]
            if len(selected) >= self.min_class_samples:
                self.calibration_scores[class_index] = torch.sort(selected).values
        self.risk_threshold = self.known_acceptance

    def _conformal_p_value(self, scores: Tensor, predicted_class: Tensor) -> Tensor:
        if not self.calibration_scores:
            raise RuntimeError("known validation calibration has not been fitted")
        p_value = scores.new_empty(scores.shape)
        for class_index in predicted_class.unique().tolist():
            selected = predicted_class == class_index
            calibration = self.calibration_scores.get(
                int(class_index), self.calibration_scores[-1]
            ).to(scores.device)
            insertion = torch.searchsorted(calibration, scores[selected], right=False)
            greater_or_equal = len(calibration) - insertion
            p_value[selected] = (1.0 + greater_or_equal.to(scores.dtype)) / (
                len(calibration) + 1.0
            )
        return p_value

    def score(
        self, output: Dict[str, Tensor]
    ) -> Tuple[Tensor, Tensor, Dict[str, Tensor]]:
        scores, predicted_class = self._nonconformity(output)
        p_value = self._conformal_p_value(scores, predicted_class)
        risk = 1.0 - p_value
        raw = self.raw_components(output)
        normal_distance = raw["normal_distance"]
        if "normal_distance" in self.quantiles:
            normalized_normal_distance = self._normalize(
                "normal_distance", normal_distance
            ).clamp(0.0, 1.0)
        else:
            normalized_normal_distance = torch.sigmoid(normal_distance)
        malicious_probability = torch.sigmoid(output["malicious_logit"])
        maliciousness = 0.5 * malicious_probability + 0.5 * normalized_normal_distance
        return risk, maliciousness, {
            "diagnostic_score": scores,
            "conformal_p_value": p_value,
        }

    def predict(self, output: Dict[str, Tensor]) -> Dict[str, Tensor]:
        risk, maliciousness, components = self.score(output)
        known_prediction = output["fused_belief"].argmax(dim=-1)
        is_unknown = risk >= float(self.risk_threshold)
        decision = known_prediction.clone()
        decision[is_unknown & (maliciousness >= self.malicious_threshold)] = -1
        decision[is_unknown & (maliciousness < self.malicious_threshold)] = -2
        return {
            "decision": decision,
            "known_prediction": known_prediction,
            "is_unknown": is_unknown,
            "risk": risk,
            "maliciousness": maliciousness,
            "components": components,
        }

    def state_dict(self) -> Dict[str, object]:
        if (
            self.prototypes is None
            or self.feature_median is None
            or self.feature_scale is None
            or not self.reference_models
            or not self.calibration_scores
        ):
            raise RuntimeError("cannot serialize an unfitted conformal calibrator")
        return {
            "type": "diagnostic_conformal",
            "num_classes": self.num_classes,
            "benign_index": self.benign_index,
            "known_acceptance": self.known_acceptance,
            "malicious_threshold": self.malicious_threshold,
            "min_class_samples": self.min_class_samples,
            "feature_names": list(self.FEATURE_NAMES),
            "feature_median": self.feature_median.tolist(),
            "feature_scale": self.feature_scale.tolist(),
            "prototypes": self.prototypes.tolist(),
            "reference_models": {
                str(key): {
                    "location": location.tolist(),
                    "precision": precision.tolist(),
                }
                for key, (location, precision) in self.reference_models.items()
            },
            "calibration_scores": {
                str(key): values.tolist()
                for key, values in self.calibration_scores.items()
            },
            "risk_threshold": float(self.risk_threshold),
        }

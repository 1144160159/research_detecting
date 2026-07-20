from __future__ import annotations

from typing import Sequence

import numpy as np


PAPER_URL = "https://arxiv.org/abs/2310.00227"
OFFICIAL_CODE_URL = "https://github.com/kai422/SCALE"
OFFICIAL_PERCENTILE = 85.0
OFFICIAL_PERCENTILE_SWEEP = (50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0)


def _validate_percentile(percentile: float) -> float:
    value = float(percentile)
    if not np.isfinite(value) or not 0.0 <= value < 100.0:
        raise ValueError("SCALE percentile must be finite and in [0, 100)")
    return value


def _prepare_activations(
    activations: np.ndarray, *, rectify_negative: bool
) -> np.ndarray:
    values = np.asarray(activations, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] == 0:
        raise ValueError("SCALE activations must be a non-empty matrix")
    if not np.isfinite(values).all():
        raise ValueError("SCALE activations must be finite")
    if rectify_negative:
        return np.maximum(values, 0.0)
    if np.any(values < 0.0):
        raise ValueError(
            "SCALE requires non-negative penultimate activations; enable "
            "rectify_negative for GELU embeddings"
        )
    return values.copy()


def _scale_details(
    activations: np.ndarray,
    percentile: float,
    *,
    rectify_negative: bool,
) -> tuple[np.ndarray, np.ndarray, int]:
    values = _prepare_activations(
        activations, rectify_negative=rectify_negative
    )
    percentile = _validate_percentile(percentile)
    feature_count = values.shape[1]

    # Match the official np.round/top-k implementation. The lower bound is a
    # tabular adaptation for dimensions where rounding would otherwise give k=0.
    pruned_count = int(np.round(feature_count * percentile / 100.0))
    top_k = max(1, feature_count - pruned_count)
    top_values = np.partition(values, feature_count - top_k, axis=1)[:, -top_k:]
    total_mass = values.sum(axis=1)
    retained_mass = top_values.sum(axis=1)

    exponent = np.zeros(len(values), dtype=np.float64)
    positive_mass = total_mass > 0.0
    if np.any(positive_mass & (retained_mass <= 0.0)):
        raise FloatingPointError("SCALE retained activation mass is not positive")
    exponent[positive_mass] = (
        total_mass[positive_mass] / retained_mass[positive_mass]
    )
    if np.any(exponent > np.log(np.finfo(np.float64).max)):
        raise OverflowError("SCALE activation exponent exceeds float64 range")

    factors = np.ones(len(values), dtype=np.float64)
    factors[positive_mass] = np.exp(exponent[positive_mass])
    return values * factors[:, None], factors, top_k


def scale_factors(
    activations: np.ndarray,
    percentile: float = OFFICIAL_PERCENTILE,
    *,
    rectify_negative: bool = True,
) -> np.ndarray:
    """Return SCALE's sample-specific exp(Q / Q_p) multipliers."""

    _, factors, _ = _scale_details(
        activations,
        percentile,
        rectify_negative=rectify_negative,
    )
    return factors


def scale_activations(
    activations: np.ndarray,
    percentile: float = OFFICIAL_PERCENTILE,
    *,
    rectify_negative: bool = True,
) -> np.ndarray:
    """Scale every activation while using top activations only to estimate r."""

    scaled, _, _ = _scale_details(
        activations,
        percentile,
        rectify_negative=rectify_negative,
    )
    return scaled


class SCALECalibrator:
    """SCALE activation shaping followed by an Energy OOD risk.

    The ICLR 2024 method estimates a per-sample ratio from the largest
    penultimate activations, scales all activations by its exponential, and
    applies the existing linear classifier. The official implementation emits
    positive Energy as ID confidence; this adapter negates it so larger values
    consistently mean more unknown in CAEOS.

    A fixed percentile requires no OOD calibration. If candidates are supplied,
    selection is restricted to labelled known-validation samples and prioritizes
    known accuracy, then known negative log likelihood.
    """

    def __init__(
        self,
        percentile: float = OFFICIAL_PERCENTILE,
        temperature: float = 1.0,
        rectify_negative: bool = True,
        percentile_candidates: Sequence[float] | None = None,
    ) -> None:
        self.requested_percentile = _validate_percentile(percentile)
        self.percentile = self.requested_percentile
        self.temperature = float(temperature)
        if not np.isfinite(self.temperature) or self.temperature <= 0.0:
            raise ValueError("SCALE temperature must be finite and positive")
        self.rectify_negative = bool(rectify_negative)
        if percentile_candidates is None:
            self.percentile_candidates: tuple[float, ...] | None = None
        else:
            candidates = tuple(
                dict.fromkeys(
                    _validate_percentile(value)
                    for value in percentile_candidates
                )
            )
            if not candidates:
                raise ValueError("SCALE percentile candidates cannot be empty")
            self.percentile_candidates = candidates

        self.classifier_weight: np.ndarray | None = None
        self.classifier_bias: np.ndarray | None = None
        self.validation_count: int | None = None
        self.validation_metrics: list[dict[str, float]] | None = None
        self.percentile_source: str | None = None
        self.top_k: int | None = None

    @staticmethod
    def _validate_labels(labels: np.ndarray, row_count: int) -> np.ndarray:
        values = np.asarray(labels)
        if values.ndim != 1 or len(values) != row_count:
            raise ValueError(
                "SCALE known-validation labels must match activation rows"
            )
        if not np.issubdtype(values.dtype, np.integer):
            raise ValueError("SCALE known-validation labels must be integers")
        return values.astype(np.int64, copy=False)

    @staticmethod
    def _validate_classifier(
        weight: np.ndarray,
        bias: np.ndarray | None,
        feature_count: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        classifier_weight = np.asarray(weight, dtype=np.float64)
        if (
            classifier_weight.ndim != 2
            or classifier_weight.shape[0] < 2
            or classifier_weight.shape[1] != feature_count
        ):
            raise ValueError(
                "SCALE classifier weight must have shape [classes, features]"
            )
        if bias is None:
            classifier_bias = np.zeros(
                classifier_weight.shape[0], dtype=np.float64
            )
        else:
            classifier_bias = np.asarray(bias, dtype=np.float64)
            if classifier_bias.shape != (classifier_weight.shape[0],):
                raise ValueError(
                    "SCALE classifier bias must have shape [classes]"
                )
        if not (
            np.isfinite(classifier_weight).all()
            and np.isfinite(classifier_bias).all()
        ):
            raise ValueError("SCALE classifier parameters must be finite")
        return classifier_weight.copy(), classifier_bias.copy()

    def _energy_knownness(self, logits: np.ndarray) -> np.ndarray:
        normalized = logits / self.temperature
        maximum = normalized.max(axis=1)
        return self.temperature * (
            maximum
            + np.log(np.exp(normalized - maximum[:, None]).sum(axis=1))
        )

    def _known_metrics(
        self, logits: np.ndarray, labels: np.ndarray
    ) -> tuple[float, float]:
        prediction = logits.argmax(axis=1)
        accuracy = float(np.mean(prediction == labels))
        normalized = logits / self.temperature
        maximum = normalized.max(axis=1)
        log_normalizer = maximum + np.log(
            np.exp(normalized - maximum[:, None]).sum(axis=1)
        )
        nll = float(
            np.mean(log_normalizer - normalized[np.arange(len(labels)), labels])
        )
        return accuracy, nll

    def fit(
        self,
        known_validation_activations: np.ndarray,
        known_validation_labels: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray | None = None,
    ) -> None:
        activations = _prepare_activations(
            known_validation_activations,
            rectify_negative=self.rectify_negative,
        )
        labels = self._validate_labels(
            known_validation_labels, len(activations)
        )
        weight, bias = self._validate_classifier(
            classifier_weight, classifier_bias, activations.shape[1]
        )
        if np.any(labels < 0) or np.any(labels >= weight.shape[0]):
            raise ValueError(
                "SCALE known-validation labels are outside classifier classes"
            )

        candidates = (
            self.percentile_candidates
            if self.percentile_candidates is not None
            else (self.requested_percentile,)
        )
        candidate_results: list[dict[str, float]] = []
        for candidate in candidates:
            scaled, _, _ = _scale_details(
                activations,
                candidate,
                rectify_negative=False,
            )
            logits = scaled @ weight.T + bias
            accuracy, nll = self._known_metrics(logits, labels)
            candidate_results.append(
                {
                    "percentile": float(candidate),
                    "known_accuracy": accuracy,
                    "known_nll": nll,
                }
            )

        if self.percentile_candidates is None:
            selected = candidate_results[0]
            self.percentile_source = (
                "fixed_paper_default_without_ood_sweep"
                if self.requested_percentile == OFFICIAL_PERCENTILE
                else "fixed_constructor_value_without_ood_sweep"
            )
        else:
            selected = max(
                candidate_results,
                key=lambda item: (
                    item["known_accuracy"],
                    -item["known_nll"],
                    -abs(item["percentile"] - OFFICIAL_PERCENTILE),
                    -item["percentile"],
                ),
            )
            self.percentile_source = (
                "selected_on_known_validation_accuracy_then_nll"
            )

        self.percentile = float(selected["percentile"])
        self.classifier_weight = weight
        self.classifier_bias = bias
        self.validation_count = int(len(activations))
        self.validation_metrics = candidate_results
        _, _, self.top_k = _scale_details(
            activations,
            self.percentile,
            rectify_negative=False,
        )

    def _require_fit(self) -> tuple[np.ndarray, np.ndarray]:
        if self.classifier_weight is None or self.classifier_bias is None:
            raise RuntimeError("SCALE calibrator has not been fitted")
        return self.classifier_weight, self.classifier_bias

    def transform(self, activations: np.ndarray) -> np.ndarray:
        weight, _ = self._require_fit()
        values = np.asarray(activations)
        if values.ndim != 2 or values.shape[1] != weight.shape[1]:
            raise ValueError(
                "SCALE inference activations and classifier dimensions differ"
            )
        return scale_activations(
            values,
            self.percentile,
            rectify_negative=self.rectify_negative,
        )

    def factors(self, activations: np.ndarray) -> np.ndarray:
        weight, _ = self._require_fit()
        values = np.asarray(activations)
        if values.ndim != 2 or values.shape[1] != weight.shape[1]:
            raise ValueError(
                "SCALE inference activations and classifier dimensions differ"
            )
        return scale_factors(
            values,
            self.percentile,
            rectify_negative=self.rectify_negative,
        )

    def logits(self, activations: np.ndarray) -> np.ndarray:
        weight, bias = self._require_fit()
        return self.transform(activations) @ weight.T + bias

    def predict(self, activations: np.ndarray) -> np.ndarray:
        return self.logits(activations).argmax(axis=1)

    def score(self, activations: np.ndarray) -> np.ndarray:
        """Return negative Energy, oriented so larger means more unknown."""

        return -self._energy_knownness(self.logits(activations))

    def evidence(self) -> dict[str, object]:
        weight, bias = self._require_fit()
        if (
            self.validation_count is None
            or self.validation_metrics is None
            or self.percentile_source is None
            or self.top_k is None
        ):
            raise RuntimeError("SCALE fit evidence is incomplete")
        return {
            "method": "SCALE",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_formula": (
                "h_scaled=h*exp(sum(h)/sum(top_k(h,p))); "
                "id_confidence=T*logsumexp(logits/T)"
            ),
            "official_default_percentile": OFFICIAL_PERCENTILE,
            "official_percentile_sweep": list(OFFICIAL_PERCENTILE_SWEEP),
            "selected_percentile": self.percentile,
            "percentile_source": self.percentile_source,
            "temperature": self.temperature,
            "temperature_source": "fixed_constructor_value",
            "fit_split": "known_only_validation",
            "validation_embedding_count": self.validation_count,
            "validation_candidate_metrics": self.validation_metrics,
            "class_count": int(weight.shape[0]),
            "feature_dimension": int(weight.shape[1]),
            "classifier_bias_present": bool(np.any(bias != 0.0)),
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "adaptation": {
                "activation_policy": (
                    "relu_clamp_for_gelu_penultimate"
                    if self.rectify_negative
                    else "require_nonnegative_rectified_penultimate"
                ),
                "minimum_top_k_for_low_dimensional_tabular_features": 1,
                "selected_top_k": self.top_k,
                "zero_activation_mass_policy": "identity_scale",
                "risk_orientation": "negative_energy_larger_is_more_unknown",
            },
        }
